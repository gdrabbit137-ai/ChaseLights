import json
from collections import Counter

from opportunity_runtime import (
    DIRECTIONAL_HORIZON_SECTORS,
    IMPLEMENTED_COMPONENTS,
    dependency_state,
    evaluate_directional_horizon,
    evaluate_visibility,
    evaluate_water_surface,
    evaluate_snow_state,
    evaluate_radiation_dni,
    evaluate_cloud_light_state,
    evaluate_cloud_sky_glow,
    evaluate_astronomy_ephemeris,
    ASTRONOMY_EPHEMERIS_PROFILES,
    evaluate_opportunity_modules,
    validate_runtime_registry,
)
from runtime_dependencies import (
    FORMULA_DEPENDENCIES,
    OPPORTUNITY_DEPENDENCY_OVERRIDES,
    dependencies_for_status,
    dependencies_for_opportunity,
    validate_dependency_inventory,
)
from spatial_weather import (
    SPATIAL_WEATHER_PROFILES,
    build_spatial_request_plan,
    index_spatial_response,
    spatial_observations_for_timestamp,
    evaluate_spatial_weather,
    validate_spatial_weather_registry,
)

import analyze_weather
import fetch_data
from opportunities import (
    ADAPTER_VERSION,
    CATALOG_COUNTS,
    CURATED_OPPORTUNITIES,
    get_opportunities,
    runtime_policy,
    validate_curated_opportunities,
)
from regions import get_spots
from taxonomy_v004 import PRODUCT_STATUS_BY_SPOT, active_in_catalog, product_status, validate_taxonomy


def _all_opportunities():
    return [o for opportunities in CURATED_OPPORTUNITIES.values() for o in opportunities]


def test_adapter_integrity():
    assert ADAPTER_VERSION == "v0.04-r4.2-b22-preview"
    assert validate_curated_opportunities() == []
    assert validate_taxonomy() == []
    assert CATALOG_COUNTS == {
        "spots": 71,
        "opportunities": 174,
        "condition_variants": 182,
        "profile_viewpoint_relations": 179,
    }

    tw = get_spots("tw")
    assert len(tw) == 71
    assert [s["spot_id"] for s in tw] == [f"tw-{i:03d}" for i in range(1, 72)]
    assert PRODUCT_STATUS_BY_SPOT == {}
    assert all(product_status(s["spot_id"]) == "keep" for s in tw)
    assert all(active_in_catalog(s["spot_id"]) for s in tw)

    curated = {s["spot_id"]: s for s in tw if s.get("opportunities")}
    assert set(curated) == {f"tw-{i:03d}" for i in range(1, 72)}
    assert sum(len(s["opportunities"]) for s in curated.values()) == 174

    all_opportunities = _all_opportunities()
    assert sum(len(o["condition_variants"]) for o in all_opportunities) == 182
    assert sum(len(o["viewpoints"]) for o in all_opportunities) == 179
    assert not any(o["formula_status"] == "legacy_fallback_pending_curated" for o in all_opportunities)
    assert not any(str(o.get("formula_version") or "").startswith("legacy_") for o in all_opportunities)

    exact = {o["opportunity_id"] for o in all_opportunities if o["geometry_required"]}
    assert exact == {"tw-017-P01", "tw-028-P04", "tw-038-P02"}
    assert all(o["mode"] == "composition_specific" for o in all_opportunities if o["geometry_required"])
    assert all(o["geometry_required"] is False for o in all_opportunities if o["mode"] == "area_opportunity")

    policies = Counter(runtime_policy(o) for o in all_opportunities)
    assert policies == {
        "module_pending": 79,
        "preview_module_available": 52,
        "prototype_pending_certification": 41,
        "hold": 1,
        "data_insufficient": 1,
    }
    assert runtime_policy(next(o for o in all_opportunities if o["opportunity_id"] == "tw-052-P01")) == "hold"
    assert runtime_policy(next(o for o in all_opportunities if o["opportunity_id"] == "tw-017-P01")) == "data_insufficient"
    assert validate_runtime_registry() == []
    assert len(DIRECTIONAL_HORIZON_SECTORS) == 25
    directional = next(o for o in all_opportunities if o["opportunity_id"] == "tw-020-P01")
    assert runtime_policy(directional) == "preview_module_available"
    matched = evaluate_directional_horizon(directional, {
        "astronomy_valid": True,
        "sun_azimuth": 88.0,
        "sun_elevation": 1.5,
        "hour": 6,
    })
    assert matched["eligible"] is True
    assert matched["reason"] == "sector_match"
    wrong_daypart = evaluate_directional_horizon(directional, {
        "astronomy_valid": True,
        "sun_azimuth": 88.0,
        "sun_elevation": 1.5,
        "hour": 18,
    })
    assert wrong_daypart["eligible"] is False
    assert wrong_daypart["reason"] == "wrong_daypart"

    visibility = evaluate_visibility({"vis": 25000})
    assert visibility["eligible"] is True
    assert visibility["quality"] == "good"
    low_visibility = evaluate_visibility({"visibility": 4.5})
    assert low_visibility["eligible"] is False

    compound = next(o for o in all_opportunities if o["opportunity_id"] == "tw-009-P02")
    assert compound["formula_status"] == "needs_directional_horizon_visibility_module"
    assert runtime_policy(compound) == "preview_module_available"
    compound_result = evaluate_opportunity_modules(compound, {
        "astronomy_valid": True,
        "sun_azimuth": 250.0,
        "sun_elevation": 0.5,
        "hour": 18,
        "vis": 24000,
    })
    assert compound_result["available"] is True
    assert compound_result["eligible"] is True
    assert set(compound_result["modules"]) == {"directional_horizon", "visibility"}

    formula_statuses = {o["formula_status"] for o in all_opportunities}
    needs_statuses = {s for s in formula_statuses if s.startswith("needs_")}
    assert needs_statuses == set(FORMULA_DEPENDENCIES)
    assert validate_dependency_inventory(formula_statuses) == []
    assert dependencies_for_status("needs_dynamic_access_visibility_module") == ("dynamic_access", "visibility")
    assert dependencies_for_status("needs_directional_horizon_cloud_sky_glow_module") == ("directional_horizon", "cloud_sky_glow")
    assert IMPLEMENTED_COMPONENTS == {
        "directional_horizon", "visibility", "water_surface_state", "snow_state",
        "radiation_DNI", "cloud_light_state", "cloud_sky_glow",
        "spatial_weather_vertical_cloud", "astronomy_ephemeris"
    }
    assert dependencies_for_status("needs_radiation_module") == ("radiation_DNI", "cloud_light_state")
    assert dependencies_for_status("needs_radiation_cloud_module") == ("radiation_DNI", "cloud_sky_glow")

    water_surface_profiles = [
        o for o in all_opportunities if o["formula_status"] == "needs_water_surface_module"
    ]
    assert len(water_surface_profiles) == 4
    assert all(runtime_policy(o) == "preview_module_available" for o in water_surface_profiles)

    calm = evaluate_water_surface({"wind": 1.4, "precipitation": 0.0, "pop": 15})
    assert calm["eligible"] is True
    assert calm["quality"] == "mirror_candidate"
    usable = evaluate_water_surface({"wind": 2.2, "precipitation": 0.0, "pop": 30})
    assert usable["eligible"] is True
    assert usable["quality"] == "reflection_usable"
    rippled = evaluate_water_surface({"wind": 3.2, "precipitation": 0.0, "pop": 30})
    assert rippled["eligible"] is False
    assert rippled["reason"] == "surface_rippled"
    rainy = evaluate_water_surface({"wind": 1.0, "precipitation": 0.4, "pop": 80})
    assert rainy["eligible"] is False
    assert rainy["reason"] == "precipitation_disturbance"
    rough = evaluate_water_surface({"wind": 5.5, "precipitation": 0.0, "pop": 10})
    assert rough["eligible"] is False
    assert rough["reason"] == "wind_too_strong"
    probability_only = evaluate_water_surface({"wind": 1.0, "pop": 80})
    assert probability_only["eligible"] is True
    assert probability_only["confidence_hint"] == "low"

    pure_water = water_surface_profiles[0]
    water_result = evaluate_opportunity_modules(pure_water, {"wind": 1.6, "precipitation": 0.0, "pop": 20})
    assert water_result["available"] is True
    assert water_result["eligible"] is True
    assert water_result["required_components"] == ("water_surface_state",)
    assert set(water_result["modules"]) == {"water_surface_state"}

    lighting_water = next(
        o for o in all_opportunities
        if o["formula_status"] == "needs_lighting_water_surface_module"
    )
    lighting_state = dependency_state(lighting_water)
    assert lighting_state["ready_components"] == ("water_surface_state",)
    assert lighting_state["missing_components"] == ("managed_lighting_state",)
    assert runtime_policy(lighting_water) == "module_pending"
    partial = evaluate_opportunity_modules(lighting_water, {"wind": 1.0, "precipitation": 0.0, "pop": 10})
    assert partial["available"] is False
    assert partial["reason"] == "runtime_contract_pending"
    assert set(partial["modules"]) == {"water_surface_state"}

    snow_profiles = [
        o for o in all_opportunities if o["formula_status"] == "needs_snow_state_module"
    ]
    assert {o["opportunity_id"] for o in snow_profiles} == {
        "tw-019-P06", "tw-040-P03", "tw-041-P05", "tw-044-P03"
    }
    assert all(runtime_policy(o) == "preview_module_available" for o in snow_profiles)

    existing = evaluate_snow_state({"snow_depth": 0.08, "snowfall": 0.0})
    assert existing["eligible"] is True
    assert existing["state"] == "established_snow_cover"
    fresh = evaluate_snow_state({"snow_depth": 0.0, "snowfall": 1.2})
    assert fresh["eligible"] is True
    assert fresh["state"] == "fresh_snowfall"
    fresh_on_cover = evaluate_snow_state({"snow_depth": 0.03, "snowfall": 0.8})
    assert fresh_on_cover["eligible"] is True
    assert fresh_on_cover["state"] == "fresh_snow_on_cover"
    trace = evaluate_snow_state({"snow_depth": 0.0, "snowfall": 0.1})
    assert trace["eligible"] is False
    assert trace["state"] == "trace_snowfall"
    missing_snow = evaluate_snow_state({})
    assert missing_snow["available"] is False
    assert missing_snow["rime_evaluated"] is False

    snow_result = evaluate_opportunity_modules(
        next(o for o in snow_profiles if o["opportunity_id"] == "tw-041-P05"),
        {"snow_depth": 0.06, "snowfall": 0.0},
    )
    assert snow_result["available"] is True
    assert snow_result["eligible"] is True
    assert snow_result["required_components"] == ("snow_state",)
    assert set(snow_result["modules"]) == {"snow_state"}
    assert snow_result["modules"]["snow_state"]["rime_evaluated"] is False

    radiation_profile = next(
        o for o in all_opportunities if o["opportunity_id"] == "tw-035-P02"
    )
    assert radiation_profile["formula_status"] == "needs_radiation_module"
    assert runtime_policy(radiation_profile) == "preview_module_available"
    strong_dni = evaluate_radiation_dni({"direct_normal_irradiance": 320})
    assert strong_dni["eligible"] is True
    weak_dni = evaluate_radiation_dni({"direct_normal_irradiance": 55})
    assert weak_dni["eligible"] is False
    broken_cloud = evaluate_cloud_light_state({
        "c_low": 20, "c_mid": 55, "c_high": 25, "pop": 20
    })
    assert broken_cloud["eligible"] is True
    opaque_cloud = evaluate_cloud_light_state({
        "c_low": 95, "c_mid": 90, "c_high": 80, "pop": 30
    })
    assert opaque_cloud["eligible"] is False
    radiation_result = evaluate_opportunity_modules(radiation_profile, {
        "direct_normal_irradiance": 320,
        "c_low": 20, "c_mid": 55, "c_high": 25, "pop": 20,
    })
    assert radiation_result["available"] is True
    assert radiation_result["eligible"] is True
    assert set(radiation_result["modules"]) == {"radiation_DNI", "cloud_light_state"}

    assert OPPORTUNITY_DEPENDENCY_OVERRIDES == {
        "tw-013-P02": ("radiation_DNI", "cloud_sky_glow"),
        "tw-026-P02": ("cloud_sky_glow",),
        "tw-030-P02": ("cloud_sky_glow",),
        "tw-020-P02": ("spatial_weather_vertical_cloud", "directional_horizon"),
        "tw-024-P02": ("spatial_weather_vertical_cloud", "directional_horizon"),
        "tw-043-P02": ("spatial_weather_vertical_cloud", "directional_horizon"),
        "tw-047-P02": ("spatial_weather_vertical_cloud", "directional_horizon"),
    }

    terrain_glow = next(
        o for o in all_opportunities if o["opportunity_id"] == "tw-013-P02"
    )
    assert dependencies_for_opportunity(terrain_glow) == ("radiation_DNI", "cloud_sky_glow")
    assert runtime_policy(terrain_glow) == "preview_module_available"
    terrain_cloud = evaluate_cloud_sky_glow(terrain_glow, {
        "astronomy_valid": True, "sun_azimuth": 270, "sun_elevation": 6, "hour": 17,
        "c_low": 25, "c_mid": 50, "c_high": 40, "precipitation": 0.0, "pop": 20,
    })
    assert terrain_cloud["eligible"] is True
    assert terrain_cloud["mode"] == "terrain_illumination"

    glow_profile = next(
        o for o in all_opportunities if o["opportunity_id"] == "tw-026-P02"
    )
    assert dependencies_for_opportunity(glow_profile) == ("cloud_sky_glow",)
    assert runtime_policy(glow_profile) == "preview_module_available"
    afterglow = evaluate_cloud_sky_glow(glow_profile, {
        "astronomy_valid": True, "sun_azimuth": 275, "sun_elevation": -3, "hour": 18,
        "c_low": 20, "c_mid": 55, "c_high": 35, "precipitation": 0.0, "pop": 20,
        "direct_normal_irradiance": 0,
    })
    assert afterglow["eligible"] is True
    assert afterglow["reason"] == "sky_glow_potential"
    assert afterglow["color_observed"] is False

    blocked_glow = evaluate_cloud_sky_glow(glow_profile, {
        "astronomy_valid": True, "sun_azimuth": 275, "sun_elevation": -3, "hour": 18,
        "c_low": 92, "c_mid": 90, "c_high": 90, "precipitation": 0.0, "pop": 20,
    })
    assert blocked_glow["eligible"] is False
    assert blocked_glow["reason"] == "low_horizon_cloud_blocked"

    cloudless_glow = evaluate_cloud_sky_glow(glow_profile, {
        "astronomy_valid": True, "sun_azimuth": 275, "sun_elevation": -3, "hour": 18,
        "c_low": 5, "c_mid": 5, "c_high": 5, "precipitation": 0.0, "pop": 10,
    })
    assert cloudless_glow["eligible"] is False
    assert cloudless_glow["reason"] == "insufficient_mid_high_cloud_texture"

    liushishi_glow = next(
        o for o in all_opportunities if o["opportunity_id"] == "tw-035-P04"
    )
    assert runtime_policy(liushishi_glow) == "preview_module_available"
    liushishi_result = evaluate_opportunity_modules(liushishi_glow, {
        "astronomy_valid": True, "sun_azimuth": 272, "sun_elevation": -2, "hour": 18,
        "c_low": 20, "c_mid": 50, "c_high": 30, "precipitation": 0.0, "pop": 15,
    })
    assert liushishi_result["available"] is True
    assert liushishi_result["eligible"] is True
    assert set(liushishi_result["modules"]) == {"directional_horizon", "cloud_sky_glow"}

    assert validate_spatial_weather_registry() == []
    assert len(SPATIAL_WEATHER_PROFILES) == 19

    spatial_pure = [
        o for o in all_opportunities
        if o["formula_status"] == "needs_spatial_weather_module"
        and o["opportunity_id"] in SPATIAL_WEATHER_PROFILES
    ]
    assert len(spatial_pure) == 17
    assert all(runtime_policy(o) == "preview_module_available" for o in spatial_pure)

    unsupported_spatial = {
        o["opportunity_id"] for o in all_opportunities
        if o["formula_status"] == "needs_spatial_weather_module"
        and o["opportunity_id"] not in SPATIAL_WEATHER_PROFILES
    }
    assert unsupported_spatial == {"tw-025-P01", "tw-025-P02", "tw-026-P01"}
    assert all(
        runtime_policy(next(o for o in all_opportunities if o["opportunity_id"] == oid)) == "module_pending"
        for oid in unsupported_spatial
    )

    tw020 = next(s for s in tw if s["spot_id"] == "tw-020")
    spatial_plan = build_spatial_request_plan(tw020)
    assert set(spatial_plan["profiles"]) == {"tw-020-P02", "tw-020-P03"}
    assert len(spatial_plan["points"]) == 9
    assert spatial_plan["profiles"]["tw-020-P02"]["camera_point_id"] == spatial_plan["profiles"]["tw-020-P03"]["camera_point_id"]

    fake_raw = []
    ts = 1900000000
    for i, point in enumerate(spatial_plan["points"]):
        is_camera = point["role"] == "camera"
        if is_camera:
            elevation, vis, rh, low = 820, 20000, 72, 20
        elif i in (1, 2, 3):
            elevation, vis, rh, low = 350, 3500, 96, 92
        else:
            elevation, vis, rh, low = 500, 14000, 75, 25
        fake_raw.append({
            "elevation": elevation,
            "hourly": {
                "time": [ts],
                "relative_humidity_2m": [rh],
                "cloud_cover_low": [low],
                "visibility": [vis],
                "precipitation": [0.0],
                "wind_speed_10m": [1.5],
            },
        })
    indexed = index_spatial_response(spatial_plan, fake_raw)
    spatial_obs = spatial_observations_for_timestamp(indexed, ts)
    p02_spatial = next(o for o in tw020["opportunities"] if o["opportunity_id"] == "tw-020-P02")
    spatial_eval = evaluate_spatial_weather(p02_spatial, {"spatial_weather": spatial_obs})
    assert spatial_eval["available"] is True
    assert spatial_eval["eligible"] is True
    assert spatial_eval["cloud_evidence_target_count"] >= 2
    assert spatial_eval["exact_target_zone_verified"] is False
    assert spatial_eval["target_resolution"] == "radial_lower_terrain_proxy_not_exact_target_zone"

    p02_full = evaluate_opportunity_modules(p02_spatial, {
        "spatial_weather": spatial_obs,
        "astronomy_valid": True,
        "sun_azimuth": 90,
        "sun_elevation": 2,
        "hour": 6,
    })
    assert p02_full["available"] is True
    assert p02_full["eligible"] is True
    assert set(p02_full["modules"]) == {"spatial_weather_vertical_cloud", "directional_horizon"}

    fogged_raw = [dict(row) for row in fake_raw]
    fogged_raw[0] = {
        "elevation": 820,
        "hourly": {
            "time": [ts],
            "relative_humidity_2m": [99],
            "cloud_cover_low": [98],
            "visibility": [1800],
            "precipitation": [0.0],
            "wind_speed_10m": [1.0],
        },
    }
    fogged_obs = spatial_observations_for_timestamp(index_spatial_response(spatial_plan, fogged_raw), ts)
    fogged_eval = evaluate_spatial_weather(p02_spatial, {"spatial_weather": fogged_obs})
    assert fogged_eval["eligible"] is False
    assert fogged_eval["reason"] == "camera_not_clear_enough"

    tw014 = next(s for s in tw if s["spot_id"] == "tw-014")
    p014 = next(o for o in tw014["opportunities"] if o["opportunity_id"] == "tw-014-P02")
    p014_state = dependency_state(p014)
    assert p014_state["ready_components"] == ("spatial_weather_vertical_cloud",)
    assert p014_state["missing_components"] == ("dynamic_access",)
    assert runtime_policy(p014) == "module_pending"

    tw021 = next(s for s in tw if s["spot_id"] == "tw-021")
    p021 = next(o for o in tw021["opportunities"] if o["opportunity_id"] == "tw-021-P02")
    p021_state = dependency_state(p021)
    assert "spatial_weather_vertical_cloud" in p021_state["missing_components"]
    assert "dynamic_access" in p021_state["missing_components"]

    assert set(ASTRONOMY_EPHEMERIS_PROFILES) == {
        "tw-019-P05", "tw-024-P05", "tw-035-P05", "tw-036-P02",
        "tw-038-P02", "tw-040-P06", "tw-045-P03", "tw-070-P02",
    }

    pure_astro = [
        o for o in all_opportunities
        if o["formula_status"] == "needs_astronomy_ephemeris_module"
    ]
    assert {o["opportunity_id"] for o in pure_astro} == {"tw-035-P05", "tw-070-P02"}
    assert all(runtime_policy(o) == "preview_module_available" for o in pure_astro)

    astro_input = {
        "astronomy_valid": True,
        "astronomical_dark": True,
        "sun_elevation": -28,
        "galactic_core_azimuth": 185,
        "galactic_core_elevation": 32,
        "moon_azimuth": 45,
        "moon_elevation": -8,
        "moon_illumination": 75,
        "c_low": 10,
        "c_mid": 20,
        "c_high": 25,
        "vis": 30000,
        "bortle_class": 3,
        "dark_sky_score": 86,
    }
    astro_profile = next(o for o in pure_astro if o["opportunity_id"] == "tw-035-P05")
    astro_ok = evaluate_astronomy_ephemeris(astro_profile, astro_input)
    assert astro_ok["available"] is True
    assert astro_ok["eligible"] is True
    assert astro_ok["scene_state"] == "milky_way_core_visible"
    assert astro_ok["exact_alignment_verified"] is False

    overcast = dict(astro_input, c_low=85)
    astro_cloud = evaluate_astronomy_ephemeris(astro_profile, overcast)
    assert astro_cloud["eligible"] is False
    assert astro_cloud["reason"] == "night_sky_cloud_blocked"

    bright_moon = dict(
        astro_input,
        moon_azimuth=190,
        moon_elevation=35,
        moon_illumination=90,
    )
    astro_moon = evaluate_astronomy_ephemeris(astro_profile, bright_moon)
    assert astro_moon["eligible"] is False
    assert astro_moon["reason"] == "bright_moon_interference"

    star_field = dict(astro_input, galactic_core_elevation=-12)
    astro_star_field = evaluate_astronomy_ephemeris(astro_profile, star_field)
    assert astro_star_field["eligible"] is True
    assert astro_star_field["scene_state"] == "dark_star_field"

    astro_result = evaluate_opportunity_modules(astro_profile, astro_input)
    assert astro_result["available"] is True
    assert astro_result["eligible"] is True
    assert set(astro_result["modules"]) == {"astronomy_ephemeris"}

    access_astro = next(o for o in all_opportunities if o["opportunity_id"] == "tw-019-P05")
    access_astro_state = dependency_state(access_astro)
    assert access_astro_state["ready_components"] == ("astronomy_ephemeris",)
    assert access_astro_state["missing_components"] == ("dynamic_access",)
    assert runtime_policy(access_astro) == "module_pending"

    marine_astro = next(o for o in all_opportunities if o["opportunity_id"] == "tw-036-P02")
    marine_astro_state = dependency_state(marine_astro)
    assert marine_astro_state["ready_components"] == ("astronomy_ephemeris",)
    assert marine_astro_state["missing_components"] == ("marine_state",)
    assert runtime_policy(marine_astro) == "module_pending"

    lake_astro = next(o for o in all_opportunities if o["opportunity_id"] == "tw-045-P03")
    lake_astro_state = dependency_state(lake_astro)
    assert lake_astro_state["ready_components"] == ("astronomy_ephemeris", "water_surface_state")
    assert lake_astro_state["missing_components"] == ("dynamic_access",)
    assert runtime_policy(lake_astro) == "module_pending"

    exact_astro = next(o for o in all_opportunities if o["opportunity_id"] == "tw-038-P02")
    exact_state = dependency_state(exact_astro)
    assert exact_state["ready_components"] == ("astronomy_ephemeris",)
    assert set(exact_state["missing_components"]) == {
        "verified_camera_geometry", "dynamic_access", "managed_lighting_state"
    }
    assert runtime_policy(exact_astro) == "module_pending"
    exact_eval = evaluate_astronomy_ephemeris(exact_astro, astro_input)
    assert exact_eval["eligible"] is True
    assert exact_eval["scene_state"] == "galactic_core_visible_exact_alignment_pending"
    assert exact_eval["exact_alignment_verified"] is False

    tw052 = get_opportunities("tw", "tw-052")
    assert tw052[0]["runtime_policy"] == "hold"
    assert get_opportunities("jp", "jp-001") == []
    assert get_opportunities("us", "us-001") == []

    copy = get_opportunities("tw", "tw-001")
    copy[0]["condition_variants"][0]["variant_name"] = "mutated"
    assert CURATED_OPPORTUNITIES["tw-001"][0]["condition_variants"][0]["variant_name"] != "mutated"

    tw018 = next(s for s in tw if s["spot_id"] == "tw-018")
    p02 = next(o for o in tw018["opportunities"] if o["opportunity_id"] == "tw-018-P02")
    assert p02["runtime_policy"] == "preview_module_available"
    assert p02["runtime_dependency_state"]["complete"] is True
    assert p02["runtime_dependency_state"]["required_components"] == ("water_surface_state",)

    diag = fetch_data._build_opportunity_runtime_diagnostics(
        tw018, {"wind": 1.2, "precipitation": 0.0, "pop": 10}
    )
    assert set(diag) == {"tw-018-P02"}
    assert diag["tw-018-P02"]["available"] is True
    assert diag["tw-018-P02"]["eligible"] is True
    assert "score" not in diag["tw-018-P02"]

    tw019 = next(s for s in tw if s["spot_id"] == "tw-019")
    snow_diag = fetch_data._build_opportunity_runtime_diagnostics(
        tw019, {"snow_depth": 0.08, "snowfall": 0.0}
    )
    assert "tw-019-P06" in snow_diag
    assert snow_diag["tw-019-P06"]["available"] is True
    assert snow_diag["tw-019-P06"]["eligible"] is True
    assert "score" not in snow_diag["tw-019-P06"]

    tw035 = next(s for s in tw if s["spot_id"] == "tw-035")
    radiation_diag = fetch_data._build_opportunity_runtime_diagnostics(
        tw035, {
            "direct_normal_irradiance": 300,
            "c_low": 20, "c_mid": 55, "c_high": 25, "pop": 15,
            "astronomy_valid": True, "sun_azimuth": 270, "sun_elevation": 18, "hour": 16,
        }
    )
    assert "tw-035-P02" in radiation_diag
    assert radiation_diag["tw-035-P02"]["available"] is True
    assert radiation_diag["tw-035-P02"]["eligible"] is True
    assert "score" not in radiation_diag["tw-035-P02"]

    tw026 = next(s for s in tw if s["spot_id"] == "tw-026")
    glow_diag = fetch_data._build_opportunity_runtime_diagnostics(
        tw026, {
            "astronomy_valid": True, "sun_azimuth": 275, "sun_elevation": -3, "hour": 18,
            "c_low": 20, "c_mid": 55, "c_high": 35, "precipitation": 0.0, "pop": 20,
        }
    )
    assert "tw-026-P02" in glow_diag
    assert glow_diag["tw-026-P02"]["available"] is True
    assert glow_diag["tw-026-P02"]["eligible"] is True
    assert "score" not in glow_diag["tw-026-P02"]

    spatial_url = fetch_data._build_spatial_open_meteo_url(spatial_plan)
    assert "latitude=" in spatial_url and "%2C" not in spatial_url
    assert "cloud_cover_low" in spatial_url
    assert spatial_url.count(",") >= 16

    tw070 = next(s for s in tw if s["spot_id"] == "tw-070")
    astro_diag = fetch_data._build_opportunity_runtime_diagnostics(
        tw070, {
            "astronomy_valid": True,
            "astronomical_dark": True,
            "sun_elevation": -28,
            "galactic_core_azimuth": 180,
            "galactic_core_elevation": 28,
            "moon_azimuth": 20,
            "moon_elevation": -5,
            "moon_illumination": 80,
            "c_low": 10, "c_mid": 20, "c_high": 25,
            "vis": 30000,
            "bortle_class": 2,
            "dark_sky_score": 94,
        }
    )
    assert "tw-070-P02" in astro_diag
    assert astro_diag["tw-070-P02"]["available"] is True
    assert astro_diag["tw-070-P02"]["eligible"] is True
    assert "score" not in astro_diag["tw-070-P02"]

    weather_url = fetch_data._build_open_meteo_url({"lat": 25.0, "lon": 121.0})
    assert ",precipitation,precipitation_probability,snowfall,snow_depth,direct_normal_irradiance," in weather_url


def test_schema9_optional_metadata_bridge():
    spot = next(s for s in get_spots("tw") if s["spot_id"] == "tw-052")
    original = analyze_weather.fetch_weather_for_spot
    try:
        analyze_weather.fetch_weather_for_spot = lambda *args, **kwargs: {
            "api_elevation": 800,
            "timezone": "Asia/Taipei",
            "timezone_abbr": "CST",
            "utc_offset_seconds": 28800,
            "hourly_forecast": [],
        }
        summary, details = analyze_weather.analyze_spot(spot, kp_rows=[])
    finally:
        analyze_weather.fetch_weather_for_spot = original

    assert summary["spot_id"] == "tw-052"
    assert details["spot_id"] == "tw-052"
    assert summary["opportunities"] == details["opportunities"]
    assert summary["opportunities"][0]["runtime_policy"] == "hold"
    assert summary["themes"] == spot["themes"]
    assert summary["daily"] == []
    assert details["hourly_forecast"] == []
    json.dumps({"schema_version": 9, "spots": [summary]}, ensure_ascii=False)


if __name__ == "__main__":
    test_adapter_integrity()
    test_schema9_optional_metadata_bridge()
    print("v0.04 R4.2 full Opportunity adapter tests: PASS")
