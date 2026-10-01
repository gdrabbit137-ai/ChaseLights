"""Versioned, uncalibrated photography-transparency diagnostic.

B170a combines visibility, aerosol and moisture evidence for replay only.
It is intentionally isolated from Opportunity scoring until field calibration.
"""

FORMULA_VERSION = "b170a-heuristic-1"


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _piecewise(value, points):
    if value is None:
        return None
    if value <= points[0][0]:
        return points[0][1]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if value <= x1:
            t = (value - x0) / (x1 - x0)
            return y0 + (y1 - y0) * t
    return points[-1][1]


VISIBILITY = [(2, .05), (5, .15), (10, .35), (20, .65), (30, .82), (40, .95), (60, 1.0)]
AOD = [(0, .98), (.05, .95), (.1, .90), (.2, .75), (.4, .50), (.8, .20), (1.5, .05)]
PM25 = [(0, 1.0), (5, .95), (10, .90), (15, .82), (25, .65), (35, .50), (50, .30), (75, .12), (100, .05)]
RH = [(30, 1.0), (60, .98), (70, .95), (80, .88), (85, .80), (90, .68), (95, .45), (98, .25), (100, .15)]
DEW_SPREAD = [(0, .15), (1, .35), (2, .55), (3, .72), (5, .90), (8, 1.0)]


def evaluate_transparency(item):
    vis_km = _number(item.get("visibility_km"))
    if vis_km is None:
        vis_m = _number(item.get("vis"))
        vis_km = vis_m / 1000.0 if vis_m is not None else None
    aod = _number(item.get("aod_550nm", item.get("aerosol_optical_depth_550nm")))
    pm25 = _number(item.get("pm2_5_ug_m3", item.get("pm2_5")))
    rh = _number(item.get("rh", item.get("relative_humidity_2m_percent")))
    temp = _number(item.get("temp", item.get("temperature_2m_c")))
    dew = _number(item.get("dew", item.get("dew_point_2m_c")))

    visibility_factor = _piecewise(vis_km, VISIBILITY)
    aod_factor = _piecewise(aod, AOD)
    pm25_factor = _piecewise(pm25, PM25)
    aerosol_parts = [v for v in (aod_factor, pm25_factor) if v is not None]
    aerosol_factor = min(aerosol_parts) if aerosol_parts else None

    rh_factor = _piecewise(rh, RH)
    dew_factor = _piecewise(max(0.0, temp - dew), DEW_SPREAD) if temp is not None and dew is not None else None
    moisture_parts = [v for v in (rh_factor, dew_factor) if v is not None]
    moisture_factor = min(moisture_parts) if moisture_parts else None

    components = {
        "visibility": visibility_factor,
        "aerosol": aerosol_factor,
        "moisture": moisture_factor,
    }
    available = {k: v for k, v in components.items() if v is not None}
    if visibility_factor is None or len(available) < 2:
        return {
            "module": "photography_transparency",
            "available": False,
            "reason": "visibility_plus_environment_evidence_required",
            "formula_version": FORMULA_VERSION,
            "calibration_status": "uncalibrated",
            "diagnostic_only": True,
            "score_effect": "none",
            "components": components,
        }

    weights = {"visibility": .50, "aerosol": .30, "moisture": .20}
    denominator = sum(weights[k] for k in available)
    raw = sum(weights[k] * available[k] for k in available) / denominator
    index = round(max(0.0, min(1.0, raw)) * 100)

    if index >= 85:
        state = "very_clear"
    elif index >= 70:
        state = "clear"
    elif index >= 50:
        state = "moderate"
    elif index >= 30:
        state = "poor"
    else:
        state = "very_poor"

    evidence_count = len(available)
    confidence = "medium" if evidence_count == 3 and aod_factor is not None and pm25_factor is not None else "low"
    return {
        "module": "photography_transparency",
        "available": True,
        "transparency_index": index,
        "state": state,
        "confidence": confidence,
        "formula_version": FORMULA_VERSION,
        "calibration_status": "uncalibrated",
        "diagnostic_only": True,
        "score_effect": "none",
        "components": {k: (round(v, 3) if v is not None else None) for k, v in components.items()},
        "inputs": {
            "visibility_km": vis_km,
            "aod_550nm": aod,
            "pm2_5_ug_m3": pm25,
            "relative_humidity_percent": rh,
            "dew_point_spread_c": (max(0.0, temp - dew) if temp is not None and dew is not None else None),
        },
    }
