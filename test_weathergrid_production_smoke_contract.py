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
        self.assertIn("LIVE GFS", self.script)
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
