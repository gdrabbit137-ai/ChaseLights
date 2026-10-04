from pathlib import Path
import re
import unittest

ROOT = Path(__file__).parent

class FieldIntakeStaticTest(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT / "field-intake.html").read_text(encoding="utf-8")
        self.js = (ROOT / "assets" / "field-intake.js").read_text(encoding="utf-8")
        self.spec = (ROOT / "RESEARCH_EVIDENCE_SPEC_R4_2.md").read_text(encoding="utf-8")
        self.handoff = (ROOT / "B120_FIELD_OBSERVATION_INTAKE.md").read_text(encoding="utf-8")
        self.index = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_local_first_contract(self):
        self.assertIn("field-observation-draft-r4.2-1", self.js)
        self.assertIn('"unreviewed"', self.js)
        self.assertRegex(self.js, r"image_bytes_uploaded\s*:\s*false")
        self.assertIn("withheld_from_export", self.js)
        self.assertRegex(self.js, r"public_photo\s*:\s*false")
        self.assertNotIn("FormData(", self.js)
        self.assertNotIn("XMLHttpRequest", self.js)

    def test_supported_file_picker_and_pinned_parser(self):
        self.assertIn("image/jpeg", self.html)
        self.assertIn("image/heic", self.html)
        self.assertIn("image/heif", self.html)
        self.assertIn("exifr@7.1.3/dist/lite.umd.js", self.html)

    def test_only_catalog_fetch_is_present(self):
        fetch_targets = re.findall(r"fetch\(([^\n]+)", self.js)
        self.assertEqual(len(fetch_targets), 1, fetch_targets)
        self.assertIn("CATALOG_URL", fetch_targets[0])

    def test_catalog_place_matching_contract(self):
        self.assertIn("runtime_catalog_v004_r4_2.json", self.js)
        self.assertIn("searchPlaceCandidates", self.js)
        self.assertIn('role","combobox"', self.js)
        self.assertIn("selected_spot_id:null", self.js)
        self.assertNotIn("placeOptions(", self.js)
        self.assertNotIn("place-select", self.js)
        self.assertIn("user_confirmed_gps_suggestion", self.js)
        self.assertIn("user_override", self.js)
        self.assertIn("manual_search_selection", self.js)
        self.assertIn('"unmatched"', self.js)
        self.assertIn("gps_suggestion", self.js)
        self.assertIn("./field-intake.html", self.index)
        self.assertIn('data-i18n="field_intake_link"', self.index)

    def test_photographer_facing_surface_hides_internal_bookkeeping(self):
        for forbidden in (
            "B120",
            "ground truth",
            "observation JSON",
            "field-observation-draft-r4.2-1",
            "unreviewed",
            "FV-",
        ):
            self.assertNotIn(forbidden, self.html)
        self.assertIn("照片只會在你的裝置上讀取，不會上傳", self.html)
        self.assertIn('id="language-select"', self.html)
        self.assertIn('data-i18n="review_help"', self.html)

    def test_localization_and_observation_semantics(self):
        for locale in ('"zh-TW"', '"en"', '"ja"'):
            self.assertIn(locale, self.js)
        for key in (
            "gps_suggestion",
            "close_results",
            "selected_override",
            "subject_empty",
            "partial_outcome",
            "failure_reason",
            "user_capture_time",
        ):
            self.assertIn(key, self.js)
        self.assertIn('outcome:""', self.js)
        self.assertIn("user_supplied_local_time", self.js)

    def test_localization_never_falls_back_to_another_supported_locale(self):
        self.assertNotIn('||L["zh-TW"][k]', self.js)
        self.assertNotIn('return o.name_zh||o.name_en||o.name_ja', self.js)
        self.assertIn("const THEME_LABELS=", self.js)
        self.assertIn('return (THEME_LABELS[state.lang]&&THEME_LABELS[state.lang][o.legacy_theme])||t("subject_generic");', self.js)
        self.assertIn('translation_unavailable:', self.js)
        self.assertNotIn('catalog_error:"Place data failed to load: {e}"', self.js)

    def test_ground_truth_boundary_documented(self):
        self.assertIn("unreviewed observation draft", self.spec)
        self.assertIn("does not admit a Field Validation case", self.spec)
        self.assertIn("ground truth", self.spec)

    def test_historical_handoff_is_not_policy_source(self):
        self.assertIn("historical implementation handoff", self.handoff)
        self.assertIn("not the current policy source-of-truth", self.handoff)
        self.assertIn("RESEARCH_EVIDENCE_SPEC_R4_2.md", self.handoff)
        self.assertIn("NAVIGATION_SPEC_R4_2.md", self.handoff)

if __name__ == "__main__":
    unittest.main()
