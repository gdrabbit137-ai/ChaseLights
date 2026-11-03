# CL-WG-11: GFS bbox-outside fill (Taiwan pilot) — static contract tests.
# Verifies the honest-degradation label, the fill wiring in weather-map.js,
# and that the fill never applies where semantics differ.
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = (ROOT / "weather-map.html").read_text(encoding="utf-8")
JS = (ROOT / "assets" / "weather-map.js").read_text(encoding="utf-8")
HELPER = (ROOT / "assets" / "weather-map-gfs-fill.js").read_text(encoding="utf-8")

GFS_FILL_NOTE = "bbox 外為 GFS 預報填充，與主源解析度/語義不同；接合帶為混合來源"


class ClWg11GfsFillContract(unittest.TestCase):
    def test_helper_script_is_loaded_by_weather_map_page(self):
        self.assertIn("weather-map-gfs-fill.js", HTML)
        # helper must load BEFORE weather-map.js so window.WeatherMapGfsFill exists
        self.assertLess(
            HTML.index("weather-map-gfs-fill.js"), HTML.index("weather-map.js?"))

    def test_honest_label_present_in_qc_panel_path(self):
        self.assertIn(GFS_FILL_NOTE, JS)

    def test_label_is_tied_to_active_fill_state(self):
        self.assertIn("gfsFillNoteHtml", JS)
        self.assertIn("state.gfsFillActive", JS)

    def test_fill_pass_wired_into_draw(self):
        self.assertIn("drawGfsFillLayer", JS)
        self.assertIn("gfsFillPlanForView", JS)
        self.assertIn("WeatherMapGfsFill.gfsFillPlan", JS)

    def test_no_semantic_mismatch_fields_in_fillable_set(self):
        # helper fillable set must be exactly the GFS-semantics keys; anything
        # else (satellite mask, AOD, PM2.5, night lights, CWA-only fields)
        # must stay blank outside the bbox.
        for forbidden in ["observed_cloud_mask", "cloud_top_height_m",
                          "aerosol_optical_depth_550nm", "pm2_5_ug_m3",
                          "nighttime_lights_radiance_nw_cm2_sr",
                          "relative_humidity_2m_percent", "temperature_2m_c",
                          "precip_total_mm", "shortwave_flux_w_m2"]:
            self.assertNotIn(f"'{forbidden}'", HELPER)

    def test_pilot_scope_is_taiwan_only(self):
        self.assertIn("['tw']", HELPER)


if __name__ == "__main__":
    unittest.main()