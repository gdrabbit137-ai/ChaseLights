"""B115 request-driven Field Snapshot capture helpers.

A capture request is a small, reviewable JSON file that tells the fixed GitHub
Actions workflow which production commit, Place, and forecast-valid time to
capture. The workflow captures from that immutable production commit, preserves
the snapshot as an artifact, and can optionally register the result as a
permanent replay baseline on the request branch.

This module never turns a forecast snapshot into field ground truth.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from field_snapshot import load_snapshot

REQUEST_SCHEMA_VERSION = "field-snapshot-capture-request-r4.2-1"
REGISTRY_SCHEMA_VERSION = "field-snapshot-baseline-registry-r4.2-1"
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_REQUEST_ID = re.compile(r"^FSCR-[A-Za-z0-9._-]+$")
_TOKEN = re.compile(r"^[A-Za-z0-9._/@:+-]+$")


def _offset_aware_iso(value):
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None or dt.utcoffset() is None:
        return None
    return dt


def validate_request(payload):
    errors = []
    if payload.get("schema_version") != REQUEST_SCHEMA_VERSION:
        errors.append("request schema mismatch")

    request_id = str(payload.get("request_id") or "")
    if not _REQUEST_ID.match(request_id):
        errors.append("request_id must match FSCR-[A-Za-z0-9._-]+")

    place_id = str(payload.get("place_id") or "")
    if not _TOKEN.match(place_id):
        errors.append("place_id missing or invalid")

    valid_at = _offset_aware_iso(payload.get("valid_at"))
    if valid_at is None:
        errors.append("valid_at must be offset-aware ISO8601")

    capture_ref = str(payload.get("capture_ref") or "").lower()
    if not _SHA40.match(capture_ref):
        errors.append("capture_ref must be a full 40-character Git commit SHA")

    scene_family = str(payload.get("scene_family") or "")
    if not _TOKEN.match(scene_family):
        errors.append("scene_family missing or invalid")

    revision_group = payload.get("revision_group")
    if revision_group is not None and not _TOKEN.match(str(revision_group)):
        errors.append("revision_group contains unsupported characters")

    persist = payload.get("persist", True)
    if not isinstance(persist, bool):
        errors.append("persist must be boolean")

    limitations = payload.get("limitations", [])
    if not isinstance(limitations, list) or any(
        not isinstance(item, str) or not item.strip() for item in limitations
    ):
        errors.append("limitations must be an array of non-empty strings")

    note = payload.get("note")
    if note is not None and not isinstance(note, str):
        errors.append("note must be a string")

    return errors


def load_request(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate_request(payload)
    if errors:
        raise ValueError("\n".join(errors))
    return payload


def request_revision_group(request, snapshot):
    explicit = str(request.get("revision_group") or "").strip()
    if explicit:
        return explicit
    return f"{snapshot['place_id']}@{snapshot['forecast_valid_at']}"


def _summary_value(target, key, value):
    if value is not None:
        target[key] = value


def summarize_opportunity(outcome):
    runtime = outcome.get("runtime") or {}
    spatial = runtime.get("spatial_mist_context") or {}
    summary = {
        "score": outcome.get("score"),
        "score_confidence": outcome.get("score_confidence"),
        "condition_state": outcome.get("condition_state"),
        "runtime_reason": runtime.get("reason"),
    }

    for key in (
        "minimum_sufficient_score_hint",
        "runtime_confidence_hint",
        "directional_mist_negative_evidence",
    ):
        _summary_value(summary, key, runtime.get(key))

    for key in (
        "target_sample_count",
        "mist_target_count",
        "directional_mist_target_count",
        "clear_target_count",
        "clear_bearing_count",
        "broad_clear_target_sector",
    ):
        _summary_value(summary, key, spatial.get(key))

    return summary


def build_recorded_summary(snapshot):
    scores = (snapshot.get("recorded_output") or {}).get(
        "opportunity_scores", {}
    )
    return {
        oid: summarize_opportunity(outcome or {})
        for oid, outcome in sorted(scores.items())
    }


def _forecast_local_time(snapshot):
    valid = _offset_aware_iso(snapshot["forecast_valid_at"])
    timezone_name = str(snapshot.get("timezone") or "UTC")
    try:
        tz = ZoneInfo(timezone_name)
    except Exception:
        return snapshot["forecast_valid_at"]
    return valid.astimezone(tz).isoformat()


def build_metadata(snapshot, request):
    return {
        "request_schema_version": request["schema_version"],
        "request_id": request["request_id"],
        "snapshot_file": f"{snapshot['snapshot_id']}.json",
        "snapshot_id": snapshot["snapshot_id"],
        "place_id": snapshot["place_id"],
        "captured_at": snapshot["captured_at"],
        "forecast_valid_at": snapshot["forecast_valid_at"],
        "forecast_local_time": _forecast_local_time(snapshot),
        "capture_ref_requested": request["capture_ref"],
        "git_commit": snapshot["provenance"]["git_commit"],
        "payload_sha256": snapshot["integrity"]["payload_sha256"],
        "observation_status": snapshot["observation"]["status"],
        "scene_family": request["scene_family"],
        "revision_group": request_revision_group(request, snapshot),
    }


def build_registry_entry(
    snapshot,
    request,
    *,
    archive_path,
    metadata_path,
    workflow_run_id=None,
    artifact_name=None,
    source_branch=None,
):
    limitations = list(request.get("limitations") or [])
    limitations.extend(
        [
            (
                "This record is an immutable forecast snapshot captured by the "
                "request-driven Field Snapshot workflow; it is not an observed scene."
            ),
            (
                "Forecast stability or replay reproducibility does not establish "
                "forecast accuracy."
            ),
            (
                "No field photograph or reviewed observation is attached unless a "
                "separate field-validation case explicitly says otherwise."
            ),
        ]
    )
    source = {
        "capture_request_id": request["request_id"],
    }
    if workflow_run_id is not None:
        source["workflow_run_id"] = int(workflow_run_id)
    if artifact_name:
        source["artifact_name"] = artifact_name
    if source_branch:
        source["source_branch"] = source_branch

    return {
        "snapshot_id": snapshot["snapshot_id"],
        "place_id": snapshot["place_id"],
        "scene_family": request["scene_family"],
        "revision_group": request_revision_group(request, snapshot),
        "archive_path": archive_path,
        "metadata_path": metadata_path,
        "captured_at": snapshot["captured_at"],
        "forecast_valid_at": snapshot["forecast_valid_at"],
        "forecast_local_time": _forecast_local_time(snapshot),
        "model_commit": snapshot["provenance"]["git_commit"],
        "payload_sha256": snapshot["integrity"]["payload_sha256"],
        "observation_status": snapshot["observation"]["status"],
        "source": source,
        "recorded_summary": build_recorded_summary(snapshot),
        "limitations": limitations,
    }


def register_baseline(registry_path, entry):
    path = Path(registry_path)
    registry = json.loads(path.read_text(encoding="utf-8"))
    if registry.get("schema_version") != REGISTRY_SCHEMA_VERSION:
        raise ValueError("baseline registry schema mismatch")
    baselines = registry.get("baselines")
    if not isinstance(baselines, list):
        raise ValueError("baseline registry baselines must be an array")

    snapshot_id = entry["snapshot_id"]
    if any(row.get("snapshot_id") == snapshot_id for row in baselines):
        raise ValueError(f"snapshot already registered: {snapshot_id}")

    baselines.append(deepcopy(entry))
    path.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return entry


def _cmd_validate(args):
    request = load_request(args.request)
    print(json.dumps(request, ensure_ascii=False, indent=2))
    return 0


def _cmd_metadata(args):
    request = load_request(args.request)
    snapshot = load_snapshot(args.snapshot)
    metadata = build_metadata(snapshot, request)
    rendered = json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


def _cmd_register(args):
    request = load_request(args.request)
    snapshot = load_snapshot(args.snapshot)
    entry = build_registry_entry(
        snapshot,
        request,
        archive_path=args.archive_path,
        metadata_path=args.metadata_path,
        workflow_run_id=args.workflow_run_id,
        artifact_name=args.artifact_name,
        source_branch=args.source_branch,
    )
    register_baseline(args.registry, entry)
    print(json.dumps(entry, ensure_ascii=False, indent=2))
    return 0


def _cmd_make(args):
    payload = {
        "schema_version": REQUEST_SCHEMA_VERSION,
        "request_id": args.request_id,
        "place_id": args.place,
        "valid_at": args.valid_at,
        "capture_ref": args.capture_ref.lower(),
        "scene_family": args.scene_family,
        "persist": not args.artifact_only,
    }
    if args.revision_group:
        payload["revision_group"] = args.revision_group
    if args.note:
        payload["note"] = args.note
    errors = validate_request(payload)
    if errors:
        raise ValueError("\n".join(errors))
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    Path(args.output).write_text(rendered, encoding="utf-8")
    print(args.output)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-request")
    validate.add_argument("request")
    validate.set_defaults(func=_cmd_validate)

    metadata = sub.add_parser("metadata")
    metadata.add_argument("--request", required=True)
    metadata.add_argument("--snapshot", required=True)
    metadata.add_argument("--output")
    metadata.set_defaults(func=_cmd_metadata)

    register = sub.add_parser("register")
    register.add_argument("--request", required=True)
    register.add_argument("--snapshot", required=True)
    register.add_argument("--registry", required=True)
    register.add_argument("--archive-path", required=True)
    register.add_argument("--metadata-path", required=True)
    register.add_argument("--workflow-run-id")
    register.add_argument("--artifact-name")
    register.add_argument("--source-branch")
    register.set_defaults(func=_cmd_register)

    make = sub.add_parser("make-request")
    make.add_argument("--request-id", required=True)
    make.add_argument("--place", required=True)
    make.add_argument("--valid-at", required=True)
    make.add_argument("--capture-ref", required=True)
    make.add_argument("--scene-family", required=True)
    make.add_argument("--revision-group")
    make.add_argument("--note")
    make.add_argument("--artifact-only", action="store_true")
    make.add_argument("--output", default=".field_snapshot_capture_request.json")
    make.set_defaults(func=_cmd_make)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
