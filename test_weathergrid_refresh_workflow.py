import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WORKFLOW = ROOT / ".github" / "workflows" / "update_weathergrid.yml"


class WeatherGridRefreshWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_schedule_tracks_four_gfs_cycles_daily(self):
        self.assertIn("cron: '20 5,11,17,23 * * *'", self.text)
        self.assertIn("chaselights-weathergrid-publish", self.text)
        self.assertIn("cancel-in-progress: true", self.text)

    def test_default_publish_horizon_is_twelve_hours(self):
        self.assertIn('default: "0,3,6,9,12"', self.text)
        self.assertIn("inputs.forecast_hours || '0,3,6,9,12'", self.text)
        self.assertIn("--coverage-scope region", self.text)

    def test_publication_contains_only_compact_browser_outputs(self):
        for path in (
            "weathergrid/gfs_tw_weather_browser.json",
            "weathergrid/gfs_tw_weather_qc.json",
            "weathergrid/weathergrid_coverage_browser.json",
        ):
            self.assertIn(path, self.text)
        publish_block = self.text.split("- name: Publish compact live snapshot", 1)[1]
        self.assertNotIn("git add gfs_multilayer_output", publish_block)
        self.assertNotIn("*.grib2", publish_block)
        self.assertNotIn("*.png", publish_block)

    def test_publish_validation_keeps_known_complete_places(self):
        self.assertIn('("tw-073", "tw-075")', self.text)
        self.assertIn('["all_topics_complete"] is True', self.text)

    def test_artifact_is_short_lived(self):
        self.assertIn("retention-days: 7", self.text)


    def test_jma_msm_refresh_is_optional_and_stale_safe(self):
        self.assertIn("id: jma_msm", self.text)
        self.assertIn("jma_msm_cloud_poc.py", self.text)
        self.assertIn("jma_msm_weathergrid_browser_bundle.py", self.text)
        self.assertIn("--forecast-hours 40", self.text)
        self.assertIn("--batch-size 160", self.text)
        self.assertIn(
            "weathergrid/jma_msm_tw_cloud_browser.json",
            self.text,
        )
        self.assertIn(
            "rm -f weathergrid/jma_msm_tw_cloud_browser.json "
            "weathergrid/jma_msm_tw_cloud_qc.json",
            self.text,
        )
        self.assertIn('"jma_msm": jma_summary', self.text)


if __name__ == "__main__":
    unittest.main()
