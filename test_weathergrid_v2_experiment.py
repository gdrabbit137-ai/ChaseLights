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
            "weather-map-v2-sampling.js?v=antimeridian-p0",
            "bboxFromWestSpan",
            "bboxContains",
            "bboxCenterLon",
            "sampleGrid(coverage, {",
            "chunkPoints(grid.points, API_BATCH_SIZE)",
            "const API_BATCH_SIZE = 100",
            "const API_BATCH_CONCURRENCY = 2",
            "const API_BATCH_RETRIES = 3",
            "function abortableDelay(",
            "response.status === 429 || response.status >= 500",
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
            "params.set('models', 'gfs_global')",
            "NCEP GFS Global",
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
        self.assertIn("timeout-minutes: 24", workflow)
        self.assertIn("for i in {1..60}; do", workflow)

    def test_public_smoke_covers_partial_native_fallback_and_retake(self):
        smoke = (ROOT / "weathergrid_v2_public_smoke.py").read_text(encoding="utf-8")
        self.assertIn('assert "NCEP GFS Global" in initial["source"]', smoke)
        self.assertIn('sample_count(initial["status"]) >= 200', smoke)
        self.assertIn('CONUS V2 handoff timed out', smoke)
        self.assertIn('coverage_contains(initial["viewport"], initial["coverage"])', smoke)
        self.assertIn("121.75, 23.8, 10.0", smoke)
        self.assertIn('"JMA MSM native tiles" in x.find_element(By.ID,"source").text', smoke)
        self.assertIn('[data-preset="us_alaska"]', smoke)
        self.assertIn('[data-preset="jp"]', smoke)
        self.assertIn("10.0, 50.0, 5.0", smoke)
        self.assertIn('Select(d.find_element(By.ID,"provider")).select_by_value("jma")', smoke)
        self.assertIn("179.0, 10.0, 6.0", smoke)
        self.assertIn("assert dw > de", smoke)
        self.assertIn("def lon_segments(", smoke)

    def test_antimeridian_geometry_contract_runs_in_ci(self):
        workflow = (ROOT / ".github/workflows/weathergrid_v2_experiment.yml").read_text(
            encoding="utf-8"
        )
        sampling = (ROOT / "assets/weather-map-v2-sampling.js").read_text(encoding="utf-8")
        self.assertIn("node test_weathergrid_v2_geo.mjs", workflow)
        self.assertIn('"test_weathergrid_v2_geo.mjs"', workflow)
        for token in (
            "export function longitudeSpan",
            "export function bboxLongitudeSegments",
            "export function bboxContains",
            "export function bboxCenterLon",
            "export function expandBBox",
            "wrapsAntimeridian",
        ):
            self.assertIn(token, sampling)

    def test_photography_layers_are_available(self):
        html = (ROOT / "weather-map-v2.html").read_text(encoding="utf-8")
        for field in (
            "cloud_cover",
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
