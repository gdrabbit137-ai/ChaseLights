import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WORKFLOW = ROOT / ".github" / "workflows" / "update_weather.yml"


class WeatherRefreshPublishWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_schedule_and_write_permission_remain_production_contract(self):
        self.assertIn("cron: '0 */3 * * *'", self.text)
        self.assertIn("contents: write", self.text)

    def test_publish_retry_fails_closed_after_five_attempts(self):
        self.assertIn("pushed=false", self.text)
        self.assertIn("for i in {1..5}; do", self.text)
        self.assertIn("if git pull --rebase && git push; then", self.text)
        self.assertIn("pushed=true", self.text)
        self.assertIn(
            'echo "::error::Failed to publish refreshed weather data after 5 attempts."',
            self.text,
        )
        self.assertIn("exit 1", self.text)
        self.assertNotIn(
            "git pull --rebase && git push && break || sleep 5",
            self.text,
        )


if __name__ == "__main__":
    unittest.main()
