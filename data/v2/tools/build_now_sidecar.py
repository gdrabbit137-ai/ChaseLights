"""CL-DATA-115: compact per-place `now` sidecar for the homepage card.

Background
----------
CL-UI-115 shipped a card weather row that renders the place's CURRENT hour.
The browser obtained it by lazily fetching `weather_details/<region>/<place>.json`
(~2.3 MB per place, concurrency 4) — hundreds of MB on a 124-card page. This
tool runs inside the SAME publish workflow, after the evaluation bundle, and
reduces the SAME already-hydrated shards to one tiny artifact:

    {"artifact_version": "now-sidecar@1",
     "generated_at": "<bundle stamp>",
     "source_bundle": "<bundle filename>",
     "hours": 168,
     "places": {"<place_id>": {"local_date": "YYYY-MM-DD", "hour": "HH:00",
                               "wmo": <int|null>, "temp_c": <num|null>,
                               "vis_km": <num|null>, "is_today": true}}}

`hours` is NULLABLE: it is copied from the bundle's `forecast_hours` and is
`null` whenever the bundle omits it or carries a non-int value. `null` means
"the bundle did not declare a horizon", never "zero hours" — a client must not
render a horizon chip from it.

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

Per-place staleness (CL-DATA-115 review condition 2)
-----------------------------------------------------
Staleness is judged PER PLACE, never as a global max over the shard set: a
single fresh shard used to rescue 458 stale ones, and the artifact then stamped
`generated_at` (the bundle's) onto hours that belonged to an older forecast.
Every real shard carries its own `updated_at` and `data_stale`; a place whose
shard says `data_stale: true` — or whose `updated_at` is missing, unparseable,
or predates the bundle's own UTC day — is OMITTED (not flagged: the row shape
has no stale flag, and an omitted place degrades to the day chip exactly like a
place with no today row). The run reports `stale_shard` / `stale_data` counts.

`is_today: true` therefore means: this row is the current local hour of the
place's local today, sourced from a shard this same run considers fresh.

Refusals
--------
The generator refuses to write (and the workflow then publishes nothing) when:

  * no shard is readable at all                      → exit 4, NO_SHARDS
  * every readable shard is stale                    → exit 3, STALE_SHARDS
  * no place yields a today row                      → exit 3, STALE_SHARDS
  * fewer than COVERAGE_MIN of the bundle's places   → exit 5, COVERAGE
    are emitted (unless every shard is stale, which is already exit 3)
  * any place carries an unresolvable timezone       → exit 6, UNKNOWN_ZONE

The last one exists because a silent ZoneInfo fallback on a host without
`tzdata` labels the hour in the wrong zone; the workflow pip-installs `tzdata`
and the run fails loudly per place instead of degrading to UTC.

On any refusal the caller deletes the artifact this run owns (`--out`), so the
site 404s and the card falls back to the day chip instead of serving the
PREVIOUS now block as if it were current.

Provenance / horizon
--------------------
`generated_at` is the bundle's own stamp and `source_bundle` the bundle's
filename, so a sidecar that lags its bundle is detectable by a client. The
newest shard row can lag the bundle by up to ONE refresh cycle (the weather
refresh and the evaluation refresh are separate jobs), and the run prints that
horizon (`newest_row`) next to the emitted/total counts. Freshness itself is
enforced per place, never as a global max over the shard set.

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
EXIT_COVERAGE = 5
EXIT_UNKNOWN_ZONE = 6

ERR_BAD_BUNDLE = "NOW_SIDECAR_BAD_BUNDLE"
ERR_STALE = "NOW_SIDECAR_STALE_SHARDS"
ERR_NO_SHARDS = "NOW_SIDECAR_NO_SHARDS"
ERR_COVERAGE = "NOW_SIDECAR_COVERAGE"
ERR_UNKNOWN_ZONE = "NOW_SIDECAR_UNKNOWN_ZONE"

#: Minimum share of the bundle's places that must survive to a `now` row. A
#: generator that silently drops (almost) everything cannot pass: only a
#: wholesale-stale shard set is allowed to emit nothing, and that raises
#: ERR_STALE before this band is consulted.
COVERAGE_MIN = 0.60

_EXIT_BY_CODE = {
    ERR_STALE: EXIT_STALE,
    ERR_NO_SHARDS: EXIT_NO_SHARDS,
    ERR_COVERAGE: EXIT_COVERAGE,
    ERR_UNKNOWN_ZONE: EXIT_UNKNOWN_ZONE,
    ERR_BAD_BUNDLE: EXIT_BAD_BUNDLE,
}

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


class UnknownZone(ValueError):
    """The place's zone could not be resolved — never silently degrade to UTC."""


def zone_for(tz_name, offset_seconds=None):
    """IANA zone, else the shard's fixed offset, else UTC.

    An explicitly named zone that cannot be resolved (no `tzdata` on the host,
    or a typo) raises UnknownZone: falling back to UTC would silently mislabel
    the hour, which is worse than omitting the place.
    """
    if tz_name:
        from zoneinfo import ZoneInfo  # noqa: PLC0415

        try:
            return ZoneInfo(str(tz_name))
        except Exception as exc:  # noqa: BLE001 — ZoneInfoNotFoundError & friends
            raise UnknownZone("unresolvable zone %r (%s)" % (tz_name, type(exc).__name__)) from exc
    if offset_seconds is not None:
        try:
            return timezone(timedelta(seconds=int(offset_seconds)))
        except (TypeError, ValueError) as exc:
            raise UnknownZone("bad utc_offset_seconds %r" % (offset_seconds,)) from exc
    return timezone.utc


def local_parts(now_utc, tz_name, offset_seconds=None):
    """(YYYY-MM-DD, minutes-since-midnight) in the place's own timezone.

    Raises UnknownZone when the place's zone is unresolvable.
    """
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


def shard_freshness(doc, bundle_day):
    """(fresh, reason) for ONE shard, using the shard's OWN stamps.

    Fresh means: the shard does not declare `data_stale`, and its `updated_at`
    is a parseable instant whose UTC date is not older than the bundle's day.
    Anything we cannot prove fresh is treated as stale (fail-closed): a
    global max over the shard set let one fresh shard rescue hundreds of stale
    ones and stamp the bundle's `generated_at` onto hours of an older forecast.
    """
    spot = doc.get("spot") if isinstance(doc.get("spot"), dict) else {}
    if doc.get("data_stale") is True or spot.get("data_stale") is True:
        return False, "data_stale"
    raw = doc.get("updated_at") or spot.get("updated_at")
    if not isinstance(raw, str) or not raw.strip():
        return False, "no_updated_at"
    try:
        stamp = parse_instant(raw)
    except ValueError:
        return False, "bad_updated_at"
    if stamp.date() < bundle_day:
        return False, "before_bundle_day"
    return True, None


def derive(bundle, weather_dir, now=None, stats: dict | None = None):
    """(artifact dict, newest row instant or None, stats counts).

    Pure: reads only `bundle` and the shards under `weather_dir`. Raises
    NowSidecarError only for INPUT faults (unreadable bundle / no readable
    shard / unresolvable zone). Staleness is judged per shard against the
    bundle's own day and simply omits places; the publish decisions (nothing
    emitted, coverage floor) live in `check_publishable` so a caller can
    inspect the counts before refusing.
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
    fresh_shards = 0
    zone_failures = []

    for pid in place_ids:
        doc = load_shard(weather_dir, pid)
        if not doc:
            stats["no_shard"] += 1
            continue
        shards_read += 1
        spot = doc.get("spot") or {}
        rows = spot.get("hourly_forecast") or []
        # Per-place staleness FIRST: a stale shard contributes neither a row nor
        # a "newest" stamp, so one fresh shard cannot rescue the rest.
        fresh, reason = shard_freshness(doc, bundle_stamp.date())
        if not fresh:
            if reason == "data_stale":
                stats["stale_data"] += 1
            else:
                stats["stale_shard"] += 1
            continue
        fresh_shards += 1
        if not isinstance(rows, list):
            stats["no_shard"] += 1
            continue
        for row in rows:
            instant = _row_instant(row, spot.get("utc_offset_seconds"))
            if instant and (newest is None or instant > newest):
                newest = instant
        tz_name = spot.get("timezone") or tz_hints.get(pid)
        offset = spot.get("utc_offset_seconds")
        try:
            local_date, minutes = local_parts(now_utc, tz_name, offset)
        except UnknownZone as exc:
            # Hard per-place failure: never fall back to UTC and mislabel the hour.
            stats["tz_error"] += 1
            zone_failures.append("%s (%s)" % (pid, exc))
            continue
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
    if zone_failures:
        raise NowSidecarError(
            ERR_UNKNOWN_ZONE,
            "%d place(s) have an unresolvable timezone (install tzdata): %s"
            % (len(zone_failures), ", ".join(zone_failures[:8])),
        )

    hours = bundle.get("forecast_hours")
    payload = {
        "artifact_version": ARTIFACT_VERSION,
        "generated_at": generated_at,
        "source_bundle": None,  # filled by the caller from the bundle path
        "hours": hours if isinstance(hours, int) else None,
        "places": places,
    }
    stats["shards_read"] = shards_read
    stats["fresh_shards"] = fresh_shards
    stats["place_total"] = len(place_ids)
    stats["place_emitted"] = len(places)
    stats["newest_row"] = newest.isoformat().replace("+00:00", "Z") if newest else None
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
        "artifact_version": payload["artifact_version"],
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


def discard_artifact(path):
    """Delete the artifact THIS run owns (plus its .tmp), so a refusal leaves the
    site with a 404 on `now-latest.json` instead of the previous now block.

    Returns True when a stale artifact was removed.
    """
    path = Path(path)
    removed = False
    for target in (path.with_name(path.name + ".tmp"), path):
        try:
            if target.exists():
                target.unlink()
                removed = removed or target == path
        except OSError:
            pass
    return removed


def check_publishable(payload, stats):
    """Publish gate (CL-DATA-115 review conditions 2 + 5).

    Runs AFTER derivation, on the finished counts:
      * nothing emitted at all → excused only when every readable shard is
        stale (that is a wholesale-stale run, not a silent generator bug) —
        both refuse, so this raises ERR_STALE either way;
      * otherwise the emitted share must clear COVERAGE_MIN of the bundle's
        places, so a generator that silently drops the catalog cannot pass.
    """
    total = stats.get("place_total", 0)
    emitted = stats.get("place_emitted", 0)
    if emitted == 0:
        raise NowSidecarError(
            ERR_STALE,
            "no place emitted a row for its local today (%d shard(s) read, %d stale, "
            "no_shard=%d no_today_row=%d timezone_mismatch=%d)"
            % (stats.get("shards_read", 0),
               stats.get("stale_shard", 0) + stats.get("stale_data", 0),
               stats.get("no_shard", 0), stats.get("no_today_row", 0),
               stats.get("timezone_mismatch", 0)),
        )
    if total and emitted < total * COVERAGE_MIN:
        raise NowSidecarError(
            ERR_COVERAGE,
            "emitted %d/%d places (%.1f%%), below the %.0f%% floor — refusing to publish "
            "a sidecar that silently dropped the catalog"
            % (emitted, total, 100.0 * emitted / total, 100.0 * COVERAGE_MIN),
        )


def build(bundle_path, weather_dir, out_path, now=None, stats=None):
    """Full pipeline: read bundle → derive → publish gate → write. Returns
    (payload, artifact bytes, stats)."""
    bundle_path = Path(bundle_path)
    try:
        bundle = json.loads(bundle_path.read_bytes().decode("utf-8"))
    except (ValueError, OSError) as exc:
        raise NowSidecarError(ERR_BAD_BUNDLE, "cannot read bundle %s: %s" % (bundle_path, exc)) from exc
    if not isinstance(bundle, dict) or not isinstance(bundle.get("places"), list):
        raise NowSidecarError(ERR_BAD_BUNDLE, "bundle %s has no places[]" % bundle_path)

    payload, _newest, stats = derive(bundle, weather_dir, now=now, stats=stats)
    check_publishable(payload, stats)
    # Provenance names the bundle the numbers came from; the artifact is only
    # written AFTER the publish gate above.
    payload["source_bundle"] = bundle_path.name
    data = render(payload)
    write_atomic(out_path, data)
    return payload, data, stats


def _report(payload, data, stats, out_path):
    newest = stats.get("newest_row")
    total = stats.get("place_total", 0)
    emitted = stats.get("place_emitted", 0)
    pct = (100.0 * emitted / total) if total else 0.0
    print("now sidecar: %s" % out_path)
    print("  artifact_version=%s generated_at=%s source_bundle=%s hours=%s" % (
        payload["artifact_version"], payload["generated_at"], payload["source_bundle"],
        "null" if payload["hours"] is None else payload["hours"]))
    print("  places emitted=%d/%d (%.1f%%) floor=%.0f%%" % (
        emitted, total, pct, 100.0 * COVERAGE_MIN))
    print("  omitted: no_shard=%d no_today_row=%d timezone_mismatch=%d "
          "stale_shard=%d stale_data=%d tz_error=%d" % (
              stats.get("no_shard", 0), stats.get("no_today_row", 0),
              stats.get("timezone_mismatch", 0), stats.get("stale_shard", 0),
              stats.get("stale_data", 0), stats.get("tz_error", 0)))
    print("  shards_read=%d fresh_shards=%d newest_row=%s bytes=%d" % (
        stats.get("shards_read", 0), stats.get("fresh_shards", 0),
        newest or "-", len(data)))


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
        # A refusal must not leave the PREVIOUS now block standing: the client
        # has to 404 and fall back to the day chip. Only this run's artifact is
        # removed.
        if discard_artifact(args.out):
            sys.stderr.write("REMOVED stale artifact %s (refusal: client must fall back "
                             "to the day chip)\n" % args.out)
        return _EXIT_BY_CODE.get(exc.code, EXIT_BAD_BUNDLE)
    _report(payload, data, stats, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
