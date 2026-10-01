import unittest
from pathlib import Path

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
        self.assertIn("weathergrid/viirs_nightlights_tw_browser.json", publish)
        self.assertIn("weathergrid/viirs_nightlights_tw_qc.json", publish)
        self.assertNotIn(".cache/viirs", publish.split("- uses: actions/upload-artifact", 1)[0])
        self.assertNotIn("*.h5", publish.split("- uses: actions/upload-artifact", 1)[0])

    def test_publish_occurs_after_fail_closed_semantic_validation(self):
        validate = self.text.index("- name: Validate artifact semantics")
        publish = self.text.index("- name: Publish QC-passing VIIRS snapshot")
        self.assertLess(validate, publish)
        self.assertIn('assert not qc["flags"], qc', self.text)


if __name__ == "__main__":
    unittest.main()
