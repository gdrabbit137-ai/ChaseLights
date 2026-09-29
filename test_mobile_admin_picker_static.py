import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class MobileAdminPickerStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "assets" / "app.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "assets" / "app.css").read_text(encoding="utf-8")

    def test_mobile_picker_has_explicit_exit_paths(self):
        for needle in (
            "data-admin-backdrop",
            "data-admin-close",
            "data-admin-done",
            "closeMobileAdminPicker",
            "popstate",
            "e.key==='Escape'",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.app)

    def test_mobile_picker_locks_and_restores_page_scroll(self):
        self.assertIn("lockAdminPickerScroll", self.app)
        self.assertIn("unlockAdminPickerScroll", self.app)
        self.assertIn("admin-picker-open", self.css)
        self.assertIn("window.scrollTo(0,adminPickerScrollY)", self.app)

    def test_mobile_picker_is_bounded_bottom_sheet(self):
        self.assertIn("height: min(72dvh, 680px)", self.css)
        self.assertIn("max-height: 82dvh", self.css)
        self.assertIn("position: fixed", self.css)
        self.assertIn("env(safe-area-inset-bottom)", self.css)

    def test_mobile_picker_keeps_search_and_multi_select(self):
        self.assertIn("adminAreaSearchPlaceholder", self.app)
        self.assertIn("previousSearch", self.app)
        self.assertIn("aria-pressed", self.app)
        self.assertIn("admin-area-check", self.css)

    def test_mobile_picker_tracks_breakpoint_changes(self):
        self.assertIn("adminPickerMedia.addEventListener('change'", self.app)
        self.assertIn("const isMobileAdminPicker=()=>adminPickerMedia.matches", self.app)

    def test_mobile_trigger_opens_sheet_explicitly(self):
        self.assertIn("summaryButton.addEventListener('click'", self.app)
        self.assertIn("details.open=true", self.app)
        self.assertIn("openMobileAdminPicker(details)", self.app)

    def test_mobile_picker_does_not_inherit_unlocked_desktop_open_state(self):
        self.assertIn(
            "const wasOpen=!!previousDetails?.open&&(!mobile||document.body.classList.contains('admin-picker-open'))",
            self.app,
        )

    def test_desktop_groups_are_not_collapsible_controls(self):
        self.assertIn("@media (min-width: 641px)", self.css)
        self.assertIn("pointer-events: none", self.css)


if __name__ == "__main__":
    unittest.main()
