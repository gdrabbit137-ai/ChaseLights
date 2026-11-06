import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent
WORKFLOW = ROOT / ".github" / "workflows" / "b169_viirs_live_ingest.yml"


class ViirsProductionPublishWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_can_publish_to_main(self):
        self.assertIn("contents: write", self.text)
        self.assertIn("Publish QC-passing VIIRS snapshot", self.text)
        self.assertIn("git push origin HEAD:main", self.text)

    def test_only_runtime_browser_and_qc_files_are_committed(self):
        publish = self.text.split("- name: Publish QC-passing VIIRS snapshot", 1)[1]
        # Region-resolved viirs_nightlights_<region>_{browser,qc} filenames match
        # assets/weather-map.js REGION_SOURCE_CATALOG.viirs.file().
        self.assertIn("${{ steps.region.outputs.browser }}", publish)
        self.assertIn("${{ steps.region.outputs.qc }}", publish)
        self.assertNotIn(".cache/viirs_gibs", publish)
        self.assertNotIn("*.png", publish)
        self.assertNotIn("manifest.json", publish)

    def test_publish_occurs_after_fail_closed_semantic_validation(self):
        validate = self.text.index("- name: Validate artifact semantics")
        publish = self.text.index("- name: Publish QC-passing VIIRS snapshot")
        self.assertLess(validate, publish)
        self.assertIn('assert not qcj["flags"], qcj', self.text)

    def test_yaml_is_valid(self):
        self.assertIsNotNone(yaml.safe_load(self.text))


if __name__ == "__main__":
    unittest.main()
