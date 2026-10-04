import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class FieldIntakeProductionSmokeContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = (ROOT / "field_intake_production_smoke.py").read_text(
            encoding="utf-8"
        )
        cls.workflow = (
            ROOT / ".github" / "workflows" / "field_intake_production_smoke.yml"
        ).read_text(encoding="utf-8")

    def test_smoke_targets_public_field_intake_and_mobile_viewport(self):
        self.assertIn("https://chaselights.app/field-intake.html", self.script)
        self.assertIn("ChaseLightsFieldIntake", self.script)
        self.assertIn("selected_spot_id", self.script)
        self.assertIn("association_method", self.script)
        self.assertIn("gps_suggestion", self.script)
        self.assertIn("390, 844", self.script)
        self.assertIn("mobile_overflow_px", self.script)

    def test_smoke_covers_search_unmatched_close_and_localization(self):
        for needle in (
            "place-search-input",
            "place-option[data-spot-id]",
            "close-results",
            "selected-place.unmatched",
            "manual_search_selection",
            "Unmatched",
            "実写検証",
            "save_screenshot",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.script)

    def test_workflow_pins_deployed_field_intake_bytes(self):
        for needle in (
            "sha256sum field-intake.html",
            "sha256sum assets/field-intake.js",
            "sha256sum assets/field-intake.css",
            "sha256sum runtime_catalog_v004_r4_2.json",
            "https://chaselights.app/field-intake.html",
            "https://chaselights.app/assets/field-intake.js",
            "https://chaselights.app/assets/field-intake.css",
            "https://chaselights.app/runtime_catalog_v004_r4_2.json",
            "field_intake_production_smoke.py",
            "actions/upload-artifact@v4",
            "workflow_dispatch:",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.workflow)


if __name__ == "__main__":
    unittest.main()
