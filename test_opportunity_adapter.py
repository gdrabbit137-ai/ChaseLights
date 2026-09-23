import json
from collections import Counter

from opportunity_runtime import DIRECTIONAL_HORIZON_SECTORS, evaluate_directional_horizon, evaluate_visibility, evaluate_opportunity_modules, validate_runtime_registry

import analyze_weather
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
    assert ADAPTER_VERSION == "v0.04-r4.2-b16-preview"
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
        "module_pending": 111,
        "preview_module_available": 20,
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

    tw052 = get_opportunities("tw", "tw-052")
    assert tw052[0]["runtime_policy"] == "hold"
    assert get_opportunities("jp", "jp-001") == []
    assert get_opportunities("us", "us-001") == []

    copy = get_opportunities("tw", "tw-001")
    copy[0]["condition_variants"][0]["variant_name"] = "mutated"
    assert CURATED_OPPORTUNITIES["tw-001"][0]["condition_variants"][0]["variant_name"] != "mutated"


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
