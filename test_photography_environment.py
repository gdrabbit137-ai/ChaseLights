import unittest

from photography_environment import classify_dark_sky_evidence, classify_fog_haze


class FogHazeEnvironmentTest(unittest.TestCase):
    def test_saturated_low_visibility_supports_fog(self):
        result = classify_fog_haze({
            "vis": 1800, "rh": 97, "temp": 22.0, "dew": 21.5,
            "c_low": 85, "weather_code": 45, "aod_550nm": 0.12,
            "pm2_5_ug_m3": 8,
        })
        self.assertEqual(result["state"], "fog_supported")
        self.assertTrue(result["fog_support"])
        self.assertFalse(result["aerosol_support"])

    def test_low_visibility_plus_aerosol_supports_haze_without_saturation(self):
        result = classify_fog_haze({
            "vis": 4200, "rh": 67, "temp": 29.0, "dew": 21.0,
            "c_low": 12, "weather_code": 1, "aod_550nm": 0.65,
            "pm2_5_ug_m3": 31,
        })
        self.assertEqual(result["state"], "haze_supported")
        self.assertFalse(result["fog_support"])
        self.assertTrue(result["aerosol_support"])

    def test_overlap_is_mixed_not_forced_to_fog_or_haze(self):
        result = classify_fog_haze({
            "vis": 2400, "rh": 98, "temp": 21.0, "dew": 20.5,
            "c_low": 90, "weather_code": 45, "aod_550nm": 0.9,
            "pm2_5_ug_m3": 42,
        })
        self.assertEqual(result["state"], "mixed_fog_haze")
        self.assertTrue(result["diagnostic_only"])
        self.assertEqual(result["score_effect"], "none")

    def test_aerosol_alone_does_not_claim_haze_visibility_degradation(self):
        result = classify_fog_haze({
            "vis": 24000, "rh": 60, "aod_550nm": 0.7, "pm2_5_ug_m3": 30,
        })
        self.assertEqual(result["state"], "aerosol_present_visibility_not_degraded")

    def test_low_visibility_without_cause_stays_unresolved(self):
        result = classify_fog_haze({
            "vis": 3000, "rh": 70, "c_low": 20, "aod_550nm": 0.1,
            "pm2_5_ug_m3": 6,
        })
        self.assertEqual(result["state"], "low_visibility_unresolved")

    def test_missing_visibility_does_not_turn_aod_into_haze_claim(self):
        result = classify_fog_haze({"aod_550nm": 0.8, "pm2_5_ug_m3": 40})
        self.assertEqual(result["state"], "aerosol_present_visibility_not_degraded")
        self.assertIsNone(result["visibility_km"])


class DarkSkyEnvironmentTest(unittest.TestCase):
    def test_low_radiance_is_context_not_bortle(self):
        result = classify_dark_sky_evidence({
            "nighttime_lights_radiance_nw_cm2_sr": 0.4,
            "nighttime_lights_quality_flag": 0,
        })
        self.assertEqual(result["state"], "low_artificial_light_radiance")
        self.assertEqual(result["confidence"], "medium")
        self.assertTrue(result["not_bortle"])
        self.assertTrue(result["not_sqm"])
        self.assertTrue(result["not_sky_brightness"])
        self.assertEqual(result["score_effect"], "none")

    def test_radiance_bins_remain_evidence_only(self):
        self.assertEqual(
            classify_dark_sky_evidence({
                "nighttime_lights_radiance_nw_cm2_sr": 3,
                "nighttime_lights_quality_flag": 0,
            })["state"],
            "moderate_artificial_light_radiance",
        )
        self.assertEqual(
            classify_dark_sky_evidence({
                "nighttime_lights_radiance_nw_cm2_sr": 7,
                "nighttime_lights_quality_flag": 0,
            })["state"],
            "elevated_artificial_light_radiance",
        )
        self.assertEqual(
            classify_dark_sky_evidence({
                "nighttime_lights_radiance_nw_cm2_sr": 18,
                "nighttime_lights_quality_flag": 0,
            })["state"],
            "high_artificial_light_radiance",
        )

    def test_poor_or_gap_filled_quality_caps_confidence(self):
        poor = classify_dark_sky_evidence({
            "nighttime_lights_radiance_nw_cm2_sr": 0.5,
            "nighttime_lights_quality_flag": 1,
        })
        gap = classify_dark_sky_evidence({
            "nighttime_lights_radiance_nw_cm2_sr": 0.5,
            "nighttime_lights_quality_flag": 2,
        })
        self.assertEqual(poor["quality"], "poor")
        self.assertEqual(gap["quality"], "gap_filled")
        self.assertEqual(poor["confidence"], "low")
        self.assertEqual(gap["confidence"], "low")

    def test_missing_quality_does_not_invent_trust(self):
        result = classify_dark_sky_evidence({
            "nighttime_lights_radiance_nw_cm2_sr": 0.3,
        })
        self.assertEqual(result["quality"], "unknown")
        self.assertFalse(result["usable_for_context"])
        self.assertEqual(result["confidence"], "low")

    def test_missing_radiance_is_unavailable(self):
        result = classify_dark_sky_evidence({
            "nighttime_lights_quality_flag": 0,
        })
        self.assertEqual(result["state"], "night_lights_unavailable")
        self.assertFalse(result["available"])
        self.assertEqual(result["score_effect"], "none")


if __name__ == "__main__":
    unittest.main()
