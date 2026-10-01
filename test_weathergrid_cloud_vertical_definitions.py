import unittest
from pathlib import Path

from weathergrid_browser_bundle import CLOUD_VERTICAL_DEFINITIONS
from icon_weathergrid_browser_bundle import ICON_CLOUD_VERTICAL_DEFINITIONS


ROOT = Path(__file__).resolve().parent
JS = (ROOT / "assets" / "weather-map.js").read_text(encoding="utf-8")
HTML = (ROOT / "weather-map.html").read_text(encoding="utf-8")
GFS_BUNDLE = (ROOT / "weathergrid_browser_bundle.py").read_text(encoding="utf-8")
ICON_BUNDLE = (ROOT / "icon_weathergrid_browser_bundle.py").read_text(encoding="utf-8")


class WeatherGridCloudVerticalDefinitionTests(unittest.TestCase):
    def test_icon_native_pressure_layers_match_dwd_contract(self):
        self.assertEqual(
            ICON_CLOUD_VERTICAL_DEFINITIONS["low_cloud_percent"]["native_definition"],
            "surface–800 hPa",
        )
        self.assertEqual(
            ICON_CLOUD_VERTICAL_DEFINITIONS["mid_cloud_percent"]["native_definition"],
            "800–400 hPa",
        )
        self.assertEqual(
            ICON_CLOUD_VERTICAL_DEFINITIONS["high_cloud_percent"]["native_definition"],
            "<400 hPa",
        )

    def test_gfs_native_pressure_layers_match_upp_contract(self):
        self.assertEqual(
            CLOUD_VERTICAL_DEFINITIONS["low_cloud_percent"]["native_definition"],
            "surface–642 hPa",
        )
        self.assertEqual(
            CLOUD_VERTICAL_DEFINITIONS["mid_cloud_percent"]["native_definition"],
            "642–350 hPa",
        )
        self.assertEqual(
            CLOUD_VERTICAL_DEFINITIONS["high_cloud_percent"]["native_definition"],
            "<350 hPa",
        )

    def test_ui_has_model_specific_vertical_definition_panel(self):
        self.assertIn('id="layer-vertical"', HTML)
        self.assertIn("vertical_definition", JS)
        self.assertIn("native_definition", JS)
        self.assertIn("approx_height", JS)
        self.assertIn("ICON Global", JS)
        self.assertIn("GFS 0.25°", JS)
        self.assertIn("vertical_definition", GFS_BUNDLE)
        self.assertIn("vertical_definition", ICON_BUNDLE)

    def test_cwa_does_not_masquerade_pressure_rh_as_cloud_cover(self):
        self.assertIn("CWA M-A0064", JS)
        self.assertIn("不以相對濕度代理冒充雲量", JS)
        self.assertIn("CWA M-A0064 實際 GRIB 沒有原生低／中／高雲量", HTML)


if __name__ == "__main__":
    unittest.main()
