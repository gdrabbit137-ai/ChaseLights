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
# CL-DATA-72 batch A: seasonal_state leaves NO_SOURCE_METRICS — the verdict is
# now computed from data/v2/seasonal-calendar.json (CL-COND-A8, deterministic
# date-window matching). water_surface_state stays a known-honest gap: the
# tide-decided shoreline subjects (天空之鏡/潮汐決定型, e.g. tw-015 高美濕地)
# keep it REQUIRED and degrade to NOT_EVALUABLE (CL-COND-A7 owner ruling).
NO_SOURCE_METRICS = {"water_surface_state"}
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
    if metric == "venue_open_window":
        return venue_open_verdict(condition, local_start_min)
    if metric == "cloud_base_height":
        # CL-DATA-71: viewpoint-relative cloud-base window for the
        # cloud-sea/雲瀑/霧海/琉璃光 families. The observation is the
        # pipeline's existing LCL proxy cell (lcl_height_m_agl, metres
        # above the viewpoint grid ground, derived from 2 m temperature
        # and dew point by the batch adapter); the contract threshold is
        # either the place's catalog-recorded band (between) or the
        # DEM−200 rule (lt viewpoint elevation − 200, the CL-DATA-12
        # cloud-sea-family convention). The viewpoint elevation is bound
        # onto the condition by the batch runner (camera altitude_m,
        # else the V1 spot-catalog DEM elevation); a missing elevation
        # means the viewpoint-relative claim is unverified — propagate
        # UNKNOWN, never a fabricated comparison.
        elevation = condition.get("viewpoint_elevation_m")
        if not isinstance(elevation, (int, float)) or isinstance(elevation, bool):
            return "UNKNOWN", "VIEWPOINT_ELEVATION_UNKNOWN"
        if operator not in ("lt", "lte", "gt", "gte", "between"):
            return "UNKNOWN", "NON_NUMERIC_OPERATOR"
        if operator == "between" and (not isinstance(threshold, list)
                                      or len(threshold) != 2):
            return "UNKNOWN", "INVALID_THRESHOLD"
        cell = values.get("lcl_height_m_agl")
        if not isinstance(cell, dict) or cell.get("state") != "AVAILABLE":
            return "UNKNOWN", "CELL_NOT_AVAILABLE"
        value = cell.get("value")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return "UNKNOWN", "CELL_VALUE_INVALID"
        try:
            passed = compare(float(value), operator, threshold)
        except Exception:
            return "UNKNOWN", "INVALID_THRESHOLD"
        detail = (f"CLOUD_BASE_HEIGHT(lcl_proxy={round(float(value))}m,"
                  f"viewpoint={round(float(elevation))}m)")
        return ("PASS" if passed else "FAIL"), detail
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


def condition_value(condition, values, astro_row, local_date=None):
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
    if metric == "seasonal_state":
        # CL-COND-A8: display the resolved window value (window_open /
        # window_closed / None when not computable) — the contract's own
        # rationale documents this display value.
        verdict, _detail = seasonal_window_verdict(
            condition.get("seasonal_entries") or [], local_date)
        return {"PASS": "window_open", "FAIL": "window_closed"}.get(verdict)
    if metric == "cloud_base_height":
        # CL-DATA-71: display the LCL proxy the window was judged on.
        cell = values.get("lcl_height_m_agl")
        if not isinstance(cell, dict) or cell.get("state") != "AVAILABLE":
            return None
        return boolean_value_label(cell.get("value"))
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
                     local_date=None):
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
                                  local_date=local_date),
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
        else:
            tz_display = {"iana": zone, "utc_offset_hours": offset,
                          "status": "DISPLAY_APPROXIMATION"}
            local_offset = offset
        need_moon = any("moon" in c["metric"] or "galactic" in c["metric"]
                        for doc in group["opportunities"]
                        for c in doc["condition_contract"]["conditions"])
        hours = artifact["hours"]
        # CL-DATA-72 batch A / CL-COND-A7: derive the per-hour
        # water_reflection_state proxy once per coordinate group and attach it
        # to the shared hour rows (idempotent — every reflection opportunity of
        # the group reads the same cells).
        reflection_levels = water_reflection_levels(hours)
        for hour_row, level in zip(hours, reflection_levels):
            hour_row["values"]["water_reflection_state"] = level
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
                if _cond.get("metric") == "cloud_base_height":
                    _cond["viewpoint_elevation_m"] = camera_alt
            # CL-DATA-72 batch A / CL-COND-A8: bind the opportunity's
            # seasonal-calendar entries onto every seasonal_state condition
            # (same binding pattern as light_direction/cloud_base_height).
            # CL-COND-A4: resolve the moon alternation (anchor + dependents)
            # once per contract.
            for _cond in conditions_eval:
                if _cond.get("metric") == "seasonal_state":
                    _cond["seasonal_entries"] = seasonal_by_spot.get(oid) or []
            alternation = moon_alternation(conditions_eval)
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
                                              need_moon=need_moon)
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
                for cid, state in states.items():
                    day_verdict_counts.setdefault(day_key, {}).setdefault(
                        cid, {"PASS": 0, "FAIL": 0, "UNKNOWN": 0})[state] += 1
                hour_ctxs.append((at, hour_row, astro_row, states, status))
                for row in detail_hour_rows(
                        hour_row, local_stamp, status, conditions_eval,
                        astro_row, states, precise_local, precise_off,
                        local_date=local_date):
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
                snap_local_date = (snap_at + timedelta(hours=local_offset)).date()
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
                                                  local_date=snap_local_date),
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
                     "氣溫派生三級（鏡面/可拍/不宜），潮汐決定型岸邊景點（天空之鏡類）誠實降級"
                     "為不可評估、拍攝前請自行查潮汐表。天氣為網格預報，不代表拍攝點實況。",
            "en": "Results are GUIDANCE only: thresholds are provisional/approved "
                  "genre-template values, not calibrated against real shoots, and never "
                  "constitute a FAVORABLE guarantee. Seasonal windows are computed from "
                  "seasonal-calendar.json (owner-maintained typical/current-season "
                  "windows); the reflection water-surface state is a derived three-level "
                  "proxy (mirror/shootable/unfit) from wind, precipitation and air "
                  "temperature, and tide-decided shoreline subjects degrade honestly to "
                  "not-evaluatable — check the tide table yourself before shooting. "
                  "Weather is grid forecast data, not on-site conditions.",
            "ja": "評価結果はGUIDANCE参考値です: 閾値は暫定/承認済みテンプレート値で、"
                  "実写検証されておらず、FAVORABLE保証にはなりません。開花窗口は"
                  "seasonal-calendar.json（例年窓・当年窓、owner管理）から算出。水面状態は"
                  "風速・降水・気温からの3段階派生（鏡面/撮影可/不適）。潮位で決まる海岸"
                  "被写体は誠実にnot_evaluatableへ降格 — 撮影前に干潮表を自身で確認して"
                  "ください。天気はグリッド予報であり現地実況ではありません。",
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
