"""Relative tide-state preview support for ChaseLights R4.2.

The provider variable is sea_level_height_msl. Because its datum is global mean
sea level and coastal accuracy is limited, ChaseLights never treats the absolute
meter value as a local chart-datum tide height. Instead each forecast window is
normalized into a local percentile and trend.

This module is independent from marine_state, water_surface_state and access.
"""

TIDE_STATE_VERSION = "tide-state-r1-preview"

TIDE_STATE_PROFILES = {
    "tw-010-P01": {"mode": "low_access_window"},
    "tw-012-P01": {"mode": "intertidal_layers"},
    "tw-012-P02": {"mode": "shallow_reflection"},
    "tw-015-P01": {"mode": "intertidal_layers"},
    "tw-015-P02": {"mode": "shallow_reflection"},
    "tw-017-P02": {"mode": "intertidal_layers"},
    "tw-059-P01": {"mode": "low_exposure_strict"},
    "tw-060-P01": {"mode": "low_exposure"},
    "tw-060-P02": {"mode": "low_exposure"},
    "tw-060-P03": {"mode": "low_exposure"},
    "tw-073-P01": {"mode": "low_exposure_strict"},
    "tw-077-P02": {"mode": "intertidal_layers"},
    "tw-078-P01": {"mode": "low_access_window"},
    "tw-078-P02": {"mode": "low_access_window"},
    "tw-079-P02": {"mode": "low_exposure"},
}


def supports_tide_state(opportunity):
    return opportunity.get("opportunity_id") in TIDE_STATE_PROFILES


def spot_requires_tide_state(spot):
    return any(
        supports_tide_state(opportunity)
        for opportunity in (spot.get("opportunities", []) or [])
    )


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def index_tide_response(raw):
    """Index relative sea-level state and derive within-window percentile/trend."""
    if not isinstance(raw, dict):
        return {}
    hourly = raw.get("hourly", {}) or {}
    times = hourly.get("time", []) or []
    values = hourly.get("sea_level_height_msl", []) or []

    valid_levels = [
        float(value) for value in values
        if value is not None
    ]
    if not valid_levels:
        return {}

    sorted_levels = sorted(valid_levels)
    n = len(sorted_levels)

    def percentile(level):
        # Mid-rank ECDF percentile; robust to repeated values and independent of datum.
        less = sum(1 for value in sorted_levels if value < level)
        equal = sum(1 for value in sorted_levels if value == level)
        return 100.0 * (less + 0.5 * equal) / n

    result = {}
    for i, ts in enumerate(times):
        if i >= len(values) or values[i] is None:
            continue
        try:
            timestamp = int(ts)
        except (TypeError, ValueError):
            continue
        level = float(values[i])

        prev_level = _number(values[i - 1]) if i > 0 else None
        next_level = _number(values[i + 1]) if i + 1 < len(values) else None
        if prev_level is not None and next_level is not None:
            trend_m_per_hour = (next_level - prev_level) / 2.0
        elif prev_level is not None:
            trend_m_per_hour = level - prev_level
        elif next_level is not None:
            trend_m_per_hour = next_level - level
        else:
            trend_m_per_hour = 0.0

        if trend_m_per_hour > 0.02:
            trend = "rising"
        elif trend_m_per_hour < -0.02:
            trend = "falling"
        else:
            trend = "near_stationary"

        result[timestamp] = {
            "sea_level_height_msl_m": level,
            "relative_percentile": percentile(level),
            "trend": trend,
            "trend_m_per_hour": trend_m_per_hour,
            "window_min_m": min(sorted_levels),
            "window_max_m": max(sorted_levels),
            "window_sample_count": n,
            "source_grid_lat": raw.get("latitude"),
            "source_grid_lon": raw.get("longitude"),
            "datum_note": "global_mean_sea_level_not_local_chart_datum",
        }
    return result


def tide_sample_for_timestamp(indexed, timestamp, max_offset_seconds=5400):
    if not indexed:
        return None
    timestamp = int(timestamp)
    if timestamp in indexed:
        return dict(indexed[timestamp], sample_time_utc=timestamp, sample_offset_seconds=0)
    nearest = min(indexed, key=lambda ts: abs(int(ts) - timestamp))
    offset = abs(int(nearest) - timestamp)
    if offset > int(max_offset_seconds):
        return None
    return dict(
        indexed[nearest],
        sample_time_utc=int(nearest),
        sample_offset_seconds=int(offset),
    )


def evaluate_tide_state(opportunity, item_data):
    oid = opportunity.get("opportunity_id")
    config = TIDE_STATE_PROFILES.get(oid)
    if not config:
        return {
            "module": "tide_state",
            "available": False,
            "eligible": False,
            "reason": "opportunity_tide_config_missing",
        }

    tide = item_data.get("tide_forecast")
    if not isinstance(tide, dict):
        return {
            "module": "tide_state",
            "available": False,
            "eligible": False,
            "reason": "tide_forecast_missing",
        }

    percentile = _number(tide.get("relative_percentile"))
    trend = tide.get("trend")
    if percentile is None:
        return {
            "module": "tide_state",
            "available": False,
            "eligible": False,
            "reason": "relative_tide_percentile_missing",
        }

    mode = config["mode"]
    if mode == "low_exposure_strict":
        eligible = percentile <= 30.0
        reason = "strict_low_tide_window" if eligible else "water_too_high_for_strict_exposure"
    elif mode == "low_exposure":
        eligible = percentile <= 40.0
        reason = "low_tide_exposure_window" if eligible else "water_too_high_for_exposure"
    elif mode == "low_access_window":
        eligible = percentile <= 45.0
        reason = "low_tide_access_window" if eligible else "water_too_high_for_access_window"
    elif mode == "shallow_reflection":
        eligible = 12.0 <= percentile <= 50.0
        reason = "shallow_reflection_tide_window" if eligible else (
            "too_low_for_reflective_water_film" if percentile < 12.0
            else "water_too_high_for_reflection_pattern"
        )
    elif mode == "intertidal_layers":
        eligible = 8.0 <= percentile <= 65.0
        reason = "intertidal_layers_window" if eligible else (
            "too_low_for_water_mudflat_layering" if percentile < 8.0
            else "water_too_high_for_intertidal_texture"
        )
    else:
        return {
            "module": "tide_state",
            "available": False,
            "eligible": False,
            "reason": "unsupported_tide_mode",
        }

    return {
        "module": "tide_state",
        "available": True,
        "eligible": eligible,
        "reason": reason,
        "mode": mode,
        "relative_percentile": round(percentile, 1),
        "trend": trend,
        "trend_m_per_hour": None if _number(tide.get("trend_m_per_hour")) is None else round(float(tide["trend_m_per_hour"]), 3),
        "sea_level_height_msl_m": _number(tide.get("sea_level_height_msl_m")),
        "datum_note": "global_mean_sea_level_not_local_chart_datum",
        "absolute_local_tide_height_verified": False,
        "local_shore_safety_verified": False,
        "marine_state_evaluated": False,
        "confidence_hint": "medium",
    }


def validate_tide_state_registry():
    expected = {
        "tw-010-P01",
        "tw-012-P01", "tw-012-P02",
        "tw-015-P01", "tw-015-P02",
        "tw-017-P02",
        "tw-059-P01",
        "tw-060-P01", "tw-060-P02", "tw-060-P03",
        "tw-073-P01",
        "tw-077-P02",
        "tw-078-P01", "tw-078-P02",
        "tw-079-P02",
    }
    errors = []
    if set(TIDE_STATE_PROFILES) != expected:
        errors.append(f"tide profile registry mismatch: {sorted(TIDE_STATE_PROFILES)}")
    return errors


_ERRORS = validate_tide_state_registry()
if _ERRORS:
    raise ValueError("Invalid tide-state registry: " + "; ".join(_ERRORS))
