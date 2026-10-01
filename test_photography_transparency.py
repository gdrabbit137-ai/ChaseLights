import unittest

from photography_transparency import FORMULA_VERSION, evaluate_transparency


class PhotographyTransparencyTest(unittest.TestCase):
    def test_clear_air_scores_high_diagnostically(self):
        result = evaluate_transparency({
            "visibility_km": 40,
            "aod_550nm": 0.05,
            "pm2_5_ug_m3": 5,
            "rh": 65,
            "temp": 25,
            "dew": 17,
        })
        self.assertTrue(result["available"])
        self.assertGreaterEqual(result["transparency_index"], 85)
        self.assertEqual(result["state"], "very_clear")
        self.assertEqual(result["formula_version"], FORMULA_VERSION)
        self.assertEqual(result["score_effect"], "none")

    def test_aerosol_and_humidity_reduce_transparency(self):
        result = evaluate_transparency({
            "visibility_km": 7,
            "aod_550nm": 0.8,
            "pm2_5_ug_m3": 45,
            "rh": 92,
            "temp": 24,
            "dew": 22.5,
        })
        self.assertTrue(result["available"])
        self.assertLess(result["transparency_index"], 50)

    def test_visibility_is_required(self):
        result = evaluate_transparency({
            "aod_550nm": 0.2,
            "pm2_5_ug_m3": 12,
            "rh": 70,
        })
        self.assertFalse(result["available"])
        self.assertEqual(result["reason"], "visibility_plus_environment_evidence_required")

    def test_partial_environment_evidence_is_low_confidence(self):
        result = evaluate_transparency({
            "visibility_km": 25,
            "aod_550nm": 0.1,
        })
        self.assertTrue(result["available"])
        self.assertEqual(result["confidence"], "low")

    def test_formula_is_explicitly_uncalibrated_and_non_scoring(self):
        result = evaluate_transparency({
            "visibility_km": 20,
            "pm2_5_ug_m3": 15,
            "rh": 80,
        })
        self.assertEqual(result["calibration_status"], "uncalibrated")
        self.assertTrue(result["diagnostic_only"])
        self.assertEqual(result["score_effect"], "none")


if __name__ == "__main__":
    unittest.main()
