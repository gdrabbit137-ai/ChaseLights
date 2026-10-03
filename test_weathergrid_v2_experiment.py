from pathlib import Path

ROOT=Path(__file__).resolve().parent

def test_weathergrid_v2_is_isolated_from_production_page():
    production=(ROOT/"weather-map.html").read_text(encoding="utf-8")
    experimental=(ROOT/"weather-map-v2.html").read_text(encoding="utf-8")
    assert "weather-map-v2.js" in experimental
    assert "weather-map-v2.css" in experimental
    assert "weather-map-v2" not in production

def test_weathergrid_v2_has_viewport_prefetch_contract():
    js=(ROOT/"assets/weather-map-v2.js").read_text(encoding="utf-8")
    assert "function expand(" in js
    assert "needs-provider-fetch" in js
    assert "request cache" in js
    assert "map.on('move',schedule)" in js
