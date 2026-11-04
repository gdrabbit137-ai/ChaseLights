# CL-WG-14: negative contract tests — the CL-WG-11 GFS bbox-outside feathered
# fill is CANCELLED (owner ruling 2026-11-04). In regional-model mode the
# regional product renders only inside its own coverage, honestly blank
# outside it (QC note), with no GFS fill pass and no mixed-source label.
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = (ROOT / "weather-map.html").read_text(encoding="utf-8")
JS = (ROOT / "assets" / "weather-map.js").read_text(encoding="utf-8")

REGIONAL_NOTE = "此為區域產品，僅在其涵蓋範圍內繪製，範圍外留白"


class ClWg14GfsFillRemoved(unittest.TestCase):
    def test_fill_helper_bundle_is_deleted_and_not_loaded(self):
        self.assertFalse((ROOT / "assets" / "weather-map-gfs-fill.js").exists())
        self.assertNotIn("weather-map-gfs-fill", HTML)

    def test_no_fill_machinery_remains_in_weather_map_js(self):
        for token in ["gfsFillPlanForView", "drawGfsFillLayer",
                      "gfsFillNoteHtml", "gfsFillActive",
                      "WeatherMapGfsFill", "rawViewBbox"]:
            self.assertNotIn(token, JS, f"{token} must be removed")

    def test_no_mixed_source_label_remains(self):
        self.assertNotIn("混合來源", JS)
        self.assertNotIn("GFS 預報填充", JS)

    def test_regional_product_honest_blank_note_is_kept(self):
        self.assertIn("function regionalModelNoteHtml", JS)
        self.assertIn(REGIONAL_NOTE, JS)
        # note shows only when the active main source is NOT the GFS bundle
        self.assertIn("mainData===state.data || !mainData?.bbox) return ''", JS)


if __name__ == "__main__":
    unittest.main()