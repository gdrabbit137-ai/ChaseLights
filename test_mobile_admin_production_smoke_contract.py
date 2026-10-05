import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class MobileAdminProductionSmokeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = (ROOT / "mobile_admin_production_smoke.py").read_text(encoding="utf-8")
        cls.workflow = (
            ROOT / ".github" / "workflows" / "b149_mobile_admin_production_smoke.yml"
        ).read_text(encoding="utf-8")

    def test_smoke_targets_public_homepage_and_phone_viewport(self):
        self.assertIn("https://chaselights.app/index.html", self.script)
        self.assertIn('"width": 390', self.script)
        self.assertIn('"height": 844', self.script)
        self.assertIn("isMobileAdminPicker", self.script)
        self.assertIn("admin-picker-open", self.script)
        self.assertIn('data-admin-area="花蓮縣"', self.script)
        self.assertIn("data-admin-done", self.script)

    def test_smoke_checks_bottom_sheet_contract(self):
        self.assertIn("ariaModal", self.script)
        self.assertIn("sheetHeight", self.script)
        self.assertIn("bodyPosition", self.script)
        self.assertIn("aria-pressed", self.script)
        self.assertIn("scroll_before", self.script)
        self.assertIn("mobile admin picker scroll restoration", self.script)
        self.assertIn('d.execute_script("return window.scrollY") - before_scroll', self.script)
        self.assertIn("save_screenshot", self.script)

    def test_smoke_checks_production_localization_on_phone_and_desktop(self):
        for needle in (
            "switchLanguage('en')",
            "Photography Weather Forecast",
            "semantic_locale_snapshot",
            "contains_han",
            '"width": 1440',
            "switchLanguage('ja')",
            "撮影向け気象予報",
            "english_place_guide_no_han",
            "japanese_semantic_rerendered",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.script)

    def test_workflow_waits_for_exact_deployed_homepage_bytes(self):
        for needle in (
            "sha256sum index.html",
            "sha256sum assets/app.js",
            "sha256sum assets/app.css",
            "live_html_sha",
            "live_js_sha",
            "live_css_sha",
            "https://chaselights.app/index.html",
            "mobile_admin_production_smoke.py",
            "actions/upload-artifact@v4",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.workflow)


if __name__ == "__main__":
    unittest.main()
