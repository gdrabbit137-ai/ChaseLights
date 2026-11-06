import unittest
from pathlib import Path

import yaml


WORKFLOW = Path(".github/workflows/b169_viirs_live_ingest.yml")


class ViirsGibsWorkflowContractTest(unittest.TestCase):
    """CL-CI-20: the live ingest is the GIBS daily DNB pipeline, no secrets."""

    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")
        cls.parsed = yaml.safe_load(cls.workflow)

    def test_workflow_yaml_parses(self):
        self.assertEqual(self.parsed["jobs"]["live-ingest"]["timeout-minutes"], 60)

    def test_live_ingest_needs_no_earthdata_secret(self):
        # LAADS path is a dead end; GIBS is public and must not gate on tokens.
        self.assertNotIn("EARTHDATA_TOKEN", self.workflow)
        self.assertNotIn("ladsweb", self.workflow.lower())
        self.assertNotIn("viirs_lads_download.py", self.workflow)

    def test_live_ingest_is_manual_and_region_parameterized(self):
        self.assertIn("workflow_dispatch:", self.workflow)
        for region in ("tw", "jp", "us", "ak", "hi"):
            self.assertIn(region, self.workflow)
        self.assertIn('default_bbox="122,24,146,46"', self.workflow)
        self.assertIn('default_bbox="-125,25,-70.5,49.5"', self.workflow)
        self.assertIn('default_bbox="-158,55,-132,69.5"', self.workflow)
        self.assertIn('default_bbox="-160.3,18.8,-154.8,22.4"', self.workflow)
        self.assertIn('default_bbox="119.5,21.5,122.5,25.5"', self.workflow)
        self.assertIn('if [ -n "${{ inputs.bbox }}" ]', self.workflow)

    def test_download_step_is_fail_closed_gibs_noaa20(self):
        self.assertIn("python viirs_gibs_download.py", self.workflow)
        self.assertIn("--date", self.workflow)
        # NOAA-20 is the primary source; the downloader defaults to it.
        self.assertNotIn("--layer", self.workflow)

    def test_mosaic_and_publish_keep_filenames(self):
        self.assertIn("python viirs_nightlights_ingest.py", self.workflow)
        self.assertIn("--tiles-manifest .cache/viirs_gibs/manifest.json", self.workflow)
        self.assertIn("viirs_nightlights_${{ inputs.region }}_browser.json", self.workflow)
        self.assertIn("viirs_nightlights_${{ inputs.region }}_qc.json", self.workflow)

    def test_artifact_keeps_nasa_semantics_and_honest_quality(self):
        self.assertIn('data["source"]=="nasa_gibs_viirs_noaa20_dnb"', self.workflow)
        self.assertIn('"VIIRS_NOAA20_DayNightBand_At_Sensor_Radiance"', self.workflow)
        self.assertIn("cloud contamination", self.workflow)
        self.assertIn("not Bortle class", self.workflow)
        self.assertIn('assert not qcj["flags"], qcj', self.workflow)

    def test_publish_only_runtime_browser_and_qc_files(self):
        self.assertIn("contents: write", self.workflow)
        publish = self.workflow.split("- name: Publish QC-passing VIIRS snapshot", 1)[1]
        self.assertIn("git push origin HEAD:main", publish)
        self.assertNotIn(".cache/viirs_gibs", publish)
        validate = self.workflow.index("- name: Validate artifact semantics")
        publish_index = self.workflow.index("- name: Publish QC-passing VIIRS snapshot")
        self.assertLess(validate, publish_index)


if __name__ == "__main__":
    unittest.main()
