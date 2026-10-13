"""Non-scoring V2 solar WINDOW: ideal-horizon NOAA/Meeus solar position.

No external weather, photographic evidence, legal camera position, navigation,
cloud geometry or favorable photographic verdict is inferred by this routine.

References: NOAA Solar Calculation Details (equation of time / declination);
Jean Meeus, Astronomical Algorithms (mean longitude, obliquity and anomaly).
Deterministic approximate solar-center altitude -0.833 deg crossing, NOT
actual visible terrain horizon/refraction or high-precision ephemeris.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
import json
import math
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA = Path(__file__).resolve().parents[2] / "specs/v2/schema/solar-window-request-v0.1.schema.json"
RESULT_SCHEMA = SCHEMA.with_name("solar-window-result-v0.1.schema.json")
MODEL_ID = "chase-v2-noaa-meeus"
ALGORITHM_VERSION = "0.1.0"


def _schema_validate(payload, path):
    schema = json.loads(path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    issues = sorted(validator.iter_errors(payload), key=lambda e: tuple(str(p) for p in e.path))
    if issues:
        raise ValueError("Invalid solar WINDOW payload: " + issues[0].message)


def _solar_altitude_deg(dt_utc: datetime, latitude: float, longitude: float) -> float:
    """Geometric solar center elevation in degrees; UTC-aware time only."""
    jd = dt_utc.timestamp() / 86400.0 + 2440587.5
    t = (jd - 2451545.0) / 36525.0
    r = math.radians
    l0 = (280.46646 + t * (36000.76983 + 0.0003032 * t)) % 360.0
    m = (357.52911 + t * (35999.05029 - 0.0001537 * t)) % 360.0
    e = 0.016708634 - t * (0.000042037 + 0.0000001267 * t)
    c = (math.sin(r(m)) * (1.914602 - t * (0.004817 + 0.000014 * t))
         + math.sin(r(2 * m)) * (0.019993 - 0.000101 * t)
         + math.sin(r(3 * m)) * 0.000289)
    omega = 125.04 - 1934.136 * t
    lam = l0 + c - 0.00569 - 0.00478 * math.sin(r(omega))
    eps0 = 23.0 + (26.0 + (21.448 - t * (46.815 + t * (0.00059 - t * 0.001813))) / 60.0) / 60.0
    eps = eps0 + 0.00256 * math.cos(r(omega))
    declination = math.asin(math.sin(r(eps)) * math.sin(r(lam)))
    y = math.tan(r(eps) / 2) ** 2
    eq_minutes = 4 * math.degrees(
        y * math.sin(2 * r(l0)) - 2 * e * math.sin(r(m))
        + 4 * e * y * math.sin(r(m)) * math.cos(2 * r(l0))
        - 0.5 * y * y * math.sin(4 * r(l0)) - 1.25 * e * e * math.sin(2 * r(m)))
    utc = dt_utc.astimezone(timezone.utc)
    minutes = utc.hour * 60 + utc.minute + utc.second / 60 + utc.microsecond / 60000000
    hour_angle = math.radians(((minutes + eq_minutes + 4 * longitude) % 1440) / 4 - 180)
    cos_zenith = (math.sin(r(latitude)) * math.sin(declination)
                  + math.cos(r(latitude)) * math.cos(declination) * math.cos(hour_angle))
    return 90 - math.degrees(math.acos(max(-1.0, min(1.0, cos_zenith))))


def _search_events(local_date: date, zone: ZoneInfo, lat: float, lon: float):
    start = datetime.combine(local_date, time.min, tzinfo=zone).astimezone(timezone.utc)
    stop = datetime.combine(local_date + timedelta(days=1), time.min, tzinfo=zone).astimezone(timezone.utc)
    if not timedelta(hours=22) <= stop - start <= timedelta(hours=26):
        raise ValueError("Unusual local-date duration; refuse to fabricate solar events")
    step = timedelta(minutes=2)
    target = -0.833
    timestamps = [start]
    while timestamps[-1] < stop:
        timestamps.append(min(stop, timestamps[-1] + step))
    altitudes = [_solar_altitude_deg(t, lat, lon) - target for t in timestamps]
    events = {"sunrise": [], "sunset": []}
    for i in range(1, len(timestamps)):
        before, after = altitudes[i - 1], altitudes[i]
        if before == 0 or after == 0 or before * after > 0:
            continue
        rising = before < after
        lo, hi = timestamps[i - 1], timestamps[i]
        for _ in range(18):
            mid = lo + (hi - lo) / 2
            mid_alt = _solar_altitude_deg(mid, lat, lon) - target
            if (mid_alt > 0) == (before > 0):
                lo = mid
            else:
                hi = mid
        crossing = lo + (hi - lo) / 2
        if crossing.astimezone(zone).date() == local_date:
            events["sunrise" if rising else "sunset"].append(crossing)
    if all(x > 0 for x in altitudes):
        polar = "POLAR_DAY"
    elif all(x < 0 for x in altitudes):
        polar = "POLAR_NIGHT"
    elif max(len(events["sunrise"]), len(events["sunset"])) > 1:
        polar = "UNKNOWN"
    else:
        polar = "NORMAL"
    return events, polar


def compute_solar_window(request: dict, *, computed_at: datetime | None = None) -> dict:
    """W1-schema-compatible approximate solar WINDOW; never a photo score.

    Unknown observer coordinates produce UNKNOWN_LOCATION; representative place
    samples produce only regional astronomical estimates (not camera geometry).
    """
    _schema_validate(request, SCHEMA)
    if (request["model"]["model_id"] != MODEL_ID or
            request["model"]["algorithm_version"] != ALGORITHM_VERSION):
        raise ValueError("Unknown or mislabeled model/algorithm version")
    if (request["model"]["horizon_assumption"] != "ideal_unobstructed" or
            request["model"]["sun_altitude_crossing_deg"] != -0.833):
        raise ValueError("Unsupported horizon/refraction assumption")
    try:
        zone = ZoneInfo(request["time_zone"])
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError("Unknown IANA timezone") from exc
    date_to_compute = date.fromisoformat(request["local_date"])
    now = computed_at if computed_at is not None else datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("computed_at must be timezone-aware")
    now = now.astimezone(timezone.utc)
    observer = request["observer"]
    result = {**request, "capability": "WINDOW",
              "computed_at_utc": now.isoformat().replace("+00:00", "Z"),
              "polar_state": "UNKNOWN", "sunrise": None, "sunset": None,
              "recommendation_eligible": False, "photography_verdict": "NOT_EVALUABLE",
              "limitations_i18n": {
                  "zh-TW": "理想無遮蔽地平線的區域日出日落估算；未驗證實際地平線、折射、雲況、合法機位或攝影適合度。",
                  "en": "Regional sunrise/sunset at an ideal unobstructed horizon; actual horizon, refraction, clouds, lawful camera point and photographic suitability are unverified.",
                  "ja": "遮蔽のない理想水平線での日の出・日の入り推定。実際の地平線・屈折・雲・適法な撮影位置や撮影適性は未確認。",
              }}
    def no_time(status: str, reason: str):
        return {"status": status, "time_utc": None, "time_local": None, "reason": reason}
    if observer["coordinate_role"] == "unknown":
        result["sunrise"] = no_time("UNKNOWN", "UNKNOWN_LOCATION")
        result["sunset"] = no_time("UNKNOWN", "UNKNOWN_LOCATION")
    else:
        events, result["polar_state"] = _search_events(date_to_compute, zone, observer["lat"], observer["lon"])
        for kind in ("sunrise", "sunset"):
            times = events[kind]
            if len(times) == 1 and result["polar_state"] != "UNKNOWN":
                event_utc = times[0]
                result[kind] = {"status": "CALCULATED",
                                "time_utc": event_utc.isoformat().replace("+00:00", "Z"),
                                "time_local": event_utc.astimezone(zone).isoformat(),
                                "reason": None}
            elif len(times) > 1 or result["polar_state"] == "UNKNOWN":
                result[kind] = no_time("UNKNOWN", "AMBIGUOUS_HIGH_LATITUDE_CROSSINGS")
            else:
                reason = (result["polar_state"]
                          if result["polar_state"] in ("POLAR_DAY", "POLAR_NIGHT")
                          else "OTHER_HIGH_LATITUDE")
                result[kind] = no_time("NO_EVENT", reason)
    _schema_validate(result, RESULT_SCHEMA)
    return result
