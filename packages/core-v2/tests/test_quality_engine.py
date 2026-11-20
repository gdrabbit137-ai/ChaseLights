"""CL-DATA-80: QUALITY engine unit tests (spec §4 trapezoid + tier + s_rank)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import quality_engine  # noqa: E402


class TrapezoidTests(unittest.TestCase):
    def test_spec_example_wind(self):
        # water_reflection wind [0, 0, 0.8, 2.0]
        quad = [0.0, 0.0, 0.8, 2.0]
        self.assertEqual(quality_engine.trapezoid(0.0, quad), 1.0)
        self.assertEqual(quality_engine.trapezoid(0.8, quad), 1.0)
        self.assertAlmostEqual(quality_engine.trapezoid(1.4, quad), 0.5)
        self.assertEqual(quality_engine.trapezoid(2.0, quad), 0.0)

    def test_higher_better_unbounded(self):
        quad = [15.0, 30.0, None, None]
        self.assertEqual(quality_engine.trapezoid(30.0, quad), 1.0)
        self.assertEqual(quality_engine.trapezoid(100.0, quad), 1.0)
        self.assertAlmostEqual(quality_engine.trapezoid(22.5, quad), 0.5)
        self.assertEqual(quality_engine.trapezoid(15.0, quad), 0.0)

    def test_unknown_value(self):
        self.assertIsNone(quality_engine.trapezoid(None, [0, 1, 2, 3]))


class EvaluateHourTests(unittest.TestCase):
    V2 = {"required": [], "quality": [
        {"id": "q1", "metric": "wind_speed_10m", "weight": 3.0,
         "ideal": [0, 0.8], "acceptable": [0.0, 2.0]},
        {"id": "q2", "metric": "cloud_cover_total", "weight": 1.5,
         "ideal": [20, 50], "acceptable": [0.0, 75.0]},
    ]}

    def test_ineligible_zero(self):
        r = quality_engine.evaluate_hour(self.V2, {}, {}, {}, False)
        self.assertEqual((r["eligible"], r["s_quality"], r["tier"]),
                         (False, 0.0, "marginal"))

    def test_no_quality_rules_default_75(self):
        r = quality_engine.evaluate_hour({"required": [], "quality": []},
                                         {}, {}, {}, True)
        self.assertEqual((r["s_quality"], r["tier"]), (75.0, "recommend"))

    def test_full_score_recommend(self):
        values = {"wind_speed_10m": {"state": "AVAILABLE", "value": 0.5},
                  "cloud_cover_total": {"state": "AVAILABLE", "value": 30}}
        r = quality_engine.evaluate_hour(self.V2, {}, values, {}, True)
        self.assertEqual((r["s_quality"], r["tier"]), (100.0, "recommend"))

    def test_mid_score_good(self):
        values = {"wind_speed_10m": {"state": "AVAILABLE", "value": 1.4},
                  "cloud_cover_total": {"state": "AVAILABLE", "value": 62.5}}
        r = quality_engine.evaluate_hour(self.V2, {}, values, {}, True)
        self.assertEqual((r["s_quality"], r["tier"]), (50.0, "good"))

    def test_low_score_marginal(self):
        values = {"wind_speed_10m": {"state": "AVAILABLE", "value": 2.0},
                  "cloud_cover_total": {"state": "AVAILABLE", "value": 75.0}}
        r = quality_engine.evaluate_hour(self.V2, {}, values, {}, True)
        self.assertEqual((r["s_quality"], r["tier"]), (0.0, "marginal"))

    def test_unknown_metric_neutral_not_fail(self):
        values = {"wind_speed_10m": {"state": "MISSING"}}
        r = quality_engine.evaluate_hour(self.V2, {}, values, {}, True)
        self.assertTrue(r.get("quality_unknown"))
        self.assertEqual(r["tier"], "good")  # neutral 0.5 midpoint -> 50

    def test_moon_override(self):
        v2 = {"required": [], "quality": [
            {"id": "m", "metric": "moon_illumination_fraction", "weight": 2.5,
             "ideal": [0, 0.05], "acceptable": [0.0, 0.35]}]}
        astro = {"moon_altitude_deg": -12.0, "moon_illumination_fraction": 0.8}
        r = quality_engine.evaluate_hour(v2, {}, {}, astro, True)
        self.assertEqual(r["s_quality"], 100.0)
        astro_up = {"moon_altitude_deg": 30.0, "moon_illumination_fraction": 0.8}
        r2 = quality_engine.evaluate_hour(v2, {}, {}, astro_up, True)
        self.assertEqual(r2["s_quality"], 0.0)


class SRankTests(unittest.TestCase):
    def test_formula(self):
        # AGLI 66.2, S_quality 100 -> 66.2^0.35 * 100^0.65
        expected = (66.2 ** 0.35) * (100.0 ** 0.65)
        self.assertAlmostEqual(quality_engine.s_rank(66.2, 100.0),
                               round(expected, 1))

    def test_none_agli(self):
        self.assertIsNone(quality_engine.s_rank(None, 90.0))
        self.assertIsNone(quality_engine.s_rank(60.0, None))


if __name__ == "__main__":
    unittest.main()
