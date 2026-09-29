import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class WeatherGridProductionFreshnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = (
            ROOT / ".github" / "workflows" / "b145_weathergrid_production_smoke.yml"
        ).read_text(encoding="utf-8")

    def test_wait_compares_exact_public_assets(self):
        for path in (
            "weather-map.html",
            "assets/weather-map.js",
            "assets/weather-map.css",
        ):
            self.assertIn(f"sha256sum {path}", self.workflow)

        self.assertIn("live_html_sha", self.workflow)
        self.assertIn("live_js_sha", self.workflow)
        self.assertIn("live_css_sha", self.workflow)
        self.assertIn('"$live_html_sha" == "$expected_html_sha"', self.workflow)
        self.assertIn('"$live_js_sha" == "$expected_js_sha"', self.workflow)
        self.assertIn('"$live_css_sha" == "$expected_css_sha"', self.workflow)

    def test_wait_bypasses_stale_cache(self):
        self.assertIn("Cache-Control: no-cache", self.workflow)
        self.assertIn("pages_probe=${nonce}", self.workflow)
        self.assertIn("${GITHUB_SHA}", self.workflow)

    def test_selenium_runs_only_after_freshness_gate(self):
        fresh = self.workflow.index("Wait for exact GitHub Pages publication")
        browser = self.workflow.index("Run deployed WeatherGrid browser smoke")
        self.assertLess(fresh, browser)


if __name__ == "__main__":
    unittest.main()
