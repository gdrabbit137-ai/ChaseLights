import json

import analyze_weather
from opportunities import (
    ADAPTER_VERSION,
    CURATED_OPPORTUNITIES,
    validate_curated_opportunities,
)
from regions import get_spots


def test_adapter_integrity():
    assert ADAPTER_VERSION == "v0.04-r3-preview"
    assert validate_curated_opportunities() == []

    tw = get_spots("tw")
    assert len(tw) == 71
    assert [s["spot_id"] for s in tw] == [f"tw-{i:03d}" for i in range(1, 72)]

    curated = {s["spot_id"]: s for s in tw if s.get("opportunities")}
    assert set(curated) == {"tw-001", "tw-035", "tw-038", "tw-046"}
    assert {sid: len(s["opportunities"]) for sid, s in curated.items()} == {
        "tw-001": 3,
        "tw-035": 6,
        "tw-038": 2,
        "tw-046": 2,
    }
    assert sum(len(s["opportunities"]) for s in curated.values()) == 13

    for sid, spot in curated.items():
        legacy_themes = set(spot["themes"])
        for opportunity in spot["opportunities"]:
            assert opportunity["legacy_theme"] in legacy_themes

    all_opportunities = [
        opportunity
        for opportunities in CURATED_OPPORTUNITIES.values()
        for opportunity in opportunities
    ]
    area = [o for o in all_opportunities if o["mode"] == "area_opportunity"]
    composition = [o for o in all_opportunities if o["mode"] == "composition_specific"]
    assert len(area) == 12
    assert len(composition) == 1
    assert composition[0]["opportunity_id"] == "tw-038-P02"
    assert composition[0]["sampling_topology"] == "exact_alignment"
    assert composition[0]["geometry_required"] is True
    assert all(o["geometry_required"] is False for o in area)

    # R3 representative opportunities are Taiwan-only.
    assert not any(s.get("opportunities") for s in get_spots("jp"))
    assert not any(s.get("opportunities") for s in get_spots("us"))


def test_schema9_optional_metadata_bridge():
    spot = next(s for s in get_spots("tw") if s["spot_id"] == "tw-035")
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

    assert summary["spot_id"] == "tw-035"
    assert details["spot_id"] == "tw-035"
    assert len(summary["opportunities"]) == 6
    assert summary["opportunities"] == details["opportunities"]
    assert summary["themes"] == spot["themes"]
    assert summary["daily"] == []
    assert details["hourly_forecast"] == []

    # Ensure optional opportunity metadata remains JSON-serializable inside schema 9.
    json.dumps({"schema_version": 9, "spots": [summary]}, ensure_ascii=False)


if __name__ == "__main__":
    test_adapter_integrity()
    test_schema9_optional_metadata_bridge()
    print("v0.04 R3 opportunity adapter tests: PASS")
