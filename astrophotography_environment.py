"""Diagnostic-only astrophotography environment synthesis.

B171a combines existing evidence without claiming target visibility or changing
Opportunity scores. Moon geometry is deliberately required for a complete
night-sky assessment and is not inferred when absent.
"""

from photography_environment import classify_dark_sky_evidence
from photography_transparency import evaluate_transparency
from lunar_ephemeris import lunar_ephemeris, lunar_ephemeris_for_galactic_core


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def evaluate_astro_environment(item, dt=None, lat_deg=None, lon_deg=None, target=None):
    dark = classify_dark_sky_evidence(item)
    transparency = evaluate_transparency(item)

    total_cloud = _number(item.get("cloud_cover_percent", item.get("cloud_cover")))
    low = _number(item.get("c_low", item.get("cloud_cover_low")))
    mid = _number(item.get("c_mid", item.get("cloud_cover_mid")))
    high = _number(item.get("c_high", item.get("cloud_cover_high")))
    cloud_values = [v for v in (total_cloud, low, mid, high) if v is not None]
    worst_cloud = max(cloud_values) if cloud_values else None

    lunar = None
    if dt is not None and lat_deg is not None and lon_deg is not None:
        if target == "galactic_core":
            lunar = lunar_ephemeris_for_galactic_core(dt, lat_deg, lon_deg)
        elif isinstance(target, dict) and target.get("ra_deg") is not None and target.get("dec_deg") is not None:
            lunar = lunar_ephemeris(
                dt, lat_deg, lon_deg, target["ra_deg"], target["dec_deg"]
            )
        else:
            lunar = lunar_ephemeris(dt, lat_deg, lon_deg)

    moon_altitude = _number(
        lunar.get("moon_altitude_deg") if lunar else item.get("moon_altitude_deg")
    )
    moon_illumination = _number(lunar.get("moon_illumination_fraction") if lunar else item.get("moon_illumination_fraction"))
    moon_separation = _number(lunar.get("moon_target_separation_deg") if lunar else item.get("moon_target_separation_deg"))
    moon_complete = moon_altitude is not None and moon_illumination is not None

    missing = []
    if not dark.get("usable_for_context"):
        missing.append("quality_checked_nighttime_light_radiance")
    if not transparency.get("available"):
        missing.append("atmospheric_transparency")
    if worst_cloud is None:
        missing.append("cloud_cover")
    if not moon_complete:
        missing.append("moon_geometry")
    if moon_separation is None:
        missing.append("moon_target_separation")

    blockers = []
    if worst_cloud is not None and worst_cloud >= 80:
        blockers.append("extensive_cloud")
    if transparency.get("available") and transparency.get("transparency_index", 100) < 30:
        blockers.append("very_poor_transparency")
    if dark.get("state") == "high_artificial_light_radiance":
        blockers.append("high_artificial_light_radiance")

    if missing:
        state = "incomplete_evidence"
        confidence = "low"
    elif blockers:
        state = "challenging_environment"
        confidence = "medium"
    else:
        state = "environment_evidence_favorable"
        confidence = "medium"

    return {
        "module": "astrophotography_environment",
        "available": bool(
            dark.get("available") or transparency.get("available") or worst_cloud is not None
        ),
        "state": state,
        "confidence": confidence,
        "dark_sky_evidence": dark,
        "transparency": transparency,
        "cloud": {
            "total_percent": total_cloud,
            "low_percent": low,
            "mid_percent": mid,
            "high_percent": high,
            "worst_available_percent": worst_cloud,
        },
        "moon": {
            "altitude_deg": moon_altitude,
            "illumination_fraction": moon_illumination,
            "target_separation_deg": moon_separation,
            "complete": moon_complete,
            "source": ("b171b_lunar_ephemeris" if lunar else "item_fields"),
            "contract_version": (lunar.get("contract_version") if lunar else None),
        },
        "missing_evidence": missing,
        "blockers": blockers,
        "not_target_visibility_claim": True,
        "not_milky_way_visibility_claim": True,
        "diagnostic_only": True,
        "score_effect": "none",
    }
