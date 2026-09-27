"""Location-aware aurora-state preview support for ChaseLights R4.2.

The canonical aurora gate uses NOAA SWPC OVATION grid output for a specific
Camera Zone. Planetary Kp remains legacy/context data and is never accepted as
proof that aurora is locally photographable.

OVATION is a short-horizon model. A sample is only attached to the nearest
hourly weather row when that row is close to NOAA's published Forecast Time.
Stale, malformed, geographically missing, or out-of-horizon data fails closed.

This module evaluates photographic opportunity conditions, not a guarantee that
a human observer or camera will see aurora.
"""

from datetime import datetime, timezone


AURORA_STATE_VERSION = "aurora-state-r1-ovation-nowcast-preview"

# All canonical Opportunities that currently require aurora_state.  Keeping the
# registry explicit prevents legacy Place/theme tags from silently enabling the
# component for new content.
AURORA_STATE_PROFILES = {
    "us-041-P02": {"min_ovation_value": 5.0},
    "us-042-P01": {"min_ovation_value": 5.0},
    "us-043-P01": {"min_ovation_value": 5.0},
    "us-044-P02": {"min_ovation_value": 5.0},
    "us-046-P02": {"min_ovation_value": 5.0},
    "us-056-P02": {"min_ovation_value": 5.0},
    "us-057-P02": {"min_ovation_value": 5.0},
    "us-058-P02": {"min_ovation_value": 5.0},
    "us-065-P02": {"min_ovation_value": 5.0},
    "us-066-P02": {"min_ovation_value": 5.0},
    "us-068-P02": {"min_ovation_value": 5.0},
    "us-069-P02": {"min_ovation_value": 5.0},
}

NOAA_OVATION_URL = "https://services.swpc.noaa.gov/json/ovation_aurora_latest.json"
MAX_TARGET_OFFSET_SECONDS = 45 * 60
MAX_PROVIDER_AGE_SECONDS = 2 * 3600
MAX_PROVIDER_LEAD_SECONDS = 2 * 3600
MAX_SUN_ELEVATION_DEG = -12.0
MAX_LOW_CLOUD = 50.0
MAX_MID_CLOUD = 65.0
MAX_HIGH_CLOUD = 80.0


def supports_aurora_state(opportunity):
    return opportunity.get("opportunity_id") in AURORA_STATE_PROFILES


def spot_requires_aurora_state(spot):
    return any(
        supports_aurora_state(opportunity)
        for opportunity in (spot.get("opportunities", []) or [])
    )


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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
    else:
        dt = dt.astimezone(timezone.utc)
    return dt


def parse_ovation_payload(raw, retrieved_at=None):
    """Parse NOAA's latest OVATION JSON into a one-degree lookup grid.

    The returned structure is an internal provider snapshot. It is intentionally
    not emitted directly into weather JSON because the global grid is large.
    """
    if not isinstance(raw, dict):
        raise ValueError("OVATION payload must be an object")

    observation = _parse_utc(raw.get("Observation Time"))
    forecast = _parse_utc(raw.get("Forecast Time"))
    if observation is None or forecast is None:
        raise ValueError("OVATION payload missing valid Observation/Forecast Time")

    data_format = str(raw.get("Data Format") or "")
    if "Longitude" not in data_format or "Latitude" not in data_format:
        raise ValueError("OVATION payload has unexpected Data Format")

    coordinates = raw.get("coordinates")
    if not isinstance(coordinates, list) or not coordinates:
        raise ValueError("OVATION payload has no coordinates")

    grid = {}
    for row in coordinates:
        if not isinstance(row, (list, tuple)) or len(row) < 3:
            continue
        lon = _number(row[0])
        lat = _number(row[1])
        value = _number(row[2])
        if lon is None or lat is None or value is None:
            continue
        if not -90.0 <= lat <= 90.0:
            continue
        lon_key = int(round(lon)) % 360
        lat_key = int(round(lat))
        grid[(lon_key, lat_key)] = max(0.0, float(value))

    if not grid:
        raise ValueError("OVATION payload has no usable grid cells")

    retrieved = retrieved_at or datetime.now(timezone.utc)
    if retrieved.tzinfo is None:
        retrieved = retrieved.replace(tzinfo=timezone.utc)
    else:
        retrieved = retrieved.astimezone(timezone.utc)

    return {
        "source": "NOAA SWPC OVATION 2020",
        "source_url": NOAA_OVATION_URL,
        "observation_time_utc": int(observation.timestamp()),
        "forecast_time_utc": int(forecast.timestamp()),
        "retrieved_time_utc": int(retrieved.timestamp()),
        "grid_resolution_deg": 1,
        "grid": grid,
    }


def _nearest_grid_value(grid, lat, lon):
    lat = _number(lat)
    lon = _number(lon)
    if lat is None or lon is None or not -90.0 <= lat <= 90.0:
        return None

    target_lon = lon % 360.0
    base_lon = int(round(target_lon)) % 360
    base_lat = max(-90, min(90, int(round(lat))))

    best = None
    for dlat in (-1, 0, 1):
        sample_lat = base_lat + dlat
        if not -90 <= sample_lat <= 90:
            continue
        for dlon in (-1, 0, 1):
            sample_lon = (base_lon + dlon) % 360
            value = grid.get((sample_lon, sample_lat))
            if value is None:
                continue
            lon_delta = abs(sample_lon - target_lon)
            lon_delta = min(lon_delta, 360.0 - lon_delta)
            distance2 = (sample_lat - lat) ** 2 + lon_delta ** 2
            candidate = (distance2, sample_lon, sample_lat, float(value))
            if best is None or candidate < best:
                best = candidate
    if best is None:
        return None
    _, sample_lon, sample_lat, value = best
    display_lon = float(sample_lon if sample_lon <= 180 else sample_lon - 360)
    return {
        "grid_lat": float(sample_lat),
        "grid_lon": display_lon,
        "ovation_value": value,
    }


def sample_ovation_for_location(
    snapshot,
    lat,
    lon,
    target_timestamp,
    max_target_offset_seconds=MAX_TARGET_OFFSET_SECONDS,
):
    """Return a local OVATION sample only inside the provider's short horizon."""
    if not isinstance(snapshot, dict) or not snapshot.get("grid"):
        return None
    try:
        target_ts = int(target_timestamp)
        forecast_ts = int(snapshot["forecast_time_utc"])
        retrieved_ts = int(snapshot["retrieved_time_utc"])
    except (KeyError, TypeError, ValueError):
        return None

    # Fail closed when a cached/provider response is stale or implausibly far
    # ahead of the retrieval time.
    provider_age = retrieved_ts - forecast_ts
    if provider_age > MAX_PROVIDER_AGE_SECONDS:
        return None
    if forecast_ts - retrieved_ts > MAX_PROVIDER_LEAD_SECONDS:
        return None

    offset = abs(target_ts - forecast_ts)
    if offset > int(max_target_offset_seconds):
        return None

    local = _nearest_grid_value(snapshot["grid"], lat, lon)
    if local is None:
        return None
    return {
        "source": snapshot.get("source"),
        "source_url": snapshot.get("source_url"),
        "observation_time_utc": snapshot.get("observation_time_utc"),
        "forecast_time_utc": forecast_ts,
        "target_offset_seconds": int(offset),
        "grid_resolution_deg": snapshot.get("grid_resolution_deg", 1),
        **local,
        "visibility_guaranteed": False,
    }


def _field_available(item_data, key):
    flag = item_data.get(f"{key}_available")
    if flag is not None:
        return bool(flag)
    return _number(item_data.get(key)) is not None


def evaluate_aurora_state(opportunity, item_data):
    """Evaluate local OVATION signal + darkness + local forecast cloud cover."""
    oid = opportunity.get("opportunity_id")
    config = AURORA_STATE_PROFILES.get(oid)
    if not config:
        return {
            "module": "aurora_state",
            "available": False,
            "eligible": False,
            "reason": "opportunity_aurora_config_missing",
            "visibility_guaranteed": False,
        }

    sample = item_data.get("aurora_forecast")
    if not isinstance(sample, dict):
        return {
            "module": "aurora_state",
            "available": False,
            "eligible": False,
            "reason": "local_ovation_forecast_unavailable_or_out_of_horizon",
            "visibility_guaranteed": False,
        }

    value = _number(sample.get("ovation_value"))
    if value is None:
        return {
            "module": "aurora_state",
            "available": False,
            "eligible": False,
            "reason": "local_ovation_value_missing",
            "visibility_guaranteed": False,
        }

    if not item_data.get("astronomy_valid"):
        return {
            "module": "aurora_state",
            "available": False,
            "eligible": False,
            "reason": "solar_geometry_missing",
            "ovation_value": round(value, 1),
            "visibility_guaranteed": False,
        }

    sun_elevation = _number(item_data.get("sun_elevation"))
    if sun_elevation is None:
        return {
            "module": "aurora_state",
            "available": False,
            "eligible": False,
            "reason": "sun_elevation_missing",
            "ovation_value": round(value, 1),
            "visibility_guaranteed": False,
        }

    cloud_keys = ("c_low", "c_mid", "c_high")
    if not all(_field_available(item_data, key) for key in cloud_keys):
        return {
            "module": "aurora_state",
            "available": False,
            "eligible": False,
            "reason": "local_cloud_forecast_missing",
            "ovation_value": round(value, 1),
            "visibility_guaranteed": False,
        }

    low = max(0.0, min(100.0, _number(item_data.get("c_low")) or 0.0))
    mid = max(0.0, min(100.0, _number(item_data.get("c_mid")) or 0.0))
    high = max(0.0, min(100.0, _number(item_data.get("c_high")) or 0.0))
    minimum = float(config.get("min_ovation_value", 5.0))

    if sun_elevation > MAX_SUN_ELEVATION_DEG:
        eligible, reason = False, "insufficient_darkness"
    elif value < minimum:
        eligible, reason = False, "local_ovation_signal_below_threshold"
    elif low > MAX_LOW_CLOUD or mid > MAX_MID_CLOUD or high > MAX_HIGH_CLOUD:
        eligible, reason = False, "local_cloud_obstruction_too_high"
    else:
        eligible, reason = True, "local_ovation_dark_sky_weather_match"

    if value >= 30:
        signal = "strong"
    elif value >= 15:
        signal = "elevated"
    elif value >= minimum:
        signal = "usable_model_signal"
    else:
        signal = "weak"

    confidence = "medium"
    if eligible and value >= 15 and low <= 25 and mid <= 35 and high <= 50:
        confidence = "medium_high"
    elif not eligible:
        confidence = "medium_low"

    return {
        "module": "aurora_state",
        "available": True,
        "eligible": eligible,
        "reason": reason,
        "provider": sample.get("source"),
        "provider_forecast_time_utc": sample.get("forecast_time_utc"),
        "provider_observation_time_utc": sample.get("observation_time_utc"),
        "target_offset_seconds": sample.get("target_offset_seconds"),
        "grid_lat": sample.get("grid_lat"),
        "grid_lon": sample.get("grid_lon"),
        "grid_resolution_deg": sample.get("grid_resolution_deg"),
        "ovation_value": round(value, 1),
        "signal_class": signal,
        "minimum_ovation_value": minimum,
        "sun_elevation_deg": round(sun_elevation, 1),
        "cloud_low": round(low),
        "cloud_mid": round(mid),
        "cloud_high": round(high),
        "forecast_scope": "NOAA_OVATION_short_horizon_location_signal",
        "visibility_guaranteed": False,
        "confidence_hint": confidence,
        "safety_note": "Aurora is probabilistic; local terrain, haze, light pollution and rapid space-weather changes can still prevent visibility.",
    }


def validate_aurora_state_registry():
    errors = []
    for oid, config in AURORA_STATE_PROFILES.items():
        if not str(oid).startswith(("tw-", "jp-", "us-")):
            errors.append(f"{oid}: invalid Opportunity id")
        threshold = _number(config.get("min_ovation_value"))
        if threshold is None or not 0.0 <= threshold <= 100.0:
            errors.append(f"{oid}: invalid OVATION threshold")
    return errors


_ERRORS = validate_aurora_state_registry()
if _ERRORS:
    raise ValueError("Invalid aurora-state registry: " + "; ".join(_ERRORS))
