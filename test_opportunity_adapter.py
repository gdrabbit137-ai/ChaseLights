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
    evaluate_opportunity_modules,
    validate_runtime_registry,
)
from runtime_dependencies import FORMULA_DEPENDENCIES, dependencies_for_status, validate_dependency_inventory

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
    assert ADAPTER_VERSION == "v0.04-r4.2-b19-preview"
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
        "module_pending": 102,
        "preview_module_available": 29,
        "prototype_pending_certification": 41,
        "hold": 1,
        "data_insufficient": 1,
    }
    assert runtime_policy(next(o for o in all_opportunities if o["opportunity_id"] == "tw-052-P01")) == "hold"
    assert runtime_policy(next(o for o in all_opportunities if o["opportunity_id"] == "tw-017-P01")) == "data_insufficient"
    assert validate_runtime_registry() == []
    assert len(DIRECTIONAL_HORIZON_SECTORS) == 20
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
        "radiation_DNI", "cloud_light_state"
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

    glow_profile = next(
        o for o in all_opportunities if o["opportunity_id"] == "tw-026-P02"
    )
    glow_state = dependency_state(glow_profile)
    assert glow_state["ready_components"] == ("radiation_DNI",)
    assert glow_state["missing_components"] == ("cloud_sky_glow",)
    assert runtime_policy(glow_profile) == "module_pending"

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
