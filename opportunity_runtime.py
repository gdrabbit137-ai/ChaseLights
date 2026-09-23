"""Preview composable runtime modules for R4.2 Opportunities.

Implemented preview modules:
- directional_horizon: broad sunrise/sunset sectors; never exact alignment.
- visibility: distance-visibility diagnostic from forecast visibility.

A profile becomes preview_module_available only when every dependency encoded in
its supported runtime contract is implemented here. This is not production
formula certification.
"""

MODULE_VERSION = "opportunity-runtime-r2-preview"

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

SUPPORTED_RUNTIME_CONTRACTS = {
    "needs_directional_horizon_module": ("directional_horizon",),
    "needs_directional_horizon_visibility_module": ("directional_horizon", "visibility"),
}


def _angle_diff(a, b):
    return abs((float(a) - float(b) + 180.0) % 360.0 - 180.0)


def supports_directional_horizon(opportunity):
    return opportunity.get("opportunity_id") in DIRECTIONAL_HORIZON_SECTORS


def supports_runtime_contract(opportunity):
    status = opportunity.get("formula_status")
    deps = SUPPORTED_RUNTIME_CONTRACTS.get(status)
    if not deps:
        return False
    if "directional_horizon" in deps and not supports_directional_horizon(opportunity):
        return False
    return True


# Backward-compatible helper name used by B16-r1.
supports_opportunity = supports_directional_horizon


def evaluate_directional_horizon(opportunity, item_data):
    oid = opportunity.get("opportunity_id")
    sector = DIRECTIONAL_HORIZON_SECTORS.get(oid)
    if not sector:
        return {"module": "directional_horizon", "available": False, "eligible": False, "reason": "unsupported_opportunity"}
    if not item_data.get("astronomy_valid"):
        return {"module": "directional_horizon", "available": True, "eligible": False, "reason": "astronomy_unavailable"}

    sun_azimuth = item_data.get("sun_azimuth")
    sun_elevation = item_data.get("sun_elevation")
    if sun_azimuth is None or sun_elevation is None:
        return {"module": "directional_horizon", "available": True, "eligible": False, "reason": "solar_geometry_missing"}

    hour = item_data.get("hour")
    if hour is not None:
        hour = int(hour)
        if sector["phase"] == "sunrise" and hour >= 12:
            return {"module": "directional_horizon", "available": True, "eligible": False, "reason": "wrong_daypart"}
        if sector["phase"] == "sunset" and hour < 12:
            return {"module": "directional_horizon", "available": True, "eligible": False, "reason": "wrong_daypart"}

    elevation = float(sun_elevation)
    if not -12.0 <= elevation <= 10.0:
        return {
            "module": "directional_horizon", "available": True, "eligible": False,
            "reason": "outside_twilight_window", "sun_elevation": round(elevation, 1),
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
    """Evaluate horizontal visibility without pretending it is a final score."""
    if item_data.get("vis") is not None:
        km = float(item_data["vis"]) / 1000.0
    elif item_data.get("visibility") is not None:
        km = float(item_data["visibility"])
    else:
        return {"module": "visibility", "available": False, "eligible": False, "reason": "visibility_missing"}

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


def evaluate_opportunity_modules(opportunity, item_data):
    deps = SUPPORTED_RUNTIME_CONTRACTS.get(opportunity.get("formula_status"))
    if not deps or not supports_runtime_contract(opportunity):
        return {
            "module_version": MODULE_VERSION,
            "available": False,
            "eligible": False,
            "reason": "runtime_contract_pending",
            "modules": {},
        }

    results = {}
    for dep in deps:
        if dep == "directional_horizon":
            results[dep] = evaluate_directional_horizon(opportunity, item_data)
        elif dep == "visibility":
            results[dep] = evaluate_visibility(item_data)

    available = all(result.get("available") for result in results.values())
    eligible = available and all(result.get("eligible") for result in results.values())
    return {
        "module_version": MODULE_VERSION,
        "available": available,
        "eligible": eligible,
        "reason": "all_modules_match" if eligible else ("module_condition_miss" if available else "module_data_missing"),
        "modules": results,
    }


def validate_runtime_registry():
    errors = []
    if len(DIRECTIONAL_HORIZON_SECTORS) != 20:
        errors.append(f"expected 20 registered directional profiles, got {len(DIRECTIONAL_HORIZON_SECTORS)}")
    for oid, sector in DIRECTIONAL_HORIZON_SECTORS.items():
        if not oid.startswith("tw-"):
            errors.append(f"{oid}: Taiwan Opportunity id expected")
        if not 0 <= float(sector["center"]) < 360:
            errors.append(f"{oid}: invalid center")
        if not 0 < float(sector["tolerance"]) <= 90:
            errors.append(f"{oid}: invalid tolerance")
        if sector["phase"] not in {"sunrise", "sunset"}:
            errors.append(f"{oid}: invalid phase")
    return errors


validate_directional_horizon_registry = validate_runtime_registry

_REGISTRY_ERRORS = validate_runtime_registry()
if _REGISTRY_ERRORS:
    raise ValueError("Invalid Opportunity runtime registry: " + "; ".join(_REGISTRY_ERRORS))
