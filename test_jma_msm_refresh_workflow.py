import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
JMA_WORKFLOW = ROOT / ".github" / "workflows" / "update_jma_msm_weathergrid.yml"
SHARED_WORKFLOW = ROOT / ".github" / "workflows" / "update_weathergrid.yml"


class JmaMsmRefreshWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.text = JMA_WORKFLOW.read_text(encoding="utf-8")
        self.shared = SHARED_WORKFLOW.read_text(encoding="utf-8")

    def test_jma_owns_three_hour_refresh_cadence(self):
        self.assertIn("cron: '10 */3 * * *'", self.text)
        self.assertIn("chaselights-jma-msm-publish", self.text)
        self.assertIn("cancel-in-progress: true", self.text)
        self.assertIn("update_interval_hours", self.text)
        self.assertNotIn("jma_msm_cloud_poc.py", self.shared)
        self.assertNotIn("jma_msm_weathergrid_browser_bundle.py", self.shared)

    def test_publish_window_preserves_hourly_msm_strength(self):
        self.assertIn('default: "40"', self.text)
        self.assertIn("inputs.forecast_hours || '40'", self.text)
        self.assertIn("--batch-size 100", self.text)
        self.assertIn('"native_time_interval_hours") == 1', self.text)
        self.assertIn('"update_interval_hours") == 3', self.text)

    def test_jma_keeps_provider_owned_boundary_and_cloud_fields(self):
        for token in (
            '"leftlon": 120.0625',
            '"rightlon": 122.5',
            '"bottomlat": 22.45',
            '"toplat": 25.6',
            '"total_cloud_percent"',
            '"low_cloud_percent"',
            '"mid_cloud_percent"',
            '"high_cloud_percent"',
            '"vertical_definition"',
        ):
            self.assertIn(token, self.text)

    def test_timeline_does_not_pretend_api_index_is_model_lead(self):
        self.assertIn(
            "hours_from_first_published_valid_time_not_model_cycle",
            self.text,
        )
        self.assertIn('"cycle_timestamp_available") is False', self.text)

    def test_failed_refresh_removes_stale_jma_files_and_surfaces_failure(self):
        self.assertIn("continue-on-error: true", self.text)
        self.assertIn(
            "rm -f weathergrid/jma_msm_tw_cloud_browser.json "
            "weathergrid/jma_msm_tw_cloud_qc.json",
            self.text,
        )
        self.assertIn("Fail if JMA refresh failed", self.text)
        self.assertIn("exit 1", self.text)

    def test_only_compact_jma_outputs_are_committed(self):
        publish = self.text.split(
            "- name: Publish current JMA MSM snapshot state", 1
        )[1]
        self.assertIn("weathergrid/jma_msm_tw_cloud_browser.json", publish)
        self.assertIn("weathergrid/jma_msm_tw_cloud_qc.json", publish)
        self.assertNotIn("jma_msm_tw_cloud_raw.json", publish)
        self.assertNotIn("*.grib2", publish)
        self.assertNotIn("*.png", publish)


if __name__ == "__main__":
    unittest.main()
