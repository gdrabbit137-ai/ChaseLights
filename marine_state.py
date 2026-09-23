"""Marine-state preview support for ChaseLights R4.2.

This module consumes coarse-grid wave-model output. It can flag elevated model-
scale marine energy, but it must never claim that a local shoreline is safe.
Tide remains a separate runtime dependency and is intentionally not evaluated
here.
"""

MARINE_STATE_VERSION = "marine-state-r1-preview"

MARINE_STATE_PROFILES = {
    "tw-010-P01": {"exposure": "controlled_rocky_coast"},
    "tw-010-P02": {"exposure": "managed_rocky_coast"},
    "tw-010-P03": {"exposure": "managed_rocky_coast"},
    "tw-033-P01": {"exposure": "exposed_beach_breakwater"},
    "tw-033-P02": {"exposure": "exposed_beach"},
    "tw-036-P01": {"exposure": "exposed_cobble_beach"},
    "tw-036-P02": {"exposure": "exposed_cobble_beach_night"},
    "tw-071-P01": {"exposure": "reef_coast"},
    "tw-071-P02": {"exposure": "reef_coast"},
    "tw-072-P01": {"exposure": "exposed_rocky_coast"},
    "tw-072-P02": {"exposure": "exposed_rocky_coast"},
    "tw-073-P01": {"exposure": "intertidal_rocky_coast"},
    "tw-075-P01": {"exposure": "exposed_sandy_coast"},
    "tw-077-P01": {"exposure": "exposed_rock_platform"},
    "tw-077-P02": {"exposure": "intertidal_rock_platform"},
    "tw-079-P01": {"exposure": "exposed_basalt_coast"},
    "tw-079-P02": {"exposure": "intertidal_basalt_pools"},
}


def supports_marine_state(opportunity):
    return opportunity.get("opportunity_id") in MARINE_STATE_PROFILES


def spot_requires_marine_state(spot):
    return any(
        supports_marine_state(opportunity)
        for opportunity in (spot.get("opportunities", []) or [])
    )


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def index_marine_response(raw):
    """Index an Open-Meteo Marine response by UNIX timestamp."""
    if not isinstance(raw, dict):
        return {}
    hourly = raw.get("hourly", {}) or {}
    times = hourly.get("time", []) or []
    fields = (
        "wave_height",
        "wave_direction",
        "wave_period",
        "wind_wave_height",
        "wind_wave_direction",
        "wind_wave_period",
        "swell_wave_height",
        "swell_wave_direction",
        "swell_wave_period",
        "swell_wave_peak_period",
    )
    result = {}
    for i, ts in enumerate(times):
        try:
            timestamp = int(ts)
        except (TypeError, ValueError):
            continue
        row = {
            "source_grid_lat": raw.get("latitude"),
            "source_grid_lon": raw.get("longitude"),
            "source_grid_elevation": raw.get("elevation"),
        }
        for field in fields:
            values = hourly.get(field, []) or []
            row[field] = values[i] if i < len(values) else None
        result[timestamp] = row
    return result


def marine_sample_for_timestamp(indexed, timestamp, max_offset_seconds=5400):
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


def evaluate_marine_state(opportunity, item_data):
    """Evaluate coarse model-scale wave exposure, not local shoreline safety."""
    oid = opportunity.get("opportunity_id")
    config = MARINE_STATE_PROFILES.get(oid)
    if not config:
        return {
            "module": "marine_state",
            "available": False,
            "eligible": False,
            "reason": "opportunity_marine_config_missing",
            "local_shore_safety_verified": False,
        }

    marine = item_data.get("marine_forecast")
    if not isinstance(marine, dict):
        return {
            "module": "marine_state",
            "available": False,
            "eligible": False,
            "reason": "marine_forecast_missing",
            "local_shore_safety_verified": False,
        }

    wave = _number(marine.get("wave_height"))
    swell = _number(marine.get("swell_wave_height"))
    swell_period = _number(marine.get("swell_wave_period"))
    wave_period = _number(marine.get("wave_period"))
    wind_wave = _number(marine.get("wind_wave_height"))

    if wave is None and swell is None:
        return {
            "module": "marine_state",
            "available": False,
            "eligible": False,
            "reason": "wave_height_missing",
            "local_shore_safety_verified": False,
        }

    wave = 0.0 if wave is None else max(0.0, wave)
    swell = 0.0 if swell is None else max(0.0, swell)
    wind_wave = 0.0 if wind_wave is None else max(0.0, wind_wave)

    long_period_energy = (
        swell_period is not None and swell_period >= 10.0 and swell >= 0.8
    )
    very_long_period_energy = (
        swell_period is not None and swell_period >= 12.0 and swell >= 1.0
    )

    if wave >= 2.0 or swell >= 1.5 or very_long_period_energy:
        state, eligible, reason = "high_energy", False, "high_energy_marine_state"
    elif wave >= 1.3 or swell >= 1.0 or wind_wave >= 1.1 or long_period_energy:
        state, eligible, reason = "elevated", False, "elevated_marine_state"
    elif wave >= 0.7 or swell >= 0.5 or wind_wave >= 0.5:
        state, eligible, reason = "moderate", True, "marine_state_not_elevated"
    else:
        state, eligible, reason = "calm", True, "marine_state_not_elevated"

    return {
        "module": "marine_state",
        "available": True,
        "eligible": eligible,
        "reason": reason,
        "state": state,
        "exposure": config["exposure"],
        "wave_height_m": round(wave, 2),
        "wave_period_s": None if wave_period is None else round(wave_period, 1),
        "wave_direction_deg": _number(marine.get("wave_direction")),
        "wind_wave_height_m": round(wind_wave, 2),
        "wind_wave_period_s": None if _number(marine.get("wind_wave_period")) is None else round(_number(marine.get("wind_wave_period")), 1),
        "swell_wave_height_m": round(swell, 2),
        "swell_wave_period_s": None if swell_period is None else round(swell_period, 1),
        "swell_wave_peak_period_s": None if _number(marine.get("swell_wave_peak_period")) is None else round(_number(marine.get("swell_wave_peak_period")), 1),
        "swell_wave_direction_deg": _number(marine.get("swell_wave_direction")),
        "sample_offset_seconds": marine.get("sample_offset_seconds"),
        "model_grid_resolution_note": "coarse_marine_grid_local_shore_effects_unresolved",
        "tide_evaluated": False,
        "local_shore_safety_verified": False,
        "safety_note": "Model-scale marine diagnostic only; verify local warnings, access and shoreline conditions.",
        "confidence_hint": "medium" if eligible else "medium_low",
    }


def validate_marine_state_registry():
    errors = []
    expected = {
        "tw-010-P01", "tw-010-P02", "tw-010-P03",
        "tw-033-P01", "tw-033-P02",
        "tw-036-P01", "tw-036-P02",
        "tw-071-P01", "tw-071-P02",
        "tw-072-P01", "tw-072-P02", "tw-073-P01",
        "tw-075-P01",
        "tw-077-P01", "tw-077-P02",
        "tw-079-P01", "tw-079-P02",
    }
    if set(MARINE_STATE_PROFILES) != expected:
        errors.append(f"marine profile registry mismatch: {sorted(MARINE_STATE_PROFILES)}")
    return errors


_ERRORS = validate_marine_state_registry()
if _ERRORS:
    raise ValueError("Invalid marine-state registry: " + "; ".join(_ERRORS))
