import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class WeatherGridUiPolishTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "weather-map.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "assets" / "weather-map.css").read_text(encoding="utf-8")
        cls.js = (ROOT / "assets" / "weather-map.js").read_text(encoding="utf-8")
        cls.workflow = (
            ROOT / ".github" / "workflows" / "b117_gfs_multilayer_poc.yml"
        ).read_text(encoding="utf-8")

    def test_controls_cannot_overflow_map_panel(self):
        self.assertIn("grid-template-columns:repeat(3,minmax(0,1fr))", self.css)
        self.assertIn(".control-bar>*{min-width:0}", self.css)
        self.assertIn("#spot-select,#opportunity-select", self.css)

    def test_time_ui_is_one_navigator_instead_of_two_competing_controls(self):
        self.assertIn('class="time-navigator"', self.html)
        self.assertIn('id="time-prev"', self.html)
        self.assertIn('id="time-slider"', self.html)
        self.assertIn('id="time-next"', self.html)
        self.assertIn('id="time-play"', self.html)
        self.assertIn("function updateTimeline()", self.js)
        self.assertNotIn('class="time-control"', self.html)

    def test_direction_uses_speed_weighted_uv_circular_interpolation(self):
        self.assertIn("function windUv(speed,directionDeg)", self.js)
        self.assertIn("function bilinearWindDirection(", self.js)
        self.assertIn("drawCircularDirectionSubcells", self.js)
        self.assertIn("'bilinear_uv_circular'", self.js)
        self.assertIn("風向以 u/v 向量循環插值", self.js)

    def test_direction_palette_is_explicitly_cyclic(self):
        self.assertIn("if(cfg.palette==='direction')", self.js)
        self.assertIn("北 0°", self.js)
        self.assertIn("北 360°", self.js)

    def test_rain_rate_uses_non_linear_threshold_scale(self):
        self.assertIn("scale:'precip_rate'", self.js)
        self.assertIn("ticks:[0,.1,.5,1,2,5,10,20]", self.js)
        self.assertIn("function normalizedPiecewise(value,breaks)", self.js)

    def test_spots_cluster_at_low_zoom_and_keep_selected_spot_distinct(self):
        self.assertIn("function spotClusterRadius()", self.js)
        self.assertIn("function buildSpotHitTargets()", self.js)
        self.assertIn("function zoomToSpotCluster(spots)", self.js)
        self.assertIn("spots.length>1", self.js)

    def test_inspector_prioritizes_layer_identity_over_raw_min_max(self):
        self.assertIn('id="layer-range"', self.html)
        self.assertIn("$('layer-summary').textContent=cfg.label", self.js)
        self.assertIn("畫面資料範圍", self.js)

    def test_qc_flags_are_explained_in_user_language(self):
        self.assertIn("function qcMessage(flag)", self.js)
        self.assertIn("能見度大量達模型上限", self.js)
        self.assertIn("內部 QC 代碼", self.js)

    def test_cycle_and_valid_time_are_user_facing(self):
        self.assertIn("模型起報", self.js)
        self.assertIn("TST", self.js)
        self.assertIn("預報時間", self.js)
        self.assertIn("自動模式：依圖層選優先模型", self.js)

    def test_model_boundary_is_drawn(self):
        self.assertIn("function drawProviderBoundary(data)", self.js)
        self.assertIn("虛線＝目前模型資料範圍", self.js)

    def test_ci_runs_ui_polish_contract(self):
        self.assertIn('"test_weathergrid_ui_polish.py"', self.workflow)
        self.assertIn("test_weathergrid_ui_polish.py", self.workflow)


if __name__ == "__main__":
    unittest.main()
