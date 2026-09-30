import unittest
from pathlib import Path


class Himawari9RefreshWorkflowTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = Path(
            ".github/workflows/update_himawari9_weathergrid.yml"
        ).read_text(encoding="utf-8")

    def test_schedule_is_ten_minute_poll(self):
        self.assertIn("cron: '*/10 * * * *'", self.workflow)

    def test_workflow_builds_and_publishes_both_files(self):
        self.assertIn("himawari9_weathergrid_browser_bundle.py", self.workflow)
        self.assertIn(
            "weathergrid/himawari9_tw_cloud_browser.json",
            self.workflow,
        )
        self.assertIn(
            "weathergrid/himawari9_tw_cloud_qc.json",
            self.workflow,
        )

    def test_observation_freshness_is_guarded(self):
        self.assertIn("age_minutes <= 90", self.workflow)
        self.assertIn("stale files were removed", self.workflow)

    def test_workflow_does_not_need_secret_api_key(self):
        forbidden = (
            "OPEN_METEO_API_KEY",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
        )
        for name in forbidden:
            self.assertNotIn(name, self.workflow)


if __name__ == "__main__":
    unittest.main()
