"""Preview composable runtime modules for R4.2 Opportunities.

Implemented preview components:
- directional_horizon: broad sunrise/sunset sectors; never exact alignment.
- visibility: horizontal forecast visibility diagnostic.
- water_surface_state: conservative reflection/calm-water diagnostic from wind,
  forecast precipitation amount, and precipitation-probability uncertainty.
- snow_state: separates instantaneous ground snow depth from preceding-hour
  snowfall; does not infer snow cover from air temperature and does not detect rime.
- radiation_DNI: direct-beam strength from hourly direct normal irradiance.
- cloud_light_state: broken-cloud/opening structure for direct-beam ray outcomes.
- cloud_sky_glow: opportunity-specific sunset/afterglow potential using solar
  geometry plus low/mid/high cloud structure; it predicts potential, not color.

A profile is preview_module_available only when every dependency in the formal
runtime dependency inventory is implemented and configured for that Opportunity.
This is not production formula certification.
"""

from runtime_dependencies import (
    FORMULA_DEPENDENCIES,
    dependencies_for_opportunity,
    validate_dependency_inventory,
)

MODULE_VERSION = "opportunity-runtime-r4-preview"

IMPLEMENTED_COMPONENTS = {
    "directional_horizon",
    "visibility",
    "water_surface_state",
    "snow_state",
    "radiation_DNI",
    "cloud_light_state",
    "cloud_sky_glow",
}

DIRECTIONAL_HORIZON_SECTORS = {
    "tw-001-P01": {"center": 247.5, "tolerance": 67.5, "phase": "sunset"},
    "tw-003-P01": {"center": 270.0, "tolerance": 70.0, "phase": "sunset"},
    "tw-004-P04": {"center": 270.0, "tolerance": 70.0, "phase": "sunset"},
    "tw-006-P02": {"center": 292.5, "tolerance": 67.5, "phase": "sunset"},
    "tw-009-P02": {"center": 247.5, "tolerance": 67.5, "phase": "sunset"},
    "tw-011-P01": {"center": 270.0, "tolerance": 70.0, "phase": "sunset"},
    "tw-020-P01": {"center": 90.0, "tolerance": 70.0, "phase": "sunrise"},
    "tw-022-P01": {"center": 270.0, "tolerance": 70.0, "phase": "sunset"},
    "tw-022-P04": {"center": 90.0, "tolerance": 70.0, "phase": "sunrise"},
    "tw-023-P01": {"center": 270.0, "tolerance": 70.0, "phase": "sunset"},
    "tw-024-P04": {"center": 270.0, "tolerance": 75.0, "phase": "sunset"},
    "tw-027-P03": {"center": 270.0, "tolerance": 75.0, "phase": "sunset"},
    "tw-028-P01": {"center": 270.0, "tolerance": 90.0, "phase": "sunset"},
    "tw-030-P01": {"center": 270.0, "tolerance": 70.0, "phase": "sunset"},
    "tw-035-P03": {"center": 270.0, "tolerance": 70.0, "phase": "sunset"},
    "tw-035-P04": {"center": 270.0, "tolerance": 75.0, "phase": "sunset"},
    "tw-051-P01": {"center": 270.0, "tolerance": 75.0, "phase": "sunset"},
    "tw-061-P01": {"center": 270.0, "tolerance": 75.0, "phase": "sunset"},
    "tw-065-P01": {"center": 247.5, "tolerance": 67.5, "phase": "sunset"},
    "tw-067-P01": {"center": 270.0, "tolerance": 75.0, "phase": "sunset"},
    "tw-070-P01": {"center": 247.5, "tolerance": 67.5, "phase": "sunset"},
}

CLOUD_SKY_GLOW_PROFILES = {
    "tw-013-P02": {"mode": "terrain_illumination", "target_center": 270.0, "target_tolerance": 85.0},
    "tw-026-P02": {"mode": "afterglow_sky", "target_center": 270.0, "target_tolerance": 85.0},
    "tw-030-P02": {"mode": "afterglow_sky", "target_center": 270.0, "target_tolerance": 85.0},
    "tw-035-P04": {"mode": "afterglow_sky", "target_center": 270.0, "target_tolerance": 85.0},
}


def _angle_diff(a, b):
    return abs((float(a) - float(b) + 180.0) % 360.0 - 180.0)


def component_ready_for_opportunity(component, opportunity):
    if component not in IMPLEMENTED_COMPONENTS:
        return False
    if component == "directional_horizon":
        return opportunity.get("opportunity_id") in DIRECTIONAL_HORIZON_SECTORS
    if component == "cloud_sky_glow":
        return opportunity.get("opportunity_id") in CLOUD_SKY_GLOW_PROFILES
    return True


def dependency_state(opportunity):
    required = dependencies_for_opportunity(opportunity)
    ready = tuple(
        component for component in required
        if component_ready_for_opportunity(component, opportunity)
    )
    missing = tuple(component for component in required if component not in ready)
    return {
        "required_components": required,
        "ready_components": ready,
        "missing_components": missing,
        "complete": bool(required) and not missing,
    }


def supports_directional_horizon(opportunity):
    return component_ready_for_opportunity("directional_horizon", opportunity)


def supports_runtime_contract(opportunity):
    status = str(opportunity.get("formula_status") or "")
    if not status.startswith("needs_"):
        return False
    return dependency_state(opportunity)["complete"]


# Backward-compatible helper name used by B16-r1.
supports_opportunity = supports_directional_horizon


def evaluate_directional_horizon(opportunity, item_data):
    oid = opportunity.get("opportunity_id")
    sector = DIRECTIONAL_HORIZON_SECTORS.get(oid)
    if not sector:
        return {
            "module": "directional_horizon",
            "available": False,
            "eligible": False,
            "reason": "opportunity_sector_not_configured",
        }
    if not item_data.get("astronomy_valid"):
        return {
            "module": "directional_horizon",
            "available": True,
            "eligible": False,
            "reason": "astronomy_unavailable",
        }

    sun_azimuth = item_data.get("sun_azimuth")
    sun_elevation = item_data.get("sun_elevation")
    if sun_azimuth is None or sun_elevation is None:
        return {
            "module": "directional_horizon",
            "available": True,
            "eligible": False,
            "reason": "solar_geometry_missing",
        }

    hour = item_data.get("hour")
    if hour is not None:
        hour = int(hour)
        if sector["phase"] == "sunrise" and hour >= 12:
            return {
                "module": "directional_horizon",
                "available": True,
                "eligible": False,
                "reason": "wrong_daypart",
            }
        if sector["phase"] == "sunset" and hour < 12:
            return {
                "module": "directional_horizon",
                "available": True,
                "eligible": False,
                "reason": "wrong_daypart",
            }

    elevation = float(sun_elevation)
    if not -12.0 <= elevation <= 10.0:
        return {
            "module": "directional_horizon",
            "available": True,
            "eligible": False,
            "reason": "outside_twilight_window",
            "sun_elevation": round(elevation, 1),
        }

    diff = _angle_diff(sun_azimuth, sector["center"])
    eligible = diff <= sector["tolerance"]
    return {
        "module": "directional_horizon",
        "available": True,
        "eligible": eligible,
        "reason": "sector_match" if eligible else "sector_miss",
        "phase": sector["phase"],
        "sector_center": sector["center"],
        "sector_tolerance": sector["tolerance"],
        "sun_azimuth": round(float(sun_azimuth), 1),
        "sun_elevation": round(elevation, 1),
        "angle_diff": round(diff, 1),
    }


def evaluate_visibility(item_data):
    if item_data.get("vis") is not None:
        km = float(item_data["vis"]) / 1000.0
    elif item_data.get("visibility") is not None:
        km = float(item_data["visibility"])
    else:
        return {
            "module": "visibility",
            "available": False,
            "eligible": False,
            "reason": "visibility_missing",
        }

    if km >= 20:
        quality, eligible = "good", True
    elif km >= 8:
        quality, eligible = "usable", True
    else:
        quality, eligible = "poor", False
    return {
        "module": "visibility",
        "available": True,
        "eligible": eligible,
        "reason": f"visibility_{quality}",
        "visibility_km": round(km, 1),
        "quality": quality,
    }


def evaluate_water_surface(item_data):
    """Conservative calm/reflection signal from forecast surface inputs.

    Wind is the primary surface-state proxy. Forecast precipitation amount is a
    hard disturbance signal when available. Precipitation probability is only
    uncertainty context; it is never treated as observed rain. This module does
    not infer tide, lake level, swell, or marine state.
    """
    wind = item_data.get("wind")
    if wind is None:
        return {
            "module": "water_surface_state",
            "available": False,
            "eligible": False,
            "reason": "wind_missing",
        }

    wind = max(0.0, float(wind))
    precip_raw = item_data.get("precipitation", item_data.get("precip"))
    precip = None if precip_raw is None else max(0.0, float(precip_raw))
    pop_raw = item_data.get("pop", item_data.get("precipitation_probability"))
    pop = None if pop_raw is None else max(0.0, min(100.0, float(pop_raw)))

    if precip is not None and precip >= 0.2:
        quality, eligible, reason = "rain_disturbed", False, "precipitation_disturbance"
    elif wind <= 1.5:
        quality, eligible, reason = "mirror_candidate", True, "surface_very_calm"
    elif wind <= 2.5:
        quality, eligible, reason = "reflection_usable", True, "surface_calm_enough"
    elif wind <= 4.0:
        quality, eligible, reason = "rippled", False, "surface_rippled"
    else:
        quality, eligible, reason = "rough", False, "wind_too_strong"

    confidence_hint = "high"
    if precip is None:
        confidence_hint = "medium"
    if pop is not None and pop >= 60:
        confidence_hint = "medium" if confidence_hint == "high" else "low"

    return {
        "module": "water_surface_state",
        "available": True,
        "eligible": eligible,
        "reason": reason,
        "quality": quality,
        "wind_mps": round(wind, 1),
        "precipitation_mm": None if precip is None else round(precip, 2),
        "precipitation_probability": None if pop is None else round(pop),
        "confidence_hint": confidence_hint,
    }

def evaluate_snow_state(item_data):
    """Evaluate modeled ground snow cover and fresh snowfall separately.

    Open-Meteo semantics used by ChaseLights:
    - snow_depth: instantaneous modeled snow depth on the ground, meters.
    - snowfall: snowfall amount of the preceding hour, centimeters.

    Air temperature is intentionally not used to invent ground snow. Rime/frost
    accretion is also not detected by this module.
    """
    depth_raw = item_data.get("snow_depth")
    snowfall_raw = item_data.get("snowfall")
    if depth_raw is None and snowfall_raw is None:
        return {
            "module": "snow_state",
            "available": False,
            "eligible": False,
            "reason": "snow_data_missing",
            "rime_evaluated": False,
        }

    depth_m = None if depth_raw is None else max(0.0, float(depth_raw))
    snowfall_cm = None if snowfall_raw is None else max(0.0, float(snowfall_raw))

    existing_cover = depth_m is not None and depth_m >= 0.01
    substantial_cover = depth_m is not None and depth_m >= 0.05
    fresh_snow = snowfall_cm is not None and snowfall_cm >= 0.5

    if existing_cover and fresh_snow:
        state, eligible, reason = "fresh_snow_on_cover", True, "fresh_snow_with_ground_cover"
    elif substantial_cover:
        state, eligible, reason = "established_snow_cover", True, "ground_snow_cover"
    elif existing_cover:
        state, eligible, reason = "snow_cover", True, "ground_snow_cover"
    elif fresh_snow:
        state, eligible, reason = "fresh_snowfall", True, "fresh_snowfall_without_confirmed_depth"
    elif snowfall_cm is not None and snowfall_cm > 0:
        state, eligible, reason = "trace_snowfall", False, "snowfall_below_visible_cover_threshold"
    else:
        state, eligible, reason = "no_meaningful_snow", False, "no_meaningful_snow_cover_or_fresh_snow"

    return {
        "module": "snow_state",
        "available": True,
        "eligible": eligible,
        "reason": reason,
        "state": state,
        "snow_depth_m": None if depth_m is None else round(depth_m, 3),
        "snowfall_cm": None if snowfall_cm is None else round(snowfall_cm, 2),
        "existing_snow_cover": bool(existing_cover),
        "fresh_snowfall": bool(fresh_snow),
        "rime_evaluated": False,
        "confidence_hint": "medium",
    }


def evaluate_radiation_dni(item_data):
    """Evaluate hourly direct-beam strength from direct normal irradiance.

    Open-Meteo direct_normal_irradiance is an hourly mean in W/m². This preview
    signal is intentionally a direct-light availability diagnostic, not a
    photographic quality score.
    """
    raw = item_data.get("direct_normal_irradiance", item_data.get("dni"))
    if raw is None:
        return {
            "module": "radiation_DNI",
            "available": False,
            "eligible": False,
            "reason": "dni_missing",
        }

    dni = max(0.0, float(raw))
    if dni >= 250:
        quality, eligible, reason = "strong", True, "strong_direct_beam"
    elif dni >= 100:
        quality, eligible, reason = "usable", True, "usable_direct_beam"
    elif dni >= 40:
        quality, eligible, reason = "weak", False, "weak_direct_beam"
    else:
        quality, eligible, reason = "minimal", False, "minimal_direct_beam"

    return {
        "module": "radiation_DNI",
        "available": True,
        "eligible": eligible,
        "reason": reason,
        "quality": quality,
        "direct_normal_irradiance_wm2": round(dni, 1),
    }


def evaluate_cloud_light_state(item_data):
    """Approximate broken-cloud structure for visible direct-beam/ray scenes.

    This does not evaluate sunset afterglow or fire-cloud probability; those
    remain under the separate cloud_sky_glow dependency.
    """
    values = [item_data.get("c_low"), item_data.get("c_mid"), item_data.get("c_high")]
    if all(value is None for value in values):
        return {
            "module": "cloud_light_state",
            "available": False,
            "eligible": False,
            "reason": "cloud_layers_missing",
        }

    low = max(0.0, min(100.0, float(item_data.get("c_low") or 0.0)))
    mid = max(0.0, min(100.0, float(item_data.get("c_mid") or 0.0)))
    high = max(0.0, min(100.0, float(item_data.get("c_high") or 0.0)))
    pop_raw = item_data.get("pop")
    pop = None if pop_raw is None else max(0.0, min(100.0, float(pop_raw)))
    peak = max(low, mid, high)

    if low >= 90 or (mid >= 95 and high >= 95):
        structure, eligible, reason = "opaque", False, "cloud_too_opaque"
    elif peak < 15:
        structure, eligible, reason = "too_clear", False, "insufficient_cloud_contrast"
    elif peak <= 85:
        structure, eligible, reason = "broken", True, "broken_cloud_openings"
    else:
        structure, eligible, reason = "mostly_cloudy", False, "openings_too_limited"

    if eligible and pop is not None and pop >= 60:
        eligible, reason = False, "precipitation_risk"

    return {
        "module": "cloud_light_state",
        "available": True,
        "eligible": eligible,
        "reason": reason,
        "structure": structure,
        "cloud_low": round(low),
        "cloud_mid": round(mid),
        "cloud_high": round(high),
        "precipitation_probability": None if pop is None else round(pop),
    }


def evaluate_cloud_sky_glow(opportunity, item_data):
    """Estimate sunset/afterglow potential without claiming observed sky color.

    Point cloud-cover fields are not sector-resolved. Low cloud is therefore a
    horizon-obstruction proxy, while mid/high cloud is a texture/illumination
    proxy. The result is preview potential only.
    """
    oid = opportunity.get("opportunity_id")
    config = CLOUD_SKY_GLOW_PROFILES.get(oid)
    if not config:
        return {
            "module": "cloud_sky_glow",
            "available": False,
            "eligible": False,
            "reason": "opportunity_mode_not_configured",
        }

    if not item_data.get("astronomy_valid"):
        return {
            "module": "cloud_sky_glow",
            "available": True,
            "eligible": False,
            "reason": "astronomy_unavailable",
        }

    sun_alt = item_data.get("sun_elevation")
    sun_az = item_data.get("sun_azimuth")
    if sun_alt is None or sun_az is None:
        return {
            "module": "cloud_sky_glow",
            "available": True,
            "eligible": False,
            "reason": "solar_geometry_missing",
        }

    hour = item_data.get("hour")
    if hour is not None and int(hour) < 12:
        return {
            "module": "cloud_sky_glow",
            "available": True,
            "eligible": False,
            "reason": "wrong_daypart",
        }

    target_diff = _angle_diff(float(sun_az), config["target_center"])
    if target_diff > config["target_tolerance"]:
        return {
            "module": "cloud_sky_glow",
            "available": True,
            "eligible": False,
            "reason": "sun_outside_western_sector",
            "sun_azimuth": round(float(sun_az), 1),
            "angle_diff": round(target_diff, 1),
        }

    low_raw = item_data.get("c_low")
    mid_raw = item_data.get("c_mid")
    high_raw = item_data.get("c_high")
    if low_raw is None or mid_raw is None or high_raw is None:
        return {
            "module": "cloud_sky_glow",
            "available": False,
            "eligible": False,
            "reason": "cloud_layers_missing",
        }

    low = max(0.0, min(100.0, float(low_raw)))
    mid = max(0.0, min(100.0, float(mid_raw)))
    high = max(0.0, min(100.0, float(high_raw)))
    precip_raw = item_data.get("precipitation", item_data.get("precip"))
    precip = None if precip_raw is None else max(0.0, float(precip_raw))
    pop_raw = item_data.get("pop", item_data.get("precipitation_probability"))
    pop = None if pop_raw is None else max(0.0, min(100.0, float(pop_raw)))

    if precip is not None and precip >= 0.5:
        reason, eligible = "heavy_precipitation", False
    elif pop is not None and pop >= 80:
        reason, eligible = "high_precipitation_risk", False
    elif low >= 85:
        reason, eligible = "low_horizon_cloud_blocked", False
    else:
        mode = config["mode"]
        altitude = float(sun_alt)
        if mode == "terrain_illumination":
            if not 0.0 <= altitude <= 12.0:
                reason, eligible = "outside_low_angle_sun_window", False
            else:
                reason, eligible = "terrain_light_path_open", True
        else:
            if not -7.0 <= altitude <= 5.0:
                reason, eligible = "outside_sunset_civil_twilight_window", False
            elif low >= 70 and mid >= 85 and high >= 85:
                reason, eligible = "uniform_overcast", False
            elif max(mid, high) < 15:
                reason, eligible = "insufficient_mid_high_cloud_texture", False
            else:
                reason, eligible = "sky_glow_potential", True

    return {
        "module": "cloud_sky_glow",
        "available": True,
        "eligible": eligible,
        "reason": reason,
        "mode": config["mode"],
        "sun_azimuth": round(float(sun_az), 1),
        "sun_elevation": round(float(sun_alt), 1),
        "cloud_low": round(low),
        "cloud_mid": round(mid),
        "cloud_high": round(high),
        "precipitation_mm": None if precip is None else round(precip, 2),
        "precipitation_probability": None if pop is None else round(pop),
        "color_observed": False,
        "direction_resolution": "point_cloud_proxy_not_sector_resolved",
        "confidence_hint": "medium" if eligible else "low",
    }


_COMPONENT_EVALUATORS = {
    "directional_horizon": evaluate_directional_horizon,
    "visibility": lambda opportunity, item_data: evaluate_visibility(item_data),
    "water_surface_state": lambda opportunity, item_data: evaluate_water_surface(item_data),
    "snow_state": lambda opportunity, item_data: evaluate_snow_state(item_data),
    "radiation_DNI": lambda opportunity, item_data: evaluate_radiation_dni(item_data),
    "cloud_light_state": lambda opportunity, item_data: evaluate_cloud_light_state(item_data),
    "cloud_sky_glow": evaluate_cloud_sky_glow,
}


def evaluate_opportunity_modules(opportunity, item_data):
    state = dependency_state(opportunity)
    results = {}
    for component in state["ready_components"]:
        evaluator = _COMPONENT_EVALUATORS.get(component)
        if evaluator:
            results[component] = evaluator(opportunity, item_data)

    if not state["required_components"]:
        return {
            "module_version": MODULE_VERSION,
            "available": False,
            "eligible": False,
            "reason": "no_module_contract",
            **state,
            "modules": results,
        }

    if state["missing_components"]:
        return {
            "module_version": MODULE_VERSION,
            "available": False,
            "eligible": False,
            "reason": "runtime_contract_pending",
            **state,
            "modules": results,
        }

    available = all(result.get("available") for result in results.values())
    eligible = available and all(result.get("eligible") for result in results.values())
    return {
        "module_version": MODULE_VERSION,
        "available": available,
        "eligible": eligible,
        "reason": "all_modules_match" if eligible else (
            "module_condition_miss" if available else "module_data_missing"
        ),
        **state,
        "modules": results,
    }


def validate_runtime_registry():
    errors = list(validate_dependency_inventory())
    if len(DIRECTIONAL_HORIZON_SECTORS) != 21:
        errors.append(
            f"expected 21 registered directional profiles, got {len(DIRECTIONAL_HORIZON_SECTORS)}"
        )
    if set(CLOUD_SKY_GLOW_PROFILES) != {"tw-013-P02", "tw-026-P02", "tw-030-P02", "tw-035-P04"}:
        errors.append(f"unexpected cloud_sky_glow registry: {sorted(CLOUD_SKY_GLOW_PROFILES)}")
    for oid, sector in DIRECTIONAL_HORIZON_SECTORS.items():
        if not oid.startswith("tw-"):
            errors.append(f"{oid}: Taiwan Opportunity id expected")
        if not 0 <= float(sector["center"]) < 360:
            errors.append(f"{oid}: invalid center")
        if not 0 < float(sector["tolerance"]) <= 90:
            errors.append(f"{oid}: invalid tolerance")
        if sector["phase"] not in {"sunrise", "sunset"}:
            errors.append(f"{oid}: invalid phase")

    # Keep this explicit so adding a dependency does not silently mark it ready.
    evaluator_components = set(_COMPONENT_EVALUATORS)
    if evaluator_components != IMPLEMENTED_COMPONENTS:
        errors.append(
            f"implemented/evaluator mismatch: implemented={sorted(IMPLEMENTED_COMPONENTS)} "
            f"evaluators={sorted(evaluator_components)}"
        )
    return errors


validate_directional_horizon_registry = validate_runtime_registry

_REGISTRY_ERRORS = validate_runtime_registry()
if _REGISTRY_ERRORS:
    raise ValueError("Invalid Opportunity runtime registry: " + "; ".join(_REGISTRY_ERRORS))
