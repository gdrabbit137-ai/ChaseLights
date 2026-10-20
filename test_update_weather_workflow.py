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
        self.assertIn('publisher.py publish --producer weather', self.text)
        self.assertNotIn('git push', self.text)
        publisher = (ROOT / 'ops/v2/data_publish/publisher.py').read_text()
        self.assertIn('for attempt in range(5):', publisher)
        self.assertIn('Main publication rejected after five bounded attempts', publisher)
        self.assertNotIn('--force', publisher)



if __name__ == "__main__":
    unittest.main()
