import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
JS = ROOT / "assets" / "weather-map.js"
HTML = ROOT / "weather-map.html"
WORKFLOW = ROOT / ".github" / "workflows" / "update_weathergrid.yml"


class WeatherGridIconBrowserContractTests(unittest.TestCase):
    def setUp(self):
        self.js = JS.read_text(encoding="utf-8")
        self.html = HTML.read_text(encoding="utf-8")
        self.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_browser_loads_icon_as_optional_cloud_provider(self):
        self.assertIn("icon_tw_cloud_browser.json", self.js)
        self.assertIn("icon_tw_cloud_qc.json", self.js)
        self.assertIn("iconFrameForValidTime", self.js)
        self.assertIn("activeDataset", self.js)
        self.assertIn("cloudLayers", self.js)
        self.assertIn("usingIcon?'ICON Global'", self.js)
        self.assertIn(":'GFS 0.25°'", self.js)

    def test_cloud_provider_requires_matching_valid_time(self):
        self.assertIn(
            "f.valid_time_utc===validTime",
            self.js,
        )
        self.assertIn(
            "iconFrameForValidTime(baseFrame()?.valid_time_utc)",
            self.js,
        )

    def test_both_regular_grids_use_display_interpolation(self):
        self.assertIn("drawBilinearSubcells", self.js)
        self.assertIn("subdivisions=lonStep>=.20 ? 4", self.js)
        self.assertIn("lonStep>=.10 ? 2 : 1", self.js)
        self.assertIn("bilinear_subcell", self.js)
        self.assertIn("Provider-independent display interpolation", self.js)
        self.assertIn("內插只改善", self.html)

    def test_circular_wind_direction_is_not_bilinearly_interpolated(self):
        self.assertIn(
            "state.layer==='wind_direction_10m_deg'",
            self.js,
        )
        self.assertIn("drawNearestCells(data,vals,cfg,visibleView)", self.js)

    def test_ui_keeps_icon_and_gfs_visible_after_model_selector_expansion(self):
        self.assertIn("ICON Global", self.html)
        self.assertIn("GFS 0.25°", self.html)
        self.assertIn("自動", self.html)
        self.assertIn("內插只改善", self.html)

    def test_scheduled_refresh_keeps_icon_failure_non_blocking(self):
        self.assertIn("id: icon_cloud", self.workflow)
        self.assertIn("continue-on-error: true", self.workflow)
        self.assertIn("icon_global_cloud_poc.py", self.workflow)
        self.assertIn("icon_weathergrid_browser_bundle.py", self.workflow)
        self.assertIn("sudo apt-get install -y cdo", self.workflow)
        self.assertIn("dwd-icon-global-0125-cdo-v1", self.workflow)
        self.assertIn(
            "rm -f weathergrid/icon_tw_cloud_browser.json",
            self.workflow,
        )


if __name__ == "__main__":
    unittest.main()
