import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class WeatherGridProgressiveInspectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "weather-map.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "assets" / "weather-map.css").read_text(encoding="utf-8")
        cls.js = (ROOT / "assets" / "weather-map.js").read_text(encoding="utf-8")
        cls.workflow = (
            ROOT / ".github" / "workflows" / "b117_gfs_multilayer_poc.yml"
        ).read_text(encoding="utf-8")

    def test_empty_spot_and_coverage_panels_start_hidden(self):
        self.assertIn('id="spot-panel" class="panel" hidden', self.html)
        self.assertIn('id="coverage-panel" class="panel" hidden', self.html)
        self.assertIn("function syncInspectorVisibility()", self.js)
        self.assertIn("$('spot-panel').hidden=!hasSpot", self.js)
        self.assertIn("$('coverage-panel').hidden=!hasSpot", self.js)

    def test_qc_is_integrated_into_primary_layer_panel(self):
        layer_start = self.html.index("<h2>目前圖層</h2>")
        spot_start = self.html.index('id="spot-panel"')
        layer_block = self.html[layer_start:spot_start]
        self.assertIn('id="qc-status"', layer_block)
        self.assertIn('class="layer-qc"', layer_block)
        self.assertNotIn("<h2>資料品質</h2>", self.html)
        self.assertIn("✓ 資料正常", self.js)

    def test_technical_notes_move_out_of_persistent_inspector(self):
        self.assertNotIn('class="panel note-panel"', self.html)
        self.assertNotIn("<h2>POC 限制</h2>", self.html)
        self.assertIn('id="data-info-open"', self.html)
        self.assertIn('id="data-info-dialog"', self.html)
        self.assertIn("資料與模型說明", self.html)
        self.assertIn("function initDataInfoDialog()", self.js)

    def test_hidden_is_strict_even_inside_grid_layouts(self):
        self.assertIn("[hidden]{display:none!important}", self.css)

    def test_debug_surface_reports_progressive_panel_visibility(self):
        self.assertIn("spotPanelVisible", self.js)
        self.assertIn("coveragePanelVisible", self.js)

    def test_ci_runs_progressive_inspector_contract(self):
        self.assertIn('"test_weathergrid_progressive_inspector.py"', self.workflow)
        self.assertIn("test_weathergrid_progressive_inspector.py", self.workflow)


if __name__ == "__main__":
    unittest.main()
