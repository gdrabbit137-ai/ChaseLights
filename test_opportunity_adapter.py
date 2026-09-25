from pathlib import Path
import json
from datetime import datetime
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
    evaluate_minimum_sufficient_visibility,
    MINIMUM_SUFFICIENT_VISIBILITY_PROFILES,
    MINIMUM_SUFFICIENT_LOCAL_SCENE_PROFILES,
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
from marine_state import (
    MARINE_STATE_PROFILES,
    evaluate_marine_state,
    index_marine_response,
    marine_sample_for_timestamp,
    validate_marine_state_registry,
)
from tide_state import (
    TIDE_STATE_PROFILES,
    evaluate_tide_state,
    index_tide_response,
    tide_sample_for_timestamp,
    validate_tide_state_registry,
)
from access_state import (
    ACCESS_DEPENDENT_PROFILE_IDS,
    ACCESS_PROFILE_CLASSIFICATION,
    ACCESS_RUNTIME_READY_PROFILES,
    HARD_ACCESS_HOLDS,
    OFFICIAL_SOURCE_HINTS,
    evaluate_dynamic_access,
    validate_access_registry,
)
from shinhotaka_access import (
    JST,
    PROVIDER_VERSION as SHINHOTAKA_PROVIDER_VERSION,
    STARGAZING_DATES_2026,
    build_shinhotaka_access_state,
    parse_shinhotaka_homepage_status,
)
from yahiko_access import (
    NIGHT_CRUISE_DATES_2026,
    PROVIDER_VERSION as YAHIKO_PROVIDER_VERSION,
    build_yahiko_access_state,
    parse_yahiko_homepage_status,
)

import analyze_weather
import fetch_data
from opportunities import (
    ADAPTER_VERSION,
    CATALOG_COUNTS,
    REGION_CATALOG_COUNTS,
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
    assert ADAPTER_VERSION == "v0.04-r4.2-b32-jp-batch01-r25-preview"
    assert validate_curated_opportunities() == []
    assert validate_taxonomy() == []
    assert CATALOG_COUNTS == {
        "spots": 106,
        "opportunities": 223,
        "condition_variants": 233,
        "profile_viewpoint_relations": 228,
    }
    assert REGION_CATALOG_COUNTS["tw"] == {
        "spots": 80,
        "opportunities": 189,
        "condition_variants": 199,
        "profile_viewpoint_relations": 194,
    }
    assert REGION_CATALOG_COUNTS["jp"] == {
        "spots": 26,
        "opportunities": 34,
        "condition_variants": 34,
        "profile_viewpoint_relations": 34,
    }
    assert REGION_CATALOG_COUNTS["us"] == {
        "spots": 0,
        "opportunities": 0,
        "condition_variants": 0,
        "profile_viewpoint_relations": 0,
    }

    jp_catalog = json.loads(
        Path("runtime_catalog_v004_r4_2_b32_jp_batch01.json").read_text(encoding="utf-8")
    )
    assert jp_catalog["schema_version"] == "v0.04-r4.2-b32-jp-batch01-25"
    assert jp_catalog["spot_count"] == len(jp_catalog["spots"]) == 26
    assert jp_catalog["opportunity_count"] == sum(len(x.get("opportunities", [])) for x in jp_catalog["spots"]) == 34
    assert jp_catalog["condition_variant_count"] == sum(
        len(o.get("condition_variants", []))
        for x in jp_catalog["spots"]
        for o in x.get("opportunities", [])
    ) == 34
    assert jp_catalog["profile_viewpoint_relation_count"] == sum(
        len(o.get("viewpoints", []))
        for x in jp_catalog["spots"]
        for o in x.get("opportunities", [])
    ) == 34

    tw = get_spots("tw")
    assert len(tw) == 81
    assert [s["spot_id"] for s in tw] == [f"tw-{i:03d}" for i in range(1, 82)]
    assert PRODUCT_STATUS_BY_SPOT == {"tw-063": "retired"}
    assert product_status("tw-063") == "retired"
    assert active_in_catalog("tw-063") is False
    assert sum(1 for s in tw if active_in_catalog(s["spot_id"])) == 80
    assert all(
        product_status(s["spot_id"]) == "keep"
        for s in tw if s["spot_id"] != "tw-063"
    )

    curated = {s["spot_id"]: s for s in tw if s.get("opportunities")}
    expected_active = {f"tw-{i:03d}" for i in range(1, 82)} - {"tw-063"}
    assert set(curated) == expected_active
    assert "tw-063" not in CURATED_OPPORTUNITIES
    assert sum(len(s["opportunities"]) for s in curated.values()) == 189

    all_opportunities = _all_opportunities()
    assert sum(len(o["condition_variants"]) for o in all_opportunities) == 233
    assert sum(len(o["viewpoints"]) for o in all_opportunities) == 228
    assert not any(o["formula_status"] == "legacy_fallback_pending_curated" for o in all_opportunities)
    assert not any(str(o.get("formula_version") or "").startswith("legacy_") for o in all_opportunities)

    exact = {o["opportunity_id"] for o in all_opportunities if o["geometry_required"]}
    assert exact == {"tw-017-P01", "tw-028-P04", "tw-038-P02"}
    assert all(o["mode"] == "composition_specific" for o in all_opportunities if o["geometry_required"])
    assert all(o["geometry_required"] is False for o in all_opportunities if o["mode"] == "area_opportunity")

    policies = Counter(runtime_policy(o) for o in all_opportunities)
    assert policies == {
        "module_pending": 72,
        "preview_module_available": 84,
        "minimum_sufficient_available": 61,
        "prototype_pending_certification": 2,
        "hold": 2,
        "data_insufficient": 2,
    }
    assert len(MINIMUM_SUFFICIENT_VISIBILITY_PROFILES) == 59
    assert MINIMUM_SUFFICIENT_LOCAL_SCENE_PROFILES == {"jp-025-P01", "jp-026-P01"}

    # R4.2 Navigation Target contract: every Place has explicit state, but
    # only individually verified arrival targets may become Directions links.
    valid_navigation_statuses = {
        "verified", "provisional_camera_anchor", "needs_review", "multiple_access_routes"
    }
    for region in ("tw", "jp", "us"):
        for nav_spot in get_spots(region):
            target = nav_spot.get("navigation_target") or {}
            assert target.get("status") in valid_navigation_statuses, (
                nav_spot["spot_id"], target
            )
            if target.get("status") == "verified":
                assert isinstance(target.get("lat"), float)
                assert isinstance(target.get("lon"), float)

    jialuo = next(s for s in get_spots("tw") if s["name_i18n"]["zh-TW"] == "加羅湖")
    assert jialuo["navigation_target"]["status"] == "needs_review"
    assert "lat" not in jialuo["navigation_target"]
    assert "lon" not in jialuo["navigation_target"]

    nanya = next(s for s in get_spots("tw") if "南雅奇岩" in s["name_i18n"]["zh-TW"])
    assert nanya["navigation_target"]["status"] == "provisional_camera_anchor"
    assert nanya["navigation_target"]["lat"] == nanya["lat"]
    assert nanya["navigation_target"]["lon"] == nanya["lon"]

    deyue = next(o for o in get_opportunities("tw", "tw-062") if o["opportunity_id"] == "tw-062-P01")
    assert deyue["legacy_theme"] == "mountain_view"
    assert deyue["runtime_policy"] == "minimum_sufficient_available"

    assert runtime_policy(next(o for o in all_opportunities if o["opportunity_id"] == "tw-052-P01")) == "hold"
    assert runtime_policy(next(o for o in all_opportunities if o["opportunity_id"] == "tw-017-P01")) == "data_insufficient"
    assert validate_runtime_registry() == []
    assert len(DIRECTIONAL_HORIZON_SECTORS) == 49

    # Hint-semantic safety: blue hour is a light/time condition, not proof of
    # city lights. Architecture alone must never auto-create a city-night Theme.
    active_spots = [spot for spot in tw if active_in_catalog(spot["spot_id"])]
    non_city_night_spots = [
        spot for spot in active_spots
        if "city_night" in spot["themes"] and "city" not in spot["scenes"]
    ]
    assert {spot["name_i18n"]["zh-TW"] for spot in non_city_night_spots} == {
        "金龍山", "頂石棹", "田寮月世界", "金門慈湖"
    }
    night_probe = {
        "astronomy_valid": True,
        "sun_elevation": -12.0,
        "is_day": False,
        "is_twilight": False,
        "hour": 21,
        "c_low": 8,
        "c_mid": 20,
        "c_high": 25,
        "pop": 5,
        "wind": 2.0,
        "vis": 30000,
    }
    for spot in non_city_night_spots:
        probe = dict(night_probe, scenes=spot["scenes"])
        _, status, indicator, status_key, indicator_key, _ = fetch_data.evaluate_tag_condition(
            "city_night", probe, 21, "zh-TW"
        )
        assert status_key == "NIGHT_SCENE_CLEAR"
        assert indicator_key == "IND_NIGHT_SCENE_CLEAR"
        assert all(word not in (status + indicator) for word in ("城市", "燈火"))

    verified_city_night = next(
        spot for spot in active_spots
        if "city" in spot["scenes"] and "city_night" in spot["themes"]
    )
    city_probe = dict(night_probe, scenes=verified_city_night["scenes"])
    _, city_status, city_indicator, city_status_key, city_indicator_key, _ = fetch_data.evaluate_tag_condition(
        "city_night", city_probe, 21, "zh-TW"
    )
    assert city_status_key == "CITY_NIGHT_CLEAR"
    assert city_indicator_key == "IND_CITY_NIGHT_CLEAR"
    assert "城市" in city_status + city_indicator
    dongyin = next(spot for spot in active_spots if spot["name_i18n"]["zh-TW"] == "東引燈塔")
    assert "architecture" in dongyin["scenes"]
    assert "city" not in dongyin["scenes"]
    assert "city_night" not in dongyin["themes"]

    blue_hour_probe = {
        "astronomy_valid": True,
        "sun_elevation": -6.0,
        "is_day": False,
        "is_twilight": True,
        "hour": 18,
        "c_low": 8,
        "c_mid": 20,
        "c_high": 25,
        "pop": 5,
        "wind": 2.0,
        "vis": 30000,
    }
    for spot in active_spots:
        if "blue_hour" not in spot["themes"]:
            continue
        _, status, indicator, status_key, indicator_key, _ = fetch_data.evaluate_tag_condition(
            "blue_hour", blue_hour_probe, 18, "zh-TW"
        )
        assert status_key == "BLUE_HOUR_CLEAR"
        assert indicator_key == "IND_BLUE_HOUR_CLEAR"
        assert all(word not in (status + indicator) for word in ("城市", "燈火", "無霧"))

    limited_probe = dict(blue_hour_probe)
    limited_probe.pop("vis")
    _, _, _, limited_status_key, limited_indicator_key, _ = fetch_data.evaluate_tag_condition(
        "blue_hour", limited_probe, 18, "zh-TW"
    )
    assert limited_status_key == "WEATHER_DATA_LIMITED"
    assert limited_indicator_key == "IND_WEATHER_DATA_LIMITED"

    outside_probe = dict(blue_hour_probe, sun_elevation=-14.0, is_twilight=False)
    _, _, _, outside_status_key, outside_indicator_key, _ = fetch_data.evaluate_tag_condition(
        "blue_hour", outside_probe, 18, "zh-TW"
    )
    assert outside_status_key == "BLUE_HOUR_OUTSIDE"
    assert outside_indicator_key == "IND_BLUE_HOUR_OUTSIDE"

    cloud_sea_night = {
        "astronomy_valid": True,
        "sun_elevation": -18.0,
        "is_day": False,
        "is_twilight": False,
        "hour": 21,
        "c_low": 55,
        "c_mid": 30,
        "c_high": 20,
        "pop": 5,
        "wind": 1.0,
        "vis": 30000,
        "rh": 92,
        "temp": 16,
        "dew": 15,
        "cloud_base_delta": 100,
        "cloud_base_near_camera": False,
        "cloud_below_camera": True,
    }
    cloud_night_score, _, _, cloud_night_status, _, _ = fetch_data.evaluate_tag_condition(
        "cloud_sea", cloud_sea_night, 21, "zh-TW"
    )
    assert cloud_night_score <= 35
    assert cloud_night_status == "CLOUD_SEA_OUTSIDE"

    cloud_sea_after_civil = dict(
        cloud_sea_night,
        sun_elevation=-7.0,
        is_twilight=True,  # UI twilight may still be broad; score must use sun altitude.
        hour=19,
    )
    cloud_after_score, _, _, cloud_after_status, _, _ = fetch_data.evaluate_tag_condition(
        "cloud_sea", cloud_sea_after_civil, 19, "zh-TW"
    )
    assert cloud_after_score <= 35
    assert cloud_after_status == "CLOUD_SEA_OUTSIDE"

    # Homepage discovery must remain place-first. Scene/theme semantics belong to
    # the ranked result/explanation, not intersecting homepage filters.
    index_html = Path("index.html").read_text(encoding="utf-8")
    assert 'id="theme-nav"' not in index_html
    assert 'id="scene-nav"' not in index_html
    assert 'id="discovery-title"' in index_html
    assert 'id="place-search"' in index_html
    assert "FILTER_UI_VERSION='3'" in index_html
    assert "return day.all||null" in index_html

    assert 'id="place-modal-overlay"' in index_html
    assert "card.onclick=()=>openPlaceModal" in index_html
    assert "data-weather" in index_html
    assert "🌦️ 天氣預報" in index_html
    assert "點擊看 96H 明細" not in index_html
    assert "op.condition_variants" in index_html
    assert "day?.opportunities||{}" in index_html
    assert "const rankedOpportunities=opportunities.map((op,index)=>" in index_html
    assert "if(a.score===null)return 1;if(b.score===null)return -1;return (b.score-a.score)||(a.index-b.index);" in index_html
    assert "no_viable_opportunity" in index_html
    assert "今天剩餘時段沒有合適的已研究拍攝機會" in index_html
    assert "const researchPending=!!metric.research_pending||!spot.opportunities?.length;const hasScore=" in index_html
    assert "&&!researchPending&&!noViable" in index_html

    # B31: Weather Forecast must fetch only the selected Place detail shard.
    assert "chaselights-v11-weather" in index_html
    assert "./weather_details/${region}/${encodeURIComponent(spotId)}.json" in index_html
    assert "loadDetails(currentRegion,spot.spot_id)" in index_html
    assert "const detail=payload?.spot" in index_html
    assert "loadLegacyDetail(region,spotId)" in index_html
    assert "catch(shardError)" in index_html

    # R4.2 Navigation Target contract: map_query is metadata only. Browser
    # navigation must be built exclusively from exact navigation_target coords.
    assert "function navigationToolHtml(spot)" in index_html
    assert "data-navigation-mode" in index_html
    assert "/maps/dir/?api=1&destination=" in index_html
    assert "/maps/search/?api=1&query=" in index_html
    assert "const navQuery=spot.map_query" not in index_html
    assert "encodeURIComponent(navQuery)" not in index_html
    assert "map_query||`${spot.lat},${spot.lon}`" not in index_html

    # Time-zone contract: shooting windows remain Place-local; only Last Updated
    # follows the user's device/browser timezone.
    assert "拍攝時間皆以景點當地時區顯示" in index_html
    assert "適合時間（景點當地時間）" in index_html
    assert "timeZoneName:'short'" in index_html

    analyze_weather_src = Path("analyze_weather.py").read_text(encoding="utf-8")
    assert 'Path("weather_details") / region' in analyze_weather_src
    assert '"spot": detail' in analyze_weather_src
    assert 'existing.unlink()' in analyze_weather_src

    update_weather_workflow = Path(".github/workflows/update_weather.yml").read_text(encoding="utf-8")
    assert "weather_details/" in update_weather_workflow

    nanya = next(o for o in all_opportunities if o["opportunity_id"] == "tw-072-P01")
    assert runtime_policy(nanya) == "preview_module_available"
    assert dependency_state(nanya)["required_components"] == ("marine_state", "directional_horizon", "visibility")
    assert dependency_state(nanya)["complete"] is True

    laomei = next(o for o in all_opportunities if o["opportunity_id"] == "tw-073-P01")
    assert runtime_policy(laomei) == "module_pending"
    assert dependency_state(laomei)["ready_components"] == ("tide_state", "marine_state", "directional_horizon", "visibility")
    assert dependency_state(laomei)["missing_components"] == ("seasonal_foreground",)

    yehliu = next(o for o in all_opportunities if o["opportunity_id"] == "tw-074-P01")
    assert runtime_policy(yehliu) == "minimum_sufficient_available"
    assert dependency_state(yehliu)["ready_components"] == ("visibility",)
    assert dependency_state(yehliu)["missing_components"] == ("geology_light",)

    waiao = next(o for o in all_opportunities if o["opportunity_id"] == "tw-075-P01")
    assert runtime_policy(waiao) == "preview_module_available"
    assert dependency_state(waiao)["required_components"] == ("marine_state", "directional_horizon", "visibility")
    assert dependency_state(waiao)["complete"] is True

    waiao_low_vis = evaluate_opportunity_modules(
        waiao,
        {
            "sun_azimuth": 95.0,
            "sun_elevation": 2.0,
            "marine_forecast": {
                "wave_height": 0.5,
                "wave_period": 5.0,
                "swell_wave_height": 0.3,
                "swell_wave_period": 6.0,
            },
            "vis": 500,
        },
    )
    assert waiao_low_vis["available"] is True
    assert waiao_low_vis["eligible"] is False
    assert waiao_low_vis["modules"]["visibility"]["eligible"] is False

    longpan_sunrise = next(o for o in all_opportunities if o["opportunity_id"] == "tw-076-P01")
    assert runtime_policy(longpan_sunrise) == "preview_module_available"
    assert dependency_state(longpan_sunrise)["required_components"] == ("directional_horizon", "visibility")

    longpan_stars = next(o for o in all_opportunities if o["opportunity_id"] == "tw-076-P02")
    assert runtime_policy(longpan_stars) == "preview_module_available"
    assert dependency_state(longpan_stars)["required_components"] == ("astronomy_ephemeris",)

    shihtiping_tide = next(o for o in all_opportunities if o["opportunity_id"] == "tw-077-P02")
    assert runtime_policy(shihtiping_tide) == "preview_module_available"
    assert dependency_state(shihtiping_tide)["required_components"] == ("marine_state", "tide_state", "visibility")

    jiangong = next(o for o in all_opportunities if o["opportunity_id"] == "tw-078-P01")
    assert runtime_policy(jiangong) == "module_pending"
    assert dependency_state(jiangong)["ready_components"] == ("tide_state",)
    assert dependency_state(jiangong)["missing_components"] == ("dynamic_access",)
    assert not any(o["opportunity_id"] == "tw-078-P02" for o in all_opportunities)

    chixi_sunset = next(o for o in all_opportunities if o["opportunity_id"] == "tw-079-P01")
    assert runtime_policy(chixi_sunset) == "preview_module_available"
    assert dependency_state(chixi_sunset)["required_components"] == ("marine_state", "directional_horizon", "visibility")

    chixi_tide = next(o for o in all_opportunities if o["opportunity_id"] == "tw-079-P02")
    assert runtime_policy(chixi_tide) == "preview_module_available"
    assert dependency_state(chixi_tide)["required_components"] == ("marine_state", "tide_state", "visibility")

    fanchuanbi_sunrise = next(o for o in all_opportunities if o["opportunity_id"] == "tw-080-P01")
    assert runtime_policy(fanchuanbi_sunrise) == "preview_module_available"
    assert dependency_state(fanchuanbi_sunrise)["required_components"] == ("directional_horizon", "visibility")

    fanchuanbi_stars = next(o for o in all_opportunities if o["opportunity_id"] == "tw-080-P02")
    assert runtime_policy(fanchuanbi_stars) == "preview_module_available"
    assert dependency_state(fanchuanbi_stars)["required_components"] == ("astronomy_ephemeris",)

    iron_fort_day = next(o for o in all_opportunities if o["opportunity_id"] == "tw-081-P01")
    assert runtime_policy(iron_fort_day) == "module_pending"
    assert dependency_state(iron_fort_day)["ready_components"] == ("visibility",)
    assert dependency_state(iron_fort_day)["missing_components"] == ("dynamic_access",)

    assert not any(o["opportunity_id"] == "tw-081-P02" for o in all_opportunities)
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
    assert needs_statuses == set(FORMULA_DEPENDENCIES), {
        "missing_dependency_mappings": sorted(needs_statuses - set(FORMULA_DEPENDENCIES)),
        "unused_dependency_mappings": sorted(set(FORMULA_DEPENDENCIES) - needs_statuses),
    }
    assert validate_dependency_inventory(formula_statuses) == []
    assert dependencies_for_status("needs_dynamic_access_visibility_module") == ("dynamic_access", "visibility")
    assert dependencies_for_status("needs_directional_horizon_cloud_sky_glow_module") == ("directional_horizon", "cloud_sky_glow")
    assert IMPLEMENTED_COMPONENTS == {
        "directional_horizon", "visibility", "water_surface_state", "snow_state",
        "radiation_DNI", "cloud_light_state", "cloud_sky_glow",
        "spatial_weather_vertical_cloud", "astronomy_ephemeris", "marine_state",
        "tide_state", "dynamic_access"
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
        "tw-033-P01": ("marine_state", "directional_horizon", "visibility"),
        "tw-033-P02": ("marine_state", "directional_horizon", "visibility"),
        "tw-036-P01": ("marine_state", "directional_horizon", "visibility"),
        "tw-072-P01": ("marine_state", "directional_horizon", "visibility"),
        "tw-072-P02": ("marine_state", "directional_horizon", "visibility"),
        "tw-073-P01": ("seasonal_foreground", "tide_state", "marine_state", "directional_horizon", "visibility"),
        "tw-075-P01": ("marine_state", "directional_horizon", "visibility"),
        "tw-077-P01": ("marine_state", "directional_horizon", "visibility"),
        "tw-077-P02": ("marine_state", "tide_state", "visibility"),
        "tw-079-P01": ("marine_state", "directional_horizon", "visibility"),
        "tw-079-P02": ("marine_state", "tide_state", "visibility"),
        "tw-013-P02": ("radiation_DNI", "cloud_sky_glow", "visibility"),
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
    assert dependencies_for_opportunity(terrain_glow) == ("radiation_DNI", "cloud_sky_glow", "visibility")
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
        "jp-021-P02", "tw-019-P05", "tw-024-P05", "tw-035-P05", "tw-036-P02",
        "tw-038-P02", "tw-040-P06", "tw-045-P03", "tw-070-P02", "tw-076-P02", "tw-080-P02",
    }

    pure_astro = [
        o for o in all_opportunities
        if o["formula_status"] == "needs_astronomy_ephemeris_module"
    ]
    assert {o["opportunity_id"] for o in pure_astro} == {"tw-035-P05", "tw-070-P02", "tw-076-P02", "tw-080-P02"}
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
    assert marine_astro_state["ready_components"] == ("astronomy_ephemeris", "marine_state")
    assert marine_astro_state["missing_components"] == ()
    assert runtime_policy(marine_astro) == "preview_module_available"

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

    assert validate_marine_state_registry() == []
    assert set(MARINE_STATE_PROFILES) == {
        "tw-010-P01", "tw-010-P02", "tw-010-P03",
        "tw-033-P01", "tw-033-P02",
        "tw-036-P01", "tw-036-P02",
        "tw-071-P01", "tw-071-P02",
        "tw-072-P01", "tw-072-P02", "tw-073-P01",
        "tw-075-P01",
        "tw-077-P01", "tw-077-P02",
        "tw-079-P01", "tw-079-P02",
    }

    calm_marine = {
        "wave_height": 0.6,
        "wave_direction": 95,
        "wave_period": 5.5,
        "wind_wave_height": 0.3,
        "wind_wave_direction": 90,
        "wind_wave_period": 4.0,
        "swell_wave_height": 0.4,
        "swell_wave_direction": 100,
        "swell_wave_period": 7.0,
        "swell_wave_peak_period": 8.0,
        "sample_offset_seconds": 0,
    }
    marine_profile = next(
        o for o in all_opportunities if o["opportunity_id"] == "tw-033-P01"
    )
    calm_eval = evaluate_marine_state(
        marine_profile, {"marine_forecast": calm_marine}
    )
    assert calm_eval["available"] is True
    assert calm_eval["eligible"] is True
    assert calm_eval["tide_evaluated"] is False
    assert calm_eval["local_shore_safety_verified"] is False

    energetic_marine = dict(
        calm_marine,
        wave_height=1.4,
        swell_wave_height=0.9,
        swell_wave_period=11.0,
    )
    energetic_eval = evaluate_marine_state(
        marine_profile, {"marine_forecast": energetic_marine}
    )
    assert energetic_eval["eligible"] is False
    assert energetic_eval["reason"] == "elevated_marine_state"
    assert energetic_eval["local_shore_safety_verified"] is False

    marine_complete_ids = {
        "tw-033-P01", "tw-033-P02", "tw-036-P01",
        "tw-036-P02", "tw-071-P01", "tw-071-P02",
    }
    assert all(
        runtime_policy(next(o for o in all_opportunities if o["opportunity_id"] == oid))
        == "preview_module_available"
        for oid in marine_complete_ids
    )

    tw010_p01 = next(o for o in all_opportunities if o["opportunity_id"] == "tw-010-P01")
    state_010_p01 = dependency_state(tw010_p01)
    assert state_010_p01["ready_components"] == ("marine_state", "tide_state", "directional_horizon")
    assert state_010_p01["missing_components"] == ("dynamic_access",)
    assert runtime_policy(tw010_p01) == "module_pending"

    tw010_p02 = next(o for o in all_opportunities if o["opportunity_id"] == "tw-010-P02")
    state_010_p02 = dependency_state(tw010_p02)
    assert state_010_p02["ready_components"] == ("marine_state",)
    assert state_010_p02["missing_components"] == ("directional_horizon",)
    assert runtime_policy(tw010_p02) == "module_pending"

    tw010_p03 = next(o for o in all_opportunities if o["opportunity_id"] == "tw-010-P03")
    state_010_p03 = dependency_state(tw010_p03)
    assert state_010_p03["ready_components"] == ("marine_state", "directional_horizon")
    assert state_010_p03["missing_components"] == ("dynamic_access",)

    fake_marine_raw = {
        "latitude": 24.0,
        "longitude": 121.7,
        "elevation": 0.0,
        "hourly": {
            "time": [1900000000, 1900003600],
            "wave_height": [0.6, 0.8],
            "wave_direction": [95, 100],
            "wave_period": [5.5, 6.0],
            "wind_wave_height": [0.3, 0.4],
            "wind_wave_direction": [90, 95],
            "wind_wave_period": [4.0, 4.5],
            "swell_wave_height": [0.4, 0.5],
            "swell_wave_direction": [100, 105],
            "swell_wave_period": [7.0, 7.5],
            "swell_wave_peak_period": [8.0, 8.5],
        },
    }
    marine_index = index_marine_response(fake_marine_raw)
    marine_sample = marine_sample_for_timestamp(marine_index, 1900001800)
    assert marine_sample["wave_height"] in {0.6, 0.8}
    assert marine_sample["sample_offset_seconds"] == 1800

    tw033 = next(s for s in tw if s["spot_id"] == "tw-033")
    marine_diag = fetch_data._build_opportunity_runtime_diagnostics(
        tw033, {
            "marine_forecast": calm_marine,
            "astronomy_valid": True,
            "sun_azimuth": 92,
            "sun_elevation": 2,
            "hour": 6,
            "vis": 30000,
        }
    )
    assert "tw-033-P01" in marine_diag
    assert marine_diag["tw-033-P01"]["available"] is True
    assert marine_diag["tw-033-P01"]["eligible"] is True
    assert marine_diag["tw-033-P01"]["modules"]["marine_state"]["local_shore_safety_verified"] is False

    tw036 = next(s for s in tw if s["spot_id"] == "tw-036")
    astro_marine_diag = fetch_data._build_opportunity_runtime_diagnostics(
        tw036, {
            "marine_forecast": calm_marine,
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
            "bortle_class": 5,
            "dark_sky_score": 60,
        }
    )
    assert "tw-036-P02" in astro_marine_diag
    assert astro_marine_diag["tw-036-P02"]["available"] is True
    assert astro_marine_diag["tw-036-P02"]["eligible"] is True

    assert validate_tide_state_registry() == []
    assert set(TIDE_STATE_PROFILES) == {
        "tw-010-P01",
        "tw-012-P01", "tw-012-P02",
        "tw-015-P01", "tw-015-P02",
        "tw-017-P02",
        "tw-059-P01",
        "tw-060-P01", "tw-060-P02", "tw-060-P03",
        "tw-073-P01",
        "tw-077-P02",
        "tw-078-P01",
        "tw-079-P02",
    }

    fake_tide_raw = {
        "latitude": 24.0,
        "longitude": 120.5,
        "hourly": {
            "time": [1900000000 + i * 3600 for i in range(8)],
            "sea_level_height_msl": [-0.2, -0.4, -0.5, -0.35, -0.05, 0.25, 0.45, 0.2],
        },
    }
    tide_index = index_tide_response(fake_tide_raw)
    low_sample = tide_sample_for_timestamp(tide_index, 1900000000 + 2 * 3600)
    high_sample = tide_sample_for_timestamp(tide_index, 1900000000 + 6 * 3600)
    assert low_sample["relative_percentile"] < high_sample["relative_percentile"]
    assert low_sample["datum_note"] == "global_mean_sea_level_not_local_chart_datum"

    strict_profile = next(
        o for o in all_opportunities if o["opportunity_id"] == "tw-059-P01"
    )
    strict_eval = evaluate_tide_state(
        strict_profile, {"tide_forecast": low_sample}
    )
    assert strict_eval["available"] is True
    assert strict_eval["eligible"] is True
    assert strict_eval["absolute_local_tide_height_verified"] is False
    assert strict_eval["marine_state_evaluated"] is False

    strict_high = evaluate_tide_state(
        strict_profile, {"tide_forecast": high_sample}
    )
    assert strict_high["eligible"] is False

    reflection_profile = next(
        o for o in all_opportunities if o["opportunity_id"] == "tw-012-P02"
    )
    very_low = dict(low_sample, relative_percentile=5.0)
    reflection_low = evaluate_tide_state(
        reflection_profile, {"tide_forecast": very_low}
    )
    assert reflection_low["eligible"] is False
    assert reflection_low["reason"] == "too_low_for_reflective_water_film"

    tide_complete_ids = {
        "tw-012-P01", "tw-015-P01", "tw-017-P02",
        "tw-060-P01", "tw-060-P02", "tw-060-P03",
        "tw-079-P02",
    }
    assert all(
        runtime_policy(next(o for o in all_opportunities if o["opportunity_id"] == oid))
        == "preview_module_available"
        for oid in tide_complete_ids
    )

    for oid in {"tw-012-P02", "tw-015-P02"}:
        state = dependency_state(next(o for o in all_opportunities if o["opportunity_id"] == oid))
        assert set(state["ready_components"]) == {"tide_state", "water_surface_state"}
        assert state["missing_components"] == ("dynamic_access",)

    state_059 = dependency_state(strict_profile)
    assert state_059["ready_components"] == ("tide_state",)
    assert state_059["missing_components"] == ("dynamic_access",)

    tw060 = next(s for s in tw if s["spot_id"] == "tw-060")
    tide_diag = fetch_data._build_opportunity_runtime_diagnostics(
        tw060, {
            "tide_forecast": low_sample,
            "astronomy_valid": True,
            "sun_azimuth": 270,
            "sun_elevation": 1,
            "hour": 18,
        }
    )
    assert tide_diag["tw-060-P01"]["available"] is True
    assert tide_diag["tw-060-P01"]["eligible"] is True
    assert tide_diag["tw-060-P02"]["available"] is True
    assert tide_diag["tw-060-P02"]["eligible"] is True
    assert tide_diag["tw-060-P02"]["modules"]["tide_state"]["absolute_local_tide_height_verified"] is False

    assert validate_access_registry() == []
    dynamic_profiles = [
        o for o in all_opportunities
        if "dynamic_access" in dependencies_for_opportunity(o)
    ]
    assert len(dynamic_profiles) == 49
    assert {o["opportunity_id"] for o in dynamic_profiles} == set(ACCESS_DEPENDENT_PROFILE_IDS)
    assert set(ACCESS_PROFILE_CLASSIFICATION) == set(ACCESS_DEPENDENT_PROFILE_IDS)
    assert ACCESS_RUNTIME_READY_PROFILES == frozenset({"jp-021-P01", "jp-021-P02", "jp-022-P01", "jp-022-P02", "jp-022-P03"})
    assert HARD_ACCESS_HOLDS["tw-052"]["policy"] == "hold"
    assert {"tw-005", "tw-037", "tw-038", "tw-078", "tw-081", "jp-002", "jp-004", "jp-021"} <= set(OFFICIAL_SOURCE_HINTS)
    assert "tw-063" not in OFFICIAL_SOURCE_HINTS
    assert all(
        runtime_policy(o) == (
            "preview_module_available"
            if o["opportunity_id"] in ACCESS_RUNTIME_READY_PROFILES
            else "module_pending"
        )
        for o in dynamic_profiles
    )

    access_profile = next(
        o for o in all_opportunities if o["opportunity_id"] == "tw-038-P01"
    )
    missing_access = evaluate_dynamic_access(access_profile, {"timestamp": 1900000000})
    assert missing_access["available"] is False
    assert missing_access["reason"] == "authoritative_access_snapshot_missing"

    fresh_open = {
        "status": "open",
        "authoritative": True,
        "authority": "Official Agency",
        "source_url": "https://example.gov.tw/access",
        "source_kind": "official_status",
        "checked_at_epoch": 1900000000,
        "valid_until_epoch": 1900020000,
    }
    open_eval = evaluate_dynamic_access(
        access_profile,
        {"timestamp": 1900001200, "access_state": fresh_open},
    )
    assert open_eval["available"] is True
    assert open_eval["eligible"] is True
    assert open_eval["source_freshness_verified"] is True
    assert open_eval["runtime_provider_connected"] is False

    closed_eval = evaluate_dynamic_access(
        access_profile,
        {
            "timestamp": 1900001200,
            "access_state": dict(fresh_open, status="closed"),
        },
    )
    assert closed_eval["available"] is True
    assert closed_eval["eligible"] is False
    assert closed_eval["reason"] == "authoritative_access_not_open"

    stale_eval = evaluate_dynamic_access(
        access_profile,
        {
            "timestamp": 1900100000,
            "access_state": dict(
                fresh_open,
                checked_at_epoch=1900000000,
                valid_until_epoch=1900200000,
            ),
        },
    )
    assert stale_eval["available"] is False
    assert stale_eval["reason"] == "access_snapshot_stale"

    mountain_access = next(
        o for o in all_opportunities if o["opportunity_id"] == "tw-019-P01"
    )
    entitlement_eval = evaluate_dynamic_access(
        mountain_access,
        {
            "timestamp": 1900001200,
            "access_state": fresh_open,
        },
    )
    assert entitlement_eval["available"] is True
    assert entitlement_eval["eligible"] is False
    assert entitlement_eval["reason"] == "permit_booking_or_permission_unconfirmed"

    entitled_eval = evaluate_dynamic_access(
        mountain_access,
        {
            "timestamp": 1900001200,
            "access_state": dict(fresh_open, entitlement_confirmed=True),
        },
    )
    assert entitled_eval["available"] is True
    assert entitled_eval["eligible"] is True

    tw052 = get_opportunities("tw", "tw-052")
    assert tw052[0]["runtime_policy"] == "hold"
    jp001 = get_opportunities("jp", "jp-001")
    assert [o["opportunity_id"] for o in jp001] == ["jp-001-P01"]
    assert jp001[0]["runtime_policy"] == "data_insufficient"
    jp002 = get_opportunities("jp", "jp-002")
    assert [o["opportunity_id"] for o in jp002] == ["jp-002-P01"]
    assert jp002[0]["runtime_policy"] == "module_pending"
    assert dependencies_for_opportunity(jp002[0]) == ("spatial_weather_vertical_cloud", "dynamic_access")
    assert ACCESS_PROFILE_CLASSIFICATION["jp-002-P01"]["access_type"] == "transport_facility_status"
    jp003 = get_opportunities("jp", "jp-003")
    assert [o["opportunity_id"] for o in jp003] == ["jp-003-P01"]
    assert jp003[0]["runtime_policy"] == "minimum_sufficient_available"
    assert dependencies_for_opportunity(jp003[0]) == ("visibility",)
    jp004 = get_opportunities("jp", "jp-004")
    assert [o["opportunity_id"] for o in jp004] == ["jp-004-P01"]
    assert jp004[0]["runtime_policy"] == "module_pending"
    assert dependencies_for_opportunity(jp004[0]) == ("dynamic_access", "visibility")
    assert ACCESS_PROFILE_CLASSIFICATION["jp-004-P01"]["access_type"] == "transport_facility_status"
    jp005 = get_opportunities("jp", "jp-005")
    assert [o["opportunity_id"] for o in jp005] == ["jp-005-P01", "jp-005-P02"]
    assert jp005[0]["runtime_policy"] == "minimum_sufficient_available"
    assert jp005[1]["runtime_policy"] == "module_pending"
    assert dependencies_for_opportunity(jp005[0]) == ("visibility",)
    assert dependencies_for_opportunity(jp005[1]) == ("managed_lighting_state",)

    jp008 = get_opportunities("jp", "jp-008")
    assert [o["opportunity_id"] for o in jp008] == ["jp-008-P01"]
    assert jp008[0]["runtime_policy"] == "preview_module_available"
    assert dependencies_for_opportunity(jp008[0]) == ("directional_horizon", "visibility")
    assert DIRECTIONAL_HORIZON_SECTORS["jp-008-P01"] == {
        "center": 98.0, "tolerance": 22.5, "phase": "sunrise"
    }
    matsushima_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp008},
        {
            "astronomy_valid": True, "sun_azimuth": 98.0, "sun_elevation": -1.0,
            "hour": 6, "vis": 30000,
        },
    )
    assert matsushima_diag["jp-008-P01"]["available"] is True
    assert matsushima_diag["jp-008-P01"]["eligible"] is True
    assert matsushima_diag["jp-008-P01"]["modules"]["directional_horizon"]["angle_diff"] == 0.0
    assert matsushima_diag["jp-008-P01"]["modules"]["visibility"]["eligible"] is True

    jp006 = get_opportunities("jp", "jp-006")
    assert [o["opportunity_id"] for o in jp006] == ["jp-006-P01"]
    assert jp006[0]["runtime_policy"] == "minimum_sufficient_available"
    assert dependencies_for_opportunity(jp006[0]) == ("visibility",)
    mashu_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp006},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0},
    )
    assert mashu_diag["jp-006-P01"]["available"] is True
    assert mashu_diag["jp-006-P01"]["eligible"] is True

    jp007 = get_opportunities("jp", "jp-007")
    assert [o["opportunity_id"] for o in jp007] == ["jp-007-P01"]
    assert jp007[0]["runtime_policy"] == "minimum_sufficient_available"
    assert dependencies_for_opportunity(jp007[0]) == ("visibility",)
    towada_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp007},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0},
    )
    assert towada_diag["jp-007-P01"]["available"] is True
    assert towada_diag["jp-007-P01"]["eligible"] is True

    jp013 = get_opportunities("jp", "jp-013")
    assert [o["opportunity_id"] for o in jp013] == ["jp-013-P01"]
    assert jp013[0]["runtime_policy"] == "preview_module_available"
    assert dependencies_for_opportunity(jp013[0]) == ("directional_horizon", "visibility")
    suwa_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp013},
        {
            "astronomy_valid": True,
            "sun_azimuth": 270.0,
            "sun_elevation": -1.0,
            "hour": 17,
            "vis": 30000,
        },
    )
    assert suwa_diag["jp-013-P01"]["available"] is True
    assert suwa_diag["jp-013-P01"]["eligible"] is True
    assert suwa_diag["jp-013-P01"]["modules"]["directional_horizon"]["angle_diff"] == 0.0
    assert suwa_diag["jp-013-P01"]["modules"]["visibility"]["eligible"] is True

    jp019 = get_opportunities("jp", "jp-019")
    assert [o["opportunity_id"] for o in jp019] == ["jp-019-P01"]
    assert jp019[0]["runtime_policy"] == "preview_module_available"
    assert dependencies_for_opportunity(jp019[0]) == ("directional_horizon", "visibility")
    hamanako_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp019},
        {
            "astronomy_valid": True,
            "sun_azimuth": 250.0,
            "sun_elevation": -1.0,
            "hour": 17,
            "vis": 30000,
        },
    )
    assert hamanako_diag["jp-019-P01"]["available"] is True
    assert hamanako_diag["jp-019-P01"]["eligible"] is True
    assert hamanako_diag["jp-019-P01"]["modules"]["directional_horizon"]["angle_diff"] == 0.0
    assert hamanako_diag["jp-019-P01"]["modules"]["visibility"]["eligible"] is True

    jp011 = get_opportunities("jp", "jp-011")
    assert [o["opportunity_id"] for o in jp011] == ["jp-011-P01", "jp-011-P02"]
    assert [o["legacy_theme"] for o in jp011] == ["mountain_view", "city_night"]
    assert all(o["runtime_policy"] == "minimum_sufficient_available" for o in jp011)
    assert all(dependencies_for_opportunity(o) == ("visibility",) for o in jp011)
    tokyo_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp011},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0, "access_open": True},
    )
    assert all(tokyo_diag[oid]["available"] is True and tokyo_diag[oid]["eligible"] is True
               for oid in ("jp-011-P01", "jp-011-P02"))
    tokyo_closed_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp011},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0, "access_open": False},
    )
    assert all(tokyo_closed_diag[oid]["eligible"] is False
               for oid in ("jp-011-P01", "jp-011-P02"))

    jp012 = get_opportunities("jp", "jp-012")
    assert [o["opportunity_id"] for o in jp012] == ["jp-012-P01"]
    assert jp012[0]["runtime_policy"] == "minimum_sufficient_available"
    assert dependencies_for_opportunity(jp012[0]) == ("visibility",)
    kamakura_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp012},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0, "access_open": True},
    )
    assert kamakura_diag["jp-012-P01"]["available"] is True
    assert kamakura_diag["jp-012-P01"]["eligible"] is True
    kamakura_closed_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp012},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0, "access_open": False},
    )
    assert kamakura_closed_diag["jp-012-P01"]["eligible"] is False

    jp015 = get_opportunities("jp", "jp-015")
    assert [o["opportunity_id"] for o in jp015] == ["jp-015-P01"]
    assert jp015[0]["runtime_policy"] == "minimum_sufficient_available"
    assert dependencies_for_opportunity(jp015[0]) == ("visibility",)
    nijubashi_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp015},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0, "access_open": True},
    )
    assert nijubashi_diag["jp-015-P01"]["available"] is True
    assert nijubashi_diag["jp-015-P01"]["eligible"] is True

    jp016 = get_opportunities("jp", "jp-016")
    assert [o["opportunity_id"] for o in jp016] == ["jp-016-P01", "jp-016-P02"]
    assert all(o["runtime_policy"] == "minimum_sufficient_available" for o in jp016)
    assert all(dependencies_for_opportunity(o) == ("visibility",) for o in jp016)
    yamashita_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp016},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0},
    )
    assert yamashita_diag["jp-016-P01"]["available"] is True
    assert yamashita_diag["jp-016-P01"]["eligible"] is True
    assert yamashita_diag["jp-016-P02"]["available"] is True
    assert yamashita_diag["jp-016-P02"]["eligible"] is True

    jp017 = get_opportunities("jp", "jp-017")
    assert [o["opportunity_id"] for o in jp017] == ["jp-017-P01"]
    assert jp017[0]["runtime_policy"] == "minimum_sufficient_available"
    assert dependencies_for_opportunity(jp017[0]) == ("visibility",)
    kenroku_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp017},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0, "access_open": True},
    )
    assert kenroku_diag["jp-017-P01"]["available"] is True
    assert kenroku_diag["jp-017-P01"]["eligible"] is True
    kenroku_closed_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp017},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0, "access_open": False},
    )
    assert kenroku_closed_diag["jp-017-P01"]["eligible"] is False

    jp018 = get_opportunities("jp", "jp-018")
    assert [o["opportunity_id"] for o in jp018] == ["jp-018-P01"]
    assert jp018[0]["runtime_policy"] == "minimum_sufficient_available"
    assert dependencies_for_opportunity(jp018[0]) == ("visibility",)
    nagoya_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp018},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0, "access_open": True},
    )
    assert nagoya_diag["jp-018-P01"]["available"] is True
    assert nagoya_diag["jp-018-P01"]["eligible"] is True
    nagoya_closed_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp018},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0, "access_open": False},
    )
    assert nagoya_closed_diag["jp-018-P01"]["eligible"] is False

    jp014 = get_opportunities("jp", "jp-014")
    assert [o["opportunity_id"] for o in jp014] == ["jp-014-P01"]
    assert jp014[0]["runtime_policy"] == "hold"
    assert dependencies_for_opportunity(jp014[0]) == ()
    assert "撮影は受け付けておりません" in jp014[0]["condition_variants"][0]["hard_gates"]
    todoroki_spot = next(s for s in get_spots("jp") if s["spot_id"] == "jp-014")
    assert abs(todoroki_spot["lat"] - 35.607857) < 1e-9
    assert abs(todoroki_spot["lon"] - 139.646545) < 1e-9
    assert todoroki_spot["map_query"] == "等々力渓谷 ゴルフ橋"
    assert todoroki_spot["navigation_target"]["status"] == "verified"
    assert todoroki_spot["navigation_target"]["target_type"] == "street_access"
    assert abs(todoroki_spot["navigation_target"]["lat"] - 35.607857) < 1e-9
    assert abs(todoroki_spot["navigation_target"]["lon"] - 139.646545) < 1e-9

    jp025 = get_opportunities("jp", "jp-025")
    assert [o["opportunity_id"] for o in jp025] == ["jp-025-P01", "jp-025-P02"]
    assert jp025[0]["runtime_policy"] == "minimum_sufficient_available"
    assert jp025[1]["runtime_policy"] == "module_pending"
    assert dependencies_for_opportunity(jp025[0]) == ()
    assert dependencies_for_opportunity(jp025[1]) == ("event_state",)
    assert dependency_state(jp025[1])["ready_components"] == ()
    assert dependency_state(jp025[1])["missing_components"] == ("event_state",)
    hagi_spot = next(s for s in get_spots("jp") if s["spot_id"] == "jp-025")
    assert abs(hagi_spot["lat"] - 34.4119363) < 1e-9
    assert abs(hagi_spot["lon"] - 131.3932271) < 1e-9
    assert hagi_spot["map_query"] == "菊屋横町 萩市"
    assert hagi_spot["name_i18n"]["zh-TW"] == "萩城下町・菊屋橫町"
    assert set(hagi_spot["themes"]) == {"mountain_view", "city_night"}
    assert hagi_spot["navigation_target"]["status"] == "verified"
    assert hagi_spot["navigation_target"]["target_type"] == "street_access"
    assert abs(hagi_spot["navigation_target"]["lat"] - 34.4119363) < 1e-9
    assert abs(hagi_spot["navigation_target"]["lon"] - 131.3932271) < 1e-9

    # Close-range historic streetscape: benign overcast / low long-range
    # visibility must not suppress the researched local scene.
    hagi_local_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp025},
        {
            "pop": 5,
            "precipitation": 0.0,
            "access_open": True,
            "c_low": 100,
            "vis": 1000,
        },
    )
    assert hagi_local_diag["jp-025-P01"]["available"] is True
    assert hagi_local_diag["jp-025-P01"]["eligible"] is True
    assert hagi_local_diag["jp-025-P01"]["minimum_sufficient_score_hint"] == 88
    assert "minimum_sufficient_local_scene" in hagi_local_diag["jp-025-P01"]["modules"]

    hagi_scored = fetch_data._score_opportunity(
        jp025[0],
        {
            "score": 40,
            "factors": [],
            "status_key": "MOUNTAIN_FOG_DAY",
            "indicator_key": "IND_NO_STAR",
            "temporal_eligible": True,
        },
        hagi_local_diag["jp-025-P01"],
    )
    assert hagi_scored["score"] == 88
    assert hagi_scored["condition_state"] == "minimum_sufficient_conditions_match"

    hagi_outside = fetch_data._score_opportunity(
        jp025[0],
        {
            "score": 40,
            "factors": [],
            "status_key": "MOUNTAIN_STABLE_NIGHT",
            "indicator_key": "IND_NIGHT_CLEAR",
            "temporal_eligible": False,
        },
        hagi_local_diag["jp-025-P01"],
    )
    assert hagi_outside["score"] == 40
    assert hagi_outside["condition_state"] == "minimum_sufficient_weather_match_outside_time_window"

    hagi_rain_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp025},
        {"pop": 70, "precipitation": 1.0, "access_open": True},
    )
    assert hagi_rain_diag["jp-025-P01"]["available"] is True
    assert hagi_rain_diag["jp-025-P01"]["eligible"] is False

    izumo = next(s for s in get_spots("jp") if s["spot_id"] == "jp-026")
    assert izumo["navigation_target"]["status"] == "multiple_access_routes"
    assert "lat" not in izumo["navigation_target"]
    assert izumo["access_hours"] == ["06:00", "19:00"]
    assert izumo["themes"] == ["mountain_view"]
    jp026 = get_opportunities("jp", "jp-026")
    assert [o["opportunity_id"] for o in jp026] == ["jp-026-P01"]
    assert jp026[0]["runtime_policy"] == "minimum_sufficient_available"
    assert dependencies_for_opportunity(jp026[0]) == ()
    assert jp026[0]["viewpoints"][0]["coord_confidence"] == "medium"
    izumo_diags = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp026},
        {"pop": 5, "precipitation": 0.0, "access_open": True, "c_low": 100, "vis": 1000},
    )
    assert izumo_diags["jp-026-P01"]["minimum_sufficient_score_hint"] == 88
    assert fetch_data._score_opportunity(
        jp026[0], {"score": 40, "temporal_eligible": True}, izumo_diags["jp-026-P01"]
    )["score"] == 88
    closed_diags = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp026},
        {"pop": 5, "precipitation": 0.0, "access_open": False},
    )
    assert closed_diags["jp-026-P01"]["eligible"] is False

    jp024 = get_opportunities("jp", "jp-024")
    assert [o["opportunity_id"] for o in jp024] == ["jp-024-P01"]
    assert jp024[0]["runtime_policy"] == "minimum_sufficient_available"
    assert dependencies_for_opportunity(jp024[0]) == ("visibility",)
    osaka_spot = next(s for s in get_spots("jp") if s["spot_id"] == "jp-024")
    assert abs(osaka_spot["lat"] - 34.6892) < 1e-6
    assert abs(osaka_spot["lon"] - 135.52675) < 1e-6
    assert osaka_spot["map_query"] == "大阪城 極楽橋"
    osaka_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp024},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0, "access_open": True},
    )
    assert osaka_diag["jp-024-P01"]["available"] is True
    assert osaka_diag["jp-024-P01"]["eligible"] is True

    jp023 = get_opportunities("jp", "jp-023")
    assert [o["opportunity_id"] for o in jp023] == ["jp-023-P01"]
    assert jp023[0]["runtime_policy"] == "minimum_sufficient_available"
    assert dependencies_for_opportunity(jp023[0]) == ("visibility",)
    assert "三腳架" in jp023[0]["condition_variants"][0]["hard_gates"]
    kiyomizu_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp023},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0, "access_open": True},
    )
    assert kiyomizu_diag["jp-023-P01"]["available"] is True
    assert kiyomizu_diag["jp-023-P01"]["eligible"] is True
    kiyomizu_closed_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp023},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0, "access_open": False},
    )
    assert kiyomizu_closed_diag["jp-023-P01"]["eligible"] is False

    jp020 = get_opportunities("jp", "jp-020")
    assert [o["opportunity_id"] for o in jp020] == ["jp-020-P01"]
    assert jp020[0]["runtime_policy"] == "minimum_sufficient_available"
    assert dependencies_for_opportunity(jp020[0]) == ("visibility",)
    minato_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp020},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0},
    )
    assert minato_diag["jp-020-P01"]["available"] is True
    assert minato_diag["jp-020-P01"]["eligible"] is True

    shinhotaka_spot = next(spot for spot in get_spots("jp") if spot["spot_id"] == "jp-021")
    assert abs(shinhotaka_spot["lat"] - 36.268335) < 1e-9
    assert abs(shinhotaka_spot["lon"] - 137.60158) < 1e-9
    assert shinhotaka_spot["elevation"] == 2156
    assert shinhotaka_spot["coordinate_confidence"] == "high"
    assert shinhotaka_spot["map_query"] == "西穂高口駅 新穂高ロープウェイ"
    assert set(shinhotaka_spot["themes"]) >= {"mountain_view", "milky_way"}
    assert shinhotaka_spot["navigation_target"]["status"] == "needs_review"
    assert "lat" not in shinhotaka_spot["navigation_target"]
    assert "lon" not in shinhotaka_spot["navigation_target"]

    jp021 = get_opportunities("jp", "jp-021")
    assert [o["opportunity_id"] for o in jp021] == ["jp-021-P01", "jp-021-P02"]
    assert all(o["runtime_policy"] == "preview_module_available" for o in jp021)
    assert dependencies_for_opportunity(jp021[0]) == ("dynamic_access", "visibility")
    assert dependencies_for_opportunity(jp021[1]) == ("astronomy_ephemeris", "dynamic_access")
    assert dependency_state(jp021[0])["ready_components"] == ("dynamic_access", "visibility")
    assert dependency_state(jp021[0])["missing_components"] == ()
    assert dependency_state(jp021[1])["ready_components"] == ("astronomy_ephemeris", "dynamic_access")
    assert dependency_state(jp021[1])["missing_components"] == ()
    assert ACCESS_PROFILE_CLASSIFICATION["jp-021-P01"]["access_type"] == "transport_facility_status"
    assert ACCESS_PROFILE_CLASSIFICATION["jp-021-P02"]["access_type"] == "event_access_control"

    # Shinhotaka provider is fixture-tested and live-page-tested.  The two
    # Opportunities are now runtime-ready; direct evaluator tests below retain
    # fail-closed coverage for stale, ambiguous and schedule-only states.
    assert SHINHOTAKA_PROVIDER_VERSION == "shinhotaka-access-r1-preview"
    assert len(STARGAZING_DATES_2026) == 18

    def jst_epoch(year, month, day, hour, minute=0):
        return datetime(year, month, day, hour, minute, tzinfo=JST).timestamp()

    fixture_dir = Path("test_fixtures")
    open_html = (fixture_dir / "shinhotaka_home_open.html").read_text(encoding="utf-8")
    suspended_html = (fixture_dir / "shinhotaka_home_no2_suspended.html").read_text(encoding="utf-8")
    ambiguous_html = (fixture_dir / "shinhotaka_home_ambiguous.html").read_text(encoding="utf-8")
    event_open_html = (fixture_dir / "shinhotaka_home_event_open.html").read_text(encoding="utf-8")

    open_provider = parse_shinhotaka_homepage_status(
        open_html, fetched_at_epoch=jst_epoch(2026, 9, 25, 8, 5)
    )
    assert open_provider["parse_ok"] is True
    assert open_provider["no1_status"] == "open"
    assert open_provider["no2_status"] == "open"
    assert open_provider["checked_at_epoch"] == jst_epoch(2026, 9, 25, 8, 0)

    p01_time = jst_epoch(2026, 9, 25, 10, 0)
    p01_state = build_shinhotaka_access_state(p01_time, open_provider)["jp-021-P01"]
    assert p01_state["status"] == "open"
    assert p01_state["freshness_mode"] == "live"
    p01_eval = evaluate_dynamic_access(
        jp021[0], {"timestamp": p01_time, "access_state": {"jp-021-P01": p01_state}}
    )
    assert p01_eval["available"] is True
    assert p01_eval["eligible"] is True
    assert p01_eval["runtime_provider_connected"] is True

    suspended_provider = parse_shinhotaka_homepage_status(
        suspended_html, fetched_at_epoch=jst_epoch(2026, 9, 25, 8, 5)
    )
    assert suspended_provider["parse_ok"] is True
    assert suspended_provider["no2_status"] == "closed"
    suspended_state = build_shinhotaka_access_state(
        p01_time, suspended_provider
    )["jp-021-P01"]
    assert suspended_state["status"] == "closed"
    assert evaluate_dynamic_access(
        jp021[0], {"timestamp": p01_time, "access_state": suspended_state}
    )["eligible"] is False

    ambiguous_provider = parse_shinhotaka_homepage_status(
        ambiguous_html, fetched_at_epoch=jst_epoch(2026, 9, 25, 8, 5)
    )
    assert ambiguous_provider["parse_ok"] is False
    assert ambiguous_provider["no2_status"] == "unknown"
    ambiguous_state = build_shinhotaka_access_state(
        p01_time, ambiguous_provider
    )["jp-021-P01"]
    assert ambiguous_state["status"] == "unknown"
    assert evaluate_dynamic_access(
        jp021[0], {"timestamp": p01_time, "access_state": ambiguous_state}
    )["eligible"] is False

    maintenance_time = jst_epoch(2026, 11, 25, 12, 0)
    maintenance_state = build_shinhotaka_access_state(
        maintenance_time, open_provider
    )["jp-021-P01"]
    assert maintenance_state["status"] == "closed"
    assert maintenance_state["freshness_mode"] == "schedule"
    maintenance_eval = evaluate_dynamic_access(
        jp021[0], {"timestamp": maintenance_time, "access_state": maintenance_state}
    )
    assert maintenance_eval["available"] is True
    assert maintenance_eval["eligible"] is False
    assert maintenance_eval["status_basis"] == "official_2026_full_line_maintenance_closure"

    ordinary_night = jst_epoch(2026, 10, 15, 20, 0)
    ordinary_p02 = build_shinhotaka_access_state(
        ordinary_night, open_provider
    )["jp-021-P02"]
    assert ordinary_p02["status"] == "closed"
    assert ordinary_p02["freshness_mode"] == "schedule"
    assert evaluate_dynamic_access(
        jp021[1], {"timestamp": ordinary_night, "access_state": ordinary_p02}
    )["eligible"] is False

    event_provider = parse_shinhotaka_homepage_status(
        event_open_html, fetched_at_epoch=jst_epoch(2026, 10, 2, 19, 5)
    )
    assert event_provider["parse_ok"] is True
    assert event_provider["no1_status"] == "closed"
    assert event_provider["no2_status"] == "open"
    event_time = jst_epoch(2026, 10, 2, 19, 30)
    event_p02 = build_shinhotaka_access_state(
        event_time, event_provider
    )["jp-021-P02"]
    assert event_p02["status"] == "open"
    assert event_p02["freshness_mode"] == "live"
    event_eval = evaluate_dynamic_access(
        jp021[1], {"timestamp": event_time, "access_state": event_p02}
    )
    assert event_eval["available"] is True
    assert event_eval["eligible"] is True

    daytime_event_provider = dict(
        open_provider,
        checked_at_epoch=jst_epoch(2026, 10, 2, 14, 0),
        visible_update_text="10 / 02 14:00 update",
    )
    event_requires_night_confirmation = build_shinhotaka_access_state(
        event_time, daytime_event_provider
    )["jp-021-P02"]
    assert event_requires_night_confirmation["status"] == "unknown"
    assert evaluate_dynamic_access(
        jp021[1],
        {"timestamp": event_time, "access_state": event_requires_night_confirmation},
    )["eligible"] is False

    future_year_event = jst_epoch(2027, 10, 2, 19, 30)
    future_p02 = build_shinhotaka_access_state(
        future_year_event, event_provider
    )["jp-021-P02"]
    assert future_p02["status"] == "unknown"
    assert future_p02["status_basis"] == "stargazing_schedule_not_verified_for_year"

    weekday_early = jst_epoch(2026, 10, 2, 8, 20)
    weekend_early = jst_epoch(2026, 10, 3, 8, 20)
    weekday_state = build_shinhotaka_access_state(
        weekday_early, open_provider
    )["jp-021-P01"]
    weekend_state = build_shinhotaka_access_state(
        weekend_early, open_provider
    )["jp-021-P01"]
    assert weekday_state["status"] == "closed"
    assert weekday_state["timetable_first_ascent"] == "08:45"
    assert weekend_state["timetable_first_ascent"] == "08:15"

    stale_time = jst_epoch(2026, 9, 25, 15, 30)
    stale_p01 = build_shinhotaka_access_state(
        stale_time, open_provider
    )["jp-021-P01"]
    stale_p01_eval = evaluate_dynamic_access(
        jp021[0], {"timestamp": stale_time, "access_state": stale_p01}
    )
    assert stale_p01_eval["available"] is False
    assert stale_p01_eval["reason"] == "access_snapshot_stale"

    synthetic_schedule_open = {
        "status": "open",
        "authoritative": True,
        "authority": "Shinhotaka Ropeway",
        "source_url": "https://shinhotaka-ropeway.jp/pdf/pamphlet/en.pdf",
        "source_kind": "official_ropeway_timetable",
        "freshness_mode": "schedule",
        "status_basis": "test_static_open_must_not_unlock_live_facility",
    }
    schedule_open_eval = evaluate_dynamic_access(
        jp021[0], {"timestamp": p01_time, "access_state": synthetic_schedule_open}
    )
    assert schedule_open_eval["available"] is True
    assert schedule_open_eval["eligible"] is False
    assert schedule_open_eval["reason"] == "live_access_confirmation_required"

    # jp-022 Yahiko: the official homepage can prove today's ropeway operation,
    # while Skyline schedule-only access remains fail-closed.
    assert YAHIKO_PROVIDER_VERSION == "yahiko-access-r1-preview"
    assert len(NIGHT_CRUISE_DATES_2026) == 10
    yahiko_html = """
    <section><h2>本日のロープウェイ情報</h2>
    <div>始 発</div><b>09:00</b>
    <div>上り</div><div>最終</div><b>16:40</b>
    <div>下り</div><div>最終</div><b>17:00</b>
    <p>15分間隔</p><strong>通常営業</strong></section>
    """
    yahiko_provider = parse_yahiko_homepage_status(
        yahiko_html, fetched_at_epoch=jst_epoch(2026, 9, 25, 10, 0)
    )
    assert yahiko_provider["parse_ok"] is True
    assert yahiko_provider["status"] == "open"
    assert yahiko_provider["first_ascent"] == "09:00"
    assert yahiko_provider["last_ascent"] == "16:40"
    assert yahiko_provider["last_descent"] == "17:00"

    jp022 = get_opportunities("jp", "jp-022")
    assert [o["opportunity_id"] for o in jp022] == ["jp-022-P01", "jp-022-P02", "jp-022-P03"]
    assert all(o["runtime_policy"] == "preview_module_available" for o in jp022)

    yahiko_day = jst_epoch(2026, 9, 25, 11, 0)
    yahiko_day_state = build_yahiko_access_state(yahiko_day, yahiko_provider)
    for oid in ("jp-022-P01", "jp-022-P02"):
        assert yahiko_day_state[oid]["status"] == "open"
        evaluation = evaluate_dynamic_access(
            next(o for o in jp022 if o["opportunity_id"] == oid),
            {"timestamp": yahiko_day, "access_state": yahiko_day_state[oid]},
        )
        assert evaluation["available"] is True
        assert evaluation["eligible"] is True

    yahiko_after_ropeway = jst_epoch(2026, 9, 25, 18, 0)
    after_state = build_yahiko_access_state(yahiko_after_ropeway, yahiko_provider)["jp-022-P02"]
    assert after_state["status"] == "unknown"
    assert after_state["freshness_mode"] == "schedule"
    assert after_state["status_basis"] == "ropeway_outside_window_and_skyline_live_status_unavailable"
    assert evaluate_dynamic_access(
        jp022[1], {"timestamp": yahiko_after_ropeway, "access_state": after_state}
    )["eligible"] is False

    non_event_night = build_yahiko_access_state(
        jst_epoch(2026, 9, 25, 19, 0), yahiko_provider
    )["jp-022-P03"]
    assert non_event_night["status"] == "closed"
    assert non_event_night["status_basis"] == "not_an_official_2026_night_cruise_date"

    yahiko_event_html = """
    <section><h2>本日のロープウェイ情報</h2>
    <div>始 発</div><b>09:00</b>
    <div>上り</div><div>最終</div><b>20:30</b>
    <div>下り</div><div>最終</div><b>21:00</b>
    <strong>通常営業</strong></section>
    """
    yahiko_event_provider = parse_yahiko_homepage_status(
        yahiko_event_html, fetched_at_epoch=jst_epoch(2026, 9, 23, 19, 0)
    )
    event_state = build_yahiko_access_state(
        jst_epoch(2026, 9, 23, 19, 30), yahiko_event_provider
    )["jp-022-P03"]
    assert event_state["status"] == "open"
    assert event_state["status_basis"] == "official_event_date_and_live_ropeway_night_service_open"
    assert evaluate_dynamic_access(
        jp022[2], {"timestamp": jst_epoch(2026, 9, 23, 19, 30), "access_state": event_state}
    )["eligible"] is True

    jp009 = get_opportunities("jp", "jp-009")
    assert [o["opportunity_id"] for o in jp009] == ["jp-009-P01"]
    assert jp009[0]["runtime_policy"] == "minimum_sufficient_available"
    assert dependencies_for_opportunity(jp009[0]) == ("visibility",)
    bandai_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp009},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0},
    )
    assert bandai_diag["jp-009-P01"]["available"] is True
    assert bandai_diag["jp-009-P01"]["eligible"] is True

    jp010 = get_opportunities("jp", "jp-010")
    assert [o["opportunity_id"] for o in jp010] == ["jp-010-P01", "jp-010-P02"]
    assert jp010[0]["runtime_policy"] == "minimum_sufficient_available"
    assert jp010[1]["runtime_policy"] == "preview_module_available"
    assert dependencies_for_opportunity(jp010[0]) == ("visibility",)
    assert dependencies_for_opportunity(jp010[1]) == ("water_surface_state", "visibility")
    fuji_diag = fetch_data._build_opportunity_runtime_diagnostics(
        {"opportunities": jp010},
        {"vis": 30000, "c_low": 10, "pop": 5, "precipitation": 0.0, "wind": 1.0},
    )
    assert fuji_diag["jp-010-P01"]["available"] is True
    assert fuji_diag["jp-010-P01"]["eligible"] is True
    assert fuji_diag["jp-010-P02"]["available"] is True
    assert fuji_diag["jp-010-P02"]["eligible"] is True
    assert fuji_diag["jp-010-P02"]["modules"]["water_surface_state"]["quality"] == "mirror_candidate"
    assert fuji_diag["jp-010-P02"]["modules"]["visibility"]["eligible"] is True

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
    assert set(diag) == {o["opportunity_id"] for o in tw018["opportunities"]}
    assert diag["tw-018-P02"]["available"] is True
    assert diag["tw-018-P02"]["eligible"] is True
    assert all("score" not in result for result in diag.values())

    # Opportunity score is authoritative. Generic Theme weather is only the
    # baseline and cannot produce an 80+ Place recommendation by itself.
    high_theme_metric = {
        "score": 92,
        "status_key": "STABLE_WEATHER",
        "indicator_key": "IND_DEFAULT",
        "factors": [],
    }

    simple_opportunity = next(
        o for o in get_opportunities("tw", "tw-004")
        if o["opportunity_id"] == "tw-004-P01"
    )
    assert simple_opportunity["runtime_policy"] == "minimum_sufficient_available"
    simple_good = evaluate_minimum_sufficient_visibility(
        simple_opportunity,
        {
            "vis": 35000,
            "c_low": 10,
            "pop": 5,
            "precipitation": 0.0,
            "access_open": True,
        },
    )
    assert simple_good["available"] is True
    assert simple_good["eligible"] is True
    assert simple_good["quality"] == "excellent"
    simple_scored = fetch_data._score_opportunity(
        simple_opportunity, high_theme_metric,
        {
            "available": True,
            "eligible": True,
            "minimum_sufficient": True,
            "reason": simple_good["reason"],
            "modules": {"minimum_sufficient_visibility": simple_good},
        },
        "zh-TW",
    )
    assert simple_scored["score"] == 92
    assert simple_scored["condition_state"] == "minimum_sufficient_conditions_match"
    assert simple_scored["score_confidence"] == "high"

    # A Place may have usable weather while still being outside the researched
    # shooting time. Preserve the low temporal baseline, but never describe that
    # hour as a fully "good shoot" match. Bitan tw-007-P03 reproduces the UI case
    # where the mountain-view baseline is capped at 38 after dark.
    bitan_simple = next(
        o for o in get_opportunities("tw", "tw-007")
        if o["opportunity_id"] == "tw-007-P03"
    )
    assert bitan_simple["runtime_policy"] == "minimum_sufficient_available"
    bitan_after_dark = fetch_data._score_opportunity(
        bitan_simple,
        {
            "score": 38,
            "status_key": "STABLE_WEATHER",
            "indicator_key": "IND_DEFAULT",
            "factors": [],
            "temporal_eligible": False,
            "temporal_reason": "landscape_visible_light",
        },
        {
            "available": True,
            "eligible": True,
            "minimum_sufficient": True,
            "reason": "scene_readable",
            "modules": {},
        },
        "zh-TW",
    )
    assert bitan_after_dark["score"] == 38
    assert bitan_after_dark["status_key"] == "OPPORTUNITY_OUTSIDE_TIME_WINDOW"
    assert bitan_after_dark["condition_state"] == "minimum_sufficient_weather_match_outside_time_window"
    assert "不在此題材的建議拍攝時段" in bitan_after_dark["status"]

    simple_bad = evaluate_minimum_sufficient_visibility(
        simple_opportunity,
        {
            "vis": 6000,
            "c_low": 85,
            "pop": 70,
            "precipitation": 0.8,
            "access_open": True,
        },
    )
    assert simple_bad["eligible"] is False
    simple_bad_score = fetch_data._score_opportunity(
        simple_opportunity, high_theme_metric,
        {
            "available": True,
            "eligible": False,
            "minimum_sufficient": True,
            "reason": simple_bad["reason"],
            "modules": {"minimum_sufficient_visibility": simple_bad},
        },
        "zh-TW",
    )
    assert simple_bad_score["score"] <= 54
    matched = fetch_data._score_opportunity(
        p02, high_theme_metric, diag["tw-018-P02"], "zh-TW"
    )
    assert matched["score"] == 92
    assert matched["condition_state"] == "dedicated_conditions_match"
    assert matched["score_confidence"] == "high"

    missed_diag = fetch_data._build_opportunity_runtime_diagnostics(
        tw018, {"wind": 7.0, "precipitation": 0.0, "pop": 10}
    )["tw-018-P02"]
    missed = fetch_data._score_opportunity(p02, high_theme_metric, missed_diag, "zh-TW")
    assert missed["score"] <= 54
    assert missed["condition_state"] == "dedicated_conditions_miss"

    pending = next(o for o in all_opportunities if runtime_policy(o) == "module_pending")
    pending_score = fetch_data._score_opportunity(dict(pending, runtime_policy=runtime_policy(pending)), high_theme_metric, {}, "zh-TW")
    assert pending_score["score"] <= 64

    prototype = next(o for o in all_opportunities if runtime_policy(o) == "prototype_pending_certification")
    prototype_score = fetch_data._score_opportunity(dict(prototype, runtime_policy=runtime_policy(prototype)), high_theme_metric, {}, "zh-TW")
    assert prototype_score["score"] <= 79

    held = next(o for o in all_opportunities if runtime_policy(o) == "hold")
    hold_score = fetch_data._score_opportunity(dict(held, runtime_policy=runtime_policy(held)), high_theme_metric, {}, "zh-TW")
    assert hold_score["score"] == 0

    insufficient = next(o for o in all_opportunities if runtime_policy(o) == "data_insufficient")
    insufficient_score = fetch_data._score_opportunity(dict(insufficient, runtime_policy=runtime_policy(insufficient)), high_theme_metric, {}, "zh-TW")
    assert insufficient_score["score"] <= 35

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

    marine_url = fetch_data._build_marine_open_meteo_url({"lat": 24.0, "lon": 121.7})
    assert marine_url.startswith("https://marine-api.open-meteo.com/v1/marine?")
    assert "cell_selection=sea" in marine_url
    assert "wave_height" in marine_url
    assert "swell_wave_height" in marine_url
    assert "swell_wave_period" in marine_url
    assert "sea_level_height_msl" not in marine_url

    tide_url = fetch_data._build_tide_open_meteo_url({"lat": 24.0, "lon": 120.5})
    assert tide_url.startswith("https://marine-api.open-meteo.com/v1/marine?")
    assert "hourly=sea_level_height_msl" in tide_url
    assert "cell_selection=sea" in tide_url
    assert "wave_height" not in tide_url

    weather_url = fetch_data._build_open_meteo_url({"lat": 25.0, "lon": 121.0})
    assert ",precipitation,precipitation_probability,snowfall,snow_depth,direct_normal_irradiance," in weather_url


def test_active_catalog_weather_generation_guard():
    active_tw = analyze_weather._active_spots("tw")
    assert len(active_tw) == 80

    chaori_spot = next(spot for spot in active_tw if spot["spot_id"] == "tw-068")
    yehliu_spot = next(spot for spot in active_tw if spot["spot_id"] == "tw-074")
    iron_fort_spot = next(spot for spot in active_tw if spot["spot_id"] == "tw-081")
    assert chaori_spot["access_hours_windows"] == [["05:00", "10:00"], ["16:00", "23:00"]]
    assert fetch_data._access_open_for_spot(
        chaori_spot, datetime(2026, 9, 24, 6, 0), True, False
    ) is True
    assert fetch_data._access_open_for_spot(
        chaori_spot, datetime(2026, 9, 24, 12, 0), True, False
    ) is False
    assert fetch_data._access_open_for_spot(
        chaori_spot, datetime(2026, 9, 24, 20, 0), False, False
    ) is True

    # Seasonal access is evaluated against the Place-local datetime passed in
    # by the weather pipeline, not the user's browser/device timezone.
    seasonal_spot = {
        "access_hours_seasonal": [
            {"start_mmdd": "04-01", "end_mmdd": "09-30", "windows": [["08:00", "17:30"]]},
            {"start_mmdd": "10-01", "end_mmdd": "03-31", "windows": [["08:00", "17:00"]]},
        ]
    }
    assert fetch_data._access_open_for_spot(
        seasonal_spot, datetime(2026, 7, 15, 17, 15), True, False
    ) is True
    assert fetch_data._access_open_for_spot(
        seasonal_spot, datetime(2026, 7, 15, 17, 45), True, False
    ) is False
    assert fetch_data._access_open_for_spot(
        seasonal_spot, datetime(2026, 12, 15, 16, 45), True, False
    ) is True
    assert fetch_data._access_open_for_spot(
        seasonal_spot, datetime(2026, 12, 15, 17, 15), False, True
    ) is False
    assert fetch_data._access_open_for_spot(
        seasonal_spot, datetime(2027, 3, 31, 16, 30), True, False
    ) is True

    multi_window_spot = {
        "access_hours_seasonal": [
            {
                "start_mmdd": "04-01",
                "end_mmdd": "08-31",
                "windows": [["04:00", "06:45"], ["07:00", "18:00"]],
            }
        ]
    }
    assert fetch_data._access_open_for_spot(
        multi_window_spot, datetime(2026, 6, 1, 5, 30), True, False
    ) is True
    assert fetch_data._access_open_for_spot(
        multi_window_spot, datetime(2026, 6, 1, 6, 50), True, False
    ) is False
    assert fetch_data._access_open_for_spot(
        multi_window_spot, datetime(2026, 6, 1, 7, 15), True, False
    ) is True

    overlap_spot = {
        "access_hours_seasonal": [
            {"start_mmdd": "01-01", "end_mmdd": "12-31", "windows": [["08:00", "17:00"]]},
            {"start_mmdd": "06-01", "end_mmdd": "08-31", "windows": [["09:00", "18:00"]]},
        ]
    }
    try:
        fetch_data._access_open_for_spot(
            overlap_spot, datetime(2026, 7, 1, 10, 0), True, False
        )
        raise AssertionError("overlapping seasonal access rules must fail")
    except ValueError as exc:
        assert "overlapping seasonal access" in str(exc)
    assert yehliu_spot["access_hours"] == ["08:00", "17:00"]
    assert iron_fort_spot["access_hours"] == ["08:00", "17:00"]
    assert fetch_data._access_open_for_spot(
        yehliu_spot, datetime(2026, 9, 24, 16, 0), True, False
    ) is True
    assert fetch_data._access_open_for_spot(
        yehliu_spot, datetime(2026, 9, 24, 18, 0), False, True
    ) is False
    assert fetch_data._access_open_for_spot(
        iron_fort_spot, datetime(2026, 9, 24, 16, 0), True, False
    ) is True
    assert fetch_data._access_open_for_spot(
        iron_fort_spot, datetime(2026, 9, 24, 18, 0), False, True
    ) is False
    assert "tw-063" not in {spot["spot_id"] for spot in active_tw}
    assert all(spot.get("active_in_catalog", True) for spot in active_tw)

    # Every active Taiwan Place shown in the product must have explicit,
    # place-specific photography research. The UI is forbidden from inventing
    # shooting advice for a Place without this catalog evidence.
    for spot in active_tw:
        opportunities = spot.get("opportunities") or []
        assert opportunities, f"{spot['spot_id']}: researched Opportunity required"
        for opportunity in opportunities:
            assert opportunity.get("opportunity_id")
            assert str(opportunity.get("name_zh") or "").strip()
            assert opportunity.get("viewpoints"), f"{opportunity['opportunity_id']}: viewpoint evidence required"
            assert all(str(v.get("name") or "").strip() for v in opportunity["viewpoints"])
            variants = opportunity.get("condition_variants") or []
            assert variants, f"{opportunity['opportunity_id']}: Condition Variant required"
            assert all(str(v.get("variant_name") or "").strip() for v in variants)
            # Detailed prose fields are optional by design. Missing research
            # fields stay absent in the UI rather than being filled by a
            # generic template.

    # Non-migrated Places must remain explicit research gaps; enabling one
    # researched Japan Place must not leak legacy scoring into the remaining pending Places.
    jp_spots = get_spots("jp")
    researched_jp = {spot["spot_id"] for spot in jp_spots if spot.get("opportunities")}
    assert researched_jp == {f"jp-{i:03d}" for i in range(1, 27)}
    assert all(
        not (spot.get("opportunities") or [])
        for spot in jp_spots if spot["spot_id"] not in {f"jp-{i:03d}" for i in range(1, 27)}
    )
    blue_pond = next(spot for spot in jp_spots if spot["spot_id"] == "jp-001")
    assert abs(blue_pond["lat"] - 43.493611) < 1e-9
    assert abs(blue_pond["lon"] - 142.614167) < 1e-9
    assert blue_pond["coordinate_confidence"] == "high"
    asahidake = next(spot for spot in jp_spots if spot["spot_id"] == "jp-002")
    assert abs(asahidake["lat"] - 43.6620489) < 1e-9
    assert abs(asahidake["lon"] - 142.8250911) < 1e-9
    assert asahidake["elevation"] == 1600
    assert asahidake["coordinate_confidence"] == "high"
    kushiro = next(spot for spot in jp_spots if spot["spot_id"] == "jp-003")
    assert abs(kushiro["lat"] - 43.0980769) < 1e-9
    assert abs(kushiro["lon"] - 144.4492556) < 1e-9
    assert kushiro["coordinate_confidence"] == "high"
    hakodate = next(spot for spot in jp_spots if spot["spot_id"] == "jp-004")
    assert abs(hakodate["lat"] - 41.7594502) < 1e-9
    assert abs(hakodate["lon"] - 140.7044467) < 1e-9
    assert hakodate["coordinate_confidence"] == "high"
    otaru = next(spot for spot in jp_spots if spot["spot_id"] == "jp-005")
    assert abs(otaru["lat"] - 43.197887) < 1e-9
    assert abs(otaru["lon"] - 141.003034) < 1e-9
    assert otaru["coordinate_confidence"] == "high"
    matsushima = next(spot for spot in jp_spots if spot["spot_id"] == "jp-008")
    assert abs(matsushima["lat"] - 38.3525784) < 1e-9
    assert abs(matsushima["lon"] - 141.0623503) < 1e-9
    assert matsushima["coordinate_confidence"] == "high"
    assert matsushima["map_query"] == "双観山 松島"
    assert matsushima["themes"] == ["sunrise"]

    bandai = next(spot for spot in jp_spots if spot["spot_id"] == "jp-009")
    assert abs(bandai["lat"] - 37.6727759) < 1e-9
    assert abs(bandai["lon"] - 140.0689901) < 1e-9
    assert bandai["coordinate_confidence"] == "high"
    assert bandai["map_query"] == "中瀬沼展望台"
    assert bandai["themes"] == ["mountain_view"]

    kawaguchiko = next(spot for spot in jp_spots if spot["spot_id"] == "jp-010")
    assert abs(kawaguchiko["lat"] - 35.5230652) < 1e-9
    assert abs(kawaguchiko["lon"] - 138.7461483) < 1e-9
    assert kawaguchiko["coordinate_confidence"] == "high"
    assert kawaguchiko["themes"] == ["mountain_view", "reflection"]
    tokyo_tower = next(spot for spot in jp_spots if spot["spot_id"] == "jp-011")
    assert abs(tokyo_tower["lat"] - 35.658656) < 1e-9
    assert abs(tokyo_tower["lon"] - 139.745364) < 1e-9
    assert tokyo_tower["coordinate_confidence"] == "high"
    assert tokyo_tower["elevation"] == 150
    assert set(tokyo_tower["themes"]) == {"mountain_view", "city_night"}
    assert tokyo_tower["access_hours"] == ["09:00", "22:30"]
    assert fetch_data._access_open_for_spot(
        tokyo_tower, datetime(2026, 9, 25, 22, 0), False, False
    ) is True
    assert fetch_data._access_open_for_spot(
        tokyo_tower, datetime(2026, 9, 25, 23, 0), False, False
    ) is False

    kamakura = next(spot for spot in jp_spots if spot["spot_id"] == "jp-012")
    assert abs(kamakura["lat"] - 35.31685) < 1e-9
    assert abs(kamakura["lon"] - 139.53572) < 1e-9
    assert kamakura["coordinate_confidence"] == "high"
    assert kamakura["themes"] == ["mountain_view"]
    assert len(kamakura["access_hours_seasonal"]) == 2
    assert fetch_data._access_open_for_spot(
        kamakura, datetime(2026, 7, 15, 17, 0), True, False
    ) is True
    assert fetch_data._access_open_for_spot(
        kamakura, datetime(2026, 7, 15, 17, 30), True, False
    ) is False
    assert fetch_data._access_open_for_spot(
        kamakura, datetime(2026, 12, 15, 16, 30), True, False
    ) is True
    assert fetch_data._access_open_for_spot(
        kamakura, datetime(2026, 12, 15, 17, 0), False, True
    ) is False

    nijubashi = next(spot for spot in jp_spots if spot["spot_id"] == "jp-015")
    assert abs(nijubashi["lat"] - 35.678475) < 1e-9
    assert abs(nijubashi["lon"] - 139.754897) < 1e-9
    assert nijubashi["coordinate_confidence"] == "high"
    assert nijubashi["themes"] == ["mountain_view"]
    assert nijubashi["name_i18n"]["zh-TW"] == "皇居外苑二重橋"
    assert nijubashi["name_i18n"]["en"] == "Nijubashi, Kokyo Gaien"
    assert nijubashi["name_i18n"]["ja"] == "皇居外苑 二重橋"
    assert nijubashi["name_local"] == "二重橋"
    assert "皇居外苑" in nijubashi["map_query"]

    yamashita = next(spot for spot in jp_spots if spot["spot_id"] == "jp-016")
    assert abs(yamashita["lat"] - 35.447738) < 1e-9
    assert abs(yamashita["lon"] - 139.646791) < 1e-9
    assert yamashita["coordinate_confidence"] == "high"
    assert set(yamashita["themes"]) == {"mountain_view", "city_night"}
    assert "インド水塔" in yamashita["map_query"]

    kenrokuen = next(spot for spot in jp_spots if spot["spot_id"] == "jp-017")
    assert abs(kenrokuen["lat"] - 36.563367) < 1e-9
    assert abs(kenrokuen["lon"] - 136.662817) < 1e-9
    assert kenrokuen["coordinate_confidence"] == "high"
    assert kenrokuen["themes"] == ["mountain_view"]
    assert "徽軫灯籠" in kenrokuen["map_query"]
    assert len(kenrokuen["access_hours_seasonal"]) == 5
    assert fetch_data._access_open_for_spot(
        kenrokuen, datetime(2026, 7, 15, 5, 30), True, False
    ) is True
    assert fetch_data._access_open_for_spot(
        kenrokuen, datetime(2026, 7, 15, 6, 40), True, False
    ) is False
    assert fetch_data._access_open_for_spot(
        kenrokuen, datetime(2026, 7, 15, 7, 15), True, False
    ) is True
    assert fetch_data._access_open_for_spot(
        kenrokuen, datetime(2026, 12, 15, 7, 40), True, False
    ) is False
    assert fetch_data._access_open_for_spot(
        kenrokuen, datetime(2026, 12, 15, 8, 15), True, False
    ) is True

    nagoya = next(spot for spot in jp_spots if spot["spot_id"] == "jp-018")
    assert abs(nagoya["lat"] - 35.185181) < 1e-9
    assert abs(nagoya["lon"] - 136.89865) < 1e-9
    assert nagoya["coordinate_confidence"] == "high"
    assert nagoya["themes"] == ["mountain_view"]
    assert nagoya["access_hours"] == ["09:00", "16:30"]
    assert nagoya["access_closed_mmdd_ranges"] == [{"start_mmdd": "12-29", "end_mmdd": "01-01"}]
    assert fetch_data._access_open_for_spot(
        nagoya, datetime(2026, 9, 25, 10, 0), True, False
    ) is True
    assert fetch_data._access_open_for_spot(
        nagoya, datetime(2026, 12, 30, 10, 0), True, False
    ) is False
    assert fetch_data._access_open_for_spot(
        nagoya, datetime(2027, 1, 1, 10, 0), True, False
    ) is False
    assert fetch_data._access_open_for_spot(
        nagoya, datetime(2027, 1, 2, 10, 0), True, False
    ) is True
    assert fetch_data._access_open_for_spot(
        nagoya, datetime(2026, 9, 25, 17, 0), True, False
    ) is False

    kiyomizu = next(spot for spot in jp_spots if spot["spot_id"] == "jp-023")
    assert abs(kiyomizu["lat"] - 34.994444) < 1e-9
    assert abs(kiyomizu["lon"] - 135.785556) < 1e-9
    assert kiyomizu["coordinate_confidence"] == "high"
    assert kiyomizu["themes"] == ["mountain_view"]
    assert "奥の院" in kiyomizu["map_query"]
    assert len(kiyomizu["access_hours_seasonal"]) == 3
    assert fetch_data._access_open_for_spot(
        kiyomizu, datetime(2026, 7, 15, 18, 15), True, False
    ) is True
    assert fetch_data._access_open_for_spot(
        kiyomizu, datetime(2026, 7, 15, 18, 45), True, False
    ) is False
    assert fetch_data._access_open_for_spot(
        kiyomizu, datetime(2026, 9, 25, 18, 15), False, True
    ) is False
    assert "三腳架" in kiyomizu["access_note_i18n"]["zh-TW"]

    minato = next(spot for spot in jp_spots if spot["spot_id"] == "jp-020")
    assert abs(minato["lat"] - 35.45099) < 1e-9
    assert abs(minato["lon"] - 139.64670) < 1e-9
    assert minato["coordinate_confidence"] == "high"
    assert minato["themes"] == ["city_night"]
    assert "OSANBASHI VIEWPOINT" in minato["map_query"]

    assert all(not (spot.get("opportunities") or []) for spot in get_spots("us"))

    stale = analyze_weather._mark_stale({"spot_id": "tw-009", "daily": []}, "weather_fetch_failed")
    assert stale["spot_id"] == "tw-009"
    assert stale["data_stale"] is True
    assert stale["data_stale_reason"] == "weather_fetch_failed"

    # Daily Place ranking is authoritative only when a researched Opportunity
    # exists. Legacy Theme metrics may remain in the payload for compatibility,
    # but may not publish a photography recommendation score on their own.
    legacy_only_hour = [{
        "is_past": False,
        "local_date": "2026-09-24",
        "time": "2026-09-24 06:00",
        "time_utc": "2026-09-23T22:00:00Z",
        "theme_scores": {
            "sunrise": {
                "score": 95,
                "status_key": "STABLE_WEATHER",
                "indicator_key": "IND_DEFAULT",
                "factors": [],
            }
        },
    }]
    unresearched_days = analyze_weather._build_day_summaries(
        legacy_only_hour, ["sunrise"], []
    )
    assert unresearched_days[0]["all"]["score"] is None
    assert unresearched_days[0]["all"]["research_pending"] is True

    researched_hour = [{
        "is_past": False,
        "local_date": "2026-09-24",
        "time": "2026-09-24 06:00",
        "time_utc": "2026-09-23T22:00:00Z",
        "theme_scores": {"reflection": {"score": 91, "factors": []}},
        "opportunity_scores": {
            "tw-018-P02": {
                "score": 88,
                "status_key": "OPPORTUNITY_MATCH",
                "indicator_key": "OPPORTUNITY_MATCH",
                "factors": [],
                "runtime_policy": "preview_module_available",
                "condition_state": "dedicated_conditions_match",
                "score_confidence": "high",
                "base_theme_score": 91,
            }
        },
    }]
    p02_for_daily = next(
        o for o in get_opportunities("tw", "tw-018")
        if o["opportunity_id"] == "tw-018-P02"
    )
    researched_days = analyze_weather._build_day_summaries(
        researched_hour, ["reflection"], [p02_for_daily]
    )
    assert researched_days[0]["all"]["opportunity_id"] == "tw-018-P02"
    assert researched_days[0]["all"]["score"] == 88
    assert researched_days[0]["all"]["research_pending"] is False

    sunrise_only = next(
        o for o in get_opportunities("tw", "tw-075")
        if o["opportunity_id"] == "tw-075-P01"
    )
    impossible_hour = [{
        "is_past": False,
        "local_date": "2026-09-24",
        "time": "2026-09-24 17:00",
        "time_utc": "2026-09-24T09:00:00Z",
        "theme_scores": {"sunrise": {"score": 16, "factors": []}},
        "opportunity_scores": {
            "tw-075-P01": {
                "score": 16,
                "temporal_eligible": False,
                "temporal_reason": "sunrise_after_noon",
                "status_key": "OPPORTUNITY_CONDITION_MISS",
                "indicator_key": "OPPORTUNITY_CONDITION_MISS",
                "factors": [],
            }
        },
    }]
    impossible_days = analyze_weather._build_day_summaries(
        impossible_hour, ["sunrise"], [sunrise_only]
    )
    assert impossible_days[0]["all"]["score"] is None
    assert impossible_days[0]["all"]["research_pending"] is False
    assert impossible_days[0]["all"]["no_viable_opportunity"] is True
    assert "opportunity_id" not in impossible_days[0]["all"]

    closed_vs_open = [
        {
            "is_past": False,
            "local_date": "2026-09-24",
            "time": "2026-09-24 05:00",
            "time_utc": "2026-09-23T21:00:00Z",
            "access_open": False,
            "theme_scores": {"reflection": {"score": 96, "factors": []}},
            "opportunity_scores": {
                "tw-018-P02": {
                    "score": 96,
                    "temporal_eligible": True,
                    "status_key": "OPPORTUNITY_MATCH",
                    "indicator_key": "OPPORTUNITY_MATCH",
                    "factors": [],
                }
            },
        },
        {
            "is_past": False,
            "local_date": "2026-09-24",
            "time": "2026-09-24 06:00",
            "time_utc": "2026-09-23T22:00:00Z",
            "access_open": True,
            "theme_scores": {"reflection": {"score": 72, "factors": []}},
            "opportunity_scores": {
                "tw-018-P02": {
                    "score": 72,
                    "temporal_eligible": True,
                    "status_key": "OPPORTUNITY_MATCH",
                    "indicator_key": "OPPORTUNITY_MATCH",
                    "factors": [],
                }
            },
        },
    ]
    access_days = analyze_weather._build_day_summaries(
        closed_vs_open, ["reflection"], [p02_for_daily]
    )
    assert access_days[0]["all"]["score"] == 72
    assert access_days[0]["all"]["access_open"] is True
    assert access_days[0]["all"]["best_time"] == "2026-09-24 06:00"
    assert access_days[0]["all"]["window_start"] == "2026-09-24 06:00"


def test_schema10_optional_metadata_bridge():
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
    assert summary["navigation_target"] == spot["navigation_target"]
    assert details["navigation_target"] == spot["navigation_target"]
    json.dumps({"schema_version": 10, "spots": [summary]}, ensure_ascii=False)


if __name__ == "__main__":
    test_adapter_integrity()
    test_active_catalog_weather_generation_guard()
    test_schema10_optional_metadata_bridge()
    print("v0.04 R4.2 full Opportunity adapter tests: PASS")
