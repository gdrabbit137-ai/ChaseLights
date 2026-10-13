"""W3 M6b: authenticatable raw NOAA/NWS gridpoint forecast transport/adapter.

No photography evaluation or live recommendation. A caller-supplied fake JSON
document is always TEST_FIXTURE, never a trusted NOAA response. Only HTTPS
through the pinned official host with redirection disabled is marked HTTPS_TLS.
The resulting record still lacks NWS model-issued/run identifiers and cannot
satisfy a photographic AUTO condition.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener
from jsonschema import Draft202012Validator, FormatChecker

SCHEMA = Path(__file__).resolve().parents[3] / "specs/v2/schema/weather-source-record-v0.1.schema.json"
POINTS = re.compile(r"^/points/(-?\\d+(?:\\.\\d+)?),(-?\\d+(?:\\.\\d+)?)$")
GRID = re.compile(r"^/gridpoints/([A-Z]{3})/(\\d+),(\\d+)$")
DURATION = re.compile(r"^P(?:(?P<days>\\d+)D)?(?:T(?:(?P<hours>\\d+)H)?(?:(?P<mins>\\d+)M)?)?$")
SOURCE_FIELDS = {
    "skyCover": {"wmoUnit:percent": (0, 100)},
    "relativeHumidity": {"wmoUnit:percent": (0, 100)},
    "probabilityOfPrecipitation": {"wmoUnit:percent": (0, 100)},
    "windSpeed": {"wmoUnit:km_h-1": (0, 400), "wmoUnit:m_s-1": (0, 112)},
    "temperature": {"wmoUnit:degC": (-120, 70)},
}
MAX_BYTES = 8 * 1024 * 1024
USER_AGENT = "ChaseLights-V2-M6b/0.1 (source research; https://github.com/gdrabbit137-ai/ChaseLights)"


class SourceFailure(ValueError):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _time(value):
    if isinstance(value, datetime):
        stamp = value
    elif isinstance(value, str):
        try:
            stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise SourceFailure("INVALID_TIME") from exc
    else:
        raise SourceFailure("INVALID_TIME")
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise SourceFailure("NAIVE_TIME")
    return stamp.astimezone(timezone.utc)


def _utc(stamp):
    return stamp.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _validate_url(url, kind):
    try:
        p = urlsplit(url)
    except (TypeError, ValueError) as exc:
        raise SourceFailure("INVALID_SOURCE_URL") from exc
    if (p.scheme != "https" or p.netloc != "api.weather.gov"
            or p.username or p.password or p.query or p.fragment):
        raise SourceFailure("INVALID_SOURCE_URL")
    match = (POINTS if kind == "points" else GRID).fullmatch(p.path)
    if match is None:
        raise SourceFailure("INVALID_SOURCE_URL")
    return match


def _interval(text):
    if not isinstance(text, str) or text.count("/") != 1:
        raise SourceFailure("INVALID_VALIDTIME_INTERVAL")
    start_raw, duration_raw = text.split("/")
    start = _time(start_raw)
    m = DURATION.fullmatch(duration_raw)
    if not m:
        raise SourceFailure("UNSUPPORTED_DURATION")
    parts = {k: int(v or 0) for k, v in m.groupdict().items()}
    delta = timedelta(days=parts["days"], hours=parts["hours"], minutes=parts["mins"])
    if not timedelta(minutes=1) <= delta <= timedelta(days=8):
        raise SourceFailure("UNSUPPORTED_DURATION")
    return start, start + delta


def _no_record(reason, *, detail=None):
    result = {"source_state": "UNKNOWN", "record": None,
              "photography_verdict": "NOT_EVALUABLE",
              "live_recommendation": False, "reasons": [reason]}
    if detail is not None:
        result["details"] = detail
    return result


def _strict_policy(policy):
    if (not isinstance(policy, dict) or policy.get("approved") is not True
            or not isinstance(policy.get("source"), str) or not policy["source"].strip()
            or type(policy.get("max_age_seconds")) is not int
            or not 0 < policy["max_age_seconds"] <= 172800):
        raise SourceFailure("FRESHNESS_POLICY_UNAPPROVED")
    return policy["max_age_seconds"]


def normalize_fixture(points_json, grid_json, original_grid_bytes, *,
                      points_url, grid_url, field, valid_at, retrieved_at,
                      coordinate_source, freshness_policy):
    """Normalize caller-supplied bytes; strictly TEST_FIXTURE and never live."""
    try:
        return _normalize(points_json, grid_json, original_grid_bytes, points_url=points_url,
                          grid_url=grid_url, field=field, valid_at=valid_at,
                          retrieved_at=retrieved_at, coordinate_source=coordinate_source,
                          freshness_policy=freshness_policy, retrieval_mode="TEST_FIXTURE")
    except (SourceFailure, TypeError, KeyError, ValueError, OverflowError) as exc:
        return _no_record(str(exc))


def _normalize(points_json, grid_json, original_grid_bytes, *,
               points_url, grid_url, field, valid_at, retrieved_at,
               coordinate_source, freshness_policy, retrieval_mode):
    p = _validate_url(points_url, "points")
    g = _validate_url(grid_url, "grid")
    lat, lon = map(float, p.groups())
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise SourceFailure("OUT_OF_RANGE_LOCATION")
    if not isinstance(coordinate_source, str) or len(coordinate_source.strip()) < 4:
        raise SourceFailure("COORDINATE_SOURCE_UNVERIFIED")
    if type(original_grid_bytes) is not bytes or not 0 < len(original_grid_bytes) <= MAX_BYTES:
        raise SourceFailure("INVALID_GRID_BYTES")
    if not isinstance(points_json, dict) or not isinstance(grid_json, dict):
        raise SourceFailure("INVALID_SOURCE_DOCUMENT")
    meta = points_json.get("properties")
    grid = grid_json.get("properties")
    if not isinstance(meta, dict) or not isinstance(grid, dict):
        raise SourceFailure("INVALID_SOURCE_DOCUMENT")
    if meta.get("forecastGridData") != grid_url:
        raise SourceFailure("GRID_MAPPING_CHANGED")
    if (meta.get("gridId") != g.group(1) or type(meta.get("gridX")) is not int
            or type(meta.get("gridY")) is not int
            or meta["gridX"] != int(g.group(2)) or meta["gridY"] != int(g.group(3))):
        raise SourceFailure("GRID_MAPPING_CHANGED")
    geometry = points_json.get("geometry") or {}
    coords = geometry.get("coordinates") if isinstance(geometry, dict) else None
    if (geometry.get("type") != "Point" or not isinstance(coords, list)
            or len(coords) < 2 or any(type(n) not in (int, float)
                                       or not math.isfinite(n) for n in coords[:2])
            or abs(coords[0] - lon) > 0.00001 or abs(coords[1] - lat) > 0.00001):
        raise SourceFailure("POINTS_COORDINATE_MISMATCH")

    fresh_limit = _strict_policy(freshness_policy)
    retrieved = _time(retrieved_at)
    source_updated = _time(grid.get("updateTime"))
    if source_updated > retrieved:
        raise SourceFailure("FUTURE_SOURCE_UPDATE")
    if (retrieved - source_updated).total_seconds() > fresh_limit:
        raise SourceFailure("STALE_SOURCE")
    requested = _time(valid_at)
    if field not in SOURCE_FIELDS:
        raise SourceFailure("UNSUPPORTED_FIELD")
    layer = grid.get(field)
    if not isinstance(layer, dict):
        raise SourceFailure("MISSING_FIELD")
    units = layer.get("uom")
    allowed = SOURCE_FIELDS[field]
    if units not in allowed:
        raise SourceFailure("UNSUPPORTED_UNIT")
    values = layer.get("values")
    if not isinstance(values, list) or not values:
        raise SourceFailure("MISSING_INTERVALS")
    candidates = []
    for entry in values:
        if not isinstance(entry, dict):
            raise SourceFailure("INVALID_INTERVAL")
        start, end = _interval(entry.get("validTime"))
        if start <= requested < end:
            candidates.append((start, end, entry.get("value")))
    if len(candidates) != 1:
        raise SourceFailure("MISSING_OR_OVERLAPPING_INTERVAL")
    start, end, value = candidates[0]
    if type(value) not in (int, float) or not math.isfinite(value):
        raise SourceFailure("RAW_VALUE_MISSING_OR_INVALID")
    minimum, maximum = allowed[units]
    if not minimum <= value <= maximum:
        raise SourceFailure("RAW_VALUE_OUT_OF_RANGE")
    sha = hashlib.sha256(original_grid_bytes).hexdigest()
    record = {
        "schema_version": "0.1.0",
        "record_id": f"NOAA_NWS-{g.group(1)}-{g.group(2)}-{g.group(3)}-{field}-{_utc(start)}",
        "source_kind": "FORECAST", "provider": "NOAA_NWS",
        "source_url": grid_url, "mapping_url": points_url,
        "source_sha256": sha, "source_update_time_utc": _utc(source_updated),
        "retrieved_at_utc": _utc(retrieved),
        "provider_issued_at_utc": None, "provider_run_id": None,
        "grid": {
            "office": g.group(1), "grid_x": int(g.group(2)), "grid_y": int(g.group(3)),
            "sample_lat": lat, "sample_lon": lon,
            "coordinate_role": "representative_place_sample",
            "coordinate_source": coordinate_source,
            "coordinate_uncertainty_m": None, "native_resolution_m": None,
        },
        "field": field, "uom": units, "raw_value": value,
        "valid_from_utc": _utc(start), "valid_until_utc": _utc(end),
        "retrieval_mode": retrieval_mode, "data_state": "RAW_ONLY",
        "calibration_status": "UNVALIDATED", "recommendation_eligible": False,
        "photography_verdict": "NOT_EVALUABLE",
        "limitations_i18n": {
            "zh-TW": "NWS 網格原始預報；非攝影機位、合法導航或經校正的拍攝適合度。",
            "en": "NWS raw grid forecast, not surveyed camera access, navigation or calibrated photographic suitability.",
            "ja": "NWS の格子予報原データであり、撮影地点・合法な経路や撮影適性の保証ではない。",
        },
    }
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record))
    if errors:
        raise SourceFailure("SCHEMA_INVALID: " + errors[0].message)
    return {"source_state": "RAW_SOURCE_ONLY", "record": record,
            "photography_verdict": "NOT_EVALUABLE",
            "live_recommendation": False, "reasons": ["NO_APPROVED_PHOTO_THRESHOLD",
                                                     "NO_VERIFIED_MODEL_RUN"]}


def _get_json_bytes(url, *, timeout, opener):
    _validate_url(url, "points" if "/points/" in url else "grid")
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/geo+json, application/json"})
    with opener.open(req, timeout=timeout) as response:
        if response.geturl() != url or response.status != 200:
            raise SourceFailure("REDIRECT_OR_BAD_HTTP_RESPONSE")
        data = response.read(MAX_BYTES + 1)
    if not 0 < len(data) <= MAX_BYTES:
        raise SourceFailure("INVALID_GRID_BYTES")
    try:
        parsed = json.loads(data.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise SourceFailure("INVALID_SOURCE_JSON") from exc
    return parsed, data


def fetch_nws_gridpoint(*, latitude, longitude, field, valid_at,
                        coordinate_source, freshness_policy, retrieved_at=None,
                        timeout=12.0, opener=None):
    """Actual HTTPS-only NOAA read; fail closed, never convert into score.

    Rate-limit production callers and cache the official /points mapping.
    A custom opener is supported for deterministic transport-security tests;
    only the default opener represents an actual TLS-validated download.
    """
    try:
        if (type(latitude) not in (int, float) or type(longitude) not in (int, float)
                or not math.isfinite(latitude) or not math.isfinite(longitude)
                or not (-90 <= latitude <= 90 and -180 <= longitude <= 180)):
            raise SourceFailure("OUT_OF_RANGE_LOCATION")
        if not 0 < timeout <= 30:
            raise SourceFailure("INVALID_TIMEOUT")
        points_url = f"https://api.weather.gov/points/{latitude:g},{longitude:g}"
        _validate_url(points_url, "points")
        transport = opener if opener is not None else build_opener(NoRedirect)
        meta, _ = _get_json_bytes(points_url, timeout=timeout, opener=transport)
        prop = meta.get("properties") if isinstance(meta, dict) else None
        grid_url = prop.get("forecastGridData") if isinstance(prop, dict) else None
        _validate_url(grid_url, "grid")
        grid, raw = _get_json_bytes(grid_url, timeout=timeout, opener=transport)
        result = _normalize(meta, grid, raw, points_url=points_url, grid_url=grid_url,
                            field=field, valid_at=valid_at,
                            retrieved_at=retrieved_at or datetime.now(timezone.utc),
                            coordinate_source=coordinate_source,
                            freshness_policy=freshness_policy,
                            retrieval_mode="HTTPS_TLS" if opener is None else "TEST_FIXTURE")
        return result
    except (SourceFailure, KeyError, TypeError, ValueError, OverflowError) as exc:
        return _no_record(str(exc))
