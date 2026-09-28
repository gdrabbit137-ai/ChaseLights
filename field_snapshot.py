"""B101 immutable field snapshot capture and replay core.

Snapshots freeze the provider payload, normalized model input, and recorded
Opportunity output from one ChaseLights forecast execution. A snapshot is not
field ground truth; observation.status remains "unreviewed" until a separate
field-validation workflow admits it.

Replay is network-free. From B101 onward a target Git commit can replay the same
normalized input in a detached worktree, so model revisions can be compared
without changing the stored snapshot.
"""

from __future__ import annotations

import argparse
import base64
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

SNAPSHOT_SCHEMA_VERSION = "field-snapshot-r4.2-1"
SNAPSHOT_KIND = "forecast_snapshot_not_ground_truth"
DEFAULT_SNAPSHOT_DIR = Path(".snapshots")
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_PROJECT_ROOT = Path(__file__).resolve().parent


def _canonical_json(payload):
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _payload_hash(snapshot):
    body = deepcopy(snapshot)
    body.pop("integrity", None)
    return hashlib.sha256(_canonical_json(body)).hexdigest()


def _run_git(args, *, cwd=_PROJECT_ROOT, check=True):
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def current_git_commit():
    """Return the commit whose code is actually checked out.

    GitHub Actions GITHUB_SHA can refer to an outer workflow/merge commit while
    replay is executing inside a detached target-version worktree. Prefer the
    repository HEAD and use GITHUB_SHA only as a fallback when Git metadata is
    unavailable.
    """
    try:
        sha = _run_git(["rev-parse", "HEAD"]).stdout.strip().lower()
    except (OSError, subprocess.CalledProcessError):
        sha = ""
    if _SHA40.match(sha):
        return sha
    env_sha = str(os.environ.get("GITHUB_SHA") or "").strip().lower()
    return env_sha if _SHA40.match(env_sha) else None


def _offset_aware_iso(value):
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None or dt.utcoffset() is None:
        return None
    return dt


def find_spot(place_id):
    from regions import get_spots

    region = str(place_id or "").split("-", 1)[0]
    if region not in {"tw", "jp", "us"}:
        raise ValueError(f"unsupported place id: {place_id}")
    for spot in get_spots(region):
        if spot.get("spot_id") == place_id:
            return spot
    raise ValueError(f"unknown place id: {place_id}")


def _provenance():
    from opportunities import ADAPTER_VERSION, CANONICAL_CATALOG_SCHEMA_VERSION
    from opportunity_runtime import MODULE_VERSION
    from spatial_weather import SPATIAL_WEATHER_VERSION

    return {
        "git_commit": current_git_commit(),
        "adapter_version": ADAPTER_VERSION,
        "catalog_schema_version": CANONICAL_CATALOG_SCHEMA_VERSION,
        "opportunity_runtime_version": MODULE_VERSION,
        "spatial_weather_version": SPATIAL_WEATHER_VERSION,
        "snapshot_writer_version": SNAPSHOT_SCHEMA_VERSION,
    }


def make_snapshot_id(place_id, captured_at):
    dt = captured_at.astimezone(timezone.utc)
    place_token = str(place_id).upper()
    return f"FVS-{place_token}-{dt:%Y%m%d-%H%M%S}"


def build_snapshot_from_event(place_id, event, *, captured_at=None):
    captured_at = captured_at or datetime.now(timezone.utc)
    if captured_at.tzinfo is None or captured_at.utcoffset() is None:
        raise ValueError("captured_at must be offset-aware")
    spot = find_spot(place_id)
    snapshot = {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "snapshot_kind": SNAPSHOT_KIND,
        "snapshot_id": make_snapshot_id(place_id, captured_at),
        "place_id": place_id,
        "place_name": (
            (spot.get("name_i18n") or {}).get("zh-TW")
            or spot.get("name")
            or place_id
        ),
        "captured_at": captured_at.isoformat(),
        "forecast_valid_at": event["forecast_valid_at"],
        "forecast_valid_epoch": int(event["forecast_valid_epoch"]),
        "timezone": event.get("timezone") or "UTC",
        "language": event.get("language") or "zh-TW",
        "provenance": _provenance(),
        "source_payloads": {
            "camera_weather_raw": deepcopy(event.get("raw_camera_weather")),
            "spatial_weather_raw": deepcopy(event.get("raw_spatial_weather")),
        },
        "spatial_request_plan": deepcopy(event.get("spatial_request_plan")),
        "normalized_input": deepcopy(event.get("normalized_input") or {}),
        "recorded_output": {
            "runtime_output": deepcopy(event.get("runtime_output") or {}),
            "theme_scores": deepcopy(event.get("theme_scores") or {}),
            "opportunity_scores": deepcopy(event.get("opportunity_scores") or {}),
        },
        "observation": {
            "status": "unreviewed",
            "note": (
                "Forecast snapshot only. This is not field ground truth and must "
                "not be promoted to a field-validation case without an observed scene."
            ),
        },
    }
    snapshot["integrity"] = {
        "algorithm": "sha256",
        "payload_sha256": _payload_hash(snapshot),
    }
    return snapshot


def validate_snapshot(snapshot):
    errors = []
    if snapshot.get("schema_version") != SNAPSHOT_SCHEMA_VERSION:
        errors.append("snapshot schema mismatch")
    if snapshot.get("snapshot_kind") != SNAPSHOT_KIND:
        errors.append("snapshot kind must remain forecast_snapshot_not_ground_truth")
    snapshot_id = str(snapshot.get("snapshot_id") or "")
    if not snapshot_id.startswith("FVS-"):
        errors.append("snapshot_id missing or invalid")
    place_id = str(snapshot.get("place_id") or "")
    try:
        find_spot(place_id)
    except ValueError as exc:
        errors.append(str(exc))
    for key in ("captured_at", "forecast_valid_at"):
        if _offset_aware_iso(snapshot.get(key)) is None:
            errors.append(f"{key} must be offset-aware ISO8601")
    if not isinstance(snapshot.get("forecast_valid_epoch"), int):
        errors.append("forecast_valid_epoch must be integer")
    provenance = snapshot.get("provenance") or {}
    sha = str(provenance.get("git_commit") or "")
    if not _SHA40.match(sha):
        errors.append("provenance.git_commit must be a full Git commit SHA")
    for key in (
        "adapter_version",
        "catalog_schema_version",
        "opportunity_runtime_version",
        "spatial_weather_version",
        "snapshot_writer_version",
    ):
        if not str(provenance.get(key) or "").strip():
            errors.append(f"provenance.{key} missing")
    source = snapshot.get("source_payloads")
    if not isinstance(source, dict) or "camera_weather_raw" not in source:
        errors.append("source_payloads.camera_weather_raw missing")
    if "spatial_request_plan" not in snapshot:
        errors.append("spatial_request_plan missing")
    normalized = snapshot.get("normalized_input")
    if not isinstance(normalized, dict) or not normalized:
        errors.append("normalized_input missing")
    recorded = snapshot.get("recorded_output") or {}
    if not isinstance(recorded.get("opportunity_scores"), dict) or not recorded.get("opportunity_scores"):
        errors.append("recorded_output.opportunity_scores missing")
    observation = snapshot.get("observation") or {}
    if observation.get("status") != "unreviewed":
        errors.append("B101 snapshot observation.status must be unreviewed")
    integrity = snapshot.get("integrity") or {}
    if integrity.get("algorithm") != "sha256":
        errors.append("integrity algorithm must be sha256")
    expected_hash = str(integrity.get("payload_sha256") or "")
    actual_hash = _payload_hash(snapshot)
    if expected_hash != actual_hash:
        errors.append("snapshot integrity hash mismatch")
    return errors


def write_snapshot(snapshot, output_dir=DEFAULT_SNAPSHOT_DIR):
    errors = validate_snapshot(snapshot)
    if errors:
        raise ValueError("\n".join(errors))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{snapshot['snapshot_id']}.json"
    with path.open("x", encoding="utf-8") as handle:
        json.dump(snapshot, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return path


def _read_snapshot_payload(path):
    path = Path(path)
    if path.name.endswith(".json.gz.b64"):
        encoded = path.read_text(encoding="ascii")
        raw = gzip.decompress(base64.b64decode(encoded))
        return json.loads(raw.decode("utf-8"))
    return json.loads(path.read_text(encoding="utf-8"))


def load_snapshot(path):
    payload = _read_snapshot_payload(path)
    errors = validate_snapshot(payload)
    if errors:
        raise ValueError("\n".join(errors))
    return payload


def evaluate_normalized_input(place_id, item_data, *, lang="zh-TW", timezone_name="UTC"):
    """Network-free current-code replay for one normalized forecast hour."""
    import fetch_data

    spot = find_spot(place_id)
    item_data = deepcopy(item_data)
    runtime_output = fetch_data._build_opportunity_runtime_diagnostics(spot, item_data)
    themes = spot.get("themes") or spot.get("tags", ["mountain_view"])
    timestamp = int(item_data["timestamp"])
    utc_dt = datetime.fromtimestamp(timestamp, timezone.utc)
    try:
        tz = ZoneInfo(timezone_name)
    except Exception:
        tz = timezone.utc
    local_dt = utc_dt.astimezone(tz)

    theme_scores = {}
    for theme in themes:
        score, status, indicator, status_key, indicator_key, factors = (
            fetch_data.evaluate_tag_condition(theme, item_data, local_dt.hour, lang)
        )
        temporal_eligible, temporal_reason = fetch_data._temporal_eligibility(
            theme, item_data
        )
        temporal_end = (
            fetch_data._temporal_end_boundary(
                theme,
                local_dt,
                spot.get("lat"),
                spot.get("lon"),
                lang,
            )
            if temporal_eligible is True
            else None
        )
        theme_scores[theme] = {
            "score": score,
            "status": status,
            "status_key": status_key,
            "key_indicator": indicator,
            "indicator_key": indicator_key,
            "factors": factors,
            "temporal_eligible": temporal_eligible,
            "temporal_reason": temporal_reason,
            "temporal_end": temporal_end,
        }

    opportunity_scores = {}
    for opportunity in spot.get("opportunities", []) or []:
        oid = opportunity.get("opportunity_id")
        theme = opportunity.get("legacy_theme")
        if not oid or not theme:
            continue
        metric = theme_scores.get(theme)
        if metric is None:
            score, status, indicator, status_key, indicator_key, factors = (
                fetch_data.evaluate_tag_condition(
                    theme, item_data, local_dt.hour, lang
                )
            )
            temporal_eligible, temporal_reason = fetch_data._temporal_eligibility(
                theme, item_data
            )
            temporal_end = (
                fetch_data._temporal_end_boundary(
                    theme,
                    local_dt,
                    spot.get("lat"),
                    spot.get("lon"),
                    lang,
                )
                if temporal_eligible is True
                else None
            )
            metric = {
                "score": score,
                "status": status,
                "status_key": status_key,
                "key_indicator": indicator,
                "indicator_key": indicator_key,
                "factors": factors,
                "temporal_eligible": temporal_eligible,
                "temporal_reason": temporal_reason,
                "temporal_end": temporal_end,
            }
            theme_scores[theme] = metric
        opportunity_scores[oid] = fetch_data._score_opportunity(
            opportunity,
            metric,
            runtime_output.get(oid),
            lang,
        )
    return {
        "runtime_output": runtime_output,
        "theme_scores": theme_scores,
        "opportunity_scores": opportunity_scores,
    }


def replay_current(snapshot):
    return evaluate_normalized_input(
        snapshot["place_id"],
        snapshot["normalized_input"],
        lang=snapshot.get("language") or "zh-TW",
        timezone_name=snapshot.get("timezone") or "UTC",
    )


def _stable_outcome(outcome):
    runtime = outcome.get("runtime") or {}
    spatial = runtime.get("spatial_mist_context") or {}
    return {
        "score": outcome.get("score"),
        "condition_state": outcome.get("condition_state"),
        "score_confidence": outcome.get("score_confidence"),
        "runtime_eligible": outcome.get("runtime_eligible"),
        "temporal_eligible": outcome.get("temporal_eligible"),
        "runtime_reason": runtime.get("reason"),
        "directional_mist_negative_evidence": runtime.get(
            "directional_mist_negative_evidence"
        ),
        "spatial_mist": {
            "available": spatial.get("available"),
            "eligible": spatial.get("eligible"),
            "reason": spatial.get("reason"),
            "target_sample_count": spatial.get("target_sample_count"),
            "mist_target_count": spatial.get("mist_target_count"),
            "directional_mist_target_count": spatial.get(
                "directional_mist_target_count"
            ),
            "clear_target_count": spatial.get("clear_target_count"),
            "clear_bearing_count": spatial.get("clear_bearing_count"),
            "broad_clear_target_sector": spatial.get(
                "broad_clear_target_sector"
            ),
        },
    }


def diff_replay(snapshot, replayed):
    recorded_scores = (snapshot.get("recorded_output") or {}).get(
        "opportunity_scores", {}
    )
    replayed_scores = replayed.get("opportunity_scores") or {}
    differences = []
    all_ids = sorted(set(recorded_scores) | set(replayed_scores))
    comparison = {}
    for oid in all_ids:
        old = _stable_outcome(recorded_scores.get(oid) or {})
        new = _stable_outcome(replayed_scores.get(oid) or {})
        comparison[oid] = {"recorded": old, "replayed": new}
        if old != new:
            differences.append(oid)
    return {
        "snapshot_id": snapshot["snapshot_id"],
        "snapshot_commit": snapshot["provenance"]["git_commit"],
        "replay_commit": current_git_commit(),
        "match": not differences,
        "different_opportunity_ids": differences,
        "comparison": comparison,
    }


def _resolve_commit(value):
    if value == "current":
        sha = current_git_commit()
        if not sha:
            raise RuntimeError("unable to resolve current Git commit")
        return sha
    try:
        return _run_git(["rev-parse", "--verify", f"{value}^{{commit}}"]).stdout.strip()
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"unknown Git commit: {value}") from exc


def replay_at_commit(snapshot_path, commit):
    """Replay in a detached worktree.

    Cross-version replay is guaranteed only for B101-and-later commits that
    contain this replay contract. Earlier commits are reported as unsupported
    instead of silently using current code.

    Permanent fixtures may be stored as .json.gz.b64. Before invoking an older
    B101-era target checkout, B103 materializes the immutable payload to a
    temporary JSON file so the target does not need to understand the archive
    wrapper.
    """
    snapshot_path = Path(snapshot_path).resolve()
    snapshot = load_snapshot(snapshot_path)
    target_sha = _resolve_commit(commit)
    if target_sha == current_git_commit():
        replayed = replay_current(snapshot)
        return {
            "target_commit": target_sha,
            "replayed_output": replayed,
            "diff": diff_replay(snapshot, replayed),
        }

    with tempfile.TemporaryDirectory(prefix="chaselights-replay-") as tmp:
        worktree = Path(tmp) / "repo"
        replay_input = snapshot_path
        if snapshot_path.name.endswith(".json.gz.b64"):
            replay_input = Path(tmp) / f"{snapshot['snapshot_id']}.json"
            replay_input.write_text(
                json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        try:
            _run_git(["worktree", "add", "--detach", str(worktree), target_sha])
            target_script = worktree / "field_snapshot.py"
            if not target_script.exists():
                raise RuntimeError(
                    "target commit predates the B101 replay contract; "
                    "cross-version replay is supported from B101 onward"
                )
            replay_env = dict(os.environ)
            replay_env.pop("GITHUB_SHA", None)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(target_script),
                    "_replay-json",
                    "--snapshot",
                    str(replay_input),
                ],
                cwd=str(worktree),
                env=replay_env,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            payload = json.loads(proc.stdout)
            return {
                "target_commit": target_sha,
                "replayed_output": payload["replayed_output"],
                "diff": payload["diff"],
            }
        finally:
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(worktree)],
                cwd=str(_PROJECT_ROOT),
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )


def capture_live(place_id, *, valid_at=None, output_dir=DEFAULT_SNAPSHOT_DIR, lang="zh-TW"):
    """Capture one forecast row from the same fetch/scoring execution."""
    import fetch_data

    spot = find_spot(place_id)
    captured_at = datetime.now(timezone.utc)
    target = _offset_aware_iso(valid_at) if valid_at else captured_at
    if target is None:
        raise ValueError("--valid-at must be offset-aware ISO8601")
    target_epoch = target.astimezone(timezone.utc).timestamp()
    selected = {"distance": None, "event": None}

    def sink(event):
        distance = abs(float(event["forecast_valid_epoch"]) - target_epoch)
        if selected["distance"] is None or distance < selected["distance"]:
            selected["distance"] = distance
            selected["event"] = event

    result = fetch_data.fetch_weather_for_spot(
        spot,
        lang=lang,
        snapshot_sink=sink,
    )
    if not result or selected["event"] is None:
        raise RuntimeError(f"unable to capture weather snapshot for {place_id}")
    snapshot = build_snapshot_from_event(
        place_id,
        selected["event"],
        captured_at=captured_at,
    )
    return write_snapshot(snapshot, output_dir)


def _snapshot_source_fingerprints(snapshot):
    source = snapshot.get("source_payloads") or {}
    return {
        "camera_weather_raw_sha256": hashlib.sha256(
            _canonical_json(source.get("camera_weather_raw"))
        ).hexdigest(),
        "spatial_weather_raw_sha256": hashlib.sha256(
            _canonical_json(source.get("spatial_weather_raw"))
        ).hexdigest(),
        "normalized_input_sha256": hashlib.sha256(
            _canonical_json(snapshot.get("normalized_input") or {})
        ).hexdigest(),
    }


def _revision_metric_view(snapshot):
    item = snapshot.get("normalized_input") or {}
    return {
        "visibility_km": (
            round(float(item["vis"]) / 1000.0, 3)
            if isinstance(item.get("vis"), (int, float))
            else None
        ),
        "low_cloud_pct": item.get("c_low"),
        "mid_cloud_pct": item.get("c_mid"),
        "high_cloud_pct": item.get("c_high"),
        "rh_pct": item.get("rh"),
        "precipitation_mm": item.get("precipitation"),
        "wind_ms": item.get("wind"),
        "temperature_c": item.get("temp"),
        "dew_point_c": item.get("dew"),
        "lcl_agl_m": item.get("cloud_base_agl"),
        "sun_elevation_deg": item.get("sun_elevation"),
    }


def _value_change(old, new):
    change = {"from": old, "to": new}
    if (
        isinstance(old, (int, float))
        and not isinstance(old, bool)
        and isinstance(new, (int, float))
        and not isinstance(new, bool)
    ):
        change["delta"] = round(float(new) - float(old), 6)
    return change


def compare_forecast_revisions(snapshots):
    """Compare multiple immutable captures of the same forecast-valid row.

    This compares the *recorded* outputs of each capture. It therefore exposes
    forecast/provider revisions even when model commits also changed. Use matrix
    replay separately when the goal is to isolate model-version effects on one
    fixed snapshot.
    """
    if len(snapshots) < 2:
        raise ValueError("compare-revisions requires at least two snapshots")

    place_ids = {str(s.get("place_id") or "") for s in snapshots}
    valid_epochs = {int(s.get("forecast_valid_epoch")) for s in snapshots}
    if len(place_ids) != 1:
        raise ValueError("revision snapshots must have the same place_id")
    if len(valid_epochs) != 1:
        raise ValueError("revision snapshots must have the same forecast_valid_at")

    ordered = sorted(
        snapshots,
        key=lambda s: _offset_aware_iso(s["captured_at"]).astimezone(timezone.utc),
    )
    rows = []
    for snapshot in ordered:
        captured = _offset_aware_iso(snapshot["captured_at"])
        valid = _offset_aware_iso(snapshot["forecast_valid_at"])
        scores = (snapshot.get("recorded_output") or {}).get(
            "opportunity_scores", {}
        )
        rows.append({
            "snapshot_id": snapshot["snapshot_id"],
            "captured_at": snapshot["captured_at"],
            "forecast_valid_at": snapshot["forecast_valid_at"],
            "lead_time_seconds": int(
                (valid.astimezone(timezone.utc) - captured.astimezone(timezone.utc))
                .total_seconds()
            ),
            "model_commit": snapshot["provenance"]["git_commit"],
            "fingerprints": _snapshot_source_fingerprints(snapshot),
            "metrics": _revision_metric_view(snapshot),
            "opportunities": {
                oid: _stable_outcome(outcome)
                for oid, outcome in sorted(scores.items())
            },
        })

    transitions = []
    for previous, current in zip(rows, rows[1:]):
        input_changed = (
            previous["fingerprints"]["normalized_input_sha256"]
            != current["fingerprints"]["normalized_input_sha256"]
        )
        model_changed = previous["model_commit"] != current["model_commit"]
        if input_changed and model_changed:
            classification = "mixed_forecast_and_model_revision"
        elif input_changed:
            classification = "forecast_data_revision"
        elif model_changed:
            classification = "model_revision_only"
        else:
            classification = "no_normalized_or_model_change"

        metric_changes = {}
        for key in sorted(set(previous["metrics"]) | set(current["metrics"])):
            old = previous["metrics"].get(key)
            new = current["metrics"].get(key)
            if old != new:
                metric_changes[key] = _value_change(old, new)

        opportunity_changes = {}
        for oid in sorted(
            set(previous["opportunities"]) | set(current["opportunities"])
        ):
            old = previous["opportunities"].get(oid)
            new = current["opportunities"].get(oid)
            if old != new:
                detail = {"from": old, "to": new}
                old_score = (old or {}).get("score")
                new_score = (new or {}).get("score")
                if isinstance(old_score, (int, float)) and isinstance(
                    new_score, (int, float)
                ):
                    detail["score_delta"] = new_score - old_score
                opportunity_changes[oid] = detail

        transitions.append({
            "from_snapshot_id": previous["snapshot_id"],
            "to_snapshot_id": current["snapshot_id"],
            "capture_interval_seconds": int(
                (
                    _offset_aware_iso(current["captured_at"]).astimezone(timezone.utc)
                    - _offset_aware_iso(previous["captured_at"]).astimezone(
                        timezone.utc
                    )
                ).total_seconds()
            ),
            "classification": classification,
            "camera_raw_changed": (
                previous["fingerprints"]["camera_weather_raw_sha256"]
                != current["fingerprints"]["camera_weather_raw_sha256"]
            ),
            "spatial_raw_changed": (
                previous["fingerprints"]["spatial_weather_raw_sha256"]
                != current["fingerprints"]["spatial_weather_raw_sha256"]
            ),
            "normalized_input_changed": input_changed,
            "model_commit_changed": model_changed,
            "metric_changes": metric_changes,
            "opportunity_changes": opportunity_changes,
        })

    return {
        "place_id": ordered[0]["place_id"],
        "forecast_valid_at": ordered[0]["forecast_valid_at"],
        "revision_count": len(rows),
        "rows": rows,
        "transitions": transitions,
    }


def _print_show(snapshot):
    recorded = snapshot["recorded_output"]["opportunity_scores"]
    print(
        f"{snapshot['snapshot_id']}  {snapshot['place_name']}\n"
        f"captured: {snapshot['captured_at']}\n"
        f"forecast: {snapshot['forecast_valid_at']}\n"
        f"commit:   {snapshot['provenance']['git_commit']}\n"
        f"status:   {snapshot['observation']['status']}"
    )
    for oid, row in sorted(recorded.items()):
        print(
            f"{oid}: score={row.get('score')} "
            f"confidence={row.get('score_confidence')} "
            f"state={row.get('condition_state')}"
        )


def _parser():
    parser = argparse.ArgumentParser(description="ChaseLights B101 field snapshot tool")
    sub = parser.add_subparsers(dest="command", required=True)

    capture = sub.add_parser("capture")
    capture.add_argument("--place", required=True)
    capture.add_argument("--valid-at")
    capture.add_argument("--output-dir", default=str(DEFAULT_SNAPSHOT_DIR))
    capture.add_argument("--lang", default="zh-TW")

    validate = sub.add_parser("validate")
    validate.add_argument("snapshot")

    show = sub.add_parser("show")
    show.add_argument("snapshot")

    replay = sub.add_parser("replay")
    replay.add_argument("snapshot")
    target = replay.add_mutually_exclusive_group()
    target.add_argument("--original", action="store_true")
    target.add_argument("--commit")

    matrix = sub.add_parser("matrix")
    matrix.add_argument("snapshot")
    matrix.add_argument("--commits", nargs="+", required=True)

    revisions = sub.add_parser("compare-revisions")
    revisions.add_argument("snapshots", nargs="+")
    revisions.add_argument("--output")

    internal = sub.add_parser("_replay-json")
    internal.add_argument("--snapshot", required=True)

    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    if args.command == "capture":
        path = capture_live(
            args.place,
            valid_at=args.valid_at,
            output_dir=args.output_dir,
            lang=args.lang,
        )
        print(path)
        return 0
    if args.command == "validate":
        snapshot = load_snapshot(args.snapshot)
        print(f"{snapshot['snapshot_id']}: valid")
        return 0
    if args.command == "show":
        _print_show(load_snapshot(args.snapshot))
        return 0
    if args.command == "_replay-json":
        snapshot = load_snapshot(args.snapshot)
        replayed = replay_current(snapshot)
        print(json.dumps({
            "replayed_output": replayed,
            "diff": diff_replay(snapshot, replayed),
        }, ensure_ascii=False))
        return 0
    if args.command == "replay":
        snapshot = load_snapshot(args.snapshot)
        if args.original:
            target = snapshot["provenance"]["git_commit"]
        else:
            target = args.commit or "current"
        result = replay_at_commit(args.snapshot, target)
        print(json.dumps(result["diff"], ensure_ascii=False, indent=2))
        return 0
    if args.command == "compare-revisions":
        snapshots = [load_snapshot(path) for path in args.snapshots]
        payload = compare_forecast_revisions(snapshots)
        rendered = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        else:
            print(rendered)
        return 0
    if args.command == "matrix":
        snapshot = load_snapshot(args.snapshot)
        rows = []
        for value in args.commits:
            if value == "original":
                value = snapshot["provenance"]["git_commit"]
            result = replay_at_commit(args.snapshot, value)
            rows.append({
                "target_commit": result["target_commit"],
                "match_recorded": result["diff"]["match"],
                "different_opportunity_ids": result["diff"][
                    "different_opportunity_ids"
                ],
                "comparison": result["diff"]["comparison"],
            })
        print(json.dumps({
            "snapshot_id": snapshot["snapshot_id"],
            "rows": rows,
        }, ensure_ascii=False, indent=2))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
