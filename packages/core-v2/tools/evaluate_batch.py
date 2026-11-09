#!/usr/bin/env python3
"""Batch V2 opportunity evaluation — GUIDANCE-only live verdicts (owner-authorized 2026-10-26).

Evaluates every genre-contracted opportunity against real Open-Meteo forecast
data (72h) plus deterministic astronomy, and publishes an evaluation-bundle
v0.1 artifact for the web-v2 UI.

Honesty contract (owner-ratified evaluation semantics):
- All conditions are GUIDANCE-mode with provisional/approved calibration.
  Results are guidance, never FAVORABLE: `live_recommendation` is always false
  and `runtime_availability` is GUIDANCE_ONLY. FAVORABLE stays locked until
  thresholds are calibrated against real shoot outcomes.
- REQUIRED-tier condition FAIL at an hour -> UNFAVORABLE for that hour.
  Any REQUIRED UNKNOWN -> NOT_EVALUABLE. Otherwise GUIDANCE_SATISFIED.
- Known-honest gaps stay UNKNOWN: water_surface_state and seasonal_state have
  no live observation source (propagate_unknown); landform_present is the
  owner-declared static presence (deterministic PASS).
- Provider provenance (URL, SHA256, retrieval time, grid point) is carried for
  every place; freshness is bounded by the pilot policy (6h -> STALE).

Usage:
  python packages/core-v2/tools/evaluate_batch.py --out apps/web-v2/evaluations-latest.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for entry in (str(ROOT / "packages/core-v2"), str(ROOT / "packages/models-v2"), str(ROOT)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from adapters import open_meteo_batch as adapter  # noqa: E402
from adapters.threshold_observations import METRIC_FIELDS, compare  # noqa: E402
from astro_hourly import (  # noqa: E402
    ASTRO_SAMPLING_PROVENANCE, WINDOW_SAMPLE_OFFSETS, hour_observations,
    sun_events_span, window_pass_profiles)

BUNDLE_VERSION = "0.1.0"
ASTRO_METRICS = {"sun_azimuth_deg", "sunrise_time_window", "sunset_window", "blue_hour_window",
                 "golden_hour_window", "astronomical_darkness",
                 "moon_illumination_fraction", "moon_altitude",
                 "moon_target_separation_deg", "moon_illuminance_proxy",
                 "galactic_core_altitude", "city_night_window",
                 "light_window", "daylight_window"}

# CL-UI-23: metrics that ARE a time window (window membership). A contract that
# already declares one of these is time-window aware; the evaluation layer does
# not second-guess it.
TIME_WINDOW_METRICS = {"sunrise_time_window", "sunset_window",
                       "blue_hour_window", "golden_hour_window",
                       "astronomical_darkness", "city_night_window",
                       "light_window", "daylight_window"}
# CL-UI-23: genre templates whose subject semantics require a night hours
# window but whose current owner contracts carry no time-window condition
# (data-layer gap, owner gate pending). The evaluation layer enforces the
# window deterministically from astronomy so a daytime hour can never become
# a "good hour" for a night subject. Syncing these into the contracts remains
# an owner decision; when a contract adds a real time-window condition, the
# gate automatically stands down (condition already in TIME_WINDOW_METRICS).
EVAL_TIME_WINDOW_GATES = {"city_night": "city_night_window"}
GATE_CONDITION_ID = "EVALGATE-city_night-window"
GATE_CONDITION = {
    "id": GATE_CONDITION_ID,
    "role": "REQUIRED",
    "domain": "ASTRONOMY",
    "evaluation_mode": "GUIDANCE",
    "capability": "CONDITIONS",
    "metric": "city_night_window",
    "operator": "none",
    "condition_tier": "MAIN",
    "notes_i18n": {
        "zh-TW": "CL-UI-23 評估層時間窗：夜景題材的小時桶須整桶日落在地平線下"
                 "（太陽仰角 ≤ -6°）。此閘門來自評估層（契約尚未含時間窗，待 owner 補）。",
        "en": "CL-UI-23 evaluation-layer time gate: a city-night hour bucket "
              "qualifies only when the whole bucket is after civil dusk (sun "
              "elevation <= -6 deg). Owner contracts pending a real window "
              "condition; this gate stands down automatically once added.",
        "ja": "CL-UI-23 評価層の時間ゲート: 夜景題材の時間バケツは全体が薄暮後"
              "（太陽高度 ≤ -6°）であることを要する。契約の時間窓追加後は自動解除。",
    },
}


def eval_conditions_for(contract):
    """Owner conditions plus the evaluation-layer time-window gate.

    The gate is injected at evaluation time (never written into the owner
    contract): a genre whose subject requires night hours gets a REQUIRED
    window-membership condition when the contract itself declares no
    time-window metric. condition_contract_sha256 stays over the owner
    contract only.
    """
    conditions = list(contract.get("conditions") or [])
    metric = EVAL_TIME_WINDOW_GATES.get(contract.get("genre_template"))
    if not metric:
        return conditions
    if any(c.get("metric") in TIME_WINDOW_METRICS for c in conditions):
        return conditions
    return conditions + [GATE_CONDITION]
DECLARED_PASS_METRICS = {"landform_present"}
NO_SOURCE_METRICS = {"water_surface_state", "seasonal_state"}
# Display-only local clocks (approximate; Place index time_zone is UNKNOWN).
# CL-UI-24: offset = local time − UTC, so western (negative-longitude) zones
# are NEGATIVE (America/Los_Angeles −8, Denver −7, New_York −5, Anchorage −9).
# These are standard-time (display approximation) values; DST is out of scope.
TZ_DISPLAY = [
    ((54, 72, -170, -130), "America/Anchorage", -9),
    ((32, 55, -130, -114), "America/Los_Angeles", -8),
    ((30, 49, -114, -96), "America/Denver", -7),
    # CL-CI-33: the Denver box required lat>=30, which left a gap covering
    # Big Bend (us-106, 29.17/-103.61) and the rest of the southern US
    # between the Rockies and the East box — those resolved UNKNOWN and the
    # bundle failed schema validation against the old constant pin.
    ((25, 49, -114, -92), "America/Chicago", -6),
    ((24, 50, -96, -66), "America/New_York", -5),
    # CL-DATA-43: Hawaii (us-112..118) was falling through to the iana=null /
    # offset=0 fallback, rendering sunrise/sunset good_hours in UTC — Makapuʻu
    # (us-117) showed its 17:00Z sunrise as 17:00 local instead of ~07:00.
    ((18, 23, -161, -154), "Pacific/Honolulu", -10),
    ((21, 26.6, 117.5, 122.2), "Asia/Taipei", 8),
    ((23, 46, 122.2, 146), "Asia/Tokyo", 9),
]


def static_timezone(lat, lon):
    for (lat_lo, lat_hi, lon_lo, lon_hi), zone, offset in TZ_DISPLAY:
        if lat_lo <= lat <= lat_hi and lon_lo <= lon <= lon_hi:
            return zone, offset
    # CL-DATA-43: a miss must propagate UNKNOWN, never a fake 0 offset —
    # 0 rendered UTC as if it were local. Callers keep the hour arithmetic
    # on offset 0 but label the place timezone_display UNKNOWN with nulls.
    return None, None


def condition_verdict(condition, values, astro_row, month=None):
    """Return (verdict, detail) with verdict in PASS/FAIL/UNKNOWN."""
    metric = condition["metric"]
    operator = condition.get("operator")
    threshold = condition.get("threshold")
    if metric in NO_SOURCE_METRICS:
        return "UNKNOWN", "NO_LIVE_OBSERVATION_SOURCE"
    if metric in DECLARED_PASS_METRICS:
        return "PASS", "OWNER_DECLARED_PRESENCE"
    if metric == "light_direction":
        # CL-DATA-13: month-calibrated light-direction arc. The contract
        # declares `sectors` — 12 monthly {arc_center_deg, arc_half_width_deg}
        # entries — because the solar azimuth at the relevant light event
        # swings ~51 deg across the year (CL-PHOTO-02 evidence: Tamsui winter
        # ~244 vs summer ~296); a single fixed arc aims at the wrong
        # direction for half of the year. The evaluator selects the current
        # month's sector and checks the sun azimuth against it. The view
        # azimuth (resolved from the opportunity's observation_relations by
        # the batch runner) is the precondition: an unknown view direction
        # means the sector claim itself is unverified, so the verdict
        # propagates UNKNOWN (never a fabricated direction).
        view_az = condition.get("view_azimuth_deg")
        if view_az is None:
            return "UNKNOWN", "VIEW_AZIMUTH_UNKNOWN"
        sectors = condition.get("sectors")
        if (not isinstance(sectors, list) or len(sectors) != 12
                or month is None or not isinstance(month, int) or not 1 <= month <= 12):
            return "UNKNOWN", "SECTORS_UNAVAILABLE"
        sector = sectors[month - 1]
        az = astro_row.get("sun_azimuth_deg")
        if not isinstance(az, (int, float)):
            return "UNKNOWN", "ASTRO_UNAVAILABLE_AT_INSTANT"
        diff = abs(float(az) - float(sector["arc_center_deg"])) % 360.0
        diff = min(diff, 360.0 - diff)
        detail = (f"LIGHT_DIRECTION_ARC({month}: {sector['arc_center_deg']}±"
                  f"{sector['arc_half_width_deg']}deg, diff={round(diff, 1)})")
        return ("PASS" if diff <= float(sector["arc_half_width_deg"])
                else "FAIL"), detail
    if metric in ASTRO_METRICS:
        # CL-DATA-24: an optional per-condition `phase` constraint ("dawn" or
        # "dusk") keeps a symmetric window metric (blue/golden hour) on the
        # side of the day the subject name names. Mismatch = FAIL for the
        # hour; the window itself can stay true, the phase is what gates.
        required_phase = condition.get("phase")
        if required_phase:
            astro_phase = astro_row.get("phase")
            if astro_phase is None:
                # honesty contract: no events (polar day/night) means the
                # phase cannot be verified — propagate UNKNOWN, never a
                # fabricated FAIL either way.
                return "UNKNOWN", "ASTRO_PHASE_UNAVAILABLE"
            if astro_phase != required_phase:
                return "FAIL", "ASTRO_PHASE_MISMATCH"
        value = astro_row.get(metric)
        if value is None:
            return "UNKNOWN", "ASTRO_UNAVAILABLE_AT_INSTANT"
        if operator == "none":
            # window-membership metric: astro_row carries the boolean directly
            return ("PASS" if value else "FAIL"), "ASTRO_WINDOW_MEMBERSHIP"
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return "UNKNOWN", "ASTRO_NON_NUMERIC"
        try:
            passed = compare(float(value), operator, threshold)
        except Exception:
            return "UNKNOWN", "INVALID_THRESHOLD"
        return ("PASS" if passed else "FAIL"), "ASTRO_THRESHOLD"
    field = METRIC_FIELDS.get(metric)
    if field is None:
        return "UNKNOWN", "METRIC_NOT_MAPPED"
    cell = values.get(field)
    if not isinstance(cell, dict) or cell.get("state") != "AVAILABLE":
        return "UNKNOWN", "CELL_NOT_AVAILABLE"
    value = cell.get("value")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "UNKNOWN", "CELL_VALUE_INVALID"
    if operator in ("is_true", "is_false", "none"):
        return "UNKNOWN", "NON_NUMERIC_OPERATOR"
    try:
        passed = compare(float(value), operator, threshold)
    except Exception:
        return "UNKNOWN", "INVALID_THRESHOLD"
    return ("PASS" if passed else "FAIL"), "FORECAST_THRESHOLD"


BOOLEAN_VALUE_SATISFIED = "satisfied"
BOOLEAN_VALUE_UNSATISFIED = "unsatisfied"


def boolean_value_label(value):
    """Map a raw boolean observation to the stable display enum (CL-UI-06).

    Contract (owner-ratified 2026-11): condition.value must never be a raw
    JSON boolean. Boolean window-membership metrics (sunset_window,
    sunrise_time_window, golden_hour_window, blue_hour_window,
    astronomical_darkness, ...) are published as the enum strings
    'satisfied' / 'unsatisfied'; the UI maps these to localized labels.
    Non-boolean values pass through unchanged.
    """
    if isinstance(value, bool):
        return BOOLEAN_VALUE_SATISFIED if value else BOOLEAN_VALUE_UNSATISFIED
    return value


def condition_value(condition, values, astro_row):
    """Observation used for the verdict, for live display (not a score).

    Boolean observations are published as 'satisfied'/'unsatisfied' (never a
    raw true/false) so no UI surface can leak an untranslated boolean.
    """
    metric = condition.get("metric")
    operator = condition.get("operator") or "none"
    if metric in NO_SOURCE_METRICS:
        return None
    if metric in DECLARED_PASS_METRICS:
        return "declared"
    if metric == "light_direction":
        # display the observation the arc was judged on
        return astro_row.get("sun_azimuth_deg")
    if metric in ASTRO_METRICS:
        return boolean_value_label(astro_row.get(metric))
    cell = values.get(metric)
    if not isinstance(cell, dict) or cell.get("state") != "AVAILABLE":
        return None
    return boolean_value_label(cell.get("value"))


def hour_status(roles, verdicts):
    """Aggregate one hour into its status, honouring role semantics:
    REQUIRED FAIL or BLOCKER PASS -> UNFAVORABLE; REQUIRED/BLOCKER UNKNOWN ->
    NOT_EVALUABLE; QUALITY never gates (advisory only)."""
    fails = [cid for cid, v in verdicts.items()
             if v == "FAIL" and roles.get(cid) == "REQUIRED"]
    blockers = [cid for cid, v in verdicts.items()
                if v == "PASS" and roles.get(cid) == "BLOCKER"]
    unknowns = [cid for cid, v in verdicts.items()
                if v == "UNKNOWN" and roles.get(cid) in ("REQUIRED", "BLOCKER")]
    if fails or blockers:
        return "UNFAVORABLE", fails, unknowns
    if unknowns:
        return "NOT_EVALUABLE", fails, unknowns
    return "GUIDANCE_SATISFIED", fails, unknowns


def detail_hour_rows(hour_row, local_stamp, status, conditions_eval,
                     astro_row, states, precise_local, precise_off):
    """CL-INT-91: details rows for one hour bucket.

    Every good_hour stamp the summary emits must key a details row (the
    cl-ui-23 contract). CL-DATA-31 stamps qualifying buckets at their
    earliest passing sub-hour sample (local_precise), so a qualifying
    bucket emits an ADDITIONAL sub-hour row keyed at that precise local
    stamp. Weather condition VALUES stay bucket-level (hourly grid
    data); the astro window metrics pass at the precise instant by
    construction — it is the same window_pass_profiles computation that
    stamped local_precise.
    """
    conditions = [
        {"id": c["id"], "metric": c["metric"],
         "tier": c.get("condition_tier") or "MAIN", "role": c.get("role"),
         "operator": c.get("operator") or "none",
         "threshold": c.get("threshold"),
         "value": condition_value(c, hour_row["values"], astro_row),
         "verdict": states[c["id"]]}
        for c in conditions_eval]
    rows = [{
        "utc": hour_row["valid_at_utc"],
        "local": local_stamp.strftime("%H:%M"),
        "status": status,
        "conditions": conditions,
    }]
    if precise_local is not None and precise_off:
        # off == 0 means the window already passes at the bucket start, so
        # the precise stamp IS the bucket stamp — the hourly row above
        # already keys it; no duplicate row.
        rows.append({
            "utc": hour_row["valid_at_utc"],
            "local": precise_local,
            "sub_hour_of_bucket": local_stamp.strftime("%H:%M"),
            "sample_offset_min": precise_off,
            "status": status,
            "conditions": conditions,
        })
    return rows


def load_contracted():
    opportunities = []
    for path in sorted((ROOT / "data/v2/opportunities").glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        contract = doc.get("condition_contract") or {}
        if not contract.get("genre_template"):
            continue
        opportunities.append(doc)
    return opportunities


def load_opportunity_docs():
    """All opportunity docs regardless of template ladder (CL-UI-41)."""
    docs = []
    for path in sorted((ROOT / "data/v2/opportunities").glob("*.json")):
        docs.append(json.loads(path.read_text(encoding="utf-8")))
    return docs


OWNER_RULING_COORDINATE_SUBJECTS = {
    # Owner ruling 2026-11-02: the six previously review-gated subjects adopt
    # the review-revised conditions and are evaluated from their place-level
    # coordinates (V1 weather snapshot geocodes) when the camera-context
    # geometry has no independently verified geojson yet.
    "tw-026-P01", "tw-026-P02", "tw-082-P01", "tw-034-P02", "jp-010-P01",
    "us-071-P01",
}
V1_WEATHER_FILES = ("tw_weather.json", "jp_weather.json", "us_weather.json")


def v1_place_coordinates():
    """Place-level coordinates carried by the V1 weather snapshots."""
    coords = {}
    for name in V1_WEATHER_FILES:
        path = ROOT / name
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for spot in data.get("spots") or []:
            spot_id = spot.get("spot_id")
            lat, lon = spot.get("lat"), spot.get("lon")
            if spot_id and isinstance(lat, (int, float)) \
                    and isinstance(lon, (int, float)):
                coords.setdefault(spot_id, (float(lat), float(lon)))
    return coords


def coordinate_of(opportunity):
    oid = opportunity["opportunity_id"]
    if oid == "tw-036-P01":
        # Sourced pilot binding coordinate (representative_place_weather_sample).
        return 24.031426, 121.62717, "pilot_binding_tw036"
    camera = opportunity["camera_contexts"][0]
    geo = ((camera.get("geometry") or {}).get("geojson") or {}).get("coordinates")
    if not geo:
        if oid in OWNER_RULING_COORDINATE_SUBJECTS:
            coords = v1_place_coordinates()
            place = coords.get(opportunity["place_id"])
            if place is not None:
                return place[0], place[1], "v1_weather_snapshot_place_coordinate"
        return None
    return geo[1], geo[0], "camera_context_provisional"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(ROOT / "apps/web-v2/evaluations-latest.json"))
    parser.add_argument("--archive", default=str(ROOT / "data/v2/evaluations"))
    parser.add_argument("--details-dir", default=str(ROOT / "apps/web-v2/evaluations-details"))
    # CL-UI-25: optional targeted regeneration (one place_id only). Bundles and
    # archive output should be redirected when using it, so a partial run never
    # clobbers the full published artifacts.
    parser.add_argument("--only-place-id", default=None,
                        help="evaluate only the coordinate groups of this place_id")
    # CL-CI-21 fail-closed: --forecast-hours has NO silent default. The Python
    # default of 72 was silently reregressing the published bundle to the old
    # 72h horizon whenever a scoped regen (CL-DATA-25/26) omitted the flag —
    # the scheduled 168h semantics were lost in the artifact without any error.
    parser.add_argument("--forecast-hours", type=int, default=None)
    arguments = parser.parse_args()
    PUBLISHED_HORIZON_HOURS = 168  # CL-DATA-06: 7-day semantics (CAMS ceiling)
    if arguments.forecast_hours is None:
        parser.error(
            "--forecast-hours is required (published semantics: 168 = 7 days; "
            "a missing flag must fail closed, not silently fall back to 72)")
    if arguments.forecast_hours < 1 or arguments.forecast_hours > 384:
        parser.error(f"--forecast-hours {arguments.forecast_hours} outside 1..384")
    if (Path(arguments.out) == ROOT / "apps/web-v2/evaluations-latest.json"
            and arguments.forecast_hours != PUBLISHED_HORIZON_HOURS):
        parser.error(
            f"refusing to write the PUBLISHED bundle with forecast_hours="
            f"{arguments.forecast_hours}: published horizon semantics is "
            f"{PUBLISHED_HORIZON_HOURS}h (7 days). Pass --forecast-hours 168, "
            "or redirect --out/--archive/--details-dir for experimental runs.")

    opportunities = load_contracted()
    places_index = json.loads((ROOT / "data/v2/indexes/research/place-index.json")
                              .read_text(encoding="utf-8"))
    names = {p["place_id"]: p.get("name_i18n") or {} for p in places_index["places"]}

    by_coordinate = {}
    skipped = []
    for doc in opportunities:
        # CL-UI-25: targeted regeneration filter — applied before coordinate
        # grouping so only the requested place's coordinates are fetched.
        if arguments.only_place_id and doc["place_id"] != arguments.only_place_id:
            continue
        coord = coordinate_of(doc)
        if coord is None:
            skipped.append({"opportunity_id": doc["opportunity_id"],
                            "place_id": doc["place_id"],
                            "reason": "NO_VERIFIED_GEOMETRY"})
            continue
        lat, lon, source = coord
        by_coordinate.setdefault((round(lat, 4), round(lon, 4)),
                                 {"lat": lat, "lon": lon, "source": source,
                                  "opportunities": []})["opportunities"].append(doc)

    # CL-UI-41: the no-evaluation card group must name WHY a place carries no
    # V2 evaluation. Emit every non-evaluated legacy-catalog place in the
    # bundle's skip list with a machine-derived reason:
    #   NO_GENRE_TEMPLATE       — contract exists, genre_template not defined
    #                             (previously dropped silently by load_contracted)
    #   NO_VERIFIED_GEOMETRY    — contract exists, camera geometry unverified
    #   NO_OPPORTUNITY_CONTRACT — no condition contract at all for the place
    evaluated_place_ids = {doc["place_id"] for coord in by_coordinate.values()
                           for doc in coord["opportunities"]}
    skipped_place_ids = {s.get("place_id") for s in skipped}
    if arguments.only_place_id:
        # Targeted regeneration: only classify this place's own subjects.
        candidate_docs = [doc for doc in load_opportunity_docs()
                          if doc["place_id"] == arguments.only_place_id]
        v1_ids = {arguments.only_place_id}
    else:
        candidate_docs = load_opportunity_docs()
        v1_ids = set(v1_place_coordinates())
    for doc in candidate_docs:
        contract = doc.get("condition_contract") or {}
        if doc["place_id"] in evaluated_place_ids \
                or doc["place_id"] in skipped_place_ids:
            continue
        if not contract.get("genre_template"):
            skipped.append({"opportunity_id": doc["opportunity_id"],
                            "place_id": doc["place_id"],
                            "reason": "NO_GENRE_TEMPLATE"})
            skipped_place_ids.add(doc["place_id"])
    for pid in sorted(v1_ids - evaluated_place_ids - skipped_place_ids):
        skipped.append({"place_id": pid, "reason": "NO_OPPORTUNITY_CONTRACT"})

    generated_at = datetime.now(timezone.utc)
    generated_iso = generated_at.isoformat(timespec="seconds").replace("+00:00", "Z")
    span_start = int(generated_at.timestamp())
    span_end = span_start + arguments.forecast_hours * 3600

    places_out = []
    provider_runs = []
    failures = []
    # CL-UI-25: detail artifacts are keyed by place_id, but a place_id can span
    # more than one coordinate group (e.g. tw-002 evaluates P01 from one
    # viewpoint and P02/P03 from another ~300 m away). Writing one file per
    # coordinate group clobbered the earlier group's opportunities (two
    # city_night details lost). Detail docs are now accumulated per place_key
    # and written once after the loop; a merged doc carries per-opportunity
    # coordinate provenance (coordinate / coordinate_source) plus a
    # coordinate_groups manifest so the single file stays honest about which
    # evaluation came from which viewpoint.
    detail_docs = {}
    for index, (key, group) in enumerate(sorted(by_coordinate.items())):
        lat, lon = group["lat"], group["lon"]
        try:
            artifact = adapter.fetch_place(lat, lon, arguments.forecast_hours)
        except adapter.FetchFailure as failure:
            failures.append({"coordinate": [lat, lon], "error": str(failure)})
            continue
        provider_runs.append({
            "run_id": f"om-{lat:.4f}-{lon:.4f}-{artifact['retrieved_at_utc']}",
            "provider": "open-meteo",
            "source": artifact["sources"][0]["source_url"],
            "issued_at": artifact["retrieved_at_utc"],
            "valid_at": artifact["hours"][0]["valid_at_utc"],
            "freshness": "FRESH",
            "grid": artifact["grid"],
        })
        events = sun_events_span(lat, lon, span_start, span_end)
        zone, offset = static_timezone(lat, lon)
        if offset is None:
            # CL-DATA-43: unresolved timezone propagates as UNKNOWN (null
            # iana/offset), not a fake 0 — hour arithmetic stays on UTC but
            # the place is labeled honestly as having no display timezone.
            tz_display = {"iana": None, "utc_offset_hours": None,
                          "status": "UNKNOWN"}
            local_offset = 0
        else:
            tz_display = {"iana": zone, "utc_offset_hours": offset,
                          "status": "DISPLAY_APPROXIMATION"}
            local_offset = offset
        need_moon = any("moon" in c["metric"] or "galactic" in c["metric"]
                        for doc in group["opportunities"]
                        for c in doc["condition_contract"]["conditions"])
        hours = artifact["hours"]
        place_out = {"place_id": None, "coordinate": [lat, lon],
                     "coordinate_source": group["source"],
                     "timezone_display": dict(tz_display),
                     "provider_run": provider_runs[-1],
                     "opportunities": []}
        place_detail = {"place_id": None, "coordinate": [lat, lon],
                        "coordinate_source": group["source"],
                        "timezone_display": dict(tz_display),
                        "opportunities": []}
        for doc in group["opportunities"]:
            oid = doc["opportunity_id"]
            contract = doc["condition_contract"]
            # CL-UI-23: the sha stays over the OWNER contract; the gate is
            # evaluation-layer only and must never leak into provenance.
            contract_sha = hashlib.sha256(
                json.dumps(contract, sort_keys=True, separators=(",", ":"))
                .encode("utf-8")).hexdigest()
            conditions_eval = eval_conditions_for(contract)
            # CL-DATA-13: resolve the view azimuth from the opportunity's
            # observation relations (backfilled from legacy where known) and
            # bind it onto every light_direction condition.
            view_az_deg = next(
                (r["azimuth_deg"] for r in doc.get("observation_relations", [])
                 if r.get("azimuth_deg") is not None), None)
            for _cond in conditions_eval:
                if _cond.get("metric") == "light_direction":
                    _cond["view_azimuth_deg"] = view_az_deg
            days = {}
            hour_ctxs = []
            for hour_row in hours:
                at = datetime.fromisoformat(hour_row["valid_at_utc"].replace("Z", "+00:00"))
                astro_row = hour_observations(at, lat, lon, events=events,
                                              need_moon=need_moon)
                states = {}
                roles = {}
                for condition in conditions_eval:
                    states[condition["id"]] = condition_verdict(
                        condition, hour_row["values"], astro_row,
                        month=at.month)[0]
                    roles[condition["id"]] = condition.get("role")
                status, fails, unknowns = hour_status(roles, states)
                local_stamp = at + timedelta(hours=local_offset)
                day_key = local_stamp.date().isoformat()
                entry = days.setdefault(day_key, {"local_date": day_key, "hours": []})
                # CL-DATA-31: a qualifying hour bucket is stamped at its
                # EARLIEST passing sub-hour sample, never at the bucket start —
                # any()-aggregated narrow windows (sunrise/sunset ±40 min,
                # blue/golden hour) can sit entirely inside the second half of
                # the bucket, so a bucket-start label led the real window by
                # up to ~55 minutes (challenger audit 2026-11-08: sunrise
                # cards showed 05:00 for an ~06:05 sunrise whose window opens
                # ~05:25, while the sun was still below −10° at 05:00).
                # Weather conditions stay bucket-level (hourly grid data), so
                # the label is precise for the astro window within the bucket.
                precise_local = None
                precise_off = None
                if status == "GUIDANCE_SATISFIED":
                    window_metrics = [c["metric"] for c in conditions_eval
                                      if c["metric"] in TIME_WINDOW_METRICS]
                    if window_metrics:
                        profiles = window_pass_profiles(at, lat, lon,
                                                        events=events)
                        for i, off in enumerate(WINDOW_SAMPLE_OFFSETS):
                            if all(profiles[m][i] for m in window_metrics):
                                precise_off = off
                                precise_local = (local_stamp
                                                 + timedelta(minutes=off)
                                                 ).strftime("%H:%M")
                                break
                entry["hours"].append({
                    "utc": hour_row["valid_at_utc"],
                    "local": local_stamp.strftime("%H:%M"),
                    "local_precise": precise_local,
                    "status": status,
                    "failed": fails,
                    "unknown": unknowns,
                })
                hour_ctxs.append((at, hour_row, astro_row, states, status))
                for row in detail_hour_rows(
                        hour_row, local_stamp, status, conditions_eval,
                        astro_row, states, precise_local, precise_off):
                    entry.setdefault("detail_hours", []).append(row)
            day_out = []
            condition_by_id = {c["id"]: c for c in conditions_eval}
            for day_key in sorted(days):
                hours_out = days[day_key]["hours"]
                counts = {"GUIDANCE_SATISFIED": 0, "UNFAVORABLE": 0,
                          "NOT_EVALUABLE": 0}
                for h in hours_out:
                    counts[h["status"]] = counts.get(h["status"], 0) + 1
                if counts["GUIDANCE_SATISFIED"]:
                    state = "GUIDANCE_SATISFIED"
                elif counts["NOT_EVALUABLE"] and not counts["UNFAVORABLE"]:
                    state = "NOT_EVALUABLE"
                elif counts["UNFAVORABLE"]:
                    state = "UNFAVORABLE"
                else:
                    state = "NOT_EVALUABLE"
                conditions_day = []
                total = len(hours_out)
                for cid, cond in condition_by_id.items():
                    fails = sum(1 for h in hours_out if cid in h["failed"])
                    unknowns = sum(1 for h in hours_out if cid in h["unknown"])
                    pass_n = total - fails - unknowns
                    if unknowns == total:
                        verdict = "UNKNOWN"
                    elif pass_n == total:
                        verdict = "PASS"
                    elif fails == total:
                        verdict = "FAIL"
                    else:
                        verdict = "PARTIAL"
                    conditions_day.append({
                        "id": cid, "metric": cond["metric"],
                        "tier": cond.get("condition_tier") or "MAIN",
                        "role": cond.get("role"),
                        "day_verdict": verdict,
                        "pass_hours": pass_n,
                    })
                day_out.append({
                    "local_date": day_key,
                    "state": state,
                    # CL-DATA-31: good_hours carry the EARLIEST passing
                    # sub-hour instant (local_precise) when one was computed —
                    # never a bucket-start stamp earlier than the light window.
                    "good_hours": [h.get("local_precise") or h["local"]
                                   for h in hours_out
                                   if h["status"] == "GUIDANCE_SATISFIED"],
                    "hour_counts": counts,
                    "conditions": conditions_day,
                })
            def _snapshot(ctx):
                if ctx is None:
                    return None
                snap_at, snap_row, snap_astro, snap_states, snap_status = ctx
                return {
                    "utc": snap_row["valid_at_utc"],
                    "local": (snap_at + timedelta(hours=local_offset)).strftime("%Y-%m-%d %H:%M"),
                    "status": snap_status,
                    "conditions": [
                        {"id": c["id"], "metric": c["metric"],
                         "tier": c.get("condition_tier") or "MAIN", "role": c.get("role"),
                         "operator": c.get("operator") or "none",
                         "threshold": c.get("threshold"),
                         "value": condition_value(c, snap_row["values"], snap_astro),
                         "verdict": snap_states[c["id"]]}
                        for c in conditions_eval],
                }

            now_ctx = next((c for c in hour_ctxs if c[0] >= generated_at), None)
            good_ctx = next((c for c in hour_ctxs if c[4] == "GUIDANCE_SATISFIED"), None)
            live = {"now": _snapshot(now_ctx), "next_good": _snapshot(good_ctx)}
            place_out["opportunities"].append({
                "opportunity_id": oid,
                "name_i18n": doc.get("name_i18n") or {},
                "genre_template": contract.get("genre_template"),
                "condition_contract_id": contract.get("contract_id"),
                "condition_contract_sha256": contract_sha,
                "days": day_out,
                "live": live,
            })
            place_detail["opportunities"].append({
                "opportunity_id": oid,
                "name_i18n": doc.get("name_i18n") or {},
                "genre_template": contract.get("genre_template"),
                "days": [{"local_date": key, "hours": days[key]["detail_hours"]}
                         for key in sorted(days)],
                "live": live,
            })
            if place_out["place_id"] is None:
                place_out["place_id"] = doc["place_id"]
        place_out["name_i18n"] = names.get(place_out["place_id"], {})
        places_out.append(place_out)
        place_key = place_out["place_id"] or f"coord-{lat:.4f}-{lon:.4f}"
        place_detail["place_id"] = place_out["place_id"]
        place_detail["name_i18n"] = place_out["name_i18n"]
        place_detail["generated_at"] = generated_iso
        # CL-UI-08 provenance: the sub-hour sampling regime used for the
        # narrow astro window metrics (evaluations-details is not
        # schema-gated; evaluations-latest.json keeps its v0.1 shape).
        place_detail["astro_sampling"] = ASTRO_SAMPLING_PROVENANCE
        entry = detail_docs.get(place_key)
        if entry is None:
            detail_docs[place_key] = {"detail": place_detail, "groups": [
                {"coordinate": [lat, lon], "coordinate_source": group["source"],
                 "opportunity_ids": [o["opportunity_id"]
                                     for o in place_detail["opportunities"]]}]}
        else:
            entry["detail"]["opportunities"].extend(place_detail["opportunities"])
            entry["groups"].append(
                {"coordinate": [lat, lon], "coordinate_source": group["source"],
                 "opportunity_ids": [o["opportunity_id"]
                                     for o in place_detail["opportunities"]]})
        time.sleep(0.25)

    details_dir = Path(arguments.details_dir)
    details_dir.mkdir(parents=True, exist_ok=True)
    for place_key, entry in detail_docs.items():
        place_detail = entry["detail"]
        # CL-UI-25 merge provenance: when one place_id covers several
        # coordinate groups, the detail doc keeps the FIRST group's coordinate
        # at file level and annotates every opportunity (and a
        # coordinate_groups manifest) with the coordinate it was actually
        # evaluated at — never a silent overwrite of the earlier group.
        if len(entry["groups"]) > 1:
            for opp in place_detail["opportunities"]:
                group = next((g for g in entry["groups"]
                              if opp["opportunity_id"] in g["opportunity_ids"]), None)
                if group is not None:
                    opp["coordinate"] = group["coordinate"]
                    opp["coordinate_source"] = group["coordinate_source"]
            place_detail["coordinate_groups"] = [
                {"coordinate": g["coordinate"],
                 "coordinate_source": g["coordinate_source"],
                 "opportunity_ids": g["opportunity_ids"]}
                for g in entry["groups"]]
        (details_dir / f"{place_key}.json").write_text(
            json.dumps(place_detail, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8")

    bundle = {
        "evaluation_bundle_version": BUNDLE_VERSION,
        "generated_at": generated_iso,
        "forecast_hours": arguments.forecast_hours,
        "guidance_only": True,
        "live_recommendation": False,
        "calibration_status": "PROVISIONAL_THRESHOLDS",
        "provider": {
            "name": "Open-Meteo",
            "licence": "CC BY 4.0",
            "urls": {"terms": "https://open-meteo.com/en/terms",
                     "licence": "https://open-meteo.com/en/licence"},
        },
        "limitations_i18n": {
            "zh-TW": "評估結果為 GUIDANCE 参考：門檻為 provisional/approved 題材模板值，"
                     "未經實拍校準，永不構成 FAVORABLE 保證。湖面狀態與花季窗口暫無即時"
                     "觀測來源（標記 UNKNOWN）。天氣為網格預報，不代表拍攝點實況。",
            "en": "Results are GUIDANCE only: thresholds are provisional/approved "
                  "genre-template values, not calibrated against real shoots, and never "
                  "constitute a FAVORABLE guarantee. Water-surface state and seasonal "
                  "windows have no live observation source (UNKNOWN). Weather is grid "
                  "forecast data, not on-site conditions.",
            "ja": "評価結果はGUIDANCE参考値です: 閾値は暫定/承認済みテンプレート値で、"
                  "実写検証されておらず、FAVORABLE保証にはなりません。水面状態と開花"
                  "窗口は観測ソースがなくUNKNOWN。天気はグリッド予報であり現地実況では"
                  "ありません。",
        },
        "place_count": len(places_out),
        "opportunity_count": sum(len(p["opportunities"]) for p in places_out),
        "fetch_failures": failures,
        "skipped": skipped,
        "provider_runs_count": len(provider_runs),
        "places": places_out,
    }
    output = Path(arguments.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, ensure_ascii=False, separators=(",", ":")) + "\n",
                      encoding="utf-8")
    archive = Path(arguments.archive)
    archive.mkdir(parents=True, exist_ok=True)
    stamp = generated_at.strftime("%Y%m%dT%H%M%SZ")
    (archive / f"bundle-{stamp}.json").write_text(
        json.dumps(bundle, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "places": len(places_out),
                      "opportunities": bundle["opportunity_count"],
                      "failures": len(failures),
                      "skipped": len(skipped),
                      "bytes": output.stat().st_size}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
