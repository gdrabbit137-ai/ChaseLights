from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent


class WeatherGridV2ExperimentTest(unittest.TestCase):
    def test_isolated_from_production_page(self):
        production = (ROOT / "weather-map.html").read_text(encoding="utf-8")
        experimental = (ROOT / "weather-map-v2.html").read_text(encoding="utf-8")
        self.assertIn("weather-map-v2.js", experimental)
        self.assertIn("weather-map-v2.css", experimental)
        self.assertNotIn("weather-map-v2", production)
        js = (ROOT / "assets/weather-map-v2.js").read_text(encoding="utf-8")
        self.assertIn("import * as maplibregl from", js)
        self.assertNotIn("import maplibregl from", js)

    def test_has_real_viewport_fetch_contract(self):
        js = (ROOT / "assets/weather-map-v2.js").read_text(encoding="utf-8")
        for token in (
            "https://api.open-meteo.com/v1/jma",
            "https://api.open-meteo.com/v1/gfs",
            "from './weather-map-v2-sampling.js'",
            "sampleGrid(coverage, {",
            "chunkPoints(grid.points, 80)",
            "function cacheFind(",
            "function fetchCoverage(",
            "forecast_hours",
            "elevation: points.map(() => 'nan').join(',')",
            "map.on('moveend'",
            "new AbortController()",
            "PROVIDER_FIELDS",
            "hourly: field",
            "function cacheFind(provider, field, v)",
            "if (field === 'visibility') return 'gfs'",
        ):
            self.assertIn(token, js)

    def test_fallback_requests_only_active_field(self):
        js = (ROOT / "assets/weather-map-v2.js").read_text(encoding="utf-8")
        self.assertIn("function buildUrl(provider, points, field)", js)
        self.assertIn("hourly: field", js)
        self.assertNotIn("hourly: PROVIDER_FIELDS[provider].join", js)
        self.assertIn("bboxKey(provider, field, coverage)", js)
        self.assertIn("elevation: points.map(() => 'nan').join(',')", js)

    def test_auto_provider_and_global_presets_are_explicit(self):
        js = (ROOT / "assets/weather-map-v2.js").read_text(encoding="utf-8")
        html = (ROOT / "weather-map-v2.html").read_text(encoding="utf-8")
        self.assertIn("MSM_DOMAIN", js)
        self.assertIn("region === 'tw' || region === 'jp'", js)
        self.assertIn("const provider = selectedProvider(v)", js)
        self.assertIn("if(lon>=-125&&lon<=-66&&lat>=24&&lat<=50) return 'us'", js)
        self.assertIn("if(lon>=-170&&lon<=-129&&lat>=51&&lat<=72) return 'us_alaska'", js)
        self.assertIn("return (region === 'tw' || region === 'jp') ? 'jma' : 'gfs'", js)
        self.assertIn('data-preset="tw"', html)
        self.assertIn('data-preset="jp"', html)
        self.assertIn('data-preset="us"', html)
        self.assertIn('data-preset="us_alaska"', html)
        self.assertIn("美國本土", html)
        self.assertIn("阿拉斯加", html)
        self.assertIn("us: { center: [-98.5, 39.0], zoom: 3.2 }", js)
        self.assertIn("us_alaska: { center: [-149.5, 61.0], zoom: 4.0 }", js)
        self.assertNotIn("us: { center: [-119.5, 38.5], zoom: 4.2 }", js)
        self.assertIn('value="auto"', html)
        self.assertIn('value="jma"', html)
        self.assertIn('value="gfs"', html)

    def test_smoke_hook_is_query_gated_and_uses_real_region_resolver(self):
        js = (ROOT / "assets/weather-map-v2.js").read_text(encoding="utf-8")
        self.assertIn("new URLSearchParams(window.location.search).has('smoke')", js)
        self.assertIn("window.__weatherGridV2Smoke", js)
        self.assertIn("return regionForView(view())", js)

    def test_deployed_smoke_waits_for_tile_loader_publication(self):
        workflow = (ROOT / ".github/workflows/weathergrid_v2_experiment.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("expected_loader_sha", workflow)
        self.assertIn("expected_sampling_sha", workflow)
        self.assertIn("weather-map-v2-tile-loader.js?pages_probe=", workflow)
        self.assertIn("weather-map-v2-sampling.js?pages_probe=", workflow)
        self.assertIn("/tmp/v2-loader.js", workflow)
        self.assertIn("/tmp/v2-sampling.js", workflow)
        self.assertIn("$expected_loader_sha", workflow)
        self.assertIn("$expected_sampling_sha", workflow)

    def test_public_smoke_covers_partial_native_fallback_and_retake(self):
        smoke = (ROOT / "weathergrid_v2_public_smoke.py").read_text(encoding="utf-8")
        self.assertIn('assert "JMA Best Match" in initial["source"]', smoke)
        self.assertIn('sample_count(initial["status"]) >= 200', smoke)
        self.assertIn('coverage_contains(initial["viewport"], initial["coverage"])', smoke)
        self.assertIn("121.75, 23.8, 10.0", smoke)
        self.assertIn('"JMA MSM native tiles" in x.find_element(By.ID,"source").text', smoke)
        self.assertIn('[data-preset="us_alaska"]', smoke)

    def test_photography_layers_are_available(self):
        html = (ROOT / "weather-map-v2.html").read_text(encoding="utf-8")
        for field in (
            "cloud_cover_low",
            "cloud_cover_mid",
            "cloud_cover_high",
            "visibility",
            "precipitation",
            "wind_speed_10m",
        ):
            self.assertIn(field, html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
