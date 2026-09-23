import json
from collections import Counter

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
        "module_pending": 131,
        "prototype_pending_certification": 41,
        "hold": 1,
        "data_insufficient": 1,
    }
    assert runtime_policy(next(o for o in all_opportunities if o["opportunity_id"] == "tw-052-P01")) == "hold"
    assert runtime_policy(next(o for o in all_opportunities if o["opportunity_id"] == "tw-017-P01")) == "data_insufficient"

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
