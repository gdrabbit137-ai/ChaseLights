import json
import tempfile
import unittest
from datetime import datetime, timezone

from fetch_data import _build_photography_environment_diagnostic, _sample_viirs_environment_for_location
from viirs_nightlights_weathergrid import build_bundle


class AstroForecastReplayWiringTest(unittest.TestCase):
    def test_timestamp_environment_contains_replayable_astro_diagnostic(self):
        item = {
            "vis": 40000,
            "rh": 55,
            "temp": 20,
            "dew": 12,
            "c_low": 5,
            "c_mid": 8,
            "c_high": 12,
            "cloud_cover": 12,
            "aod_550nm": 0.05,
            "pm2_5_ug_m3": 4,
            # VIIRS is intentionally absent until static spatial sampling is wired.
        }
        result = _build_photography_environment_diagnostic(
            item,
            datetime(2026, 9, 28, 12, tzinfo=timezone.utc),
            24.18,
            121.31,
        )
        astro = result["astrophotography"]
        self.assertEqual(astro["moon"]["source"], "b171b_lunar_ephemeris")
        self.assertNotIn("moon_geometry", astro["missing_evidence"])
        self.assertNotIn("moon_target_separation", astro["missing_evidence"])
        self.assertIn("quality_checked_nighttime_light_radiance", astro["missing_evidence"])
        self.assertEqual(astro["score_effect"], "none")

    def test_no_coordinates_fails_incomplete_instead_of_guessing(self):
        result = _build_photography_environment_diagnostic({
            "vis": 30000, "rh": 60, "c_low": 10, "c_mid": 10, "c_high": 10,
        })
        astro = result["astrophotography"]
        self.assertEqual(astro["state"], "incomplete_evidence")
        self.assertIn("moon_geometry", astro["missing_evidence"])
        self.assertEqual(astro["score_effect"], "none")


    def test_published_viirs_artifact_removes_light_radiance_missing_evidence(self):
        bundle, qc = build_bundle(
            [25.0, 24.0],
            [121.0, 122.0],
            [0.4, 2.0, 8.0, 12.0],
            [0, 1, 2, 0],
            2025,
        )
        with tempfile.TemporaryDirectory() as tmp:
            browser = tmp + "/browser.json"
            qc_path = tmp + "/qc.json"
            with open(browser, "w", encoding="utf-8") as handle:
                json.dump(bundle, handle)
            with open(qc_path, "w", encoding="utf-8") as handle:
                json.dump(qc, handle)
            sample = _sample_viirs_environment_for_location(
                24.96, 121.04, browser_path=browser, qc_path=qc_path
            )

        item = {
            "vis": 40000, "rh": 55, "temp": 20, "dew": 12,
            "c_low": 5, "c_mid": 8, "c_high": 12, "cloud_cover": 12,
            **sample,
        }
        result = _build_photography_environment_diagnostic(
            item, datetime(2026, 9, 28, 12, tzinfo=timezone.utc), 24.96, 121.04
        )
        astro = result["astrophotography"]
        self.assertNotIn("quality_checked_nighttime_light_radiance", astro["missing_evidence"])
        self.assertEqual(astro["dark_sky_evidence"]["quality"], "good")
        self.assertEqual(astro["score_effect"], "none")

    def test_missing_viirs_artifact_fails_closed(self):
        sample = _sample_viirs_environment_for_location(
            24.96, 121.04, browser_path="/missing/browser.json", qc_path="/missing/qc.json"
        )
        self.assertIsNone(sample)


if __name__ == "__main__":
    unittest.main()
