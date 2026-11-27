"""CL-DATA-115: compact per-place `now` sidecar for the homepage card.

Background
----------
CL-UI-115 shipped a card weather row that renders the place's CURRENT hour.
The browser obtained it by lazily fetching `weather_details/<region>/<place>.json`
(~2.3 MB per place, concurrency 4) — hundreds of MB on a 124-card page. This
tool runs inside the SAME publish workflow, after the evaluation bundle, and
reduces the SAME already-hydrated shards to one tiny artifact:

    {"generated_at": "<bundle stamp>",
     "source_bundle": "<bundle filename>",
     "hours": 168,
     "places": {"<place_id>": {"local_date": "YYYY-MM-DD", "hour": "HH:00",
                               "wmo": <int|null>, "temp_c": <num|null>,
                               "vis_km": <num|null>, "is_today": true}}}

Derivation rules (deliberately a port of the shipped client picker,
`clui115NowHourRow` in assets/app.js — this file only moves the same pick to
publish time; it changes NO evaluation logic, threshold or verdict, and it
never re-runs the evaluator):

  1. the place's local "today" and local hour come from the place's own
     timezone (`spot.timezone` in the shard, else the bundle's
     `timezone_display.iana`, else the shard's fixed `utc_offset_seconds`);
  2. the row whose local_date is today and whose hour is the current local
     hour is emitted; if today is covered but that exact hour is not served,
     the nearest edge row OF TODAY is emitted and its own `hour` label says
     which hour it is (never a fabricated "now");
  3. when the shard has no row for the place-local today, the place is OMITTED
     entirely — the card then keeps its day-weather chip. That is the honest
     fallback already shipped in CL-UI-115; a stale shard must never wear a
     `now` row.

Provenance / staleness
----------------------
`generated_at` is the bundle's own stamp and `source_bundle` the bundle's
filename, so a sidecar that lags its bundle is detectable by a client. The
generator refuses to write at all (exit 3, `NOW_SIDECAR_STALE_SHARDS`) when
the newest served row across the shard set predates the bundle's day: a stale
sidecar is worse than none.

Determinism
-----------
The default evaluation instant is the bundle's `generated_at` (not the wall
clock), so the artifact is a pure function of (bundle, shards). Identical
inputs produce byte-identical output. `--now` exists for tests/replays only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BUNDLE = ROOT / "apps/web-v2/evaluations-latest.json"
DEFAULT_WEATHER_DIR = ROOT / "weather_details"
DEFAULT_OUT = ROOT / "apps/web-v2/now-latest.json"

ARTIFACT_VERSION = "now-sidecar@1"

EXIT_BAD_BUNDLE = 2
EXIT_STALE = 3
EXIT_NO_SHARDS = 4

ERR_BAD_BUNDLE = "NOW_SIDECAR_BAD_BUNDLE"
ERR_STALE = "NOW_SIDECAR_STALE_SHARDS"
ERR_NO_SHARDS = "NOW_SIDECAR_NO_SHARDS"

_HHMM = re.compile(r"(\d{2}):(\d{2})")


# ---------------------------------------------------------------- time helpers
def parse_instant(value):
    """ISO-8601 (with Z or an offset, optional fraction) → aware UTC datetime."""
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value or "").strip()
        if not text:
            raise ValueError("empty instant")
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def zone_for(tz_name, offset_seconds=None):
    """IANA zone, else a fixed offset, else UTC. Never raises."""
    if tz_name:
        try:
            from zoneinfo import ZoneInfo  # noqa: PLC0415

            return ZoneInfo(str(tz_name))
        except Exception:  # noqa: BLE001 — missing tzdata is a fallback, not a failure
            pass
    if offset_seconds is not None:
        try:
            return timezone(timedelta(seconds=int(offset_seconds)))
        except (TypeError, ValueError):
            pass
    return timezone.utc


def local_parts(now_utc, tz_name, offset_seconds=None):
    """(YYYY-MM-DD, minutes-since-midnight) in the place's own timezone."""
    local = now_utc.astimezone(zone_for(tz_name, offset_seconds))
    return local.strftime("%Y-%m-%d"), local.hour * 60 + local.minute


# ---------------------------------------------------------------- row helpers
def row_parts(row):
    """Normalise one shard hour → {row, date, minutes, hhmm} or None."""
    if not isinstance(row, dict):
        return None
    stamp = str(row.get("time") or "")
    match = _HHMM.search(stamp)
    if not match:
        return None
    date = row.get("local_date")
    if not isinstance(date, str) or not date:
        date = stamp[:10]
    if not date:
        return None
    hour, minute = int(match.group(1)), int(match.group(2))
    if hour > 23 or minute > 59:
        return None
    return {
        "row": row,
        "date": date,
        "minutes": hour * 60 + minute,
        "hhmm": "%02d:%02d" % (hour, minute),
    }


def pick_now_row(rows, local_date, minutes):
    """The current-hour row of the place-local today, or None (see module docs)."""
    parts = [p for p in (row_parts(r) for r in rows or []) if p]
    todays = sorted((p for p in parts if p["date"] == local_date),
                    key=lambda p: p["minutes"])
    if not todays:
        return None
    current = (minutes // 60) * 60
    exact = next((p for p in todays if p["minutes"] == current), None)
    if exact:
        return exact
    before = [p for p in todays if p["minutes"] < current]
    after = [p for p in todays if p["minutes"] > current]
    return before[-1] if before else (after[0] if after else todays[0])


def _number(value):
    """Finite int/float passthrough (no re-rounding: rounding could flip a
    `vis < 1 km` fog read), anything else → None."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if value != value or value in (float("inf"), float("-inf")):
            return None
        return value
    return None


def _wmo(value):
    num = _number(value)
    return int(num) if num is not None else None


# ---------------------------------------------------------------- derivation
def bundle_index(bundle):
    """place_id → declared display timezone (iana), from one bundle."""
    index = {}
    for place in bundle.get("places") or []:
        pid = place.get("place_id")
        if not isinstance(pid, str) or not pid:
            continue
        tz = (place.get("timezone_display") or {}).get("iana")
        index[pid] = tz if isinstance(tz, str) and tz else None
    return index


def shard_path(weather_dir, place_id):
    region = place_id.split("-", 1)[0]
    return Path(weather_dir) / region / ("%s.json" % place_id)


def load_shard(weather_dir, place_id):
    path = shard_path(weather_dir, place_id)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_bytes().decode("utf-8"))
    except (ValueError, OSError):
        return None


def derive(bundle, weather_dir, now=None, stats: dict | None = None):
    """(artifact dict, newest row instant or None, stats counts).

    Pure: reads only `bundle` and the shards under `weather_dir`. Raises
    NowSidecarError for the two named refusals (no shards / stale shards);
    staleness is judged against the bundle's own day, so the caller can decide
    whether to write.
    """
    stats = stats if stats is not None else Counter()
    generated_at = bundle.get("generated_at")
    if not isinstance(generated_at, str) or not generated_at:
        raise NowSidecarError(ERR_BAD_BUNDLE, "bundle has no generated_at")
    try:
        bundle_stamp = parse_instant(generated_at)
    except ValueError as exc:
        raise NowSidecarError(ERR_BAD_BUNDLE, "bad generated_at %r: %s" % (generated_at, exc)) from exc

    try:
        now_utc = parse_instant(now) if now else bundle_stamp
    except ValueError as exc:
        raise NowSidecarError(ERR_BAD_BUNDLE, "bad --now %r: %s" % (now, exc)) from exc

    tz_hints = bundle_index(bundle)
    place_ids = sorted(tz_hints)
    places = {}
    newest = None
    shards_read = 0

    for pid in place_ids:
        doc = load_shard(weather_dir, pid)
        if not doc:
            stats["no_shard"] += 1
            continue
        shards_read += 1
        spot = doc.get("spot") or {}
        rows = spot.get("hourly_forecast") or []
        if not isinstance(rows, list):
            stats["no_shard"] += 1
            continue
        for row in rows:
            instant = _row_instant(row, spot.get("utc_offset_seconds"))
            if instant and (newest is None or instant > newest):
                newest = instant
        tz_name = spot.get("timezone") or tz_hints.get(pid)
        offset = spot.get("utc_offset_seconds")
        local_date, minutes = local_parts(now_utc, tz_name, offset)
        pick = pick_now_row(rows, local_date, minutes)
        if not pick:
            stats["no_today_row"] += 1
            continue
        row = pick["row"]
        row_tz = row.get("timezone")
        if tz_name and isinstance(row_tz, str) and row_tz and row_tz != tz_name:
            # A row stamped for another zone is never a "now" for this place.
            stats["timezone_mismatch"] += 1
            continue
        places[pid] = {
            "local_date": pick["date"],
            "hour": pick["hhmm"],
            "wmo": _wmo(row.get("weather_code")),
            "temp_c": _number(row.get("temp")),
            "vis_km": _number(row.get("visibility")),
            "is_today": True,
        }

    if shards_read == 0:
        raise NowSidecarError(ERR_NO_SHARDS, "no readable shard under %s for any bundle place" % weather_dir)
    if newest is None:
        raise NowSidecarError(ERR_NO_SHARDS, "shard set carries no usable hourly row")

    # Stale sidecar is worse than none: refuse when the newest served row
    # predates the bundle's day (a shard set from an older generation).
    if newest.date() < bundle_stamp.date():
        raise NowSidecarError(
            ERR_STALE,
            "newest shard row %s predates bundle day %s (generated_at %s)"
            % (newest.isoformat().replace("+00:00", "Z"), bundle_stamp.date(), generated_at),
        )

    hours = bundle.get("forecast_hours")
    payload = {
        "generated_at": generated_at,
        "source_bundle": None,  # filled by the caller from the bundle path
        "hours": hours if isinstance(hours, int) else None,
        "places": places,
    }
    stats["shards_read"] = shards_read
    stats["newest_row"] = newest.isoformat().replace("+00:00", "Z")
    return payload, newest, stats


def _row_instant(row, offset_seconds=None):
    """UTC instant of one shard row: time_utc when present, else local + offset."""
    if not isinstance(row, dict):
        return None
    raw = row.get("time_utc")
    if isinstance(raw, str) and raw:
        try:
            return parse_instant(raw)
        except ValueError:
            pass
    parts = row_parts(row)
    if not parts:
        return None
    try:
        naive = datetime.strptime(parts["date"] + " " + parts["hhmm"], "%Y-%m-%d %H:%M")
    except ValueError:
        return None
    offset = offset_seconds
    if offset is None:
        offset = 0
    try:
        return (naive - timedelta(seconds=int(offset))).replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None


class NowSidecarError(RuntimeError):
    """Named refusal: never a silent partial write."""

    def __init__(self, code, message):
        super().__init__("%s: %s" % (code, message))
        self.code = code
        self.message = message


def render(payload):
    """Deterministic bytes: compact separators, sorted places, one trailing \\n."""
    ordered = {
        "generated_at": payload["generated_at"],
        "source_bundle": payload["source_bundle"],
        "hours": payload["hours"],
        "places": {k: payload["places"][k] for k in sorted(payload["places"])},
    }
    return (json.dumps(ordered, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def write_atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)
    return path


def build(bundle_path, weather_dir, out_path, now=None, stats=None):
    """Full pipeline: read bundle → derive → refuse-if-stale → write. Returns
    (payload, artifact bytes, stats)."""
    bundle_path = Path(bundle_path)
    try:
        bundle = json.loads(bundle_path.read_bytes().decode("utf-8"))
    except (ValueError, OSError) as exc:
        raise NowSidecarError(ERR_BAD_BUNDLE, "cannot read bundle %s: %s" % (bundle_path, exc)) from exc
    if not isinstance(bundle, dict) or not isinstance(bundle.get("places"), list):
        raise NowSidecarError(ERR_BAD_BUNDLE, "bundle %s has no places[]" % bundle_path)

    payload, _newest, stats = derive(bundle, weather_dir, now=now, stats=stats)
    # Provenance names the bundle the numbers came from; the artifact is only
    # written AFTER the staleness refusal inside derive().
    payload["source_bundle"] = bundle_path.name
    data = render(payload)
    write_atomic(out_path, data)
    return payload, data, stats


def _report(payload, data, stats, out_path):
    newest = stats.get("newest_row")
    print("now sidecar: %s" % out_path)
    print("  generated_at=%s source_bundle=%s hours=%s" % (
        payload["generated_at"], payload["source_bundle"], payload["hours"]))
    print("  places=%d  omitted: no_shard=%d no_today_row=%d timezone_mismatch=%d" % (
        len(payload["places"]), stats.get("no_shard", 0),
        stats.get("no_today_row", 0), stats.get("timezone_mismatch", 0)))
    print("  shards_read=%d newest_row=%s bytes=%d" % (
        stats.get("shards_read", 0),
        newest or "-",
        len(data)))


def main(argv=None):
    parser = argparse.ArgumentParser(description="CL-DATA-115 compact `now` sidecar")
    parser.add_argument("--bundle", default=str(DEFAULT_BUNDLE),
                        help="evaluation bundle (default: apps/web-v2/evaluations-latest.json)")
    parser.add_argument("--weather-dir", default=str(DEFAULT_WEATHER_DIR),
                        help="hydrated weather_details root (default: ./weather_details)")
    parser.add_argument("--out", default=str(DEFAULT_OUT),
                        help="artifact path (default: apps/web-v2/now-latest.json)")
    parser.add_argument("--now", default=None,
                        help="evaluation instant override (default: the bundle's generated_at)")
    args = parser.parse_args(argv)
    try:
        payload, data, stats = build(args.bundle, args.weather_dir, args.out, now=args.now)
    except NowSidecarError as exc:
        sys.stderr.write("ERROR %s\n" % exc)
        return EXIT_STALE if exc.code == ERR_STALE else (
            EXIT_NO_SHARDS if exc.code == ERR_NO_SHARDS else EXIT_BAD_BUNDLE)
    _report(payload, data, stats, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
