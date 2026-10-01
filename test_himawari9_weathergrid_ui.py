import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class Himawari9WeatherGridUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "weather-map.html").read_text(encoding="utf-8")
        cls.js = (ROOT / "assets" / "weather-map.js").read_text(encoding="utf-8")

    def test_selector_exposes_himawari_as_observation_source(self):
        self.assertIn("<span>進階 · 資料來源</span>", self.html)
        self.assertIn('value="himawari"', self.html)
        self.assertIn("觀測 · Himawari-9 2 km", self.html)
        self.assertIn("自動預報", self.html)

    def test_browser_loads_published_himawari_bundle(self):
        self.assertIn(
            "./weathergrid/himawari9_tw_cloud_browser.json",
            self.js,
        )
        self.assertIn(
            "./weathergrid/himawari9_tw_cloud_qc.json",
            self.js,
        )
        self.assertIn("normalizeHimawariBundle", self.js)
        self.assertIn("HIMAWARI9_AHI_OBS", self.js)

    def test_observed_layers_are_not_forecast_cloud_layers(self):
        self.assertIn("observed_cloud_mask", self.js)
        self.assertIn("cloud_top_height_m", self.js)
        self.assertIn("衛星雲遮罩", self.js)
        self.assertIn("雲頂高度", self.js)
        self.assertIn("這不是預報雲量百分比", self.js)
        self.assertIn("不等同低／中／高雲量百分比", self.js)

    def test_cloud_mask_is_categorical_and_not_bilinear(self):
        self.assertIn("palette:'cloudMask'", self.js)
        self.assertIn(
            "if(isObservationMode()){",
            self.js,
        )
        self.assertIn("drawNearestCells(data,vals,cfg,visibleView)", self.js)
        self.assertIn("衛星 presentation grid 最近鄰取樣", self.js)

    def test_cloud_top_height_uses_observation_units_and_nearest_sampling(self):
        self.assertIn("palette:'cloudHeight'", self.js)
        self.assertIn("cloud_top_height_m", self.js)
        self.assertIn("原始單位 m · 顯示 km", self.js)
        self.assertIn("視差校正座標", self.js)
        self.assertIn("if(isObservationMode()){", self.js)
        self.assertIn(
            "return values[nearestCellIndex(point.lon,point.lat,data)] ?? null",
            self.js,
        )
        self.assertIn(
            "衛星 presentation grid 最近鄰取樣",
            self.js,
        )

    def test_observation_time_is_not_presented_as_forecast_lead(self):
        self.assertIn("function isObservationMode()", self.js)
        self.assertIn("觀測時間 ·", self.js)
        self.assertIn("衛星觀測", self.js)
        self.assertIn("資料年齡", self.js)
        self.assertIn("play.disabled=observation || frames.length<2", self.js)

    def test_debug_contract_exposes_observation_identity(self):
        self.assertIn("himawariAvailable: Boolean(state.himawariData)", self.js)
        self.assertIn(
            "sourceKind: activeDataset(state.layer)?.source_kind || 'forecast'",
            self.js,
        )
        self.assertIn(
            "observationTime: state.himawariData?.observation?.time_coverage_end",
            self.js,
        )

    def test_auto_forecast_does_not_include_himawari(self):
        auto_block = self.js.split(
            "function availableLayerKeys(){", 1
        )[1].split("function refreshModelControls()", 1)[0]
        self.assertIn("state.modelMode==='auto'", auto_block)
        self.assertNotIn("himawariData", auto_block)


if __name__ == "__main__":
    unittest.main()
