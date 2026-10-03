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
        self.assertIn("image_bytes_uploaded: false", self.js)
        self.assertIn("withheld_from_export", self.js)
        self.assertIn("public_photo: false", self.js)
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
        self.assertIn("nearest_catalog_viewpoint", self.js)
        self.assertIn("./field-intake.html", self.index)
        self.assertIn('data-i18n="field_intake_link"', self.index)

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
