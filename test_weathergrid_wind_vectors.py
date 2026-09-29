import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class WeatherGridWindVectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "weather-map.html").read_text(encoding="utf-8")
        cls.js = (ROOT / "assets" / "weather-map.js").read_text(encoding="utf-8")
        cls.smoke = (ROOT / "weathergrid_production_smoke.py").read_text(encoding="utf-8")
        cls.workflow = (
            ROOT / ".github" / "workflows" / "b117_gfs_multilayer_poc.yml"
        ).read_text(encoding="utf-8")

    def test_ui_exposes_wind_vector_toggle(self):
        self.assertIn('id="wind-vector-toggle"', self.html)
        self.assertIn("顯示 10 m 風向箭頭", self.html)

    def test_vectors_use_speed_and_meteorological_direction(self):
        self.assertIn("function drawWindVectors()", self.js)
        self.assertIn("wind_speed_10m_m_s", self.js)
        self.assertIn("wind_direction_10m_deg", self.js)
        self.assertIn("const toward=((direction+180)%360)", self.js)
        self.assertIn("speed<0.5", self.js)

    def test_vector_density_adapts_to_zoom(self):
        self.assertIn("function windVectorStep()", self.js)
        self.assertIn("if(zoom>=8) return 1", self.js)
        self.assertIn("if(zoom>=6.4) return 2", self.js)
        self.assertIn("return 3", self.js)

    def test_wind_layer_auto_enables_vectors_until_user_touches_toggle(self):
        self.assertIn("windVectorTouched:false", self.js)
        self.assertIn("if(windLayer && hasWind && !state.windVectorTouched)", self.js)
        self.assertIn("state.windVectorTouched=true", self.js)

    def test_production_smoke_exercises_wind_vectors(self):
        self.assertIn('select_by_value("wind_speed_10m_m_s")', self.smoke)
        self.assertIn("windVectors === true", self.smoke)
        self.assertIn('"wind-vector-toggle"', self.smoke)

    def test_b117_ci_runs_wind_vector_contract(self):
        self.assertIn('"test_weathergrid_wind_vectors.py"', self.workflow)
        self.assertIn("test_weathergrid_wind_vectors.py", self.workflow)


if __name__ == "__main__":
    unittest.main()
