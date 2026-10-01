import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
JS = (ROOT / "assets" / "weather-map.js").read_text(encoding="utf-8")
HTML = (ROOT / "weather-map.html").read_text(encoding="utf-8")


class CwaWeatherGridUiContractTests(unittest.TestCase):
    def test_model_selector_exposes_cwa_without_replacing_existing_modes(self):
        self.assertIn('id="model-select"', HTML)
        self.assertIn('value="cwa">CWA WRF 3 km', HTML)
        self.assertIn('value="icon">ICON Global', HTML)
        self.assertIn('value="gfs">GFS 0.25°', HTML)
        self.assertIn('value="auto">自動', HTML)

    def test_browser_loads_cwa_as_optional_provider(self):
        self.assertIn("cwa_wrf3_tw_weather_browser.json", JS)
        self.assertIn("cwa_wrf3_tw_weather_qc.json", JS)
        self.assertIn("state.cwaData", JS)
        self.assertIn("switchModel", JS)

    def test_each_manual_model_owns_its_timeline_and_boundary(self):
        self.assertIn("function timelineDataset()", JS)
        self.assertIn("setViewBbox(timeline.bbox", JS)
        self.assertIn("timelineDataset().frames.map", JS)
        self.assertIn("公開資料間隔", JS)

    def test_cwa_unique_fields_are_available(self):
        for key in (
            "temperature_2m_c",
            "relative_humidity_2m_percent",
            "precip_total_mm",
            "shortwave_flux_w_m2",
        ):
            self.assertIn(key, JS)

    def test_auto_mode_uses_explicit_photographer_first_provider_policy(self):
        self.assertIn("function autoDataset(key=state.layer)", JS)
        self.assertIn("? [state.cwaData,state.jmaData,state.iconData,state.data]", JS)
        self.assertIn(": [state.cwaData,state.jmaData,state.data,state.iconData]", JS)
        self.assertIn("datasetHasFrameForLayer(data,key,validTime)", JS)


if __name__ == "__main__":
    unittest.main()
