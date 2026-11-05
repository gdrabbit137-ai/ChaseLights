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

    def test_live_ingest_mosaics_all_discovered_tiles(self):
        self.assertIn("Build WeatherGrid mosaic", self.workflow)
        self.assertIn('args+=(--input-h5 "$file")', self.workflow)
        self.assertIn('"${args[@]}"', self.workflow)
        self.assertIn("No VNP46A4 source tiles were downloaded", self.workflow)

    def test_live_ingest_is_region_parameterized(self):
        # CL-DATA-07: tw is the default, us uses the us region bbox and the
        # viirs_nightlights_<region> filename convention that
        # assets/weather-map.js REGION_SOURCE_CATALOG.viirs.file() resolves.
        self.assertIn('default: "tw"', self.workflow)
        self.assertIn('default_bbox="125,25,-70.5,49.5"', self.workflow)
        self.assertIn('browser="viirs_nightlights_us_browser.json"', self.workflow)
        self.assertIn('qc="viirs_nightlights_us_qc.json"', self.workflow)
        self.assertIn('default_bbox="119.5,21.5,122.5,25.5"', self.workflow)
        self.assertIn('browser="viirs_nightlights_tw_browser.json"', self.workflow)
        # The explicit bbox input still overrides the region default.
        self.assertIn('if [ -n "${{ inputs.bbox }}" ]', self.workflow)


    def test_artifact_keeps_nasa_semantics(self):
        self.assertIn('nasa_black_marble_vnp46a4', self.workflow)
        self.assertIn('10.5067/VIIRS/VNP46A4.002', self.workflow)
        self.assertIn('not Bortle class', self.workflow)


if __name__ == "__main__":
    unittest.main()
