import unittest

from astrophotography_environment import evaluate_astro_environment


class AstrophotographyEnvironmentTest(unittest.TestCase):
    def test_missing_moon_stays_incomplete_even_when_dark_and_clear(self):
        result = evaluate_astro_environment({
            "nighttime_lights_radiance_nw_cm2_sr": 0.3,
            "nighttime_lights_quality_flag": 0,
            "visibility_km": 40,
            "aod_550nm": 0.05,
            "pm2_5_ug_m3": 4,
            "rh": 55,
            "cloud_cover_percent": 5,
        })
        self.assertEqual(result["state"], "incomplete_evidence")
        self.assertIn("moon_geometry", result["missing_evidence"])
        self.assertIn("moon_target_separation", result["missing_evidence"])
        self.assertEqual(result["score_effect"], "none")

    def test_cloud_can_be_a_challenge_without_becoming_score(self):
        result = evaluate_astro_environment({
            "nighttime_lights_radiance_nw_cm2_sr": 0.4,
            "nighttime_lights_quality_flag": 0,
            "visibility_km": 35,
            "aod_550nm": 0.08,
            "pm2_5_ug_m3": 5,
            "rh": 60,
            "cloud_cover_percent": 90,
            "moon_altitude_deg": -12,
            "moon_illumination_fraction": 0.2,
            "moon_target_separation_deg": 120,
        })
        self.assertEqual(result["state"], "challenging_environment")
        self.assertIn("extensive_cloud", result["blockers"])
        self.assertEqual(result["score_effect"], "none")

    def test_complete_favorable_evidence_still_does_not_claim_milky_way(self):
        result = evaluate_astro_environment({
            "nighttime_lights_radiance_nw_cm2_sr": 0.2,
            "nighttime_lights_quality_flag": 0,
            "visibility_km": 45,
            "aod_550nm": 0.04,
            "pm2_5_ug_m3": 3,
            "rh": 50,
            "cloud_cover_percent": 8,
            "moon_altitude_deg": -15,
            "moon_illumination_fraction": 0.1,
            "moon_target_separation_deg": 140,
        })
        self.assertEqual(result["state"], "environment_evidence_favorable")
        self.assertEqual(result["missing_evidence"], [])
        self.assertTrue(result["not_target_visibility_claim"])
        self.assertTrue(result["not_milky_way_visibility_claim"])

    def test_bad_nightlight_quality_is_explicit_missing_evidence(self):
        result = evaluate_astro_environment({
            "nighttime_lights_radiance_nw_cm2_sr": 0.2,
            "nighttime_lights_quality_flag": 255,
            "visibility_km": 30,
            "rh": 65,
            "cloud_cover_percent": 10,
            "moon_altitude_deg": -5,
            "moon_illumination_fraction": 0.3,
            "moon_target_separation_deg": 90,
        })
        self.assertEqual(result["state"], "incomplete_evidence")
        self.assertIn("quality_checked_nighttime_light_radiance", result["missing_evidence"])


if __name__ == "__main__":
    unittest.main()
