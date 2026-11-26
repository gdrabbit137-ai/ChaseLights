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
- Known-honest gaps stay UNKNOWN: water_surface_state (tide-decided shoreline
  subjects — CL-DATA-72 batch A item 4) has no live observation source
  (propagate_unknown); landform_present is the owner-declared static presence
  (deterministic PASS).
- CL-DATA-72 batch A bridges the two former no-source metrics:
  * seasonal_state is now computed from data/v2/seasonal-calendar.json
    (current_season first, typical_window fallback, neither -> UNKNOWN) —
    CL-COND-A8.
  * reflection contracts evaluate the DERIVED water_reflection_state
    (wind/precipitation/temperature proxy: mirror / shootable / unfit) —
    CL-COND-A7; tide-decided shoreline subjects keep water_surface_state and
    degrade to NOT_EVALUABLE honestly.
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
import quality_engine  # noqa: E402  CL-DATA-80 QUALITY scoring engine (v2)

BUNDLE_VERSION = "0.2.0"  # CL-DATA-80: quality-engine fields (engine/s_rank/good_hours_v2)
ASTRO_METRICS = {"sun_azimuth_deg", "sunrise_time_window", "sunset_window", "blue_hour_window",
                 "golden_hour_window", "astronomical_darkness",
                 "moon_illumination_fraction", "moon_altitude",
                 "moon_target_separation_deg", "moon_illuminance_proxy",
                 "galactic_core_altitude", "city_night_window",
                 # CL-DATA-78 Phase 1 spec-standard astro key aliases (§2)
                 # plus moon_azimuth_deg (view-azimuth separation branch).
                 "moon_azimuth_deg", "moon_altitude_deg",
                 "moon_illumination", "galactic_core_altitude_deg",
                 "light_window", "daylight_window",
                 # CL-DATA-73: misty-forest soft-light + morning windows.
                 "soft_light_window", "morning_window",
 # CL-DATA-74: five-genre alpenglow window.
                 "alpenglow_window"}

# CL-UI-23: metrics that ARE a time window (window membership). A contract that
# already declares one of these is time-window aware; the evaluation layer does
# not second-guess it.
TIME_WINDOW_METRICS = {"sunrise_time_window", "sunset_window",
                       "blue_hour_window", "golden_hour_window",
                       "astronomical_darkness", "city_night_window",
                       "light_window", "daylight_window",
                       # CL-DATA-73: misty-forest soft-light + morning windows.
                       "soft_light_window", "morning_window",
 # CL-DATA-74: five-genre alpenglow window.
                       "alpenglow_window"}
# CL-UI-23: genre templates whose subject semantics require a night hours
# window but whose current owner contracts carry no time-window condition
# (data-layer gap, owner gate pending). The evaluation layer enforces the
# window deterministically from astronomy so a daytime hour can never become
# a "good hour" for a night subject. Syncing these into the contracts remains
# an owner decision; when a contract adds a real time-window condition, the
# gate automatically stands down (condition already in TIME_WINDOW_METRICS).
EVAL_TIME_WINDOW_GATES = {
    "city_night": "city_night_window",
    # CL-PHYS-03 §5 (data half): the three moonlit_scene subjects carry no
    # time-window condition at all, so their night hours were emitted with no
    # window semantics. The evaluation layer supplies the deterministic
    # astronomical-darkness window so deep-night hours (00:00–04:00) are
    # legitimate windows with their own code, never a generic 非建議. The gate
    # stands down automatically once a contract declares a real window metric.
    "moonlit_scene": "astronomical_darkness",
}
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
    if metric == GATE_CONDITION["metric"]:
        return conditions + [GATE_CONDITION]
    # CL-PHYS-03 §5: per-genre gate built from the same shape (one shared
    # implementation, no per-subject ifs).
    gate = dict(GATE_CONDITION, id=f"EVALGATE-{contract['genre_template']}-window",
                metric=metric)
    return conditions + [gate]
DECLARED_PASS_METRICS = {"landform_present"}
# CL-DATA-72 batch A: seasonal_state leaves NO_SOURCE_METRICS — the verdict is
# now computed from data/v2/seasonal-calendar.json (CL-COND-A8, deterministic
# date-window matching). water_surface_state stays a known-honest gap: the
# tide-decided shoreline subjects (天空之鏡/潮汐決定型, e.g. tw-015 高美濕地)
# keep it REQUIRED and degrade to NOT_EVALUABLE (CL-COND-A7 owner ruling).
NO_SOURCE_METRICS = {"water_surface_state"}
# CL-DATA-77: spring-tide band proxy thresholds (jp-030-P01 whirlpools) —
# syzygy (new/full moon) drives spring tides; the band is ~syzygy ±2.7 days,
# proxied by moon illumination <=8% or >=92% (provisional, astro-only input).
SPRING_TIDE_ILLUM_MAX = 0.08
SPRING_TIDE_ILLUM_MIN = 0.92
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


# ---------------------------------------------------------------------------
# CL-DATA-72 batch A — CL-COND-A8: seasonal-window bridge (data/v2/audits/
# challenger-15-conditions-audit.md A8). seasonal_state was hard-coded into
# NO_SOURCE_METRICS while data/v2/seasonal-calendar.json sits in the repo with
# owner-maintained typical windows (and sourced current-season live windows):
# 764/764 evaluations were UNKNOWN and every flower-season subject was
# NOT_EVALUABLE on otherwise-good days. The window verdict is a deterministic
# calendar-date match — no live observation source is needed.
#
# Hemisphere/latitude semantics: calendar windows are PER-SPOT owner-maintained
# entries in the spot's own local calendar (e.g. 北半球 12-05~01-15 落羽松窗);
# the evaluator matches them against the hour's LOCAL date, so the
# northern/southern distinction lives entirely in the owner data — no global
# hemisphere flip is hard-coded here, and a future southern-hemisphere spot is
# simply maintained with its own local windows. Window endpoints are inclusive
# MM-DD pairs; a window whose start > end wraps across New Year.
SEASONAL_CALENDAR_PATH = ROOT / "data/v2/seasonal-calendar.json"


def load_seasonal_calendar():
    """Map opportunity_id -> [seasonal entry, ...] from seasonal-calendar.json.

    Fail-closed per the calendar's own _meta rule: a current_season entry
    without source_url + retrieved_at is ignored (never trusted as a live
    window), leaving the climatological typical window.
    """
    try:
        data = json.loads(SEASONAL_CALENDAR_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    by_spot = {}
    for entry in data.get("entries") or []:
        current = entry.get("current_season")
        if current and not (current.get("start") and current.get("end")
                            and current.get("source_url")
                            and current.get("retrieved_at")):
            current = None  # fail-closed: unsourced "live" windows are ignored
        by_spot_entry = {
            "plant_id": entry.get("plant_id"),
            "typical_window": entry.get("typical_window"),
            "current_season": current,
        }
        for spot in entry.get("spots") or []:
            by_spot.setdefault(spot, []).append(by_spot_entry)
    return by_spot


def _mmdd_inside(md, window):
    """Inclusive MM-DD window membership, wrap-aware across New Year."""
    start, end = window.get("start"), window.get("end")
    if not (isinstance(start, str) and isinstance(end, str)
            and len(start) == 5 and len(end) == 5):
        return False
    if start <= end:
        return start <= md <= end
    return md >= start or md <= end


def seasonal_window_verdict(entries, local_date):
    """CL-COND-A8 verdict for one hour's local date: window_open/closed.

    current_season (sourced live window, full dates) takes precedence over
    typical_window (climatological MM-DD); either matching = window_open.
    Neither matches = window_closed (FAIL — the hour is honestly unfavorable,
    no longer an UNKNOWN that blinds the whole subject). Fail-closed: a
    current_season without source_url + retrieved_at is never trusted (the
    calendar's own _meta rule), regardless of the caller.
    """
    if local_date is None:
        return "UNKNOWN", "LOCAL_DATE_UNAVAILABLE"
    date_iso = local_date.isoformat()
    md = date_iso[5:]
    typical_open = None
    for entry in entries or []:
        current = entry.get("current_season")
        if (current and current.get("source_url") and current.get("retrieved_at")
                and current["start"] <= date_iso <= current["end"]):
            return "PASS", (f"SEASONAL_WINDOW_OPEN(current_season "
                            f"{current['start']}~{current['end']}, "
                            f"plant={entry.get('plant_id')})")
        typical = entry.get("typical_window")
        if typical and typical_open is None and _mmdd_inside(md, typical):
            typical_open = (f"SEASONAL_WINDOW_OPEN(typical "
                            f"{typical['start']}~{typical['end']}, "
                            f"plant={entry.get('plant_id')})")
    if typical_open is not None:
        return "PASS", typical_open
    plant = ",".join(sorted({e.get("plant_id") or "?" for e in entries or []}))
    return "FAIL", f"SEASONAL_WINDOW_CLOSED({date_iso} outside {plant})"


def venue_open_verdict(condition, local_start_min):
    """CL-DATA-68: deterministic venue operating-window verdict.

    The window is declared on the condition as threshold ["HH:MM", "HH:MM"]
    (open, close) in the venue's local display clock; an hour bucket
    qualifies only when its START sits inside [open, close). Overnight
    windows (close <= open) and out-of-range clocks are malformed and fail
    closed as UNKNOWN — never a fabricated PASS/FAIL.
    """
    threshold = condition.get("threshold")
    if local_start_min is None:
        return "UNKNOWN", "LOCAL_TIME_UNAVAILABLE"
    if (not isinstance(threshold, list) or len(threshold) != 2
            or not all(isinstance(x, str) for x in threshold)):
        return "UNKNOWN", "VENUE_WINDOW_MALFORMED"

    def _minutes(token):
        hh, mm = token.split(":")
        return int(hh) * 60 + int(mm)

    try:
        open_min = _minutes(threshold[0])
        close_min = _minutes(threshold[1])
    except (ValueError, AttributeError):
        return "UNKNOWN", "VENUE_WINDOW_MALFORMED"
    if not (0 <= open_min < close_min <= 1440):
        return "UNKNOWN", "VENUE_WINDOW_MALFORMED"
    ok = open_min <= local_start_min < close_min
    return ("PASS" if ok else "FAIL"), (
        f"VENUE_OPEN_WINDOW({threshold[0]}-{threshold[1]})")


def condition_verdict(condition, values, astro_row, month=None,
                      local_start_min=None, local_date=None):
    """Return (verdict, detail) with verdict in PASS/FAIL/UNKNOWN."""
    metric = condition["metric"]
    operator = condition.get("operator")
    threshold = condition.get("threshold")
    if metric in PHYS_GATE_METRICS:
        # CL-PHYS-02/03 evaluation-layer gates (in_cloud_fog /
        # data_contradiction / cloud_sea_inversion / fog_visibility /
        # data_floor / season + venue policy) — derived cells, judged by their
        # single predicate, never by the generic field mapping.
        return phys_gate_verdict(condition, values,
                                 local_start_min=local_start_min,
                                 local_date=local_date)
    if metric in NO_SOURCE_METRICS:
        return "UNKNOWN", "NO_LIVE_OBSERVATION_SOURCE"
    if metric in DECLARED_PASS_METRICS:
        return "PASS", "OWNER_DECLARED_PRESENCE"
    if metric == "seasonal_state":
        # CL-DATA-72 batch A / CL-COND-A8: deterministic seasonal-window
        # verdict from seasonal-calendar.json (current_season first, typical
        # fallback, neither -> UNKNOWN). The contract threshold is the display
        # value "window_open" (eq); anything else fails closed as malformed.
        if operator != "eq" or threshold != "window_open":
            return "UNKNOWN", "UNSUPPORTED_SEASONAL_THRESHOLD"
        if not condition.get("seasonal_entries"):
            return "UNKNOWN", "NO_SEASONAL_CALENDAR_ENTRY"
        return seasonal_window_verdict(condition.get("seasonal_entries"),
                                       local_date)
    if metric == "water_reflection_state":
        # CL-DATA-72 batch A / CL-COND-A7: the reflection family evaluates the
        # DERIVED surface-state proxy (water_reflection_state: mirror /
        # shootable / unfit) that the batch runner computes per hour from wind,
        # precipitation history and air temperature. The contract carries no
        # threshold (operator "none"): only the "unfit" level vetoes —
        # mirror/shootable both satisfy the condition.
        cell = values.get("water_reflection_state") if isinstance(values, dict) else None
        if not isinstance(cell, dict) or cell.get("state") != "AVAILABLE":
            return "UNKNOWN", "REFLECTION_STATE_DERIVATION_UNAVAILABLE"
        level = cell.get("value")
        if level not in ("mirror", "shootable", "unfit"):
            return "UNKNOWN", "REFLECTION_STATE_INVALID_LEVEL"
        if operator in ("none", None, "neq"):
            passed = level != "unfit" if operator in (None, "none") \
                else level != threshold
        elif operator == "eq":
            passed = level == threshold
        else:
            return "UNKNOWN", "NON_NUMERIC_OPERATOR"
        return ("PASS" if passed else "FAIL"), f"WATER_REFLECTION_STATE({level})"
    if metric == "river_flow_state":
        # CL-DATA-77: the derived trailing-72h-precipitation level (waterfall
        # template T1; see river_flow_levels). operator "none" (threshold
        # null): mid/high satisfy the shootable window, "low" (dry 72h)
        # vetoes; very high is a caution note, not an exclusion. Malformed
        # operator or an unavailable derived cell degrades to UNKNOWN —
        # never a fabricated flow verdict.
        cell = values.get("river_flow_state") if isinstance(values, dict) else None
        if not isinstance(cell, dict) or cell.get("state") != "AVAILABLE":
            return "UNKNOWN", "RIVER_FLOW_STATE_DERIVATION_UNAVAILABLE"
        level = cell.get("value")
        if level not in RIVER_FLOW_LEVELS:
            return "UNKNOWN", "RIVER_FLOW_STATE_INVALID_LEVEL"
        if operator not in ("none", None):
            return "UNKNOWN", "UNSUPPORTED_RIVER_FLOW_OPERATOR"
        passed = level != "low"
        return ("PASS" if passed else "FAIL"), f"RIVER_FLOW_STATE({level})"
    if metric == "spring_tide_state":
        # CL-DATA-77: spring-tide band proxy (jp-030-P01 Naruto whirlpools).
        # Spring tides follow syzygy (new/full moon); the band spans ~±2.7
        # days around syzygy, proxied by the moon illumination fraction
        # (<=8% or >=92%). Pure astro input — no new provider, no fabricated
        # tide curve; the official tide-table best hours stay a documented
        # check-yourself semantic (claim jp-030-P01-claim-02). An unknown
        # illumination propagates UNKNOWN (fail-closed).
        illum = (astro_row.get("moon_illumination_fraction")
                 if isinstance(astro_row, dict) else None)
        if not isinstance(illum, (int, float)) or isinstance(illum, bool):
            return "UNKNOWN", "MOON_ILLUMINATION_UNAVAILABLE"
        if operator not in ("none", None):
            return "UNKNOWN", "UNSUPPORTED_SPRING_TIDE_OPERATOR"
        in_band = (float(illum) <= SPRING_TIDE_ILLUM_MAX
                   or float(illum) >= SPRING_TIDE_ILLUM_MIN)
        detail = (f"SPRING_TIDE(illum={round(float(illum), 3)}, band "
                  f"<= {SPRING_TIDE_ILLUM_MAX} or >= {SPRING_TIDE_ILLUM_MIN})")
        return ("PASS" if in_band else "FAIL"), detail
    if metric == "fog_state":
        # CL-DATA-73: the misty-forest decisive condition evaluates the DERIVED
        # fog-state cell (fog / forming / not_forming / no_fog). The owner
        # ANY semantics (fog present OR fog forming) is one branch here:
        # "fog" and "forming" both satisfy; "not_forming" and "no_fog"
        # fail — visibility > 1 km is the explicit 無霧 failure. The contract
        # carries no threshold (operator "none"); a malformed operator
        # degrades to UNKNOWN, never a fabricated verdict.
        cell = values.get("fog_state") if isinstance(values, dict) else None
        if not isinstance(cell, dict) or cell.get("state") != "AVAILABLE":
            return "UNKNOWN", "FOG_STATE_DERIVATION_UNAVAILABLE"
        level = cell.get("value")
        if level not in FOG_LEVELS:
            return "UNKNOWN", "FOG_STATE_INVALID_LEVEL"
        if operator not in ("none", None):
            return "UNKNOWN", "UNSUPPORTED_FOG_STATE_OPERATOR"
        passed = level in ("fog", "forming")
        return ("PASS" if passed else "FAIL"), f"FOG_STATE({level})"

    if metric == "snow_cover_state":
        # CL-DATA-74: the snow_scene family evaluates the DERIVED ground-state
        # enum the batch runner computes per hour from the Open-Meteo snow
        # fields (snow_cover_state: snowing / snow_covered / none). The ticket
        # semantics is an OR (snowfall > 0 OR snow_depth > 0) — the derived
        # enum collapses it into one displayable state so a flat-AND contract
        # list never demands both at once. operator "none" (threshold null):
        # only "none" (neither falling nor lying snow) vetoes; snowing and
        # snow_covered both satisfy. Fail-closed: a missing/invalid snow cell
        # propagates UNKNOWN — never a fabricated "no snow".
        cell = values.get("snow_cover_state") if isinstance(values, dict) else None
        if not isinstance(cell, dict) or cell.get("state") != "AVAILABLE":
            return "UNKNOWN", "SNOW_COVER_STATE_DERIVATION_UNAVAILABLE"
        level = cell.get("value")
        if level not in ("snowing", "snow_covered", "none"):
            return "UNKNOWN", "SNOW_COVER_STATE_INVALID_LEVEL"
        if operator in ("none", None):
            passed = level != "none"
        elif operator == "neq":
            passed = level != threshold
        elif operator == "eq":
            passed = level == threshold
        else:
            return "UNKNOWN", "NON_NUMERIC_OPERATOR"
        return ("PASS" if passed else "FAIL"), f"SNOW_COVER_STATE({level})"
    if metric == "venue_open_window":
        return venue_open_verdict(condition, local_start_min)
    if metric in ("cloud_base_height", "lcl_height_m_agl"):
        # CL-DATA-71 + CL-PHYS-02 §1 (datum fix): viewpoint-relative
        # cloud-base window for the cloud-sea/雲瀑/霧海/琉璃光 families.
        # The observation is the pipeline's LCL proxy cell
        # (lcl_height_m_agl — metres ABOVE THE GRID CELL'S GROUND, never
        # ASL). Both the observed base and the threshold are therefore
        # judged on the ASL datum: the observed base is
        # grid_elevation + lcl_height_m_agl, and an absolute threshold
        # (the CL-DATA-12 DEM−200 rule, lt viewpoint elevation − 200) is
        # already ASL. A catalog band (between, e.g. 琉璃光 50–120 m) is
        # recorded as cloud-base HEIGHT RELATIVE TO THE VIEWPOINT, so the
        # ASL base is converted back to a viewpoint-relative height for
        # that operator only. Never compare AGL to ASL. See
        # cloud_base_verdict() for the single implementation.
        return cloud_base_verdict(condition, values)
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
    if metric == "moon_illumination_fraction":
        # CL-DATA-72 batch A / CL-COND-A3: a moon BELOW the horizon cannot
        # illuminate the sky — the phase fraction of an unseen moon (jp-021-P02
        # 2026-11-19 02:00-05:00: moon -18 to -50 deg, proxy 0, yet vetoed by
        # 0.52-0.81 illumination) must never gate the hour. The gate stays
        # active only while the moon is up; below the horizon it passes
        # outright. An unknown moon altitude falls through to the generic gate
        # (value None -> UNKNOWN), never a fabricated PASS.
        alt = astro_row.get("moon_altitude") if isinstance(astro_row, dict) else None
        if isinstance(alt, (int, float)) and not isinstance(alt, bool) and alt < 0:
            return "PASS", "MOON_BELOW_HORIZON_PASS"
    if metric == "moon_target_separation_deg":
        # CL-DATA-78 Phase 1 (spec-quality-engine.md §2): the spec's 月亮-目標夾
        # angle is the moon vs the SUBJECT'S VIEWING DIRECTION. When the batch
        # runner resolved a view azimuth from the opportunity's observation
        # relations (bound below alongside light_direction), the separation is
        # the cyclic azimuth-plane difference between the moon azimuth and the
        # view azimuth — fail-closed: an unknown moon azimuth propagates
        # UNKNOWN (never a fabricated angle); below-horizon moons pass via
        # the same MOON_BELOW_HORIZON semantics as the illumination gate (the
        # alternation anchor stands the whole moon set down anyway).
        # Contracts WITHOUT a resolvable view azimuth keep the legacy
        # galactic-core-target separation value below (unchanged behaviour —
        # zero verdict drift for the 34 serving contracts; the target stays
        # the galactic core per the metric-vocabulary note).
        view_az = condition.get("view_azimuth_deg")
        if isinstance(view_az, (int, float)) and not isinstance(view_az, bool):
            alt = astro_row.get("moon_altitude") if isinstance(astro_row, dict) else None
            if isinstance(alt, (int, float)) and not isinstance(alt, bool) and alt < 0:
                return "PASS", "MOON_BELOW_HORIZON_PASS"
            moon_az = astro_row.get("moon_azimuth_deg") if isinstance(astro_row, dict) else None
            if not isinstance(moon_az, (int, float)) or isinstance(moon_az, bool):
                return "UNKNOWN", "MOON_AZIMUTH_UNKNOWN"
            diff = abs(float(moon_az) - float(view_az)) % 360.0
            diff = min(diff, 360.0 - diff)
            try:
                passed = compare(diff, operator, threshold)
            except Exception:
                return "UNKNOWN", "INVALID_THRESHOLD"
            detail = (f"MOON_TARGET_SEPARATION(view_az={round(float(view_az), 1)}, "
                      f"moon_az={round(float(moon_az), 1)}, sep={round(diff, 1)})")
            return ("PASS" if passed else "FAIL"), detail
        # CL-DATA-72 batch A / C3 (fail-closed sentinel): astro_hourly reports
        # 999 when the moon is below the horizon. It must never be compared as
        # a real 999-degree separation (the old permanent-PASS); when this
        # branch is reached the condition is actually being judged, so the
        # sentinel degrades to NOT_EVALUABLE. (With the M2/M3/M5 alternation
        # below, a met moon_altitude anchor stands this condition down to PASS
        # BEFORE judging — see moon_alternation_states.)
        value = astro_row.get(metric) if isinstance(astro_row, dict) else None
        if value is not None and not isinstance(value, bool) \
                and float(value) >= 900.0:
            return "UNKNOWN", "MOON_BELOW_HORIZON_SENTINEL_NOT_EVALUABLE"
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


def condition_value(condition, values, astro_row, local_date=None,
                    local_start_min=None):
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
    if metric == "river_flow_state":
        # CL-DATA-77: display the derived level the verdict judged on; a
        # legacy boolean cell (pre-derivation shape) still maps to the
        # satisfied/unsatisfied enum like any other boolean observation.
        cell = values.get("river_flow_state")
        if not isinstance(cell, dict) or cell.get("state") != "AVAILABLE":
            return None
        value = cell.get("value")
        if isinstance(value, bool):
            return boolean_value_label(value)
        return value
    if metric == "spring_tide_state":
        # CL-DATA-77: display the boolean the verdict judged on (the UI maps
        # it to the satisfied/unsatisfied enum, never a raw boolean).
        illum = (astro_row.get("moon_illumination_fraction")
                 if isinstance(astro_row, dict) else None)
        if not isinstance(illum, (int, float)) or isinstance(illum, bool):
            return None
        return (float(illum) <= SPRING_TIDE_ILLUM_MAX
                or float(illum) >= SPRING_TIDE_ILLUM_MIN)
    if metric == "seasonal_state":
        # CL-COND-A8: display the resolved window value (window_open /
        # rationale documents this display value.
        verdict, _detail = seasonal_window_verdict(
            condition.get("seasonal_entries") or [], local_date)
        return {"PASS": "window_open", "FAIL": "window_closed"}.get(verdict)
    if metric == "cloud_base_height":
        # CL-DATA-71 + CL-PHYS-02 §1: display the ASL cloud base the window
        # was judged on (grid elevation + LCL), never the raw AGL proxy.
        value, _reason = lcl_asl_m(values)
        return None if value is None else round(float(value), 1)
    if metric == "lcl_height_m_agl":
        # CL-PHYS-02 §1: the cloud_sea family's cloud-base observation is
        # published on the same ASL datum as the verdict.
        value, _reason = lcl_asl_m(values)
        return None if value is None else round(float(value), 1)
    if metric in PHYS_GATE_METRICS:
        # CL-PHYS-02/03 gates: display the derived level the verdict judged on.
        cell = phys_gate_state(condition, values, local_date=local_date,
                               local_start_min=local_start_min)
        return cell.get("value") if cell.get("state") == "AVAILABLE" else None
    if metric == "snow_cover_state":
        # CL-DATA-74: display the derived ground-state the verdict judged on.
        cell = values.get("snow_cover_state")
        if not isinstance(cell, dict) or cell.get("state") != "AVAILABLE":
            return None
        return cell.get("value")
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


# CL-DATA-72 batch A / CL-COND-A4 (audit A3+A4): the night-sky moon condition
# set is an ALTERNATION, not a flat AND — templates/night_sky.json marks M3
# (moon_target_separation_deg >= 40) and M5 (moon_illuminance_proxy <= 0.15)
# with activate_when {template_ref: M2, mode: when_not_met}: M2 (moon_altitude
# < 0, the moon below the horizon) is the preferred state, and when it is NOT
# met (moon up) the pair (M3, M5) takes over. Flat ANDing them (the old
# behaviour) vetoed moon-up/far-from-core hours (audit A4: moon 5 deg,
# separation 86.7 deg, M3 PASS not credited) and, via B2, moon-below-horizon
# hours (audit A3). The evaluator now applies the alternation:
#   anchor (moon_altitude < 0) PASS  -> moon down: the moon-constraint set is
#                                       satisfied; M3/M5 stand down (PASS).
#   anchor FAIL                      -> moon up: M3/M5 keep their own verdicts
#                                       (M2's FAIL no longer gates — it was
#                                       only the selector).
#   anchor UNKNOWN                   -> propagate UNKNOWN (honest).
# Applies to night_sky contracts and to the blue_tears copies of the same
# moon set (template-less genre); a contract without a moon_altitude anchor is
# evaluated flat, exactly as before.
MOON_ALTERNATION_DEPENDENTS = ("moon_target_separation_deg",
                               "moon_illuminance_proxy")


def moon_alternation(conditions):
    """Return (anchor_condition_id, [dependent_condition_id, ...]) or None.

    The anchor is the contract's moon_altitude condition with operator lt and
    threshold <= 0 (the M2 semantics); dependents are the M3/M5 metrics that
    templates declare activate_when M2 when_not_met.
    """
    anchor = next((c for c in conditions
                   if c.get("metric") == "moon_altitude"
                   and c.get("operator") == "lt"
                   and isinstance(c.get("threshold"), (int, float))
                   and not isinstance(c.get("threshold"), bool)
                   and c["threshold"] <= 0), None)
    if anchor is None:
        return None
    deps = [c["id"] for c in conditions
            if c.get("metric") in MOON_ALTERNATION_DEPENDENTS]
    return (anchor["id"], deps)


def apply_moon_alternation(states, alternation):
    """Rewrite the alternation verdicts (in place) for one hour.

    anchor PASS (moon below horizon): the moon-constraint set is satisfied —
    dependents stand down to PASS (moon 999 separation sentinel is never
    judged on those hours). anchor FAIL (moon up): the anchor was only the
    selector, so its own FAIL is neutralized and the dependents' real verdicts
    (separation / illuminance proxy) gate instead. anchor UNKNOWN propagates.
    """
    if not alternation:
        return
    anchor_id, deps = alternation
    anchor_state = states.get(anchor_id)
    if anchor_state == "PASS":
        for dep in deps:
            states[dep] = "PASS"
    elif anchor_state == "FAIL":
        states[anchor_id] = "PASS"
        # dependents keep their own evaluated verdicts
    elif anchor_state == "UNKNOWN":
        for dep in deps:
            states[dep] = "UNKNOWN"


# CL-DATA-72 batch A — CL-COND-A7 (owner ruling, batch-A item 4): the
# reflection family's water-surface state is DERIVED per hour from the forecast
# cells the pipeline already fetches — wind speed, precipitation and 2 m air
# temperature — instead of staying a permanent no-source UNKNOWN that blinded
# 47 REQUIRED contracts (whole-genre NOT_EVALUABLE, 5 satisfied days in the
# entire bundle). Levels (owner-decreed three-state scale):
#   mirror    鏡面: wind <= 1.5 m/s, no rain now AND no measurable rain in the
#             past 2-6 h (>= 2 h of history is required to claim it), air temp
#             > 0 °C — the highest-probability specular water.
#   shootable 可拍: wind <= 3 m/s and near-no-rain (< 0.2 mm/h) — ripples OK,
#             reflections still form.
#   unfit     不宜: wind > 3 m/s, or rain >= 0.2 mm/h, or air temp <= 0 °C
#             (icing risk — honestly annotated 可能結冰 in the copy layer).
# Marine wave height ( > 0.3 m -> unfit) has NO connected source in the batch
# adapter; the gap is documented in the metric-vocabulary entry instead of a
# fabricated 0. Tide-decided shoreline subjects (高美濕地 etc.) do NOT use
# this proxy at all — their contracts keep water_surface_state (no-source,
# honest NOT_EVALUABLE, 拍攝指南 需查潮汐表).
REFLECTION_MIRROR_MAX_WIND_MS = 1.5
REFLECTION_SHOOTABLE_MAX_WIND_MS = 3.0
REFLECTION_RAIN_MM = 0.2
REFLECTION_DRY_TRACE_MM = 0.05
REFLECTION_MIN_HISTORY_HOURS = 2
REFLECTION_HISTORY_WINDOW_HOURS = 6


def water_reflection_levels(hours):
    """Per-hour derived water_reflection_state cells, aligned with `hours`.

    Fail-closed: any hour missing a usable wind or precipitation cell gets an
    UNKNOWN cell (the condition then degrades to REFLECTION_STATE_DERIVATION_
    UNAVAILABLE, never a fabricated level). Temperature only decides between
    "unfit by icing" and the wind/rain scale; an unknown temperature simply
    cannot certify mirror (it stays shootable/unfit by wind+rain).
    """
    levels = []
    precip_history = []
    for hour_row in hours:
        values = hour_row.get("values") or {}

        def _cell(name, _values=values):
            cell = _values.get(name)
            if (isinstance(cell, dict) and cell.get("state") == "AVAILABLE"
                    and isinstance(cell.get("value"), (int, float))
                    and not isinstance(cell.get("value"), bool)):
                return float(cell["value"])
            return None

        wind = _cell("wind_speed_10m")
        precip = _cell("precipitation")
        temp = _cell("temperature_2m")
        if wind is None or precip is None:
            levels.append({"state": "UNKNOWN", "value": None})
            precip_history.append(None)
            continue
        history = [p for p in precip_history[-REFLECTION_HISTORY_WINDOW_HOURS:]
                   if p is not None]
        dry_recent = (len(history) >= REFLECTION_MIN_HISTORY_HOURS
                      and max(history) <= REFLECTION_DRY_TRACE_MM)
        if temp is not None and temp <= 0.0:
            level = "unfit"  # icing risk (可能結冰) — honest annotate in copy
        elif wind > REFLECTION_SHOOTABLE_MAX_WIND_MS or precip >= REFLECTION_RAIN_MM:
            level = "unfit"
        elif (wind <= REFLECTION_MIRROR_MAX_WIND_MS and precip == 0.0
                and dry_recent and temp is not None and temp > 0.0):
            # mirror needs a certified > 0 deg air temperature; an unknown
            # temperature cannot certify it and stays "shootable" at most
            level = "mirror"
        elif wind <= REFLECTION_SHOOTABLE_MAX_WIND_MS and precip < REFLECTION_RAIN_MM:
            level = "shootable"
        else:
            level = "unfit"
        levels.append({"state": "AVAILABLE", "value": level})
        precip_history.append(precip)
    return levels


# CL-DATA-77: river flow state for the waterfall family — the decisive
# condition the waterfall template (data/v2/templates/waterfall.json T1)
# already declares: river_flow_state is DERIVED per hour from the trailing
# 72h accumulated precipitation (provisional mapping <5 mm low, 5-40 mid,
# >40 high, pending real-shoot calibration). The mapping was drafted in the
# template but never wired into the evaluator, which left every
# genre_template=waterfall contract permanently NOT_EVALUABLE
# (METRIC_NOT_MAPPED -> REQUIRED UNKNOWN). Levels follow the template
# rationale: mid/high are the shootable window; very high (>40 mm) is a
# caution note, not an exclusion — only a dry (<5 mm) 72h window vetoes.
RIVER_FLOW_TRAILING_HOURS = 72
RIVER_FLOW_LOW_MM = 5.0
RIVER_FLOW_HIGH_MM = 40.0
RIVER_FLOW_LEVELS = ("low", "mid", "high")


def river_flow_levels(hours, trailing_past_mm):
    """Per-hour derived river_flow_state cells, aligned with `hours`.

    `trailing_past_mm` is the adapter's trailing hourly precipitation series
    (RIVER_FLOW_TRAILING_HOURS values ending at the hour before the horizon
    start) or None when the past-window fetch failed (fail-closed: every hour
    then degrades to UNKNOWN, never a fabricated flow level). The full series
    (past + in-horizon) makes every window EXACT — no extrapolation; a window
    containing a missing cell degrades that hour to UNKNOWN.
    """
    levels = []
    series = list(trailing_past_mm or [])
    if series is None:
        series = []
    for hour_row in hours:
        values = hour_row.get("values") or {}
        cell = values.get("precipitation")
        if (isinstance(cell, dict) and cell.get("state") == "AVAILABLE"
                and isinstance(cell.get("value"), (int, float))
                and not isinstance(cell.get("value"), bool)
                and cell["value"] >= 0):
            series.append(float(cell["value"]))
        else:
            series.append(None)
        window = series[-RIVER_FLOW_TRAILING_HOURS:]
        if len(window) < RIVER_FLOW_TRAILING_HOURS \
                or any(v is None for v in window):
            levels.append({"state": "UNKNOWN", "value": None})
            continue
        trailing = sum(window)
        if trailing < RIVER_FLOW_LOW_MM:
            level = "low"
        elif trailing <= RIVER_FLOW_HIGH_MM:
            level = "mid"
        else:
            level = "high"
        levels.append({"state": "AVAILABLE", "value": level})
    return levels


# CL-DATA-73: misty-forest fog state. The fog IS the subject, so the decisive
# condition INVERTS the usual visibility logic — owner-approved exception to
# the "no fabricated reverse visibility thresholds" doctrine (fog is the only
# genre where the inverted metric is the photographic subject itself). The
# derivation unifies the owner-specified ANY branches into one per-hour cell:
#   fog        霧正在發生: 0.05 km <= visibility <= 0.5 km (50-500 m)
#   forming    霧形成中:   visibility outside the fog band but RH >= 95%
#                          AND (T - Td) < 1 deg C
#   not_forming 霧未成形:  visibility <= 1 km but neither branch holds
#   no_fog     無霧:      visibility > 1 km — the explicit "no fog" failure
# Visibility drives the verdict when known; a missing visibility cell degrades
# the hour to UNKNOWN (fail-closed), never a fabricated level.
FOG_PRESENT_MIN_KM = 0.05
FOG_PRESENT_MAX_KM = 0.5
FOG_NO_FOG_KM = 1.0
FOG_FORMING_RH_PCT = 95.0
FOG_FORMING_DEW_SPREAD_C = 1.0
FOG_LEVELS = ("fog", "forming", "not_forming", "no_fog")


def fog_states(hours):
    """Per-hour derived fog_state cells, aligned with `hours`.

    Fail-closed: a missing/unusable visibility cell yields an UNKNOWN cell
    (the condition then reads FOG_STATE_DERIVATION_UNAVAILABLE). RH/temperature
    spread are only consulted inside the forming branch; unknown supporting
    cells there simply leave the hour not_forming-or-no_fog by visibility —
    they never fabricate a forming verdict.
    """
    states_out = []
    for hour_row in hours:
        values = hour_row.get("values") or {}
        cell = values.get("visibility")
        vis = None
        if (isinstance(cell, dict) and cell.get("state") == "AVAILABLE"
                and isinstance(cell.get("value"), (int, float))
                and not isinstance(cell.get("value"), bool)
                and cell["value"] >= 0):
            vis = float(cell["value"])
        if vis is None:
            states_out.append({"state": "UNKNOWN", "value": None})
            continue
        if FOG_PRESENT_MIN_KM <= vis <= FOG_PRESENT_MAX_KM:
            level = "fog"
        elif vis > FOG_NO_FOG_KM:
            level = "no_fog"
        else:
            rh = _cell_value(values, "relative_humidity_2m")
            temp = _cell_value(values, "temperature_2m")
            dew = _cell_value(values, "dew_point_2m")
            forming = (rh is not None and rh >= FOG_FORMING_RH_PCT
                       and temp is not None and dew is not None
                       and (temp - dew) < FOG_FORMING_DEW_SPREAD_C)
            level = "forming" if forming else "not_forming"
        states_out.append({"state": "AVAILABLE", "value": level})
    return states_out


def _cell_value(values, name):
    cell = (values or {}).get(name)
    if (isinstance(cell, dict) and cell.get("state") == "AVAILABLE"
            and isinstance(cell.get("value"), (int, float))
            and not isinstance(cell.get("value"), bool)):
        return float(cell["value"])
    return None


# ---------------------------------------------------------------------------
# CL-PHYS-02 stage 1 — datum (AGL → ASL), In-Cloud Fog hard block, data
# contradiction downgrade, and the 雲海 criteria transition.
#
# DATUM. The Open-Meteo LCL proxy `lcl_height_m_agl` is 125·(T2m − Td2m)
# metres above the GRID CELL'S GROUND. Every comparison against a viewpoint
# elevation (m ASL) must convert it first: base_asl = grid_elevation_m +
# lcl_height_m_agl. Judging the AGL number directly against an ASL threshold
# read a cloud base that sits OVERHEAD as a cloud sea below the feet —
# 大屯山助航站 (tw-001-P02: grid 1082 m + LCL 25 m = 1107 m ASL, above the
# 1092 m viewpoint) satisfied `lcl_height_m_agl lt 892` and a white-out fog
# wall was recommended. Never compare AGL with ASL.
# ---------------------------------------------------------------------------
CLOUD_BASE_OPERATORS = ("lt", "lte", "gt", "gte", "between")
# In-Cloud Fog Override (§2), all subjects: the viewpoint is inside the cloud
# when the (ASL) cloud base is at or below the viewpoint + 50 m AND the air
# has a deck there (low cloud >= 80% or RH850 >= 95%).
IN_CLOUD_MARGIN_M = 50.0
IN_CLOUD_LOW_CLOUD_PCT = 80.0
IN_CLOUD_RH850_PCT = 95.0
# An in-cloud hour is treated as 濃霧 for every general subject: below the
# lowest published visibility band, i.e. scene readability ~0.
IN_CLOUD_EFFECTIVE_VISIBILITY_KM = 0.2
# CL-PHYS-03 §2 (over-block fix): raw visibility at/above this proves the air
# is clear, so the in-cloud geometry may not close the veto (see
# in_cloud_fog_state). 10 km is the same band the data-contradiction gate uses.
IN_CLOUD_CLEAR_VISIBILITY_KM = 10.0
# Dedicated fog subjects are the ONLY subjects an in-cloud hour serves — the
# fog IS the picture (CL-DATA-73 misty_forest). Every other genre (landscape,
# sunrise, sunset, cloud_sea, night, ...) is blocked.
FOG_SUBJECT_GENRES = frozenset({"misty_forest"})
# Data-contradiction downgrade (§3): 低雲 >= 90% together with a raw
# visibility >= 10 km cannot both describe the same air; the pair is tagged
# and the slot is capped below ✓ 推薦.
CONTRADICTION_LOW_CLOUD_PCT = 90.0
CONTRADICTION_VISIBILITY_KM = 10.0
# 雲海 criteria transition (§4): with the single summit grid point now on the
# ASL datum the cloud-base window can only say "the base is at/above the
# summit" — a deck BELOW the summit implies a supersaturated grid point and
# the LCL proxy refuses that input. The cloud-sea PRIMARY criterion is
# therefore the high-humidity inversion structure (RH850 or RH925 >= 90% —
# the moist layer the deck sits in) plus the low-cloud amount (>= 60%). The
# valley dual-grid model that would resolve the deck height directly is
# explicitly deferred to CL-DATA-85.
CLOUD_SEA_RH_PRIMARY_PCT = 90.0
CLOUD_SEA_LOW_CLOUD_PCT = 60.0

IN_CLOUD_FOG_METRIC = "in_cloud_fog"
DATA_CONTRADICTION_METRIC = "data_contradiction"
CLOUD_SEA_INVERSION_METRIC = "cloud_sea_inversion"
PHYS_GATE_METRICS = (IN_CLOUD_FOG_METRIC, DATA_CONTRADICTION_METRIC,
                     CLOUD_SEA_INVERSION_METRIC)


def grid_elevation_m(values):
    """CL-PHYS-02 §1: the grid cell's ground elevation in metres ASL."""
    return _cell_value(values, "grid_elevation_m")


def lcl_asl_m(values):
    """CL-PHYS-02 §1: the LCL cloud base on the ASL datum.

    Returns (value_m_asl, reason). A missing LCL cell or a missing grid
    elevation is never defaulted to zero — the caller propagates UNKNOWN.
    A REFUSED LCL (supersaturated T2m − Td2m, adapter reason_code
    SUPERSATURATED) is reported as LCL_SUPERSATURATED so the in-cloud gate
    can distinguish "no observation" from "the air is at saturation".
    """
    lcl_cell = values.get("lcl_height_m_agl")
    lcl = _cell_value(values, "lcl_height_m_agl")
    if lcl is None:
        reason_code = (lcl_cell.get("reason_code")
                       if isinstance(lcl_cell, dict) else None)
        return None, ("LCL_SUPERSATURATED" if reason_code == "SUPERSATURATED"
                      else "CELL_NOT_AVAILABLE")
    grid = grid_elevation_m(values)
    if grid is None:
        return None, "GRID_ELEVATION_UNKNOWN"
    return grid + lcl, None


def cloud_base_verdict(condition, values, require_viewpoint=True):
    """CL-DATA-71 + CL-PHYS-02 §1: one cloud-base comparison, one datum.

    The observed base is converted AGL → ASL (grid elevation + LCL) before
    it meets any threshold. Absolute operators (lt/lte/gt/gte) carry an ASL
    threshold — the CL-DATA-12 DEM−200 rule (`lt viewpoint − 200`). The
    `between` operator carries a catalog-recorded band (琉璃光 50–120 m) that
    is a height RELATIVE TO THE VIEWPOINT, so the ASL base is expressed
    relative to the viewpoint for that comparison only. Fail-closed: a
    missing viewpoint elevation (when required), cell or grid elevation
    propagates UNKNOWN, never a fabricated verdict.
    """
    elevation = condition.get("viewpoint_elevation_m")
    have_elevation = (isinstance(elevation, (int, float))
                      and not isinstance(elevation, bool))
    if require_viewpoint and not have_elevation:
        return "UNKNOWN", "VIEWPOINT_ELEVATION_UNKNOWN"
    operator = condition.get("operator")
    threshold = condition.get("threshold")
    if operator not in CLOUD_BASE_OPERATORS:
        return "UNKNOWN", "NON_NUMERIC_OPERATOR"
    if operator == "between":
        if not have_elevation:
            return "UNKNOWN", "VIEWPOINT_ELEVATION_UNKNOWN"
        if not isinstance(threshold, list) or len(threshold) != 2:
            return "UNKNOWN", "INVALID_THRESHOLD"
    base_asl, reason = lcl_asl_m(values)
    if base_asl is None:
        return "UNKNOWN", reason
    grid = grid_elevation_m(values)
    grid_m = float(grid) if grid is not None else 0.0
    # CL-PHYS-02 §1 (datum, reviewer blocker 2): a `lt viewpoint − N` window
    # whose threshold lies BELOW the grid ground is physically
    # unimplementable on this datum. The parcel LCL is measured from the grid
    # ground, so base_asl >= grid always; when threshold < grid the
    # comparison can never pass and the condition would pin the subject at
    # 不宜 for every hour of every run. The single summit grid point simply
    # cannot resolve a base below its own ground, so the window is
    # UNRESOLVABLE, not FAILED: UNKNOWN is the honest verdict (upstream it
    # becomes an advisory / NOT_EVALUABLE hour, never a fabricated pass).
    if (operator in ("lt", "lte")
            and isinstance(threshold, (int, float))
            and not isinstance(threshold, bool)
            and grid is not None
            and float(threshold) < grid_m - 1e-9):
        return "UNKNOWN", (
            f"CLOUD_BASE_WINDOW_UNRESOLVABLE(threshold={round(float(threshold))}m"
            f"<grid={round(grid_m)}m: LCL is measured from the grid ground)")
    if operator == "between":
        judged = float(base_asl) - float(elevation)
        datum_label = "above_viewpoint"
    else:
        judged = float(base_asl)
        datum_label = "asl"
    try:
        passed = compare(judged, operator, threshold)
    except Exception:
        return "UNKNOWN", "INVALID_THRESHOLD"
    detail = (f"CLOUD_BASE_HEIGHT(base_{datum_label}={round(judged)}m,"
              f"lcl_agl={round(float(base_asl) - grid_m)}m"
              f"+grid={round(grid_m)}m,"
              f"viewpoint={round(float(elevation)) if have_elevation else None}m)")
    return ("PASS" if passed else "FAIL"), detail


def in_cloud_fog_state(values, viewpoint_elevation_m):
    """CL-PHYS-02 §2: THE In-Cloud Fog predicate (single source of truth).

    Returns a derived cell:
        {"value": "in_cloud" | "clear", "state": "AVAILABLE"|"UNKNOWN", ...}

    `in_cloud` iff (cloud_base_asl <= viewpoint_elevation + 50 m) AND
    (cloud_cover_low >= 80 % OR RH850 >= 95 %). Both sides of the geometry
    comparison are metres ASL. Missing moisture evidence (both cells absent)
    or missing grid geometry leaves the veto UNKNOWN and the caller treats it
    as unverified — a veto that cannot see is not a veto. Only a REFUSED LCL
    next to a saturated deck fails CLOSED (see below): the supersaturation
    refusal itself is the telephone-number fog signature. A merely absent
    LCL (NULL_OR_INVALID) makes no saturation claim and stays UNKNOWN.
    """
    if (not isinstance(viewpoint_elevation_m, (int, float))
            or isinstance(viewpoint_elevation_m, bool)):
        return {"state": "UNKNOWN", "value": None,
                "reason_code": "VIEWPOINT_ELEVATION_UNKNOWN"}
    low_cloud = _cell_value(values, "cloud_cover_low")
    rh850 = _cell_value(values, "relative_humidity_850hpa")
    if low_cloud is None and rh850 is None:
        return {"state": "UNKNOWN", "value": None,
                "reason_code": "MOISTURE_CELLS_UNAVAILABLE"}
    # CL-PHYS-03 §2 (over-block fix): the humidity side alone can fire on a
    # genuinely clear hour. us-158-P01 2026-12-02 10:00 had low cloud 17 %,
    # visibility 13.62 km — a clear sky — yet RH850 >= 95 % plus a near-ground
    # LCL (a moist boundary layer under a mid/high overcast) satisfied
    # "ceiling_inside AND humid" and vetoed it. 53 such hours were made 不宜
    # by this gate alone. Raw visibility IS the observation of whether the
    # viewpoint is inside cloud, so when the provider reports 10 km or more
    # the geometry cannot close the veto: the air is demonstrably clear and
    # the gate returns "clear". Deliberate OPEN choice — do not veto a clear
    # sky. (A saturated deck at 100 % LOW cloud with 10 km+ visibility is the
    # separate data-contradiction gate's job, not this one's.)
    raw_visibility = _cell_value(values, "visibility")
    if (raw_visibility is not None
            and raw_visibility >= IN_CLOUD_CLEAR_VISIBILITY_KM):
        return {"state": "AVAILABLE", "value": "clear",
                "reason_code": "VISIBILITY_DISPROVES_IN_CLOUD",
                "cloud_base_asl_m": None,
                "effective_visibility_km": raw_visibility}
    humid = ((low_cloud is not None and low_cloud >= IN_CLOUD_LOW_CLOUD_PCT)
             or (rh850 is not None and rh850 >= IN_CLOUD_RH850_PCT))
    base_asl, reason = lcl_asl_m(values)
    if base_asl is None:
        if reason == "GRID_ELEVATION_UNKNOWN":
            return {"state": "UNKNOWN", "value": None, "reason_code": reason}
        # FAIL CLOSED — but ONLY on a REFUSED (supersaturated) LCL. A
        # supersaturated parcel (T2m − Td2m < 0) is undefined precisely
        # BECAUSE the air is at or beyond saturation: the LCL sits at the
        # ground, i.e. the viewpoint is in the cloud, and with a saturated
        # deck (低雲 >= 80 % or RH850 >= 95 %) alongside the fog signature is
        # complete. An ABSENT LCL (NULL_OR_INVALID: the provider simply did
        # not ship the dew-point pair) is a different animal — there is no
        # saturation claim in it at all, so a dew-point gap on an overcast day
        # keeps its own reason code and stays UNKNOWN (資料不足), never a hard
        # ✕. "LCL present but grid geometry absent" is UNKNOWN for the same
        # reason: an ASL base exists to be computed, the elevation is the gap.
        if reason == "LCL_SUPERSATURATED" and humid:
            return {"state": "AVAILABLE", "value": "in_cloud",
                    "reason_code": "LCL_UNAVAILABLE_SATURATED_DECK",
                    "cloud_base_asl_m": None,
                    "effective_visibility_km": IN_CLOUD_EFFECTIVE_VISIBILITY_KM}
        return {"state": "UNKNOWN", "value": None, "reason_code": reason}
    ceiling_inside = base_asl <= float(viewpoint_elevation_m) + IN_CLOUD_MARGIN_M
    inside = ceiling_inside and humid
    return {"state": "AVAILABLE", "value": "in_cloud" if inside else "clear",
            "reason_code": None,
            "cloud_base_asl_m": round(float(base_asl), 1),
            "effective_visibility_km": (IN_CLOUD_EFFECTIVE_VISIBILITY_KM
                                        if inside else
                                        _cell_value(values, "visibility"))}


def data_contradiction_state(values):
    """CL-PHYS-02 §3: 低雲 >= 90 % vs raw visibility >= 10 km contradiction.

    Returns "contradiction" / "consistent" / UNKNOWN. Judged on the RAW
    visibility cell (never the in-cloud effective visibility), because the
    point is that the two provider fields disagree.
    """
    low_cloud = _cell_value(values, "cloud_cover_low")
    visibility = _cell_value(values, "visibility")
    if low_cloud is None or visibility is None:
        return {"state": "UNKNOWN", "value": None,
                "reason_code": "CONTRADICTION_CELLS_UNAVAILABLE"}
    contradicting = (low_cloud >= CONTRADICTION_LOW_CLOUD_PCT
                     and visibility >= CONTRADICTION_VISIBILITY_KM)
    return {"state": "AVAILABLE",
            "value": "contradiction" if contradicting else "consistent",
            "reason_code": None}


def cloud_sea_inversion_state(values, viewpoint_elevation_m):
    """CL-PHYS-02 §4: 雲海 primary criterion (RH inversion + low cloud).

    The criterion the owner ruled on is the inversion moisture layer
    (RH850 or RH925 >= 90 %) plus a low-cloud amount >= 60 % — the humid
    structure a cloud sea sits in. Deck height is a QUALITY modifier, never
    the gate: this model compares the LCL-derived base of the SUMMIT grid
    cell against the viewpoint, so a deck that sits at or above the summit
    is the model saying "the base over this cell is overhead", NOT the model
    saying "there is no sea". A real cloud sea is a deck in the VALLEY,
    which a single summit grid point cannot see (CL-DATA-85, out of scope).
    The classic dry-summit-above-valley-sea hour (LCL 800 m AGL, RH850 96 %,
    低雲 80 %) therefore returns UNKNOWN — 資料不足 — instead of a
    fabricated 逆溫濕層不足 FAIL. The same applies to the 12 cloud_sea spots
    whose viewpoint equals the grid elevation, where only LCL == 0 puts the
    modelled base at the ground.

    When the modelled deck IS genuinely at or below the viewpoint it is a
    resolved, sea-compatible geometry and the humidity pair decides
    PASS/FAIL. A willingness to place a deck below the summit is not
    evidence of one.
    """
    rh850 = _cell_value(values, "relative_humidity_850hpa")
    rh925 = _cell_value(values, "relative_humidity_925hpa")
    low_cloud = _cell_value(values, "cloud_cover_low")
    humidities = [rh for rh in (rh850, rh925) if rh is not None]
    if low_cloud is None or not humidities:
        return {"state": "UNKNOWN", "value": None,
                "reason_code": "INVERSION_CELLS_UNAVAILABLE"}
    if (not isinstance(viewpoint_elevation_m, (int, float))
            or isinstance(viewpoint_elevation_m, bool)):
        return {"state": "UNKNOWN", "value": None,
                "reason_code": "VIEWPOINT_ELEVATION_UNKNOWN"}
    deck_asl, reason = lcl_asl_m(values)
    if deck_asl is None:
        if reason == "GRID_ELEVATION_UNKNOWN":
            return {"state": "UNKNOWN", "value": None, "reason_code": reason}
        # Refused/absent LCL: saturated at the grid ground, so the deck
        # cannot be above the grid elevation.
        deck_asl = grid_elevation_m(values)
        if deck_asl is None:
            return {"state": "UNKNOWN", "value": None,
                    "reason_code": "GRID_ELEVATION_UNKNOWN"}
    deck_below = float(deck_asl) <= float(viewpoint_elevation_m)
    humid_structure = (max(humidities) >= CLOUD_SEA_RH_PRIMARY_PCT
                       and low_cloud >= CLOUD_SEA_LOW_CLOUD_PCT)
    if not deck_below:
        # The summit-cell deck is overhead. That is NOT evidence of a missing
        # sea — the valley deck is simply invisible to this model — so the
        # criterion abstains (資料不足) instead of failing. No humidity
        # evidence is consumed here: UNKNOWN either way.
        return {"state": "UNKNOWN", "value": None,
                "reason_code": "DECK_AT_OR_ABOVE_VIEWPOINT",
                "deck_ceiling_asl_m": round(float(deck_asl), 1),
                "deck_below_viewpoint": False,
                "humid_structure": humid_structure}
    return {"state": "AVAILABLE",
            "value": "inversion" if humid_structure else "no_inversion",
            "reason_code": None,
            "deck_ceiling_asl_m": round(float(deck_asl), 1),
            "deck_below_viewpoint": True}


def phys_gate_state(condition, values, local_start_min=None, local_date=None):
    """Derived cell for one CL-PHYS-02/03 gate condition."""
    metric = condition.get("metric")
    if metric == IN_CLOUD_FOG_METRIC:
        return in_cloud_fog_state(values, condition.get("viewpoint_elevation_m"))
    if metric == DATA_CONTRADICTION_METRIC:
        return data_contradiction_state(values)
    if metric == CLOUD_SEA_INVERSION_METRIC:
        return cloud_sea_inversion_state(
            values, condition.get("viewpoint_elevation_m"))
    if metric == FOG_VISIBILITY_METRIC:
        return fog_visibility_state(values)
    if metric == DATA_FLOOR_METRIC:
        return data_floor_state(values)
    if metric == SEASON_POLICY_METRIC:
        verdict, detail = season_policy_verdict(
            condition.get("policy_entry"), local_date)
        if verdict == "UNKNOWN":
            return {"state": "UNKNOWN", "value": None, "reason_code": detail}
        return {"state": "AVAILABLE",
                "value": "window_open" if verdict == "PASS" else "window_closed",
                "reason_code": None, "detail": detail}
    if metric == VENUE_HOURS_METRIC:
        verdict, detail = venue_hours_verdict(
            condition.get("policy_entry"), local_start_min)
        if verdict == "UNKNOWN":
            return {"state": "UNKNOWN", "value": None, "reason_code": detail}
        return {"state": "AVAILABLE",
                "value": "open" if verdict == "PASS" else "closed",
                "reason_code": None, "detail": detail}
    return {"state": "UNKNOWN", "value": None, "reason_code": "UNKNOWN_GATE"}


def phys_gate_verdict(condition, values, local_start_min=None, local_date=None):
    """PASS/FAIL/UNKNOWN for one CL-PHYS-02/03 gate condition.

    The VETO gates (in_cloud_fog, data_contradiction, fog_visibility) fail on
    their detected level and pass when the evidence is merely unverifiable:
    they remove a recommendation, they never manufacture a NOT_EVALUABLE hour.
    The data-completeness floor deliberately closes instead (CL-PHYS-03 §3):
    a recommendation needs usable inputs, so missing/thin data FAILS.
    The cloud_sea inversion gate is a real PRIMARY criterion and propagates
    UNKNOWN fail-closed when its cells are missing. The policy gates
    (season / venue hours) fail on a resolved closed state and abstain
    (UNKNOWN) only when the clock or the entry itself is unreadable.
    """
    metric = condition.get("metric")
    cell = phys_gate_state(condition, values,
                          local_start_min=local_start_min,
                          local_date=local_date)
    value = cell.get("value")
    if metric in (IN_CLOUD_FOG_METRIC, DATA_CONTRADICTION_METRIC):
        if cell.get("state") != "AVAILABLE":
            return "PASS", f"{metric.upper()}_UNVERIFIED"
        failing = "in_cloud" if metric == IN_CLOUD_FOG_METRIC else "contradiction"
        level = "FAIL" if value == failing else "PASS"
        return level, f"{metric.upper()}({value})"
    if metric == FOG_VISIBILITY_METRIC:
        return fog_visibility_verdict(condition, values)
    if metric == DATA_FLOOR_METRIC:
        # Deliberate CLOSED choice: "no usable weather input" is a refusal to
        # recommend, never a silent pass. reason codes ride in the detail so
        # the UI can say 資料不足 instead of a bare ✗.
        if cell.get("state") != "AVAILABLE":
            return "FAIL", "DATA_FLOOR_UNAVAILABLE"
        if value == "ok":
            return "PASS", "DATA_FLOOR(ok)"
        detail = cell.get("reason_code") or value
        if value == "visibility_low":
            detail = f"{detail}(vis={cell.get('visibility_km')}km)"
        return "FAIL", f"DATA_FLOOR({value}:{detail})"
    if metric in (SEASON_POLICY_METRIC, VENUE_HOURS_METRIC):
        if cell.get("state") != "AVAILABLE":
            reason = cell.get("reason_code") or "UNAVAILABLE"
            return "UNKNOWN", f"{metric.upper()}_{reason}"
        return (("PASS" if value in ("window_open", "open") else "FAIL"),
                cell.get("detail") or f"{metric.upper()}({value})")
    if cell.get("state") != "AVAILABLE":
        reason = cell.get("reason_code") or "UNAVAILABLE"
        return "UNKNOWN", f"{metric.upper()}_{reason}"
    return ("FAIL" if value == "no_inversion" else "PASS"), f"{metric.upper()}({value})"


def _phys_gate(cond_id, metric, notes):
    return {
        "id": cond_id,
        "role": "REQUIRED",
        "domain": "WEATHER",
        "evaluation_mode": "GUIDANCE",
        "capability": "CONDITIONS",
        "metric": metric,
        "operator": "none",
        "threshold": None,
        "condition_tier": "MAIN",
        "unknown_policy": "propagate_unknown",
        "threshold_source": "formula_derived",
        "calibration_status": "provisional",
        "claim_refs": [],
        "notes_i18n": notes,
    }


IN_CLOUD_FOG_GATE = _phys_gate(
    "EVALGATE-in-cloud-fog", IN_CLOUD_FOG_METRIC, {
        "zh-TW": "CL-PHYS-02 評估層硬擋（全題材）：雲底（格點海拔＋LCL，皆 ASL）"
                 "不高於觀測點 +50 m，且低雲 ≥80% 或 RH850 ≥95%，代表觀測點"
                 "身處雲霧內；有效能見度視為濃霧，一般風景／日出／日落／雲海／"
                 "夜景題材一律不宜。LCL 被拒絕（過飽和）且伴隨飽和雲層時一律"
                 "關閉放行（fail closed）：拒絕本身即是霧的訊號；LCL 單純缺值"
                 "（非過飽和）則維持資料不足，不硬擋。專拍霧的題材"
                 "（misty_forest）不受此擋。",
        "en": "CL-PHYS-02 evaluation-layer hard block (all subjects): when the "
              "cloud base (grid elevation + LCL, both ASL) is at or below the "
              "viewpoint +50 m AND low cloud >= 80% or RH850 >= 95%, the "
              "viewpoint is inside cloud/fog. Effective visibility is 濃霧 and "
              "every general landscape/sunrise/sunset/cloud-sea/night subject "
              "is not recommended. A REFUSED (supersaturated) LCL together with "
              "a saturated deck FAILS CLOSED: the refusal is itself the fog "
              "signature. A merely absent LCL (no dew-point pair) stays "
              "UNKNOWN (資料不足), never a hard block. Dedicated fog subjects "
              "(misty_forest) are exempt.",
        "ja": "CL-PHYS-02 評価層のハードブロック（全題材）：雲底（グリッド標高＋"
              "LCL、いずれもASL）が視点+50m以下、かつ低雲≥80%またはRH850≥95%なら"
              "視点は雲霧内。有効視程は濃霧とし、一般風景／日の出／日の入り／雲海／"
              "夜景は不適。LCLが拒否（過飽和）で飽和した雲層を伴う場合はフェイル"
              "クローズ。単なる欠測（露点なし）はUNKNOWN（資料不足）のまま。"
              "霧専門題材（misty_forest）は対象外。",
    })
DATA_CONTRADICTION_GATE = _phys_gate(
    "EVALGATE-data-contradiction", DATA_CONTRADICTION_METRIC, {
        "zh-TW": "CL-PHYS-02 資料矛盾降級：低雲 ≥90% 但原始能見度 ≥10 km，兩者"
                 "不可能同時描述同一團空氣；標記「資料矛盾／山區易起霧」，槽位"
                 "一律不得成為 ✓ 推薦。",
        "en": "CL-PHYS-02 data-contradiction downgrade: low cloud >= 90% with a "
              "raw visibility >= 10 km cannot describe the same air. The slot "
              "is tagged 「資料矛盾／山區易起霧」 and capped below recommend.",
        "ja": "CL-PHYS-02 データ矛盾の降格：低雲≥90%かつ生の視程≥10kmは同じ空気を"
              "記述できない。スロットは「資料矛盾／山區易起霧」とし推奨にしない。",
    })
CLOUD_SEA_INVERSION_GATE = _phys_gate(
    "EVALGATE-cloud-sea-inversion", CLOUD_SEA_INVERSION_METRIC, {
        "zh-TW": "CL-PHYS-02 雲海主判據：濕層逆溫（RH850 或 RH925 ≥90%）＋低雲量"
                 "≥60%（業主裁定）。雲底高度僅為品質修飾：模型比較的是「山頂格點」"
                 "的 LCL 雲底，谷地雲海（真正的雲海）單一格點看不到（CL-DATA-85）；"
                 "因此雲底高於或等於觀測點時本判據「資料不足」（UNKNOWN），"
                 "絕不判定不宜。僅當模型雲底確實低於觀測點時才由濕層結構判 PASS／FAIL。",
        "en": "CL-PHYS-02 cloud-sea primary criterion (owner ruling): humid "
              "inversion layer (RH850 or RH925 >= 90%) plus low-cloud amount "
              ">= 60%. Cloud-base height is a QUALITY modifier only: the model "
              "compares the LCL base of the SUMMIT grid cell, and the valley "
              "deck that a cloud sea actually is cannot be seen from a single "
              "grid point (CL-DATA-85). When the modelled base sits at or "
              "above the viewpoint the criterion is UNKNOWN (資料不足) — never "
              "不宜. Only a deck genuinely below the viewpoint lets the "
              "humidity structure decide PASS/FAIL.",
        "ja": "CL-PHYS-02 雲海の主判準（オーナー裁定）：湿潤逆転層（RH850または"
              "RH925≥90%）＋低雲量≥60%。雲底高度は品質修飾のみ：モデルは「山頂"
              "グリッド」のLCL雲底を比較し、谷の雲海は単一グリッドでは見えない"
              "（CL-DATA-85）。雲底が視点以上なら本判準はUNKNOWN（資料不足）で"
              "あり、不適とはしない。雲底が視点より下にある場合のみ湿潤構造で"
              "PASS/FAILを判定する。",
    })


def demote_cloud_sea_lcl(conditions, contract):
    """CL-PHYS-02 §4: the 雲海 cloud-base window becomes advisory.

    With the summit grid point on the ASL datum, `<base> lt viewpoint − 200`
    can only be satisfied by a base below the grid ground — a deck below
    the summit is not resolvable from a single summit grid point (the LCL
    proxy refuses the supersaturated input, and base_asl >= grid by
    construction). The condition keeps its honest verdict (UNRESOLVABLE /
    QUALITY signal) instead of gating every cloud-sea hour, and the
    inversion gate above becomes the primary criterion. Both cloud-base
    metric keys are covered: the cloud_sea family carries the window as
    `lcl_height_m_agl` in some contracts and as `cloud_base_height` in
    others (tw-035-P06 / tw-047-P01 / tw-049-P03), and keying on the
    metric name alone left the second spelling as a permanent 不宜.
    Evaluation-layer only: the owner contract and its sha are untouched.
    """
    if contract.get("genre_template") != "cloud_sea":
        return conditions
    out = []
    for condition in conditions:
        if (condition.get("metric") in ("lcl_height_m_agl", "cloud_base_height")
                and condition.get("role") == "REQUIRED"):
            condition = dict(
                condition, role="QUALITY", condition_tier="MODIFIER",
                cl_phys_02="cloud_sea_lcl_is_advisory_until_cl_data_85")
        out.append(condition)
    return out


def demote_unresolvable_cloud_base(conditions, contract, viewpoint_elevation_m,
                                   grid_elevation_m=None):
    """CL-PHYS-02 §4b: a cloud-base window below the ground is advisory.

    Every `lt/lte` cloud-base window outside cloud_sea is the DEM−200 rule
    (`threshold = viewpoint − 200 m`). Where the viewpoint sits on its own
    grid cell — which is the normal case, and the exact case of the nine
    subjects the reviewer named (tw-145-P01, tw-148-P01, tw-163-P01,
    tw-179-P01, jp-037-P02, us-113-P01, tw-043-P02, tw-047-P02,
    us-087-P01) — the parcel LCL is measured from that same ground, so
    base_asl >= grid and the threshold can never be met: a REQUIRED window
    that is permanently CLOUD_BASE_WINDOW_UNRESOLVABLE pins the whole
    subject at 不宜 for every hour of every run.

    The feasibility test is mechanical, not a hardcoded id list: a window
    whose threshold lies below the GRID GROUND — the datum the LCL is
    measured from — can never be met, because base_asl = grid + lcl >= grid.
    Keying on the grid ground rather than the viewpoint keeps a mountain
    viewpoint whose ground sits well below it (vp 3055 / grid 2700 /
    threshold 2855) resolvable and REQUIRED. Demoted to QUALITY so the
    resolvable part of the subject still produces a verdict and the dead
    clause reads as advisory. Evaluation-layer only — the owner contract
    (and its sha) is untouched.
    """
    conditions = list(conditions)
    if (not isinstance(viewpoint_elevation_m, (int, float))
            or isinstance(viewpoint_elevation_m, bool)):
        return conditions
    bound = (grid_elevation_m
             if (isinstance(grid_elevation_m, (int, float))
                 and not isinstance(grid_elevation_m, bool))
             else viewpoint_elevation_m)
    out = []
    for condition in conditions:
        threshold = condition.get("threshold")
        if (condition.get("metric") in ("cloud_base_height", "lcl_height_m_agl")
                and condition.get("role") == "REQUIRED"
                and condition.get("operator") in ("lt", "lte")
                and isinstance(threshold, (int, float))
                and not isinstance(threshold, bool)
                and float(threshold) < float(bound)):
            condition = dict(
                condition, role="QUALITY", condition_tier="MODIFIER",
                cl_phys_02="cloud_base_window_below_grid_is_advisory")
        out.append(condition)
    return out


def phys_gates_for(contract, viewpoint_elevation_m):
    """CL-PHYS-02: the evaluation-layer gates for one opportunity.

    in_cloud_fog  — all subjects except the dedicated fog genres (§2);
    data_contradiction — all subjects (§3);
    cloud_sea_inversion — cloud_sea subjects only (§4).
    """
    genre = contract.get("genre_template")
    gates = []
    if genre not in FOG_SUBJECT_GENRES:
        gates.append(dict(IN_CLOUD_FOG_GATE,
                          viewpoint_elevation_m=viewpoint_elevation_m))
        # CL-PHYS-03 §1: the global raw-hour visibility gate. Same exemption as
        # the in-cloud gate — for misty_forest the fog IS the picture.
        gates.append(dict(FOG_VISIBILITY_GATE))
    gates.append(dict(DATA_CONTRADICTION_GATE))
    # CL-PHYS-03 §3: the data-completeness/visibility floor applies to EVERY
    # subject, fog genres included: no usable inputs, no recommendation.
    gates.append(dict(DATA_FLOOR_GATE))
    if genre == "cloud_sea":
        gates.append(dict(CLOUD_SEA_INVERSION_GATE,
                          viewpoint_elevation_m=viewpoint_elevation_m))
    return gates

# ---------------------------------------------------------------------------
# CL-PHYS-03 — evaluation-layer gates (no contract edits, schema_version stays
# 10, contract_sha256 stays over the owner contract).
#
# 1. FOG / VISIBILITY (global white-wall gate). The CL-PHYS-02 in-cloud gate
#    only sees the grid's own moisture geometry (LCL ASL vs viewpoint). A
#    contract without `cloud_cover_low`/`visibility` conditions (e.g.
#    tw-112-P01 geological_landform, us-162-P01) therefore still read
#    GUIDANCE_SATISFIED on an hour whose RAW visibility is 0.1 km and whose
#    low cloud is 100 % — 25 spots / 155 hours on the 2026-11-26 live bundle.
#    The veto belongs to the evaluation layer, once, as a pure predicate over
#    the raw hour cells — never to each owner contract:
#      visibility <  2 km                                  -> ✕ 濃霧 (whiteout)
#      visibility < 10 km AND low cloud >= 90 %             -> ✕ (solid deck,
#                                                            白牆/雨幕)
#      visibility <  5 km                                  -> cap below 推薦
#                                                            (haze: shootable,
#                                                             not recommendable)
#      otherwise                                            -> clear
#    Dedicated fog subjects (misty_forest) stay exempt: for them the fog IS
#    the picture, exactly as with the CL-PHYS-02 in-cloud gate.
# ---------------------------------------------------------------------------
FOG_VISIBILITY_METRIC = "fog_visibility"
# ✕ 濃霧: below the lowest published visibility band — scene readability ~0.
FOG_WHITEOUT_KM = 2.0
# ✕ 白牆: a solid low deck with visibility below 10 km is a white wall even
# when the grid's LCL arithmetic happens to place the ceiling overhead.
FOG_DECK_VISIBILITY_KM = 10.0
FOG_DECK_LOW_CLOUD_PCT = 90.0
# Cap (never a veto): haze keeps the hour shootable but never 推薦.
FOG_HAZE_MAX_KM = 5.0

FOG_LEVELS_03 = ("whiteout", "fogged", "hazy", "clear")


def fog_visibility_state(values):
    """CL-PHYS-03 §1: THE raw-hour fog predicate (single source of truth).

    Pure function of the raw `visibility` / `cloud_cover_low` cells; it never
    consults a contract, a viewpoint or a derived LCL. Returns a derived cell
    with value in FOG_LEVELS_03 and state AVAILABLE|UNKNOWN.

    Deliberate "abstain" choice: when the visibility cell is absent the
    predicate cannot see its input, so it returns UNKNOWN and the gate stands
    down (PASS/UNVERIFIED) — a veto that cannot see is not a veto. That is
    NOT a licence to recommend blind: the data-completeness floor below
    refuses 推薦 on an hour with no usable weather input at all.
    """
    vis = _cell_value(values, "visibility")
    if vis is None or vis < 0:
        return {"state": "UNKNOWN", "value": None,
                "reason_code": "VISIBILITY_UNAVAILABLE"}
    low_cloud = _cell_value(values, "cloud_cover_low")
    if vis < FOG_WHITEOUT_KM:
        level = "whiteout"
    elif (vis < FOG_DECK_VISIBILITY_KM and low_cloud is not None
          and low_cloud >= FOG_DECK_LOW_CLOUD_PCT):
        level = "fogged"
    elif vis < FOG_HAZE_MAX_KM:
        level = "hazy"
    else:
        level = "clear"
    return {"state": "AVAILABLE", "value": level, "reason_code": None,
            "visibility_km": round(float(vis), 2),
            "cloud_cover_low_pct": (round(float(low_cloud), 1)
                                    if low_cloud is not None else None)}


def fog_visibility_verdict(condition, values):
    """PASS/FAIL/UNKNOWN for the fog gate: veto bands FAIL, else PASS.

    `hazy` is deliberately NOT a veto — it rides the tier cap in the quality
    pathway (hour stays GUIDANCE_SATISFIED but leaves good_hours), so a
    4 km-haze sunset is still described honestly as 可拍, never as 濃霧.
    """
    cell = fog_visibility_state(values)
    if cell.get("state") != "AVAILABLE":
        return "PASS", "FOG_VISIBILITY_UNVERIFIED"
    level = cell["value"]
    detail = (f"FOG_VISIBILITY({level}, vis={cell['visibility_km']}km,"
              f"low_cloud={cell['cloud_cover_low_pct']}%)")
    return ("FAIL" if level in ("whiteout", "fogged") else "PASS"), detail


def visibility_cap_applies(values):
    """True when the hour is haze-capped below 推薦 (CL-PHYS-03 §1)."""
    cell = fog_visibility_state(values)
    return cell.get("state") == "AVAILABLE" and cell.get("value") == "hazy"


# ---------------------------------------------------------------------------
# CL-PHYS-03 §3 — DATA COMPLETENESS FLOOR.
#
# A card with NO weather data at all (內洞瀑布: only an elevation) and a card
# with visibility 0.2 km (宇老觀景台) both carried ✓ 推薦. A recommendation is
# a claim about an hour; without usable inputs there is nothing to claim.
# Deliberate CLOSED choice (opposite of the fog gate): missing inputs FAIL —
# "no evidence" must never be silently promoted to 推薦. The fog gate abstains
# because it is a veto (a veto that cannot see is not a veto); this gate is a
# production requirement (a recommendation that cannot see is not a
# recommendation), so it closes.
# ---------------------------------------------------------------------------
DATA_FLOOR_METRIC = "data_floor"
# The core weather inputs a recommendation is judged on.
DATA_FLOOR_CORE_FIELDS = ("temperature_2m", "relative_humidity_2m",
                          "cloud_cover_low", "cloud_cover_total",
                          "wind_speed_10m", "precipitation", "visibility")
# Fewer than this many available core cells = no usable weather judgement.
DATA_FLOOR_MIN_CORE = 3
# Visibility floor for a recommendation (independent of the fog veto): a
# sub-2 km hour is never 推薦 under any contract.
DATA_FLOOR_VISIBILITY_KM = 2.0


def data_floor_state(values):
    """CL-PHYS-03 §3: usable-input floor for one hour.

    Levels: "ok" | "no_data" (zero core cells) | "thin" (< MIN_CORE) |
    "visibility_low" (raw visibility under the floor) |
    "visibility_missing" (visibility cell absent).
    """
    values = values or {}
    available = [name for name in DATA_FLOOR_CORE_FIELDS
                 if _cell_value(values, name) is not None]
    if not available:
        return {"state": "AVAILABLE", "value": "no_data",
                "reason_code": "NO_CORE_WEATHER_FIELDS",
                "available_fields": []}
    if len(available) < DATA_FLOOR_MIN_CORE:
        return {"state": "AVAILABLE", "value": "thin",
                "reason_code": "INSUFFICIENT_CORE_WEATHER_FIELDS",
                "available_fields": available}
    vis = _cell_value(values, "visibility")
    if vis is None:
        return {"state": "AVAILABLE", "value": "visibility_missing",
                "reason_code": "VISIBILITY_UNAVAILABLE",
                "available_fields": available}
    if vis < DATA_FLOOR_VISIBILITY_KM:
        return {"state": "AVAILABLE", "value": "visibility_low",
                "reason_code": "VISIBILITY_BELOW_RECOMMEND_FLOOR",
                "available_fields": available, "visibility_km": round(vis, 2)}
    return {"state": "AVAILABLE", "value": "ok", "reason_code": None,
            "available_fields": available}


# ---------------------------------------------------------------------------
# CL-PHYS-03 §4 — SEASON + VENUE OPENING-HOURS POLICY GATES.
#
# Two owner tables live under data/v2/policy/ (NEW files; the pinned
# opportunity records are never edited):
#   subject-seasonal-windows.json  — the subject's own season window
#   venue-hours.json               — the venue's local opening hours
# Both gates are injected ONLY for subjects present in the table. A subject
# with no entry is ABSTAINED on — the gate does not exist for it. That is the
# deliberate "open" choice for unknown venue hours: we never invent a 09:00
# close for a venue whose hours nobody verified, because a fabricated window
# would veto real shoots.
# ---------------------------------------------------------------------------
SEASON_POLICY_METRIC = "season_window_policy"
VENUE_HOURS_METRIC = "venue_hours_policy"
POLICY_DIR = ROOT / "data/v2/policy"


def _load_policy(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def load_subject_season_windows():
    """opportunity_id -> season window entry (MM-DD, wrap-aware)."""
    doc = _load_policy(POLICY_DIR / "subject-seasonal-windows.json")
    windows = doc.get("windows") if isinstance(doc, dict) else None
    return windows if isinstance(windows, dict) else {}


def load_venue_hours():
    """opportunity_id -> venue hours entry ({open, close} local HH:MM)."""
    doc = _load_policy(POLICY_DIR / "venue-hours.json")
    venues = doc.get("venues") if isinstance(doc, dict) else None
    return venues if isinstance(venues, dict) else {}


def season_policy_verdict(entry, local_date):
    """PASS inside the subject's own season window, FAIL outside, else UNKNOWN.

    Window endpoints are inclusive MM-DD pairs in the subject's LOCAL calendar
    and wrap across New Year (start > end), matching the CL-COND-A8 rule.
    """
    if local_date is None:
        return "UNKNOWN", "LOCAL_DATE_UNAVAILABLE"
    if not isinstance(entry, dict):
        return "UNKNOWN", "SEASON_POLICY_UNAVAILABLE"
    window = {"start": entry.get("start"), "end": entry.get("end")}
    if not (isinstance(window["start"], str) and isinstance(window["end"], str)
            and len(window["start"]) == 5 and len(window["end"]) == 5):
        return "UNKNOWN", "SEASON_POLICY_MALFORMED"
    md = local_date.isoformat()[5:]
    inside = _mmdd_inside(md, window)
    return (("PASS", f"SEASON_WINDOW_OPEN({window['start']}~{window['end']})")
            if inside else
            ("FAIL", f"SEASON_WINDOW_CLOSED({md} outside "
                     f"{window['start']}~{window['end']})"))


def venue_hours_verdict(entry, local_start_min):
    """PASS when the hour bucket starts inside [open, close); FAIL outside.

    Unknown hours abstain at gate-injection time (no entry -> no gate), never
    here. A malformed entry (missing token, overnight close <= open) is
    UNKNOWN — an unreadable window must not veto a shoot.
    """
    if local_start_min is None:
        return "UNKNOWN", "LOCAL_TIME_UNAVAILABLE"
    if not isinstance(entry, dict):
        return "UNKNOWN", "VENUE_HOURS_UNAVAILABLE"

    def _minutes(token):
        if not isinstance(token, str) or ":" not in token:
            return None
        hh, mm = token.split(":", 1)
        try:
            return int(hh) * 60 + int(mm)
        except ValueError:
            return None

    open_min = _minutes(entry.get("open"))
    close_min = _minutes(entry.get("close"))
    if open_min is None or close_min is None:
        return "UNKNOWN", "VENUE_HOURS_MALFORMED"
    if not (0 <= open_min < close_min <= 1440):
        return "UNKNOWN", "VENUE_HOURS_MALFORMED"
    ok = open_min <= local_start_min < close_min
    return (("PASS", f"VENUE_OPEN({entry['open']}-{entry['close']})")
            if ok else
            ("FAIL", f"VENUE_CLOSED({entry['open']}-{entry['close']})"))


# CL-PHYS-03 gate metrics join the single phys-gate implementation so
# condition_verdict/condition_value route them through one predicate each.
PHYS_GATE_METRICS = PHYS_GATE_METRICS + (FOG_VISIBILITY_METRIC, DATA_FLOOR_METRIC,
                                         SEASON_POLICY_METRIC, VENUE_HOURS_METRIC)

FOG_VISIBILITY_GATE = _phys_gate(
    "EVALGATE-fog-visibility", FOG_VISIBILITY_METRIC, {
        "zh-TW": "CL-PHYS-03 評估層能見度硬擋（全題材，專拍霧的 misty_forest 除外）："
                 "原始能見度 <2 km 即濃霧、不得推薦；能見度 <10 km 且低雲 ≥90% "
                 "視為白牆（雲幕貼地）。能見度 <5 km 時時段降級為可拍、不得為推薦。"
                 "此閘門對每個題材注入，不寫入業主契約。",
        "en": "CL-PHYS-03 evaluation-layer visibility gate (all subjects except the "
              "dedicated fog genre misty_forest): raw visibility < 2 km is 濃霧 and "
              "can never be recommended; visibility < 10 km with low cloud >= 90% "
              "is a white wall (deck at ground level); visibility < 5 km caps the "
              "hour below recommend (shootable haze). Injected for every "
              "opportunity, never written into the owner contract.",
        "ja": "CL-PHYS-03 評価層の視程ゲート（霧専門の misty_forest を除く全題材）："
              "生の視程<2kmは濃霧で推奨不可、視程<10kmかつ低雲≥90%は白壁、視程<5kmは"
              "推奨未満に上限。契約には書き込まない。",
    })
DATA_FLOOR_GATE = _phys_gate(
    "EVALGATE-data-floor", DATA_FLOOR_METRIC, {
        "zh-TW": "CL-PHYS-03 資料底線：一小時若沒有可用天氣輸入（核心欄位少於 3 項）、"
                 "或缺能見度、或能見度 <2 km，一律不得成為 ✓ 推薦（顯示資料不足）。"
                 "刻意選擇關閉（fail closed）：推薦是對該小時的斷言，沒有輸入就沒有斷言。",
        "en": "CL-PHYS-03 data floor: an hour with no usable weather input (fewer "
              "than 3 core fields), no visibility cell, or visibility < 2 km is "
              "never ✓ recommend. Deliberate CLOSED choice: a recommendation is a "
              "claim about the hour, and a claim without inputs is not a claim.",
        "ja": "CL-PHYS-03 データ下限：中核項目3未満・視程欠測・視程<2kmの時間は推奨不可。",
    })


def policy_gates_for(opportunity_id, season_windows, venue_hours):
    """CL-PHYS-03 §4: inject the season / venue gates the owner tables cover.

    A subject absent from a table gets no gate at all (abstain) — an unknown
    venue window is never invented, and a subject whose season nobody recorded
    keeps its contract semantics unchanged.
    """
    gates = []
    season = (season_windows or {}).get(opportunity_id)
    if isinstance(season, dict) and season.get("start") and season.get("end"):
        gate = _phys_gate("EVALGATE-season-window", SEASON_POLICY_METRIC, {
            "zh-TW": ("CL-PHYS-03 季窗閘門：本題材自身季節窗為 "
                      f"{season['start']}~{season['end']}，窗外時段一律不得推薦。"),
            "en": ("CL-PHYS-03 season gate: this subject's own window is "
                   f"{season['start']}~{season['end']}; hours outside it are "
                   "never recommended."),
            "ja": ("CL-PHYS-03 季節ゲート：本題材の窓は "
                   f"{season['start']}~{season['end']}、窓外は推奨しない。"),
        })
        gate["policy_entry"] = dict(season)
        gates.append(gate)
    venue = (venue_hours or {}).get(opportunity_id)
    if isinstance(venue, dict) and venue.get("open") and venue.get("close"):
        gate = _phys_gate("EVALGATE-venue-hours", VENUE_HOURS_METRIC, {
            "zh-TW": (f"CL-PHYS-03 開放時間閘門：場地開放 {venue['open']}–"
                      f"{venue['close']}（當地時間），時段起點不在開放區間內一律"
                      "不得推薦。未登錄開放時間的場地不注入此閘門（不臆測）。"),
            "en": (f"CL-PHYS-03 venue-hours gate: the venue opens {venue['open']}–"
                   f"{venue['close']} local; an hour bucket starting outside that "
                   "window is never recommended. Venues with no verified hours "
                   "get no gate at all (never invented)."),
            "ja": (f"CL-PHYS-03 開館時間ゲート：{venue['open']}–{venue['close']}"
                   "（現地時間）の外は推奨しない。未登録の施設には適用しない。"),
        })
        gate["policy_entry"] = dict(venue)
        gates.append(gate)
    return gates


# CL-PHYS-03 §5 — NIGHT WINDOWS (data half only; the display collapse is
# CL-UI-45 and lives outside this package).
#
# Night subjects were being flattened into one generic 非建議 bucket, so the
# 00:00–04:00 deep-night window (Milky Way / deep sky), the 18:00 blue-hour
# window and the 22:00–23:00 city-night window carried no reason code of their
# own. The data side now names the window each night hour legitimately sits in
# so the UI can label it instead of collapsing it. Presentation is NOT changed
# here (assets/** is out of scope).
NIGHT_WINDOW_GENRES = frozenset({
    "night_sky", "city_night", "blue_hour_city", "moonlit_scene",
    "star_trails", "blue_tears", "firefly", "snow_ice_night",
})
NIGHT_DEEP_HOURS = (0, 1, 2, 3)        # 00:00–04:00 deep night / Milky Way
NIGHT_EVENING_HOURS = (18, 19, 20, 21)  # 18:00 blue hour → evening city night
NIGHT_CITY_HOURS = (22, 23)             # 22:00–23:00 city night


def night_window_code(genre, local_hour, astro_row):
    """CL-PHYS-03 §5: reason code for a night subject's hour, or None.

    Order matters and is deliberate:
      1. blue_hour_window (sun -8..-4 deg) wins — it is the 18:00 window and
         it is a narrow, physically defined band;
      2. 00:00–03:59  -> NIGHT_DEEP_WINDOW     (Milky Way / deep night);
      3. 22:00–23:59  -> NIGHT_CITY_WINDOW     (city night, artificial light);
      4. 18:00–21:59  -> NIGHT_EVENING_WINDOW  (after blue hour, before 22:00);
      daylight hours return None — a night subject has no night window there.
    """
    if genre not in NIGHT_WINDOW_GENRES:
        return None
    if isinstance(astro_row, dict) and astro_row.get("blue_hour_window"):
        return "NIGHT_BLUE_HOUR_WINDOW"
    if not isinstance(local_hour, int):
        return None
    if local_hour in NIGHT_DEEP_HOURS:
        return "NIGHT_DEEP_WINDOW"
    if local_hour in NIGHT_CITY_HOURS:
        return "NIGHT_CITY_WINDOW"
    if local_hour in NIGHT_EVENING_HOURS:
        return "NIGHT_EVENING_WINDOW"
    return None


def night_window_reason(code):
    """Trilingual label for one night-window reason code."""
    return {
        "NIGHT_DEEP_WINDOW": {
            "zh-TW": "深夜窗（00:00–04:00，銀河／深空）",
            "en": "Deep-night window (00:00–04:00, Milky Way / deep sky)",
            "ja": "深夜窓（00:00–04:00、天の川／深宇宙）"},
        "NIGHT_BLUE_HOUR_WINDOW": {
            "zh-TW": "藍調窗（日落後藍調時刻）",
            "en": "Blue-hour window (after sunset)",
            "ja": "ブルーアワー窓（日没後）"},
        "NIGHT_CITY_WINDOW": {
            "zh-TW": "夜景窗（22:00–23:00，城市燈火）",
            "en": "City-night window (22:00–23:00, city lights)",
            "ja": "夜景窓（22:00–23:00、都市の灯）"},
        "NIGHT_EVENING_WINDOW": {
            "zh-TW": "夜間窗（18:00–22:00）",
            "en": "Evening window (18:00–22:00)",
            "ja": "夜間窓（18:00–22:00）"},
    }.get(code)


# CL-DATA-74 — snow_scene family: derived ground-state enum per hour from the
# Open-Meteo snow fields. The ticket semantics (snowfall > 0 OR snow_depth > 0)
# is collapsed into one displayable level so the flat-AND contract list never
# demands both at once:
#   snowing      降雪中: snowfall > 0 cm/h (falling snow, ground may be bare)
#   snow_covered 積雪: snow_depth_cm > 0 while not snowing (lying snow)
#   none         無雪: neither field shows snow
# Fail-closed: BOTH snow cells missing -> UNKNOWN cell (never fabricated "no
# snow"); one available cell is enough to certify the "none"/"snowing" states
# it can speak for (depth-only rows can never claim "snowing", and vice versa).
def snow_cover_levels(hours):
    levels = []
    for hour_row in hours:
        values = hour_row.get("values") or {}

        def _cell(name, _values=values):
            cell = _values.get(name)
            if (isinstance(cell, dict) and cell.get("state") == "AVAILABLE"
                    and isinstance(cell.get("value"), (int, float))
                    and not isinstance(cell.get("value"), bool)):
                return float(cell["value"])
            return None

        snowfall = _cell("snowfall")
        depth = _cell("snow_depth_cm")
        if snowfall is None and depth is None:
            levels.append({"state": "UNKNOWN", "value": None})
            continue
        if snowfall is not None and snowfall > 0.0:
            level = "snowing"
        elif depth is not None and depth > 0.0:
            level = "snow_covered"
        else:
            level = "none"
        levels.append({"state": "AVAILABLE", "value": level})
    return levels


# CL-DATA-74 — star_trails family: continuous-clear-window probe (the
# CHALLENGER-15 streak semantics). A star-trail stack is one multi-hour
# exposure; a cloud band crossing mid-stack ruins it, so the veto is
# CONTINUITY, not the single-hour cloud mean. The runner computes, for every
# hour, the length of the clear streak ENDING at that hour (the hour itself
# plus directly preceding consecutive hours with cloud_cover_total <=
# STARTRAIL_STREAK_CLOUD_MAX). Missing/invalid cloud cells break the streak
# honestly: the hour's value is None (UNKNOWN cell) and the streak restarts at
# the next certified-clear hour — a gap can never be counted as clear time.
STARTRAIL_STREAK_CLOUD_MAX = 20.0


def clear_streak_levels(hours):
    levels = []
    streak = 0.0
    for hour_row in hours:
        values = hour_row.get("values") or {}

        def _cell(name, _values=values):
            cell = _values.get(name)
            if (isinstance(cell, dict) and cell.get("state") == "AVAILABLE"
                    and isinstance(cell.get("value"), (int, float))
                    and not isinstance(cell.get("value"), bool)):
                return float(cell["value"])
            return None

        cloud = _cell("cloud_cover_total")
        if cloud is not None:
            clear = cloud <= STARTRAIL_STREAK_CLOUD_MAX
            streak = streak + 1.0 if clear else 0.0
            levels.append({"state": "AVAILABLE", "value": streak})
        else:
            streak = 0.0
            levels.append({"state": "UNKNOWN", "value": None})
    return levels


def conditions_day_rows(condition_by_id, counts_by_cid, total):
    """Per-condition day verdict rows from the condition's OWN hourly verdicts.

    CL-DATA-56: `counts_by_cid` tallies each condition's raw PASS/FAIL/UNKNOWN
    state per hour bucket (recorded before any role gating). Counting
    pass_hours from the role-gated hour_status lists instead made QUALITY/
    BONUS conditions — e.g. golden_hour_window — read PASS with
    pass_hours == total (24) even when their own verdicts failed all day,
    which is physically impossible for a solar window (~2 h/day at
    mid-latitudes).
    """
    rows = []
    for cid, cond in condition_by_id.items():
        tally = counts_by_cid.get(cid, {"PASS": 0, "FAIL": 0, "UNKNOWN": 0})
        unknowns = tally["UNKNOWN"]
        fails = tally["FAIL"]
        pass_n = total - fails - unknowns
        if unknowns == total:
            verdict = "UNKNOWN"
        elif pass_n == total:
            verdict = "PASS"
        elif fails == total:
            verdict = "FAIL"
        else:
            verdict = "PARTIAL"
        rows.append({
            "id": cid, "metric": cond["metric"],
            "tier": cond.get("condition_tier") or "MAIN",
            "role": cond.get("role"),
            "day_verdict": verdict,
            "pass_hours": pass_n,
        })
    return rows


def detail_hour_rows(hour_row, local_stamp, status, conditions_eval,
                     astro_row, states, precise_local, precise_off,
                     local_date=None, local_start_min=None, night_code=None):
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
         "value": condition_value(c, hour_row["values"], astro_row,
                                  local_date=local_date,
                                  local_start_min=local_start_min),
         "verdict": states[c["id"]]}
        for c in conditions_eval]
    # CL-PHYS-03 §5: name the night window the hour legitimately sits in so a
    # night subject is not flattened into a generic 非建議. Additive and only
    # for night genres; the published bundle schema is untouched (details are
    # not schema-gated).
    night = ({"night_window": {"code": night_code,
                               "reason": night_window_reason(night_code)}}
             if night_code else {})
    rows = [{
        "utc": hour_row["valid_at_utc"],
        "local": local_stamp.strftime("%H:%M"),
        "status": status,
        **night,
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
            **night,
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
        if doc.get("lifecycle_status") == "retired":
            # CL-DATA-62: retired product never evaluates.
            continue
        opportunities.append(doc)
    return opportunities


def load_opportunity_docs():
    """All opportunity docs regardless of template ladder (CL-UI-41).

    CL-DATA-62: docs whose product is retired (lifecycle_status == "retired")
    are excluded from evaluation entirely; the bundle records them as
    PRODUCT_RETIRED skips instead of evaluating retired Places.
    """
    docs = []
    for path in sorted((ROOT / "data/v2/opportunities").glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("lifecycle_status") == "retired":
            continue
        docs.append(doc)
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


def v1_place_elevations():
    """CL-DATA-71: viewpoint elevations from the V1 spot catalog DEM.

    The V1 weather snapshots record each spot's curated ``elevation`` when
    verified and the Open-Meteo grid DEM elevation (``api_elevation``,
    Copernicus DEM) of the coordinate always; the spot catalog is the DEM
    source of record for viewpoint-relative thresholds. Curated elevation
    wins, DEM fallback otherwise; spots absent from the snapshots resolve
    to None (the verdict then propagates UNKNOWN honestly).
    """
    elevations = {}
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
            elevation = spot.get("elevation")
            if elevation is None:
                elevation = spot.get("api_elevation")
            if (spot_id and isinstance(elevation, (int, float))
                    and not isinstance(elevation, bool) and elevation > 0):
                elevations.setdefault(spot_id, float(elevation))
    return elevations


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
    # CL-DATA-80: --legacy-engine is the escape hatch back to the pre-v2
    # boolean path (GUIDANCE_SATISFIED/UNFAVORABLE with no quality score).
    # Default is the QUALITY engine (Gatekeeper -> S_quality -> tier).
    parser.add_argument("--legacy-engine", action="store_true",
                        help="evaluate with the legacy boolean path only "
                             "(no S_quality/tier_v2/s_rank fields)")
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
    # CL-DATA-71: catalog DEM elevations for viewpoint-relative conditions.
    place_elevations = v1_place_elevations()
    # CL-DATA-72 batch A / CL-COND-A8: seasonal-calendar windows for the
    # seasonal_state bridge.
    seasonal_by_spot = load_seasonal_calendar()
    # CL-PHYS-03 §4: owner policy tables (season window + venue opening hours).
    # Missing tables degrade to {} — no gate exists for a subject nobody has
    # recorded hours/windows for (abstain, never invented).
    season_windows = load_subject_season_windows()
    venue_hours = load_venue_hours()
    # CL-DATA-80: place AGLI for S_rank = AGLI^0.35 * S_quality^0.65. The dual
    # board (AGLI-L landscape + AGLI-P photography) is averaged into the single
    # AGLI the engine spec formula uses; places with no AGLI (scoring paused)
    # carry s_rank = null honestly, never a fabricated score.
    agli_by_place = {}
    _agli_path = ROOT / "data/v2/audits/agli/agli-final.json"
    if _agli_path.exists():
        for p in (json.loads(_agli_path.read_text(encoding="utf-8"))
                  .get("places") or []):
            l, pp = p.get("agli_l"), p.get("agli_p")
            if isinstance(l, (int, float)) and isinstance(pp, (int, float)):
                agli_by_place[p["place_id"]] = round((float(l) + float(pp)) / 2.0, 1)

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
    # CL-DATA-62: retired Places leave the evaluation product; the skip list
    # records them honestly instead of evaluating or mislabeling them.
    retired_place_ids = set()
    for path in sorted((ROOT / "data/v2/opportunities").glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        if doc.get("lifecycle_status") == "retired":
            retired_place_ids.add(doc["place_id"])
    for pid in sorted(retired_place_ids - evaluated_place_ids - skipped_place_ids):
        skipped.append({"place_id": pid, "reason": "PRODUCT_RETIRED"})
        skipped_place_ids.add(pid)
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
            # CL-PHYS-GUARD: with no resolved offset the sunrise/sunset
            # guards must NOT be run on a fake UTC clock (that would block
            # every real window east of Greenwich). Pass None so the engine
            # falls back to the longitude's mean-solar offset instead.
            guard_offset_seconds = None
        else:
            tz_display = {"iana": zone, "utc_offset_hours": offset,
                          "status": "DISPLAY_APPROXIMATION"}
            local_offset = offset
            # CL-PHYS-GUARD: the SAME offset that labels the hour rows feeds
            # the hard local-clock guard on sunrise_time_window/sunset_window
            # — label and verdict can never disagree about the spot's clock.
            guard_offset_seconds = offset * 3600
        need_moon = any("moon" in c["metric"] or "galactic" in c["metric"]
                        or "spring_tide" in c["metric"]
                        for doc in group["opportunities"]
                        for c in doc["condition_contract"]["conditions"])
        hours = artifact["hours"]
        # CL-PHYS-02 §1 (datum): every hour of this coordinate group carries
        # the grid cell's ground elevation (m ASL), so an AGL LCL can be
        # converted to the ASL datum exactly where it is compared with a
        # viewpoint elevation. A missing provider elevation stays an
        # UNAVAILABLE cell (fail-closed downstream), never a 0 m default.
        grid_elevation = (artifact.get("grid") or {}).get("elevation_m")
        grid_cell = ({"value": float(grid_elevation), "unit": "m",
                      "state": "AVAILABLE", "reason_code": None}
                     if isinstance(grid_elevation, (int, float))
                     and not isinstance(grid_elevation, bool)
                     else {"value": None, "unit": "m", "state": "UNAVAILABLE",
                           "reason_code": "GRID_ELEVATION_UNKNOWN"})
        for hour_row in hours:
            hour_row["values"]["grid_elevation_m"] = dict(grid_cell)
        # CL-DATA-72 batch A / CL-COND-A7: derive the per-hour
        # water_reflection_state proxy once per coordinate group and attach it
        # to the shared hour rows (idempotent — every reflection opportunity of
        # the group reads the same cells).
        reflection_levels = water_reflection_levels(hours)
        for hour_row, level in zip(hours, reflection_levels):
            hour_row["values"]["water_reflection_state"] = level
        # CL-DATA-73: derive the per-hour fog_state proxy once per coordinate
        # group and attach it to the shared hour rows (idempotent — every
        # misty-forest opportunity of the group reads the same cells).
        fog_levels = fog_states(hours)
        for hour_row, fstate in zip(hours, fog_levels):
            hour_row["values"]["fog_state"] = fstate

        # CL-DATA-74: derive the snow_scene ground-state and the star_trails
        # continuous-clear streak once per coordinate group and attach them to
        # the shared hour rows (idempotent — every snow/trail opportunity of
        # the group reads the same cells).
        snow_levels = snow_cover_levels(hours)
        for hour_row, level in zip(hours, snow_levels):
            hour_row["values"]["snow_cover_state"] = level
        streak_levels = clear_streak_levels(hours)
        for hour_row, streak in zip(hours, streak_levels):
            hour_row["values"]["clear_streak_hours"] = streak
        # CL-DATA-77: derive the river_flow_state for the waterfall family
        # once per coordinate group — one trailing-72h-precipitation fetch,
        # fail-closed to UNKNOWN cells when the past-window fetch fails.
        needs_flow = any(c["metric"] == "river_flow_state"
                         for doc in group["opportunities"]
                         for c in doc["condition_contract"]["conditions"])
        if needs_flow:
            try:
                trailing_past, _t_url, _t_sha = adapter.fetch_trailing_precipitation(
                    lat, lon, RIVER_FLOW_TRAILING_HOURS)
            except adapter.FetchFailure:
                trailing_past = None
            flow_levels = river_flow_levels(hours, trailing_past)
            for hour_row, flow in zip(hours, flow_levels):
                hour_row["values"]["river_flow_state"] = flow
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
                if _cond.get("metric") in ("light_direction",
                                           "moon_target_separation_deg"):
                    _cond["view_azimuth_deg"] = view_az_deg
            # CL-DATA-71: bind the viewpoint elevation onto every
            # cloud_base_height condition — camera_context altitude_m when
            # web-verified, else the V1 spot-catalog DEM elevation. Nothing
            # binds when neither source has the place: the verdict then
            # propagates UNKNOWN (VIEWPOINT_ELEVATION_UNKNOWN).
            camera_alt = next(
                (c.get("altitude_m") for c in doc.get("camera_contexts", [])
                 if isinstance(c.get("altitude_m"), (int, float))
                 and not isinstance(c.get("altitude_m"), bool)), None)
            if camera_alt is None:
                camera_alt = place_elevations.get(doc["place_id"])
            for _cond in conditions_eval:
                if _cond.get("metric") in ("cloud_base_height",
                                           "lcl_height_m_agl"):
                    _cond["viewpoint_elevation_m"] = camera_alt
            # CL-PHYS-02 §4: on the ASL datum a single summit grid point
            # cannot resolve a deck BELOW the summit, so the cloud-sea
            # cloud-base window becomes advisory and the RH-inversion gate
            # is the primary criterion (valley dual-grid → CL-DATA-85).
            conditions_eval = demote_cloud_sea_lcl(conditions_eval, contract)
            # CL-PHYS-02 §4b: outside cloud_sea the same DEM−200 window is
            # REQUIRED and equally unresolvable wherever the viewpoint sits on
            # its own grid cell (nine subjects were pinned at 不宜 forever) —
            # demote it to QUALITY so the resolvable part of the subject can
            # still produce a verdict.
            conditions_eval = demote_unresolvable_cloud_base(
                conditions_eval, contract, camera_alt)
            # CL-PHYS-02 §2/§3: the evaluation-layer gates (In-Cloud Fog hard
            # block, data-contradiction downgrade, cloud-sea inversion) join
            # the condition set for this opportunity. They are NEVER written
            # into the owner contract — contract_sha256 stays over it.
            conditions_eval = conditions_eval + phys_gates_for(
                contract, camera_alt)
            # CL-PHYS-03 §4: season-window and venue-hours policy gates join
            # the condition set ONLY for subjects the owner tables cover.
            conditions_eval = conditions_eval + policy_gates_for(
                oid, season_windows, venue_hours)
            # CL-DATA-72 batch A / CL-COND-A8: bind the opportunity's
            # seasonal-calendar entries onto every seasonal_state condition
            # (same binding pattern as light_direction/cloud_base_height).
            # CL-COND-A4: resolve the moon alternation (anchor + dependents)
            # once per contract.
            for _cond in conditions_eval:
                if _cond.get("metric") == "seasonal_state":
                    _cond["seasonal_entries"] = seasonal_by_spot.get(oid) or []
            alternation = moon_alternation(conditions_eval)
            # CL-DATA-80: engine selection is PER CONTRACT — migrated contracts
            # run the QUALITY engine unless --legacy-engine; an unmigrated
            # contract (defensive) silently keeps the legacy boolean path.
            engine_v2 = (not arguments.legacy_engine
                         and isinstance(contract.get("conditions_v2"), dict))
            best_s_quality = None
            days = {}
            # CL-DATA-56: per-condition verdict counts, keyed by local day.
            # The published hours rows carry only the ROLE-GATED failed/
            # unknown lists from hour_status (REQUIRED failures, REQUIRED/
            # BLOCKER unknowns) — those lists drive the hour gate, not the
            # per-condition day verdict. Counting every condition's day
            # pass_hours from them made QUALITY/BONUS conditions (e.g.
            # golden_hour_window) read PASS with pass_hours == total even
            # when their own per-hour verdicts were FAIL all day.
            day_verdict_counts = {}
            hour_ctxs = []
            for hour_row in hours:
                at = datetime.fromisoformat(hour_row["valid_at_utc"].replace("Z", "+00:00"))
                astro_row = hour_observations(at, lat, lon, events=events,
                                              need_moon=need_moon,
                                              utc_offset_seconds=guard_offset_seconds)
                states = {}
                roles = {}
                local_bucket_start = at + timedelta(hours=local_offset)
                local_start_min = (local_bucket_start.hour * 60
                                   + local_bucket_start.minute)
                local_date = local_bucket_start.date()
                for condition in conditions_eval:
                    states[condition["id"]] = condition_verdict(
                        condition, hour_row["values"], astro_row,
                        month=at.month,
                        local_start_min=local_start_min,
                        local_date=local_date)[0]
                    roles[condition["id"]] = condition.get("role")
                # CL-COND-A4: apply the M2/M3/M5 moon alternation BEFORE the
                # role gate — a met anchor stands the dependents down, a failed
                # anchor hands the gate to them.
                apply_moon_alternation(states, alternation)
                status, fails, unknowns = hour_status(roles, states)
                local_stamp = at + timedelta(hours=local_offset)
                # CL-PHYS-03 §1: a haze-capped hour (visibility < 5 km, not a
                # white-out) stays GUIDANCE_SATISFIED — it is still shootable —
                # but it leaves good_hours and its QUALITY tier is capped below
                # 推薦, so no ✓ 推薦 can ever be built out of it.
                capped = (status == "GUIDANCE_SATISFIED"
                          and visibility_cap_applies(hour_row["values"]))
                day_key = local_stamp.date().isoformat()
                entry = days.setdefault(day_key, {"local_date": day_key, "hours": [],
                                                  "capped": set()})
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
                # CL-UI-70 (CHALLENGER-13 P7, edge-bucket policy confirmed):
                # the precise sub-hour stamp is computed ONLY for
                # GUIDANCE_SATISFIED buckets. On an UNFAVORABLE day a window
                # metric can still pass one bucket (its day condition
                # pass_hours counts bucket-level passes), but no precise
                # stamp is emitted — good_hours stays empty for that day, so
                # a blue-hour day that failed on weather shows the bucket
                # label (17:00) in the hourly grid without the 17:25 precise
                # stamp its qualifying neighbours carry. That asymmetry is
                # the documented edge-bucket behaviour, not a bug; the
                # subject-cards layer never fabricates a hint from it.
                precise_local = None
                precise_off = None
                if status == "GUIDANCE_SATISFIED" and not capped:
                    window_metrics = [c["metric"] for c in conditions_eval
                                      if c["metric"] in TIME_WINDOW_METRICS]
                    if window_metrics:
                        profiles = window_pass_profiles(at, lat, lon,
                                                        events=events,
                                                        utc_offset_seconds=guard_offset_seconds)
                        for i, off in enumerate(WINDOW_SAMPLE_OFFSETS):
                            if all(profiles[m][i] for m in window_metrics):
                                precise_off = off
                                precise_local = (local_stamp
                                                 + timedelta(minutes=off)
                                                 ).strftime("%H:%M")
                                break
                qe = None
                if engine_v2:
                    qe = quality_engine.evaluate_hour(
                        contract.get("conditions_v2"), states,
                        hour_row["values"], astro_row,
                        status == "GUIDANCE_SATISFIED")
                    # CL-PHYS-03 §1 cap: haze never reaches 推薦; the honest
                    # S_quality is kept, only the tier ceiling moves. (Read via
                    # .get so the engine stays an ANNOTATION input — see
                    # CL-DATA-79 engine-bypass: verdicts never read the engine.)
                    engine_tier = qe.get("tier") if qe else None
                    if capped and engine_tier == "recommend":
                        qe = dict(qe, tier="good")
                    if (qe["eligible"] and not capped
                            and (best_s_quality is None
                                 or qe["s_quality"] > best_s_quality)):
                        best_s_quality = qe["s_quality"]
                if capped:
                    entry["capped"].add(local_stamp.strftime("%H:%M"))
                entry["hours"].append({
                    "utc": hour_row["valid_at_utc"],
                    "local": local_stamp.strftime("%H:%M"),
                    "local_precise": precise_local,
                    "status": status,
                    "failed": fails,
                    "unknown": unknowns,
                    # CL-DATA-80: eligible hours only — ineligible hours carry
                    # no score fields (G=0 -> S_quality=0 by spec §4, tier ✗).
                    **({"s_quality": qe["s_quality"], "tier_v2": qe["tier"]}
                       if qe and qe["eligible"] else {}),
                })
                for cid, state in states.items():
                    day_verdict_counts.setdefault(day_key, {}).setdefault(
                        cid, {"PASS": 0, "FAIL": 0, "UNKNOWN": 0})[state] += 1
                hour_ctxs.append((at, hour_row, astro_row, states, status, capped))
                for row in detail_hour_rows(
                        hour_row, local_stamp, status, conditions_eval,
                        astro_row, states, precise_local, precise_off,
                        local_date=local_date,
                        local_start_min=local_start_min,
                        night_code=night_window_code(
                            contract.get("genre_template"),
                            local_stamp.hour, astro_row)):
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
                conditions_day = conditions_day_rows(
                    condition_by_id, day_verdict_counts.get(day_key, {}),
                    len(hours_out))
                capped_hours = days[day_key].get("capped") or set()

                def _recommendable(h):
                    """GUIDANCE_SATISFIED and not haze-capped (CL-PHYS-03 §1)."""
                    return (h["status"] == "GUIDANCE_SATISFIED"
                            and h["local"] not in capped_hours)

                day_out.append({
                    "local_date": day_key,
                    "state": state,
                    # CL-DATA-31: good_hours carry the EARLIEST passing
                    # sub-hour instant (local_precise) when one was computed —
                    # never a bucket-start stamp earlier than the light window.
                    "good_hours": [h.get("local_precise") or h["local"]
                                   for h in hours_out
                                   if _recommendable(h)],
                    # CL-DATA-80: per-hour QUALITY-engine scores for the same
                    # eligible buckets (additive; legacy consumers read
                    # good_hours unchanged).
                    **({"good_hours_v2": [
                        {"local": h.get("local_precise") or h["local"],
                         "s_quality": h["s_quality"], "tier_v2": h["tier_v2"]}
                        for h in hours_out
                        if _recommendable(h)
                        and "s_quality" in h]}
                       if engine_v2 else {}),
                    "hour_counts": counts,
                    "conditions": conditions_day,
                })
            def _snapshot(ctx):
                if ctx is None:
                    return None
                snap_at, snap_row, snap_astro, snap_states, snap_status, *_rest = ctx
                snap_local_date = (snap_at + timedelta(hours=local_offset)).date()
                snap_local_start = ((snap_at + timedelta(hours=local_offset)).hour * 60)
                return {
                    "utc": snap_row["valid_at_utc"],
                    "local": (snap_at + timedelta(hours=local_offset)).strftime("%Y-%m-%d %H:%M"),
                    "status": snap_status,
                    "conditions": [
                        {"id": c["id"], "metric": c["metric"],
                         "tier": c.get("condition_tier") or "MAIN", "role": c.get("role"),
                         "operator": c.get("operator") or "none",
                         "threshold": c.get("threshold"),
                         "value": condition_value(c, snap_row["values"], snap_astro,
                                                  local_date=snap_local_date,
                                                  local_start_min=snap_local_start),
                         "verdict": snap_states[c["id"]]}
                        for c in conditions_eval],
                }

            now_ctx = next((c for c in hour_ctxs if c[0] >= generated_at), None)
            # CL-PHYS-03 §1: the next recommendable hour is never a haze-capped
            # hour (it stays shootable, it is not 推薦).
            good_ctx = next((c for c in hour_ctxs
                             if c[4] == "GUIDANCE_SATISFIED"
                             and not (len(c) > 5 and c[5])), None)
            live = {"now": _snapshot(now_ctx), "next_good": _snapshot(good_ctx)}
            place_out["opportunities"].append({
                "opportunity_id": oid,
                "name_i18n": doc.get("name_i18n") or {},
                "genre_template": contract.get("genre_template"),
                "condition_contract_id": contract.get("contract_id"),
                "condition_contract_sha256": contract_sha,
                # CL-DATA-80: which evaluation engine produced this record.
                "engine": ("legacy_boolean" if not engine_v2
                           else "quality_engine_v2"),
                # S_rank = AGLI^0.35 * S_quality_best^0.65 (spec §4) over the
                # eligible hours of the 168h window; null when the place has no
                # AGLI (scoring paused) or no eligible hour.
                "s_rank": ({
                    "agli": agli_by_place.get(doc["place_id"]),
                    "s_quality_best": best_s_quality,
                    "value": quality_engine.s_rank(
                        agli_by_place.get(doc["place_id"]), best_s_quality),
                } if engine_v2 and best_s_quality is not None else None),
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

    # CL-CI-36: a place_id spanning several coordinate groups (CL-UI-25) must
    # appear ONCE in the published places list — the CL-UI-25 fix merged the
    # detail docs but left places_out with one entry per group, so the bundle
    # carried duplicate place rows (tw-002/us-005/us-011/us-013 each twice in
    # the 2026-11-12 cron bundle) and place_count overstated the product.
    # Merge by place_id: keep the first group's coordinate/provenance and
    # append later groups' opportunities (detail side already records the
    # per-opportunity coordinate in evaluations-details).
    merged_places = {}
    place_order = []
    for place_out in places_out:
        pid = place_out["place_id"]
        if pid in merged_places:
            merged_places[pid]["opportunities"].extend(place_out["opportunities"])
        else:
            merged_places[pid] = place_out
            place_order.append(pid)
    places_out = [merged_places[pid] for pid in place_order]

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
                     "未經實拍校準，永不構成 FAVORABLE 保證。花季窗口由 seasonal-calendar"
                     ".json 例年窗/今年實況窗計算（owner 維護）；倒影題材水面狀態由風速/降水/"
                     "氣溫派生三級（鏡面/可拍/不宜），瀑布題材水量由過去 72h 累積雨量派生三級（枯水/平水/豐水，provisional 映射），潮汐決定型岸邊景點（天空之鏡類）誠實降級"
                     "為不可評估、拍攝前請自行查潮汐表。鳴門漩渦題材的大潮帶由朔望天文代理判定，精確潮流時刻請查官方潮見表。天氣為網格預報，不代表拍攝點實況。",
            "en": "Results are GUIDANCE only: thresholds are provisional/approved "
                  "genre-template values, not calibrated against real shoots, and never "
                  "constitute a FAVORABLE guarantee. Seasonal windows are computed from "
                  "seasonal-calendar.json (owner-maintained typical/current-season "
                  "windows); the reflection water-surface state is a derived three-level "
                  "proxy (mirror/shootable/unfit) from wind, precipitation and air "
                  "temperature, and tide-decided shoreline subjects degrade honestly to "
                  "not-evaluatable — check the tide table yourself before shooting. "
                  "Waterfall flow state is a derived three-level proxy (low/mid/high) "
                  "from the trailing 72h accumulated precipitation, and the Naruto "
                  "whirlpool spring-tide band is judged from the syzygy astronomy proxy "
                  "(exact current hours: official tide table). "
                  "Weather is grid forecast data, not on-site conditions.",
            "ja": "評価結果はGUIDANCE参考値です: 閾値は暫定/承認済みテンプレート値で、"
                  "実写検証されておらず、FAVORABLE保証にはなりません。開花窗口は"
                  "seasonal-calendar.json（例年窓・当年窓、owner管理）から算出。水面状態は"
                  "風速・降水・気温からの3段階派生（鏡面/撮影可/不適）。潮位で決まる海岸"
                  "被写体は誠実にnot_evaluatableへ降格 — 撮影前に干潮表を自身で確認して"
                  "ください。滝の水量状態は直前72h累積雨量からの3段階派生（low/mid/high）、"
                  "鳴門渦潮の大潮帯は朔望の天文代理で判定（正確な時刻は公式潮見表）。"
                  "天気はグリッド予報であり現地実況ではありません。",
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
