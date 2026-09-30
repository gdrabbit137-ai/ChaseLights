import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class HimawariWeatherGridUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "weather-map.html").read_text(encoding="utf-8")
        cls.js = (ROOT / "assets" / "weather-map.js").read_text(encoding="utf-8")
        cls.workflow = (
            ROOT / ".github" / "workflows" / "b117_gfs_multilayer_poc.yml"
        ).read_text(encoding="utf-8")

    def test_observation_is_a_separate_data_mode(self):
        self.assertIn('id="data-mode-select"', self.html)
        self.assertIn('value="forecast"', self.html)
        self.assertIn('value="observed"', self.html)
        self.assertIn("function switchDataMode(mode)", self.js)
        self.assertIn("dataMode:'forecast'", self.js)

    def test_himawari_bundle_is_loaded_fail_soft(self):
        self.assertIn("LIVE_HIMAWARI_DATA", self.js)
        self.assertIn("LIVE_HIMAWARI_QC", self.js)
        self.assertIn("Himawari-9 observed cloud bundle unavailable", self.js)
        self.assertIn("himawariAvailable: Boolean(state.himawariData)", self.js)

    def test_observation_layers_keep_native_semantics(self):
        self.assertIn("observed_cloud_mask", self.js)
        self.assertIn("cloud_top_height_m", self.js)
        self.assertIn("這是衛星觀測分類，不是雲量百分比", self.js)
        self.assertIn("不把觀測值轉成預報雲量", self.js)

    def test_observation_uses_nearest_neighbour_not_forecast_interpolation(self):
        self.assertIn(
            "if(isObservedMode()){\n      drawNearestCells(data,vals,cfg,visibleView);",
            self.js,
        )
        self.assertIn(
            "if(isObservedMode()) return values[nearestCellIndex",
            self.js,
        )
        self.assertIn("不做雙線性內插", self.js)

    def test_observation_time_and_age_are_explicit(self):
        self.assertIn("function formatObservationAge(iso)", self.js)
        self.assertIn("觀測時間", self.js)
        self.assertIn("OBSERVED · Himawari-9", self.js)
        self.assertIn("單一實況", self.js)

    def test_observation_qc_exposes_distance_and_missing_retrieval(self):
        self.assertIn("nearest_distance_m", self.js)
        self.assertIn("最近鄰距離 p99", self.js)
        self.assertIn("cloud_fraction", self.js)
        self.assertIn("雲頂高度有效 retrieval", self.js)
        self.assertIn("其餘保持 missing", self.js)

    def test_ci_runs_b158_contract(self):
        self.assertIn("test_himawari_weathergrid_ui.py", self.workflow)
        self.assertIn("B158_HIMAWARI9_OBSERVED_WEATHERGRID_UI.md", self.workflow)


if __name__ == "__main__":
    unittest.main()
