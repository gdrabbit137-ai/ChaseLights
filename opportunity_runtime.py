"""Preview composable runtime modules for R4.2 Opportunities.

Implemented preview components:
- directional_horizon: broad sunrise/sunset sectors; never exact alignment.
- visibility: horizontal forecast visibility diagnostic.
- water_surface_state: conservative reflection/calm-water diagnostic from wind
  and precipitation probability.

A profile is preview_module_available only when every dependency in the formal
runtime dependency inventory is implemented and configured for that Opportunity.
This is not production formula certification.
"""

from runtime_dependencies import (
    FORMULA_DEPENDENCIES,
    dependencies_for_opportunity,
    validate_dependency_inventory,
)

MODULE_VERSION = "opportunity-runtime-r3-preview"

IMPLEMENTED_COMPONENTS = {
    "directional_horizon",
    "visibility",
    "water_surface_state",
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
    "tw-051-P01": {"center": 270.0, "tolerance": 75.0, "phase": "sunset"},
    "tw-061-P01": {"center": 270.0, "tolerance": 75.0, "phase": "sunset"},
    "tw-065-P01": {"center": 247.5, "tolerance": 67.5, "phase": "sunset"},
    "tw-067-P01": {"center": 270.0, "tolerance": 75.0, "phase": "sunset"},
    "tw-070-P01": {"center": 247.5, "tolerance": 67.5, "phase": "sunset"},
}


def _angle_diff(a, b):
    return abs((float(a) - float(b) + 180.0) % 360.0 - 180.0)


def component_ready_for_opportunity(component, opportunity):
    if component not in IMPLEMENTED_COMPONENTS:
        return False
    if component == "directional_horizon":
        return opportunity.get("opportunity_id") in DIRECTIONAL_HORIZON_SECTORS
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
    """Conservative calm/reflection signal from existing trustworthy inputs.

    Wind is the primary surface-state proxy. Precipitation probability is used
    only as a risk modifier; this module does not infer tide, lake level, swell,
    or actual rainfall from ordinary weather fields.
    """
    wind = item_data.get("wind")
    pop = item_data.get("pop")
    if wind is None or pop is None:
        return {
            "module": "water_surface_state",
            "available": False,
            "eligible": False,
            "reason": "wind_or_precipitation_probability_missing",
        }

    wind = max(0.0, float(wind))
    pop = max(0.0, min(100.0, float(pop)))

    if wind <= 2.0 and pop <= 40.0:
        quality, eligible, reason = "mirror_candidate", True, "surface_very_calm"
    elif wind <= 4.0 and pop <= 50.0:
        quality, eligible, reason = "reflection_usable", True, "surface_calm_enough"
    elif wind > 4.0:
        quality, eligible, reason = "rough", False, "wind_too_strong"
    else:
        quality, eligible, reason = "rain_risk", False, "precipitation_risk"

    return {
        "module": "water_surface_state",
        "available": True,
        "eligible": eligible,
        "reason": reason,
        "quality": quality,
        "wind_mps": round(wind, 1),
        "precipitation_probability": round(pop),
    }


_COMPONENT_EVALUATORS = {
    "directional_horizon": evaluate_directional_horizon,
    "visibility": lambda opportunity, item_data: evaluate_visibility(item_data),
    "water_surface_state": lambda opportunity, item_data: evaluate_water_surface(item_data),
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
    if len(DIRECTIONAL_HORIZON_SECTORS) != 20:
        errors.append(
            f"expected 20 registered directional profiles, got {len(DIRECTIONAL_HORIZON_SECTORS)}"
        )
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
