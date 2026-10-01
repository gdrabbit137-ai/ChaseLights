import unittest
from pathlib import Path


class ViirsLiveWorkflowContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = Path(".github/workflows/b169_viirs_live_ingest.yml").read_text(encoding="utf-8")

    def test_live_ingest_is_manual_and_secret_gated(self):
        self.assertIn("workflow_dispatch:", self.workflow)
        self.assertIn("secrets.EARTHDATA_TOKEN", self.workflow)
        self.assertIn("Require Earthdata token secret", self.workflow)
        self.assertNotIn("echo $EARTHDATA_TOKEN", self.workflow)

    def test_live_ingest_fails_closed_before_multi_tile_publish(self):
        self.assertIn('Expected one VNP46A4 tile for Taiwan bbox', self.workflow)
        self.assertIn('Add mosaic support before publishing', self.workflow)

    def test_artifact_keeps_nasa_semantics(self):
        self.assertIn('nasa_black_marble_vnp46a4', self.workflow)
        self.assertIn('10.5067/VIIRS/VNP46A4.002', self.workflow)
        self.assertIn('not Bortle class', self.workflow)


if __name__ == "__main__":
    unittest.main()
