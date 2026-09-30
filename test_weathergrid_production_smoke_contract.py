import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class WeatherGridProductionSmokeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = (ROOT / "weathergrid_production_smoke.py").read_text(encoding="utf-8")
        cls.workflow = (
            ROOT / ".github" / "workflows" / "b145_weathergrid_production_smoke.yml"
        ).read_text(encoding="utf-8")

    def test_smoke_targets_public_weathergrid(self):
        self.assertIn("https://chaselights.app/weather-map.html", self.script)
        self.assertIn("__weatherGridPreviewReady", self.script)
        self.assertIn("basemap-status", self.script)
        self.assertIn("maplibregl-canvas", self.script)
        self.assertIn("AUTO · GFS", self.script)
        self.assertIn("CWA WRF 3 km", self.script)
        self.assertIn("CWA_WRF_3KM", self.script)
        self.assertIn("JMA MSM 5 km", self.script)
        self.assertIn("JMA_MSM", self.script)
        self.assertIn("Himawari-9 2 km", self.script)
        self.assertIn("HIMAWARI9_AHI_OBS", self.script)
        self.assertIn("observed_cloud_mask", self.script)
        self.assertIn("cloud_top_height_m", self.script)
        self.assertIn("sourceKind === 'observation'", self.script)
        self.assertIn("觀測時間", self.script)
        self.assertIn("衛星觀測", self.script)
        self.assertIn("total_cloud_percent", self.script)
        self.assertIn("high_cloud_percent", self.script)
        self.assertIn("model-select", self.script)
        self.assertIn("time-slider", self.script)
        self.assertIn("time-label", self.script)
        self.assertNotIn("#timeline button", self.script)
        self.assertIn("tw-073", self.script)
        self.assertIn("coverageSource", self.script)

    def test_smoke_captures_visual_artifact(self):
        self.assertIn("save_screenshot", self.script)
        self.assertIn("weathergrid-production-smoke.png", self.script)

    def test_workflow_has_pr_contract_and_post_merge_production_run(self):
        self.assertIn("pull_request:", self.workflow)
        self.assertIn("push:", self.workflow)
        self.assertIn("branches: [main]", self.workflow)
        self.assertIn("workflow_dispatch:", self.workflow)
        self.assertIn("test_weathergrid_production_smoke_contract.py", self.workflow)
        self.assertIn("weathergrid_production_smoke.py", self.workflow)
        self.assertIn("weathergrid/jma_msm_tw_cloud_browser.json", self.workflow)
        self.assertIn("weathergrid/jma_msm_tw_cloud_qc.json", self.workflow)
        self.assertIn("https://chaselights.app/weather-map.html", self.workflow)
        self.assertIn("actions/upload-artifact@v4", self.workflow)
        self.assertIn("sha256sum weather-map.html", self.workflow)
        self.assertIn("sha256sum assets/weather-map.js", self.workflow)
        self.assertIn("sha256sum assets/weather-map.css", self.workflow)
        self.assertIn("live_html_sha", self.workflow)
        self.assertIn("live_js_sha", self.workflow)
        self.assertIn("live_css_sha", self.workflow)


if __name__ == "__main__":
    unittest.main()
