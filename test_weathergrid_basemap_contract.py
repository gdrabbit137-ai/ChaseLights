import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class WeatherGridBasemapContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "weather-map.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "assets" / "weather-map.css").read_text(encoding="utf-8")
        cls.js = (ROOT / "assets" / "weather-map.js").read_text(encoding="utf-8")
        cls.workflow = (
            ROOT / ".github" / "workflows" / "b117_gfs_multilayer_poc.yml"
        ).read_text(encoding="utf-8")

    def test_html_mounts_basemap_below_weather_overlay(self):
        self.assertIn("maplibre-gl@6.11.2/dist/maplibre-gl.css", self.html)
        self.assertIn('id="weather-basemap"', self.html)
        self.assertIn('id="weather-canvas"', self.html)
        self.assertLess(
            self.html.index('id="weather-basemap"'),
            self.html.index('id="weather-canvas"'),
        )
        self.assertIn('id="opacity-slider"', self.html)
        self.assertIn('id="basemap-status"', self.html)

    def test_js_uses_pinned_maplibre_and_openfreemap_style(self):
        self.assertIn(
            "https://unpkg.com/maplibre-gl@6.11.2/dist/maplibre-gl.mjs",
            self.js,
        )
        self.assertIn(
            "https://tiles.openfreemap.org/styles/liberty",
            self.js,
        )
        self.assertIn("await import(MAPLIBRE_MODULE)", self.js)
        self.assertIn("state.map.project([lon,lat])", self.js)
        self.assertIn("state.map.fitBounds(", self.js)

    def test_weather_overlay_is_translucent_and_has_canvas_fallback(self):
        self.assertIn("weatherOpacity:0.62", self.js)
        self.assertIn("ctx.globalAlpha=state.weatherOpacity", self.js)
        self.assertIn("Canvas fallback", self.js)
        self.assertIn("if(!state.mapReady) drawGrid()", self.js)
        self.assertIn("#weather-basemap{position:absolute;inset:0}", self.css)
        self.assertIn("#weather-canvas{position:absolute;inset:0;z-index:2", self.css)

    def test_b117_ci_runs_basemap_contract(self):
        self.assertIn('"test_weathergrid_basemap_contract.py"', self.workflow)
        self.assertIn("test_weathergrid_basemap_contract.py", self.workflow)
        self.assertIn('"B144_WEATHERGRID_CARTOGRAPHIC_BASEMAP.md"', self.workflow)


if __name__ == "__main__":
    unittest.main()
