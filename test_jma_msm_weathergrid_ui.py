import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
JS = (ROOT / "assets" / "weather-map.js").read_text(encoding="utf-8")
HTML = (ROOT / "weather-map.html").read_text(encoding="utf-8")


class JmaMsmWeatherGridUiTests(unittest.TestCase):
    def test_model_selector_exposes_jma_msm(self):
        self.assertIn('value="jma">JMA MSM 5 km', HTML)
        self.assertIn("JMA MSM 5 km", HTML)
        self.assertIn("22.4°N", HTML)
        self.assertIn("120°E", HTML)

    def test_browser_loads_optional_jma_bundle(self):
        self.assertIn("jma_msm_tw_cloud_browser.json", JS)
        self.assertIn("jma_msm_tw_cloud_qc.json", JS)
        self.assertIn("state.jmaData", JS)
        self.assertIn("state.jmaQc", JS)
        self.assertIn("JMA MSM 5 km", JS)

    def test_jma_keeps_own_timeline_and_bbox(self):
        self.assertIn("state.modelMode==='jma'", JS)
        self.assertIn("timelineDataset()", JS)
        self.assertIn("setViewBbox(timeline.bbox", JS)
        self.assertIn("native_time_interval_hours", JS)

    def test_jma_cloud_layers_include_total_low_mid_high(self):
        for key in (
            "total_cloud_percent",
            "low_cloud_percent",
            "mid_cloud_percent",
            "high_cloud_percent",
        ):
            self.assertIn(key, JS)

    def test_jma_vertical_definition_is_rendered_from_field_metadata(self):
        self.assertIn("vertical_definition", JS)
        self.assertIn("native_definition", JS)
        self.assertIn("approx_height", JS)
        self.assertIn("usingJma?'JMA MSM 5 km'", JS)

    def test_jma_uses_true_model_forecast_lead_from_aws_cycle(self):
        self.assertNotIn("API 發布時間軸", JS)
        self.assertIn("frameLead", JS)
        self.assertIn("padStart(3,'0')", JS)

    def test_jma_transport_attribution_is_visible(self):
        self.assertIn('id="source-attribution"', HTML)
        self.assertIn("Open-Meteo", JS)
        self.assertIn("資料模型：JMA MSM", JS)
        self.assertIn("Open-Meteo AWS", JS)
        self.assertIn("https://registry.opendata.aws/open-meteo/", JS)

    def test_b172_auto_policy_explicitly_includes_jma(self):
        self.assertIn("function autoDataset(key=state.layer)", JS)
        self.assertIn("[state.cwaData,state.jmaData,state.iconData,state.data]", JS)
        self.assertIn("datasetHasFrameForLayer(data,key,validTime)", JS)
        self.assertIn("if(data===state.jmaData) return state.jmaQc", JS)


if __name__ == "__main__":
    unittest.main()
