"""Spatial / vertical low-cloud preview support for ChaseLights R4.2.

This module deliberately does not infer cloud sea from one point. For configured
profiles it builds a camera sample plus an 8-direction ring of nearby points.
Open-Meteo supplies each point's DEM elevation and hourly weather. The evaluator
then asks whether the camera is relatively clear while multiple materially lower
terrain samples show low-cloud/fog evidence.

Under RESEARCH_EVIDENCE_SPEC_R4_2 this spatial/vertical result may establish the
forecast-derived environmental condition "cloud layer below camera" for cloud-sea
classification. It still does not prove an exact foreground composition, scenic
quality, access, or a verified photographic target zone.

The ring is an environmental proxy, not a verified photographic target zone.
That limitation is returned in every diagnostic.
"""

import math

SPATIAL_WEATHER_VERSION = "spatial-weather-r7-qingshui-directional-contrast"

_SUPPORTED_PROFILE_IDS = (
    "tw-004-P02", "tw-004-P03", "tw-008-P03",
    "tw-014-P02",
    "tw-019-P04",
    "tw-020-P02", "tw-020-P03",
    "tw-022-P02",
    "tw-023-P02", "tw-023-P03",
    "tw-024-P02",
    "tw-032-P02",
    "tw-035-P06",
    "tw-040-P04",
    "tw-043-P02", "tw-043-P03",
    "tw-047-P01", "tw-047-P02",
    "tw-049-P03",
)

SPATIAL_WEATHER_PROFILES = {
    oid: {
        "mode": "lower_cloud_below_camera",
        "sample_distance_km": 8.0,
        "bearings_deg": tuple(range(0, 360, 45)),
        "min_vertical_drop_m": 250.0,
        "min_cloudy_targets": 2,
    }
    for oid in _SUPPORTED_PROFILE_IDS
}

# B83 Qixingtan: a required northward multi-point contract for a researched
# coast-clear / mountain-cloud-band subject. Unlike cloud-sea profiles, target
# terrain is materially HIGHER than the camera. The samples are broad
# environmental proxies only; they do not prove an exact cloud/ridge overlap.
SPATIAL_WEATHER_PROFILES["tw-036-P03"] = {
    "mode": "directional_mountain_cloud_sector",
    "bearings_deg": (350.0, 5.0, 20.0),
    "sample_distances_km": (8.0, 15.0, 22.0),
    "min_target_elevation_gain_m": 250.0,
    "min_cloudy_targets": 2,
    "min_directional_cloud_targets": 2,
    # B85 low-confidence fallback for grid-scale misses. This is deliberately
    # stricter than a simple low LCL: the camera must stay clear, terrain must
    # intersect the LCL proxy across multiple bearings, and at least one
    # elevated target must show a strong visibility collapse plus some low-cloud
    # support. It can create only an uncertain candidate, never a confirmed band.
    "orographic_proxy_min_intersection_targets": 2,
    "orographic_proxy_min_intersection_bearings": 2,
    "orographic_proxy_max_visibility_km": 8.0,
    "orographic_proxy_max_visibility_ratio": 0.30,
    "orographic_proxy_min_low_cloud_pct": 15.0,
    "orographic_proxy_min_readable_targets": 2,
    "orographic_proxy_min_readable_bearings": 2,
}

# B84 sibling Opportunity: same researched northward mountain sector, but this
# contract asks whether the distant Qingshui Cliff / Qingshui Mountain layers
# remain broadly readable. It is deliberately separate from the cloud-band
# subject so "clear mountain view" and "terrain-attached cloud" can coexist as
# different photographic outcomes.
SPATIAL_WEATHER_PROFILES["tw-036-P04"] = {
    "mode": "directional_mountain_visibility_sector",
    "bearings_deg": (350.0, 5.0, 20.0),
    "sample_distances_km": (8.0, 15.0, 22.0),
    "min_target_elevation_gain_m": 250.0,
    "min_readable_targets": 2,
    "min_readable_bearings": 2,
}

# Optional spatial context for researched minimum-sufficient subjects. These
# profiles enrich confidence but do not become formal runtime dependencies:
# if the multi-point fetch is unavailable, the base place-specific contract
# still returns a conservative low-confidence candidate rather than failing.
OPTIONAL_DIRECTIONAL_MIST_PROFILES = {
    "tw-034-P03": {
        "mode": "directional_mist_sector",
        # Sample the broad Qingshui-Cliff viewing sector at two ranges. These
        # are environmental proxy points, not verified tripod/subject points.
        # Official Taroko/National Park guidance for the Chongde area says
        # Qingshui Cliff is viewed to the north. Use a broad north-facing
        # environmental sector instead of the legacy spot-level 155° azimuth,
        # which is not an Opportunity-specific cliff geometry contract.
        "bearings_deg": (330.0, 0.0, 30.0),
        "sample_distances_km": (2.5, 5.0),
        "min_misty_targets": 1,
    },
}


def _profile_config(opportunity_id):
    return (
        SPATIAL_WEATHER_PROFILES.get(opportunity_id)
        or OPTIONAL_DIRECTIONAL_MIST_PROFILES.get(opportunity_id)
    )


def _camera_viewpoint(opportunity):
    for vp in opportunity.get("viewpoints", []) or []:
        if vp.get("lat") is not None and vp.get("lon") is not None:
            return vp
    return None


def supports_spatial_weather(opportunity):
    return (
        _profile_config(opportunity.get("opportunity_id")) is not None
        and _camera_viewpoint(opportunity) is not None
    )


def _offset_point(lat, lon, bearing_deg, distance_km):
    radius_km = 6371.0088
    angular = float(distance_km) / radius_km
    bearing = math.radians(float(bearing_deg))
    lat1 = math.radians(float(lat))
    lon1 = math.radians(float(lon))
    lat2 = math.asin(
        math.sin(lat1) * math.cos(angular)
        + math.cos(lat1) * math.sin(angular) * math.cos(bearing)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(angular) * math.cos(lat1),
        math.cos(angular) - math.sin(lat1) * math.sin(lat2),
    )
    return round(math.degrees(lat2), 6), round((math.degrees(lon2) + 540.0) % 360.0 - 180.0, 6)


def build_spatial_request_plan(spot):
    points = []
    point_by_coord = {}
    profiles = {}

    def add_point(lat, lon, role, bearing=None, distance_km=None):
        key = (round(float(lat), 5), round(float(lon), 5))
        if key in point_by_coord:
            return point_by_coord[key]
        point_id = f"S{len(points):02d}"
        point = {
            "point_id": point_id,
            "lat": float(lat),
            "lon": float(lon),
            "role": role,
        }
        if bearing is not None:
            point["bearing_deg"] = float(bearing)
        if distance_km is not None:
            point["distance_km"] = float(distance_km)
        points.append(point)
        point_by_coord[key] = point_id
        return point_id

    for opportunity in spot.get("opportunities", []) or []:
        if not supports_spatial_weather(opportunity):
            continue
        oid = opportunity["opportunity_id"]
        config = _profile_config(oid)
        viewpoint = _camera_viewpoint(opportunity)
        camera_id = add_point(viewpoint["lat"], viewpoint["lon"], "camera")
        target_ids = []
        distances = config.get("sample_distances_km")
        if not distances:
            distances = (config["sample_distance_km"],)
        if config.get("mode") == "directional_mist_sector":
            target_role = "directional_mist_proxy"
        elif config.get("mode") in {
            "directional_mountain_cloud_sector",
            "directional_mountain_visibility_sector",
        }:
            target_role = "directional_mountain_proxy"
        else:
            target_role = "lower_terrain_proxy"
        for distance_km in distances:
            for bearing in config["bearings_deg"]:
                lat, lon = _offset_point(
                    viewpoint["lat"],
                    viewpoint["lon"],
                    bearing,
                    distance_km,
                )
                target_ids.append(
                    add_point(
                        lat, lon, target_role,
                        bearing=bearing,
                        distance_km=distance_km,
                    )
                )
        profiles[oid] = {
            "camera_point_id": camera_id,
            "target_point_ids": target_ids,
            "camera_reference_elevation_m": viewpoint.get("elevation_m"),
            "target_resolution": (
                "directional_sector_environment_proxy_not_exact_cliff_or_mist_location"
                if config.get("mode") == "directional_mist_sector"
                else (
                    "directional_mountain_sector_environment_proxy_not_exact_cloud_or_ridge_location"
                    if config.get("mode") == "directional_mountain_cloud_sector"
                    else (
                        "directional_mountain_sector_environment_proxy_not_exact_ridge_visibility"
                        if config.get("mode") == "directional_mountain_visibility_sector"
                        else "radial_lower_terrain_proxy_not_exact_target_zone"
                    )
                )
            ),
        }

    return {
        "version": SPATIAL_WEATHER_VERSION,
        "points": points,
        "profiles": profiles,
    }


def index_spatial_response(plan, raw):
    if not plan or not plan.get("points"):
        return None
    responses = raw if isinstance(raw, list) else [raw]
    if len(responses) != len(plan["points"]):
        raise ValueError(
            f"spatial response count mismatch: expected {len(plan['points'])}, got {len(responses)}"
        )

    series = {}
    fields = (
        "temperature_2m",
        "dew_point_2m",
        "relative_humidity_2m",
        "cloud_cover_low",
        "visibility",
        "precipitation",
        "wind_speed_10m",
        "weather_code",
    )
    for point, response in zip(plan["points"], responses):
        hourly = response.get("hourly", {}) or {}
        times = hourly.get("time", []) or []
        by_time = {}
        for i, ts in enumerate(times):
            sample = {
                "point_id": point["point_id"],
                "lat": point["lat"],
                "lon": point["lon"],
                "role": point["role"],
                "elevation_m": response.get("elevation"),
                "bearing_deg": point.get("bearing_deg"),
                "distance_km": point.get("distance_km"),
            }
            for field in fields:
                values = hourly.get(field, []) or []
                sample[field] = values[i] if i < len(values) else None
            by_time[int(ts)] = sample
        series[point["point_id"]] = {
            "meta": point,
            "by_time": by_time,
        }

    return {
        "version": plan["version"],
        "plan": plan,
        "series": series,
    }


def spatial_observations_for_timestamp(indexed, timestamp):
    if not indexed:
        return {}
    timestamp = int(timestamp)
    observations = {}
    for oid, config in indexed["plan"]["profiles"].items():
        camera_series = indexed["series"].get(config["camera_point_id"], {})
        camera = (camera_series.get("by_time") or {}).get(timestamp)
        targets = []
        for point_id in config["target_point_ids"]:
            row = ((indexed["series"].get(point_id) or {}).get("by_time") or {}).get(timestamp)
            if row is not None:
                targets.append(row)
        observations[oid] = {
            "camera": camera,
            "targets": targets,
            "camera_reference_elevation_m": config.get("camera_reference_elevation_m"),
            "target_resolution": config["target_resolution"],
        }
    return observations


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _evaluate_directional_mist_sector(config, observation):
    camera = observation.get("camera") or {}
    camera_vis = _number(camera.get("visibility"))
    camera_low = _number(camera.get("cloud_cover_low"))
    camera_rh = _number(camera.get("relative_humidity_2m"))
    camera_precip = _number(camera.get("precipitation"))
    camera_weather_code = camera.get("weather_code")
    camera_fog_code = camera_weather_code in {45, 48}

    if camera_vis is None or camera_low is None or camera_rh is None:
        return {
            "module": "directional_mist_spatial_context",
            "available": False,
            "eligible": False,
            "reason": "camera_weather_missing",
        }

    camera_whiteout = (
        camera_vis < 250
        or (
            camera_vis < 500
            and camera_rh >= 96
            and camera_low >= 90
        )
        or (camera_precip is not None and camera_precip >= 1.0)
    )
    if camera_whiteout:
        return {
            "module": "directional_mist_spatial_context",
            "available": True,
            "eligible": False,
            "reason": "camera_whiteout_risk",
            "camera_whiteout_risk": True,
            "camera_visibility_km": round(camera_vis / 1000.0, 1),
            "camera_low_cloud": round(camera_low),
            "camera_rh": round(camera_rh),
            "target_resolution": observation.get("target_resolution"),
            "exact_target_zone_verified": False,
            "confidence_hint": "medium",
        }

    mist_targets = []
    directional_targets = []
    valid_targets = []
    for target in observation.get("targets", []) or []:
        vis = _number(target.get("visibility"))
        low = _number(target.get("cloud_cover_low"))
        rh = _number(target.get("relative_humidity_2m"))
        precip = _number(target.get("precipitation"))
        weather_code = target.get("weather_code")
        if vis is None or low is None or rh is None:
            continue
        if precip is not None and precip >= 1.0:
            continue

        valid_targets.append(target)
        fog_code = weather_code in {45, 48}
        mist_signal = (
            fog_code
            or (vis <= 3000 and rh >= 85)
            or (vis <= 6000 and rh >= 90 and low >= 50)
        )
        if not mist_signal:
            continue

        mist_targets.append(target)
        # Fog at a target is directional evidence only when it differs
        # from the camera state. If camera and target are both fog-coded, the
        # target sector still needs a material visibility / low-cloud / RH
        # contrast before it may promote the Qingshui candidate.
        directional_contrast = (
            (fog_code and not camera_fog_code)
            or vis <= camera_vis * 0.75
            or low >= camera_low + 25
            or rh >= camera_rh + 8
        )
        if directional_contrast:
            directional_targets.append(target)

    if len(valid_targets) < 2:
        return {
            "module": "directional_mist_spatial_context",
            "available": False,
            "eligible": False,
            "reason": "insufficient_directional_samples",
            "target_sample_count": len(valid_targets),
            "camera_whiteout_risk": False,
            "target_resolution": observation.get("target_resolution"),
            "exact_target_zone_verified": False,
        }

    required = min(int(config.get("min_misty_targets", 1)), len(valid_targets))
    eligible = len(directional_targets) >= required
    return {
        "module": "directional_mist_spatial_context",
        "available": True,
        "eligible": eligible,
        "reason": (
            "directional_mist_signal_detected"
            if eligible else "directional_mist_not_distinguished_from_camera"
        ),
        "camera_whiteout_risk": False,
        "camera_visibility_km": round(camera_vis / 1000.0, 1),
        "camera_low_cloud": round(camera_low),
        "camera_rh": round(camera_rh),
        "target_sample_count": len(valid_targets),
        "mist_target_count": len(mist_targets),
        "directional_mist_target_count": len(directional_targets),
        "target_resolution": observation.get("target_resolution"),
        "exact_target_zone_verified": False,
        "confidence_hint": "medium" if eligible else "low",
    }



def _evaluate_directional_mountain_cloud_sector(config, observation, item_data=None):
    """Evaluate Qixingtan-style clear-coast / cloud-on-mountain contrast.

    This is a forecast candidate, not visual confirmation. A valid match needs:
    - a readable camera/coast grid,
    - multiple materially elevated northward proxy samples,
    - coherent low-cloud/moisture evidence stronger than at the camera,
    - at least one cloud-bearing target that is not an opaque local whiteout.
    """
    camera = observation.get("camera") or {}
    camera_vis = _number(camera.get("visibility"))
    camera_low = _number(camera.get("cloud_cover_low"))
    camera_rh = _number(camera.get("relative_humidity_2m"))
    camera_precip = _number(camera.get("precipitation"))
    camera_elevation = _number(camera.get("elevation_m"))
    if camera_vis is None or camera_low is None or camera_rh is None or camera_elevation is None:
        return {
            "module": "spatial_weather_vertical_cloud",
            "mode": "directional_mountain_cloud_sector",
            "available": False,
            "eligible": False,
            "reason": "camera_weather_or_elevation_missing",
        }

    camera_whiteout = (
        camera_vis < 8000
        or (camera_low >= 85 and camera_rh >= 94)
        or (camera_precip is not None and camera_precip >= 1.0)
    )
    if camera_whiteout:
        return {
            "module": "spatial_weather_vertical_cloud",
            "mode": "directional_mountain_cloud_sector",
            "available": True,
            "eligible": False,
            "reason": "camera_not_clear_enough_for_mountain_cloud_subject",
            "camera_whiteout_risk": True,
            "camera_visibility_km": round(camera_vis / 1000.0, 1),
            "camera_low_cloud": round(camera_low),
            "camera_rh": round(camera_rh),
            "target_resolution": observation.get("target_resolution"),
            "exact_target_zone_verified": False,
            "visibility_guaranteed": False,
        }

    elevated_targets = []
    cloud_targets = []
    directional_cloud_targets = []
    readable_cloud_targets = []
    min_gain = float(config.get("min_target_elevation_gain_m", 250.0))

    for target in observation.get("targets", []) or []:
        elevation = _number(target.get("elevation_m"))
        vis = _number(target.get("visibility"))
        low = _number(target.get("cloud_cover_low"))
        rh = _number(target.get("relative_humidity_2m"))
        precip = _number(target.get("precipitation"))
        weather_code = target.get("weather_code")
        if elevation is None or vis is None or low is None or rh is None:
            continue
        gain = elevation - camera_elevation
        if gain < min_gain:
            continue
        if precip is not None and precip >= 1.0:
            continue

        row = dict(target)
        row["elevation_gain_m"] = gain
        elevated_targets.append(row)

        fog_code = weather_code in {45, 48}
        cloud_signal = (
            fog_code
            or (low >= 35 and rh >= 80)
            or (low >= 45 and low >= camera_low + 20)
            or (vis <= 8000 and rh >= 85 and low >= 25)
        )
        if not cloud_signal:
            continue
        cloud_targets.append(row)

        contrast = (
            fog_code
            or low >= camera_low + 20
            or rh >= camera_rh + 8
            or vis <= camera_vis * 0.75
        )
        if contrast:
            directional_cloud_targets.append(row)

        # Local target-grid whiteout can mean the ridge is completely hidden.
        # Preserve candidates only when at least one cloud-bearing mountain
        # sample remains in a planning-grade readable range.
        if vis >= 3000 and low <= 92:
            readable_cloud_targets.append(row)

    if len(elevated_targets) < 2:
        return {
            "module": "spatial_weather_vertical_cloud",
            "mode": "directional_mountain_cloud_sector",
            "available": False,
            "eligible": False,
            "reason": "insufficient_elevated_directional_samples",
            "elevated_target_count": len(elevated_targets),
            "target_resolution": observation.get("target_resolution"),
            "exact_target_zone_verified": False,
            "visibility_guaranteed": False,
        }

    # B84 calibration diagnostics: retain only compact aggregates so production
    # JSON can explain why a ground-truth scene was missed without embedding all
    # nine raw target samples. The camera cloud_base_agl field is a planning-grade
    # LCL proxy derived from temperature/dew point in fetch_data, not an observed
    # cloud base.
    item_data = item_data or {}
    camera_lcl_agl = _number(item_data.get("cloud_base_agl"))
    camera_lcl_asl = (
        camera_elevation + camera_lcl_agl
        if camera_lcl_agl is not None else None
    )
    lcl_intersection_targets = []
    lcl_intersection_bearings = set()
    if camera_lcl_asl is not None:
        for row in elevated_targets:
            elevation = _number(row.get("elevation_m"))
            if elevation is not None and elevation >= camera_lcl_asl:
                lcl_intersection_targets.append(row)
                bearing = _number(row.get("bearing_deg"))
                if bearing is not None:
                    lcl_intersection_bearings.add(round(bearing, 1))

    elevated_low_values = [
        _number(row.get("cloud_cover_low")) for row in elevated_targets
        if _number(row.get("cloud_cover_low")) is not None
    ]
    elevated_rh_values = [
        _number(row.get("relative_humidity_2m")) for row in elevated_targets
        if _number(row.get("relative_humidity_2m")) is not None
    ]
    elevated_vis_values = [
        _number(row.get("visibility")) for row in elevated_targets
        if _number(row.get("visibility")) is not None
    ]
    elevated_elevations = [
        _number(row.get("elevation_m")) for row in elevated_targets
        if _number(row.get("elevation_m")) is not None
    ]

    readable_elevated_targets = []
    readable_elevated_bearings = set()
    for row in elevated_targets:
        vis = _number(row.get("visibility"))
        low = _number(row.get("cloud_cover_low"))
        weather_code = row.get("weather_code")
        if vis is None or low is None:
            continue
        if weather_code in {45, 48} or vis < 8000 or low >= 90:
            continue
        readable_elevated_targets.append(row)
        bearing = _number(row.get("bearing_deg"))
        if bearing is not None:
            readable_elevated_bearings.add(round(bearing, 1))

    min_elevated_visibility = min(elevated_vis_values) if elevated_vis_values else None
    max_elevated_low = max(elevated_low_values) if elevated_low_values else None
    visibility_ratio = (
        min_elevated_visibility / camera_vis
        if min_elevated_visibility is not None and camera_vis > 0
        else None
    )

    required_cloud = min(int(config.get("min_cloudy_targets", 2)), len(elevated_targets))
    required_directional = min(
        int(config.get("min_directional_cloud_targets", required_cloud)),
        len(elevated_targets),
    )
    direct_eligible = (
        len(cloud_targets) >= required_cloud
        and len(directional_cloud_targets) >= required_directional
        and len(readable_cloud_targets) >= 1
    )

    proxy_intersections_ok = (
        len(lcl_intersection_targets) >= int(config.get("orographic_proxy_min_intersection_targets", 999))
        and len(lcl_intersection_bearings) >= int(config.get("orographic_proxy_min_intersection_bearings", 999))
    )
    proxy_visibility_ok = (
        min_elevated_visibility is not None
        and visibility_ratio is not None
        and min_elevated_visibility <= float(config.get("orographic_proxy_max_visibility_km", 0)) * 1000.0
        and visibility_ratio <= float(config.get("orographic_proxy_max_visibility_ratio", 0))
    )
    proxy_low_cloud_ok = (
        max_elevated_low is not None
        and max_elevated_low >= float(config.get("orographic_proxy_min_low_cloud_pct", 101))
    )
    proxy_readability_ok = (
        len(readable_elevated_targets) >= int(config.get("orographic_proxy_min_readable_targets", 999))
        and len(readable_elevated_bearings) >= int(config.get("orographic_proxy_min_readable_bearings", 999))
    )
    proxy_eligible = (
        not direct_eligible
        and proxy_intersections_ok
        and proxy_visibility_ok
        and proxy_low_cloud_ok
        and proxy_readability_ok
    )

    eligible = direct_eligible or proxy_eligible
    reason = (
        "directional_mountain_cloud_band_candidate"
        if direct_eligible
        else (
            "orographic_cloud_proxy_candidate"
            if proxy_eligible
            else "directional_mountain_cloud_band_not_supported"
        )
    )
    return {
        "module": "spatial_weather_vertical_cloud",
        "mode": "directional_mountain_cloud_sector",
        "available": True,
        "eligible": eligible,
        "reason": reason,
        "camera_whiteout_risk": False,
        "camera_visibility_km": round(camera_vis / 1000.0, 1),
        "camera_low_cloud": round(camera_low),
        "camera_rh": round(camera_rh),
        "elevated_target_count": len(elevated_targets),
        "cloud_band_target_count": len(cloud_targets),
        "directional_cloud_target_count": len(directional_cloud_targets),
        "readable_cloud_target_count": len(readable_cloud_targets),
        "max_target_elevation_gain_m": round(
            max((row["elevation_gain_m"] for row in elevated_targets), default=0.0)
        ),
        "elevated_target_max_elevation_m": (
            round(max(elevated_elevations)) if elevated_elevations else None
        ),
        "elevated_target_max_low_cloud_pct": (
            round(max(elevated_low_values)) if elevated_low_values else None
        ),
        "elevated_target_max_rh_pct": (
            round(max(elevated_rh_values)) if elevated_rh_values else None
        ),
        "elevated_target_min_visibility_km": (
            round(min(elevated_vis_values) / 1000.0, 1) if elevated_vis_values else None
        ),
        "camera_lcl_agl_proxy_m": (
            round(camera_lcl_agl) if camera_lcl_agl is not None else None
        ),
        "camera_lcl_asl_proxy_m": (
            round(camera_lcl_asl) if camera_lcl_asl is not None else None
        ),
        "terrain_lcl_intersection_target_count": len(lcl_intersection_targets),
        "terrain_lcl_intersection_bearing_count": len(lcl_intersection_bearings),
        "readable_elevated_target_count": len(readable_elevated_targets),
        "readable_elevated_bearing_count": len(readable_elevated_bearings),
        "elevated_target_min_visibility_ratio": (
            round(visibility_ratio, 2) if visibility_ratio is not None else None
        ),
        "direct_cloud_signal": direct_eligible,
        "orographic_proxy_candidate": proxy_eligible,
        "target_resolution": observation.get("target_resolution"),
        "exact_target_zone_verified": False,
        "visibility_guaranteed": False,
        "confidence_hint": "medium" if direct_eligible else ("low" if proxy_eligible else "low"),
    }


def _evaluate_directional_mountain_visibility_sector(config, observation):
    """Evaluate broad northward mountain/coast readability from Qixingtan.

    This does not require perfectly cloud-free ridges. It asks whether the camera
    grid is clear and multiple materially elevated proxies across the researched
    northward sector remain readable rather than whiteout/opaque.
    """
    camera = observation.get("camera") or {}
    camera_vis = _number(camera.get("visibility"))
    camera_low = _number(camera.get("cloud_cover_low"))
    camera_rh = _number(camera.get("relative_humidity_2m"))
    camera_precip = _number(camera.get("precipitation"))
    camera_elevation = _number(camera.get("elevation_m"))
    if camera_vis is None or camera_low is None or camera_rh is None or camera_elevation is None:
        return {
            "module": "spatial_weather_vertical_cloud",
            "mode": "directional_mountain_visibility_sector",
            "available": False,
            "eligible": False,
            "reason": "camera_weather_or_elevation_missing",
        }

    camera_blocked = (
        camera_vis < 12000
        or (camera_low >= 90 and camera_rh >= 94)
        or (camera_precip is not None and camera_precip >= 1.0)
    )
    if camera_blocked:
        return {
            "module": "spatial_weather_vertical_cloud",
            "mode": "directional_mountain_visibility_sector",
            "available": True,
            "eligible": False,
            "reason": "camera_not_clear_enough_for_distant_mountain_view",
            "camera_visibility_km": round(camera_vis / 1000.0, 1),
            "camera_low_cloud": round(camera_low),
            "camera_rh": round(camera_rh),
            "readable_target_count": 0,
            "readable_bearing_count": 0,
            "target_resolution": observation.get("target_resolution"),
            "exact_target_zone_verified": False,
            "visibility_guaranteed": False,
            "confidence_hint": "low",
        }

    min_gain = float(config.get("min_target_elevation_gain_m", 250.0))
    elevated_targets = []
    readable_targets = []
    opaque_targets = []
    readable_bearings = set()

    for target in observation.get("targets", []) or []:
        elevation = _number(target.get("elevation_m"))
        vis = _number(target.get("visibility"))
        low = _number(target.get("cloud_cover_low"))
        rh = _number(target.get("relative_humidity_2m"))
        precip = _number(target.get("precipitation"))
        weather_code = target.get("weather_code")
        if elevation is None or vis is None or low is None or rh is None:
            continue
        if elevation - camera_elevation < min_gain:
            continue

        row = dict(target)
        row["elevation_gain_m"] = elevation - camera_elevation
        elevated_targets.append(row)

        fog_code = weather_code in {45, 48}
        opaque = (
            fog_code
            or vis < 3000
            or (low >= 90 and rh >= 90)
            or (precip is not None and precip >= 1.0)
        )
        if opaque:
            opaque_targets.append(row)
            continue

        readable = (
            vis >= 8000
            and low <= 80
            and (precip is None or precip < 1.0)
        )
        if readable:
            readable_targets.append(row)
            bearing = _number(row.get("bearing_deg"))
            if bearing is not None:
                readable_bearings.add(round(bearing, 1))

    if len(elevated_targets) < 2:
        return {
            "module": "spatial_weather_vertical_cloud",
            "mode": "directional_mountain_visibility_sector",
            "available": False,
            "eligible": False,
            "reason": "insufficient_elevated_directional_samples",
            "elevated_target_count": len(elevated_targets),
            "target_resolution": observation.get("target_resolution"),
            "exact_target_zone_verified": False,
            "visibility_guaranteed": False,
        }

    required_targets = min(int(config.get("min_readable_targets", 2)), len(elevated_targets))
    required_bearings = min(int(config.get("min_readable_bearings", 2)), len({
        round(_number(row.get("bearing_deg")), 1)
        for row in elevated_targets
        if _number(row.get("bearing_deg")) is not None
    }))
    eligible = (
        len(readable_targets) >= required_targets
        and len(readable_bearings) >= required_bearings
    )
    return {
        "module": "spatial_weather_vertical_cloud",
        "mode": "directional_mountain_visibility_sector",
        "available": True,
        "eligible": eligible,
        "reason": (
            "directional_mountain_view_readable"
            if eligible else "directional_mountain_view_not_readable"
        ),
        "camera_visibility_km": round(camera_vis / 1000.0, 1),
        "camera_low_cloud": round(camera_low),
        "camera_rh": round(camera_rh),
        "elevated_target_count": len(elevated_targets),
        "readable_target_count": len(readable_targets),
        "readable_bearing_count": len(readable_bearings),
        "opaque_target_count": len(opaque_targets),
        "min_readable_target_visibility_km": (
            round(min(_number(row.get("visibility")) for row in readable_targets) / 1000.0, 1)
            if readable_targets else None
        ),
        "max_readable_target_low_cloud_pct": (
            round(max(_number(row.get("cloud_cover_low")) for row in readable_targets))
            if readable_targets else None
        ),
        "target_resolution": observation.get("target_resolution"),
        "exact_target_zone_verified": False,
        "visibility_guaranteed": False,
        "confidence_hint": "medium" if eligible else "low",
    }


def evaluate_spatial_weather(opportunity, item_data):
    oid = opportunity.get("opportunity_id")
    config = _profile_config(oid)
    if not config:
        return {
            "module": "spatial_weather_vertical_cloud",
            "available": False,
            "eligible": False,
            "reason": "opportunity_spatial_config_missing",
        }

    observation = (item_data.get("spatial_weather") or {}).get(oid)
    if not observation or not observation.get("camera"):
        return {
            "module": "spatial_weather_vertical_cloud",
            "available": False,
            "eligible": False,
            "reason": "spatial_samples_missing",
        }

    if config.get("mode") == "directional_mist_sector":
        return _evaluate_directional_mist_sector(config, observation)
    if config.get("mode") == "directional_mountain_cloud_sector":
        return _evaluate_directional_mountain_cloud_sector(config, observation, item_data)
    if config.get("mode") == "directional_mountain_visibility_sector":
        return _evaluate_directional_mountain_visibility_sector(config, observation)

    camera = observation["camera"]
    camera_elevation = _number(observation.get("camera_reference_elevation_m"))
    if camera_elevation is None:
        camera_elevation = _number(camera.get("elevation_m"))
    if camera_elevation is None:
        return {
            "module": "spatial_weather_vertical_cloud",
            "available": False,
            "eligible": False,
            "reason": "camera_elevation_missing",
        }

    camera_vis = _number(camera.get("visibility"))
    camera_low = _number(camera.get("cloud_cover_low"))
    camera_rh = _number(camera.get("relative_humidity_2m"))
    camera_precip = _number(camera.get("precipitation"))
    camera_temp = _number(camera.get("temperature_2m"))
    camera_dew = _number(camera.get("dew_point_2m"))
    camera_dewpoint_spread = None
    camera_lcl_agl_proxy = None
    if camera_temp is not None and camera_dew is not None:
        camera_dewpoint_spread = max(0.0, camera_temp - camera_dew)
        # Planning-grade lifting-condensation-level proxy. This is not an
        # observed cloud base; it is only used as a conservative local
        # saturation/intersection veto for cloud-sea photography.
        camera_lcl_agl_proxy = camera_dewpoint_spread * 125.0

    if camera_vis is None or camera_low is None or camera_rh is None:
        return {
            "module": "spatial_weather_vertical_cloud",
            "available": False,
            "eligible": False,
            "reason": "camera_weather_missing",
        }

    camera_whiteout = (
        camera_vis < 5000
        or (camera_low >= 90 and camera_rh >= 95)
        or (camera_precip is not None and camera_precip >= 1.0)
    )
    camera_clear_enough = (
        not camera_whiteout
        and camera_vis >= 7000
        and not (camera_low >= 85 and camera_rh >= 95)
    )
    if not camera_clear_enough:
        return {
            "module": "spatial_weather_vertical_cloud",
            "available": True,
            "eligible": False,
            "reason": "camera_not_clear_enough",
            "camera_visibility_km": round(camera_vis / 1000.0, 1),
            "camera_low_cloud": round(camera_low),
            "camera_rh": round(camera_rh),
            "target_resolution": observation.get("target_resolution"),
            "exact_target_zone_verified": False,
        }

    # Grid visibility can remain deceptively usable when an elevated viewpoint
    # is actually brushing saturated orographic cloud. Add a second veto using
    # the local dew-point spread (LCL proxy) plus RH/low-cloud context. This
    # catches "camera inside cloud" cases that the coarse visibility field can
    # otherwise miss.
    camera_in_cloud_risk = False
    if camera_lcl_agl_proxy is not None:
        camera_in_cloud_risk = (
            (camera_lcl_agl_proxy <= 125 and camera_rh >= 94)
            or (
                camera_lcl_agl_proxy <= 225
                and camera_rh >= 92
                and camera_low >= 70
            )
            or (
                camera_lcl_agl_proxy <= 315
                and camera_rh >= 90
                and camera_low >= 80
                and camera_vis < 10000
            )
        )
    if camera_in_cloud_risk:
        return {
            "module": "spatial_weather_vertical_cloud",
            "available": True,
            "eligible": False,
            "reason": "camera_in_cloud_risk",
            "camera_visibility_km": round(camera_vis / 1000.0, 1),
            "camera_low_cloud": round(camera_low),
            "camera_rh": round(camera_rh),
            "camera_dewpoint_spread_c": round(camera_dewpoint_spread, 1),
            "camera_lcl_agl_proxy_m": round(camera_lcl_agl_proxy),
            "target_resolution": observation.get("target_resolution"),
            "exact_target_zone_verified": False,
        }

    lower_targets = []
    evidence_targets = []
    for target in observation.get("targets", []) or []:
        target_elevation = _number(target.get("elevation_m"))
        if target_elevation is None:
            continue
        vertical_drop = camera_elevation - target_elevation
        if vertical_drop < config["min_vertical_drop_m"]:
            continue

        row = dict(target)
        row["vertical_drop_m"] = vertical_drop
        lower_targets.append(row)

        vis = _number(target.get("visibility"))
        low = _number(target.get("cloud_cover_low"))
        rh = _number(target.get("relative_humidity_2m"))
        precip = _number(target.get("precipitation"))
        if vis is None or low is None or rh is None:
            continue
        if precip is not None and precip >= 1.0:
            continue

        fog_signal = vis <= 6000 and rh >= 88
        low_cloud_signal = vis <= 10000 and rh >= 90 and low >= 70
        if fog_signal or low_cloud_signal:
            evidence_targets.append(row)

    if len(lower_targets) < 2:
        return {
            "module": "spatial_weather_vertical_cloud",
            "available": False,
            "eligible": False,
            "reason": "insufficient_lower_terrain_samples",
            "lower_target_count": len(lower_targets),
            "target_resolution": observation.get("target_resolution"),
            "exact_target_zone_verified": False,
        }

    required_evidence = min(config["min_cloudy_targets"], len(lower_targets))
    eligible = len(evidence_targets) >= required_evidence
    max_drop = max((row["vertical_drop_m"] for row in evidence_targets), default=0.0)

    return {
        "module": "spatial_weather_vertical_cloud",
        "available": True,
        "eligible": eligible,
        "reason": "camera_clear_lower_cloud_detected" if eligible else "lower_cloud_not_detected",
        "camera_elevation_m": round(camera_elevation),
        "camera_visibility_km": round(camera_vis / 1000.0, 1),
        "camera_low_cloud": round(camera_low),
        "camera_rh": round(camera_rh),
        "camera_dewpoint_spread_c": (
            None if camera_dewpoint_spread is None else round(camera_dewpoint_spread, 1)
        ),
        "camera_lcl_agl_proxy_m": (
            None if camera_lcl_agl_proxy is None else round(camera_lcl_agl_proxy)
        ),
        "camera_in_cloud_risk": False,
        "lower_target_count": len(lower_targets),
        "cloud_evidence_target_count": len(evidence_targets),
        "max_evidence_vertical_drop_m": round(max_drop),
        "target_resolution": observation.get("target_resolution"),
        "exact_target_zone_verified": False,
        "confidence_hint": "medium" if eligible else "low",
    }


def validate_spatial_weather_registry():
    errors = []
    expected = set(_SUPPORTED_PROFILE_IDS) | {"tw-036-P03", "tw-036-P04"}
    if set(SPATIAL_WEATHER_PROFILES) != expected:
        errors.append("spatial profile registry mismatch")
    for oid, config in SPATIAL_WEATHER_PROFILES.items():
        if not oid.startswith("tw-"):
            errors.append(f"{oid}: invalid opportunity id")
        mode = config.get("mode")
        if mode == "lower_cloud_below_camera":
            if float(config["sample_distance_km"]) <= 0:
                errors.append(f"{oid}: invalid sample distance")
            if float(config["min_vertical_drop_m"]) < 100:
                errors.append(f"{oid}: vertical drop threshold too small")
            if int(config["min_cloudy_targets"]) < 1:
                errors.append(f"{oid}: invalid evidence target count")
        elif mode == "directional_mountain_cloud_sector":
            if len(config.get("bearings_deg") or ()) < 3:
                errors.append(f"{oid}: insufficient mountain-cloud bearings")
            if len(config.get("sample_distances_km") or ()) < 2:
                errors.append(f"{oid}: insufficient mountain-cloud distance bands")
            if any(float(x) <= 0 for x in config.get("sample_distances_km") or ()):
                errors.append(f"{oid}: invalid mountain-cloud sample distance")
            if float(config.get("min_target_elevation_gain_m") or 0) < 100:
                errors.append(f"{oid}: mountain-cloud elevation gain too small")
            if int(config.get("min_cloudy_targets") or 0) < 1:
                errors.append(f"{oid}: invalid mountain-cloud target count")
            if int(config.get("min_directional_cloud_targets") or 0) < 1:
                errors.append(f"{oid}: invalid directional-cloud target count")
            if int(config.get("orographic_proxy_min_intersection_targets") or 0) < 1:
                errors.append(f"{oid}: invalid orographic intersection target count")
            if int(config.get("orographic_proxy_min_intersection_bearings") or 0) < 1:
                errors.append(f"{oid}: invalid orographic intersection bearing count")
            if not 0 < float(config.get("orographic_proxy_max_visibility_ratio") or 0) < 1:
                errors.append(f"{oid}: invalid orographic visibility ratio")
            if float(config.get("orographic_proxy_max_visibility_km") or 0) <= 0:
                errors.append(f"{oid}: invalid orographic visibility threshold")
            if not 0 <= float(config.get("orographic_proxy_min_low_cloud_pct") or -1) <= 100:
                errors.append(f"{oid}: invalid orographic low-cloud threshold")
            if int(config.get("orographic_proxy_min_readable_targets") or 0) < 1:
                errors.append(f"{oid}: invalid orographic readable target count")
            if int(config.get("orographic_proxy_min_readable_bearings") or 0) < 1:
                errors.append(f"{oid}: invalid orographic readable bearing count")
        elif mode == "directional_mountain_visibility_sector":
            if len(config.get("bearings_deg") or ()) < 3:
                errors.append(f"{oid}: insufficient mountain-visibility bearings")
            if len(config.get("sample_distances_km") or ()) < 2:
                errors.append(f"{oid}: insufficient mountain-visibility distance bands")
            if any(float(x) <= 0 for x in config.get("sample_distances_km") or ()):
                errors.append(f"{oid}: invalid mountain-visibility sample distance")
            if float(config.get("min_target_elevation_gain_m") or 0) < 100:
                errors.append(f"{oid}: mountain-visibility elevation gain too small")
            if int(config.get("min_readable_targets") or 0) < 1:
                errors.append(f"{oid}: invalid readable target count")
            if int(config.get("min_readable_bearings") or 0) < 1:
                errors.append(f"{oid}: invalid readable bearing count")
        else:
            errors.append(f"{oid}: invalid spatial profile mode {mode}")

    for oid, config in OPTIONAL_DIRECTIONAL_MIST_PROFILES.items():
        if not oid.startswith("tw-"):
            errors.append(f"{oid}: invalid optional directional-mist id")
        if config.get("mode") != "directional_mist_sector":
            errors.append(f"{oid}: invalid optional directional-mist mode")
        if len(config.get("bearings_deg") or ()) < 3:
            errors.append(f"{oid}: insufficient directional bearings")
        if len(config.get("sample_distances_km") or ()) < 1:
            errors.append(f"{oid}: missing directional sample distances")
        if any(float(x) <= 0 for x in config.get("sample_distances_km") or ()):
            errors.append(f"{oid}: invalid directional sample distance")
        if int(config.get("min_misty_targets") or 0) < 1:
            errors.append(f"{oid}: invalid directional mist target count")
    if set(SPATIAL_WEATHER_PROFILES) & set(OPTIONAL_DIRECTIONAL_MIST_PROFILES):
        errors.append("required and optional spatial registries overlap")
    return errors


_ERRORS = validate_spatial_weather_registry()
if _ERRORS:
    raise ValueError("Invalid spatial weather registry: " + "; ".join(_ERRORS))
