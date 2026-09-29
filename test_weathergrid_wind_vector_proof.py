import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class WeatherGridWindVectorProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.js = (ROOT / "assets" / "weather-map.js").read_text(encoding="utf-8")
        cls.smoke = (ROOT / "weathergrid_production_smoke.py").read_text(encoding="utf-8")
        cls.workflow = (
            ROOT / ".github" / "workflows" / "b117_gfs_multilayer_poc.yml"
        ).read_text(encoding="utf-8")

    def test_renderer_reports_actual_vector_count(self):
        self.assertIn("lastWindVectorCount:0", self.js)
        self.assertIn("state.lastWindVectorCount=0", self.js)
        self.assertIn("state.lastWindVectorCount+=1", self.js)
        self.assertIn("windVectorCount: state.lastWindVectorCount", self.js)

    def test_production_smoke_requires_at_least_one_rendered_vector(self):
        self.assertIn("windVectorCount > 0", self.smoke)
        self.assertIn("wind-overview", self.smoke)
        self.assertIn("wind_overview_screenshot", self.smoke)

    def test_b117_ci_runs_proof_contract(self):
        self.assertIn('"test_weathergrid_wind_vector_proof.py"', self.workflow)
        self.assertIn("test_weathergrid_wind_vector_proof.py", self.workflow)


if __name__ == "__main__":
    unittest.main()
