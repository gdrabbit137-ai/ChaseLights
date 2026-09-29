import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class WeatherGridOverlayReadabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "weather-map.html").read_text(encoding="utf-8")
        cls.js = (ROOT / "assets" / "weather-map.js").read_text(encoding="utf-8")
        cls.workflow = (
            ROOT / ".github" / "workflows" / "b117_gfs_multilayer_poc.yml"
        ).read_text(encoding="utf-8")

    def test_opacity_slider_can_show_basemap_only(self):
        self.assertIn(
            'id="opacity-slider" type="range" min="0" max="100" value="62"',
            self.html,
        )

    def test_weather_cells_use_value_aware_opacity(self):
        self.assertIn("function cellOpacityFor(value,cfg)", self.js)
        self.assertIn("state.weatherOpacity*cellOpacityFor(value,cfg)", self.js)
        self.assertNotIn("ctx.globalAlpha=state.weatherOpacity;", self.js)

    def test_clear_cloud_and_dry_precip_recede(self):
        self.assertIn("return .04 + .96*Math.pow(t,.8)", self.js)
        self.assertIn("if(value < .01) return 0", self.js)

    def test_clear_visibility_and_low_wind_recede(self):
        self.assertIn("return .08 + .92*Math.pow(1-t,.8)", self.js)
        self.assertIn("return .12 + .88*t", self.js)

    def test_b117_ci_runs_readability_contract(self):
        self.assertIn('"test_weathergrid_overlay_readability.py"', self.workflow)
        self.assertIn("test_weathergrid_overlay_readability.py", self.workflow)


if __name__ == "__main__":
    unittest.main()
