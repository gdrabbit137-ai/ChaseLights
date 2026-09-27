"""Location-aware aurora runtime provider for ChaseLights R4.2.

B79 uses NOAA SWPC OVATION 2020 grid output as a short-horizon local aurora
signal.  Planetary Kp remains legacy/context data and is deliberately NOT used
as a canonical aurora_state fallback.

NOAA describes OVATION as a roughly 30–90 minute forecast of aurora location
and intensity.  The JSON grid's third value is treated as the local visible-
aurora probability/intensity proxy published by SWPC.  ChaseLights samples the
nearest 1-degree grid cell conservatively; it does not expand the oval by
hundreds of kilometres or claim exact visual certainty.
"""

from datetime import datetime, timezone
import math

from runtime_dependencies import dependencies_for_opportunity


PROVIDER_VERSION = "noaa-swpc-ovation-2020-b79-v1"
PRIMARY_URL = "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json"
FALLBACK_URL = "https://services.swpc.woc.noaa.gov/json/ovation_aurora_latest.json"
PROVIDER_URLS = (PRIMARY_URL, FALLBACK_URL)

# NOAA describes OVATION as a 30–90 minute forecast.  The generated ChaseLights
# weather grid is hourly, so ±90 minutes allows the nearest current/next hourly
# row without stretching one OVATION frame across the multi-day forecast.
VALID_WINDOW_MINUTES = 90

# The product graphics describe probability of visible aurora with 10/50/90%
# reference levels.  Ten is deliberately the minimum canonical activity gate;
# it is a signal that local auroral activity is forecast, not a guarantee that
# a person will see or photograph it.
MIN_LOCAL_AURORA_VALUE = 10.0


def _parse_utc(value):
    if not value:
        return None
    text = str(value).strip()
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def index_ovation_payload(payload):
    """Validate/index one NOAA OVATION JSON payload.

    Expected coordinate rows are [longitude, latitude, aurora].  Longitudes are
    0..359 in the NOAA grid.  Datetimes remain timezone-aware internally.
    """
    if not isinstance(payload, dict):
        raise ValueError("OVATION payload must be an object")

    observation_time = _parse_utc(payload.get("Observation Time"))
    forecast_time = _parse_utc(payload.get("Forecast Time"))
    if observation_time is None or forecast_time is None:
        raise ValueError("OVATION payload missing valid observation/forecast time")

    coordinates = payload.get("coordinates")
    if not isinstance(coordinates, list) or not coordinates:
        raise ValueError("OVATION payload missing coordinates")

    grid = {}
    for row in coordinates:
        if not isinstance(row, (list, tuple)) or len(row) < 3:
            continue
        try:
            lon = int(round(float(row[0]))) % 360
            lat = int(round(float(row[1])))
            value = float(row[2])
        except (TypeError, ValueError):
            continue
        if not -90 <= lat <= 90 or not math.isfinite(value):
            continue
        grid[(lon, lat)] = max(0.0, min(100.0, value))

    if not grid:
        raise ValueError("OVATION payload has no usable coordinate rows")

    return {
        "provider": "NOAA SWPC OVATION",
        "provider_version": PROVIDER_VERSION,
        "observation_time": observation_time,
        "forecast_time": forecast_time,
        "grid": grid,
        "data_format": payload.get("Data Format"),
    }


def _nearest_grid_value(indexed, lat, lon):
    grid = (indexed or {}).get("grid") or {}
    if not grid:
        return None

    lat_value = max(-90.0, min(90.0, float(lat)))
    lon_value = float(lon) % 360.0

    lat_floor = math.floor(lat_value)
    lat_ceil = math.ceil(lat_value)
    lon_floor = math.floor(lon_value) % 360
    lon_ceil = math.ceil(lon_value) % 360

    candidates = []
    for glat in {int(lat_floor), int(lat_ceil)}:
        for glon in {int(lon_floor), int(lon_ceil)}:
            value = grid.get((glon, glat))
            if value is None:
                continue
            # Longitude degrees shrink with latitude.  This is sufficient for
            # selecting among the four neighbouring 1-degree OVATION cells.
            lon_scale = max(0.05, math.cos(math.radians(lat_value)))
            dlat = float(glat) - lat_value
            dlon = abs(float(glon) - lon_value)
            dlon = min(dlon, 360.0 - dlon)
            dist2 = dlat * dlat + (dlon * lon_scale) ** 2
            candidates.append((dist2, glon, glat, float(value)))

    if not candidates:
        return None
    _, glon, glat, value = min(candidates, key=lambda row: row[0])
    return {"grid_lon": glon, "grid_lat": glat, "aurora_value": value}


def sample_aurora_for_timestamp(indexed, lat, lon, timestamp):
    """Return the local OVATION sample only near the product's forecast time."""
    if not indexed:
        return None

    forecast_time = indexed.get("forecast_time")
    observation_time = indexed.get("observation_time")
    if forecast_time is None or observation_time is None:
        return {
            "available": False,
            "reason": "ovation_time_metadata_missing",
            "provider": indexed.get("provider"),
            "provider_version": indexed.get("provider_version"),
        }

    target = datetime.fromtimestamp(int(timestamp), timezone.utc)
    delta_minutes = abs((target - forecast_time).total_seconds()) / 60.0

    base = {
        "provider": indexed.get("provider"),
        "provider_version": indexed.get("provider_version"),
        "observation_time": observation_time.isoformat().replace("+00:00", "Z"),
        "forecast_time": forecast_time.isoformat().replace("+00:00", "Z"),
        "target_time": target.isoformat().replace("+00:00", "Z"),
        "forecast_delta_minutes": round(delta_minutes, 1),
        "valid_window_minutes": VALID_WINDOW_MINUTES,
        "kp_fallback_used": False,
    }

    if delta_minutes > VALID_WINDOW_MINUTES:
        return {
            **base,
            "available": False,
            "reason": "outside_ovation_forecast_window",
        }

    local = _nearest_grid_value(indexed, lat, lon)
    if local is None:
        return {
            **base,
            "available": False,
            "reason": "ovation_local_grid_missing",
        }

    return {
        **base,
        **local,
        "available": True,
        "reason": "ovation_local_grid_sample",
    }


def spot_requires_aurora_state(spot):
    for opportunity in (spot or {}).get("opportunities", []) or []:
        if "aurora_state" in dependencies_for_opportunity(opportunity):
            return True
    return False


def validate_aurora_state_provider():
    errors = []
    if not PROVIDER_URLS or not all(str(url).startswith("https://") for url in PROVIDER_URLS):
        errors.append("aurora provider URLs must be HTTPS")
    if VALID_WINDOW_MINUTES < 30 or VALID_WINDOW_MINUTES > 120:
        errors.append("aurora valid window must stay within conservative short-horizon bounds")
    if not 0 < MIN_LOCAL_AURORA_VALUE <= 100:
        errors.append("invalid local aurora threshold")
    return errors


_ERRORS = validate_aurora_state_provider()
if _ERRORS:
    raise ValueError("Invalid aurora_state provider: " + "; ".join(_ERRORS))
