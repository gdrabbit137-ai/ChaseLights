import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
JS = (ROOT / "assets" / "weather-map.js").read_text(encoding="utf-8")
HTML = (ROOT / "weather-map.html").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github" / "workflows" / "update_weathergrid.yml").read_text(encoding="utf-8")


class JmaMsmWeatherGridUiTests(unittest.TestCase):
    def test_model_selector_exposes_jma_msm(self):
        self.assertIn('value="jma">JMA MSM 5 km', HTML)
        self.assertIn("jma_msm_tw_cloud_browser.json", JS)
        self.assertIn("jma_msm_tw_cloud_qc.json", JS)
        self.assertIn("state.jmaData", JS)
        self.assertIn("JMA MSM 5 km", JS)

    def test_manual_jma_owns_timeline_and_boundary(self):
        self.assertIn("mode==='jma'", JS)
        self.assertIn("state.modelMode==='jma'", JS)
        self.assertIn("setViewBbox(timeline.bbox", JS)
        self.assertIn("原生時間間隔", JS)

    def test_jma_total_and_layer_cloud_fields_are_available(self):
        for key in (
            "total_cloud_percent",
            "low_cloud_percent",
            "mid_cloud_percent",
            "high_cloud_percent",
        ):
            self.assertIn(key, JS)

    def test_auto_mode_is_not_changed_yet(self):
        auto_block = JS.split("function availableLayerKeys()", 1)[1].split(
            "function refreshModelControls()", 1
        )[0]
        self.assertNotIn("state.jmaData?.fields", auto_block)

    def test_scheduled_refresh_is_non_blocking_and_removes_stale_jma(self):
        self.assertIn("id: jma_msm", WORKFLOW)
        self.assertIn("continue-on-error: true", WORKFLOW)
        self.assertIn("jma_msm_cloud_poc.py", WORKFLOW)
        self.assertIn("jma_msm_weathergrid_browser_bundle.py", WORKFLOW)
        self.assertIn("rm -f weathergrid/jma_msm_tw_cloud_browser.json", WORKFLOW)


if __name__ == "__main__":
    unittest.main()
