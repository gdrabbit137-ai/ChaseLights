"""One pinned Open-Meteo / tw-036 hourly research pilot; never an evaluator.

The W1 schema and W2 binding are read from their immutable Git objects, not
copied or modified here. No import performs I/O against a weather provider.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import hashlib
from importlib import resources
import json
import math
from pathlib import Path
import re
import subprocess
from zoneinfo import TZPATH, ZoneInfo

from jsonschema import Draft202012Validator, FormatChecker

CONTRACT_SHA = "74f21b365d366b0d1d12efbc23cf6cce484b6b5e"
STUDY_SHA = "a649ace57cda5ca02edc1481660ef2f567eb86f1"
SCHEMA_PATH = "specs/v2/schema/hourly-weather-info-v0.1.schema.json"
BINDING_PATH = "data/v2/weather-pilots/tw-036-open-meteo.json"
SCHEMA_SHA256 = "ce29fee0f08fdd8c71d96a8d33dfb7f68b6235b67e175ac9e1e3775250b06a1a"
BINDING_SHA256 = "9fb4cc6f89daae3ce851a30f2880847705b4afa6097b7c4c54d19d357b202921"
ENDPOINT = "https://api.open-meteo.com/v1/forecast"
MAX_BYTES = 3 * 1024 * 1024
MAX_AGE = 21600
FIELDS = {
    "temperature_2m": "°C", "dew_point_2m": "°C",
    "relative_humidity_2m": "%", "cloud_cover_low": "%",
    "cloud_cover_mid": "%", "cloud_cover_high": "%",
    "wind_speed_10m": "m/s", "visibility": "m",
    "precipitation": "mm", "precipitation_probability": "%",
}
ACCUMULATED = frozenset(("precipitation", "precipitation_probability"))


class PilotFailure(ValueError):
    """An explicit rejection; never an implicit zero or an old artifact."""


def utc(value):
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise PilotFailure("INVALID_CLOCK") from exc
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise PilotFailure("NAIVE_OR_INVALID_CLOCK")
    return value.astimezone(timezone.utc)


def stamp(value):
    return utc(value).isoformat().replace("+00:00", "Z")


def _finite(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def _unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise PilotFailure("DUPLICATE_JSON_KEY")
        obj[key] = value
    return obj


def decode(raw):
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object,
                          parse_constant=lambda _: (_ for _ in ()).throw(PilotFailure("NONFINITE_JSON")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise PilotFailure("INVALID_JSON") from exc


class PilotInputs:
    __slots__ = ("_binding_raw", "_schema_raw")

    def __init__(self, binding_raw, schema_raw):
        if hashlib.sha256(binding_raw).hexdigest() != BINDING_SHA256:
            raise PilotFailure("PILOT_BINDING_HASH_MISMATCH")
        if hashlib.sha256(schema_raw).hexdigest() != SCHEMA_SHA256:
            raise PilotFailure("PILOT_SCHEMA_HASH_MISMATCH")
        self._binding_raw, self._schema_raw = binding_raw, schema_raw

    @property
    def binding_raw(self):
        return self._binding_raw

    @property
    def schema_raw(self):
        return self._schema_raw

    @property
    def binding(self):
        return decode(self.binding_raw)

    @property
    def validator(self):
        schema = decode(self.schema_raw)
        Draft202012Validator.check_schema(schema)
        return Draft202012Validator(schema, format_checker=FormatChecker())


def load_inputs(repo=None):
    repo = Path(repo) if repo else Path(__file__).resolve().parents[3]
    def read(path):
        try:
            return subprocess.check_output(["git", "-C", str(repo), "show", CONTRACT_SHA + ":" + path],
                                           stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as exc:
            raise PilotFailure("PINNED_CONTRACT_UNAVAILABLE: fetch PR #521 fixed HEAD") from exc
    return PilotInputs(read(BINDING_PATH), read(SCHEMA_PATH))


def request_metadata(inputs):
    b = inputs.binding
    return {"latitude": b["sample"]["latitude"], "longitude": b["sample"]["longitude"],
            "coordinate_role": b["sample"]["coordinate_role"], "forecast_hours": 72,
            "past_hours": 0, "timezone": "GMT", "timeformat": "unixtime",
            "cell_selection": "land", "temperature_unit": "celsius",
            "wind_speed_unit": "ms", "precipitation_unit": "mm", "hourly": ",".join(FIELDS)}


def build_request(inputs):
    from urllib.parse import urlencode
    return ENDPOINT + "?" + urlencode({k: v for k, v in request_metadata(inputs).items()
                                       if k != "coordinate_role"})


def taipei_zone():
    """Load the actual zone file and its colocated IANA version, without fallback."""
    for directory in TZPATH:
        root = Path(directory)
        path = root / "Asia/Taipei"
        if not path.is_file():
            continue
        try:
            first = (root / "tzdata.zi").read_text().splitlines()[0]
            version = re.fullmatch(r"# version (20\d{2}[a-z])", first)
            if version is None:
                raise PilotFailure("UNKNOWN_TZDB_VERSION")
            with path.open("rb") as file:
                return ZoneInfo.from_file(file, key="Asia/Taipei"), version.group(1)
        except OSError as exc:
            raise PilotFailure("UNKNOWN_TZDB_VERSION") from exc
    try:
        import tzdata
        with resources.files("tzdata.zoneinfo").joinpath("Asia/Taipei").open("rb") as file:
            return ZoneInfo.from_file(file, key="Asia/Taipei"), tzdata.IANA_VERSION
    except (ImportError, OSError) as exc:
        raise PilotFailure("TIME_ZONE_UNAVAILABLE") from exc


def _cell(field, hourly, units, index):
    unit = FIELDS[field]
    supplied_unit = units.get(field)
    source_unit = supplied_unit if isinstance(supplied_unit, str) else None
    values = hourly.get(field)
    value, reason = None, None
    if field not in hourly or (isinstance(values, list) and index >= len(values)):
        reason = "MISSING_FIELD"
    elif not isinstance(values, list):
        reason = "INVALID_VALUE"
    elif values[index] is None:
        reason = "NULL_VALUE"
    elif not _finite(values[index]):
        reason = "INVALID_VALUE"
    elif source_unit != unit:
        reason = "UNIT_MISMATCH"
    elif ((unit == "%" and not 0 <= values[index] <= 100)
          or (unit in ("m/s", "m", "mm") and values[index] < 0)):
        reason = "INVALID_VALUE"
    else:
        value = values[index]
    return {"value": value, "unit": unit, "source_unit": source_unit,
            "state": "UNAVAILABLE" if reason else "AVAILABLE", "reason_code": reason}


def diagnostic(reason, *, availability="ERROR"):
    return {"availability": availability, "artifact": None, "reasons": [reason],
            "data_state": "RAW_ONLY", "calibration_status": "UNVALIDATED",
            "recommendation_eligible": False, "photography_verdict": "NOT_EVALUABLE"}


def normalize_fixture(raw, *, inputs, source_url, expected_sha256, requested_at,
                      retrieved_at, normalized_at, checked_at):
    """Caller-supplied bytes are always TEST_FIXTURE, never live evidence."""
    return _normalize(raw, inputs=inputs, source_url=source_url, expected_sha256=expected_sha256,
                      requested_at=requested_at, retrieved_at=retrieved_at,
                      normalized_at=normalized_at, checked_at=checked_at, retrieval_mode="TEST_FIXTURE")


def _normalize(raw, *, inputs, source_url, expected_sha256, requested_at,
               retrieved_at, normalized_at, checked_at, retrieval_mode):
    try:
        artifact = _artifact(raw, inputs=inputs, source_url=source_url,
                             expected_sha256=expected_sha256, requested_at=requested_at,
                             retrieved_at=retrieved_at, normalized_at=normalized_at,
                             checked_at=checked_at, retrieval_mode=retrieval_mode)
        return {"availability": artifact["availability"], "artifact": artifact, "reasons": [],
                "data_state": "RAW_ONLY", "calibration_status": "UNVALIDATED",
                "recommendation_eligible": False, "photography_verdict": "NOT_EVALUABLE"}
    except PilotFailure as exc:
        reason = str(exc)
        return diagnostic(reason, availability="EMPTY" if reason == "EMPTY_TIME_AXIS" else "ERROR")
    except (TypeError, ValueError, KeyError, OverflowError, OSError) as exc:
        return diagnostic("INVALID_RESPONSE: " + type(exc).__name__)


def _artifact(raw, *, inputs, source_url, expected_sha256, requested_at,
              retrieved_at, normalized_at, checked_at, retrieval_mode):
    if source_url != build_request(inputs):
        raise PilotFailure("REQUEST_IDENTITY_MISMATCH")
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_BYTES:
        raise PilotFailure("EMPTY_OR_OVERSIZED_BODY")
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise PilotFailure("SOURCE_SHA256_MISMATCH")
    requested, retrieved, normalized, checked = map(utc, (requested_at, retrieved_at, normalized_at, checked_at))
    if not requested <= retrieved <= normalized <= checked:
        raise PilotFailure("CLOCK_ORDER_OR_FUTURE_RETRIEVAL")
    if retrieval_mode not in ("TEST_FIXTURE", "HTTPS_TLS"):
        raise PilotFailure("INVALID_RETRIEVAL_MODE")
    source = decode(raw)
    if not isinstance(source, dict) or source.get("error"):
        raise PilotFailure("INVALID_SOURCE_OBJECT")
    if source.get("timezone") != "GMT" or type(source.get("utc_offset_seconds")) is not int or source["utc_offset_seconds"] != 0:
        raise PilotFailure("PROVIDER_TIME_ZONE_MISMATCH")
    lat, lon = source.get("latitude"), source.get("longitude")
    if not _finite(lat) or not _finite(lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise PilotFailure("INVALID_RESPONSE_GRID")
    # Gross request/response misbinding guard only, NOT model resolution,
    # accuracy or coastal representativeness. Accept provider grid snapping.
    point = inputs.binding["sample"]
    if abs(lat - point["latitude"]) > 0.5 or abs(lon - point["longitude"]) > 0.5:
        raise PilotFailure("RESPONSE_GRID_OUTSIDE_PILOT_AREA")
    elevation = source.get("elevation")
    if elevation is not None and not _finite(elevation):
        raise PilotFailure("INVALID_RESPONSE_ELEVATION")
    hourly, units = source.get("hourly"), source.get("hourly_units")
    if not isinstance(hourly, dict):
        raise PilotFailure("EMPTY_TIME_AXIS")
    times = hourly.get("time")
    if times is None or times == []:
        raise PilotFailure("EMPTY_TIME_AXIS")
    if not isinstance(times, list) or len(times) > 72:
        raise PilotFailure("INVALID_TIME_AXIS_LENGTH")
    if not isinstance(units, dict) or units.get("time") != "unixtime":
        raise PilotFailure("INVALID_TIME_UNIT")
    if any(not _finite(t) or t % 3600 != 0 for t in times):
        raise PilotFailure("INVALID_HOUR_AXIS")
    if any(b - a != 3600 for a, b in zip(times, times[1:])):
        raise PilotFailure("NONCONTIGUOUS_HOUR_AXIS")
    start_min = requested.replace(minute=0, second=0, microsecond=0).timestamp()
    start_max = retrieved.replace(minute=0, second=0, microsecond=0).timestamp()
    if not start_min <= times[0] <= start_max:
        raise PilotFailure("RESPONSE_HORIZON_MISMATCH")
    for field in FIELDS:
        if isinstance(hourly.get(field), list) and len(hourly[field]) > len(times):
            raise PilotFailure("FIELD_LONGER_THAN_TIME_AXIS: " + field)
    rows = []
    for index, epoch in enumerate(times):
        t = datetime.fromtimestamp(epoch, timezone.utc)
        rows.append({"valid_at_utc": stamp(t),
                     "preceding_hour": {"start_utc": stamp(t - timedelta(hours=1)), "end_utc": stamp(t)},
                     "values": {field: _cell(field, hourly, units, index) for field in FIELDS}})
    complete = len(rows) == 72 and all(cell["state"] == "AVAILABLE" for row in rows for cell in row["values"].values())
    age = (checked - retrieved).total_seconds()
    _, tzdb = taipei_zone()
    artifact = {
        "schema_version": "0.1.0", "artifact_kind": "HOURLY_WEATHER_INFO",
        "pilot_id": inputs.binding["pilot_id"], "pilot_binding_sha256": BINDING_SHA256,
        "place_id": "tw-036", "time_zone": "Asia/Taipei", "tzdb_version": tzdb,
        "data_state": "RAW_ONLY", "recommendation_eligible": False,
        "photography_verdict": "NOT_EVALUABLE", "calibration_status": "UNVALIDATED",
        "availability": "STALE" if age > MAX_AGE else ("COMPLETE" if complete else "PARTIAL"),
        "request": request_metadata(inputs),
        "source": {"provider": "OPEN_METEO", "source_url": source_url,
                   "source_sha256": expected_sha256, "retrieval_mode": retrieval_mode,
                   "retrieved_at_utc": stamp(retrieved), "normalized_at_utc": stamp(normalized),
                   "source_update_time_utc": None, "provider_issued_at_utc": None,
                   "provider_run_id": None, "model_selection": "provider_default_auto",
                   "resolved_model_ids": None, "native_resolution_m": None,
                   "native_time_resolution_seconds": None, "output_step_seconds": 3600,
                   "provider_timezone": "GMT", "provider_utc_offset_seconds": 0,
                   "response_grid_latitude": lat, "response_grid_longitude": lon,
                   "response_elevation_m": elevation, "source_freshness": "UNKNOWN",
                   "source_metadata_reason": "NOT_SUPPLIED_BY_FORECAST_RESPONSE"},
        "retrieval_age_policy": {"checked_at_utc": stamp(checked), "max_age_seconds": MAX_AGE,
                                 "basis": "RETRIEVAL_AGE_ONLY_NOT_MODEL_AGE"},
        "hours": rows,
        "attribution": {"provider_url": "https://open-meteo.com/",
                        "licence_url": "https://creativecommons.org/licenses/by/4.0/",
                        "modifications_i18n": {
                            "zh-TW": "保留原始數值與單位，轉換 UTC 時間格式並標示缺值、無效值及前一小時區間；未進行插補或攝影評分。",
                            "en": "Original values and units retained; UTC timestamps, unavailable values and preceding-hour support normalized. No interpolation or photography scoring.",
                            "ja": "原値と単位を保持し、UTC時刻、欠損・無効値、直前1時間の区間を明示しました。補間や撮影スコアの算出はしていません。"}},
        "limitations_i18n": inputs.binding["limitations_i18n"],
    }
    validate_artifact(artifact, inputs)
    return artifact


def validate_artifact(artifact, inputs):
    """Schema PLUS identity/clock/axis semantics; schema alone is insufficient."""
    def finite_tree(value):
        if isinstance(value, float) and not math.isfinite(value):
            raise PilotFailure("NONFINITE_ARTIFACT")
        if isinstance(value, dict):
            for child in value.values(): finite_tree(child)
        elif isinstance(value, list):
            for child in value: finite_tree(child)
    finite_tree(artifact)
    errors = list(inputs.validator.iter_errors(artifact))
    if errors:
        raise PilotFailure("SCHEMA_INVALID: " + errors[0].message)
    if (artifact["pilot_binding_sha256"] != BINDING_SHA256
            or artifact["request"] != request_metadata(inputs)
            or artifact["source"]["source_url"] != build_request(inputs)):
        raise PilotFailure("ARTIFACT_IDENTITY_MISMATCH")
    s, p = artifact["source"], artifact["retrieval_age_policy"]
    retrieved, normalized, checked = map(utc, (s["retrieved_at_utc"], s["normalized_at_utc"], p["checked_at_utc"]))
    if not retrieved <= normalized <= checked:
        raise PilotFailure("CLOCK_ORDER_OR_FUTURE_RETRIEVAL")
    rows, previous, all_available = artifact["hours"], None, True
    for row in rows:
        t = utc(row["valid_at_utc"])
        if t.minute or t.second or t.microsecond or (previous and t - previous != timedelta(hours=1)):
            raise PilotFailure("INVALID_HOUR_AXIS")
        if utc(row["preceding_hour"]["start_utc"]) != t - timedelta(hours=1) or utc(row["preceding_hour"]["end_utc"]) != t:
            raise PilotFailure("INVALID_PRECEDING_HOUR")
        previous = t
        for cell in row["values"].values():
            if cell["value"] is not None and not _finite(cell["value"]):
                raise PilotFailure("INVALID_CELL")
            all_available &= cell["state"] == "AVAILABLE"
    expected = ("STALE" if (checked - retrieved).total_seconds() > MAX_AGE else
                "COMPLETE" if len(rows) == 72 and all_available else "PARTIAL")
    if artifact["availability"] != expected:
        raise PilotFailure("AVAILABILITY_MISMATCH")


def select_local_date(artifact, selected_date, inputs):
    """Read-only row selection by instant/accumulation END date, never prorated."""
    validate_artifact(artifact, inputs)
    if not isinstance(selected_date, str) or not re.fullmatch(r"\d{4}-\d\d-\d\d", selected_date):
        raise PilotFailure("INVALID_LOCAL_DATE")
    selected = date.fromisoformat(selected_date)
    zone, version = taipei_zone()
    if artifact["tzdb_version"] != version:
        raise PilotFailure("TZDB_VERSION_MISMATCH")
    return [row for row in artifact["hours"] if utc(row["valid_at_utc"]).astimezone(zone).date() == selected]
