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

    def test_has_real_viewport_fetch_contract(self):
        js = (ROOT / "assets/weather-map-v2.js").read_text(encoding="utf-8")
        for token in (
            "https://api.open-meteo.com/v1/jma",
            "https://api.open-meteo.com/v1/gfs",
            "function sampleGrid(",
            "function cacheFind(",
            "function fetchCoverage(",
            "forecast_hours",
            "elevation: 'nan'",
            "map.on('moveend'",
            "new AbortController()",
            "PROVIDER_FIELDS",
            "if (field === 'visibility') return 'gfs'",
        ):
            self.assertIn(token, js)

    def test_auto_provider_and_global_presets_are_explicit(self):
        js = (ROOT / "assets/weather-map-v2.js").read_text(encoding="utf-8")
        html = (ROOT / "weather-map-v2.html").read_text(encoding="utf-8")
        self.assertIn("MSM_DOMAIN", js)
        self.assertIn("return contains(MSM_DOMAIN, b) ? 'jma' : 'gfs'", js)
        self.assertIn('data-preset="tw"', html)
        self.assertIn('data-preset="jp"', html)
        self.assertIn('data-preset="us"', html)
        self.assertIn('value="auto"', html)
        self.assertIn('value="jma"', html)
        self.assertIn('value="gfs"', html)

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
