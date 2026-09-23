"""Preview directional-horizon runtime module for R4.2 Opportunities.

This module handles broad sunrise/sunset illumination sectors, not exact
subject/sun alignment. Exact alignments remain geometry-specific contracts.
Only Opportunities whose sole outstanding dependency is the directional
horizon module are registered here.
"""

MODULE_VERSION = "directional-horizon-r1-preview"

# Broad photographic sectors derived from the reviewed R4.2 Opportunity
# condition geometry. Tolerances intentionally represent usable sectors rather
# than a single tripod/subject bearing.
DIRECTIONAL_HORIZON_SECTORS = {
    "tw-001-P01": {"center": 247.5, "tolerance": 67.5, "phase": "sunset"},
    "tw-003-P01": {"center": 270.0, "tolerance": 70.0, "phase": "sunset"},
    "tw-004-P04": {"center": 270.0, "tolerance": 70.0, "phase": "sunset"},
    "tw-006-P02": {"center": 292.5, "tolerance": 67.5, "phase": "sunset"},
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
    "tw-070-P01": {"center": 247.5, "tolerance": 67.5, "phase": "sunset"},
}


def _angle_diff(a, b):
    return abs((float(a) - float(b) + 180.0) % 360.0 - 180.0)


def supports_opportunity(opportunity):
    return (
        opportunity.get("formula_status") == "needs_directional_horizon_module"
        and opportunity.get("opportunity_id") in DIRECTIONAL_HORIZON_SECTORS
    )


def evaluate_directional_horizon(opportunity, item_data):
    """Evaluate broad solar-sector eligibility for one hourly weather item.

    Returns a diagnostic preview result. It deliberately does not emit a final
    Opportunity score; cloud quality, visibility, access, and other modules
    remain separate dependencies.
    """
    oid = opportunity.get("opportunity_id")
    sector = DIRECTIONAL_HORIZON_SECTORS.get(oid)
    if not supports_opportunity(opportunity) or not sector:
        return {
            "module": MODULE_VERSION,
            "available": False,
            "eligible": False,
            "reason": "unsupported_opportunity",
        }

    if not item_data.get("astronomy_valid"):
        return {
            "module": MODULE_VERSION,
            "available": True,
            "eligible": False,
            "reason": "astronomy_unavailable",
        }

    sun_azimuth = item_data.get("sun_azimuth")
    sun_elevation = item_data.get("sun_elevation")
    if sun_azimuth is None or sun_elevation is None:
        return {
            "module": MODULE_VERSION,
            "available": True,
            "eligible": False,
            "reason": "solar_geometry_missing",
        }

    hour = item_data.get("hour")
    if hour is not None:
        hour = int(hour)
        if sector["phase"] == "sunrise" and hour >= 12:
            return {
                "module": MODULE_VERSION,
                "available": True,
                "eligible": False,
                "reason": "wrong_daypart",
            }
        if sector["phase"] == "sunset" and hour < 12:
            return {
                "module": MODULE_VERSION,
                "available": True,
                "eligible": False,
                "reason": "wrong_daypart",
            }

    elevation = float(sun_elevation)
    if not -12.0 <= elevation <= 10.0:
        return {
            "module": MODULE_VERSION,
            "available": True,
            "eligible": False,
            "reason": "outside_twilight_window",
            "sun_elevation": round(elevation, 1),
        }

    diff = _angle_diff(sun_azimuth, sector["center"])
    eligible = diff <= sector["tolerance"]
    return {
        "module": MODULE_VERSION,
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


def validate_directional_horizon_registry():
    errors = []
    if len(DIRECTIONAL_HORIZON_SECTORS) != 17:
        errors.append(f"expected 17 pure directional profiles, got {len(DIRECTIONAL_HORIZON_SECTORS)}")
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


_REGISTRY_ERRORS = validate_directional_horizon_registry()
if _REGISTRY_ERRORS:
    raise ValueError("Invalid directional horizon registry: " + "; ".join(_REGISTRY_ERRORS))
