"""Batch Open-Meteo forecast adapter for V2 opportunity evaluation.

Extends the scoped open_meteo_hourly pilot adapter to a batch, multi-place
research pipeline authorized by the owner (2026-10-26). Noncommercial
Open-Meteo use per the pilot gate terms review; no fabricated values.

Two calls per place:
- /v1/forecast: pilot ten fields + pressure-level vars (925/850 hPa) +
  legacy total cloudcover + visibility.
- /v1/air-quality: aerosol_optical_depth (CAMS 550 nm).

Derived quantities (documented approximations, never raw passthrough):
- cloud_cover_mid_and_high = max(mid, high) (worst of the two layers)
- lcl_height_m_agl = 125 * (T2m - Td2m) parcel LCL approximation (m AGL)
- temperature_delta_850_925_c = T850 - T925 (inversion indicator)
Missing cells become state=UNAVAILABLE cells; never zero-filled.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

FORECAST_FIELDS = [
    "temperature_2m", "dew_point_2m", "relative_humidity_2m",
    "cloudcover_low", "cloudcover_mid", "cloudcover_high", "cloudcover",
    "wind_speed_10m", "visibility", "precipitation", "precipitation_probability",
    "temperature_925hPa", "relative_humidity_925hPa",
    "temperature_850hPa", "relative_humidity_850hPa", "wind_speed_850hPa",
]
AQ_FIELDS = ["aerosol_optical_depth"]
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
AQ_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
TIMEOUT_S = 30
MAX_BODY_BYTES = 3 * 1024 * 1024
RETRIEVAL_FRESHNESS_S = 21600  # same operational cache-age bound as the pilot


class FetchFailure(Exception):
    pass


def _get_json(url, params, attempts=3):
    query = urllib.parse.urlencode(params)
    target = f"{url}?{query}"
    request = urllib.request.Request(target, headers={"User-Agent": "ChaseLights-v2-evaluation/0.1 research"})
    last_error = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
                status = response.status
                raw = response.read(MAX_BODY_BYTES + 1)
            if len(raw) > MAX_BODY_BYTES:
                raise FetchFailure("OVERSIZED_BODY")
            if status != 200:
                raise FetchFailure(f"HTTP_{status}")
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise FetchFailure("NOT_JSON") from error
            if payload.get("error"):
                raise FetchFailure("PROVIDER_ERROR:" + str(payload.get("reason", ""))[:80])
            digest = hashlib.sha256(raw).hexdigest()
            return payload, target, digest
        except FetchFailure as error:
            code = str(error)
            last_error = error
            # 5xx and transport errors are retried with backoff; 4xx are not.
            if code.startswith("HTTP_5") or code.startswith("TRANSPORT_"):
                time.sleep(2 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last_error = FetchFailure(f"TRANSPORT_{type(error).__name__}")
            time.sleep(2 * (attempt + 1))
    raise last_error


def _cell(value, unit, *, integer=False, minimum=None, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return {"value": None, "unit": unit, "state": "UNAVAILABLE", "reason_code": "NULL_OR_INVALID"}
    if minimum is not None and value < minimum or maximum is not None and value > maximum:
        return {"value": None, "unit": unit, "state": "UNAVAILABLE", "reason_code": "OUT_OF_RANGE"}
    return {"value": value, "unit": unit, "state": "AVAILABLE", "reason_code": None}


def _km(value):
    return None if value is None else value / 1000.0


def _lcl_height_m(t_c, td_c):
    if t_c is None or td_c is None:
        return None
    spread = t_c - td_c
    if spread < 0:
        return None  # super-saturated input: refuse rather than clamp
    return 125.0 * spread


def fetch_place(lat, lon, forecast_hours=72):
    """Return a normalized RAW_ONLY artifact for one coordinate."""
    retrieved_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    forecast_params = {
        "latitude": f"{lat:.6f}", "longitude": f"{lon:.6f}",
        "forecast_hours": str(forecast_hours), "past_hours": "0",
        "timezone": "GMT", "timeformat": "unixtime", "cell_selection": "land",
        "temperature_unit": "celsius", "wind_speed_unit": "ms",
        "precipitation_unit": "mm", "hourly": ",".join(FORECAST_FIELDS),
    }
    aq_params = {
        "latitude": f"{lat:.6f}", "longitude": f"{lon:.6f}",
        "forecast_hours": str(forecast_hours), "timezone": "GMT",
        "hourly": ",".join(AQ_FIELDS),
    }
    forecast, forecast_url, forecast_sha = _get_json(FORECAST_URL, forecast_params)
    time.sleep(0.25)
    aq, aq_url, aq_sha = _get_json(AQ_URL, aq_params)
    hourly = forecast["hourly"]
    times = hourly["time"]
    if not times or any(not isinstance(t, int) for t in times):
        raise FetchFailure("INVALID_TIME_AXIS")
    for earlier, later in zip(times, times[1:]):
        if later - earlier != 3600:
            raise FetchFailure("NON_CONTIGUOUS_HOURS")
    aq_times = aq["hourly"]["time"]
    aod_by_time = {}
    for t, v in zip(aq_times, aq["hourly"]["aerosol_optical_depth"]):
        aod_by_time[t] = v
    hours = []
    for index, t in enumerate(times):
        values = {
            "temperature_2m": _cell(_at(hourly, "temperature_2m", index), "°C"),
            "dew_point_2m": _cell(_at(hourly, "dew_point_2m", index), "°C"),
            "relative_humidity_2m": _cell(_at(hourly, "relative_humidity_2m", index), "%", minimum=0, maximum=100),
            "cloud_cover_low": _cell(_at(hourly, "cloudcover_low", index), "%", minimum=0, maximum=100),
            "cloud_cover_mid": _cell(_at(hourly, "cloudcover_mid", index), "%", minimum=0, maximum=100),
            "cloud_cover_high": _cell(_at(hourly, "cloudcover_high", index), "%", minimum=0, maximum=100),
            "cloud_cover_total": _cell(_at(hourly, "cloudcover", index), "%", minimum=0, maximum=100),
            "wind_speed_10m": _cell(_at(hourly, "wind_speed_10m", index), "m/s", minimum=0),
            "visibility": _cell(_km(_at(hourly, "visibility", index)), "km", minimum=0),
            "precipitation": _cell(_at(hourly, "precipitation", index), "mm", minimum=0),
            "precipitation_probability": _cell(_at(hourly, "precipitation_probability", index), "%", minimum=0, maximum=100),
            "relative_humidity_925hpa": _cell(_at(hourly, "relative_humidity_925hPa", index), "%", minimum=0, maximum=100),
            "relative_humidity_850hpa": _cell(_at(hourly, "relative_humidity_850hPa", index), "%", minimum=0, maximum=100),
            "wind_speed_850hpa": _cell(_at(hourly, "wind_speed_850hPa", index), "m/s", minimum=0),
            "aod_550nm": _cell(aod_by_time.get(t), "1", minimum=0, maximum=5),
        }
        t925 = _at(hourly, "temperature_925hPa", index)
        t850 = _at(hourly, "temperature_850hPa", index)
        if t925 is not None and t850 is not None:
            delta = t850 - t925
        else:
            delta = None
        values["temperature_delta_850_925_c"] = _cell(delta, "°C")
        t2m = _at(hourly, "temperature_2m", index)
        td2m = _at(hourly, "dew_point_2m", index)
        values["lcl_height_m_agl"] = _cell(_lcl_height_m(t2m, td2m), "m", minimum=0)
        mid = _at(hourly, "cloudcover_mid", index)
        high = _at(hourly, "cloudcover_high", index)
        values["cloud_cover_mid_and_high"] = _cell(
            None if mid is None or high is None else max(mid, high),
            "%", minimum=0, maximum=100)
        hours.append({"valid_at_utc": datetime.fromtimestamp(t, timezone.utc)
                      .isoformat(timespec="seconds").replace("+00:00", "Z"),
                      "values": values})
    return {
        "adapter_version": "open-meteo-batch-0.1",
        "provider": "open-meteo",
        "place_coordinate": {"latitude": lat, "longitude": lon},
        "grid": {"latitude": forecast.get("latitude"), "longitude": forecast.get("longitude"),
                 "elevation_m": forecast.get("elevation")},
        "retrieved_at_utc": retrieved_at,
        "sources": [
            {"source_url": forecast_url, "source_sha256": forecast_sha,
             "kind": "forecast", "fields": FORECAST_FIELDS},
            {"source_url": aq_url, "source_sha256": aq_sha,
             "kind": "air_quality", "fields": AQ_FIELDS},
        ],
        "freshness_policy": {"max_age_seconds": RETRIEVAL_FRESHNESS_S},
        "notes": {
            "visibility": "Open-Meteo returns metres; normalized to km to match metric-vocabulary",
            "lcl_height_m_agl": "125*(T2m-Td2m) parcel approximation, metres above ground",
            "cloud_cover_mid_and_high": "max(mid, high) worst-layer",
            "temperature_delta_850_925_c": "T850-T925 inversion indicator",
        },
        "hours": hours,
    }


def _at(hourly, key, index):
    series = hourly.get(key)
    if not isinstance(series, list) or index >= len(series):
        return None
    value = series[index]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    return float(value)
