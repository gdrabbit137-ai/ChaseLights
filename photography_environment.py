"""Conservative photography-environment classifier for fog versus aerosol haze.

B168 is diagnostic only. It must not directly change Opportunity scores.
Thresholds are planning heuristics and deliberately return mixed/uncertain when
meteorological saturation and aerosol evidence overlap.
"""

FOG_WEATHER_CODES = {45, 48}


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def classify_fog_haze(item):
    """Classify visibility degradation without treating AOD/PM2.5 as fog.

    Expected inputs may include visibility metres (vis), RH percent (rh),
    temperature/dew point C (temp/dew), low cloud percent (c_low), WMO weather
    code, AOD 550 nm, and PM2.5 µg/m³.
    """
    vis_m = _number(item.get("vis", item.get("visibility_m")))
    rh = _number(item.get("rh", item.get("relative_humidity_2m")))
    temp = _number(item.get("temp", item.get("temperature_2m")))
    dew = _number(item.get("dew", item.get("dew_point_2m")))
    low = _number(item.get("c_low", item.get("cloud_cover_low")))
    code = item.get("weather_code")
    aod = _number(item.get("aod_550nm", item.get("aerosol_optical_depth_550nm")))
    pm25 = _number(item.get("pm2_5_ug_m3", item.get("pm2_5")))

    visibility_low = vis_m is not None and vis_m <= 5000
    near_saturation = (
        (rh is not None and rh >= 95)
        or (temp is not None and dew is not None and temp - dew <= 1.5)
    )
    fog_code = code in FOG_WEATHER_CODES
    low_cloud_support = low is not None and low >= 70
    fog_support = visibility_low and (near_saturation or fog_code or low_cloud_support)

    # Aerosol thresholds are intentionally coarse planning signals, not health
    # categories. Either CAMS field can support haze; neither proves visibility
    # degradation without a visibility observation/forecast.
    aerosol_support = (
        (pm25 is not None and pm25 >= 25)
        or (aod is not None and aod >= 0.4)
    )
    aerosol_strong = (
        (pm25 is not None and pm25 >= 35)
        or (aod is not None and aod >= 0.8)
    )

    evidence = []
    if visibility_low:
        evidence.append("low_visibility")
    if near_saturation:
        evidence.append("near_saturation")
    if fog_code:
        evidence.append("fog_weather_code")
    if low_cloud_support:
        evidence.append("low_cloud_support")
    if pm25 is not None and pm25 >= 25:
        evidence.append("pm25_elevated")
    if aod is not None and aod >= 0.4:
        evidence.append("aod_elevated")

    if fog_support and aerosol_support:
        state = "mixed_fog_haze"
        confidence = "medium" if aerosol_strong and (near_saturation or fog_code) else "low"
    elif fog_support:
        state = "fog_supported"
        confidence = "medium" if near_saturation and (fog_code or low_cloud_support) else "low"
    elif visibility_low and aerosol_support:
        state = "haze_supported"
        confidence = "medium" if aerosol_strong else "low"
    elif visibility_low:
        state = "low_visibility_unresolved"
        confidence = "low"
    elif aerosol_support:
        state = "aerosol_present_visibility_not_degraded"
        confidence = "low"
    elif vis_m is not None:
        state = "no_fog_haze_signal"
        confidence = "low"
    else:
        state = "insufficient_visibility_evidence"
        confidence = "low"

    return {
        "module": "fog_haze_environment",
        "available": vis_m is not None or aod is not None or pm25 is not None,
        "state": state,
        "confidence": confidence,
        "visibility_km": round(vis_m / 1000.0, 1) if vis_m is not None else None,
        "aod_550nm": aod,
        "pm2_5_ug_m3": pm25,
        "evidence": evidence,
        "fog_support": fog_support,
        "aerosol_support": aerosol_support,
        "diagnostic_only": True,
        "score_effect": "none",
    }


def classify_dark_sky_evidence(item):
    """Describe VIIRS nighttime-light evidence without inventing sky brightness.

    This diagnostic intentionally stops at upward/observed nighttime-light
    radiance context. It is not a Bortle, SQM, limiting-magnitude, Milky Way
    visibility, or skyglow model.
    """
    radiance = _number(item.get(
        "nighttime_lights_radiance_nw_cm2_sr",
        item.get("viirs_nighttime_lights_radiance"),
    ))
    quality = item.get(
        "nighttime_lights_quality_flag",
        item.get("viirs_nighttime_lights_quality_flag"),
    )
    try:
        quality = int(quality) if quality is not None else None
    except (TypeError, ValueError):
        quality = None

    quality_labels = {0: "good", 1: "poor", 2: "gap_filled"}
    quality_label = quality_labels.get(quality, "unknown")
    usable = radiance is not None and quality in quality_labels

    # These bins are presentation/planning heuristics for *radiance evidence*
    # only. They are deliberately not mapped to Bortle/SQM or a score.
    if radiance is None:
        state = "night_lights_unavailable"
    elif radiance < 1:
        state = "low_artificial_light_radiance"
    elif radiance < 5:
        state = "moderate_artificial_light_radiance"
    elif radiance < 10:
        state = "elevated_artificial_light_radiance"
    else:
        state = "high_artificial_light_radiance"

    confidence = (
        "medium" if quality == 0 and radiance is not None
        else "low"
    )
    evidence = []
    if radiance is not None:
        evidence.append("viirs_annual_nighttime_radiance")
    if quality_label != "unknown":
        evidence.append(f"viirs_quality_{quality_label}")

    return {
        "module": "dark_sky_environment",
        "available": radiance is not None,
        "state": state,
        "confidence": confidence,
        "radiance_nw_cm2_sr": radiance,
        "quality_flag": quality,
        "quality": quality_label,
        "usable_for_context": usable,
        "evidence": evidence,
        "interpretation": "artificial_light_radiance_context_only",
        "not_bortle": True,
        "not_sqm": True,
        "not_sky_brightness": True,
        "diagnostic_only": True,
        "score_effect": "none",
    }
