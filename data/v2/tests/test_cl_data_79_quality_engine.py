"""CL-DATA-79 Phase 2 — spec-quality-engine.md §3/§4/§5 implementation tests.

Localized re-implementation of the Gemini prototype's cases
(D:/ChaseLightsWorkspace/tmp/spec-quality-engine-prototype-gemini.py):
trapezoid abcd boundary points, moon-below-horizon override, empty-quality
default 75, gatekeeper rejection + tiers, nested any_of/all_of, plus the 10
genre quality-configs (§5 weights/abcd, §1 gates) loaded from
data/v2/templates/quality-configs/ and an end-to-end trial: paste a
quality-config onto a contract-like snapshot and check the grade is sane.
All offline: no network calls.
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "quality_engine", ROOT / "packages/core-v2/tools/quality_engine.py")
qe = importlib.util.module_from_spec(spec)
sys.modules["quality_engine"] = qe
spec.loader.exec_module(qe)

CONFIGS = qe.load_quality_config_dir(ROOT / "data/v2/templates/quality-configs")
DAY = date(2026, 11, 20)


class TrapezoidBoundaryTests(unittest.TestCase):
    """§4.2 five-segment formula at a/b/c/d four boundary points."""

    def test_generic_trapezoid(self):
        m = qe.trapezoid_membership
        a, b, c, d = 10.0, 20.0, 50.0, 70.0
        self.assertEqual(m(5, a, b, c, d), 0.0)
        self.assertEqual(m(10, a, b, c, d), 0.0)          # a
        self.assertAlmostEqual(m(15, a, b, c, d), 0.5)    # rising mid
        self.assertEqual(m(20, a, b, c, d), 1.0)          # b
        self.assertEqual(m(35, a, b, c, d), 1.0)
        self.assertEqual(m(50, a, b, c, d), 1.0)          # c
        self.assertAlmostEqual(m(60, a, b, c, d), 0.5)    # falling mid
        self.assertEqual(m(70, a, b, c, d), 0.0)          # d
        self.assertEqual(m(80, a, b, c, d), 0.0)

    def test_left_shoulder(self):
        m = qe.trapezoid_membership
        self.assertEqual(m(0.0, 0, 0, 0.8, 2.0), 1.0)     # a==b still ideal
        self.assertEqual(m(0.8, 0, 0, 0.8, 2.0), 1.0)     # c
        self.assertAlmostEqual(m(1.4, 0, 0, 0.8, 2.0), 0.5)
        self.assertEqual(m(2.0, 0, 0, 0.8, 2.0), 0.0)     # d

    def test_right_shoulder_inf(self):
        m = qe.trapezoid_membership
        self.assertEqual(m(15.0, 15, 30, math.inf, math.inf), 0.0)   # a
        self.assertAlmostEqual(m(22.5, 15, 30, math.inf, math.inf), 0.5)
        self.assertEqual(m(30.0, 15, 30, math.inf, math.inf), 1.0)   # b
        self.assertEqual(m(99.0, 15, 30, math.inf, math.inf), 1.0)

    def test_invalid_abcd_raises(self):
        with self.assertRaises(ValueError):
            qe.trapezoid_membership(1, 5, 3, 2, 1)

    def test_normalize_abcd_split_form_and_inf_strings(self):
        a, b, c, d = qe.normalize_abcd({"ideal": [30, None], "acceptable": [15, "inf"]})
        self.assertEqual((a, b), (15.0, 30.0))
        self.assertEqual(c, math.inf)
        self.assertEqual(d, math.inf)


class Default75Tests(unittest.TestCase):
    """§4.3: G(t)=1 with no quality rules -> S_quality=75.0 / recommend."""

    def test_empty_quality_defaults_to_75(self):
        rule = {
            "opportunity_id": "tw-001-P01", "place_id": "tw-001", "tag": "scenic_lookout",
            "windows": {"time_of_day": ["civil_daylight"],
                        "seasonal": [{"start": "12-15", "end": "02-25"}]},
            "conditions": {"required": [{"metric": "precipitation", "op": "lt", "value": 0.2}],
                           "quality": []},
        }
        res = qe.score_opportunity(rule, {"precipitation": 0.0},
                                   {"civil_daylight"}, date(2026, 1, 15), agli_score=80.0)
        self.assertTrue(res.eligible)
        self.assertEqual(res.s_quality, 75.0)
        self.assertEqual(res.tier, "recommend")
        self.assertAlmostEqual(res.s_rank, round(80.0 ** 0.35 * 75.0 ** 0.65, 2))

    def test_cross_year_seasonal_open_and_closed(self):
        rule = {
            "opportunity_id": "x", "place_id": "p", "tag": "seasonal_foliage",
            "windows": {"time_of_day": [], "seasonal": [{"start": "12-15", "end": "02-25"}]},
            "conditions": {"required": [], "quality": []},
        }
        ok = qe.evaluate_gatekeeper(rule, {}, set(), date(2026, 1, 15))
        bad = qe.evaluate_gatekeeper(rule, {}, set(), date(2026, 7, 1))
        self.assertTrue(ok[0])
        self.assertFalse(bad[0])
        self.assertIn("seasonal_closed:2026-07-01", bad[1])


class MoonOverrideTests(unittest.TestCase):
    """§4.2 月光覆寫 + §1.2 any_of moonlight dual-track gate."""

    ASTRO = {  # the landed quality-config instantiated for an opportunity
        "opportunity_id": "jp-021-P02", "place_id": "jp-021", "tag": "astrophotography",
        "windows": {"time_of_day": ["astronomical_darkness"], "seasonal": None},
        "conditions": json.loads((ROOT / "data/v2/templates/quality-configs/"
                                  "astrophotography.json").read_text(encoding="utf-8"))["conditions"],
    }

    def score(self, metrics):
        return qe.score_opportunity(self.ASTRO, metrics, {"astronomical_darkness"}, DAY)

    def test_moon_below_horizon_overrides_illumination(self):
        res = self.score({"cloud_cover": 0.0, "moon_altitude_deg": -12.0,
                          "moon_illumination": 0.98, "moon_target_separation_deg": 10.0,
                          "galactic_core_altitude_deg": 30.0, "aerosol_optical_depth": 0.0})
        self.assertTrue(res.eligible)  # any_of leg 1: moon below horizon
        moon = next(b for b in res.breakdown if b.metric == "moon_illumination")
        self.assertTrue(moon.overridden)
        self.assertEqual(moon.membership_q, 1.0)
        self.assertEqual(res.s_quality, 100.0)
        self.assertEqual(res.tier, "recommend")

    def test_moon_above_horizon_dim_and_far_passes_gate_no_override(self):
        res = self.score({"cloud_cover": 0.0, "moon_altitude_deg": 25.0,
                          "moon_illumination": 0.20, "moon_target_separation_deg": 60.0,
                          "galactic_core_altitude_deg": 30.0, "aerosol_optical_depth": 0.0})
        self.assertTrue(res.eligible)  # any_of leg 2: illum<=0.25 AND sep>=45
        moon = next(b for b in res.breakdown if b.metric == "moon_illumination")
        self.assertFalse(moon.overridden)
        self.assertAlmostEqual(moon.membership_q, 0.5)  # 0.20 is mid of [0.05, 0.35]
        expected = round(100.0 * (3.0 * 1.0 + 2.5 * 0.5 + 1.5 * 1.0 + 1.5 * 1.0) / 8.5, 2)
        self.assertAlmostEqual(res.s_quality, expected)

    def test_bright_moon_close_to_target_fails_gate(self):
        res = self.score({"cloud_cover": 0.0, "moon_altitude_deg": 40.0,
                          "moon_illumination": 0.9, "moon_target_separation_deg": 20.0,
                          "galactic_core_altitude_deg": 30.0, "aerosol_optical_depth": 0.0})
        self.assertFalse(res.eligible)
        self.assertEqual(res.s_quality, 0.0)
        self.assertEqual(res.tier, "ineligible")
        self.assertTrue(any("any_of_failed" in r for r in res.failed_reasons))

    def test_moon_gate_missing_metric_fails_closed(self):
        res = self.score({"cloud_cover": 0.0})
        self.assertFalse(res.eligible)
        self.assertTrue(any(r.startswith("missing_metric") or "any_of_failed" in r
                            for r in res.failed_reasons))


class GatekeeperAndTierTests(unittest.TestCase):
    """G(t) rejection -> eligible=False + S=0; marginal/good/recommend tiers."""

    def test_gatekeeper_rejection_and_marginal(self):
        rule = {
            "opportunity_id": "jp-010-P02", "place_id": "jp-010", "tag": "water_reflection",
            "windows": {"time_of_day": ["civil_daylight"], "seasonal": None},
            "conditions": {"required": [{"metric": "wind_speed_10m", "op": "lte", "value": 2.0}],
                           "quality": [{"metric": "wind_speed_10m", "weight": 3.0,
                                        "abcd": [0, 0, 0.8, 2.0]}]},
        }
        res = qe.score_opportunity(rule, {"wind_speed_10m": 1.7}, {"civil_daylight"}, DAY)
        self.assertTrue(res.eligible)
        self.assertEqual(res.s_quality, 25.0)   # q = (2.0-1.7)/1.2 = 0.25
        self.assertEqual(res.tier, "marginal")

        res_fail = qe.score_opportunity(rule, {"wind_speed_10m": 2.5}, {"civil_daylight"}, DAY)
        self.assertFalse(res_fail.eligible)
        self.assertEqual(res_fail.s_quality, 0.0)
        self.assertEqual(res_fail.tier, "ineligible")

    def test_time_of_day_window_gate(self):
        rule = {
            "opportunity_id": "x", "place_id": "p", "tag": "golden_hour",
            "windows": {"time_of_day": ["golden_hour"], "seasonal": None},
            "conditions": {"required": [], "quality": []},
        }
        ok = qe.evaluate_gatekeeper(rule, {}, {"golden_hour"}, DAY)
        bad = qe.evaluate_gatekeeper(rule, {}, {"civil_daylight"}, DAY)
        self.assertTrue(ok[0])
        self.assertFalse(bad[0])
        self.assertIn("time_of_day_mismatch", bad[1][0])

    def test_tier_boundaries(self):
        self.assertEqual(qe.classify_tier(75.0, True), "recommend")
        self.assertEqual(qe.classify_tier(74.99, True), "good")
        self.assertEqual(qe.classify_tier(45.0, True), "good")
        self.assertEqual(qe.classify_tier(44.99, True), "marginal")
        self.assertEqual(qe.classify_tier(100.0, False), "ineligible")

    def test_nested_all_of_inside_any_of(self):
        rule = {
            "opportunity_id": "x", "place_id": "p", "tag": "t",
            "windows": {"time_of_day": [], "seasonal": None},
            "conditions": {"required": [{"any_of": [
                {"metric": "a", "op": "gte", "value": 1},
                {"all_of": [{"metric": "b", "op": "gte", "value": 1},
                            {"metric": "c", "op": "gte", "value": 1}]}]}],
                "quality": []},
        }
        self.assertTrue(qe.evaluate_gatekeeper(rule, {"b": 2, "c": 2}, set(), DAY)[0])
        self.assertFalse(qe.evaluate_gatekeeper(rule, {"b": 2}, set(), DAY)[0])


class GenreConfigTests(unittest.TestCase):
    """§5: all 10 genre configs load, weights/abcd match the spec table,
    and §1 gate corrections are present."""

    def test_ten_genres_loaded_with_unique_tags(self):
        expected = {"water_reflection", "mountain_vista", "sunrise_sunset", "golden_hour",
                    "city_night", "astrophotography", "seasonal_foliage", "snow_ice",
                    "overcast_soft_light", "scenic_lookout"}
        self.assertEqual(set(CONFIGS), expected)

    def test_required_key_validation(self):
        for tag, cfg in CONFIGS.items():
            instance = dict(cfg)
            instance["opportunity_id"] = f"validate-{tag}"
            instance["place_id"] = "validate-place"
            rules = qe.load_quality_rules(instance)  # raises on missing keys
            self.assertEqual(rules[0]["tag"], tag)

    def test_spec_section5_weights_and_abcd(self):
        spec_table = {
            "water_reflection": {"wind_speed_10m": (3.0, [0, 0, 0.8, 2.0]),
                                 "golden_hour_match": (2.0, [0, 1, 1, 1]),
                                 "cloud_cover": (1.5, [0, 20, 50, 75])},
            "mountain_vista": {"cloud_cover_mid": (2.0, [0, 20, 50, 75]),
                               "visibility_km": (2.0, [15, 30, "inf", "inf"]),
                               "golden_hour_match": (1.5, [0, 1, 1, 1]),
                               "aerosol_optical_depth": (1.0, [0, 0, 0.15, 0.5])},
            "sunrise_sunset": {"cloud_cover_mid_high": (3.0, [5, 25, 65, 85]),
                               "cloud_cover_low": (2.5, [0, 0, 10, 35]),
                               "aerosol_optical_depth": (1.0, [0, 0.05, 0.25, 0.6])},
            "golden_hour": {"cloud_cover_low": (2.5, [0, 0, 15, 40]),
                            "cloud_cover_mid_high": (1.5, [0, 15, 45, 70]),
                            "aerosol_optical_depth": (1.5, [0, 0, 0.2, 0.5])},
            "city_night": {"blue_hour_match": (2.5, [0, 1, 1, 1]),
                           "visibility_km": (2.0, [10, 25, "inf", "inf"]),
                           "aerosol_optical_depth": (1.5, [0, 0, 0.15, 0.5]),
                           "wind_speed_10m": (2.0, [0, 0, 1.0, 2.5])},
            "astrophotography": {"cloud_cover": (3.0, [0, 0, 5, 20]),
                                 "moon_illumination": (2.5, [0, 0, 0.05, 0.35]),
                                 "galactic_core_altitude_deg": (1.5, [0, 25, "inf", "inf"]),
                                 "aerosol_optical_depth": (1.5, [0, 0, 0.1, 0.3])},
            "seasonal_foliage": {"cloud_cover": (2.0, [10, 40, 75, 95]),
                                 "wind_speed_10m": (2.0, [0, 0, 1.5, 5.0]),
                                 "golden_hour_match": (1.5, [0, 1, 1, 1])},
            "snow_ice": {"snow_depth_cm": (3.0, [2, 15, "inf", "inf"]),
                         "wind_speed_10m": (2.0, [0, 0, 2.5, 7.0]),
                         "golden_hour_match": (1.5, [0, 1, 1, 1])},
            "overcast_soft_light": {"cloud_cover": (3.0, [70, 85, 100, 100]),
                                    "wind_speed_10m": (2.0, [0, 0, 1.5, 4.5]),
                                    "precipitation": (1.5, [0, 0, 0.1, 0.5])},
            "scenic_lookout": {"visibility_km": (3.0, [15, 35, "inf", "inf"]),
                               "aerosol_optical_depth": (2.0, [0, 0, 0.12, 0.4]),
                               "cloud_cover_low": (1.5, [0, 0, 10, 30])},
        }
        for tag, metrics in spec_table.items():
            quality = {q["metric"]: q for q in CONFIGS[tag]["conditions"]["quality"]}
            self.assertEqual(set(quality), set(metrics), tag)
            for metric, (weight, abcd) in metrics.items():
                self.assertEqual(quality[metric]["weight"], weight, f"{tag}/{metric}")
                self.assertEqual(quality[metric]["abcd"], abcd, f"{tag}/{metric}")

    def test_spec_section1_gate_corrections(self):
        # §1.1 mountain_vista: mid-cloud cap REMOVED (bonus only), visibility+low-cloud required
        reqs = CONFIGS["mountain_vista"]["conditions"]["required"]
        req_metrics = {n["metric"] for n in reqs if "metric" in n}
        self.assertEqual(req_metrics, {"visibility_km", "cloud_cover_low"})
        self.assertNotIn("cloud_cover_mid", req_metrics)
        # §1.2 astrophotography: moonlight any_of gate, no galactic_core hard gate
        reqs = CONFIGS["astrophotography"]["conditions"]["required"]
        any_of = next(n for n in reqs if "any_of" in n)
        leg_metrics = {leg["metric"] for leg in any_of["any_of"]
                       if "metric" in leg} | {c["metric"] for leg in any_of["any_of"]
                                              for c in leg.get("all_of", [])}
        self.assertEqual(leg_metrics, {"moon_altitude_deg", "moon_illumination",
                                       "moon_target_separation_deg"})
        self.assertNotIn("galactic_core_altitude_deg",
                         {n["metric"] for n in reqs if "metric" in n})
        # §1.3 golden_hour: window is required + low cloud cap
        gh = CONFIGS["golden_hour"]["conditions"]["required"]
        self.assertIn({"metric": "golden_hour_match", "op": "eq", "value": 1}, gh)
        # §1.3 snow_ice: snow present + rain excluded + wind<=7
        snow_reqs = CONFIGS["snow_ice"]["conditions"]["required"]
        self.assertTrue(any("any_of" in n for n in snow_reqs))
        flat = [n for n in snow_reqs if "metric" in n]
        self.assertIn({"metric": "precipitation", "op": "lt", "value": 0.2}, flat)
        self.assertIn({"metric": "wind_speed_10m", "op": "lte", "value": 7.0}, flat)
        # owner 雲量_min ruling: overcast needs cloud PRESENT (>=70% gate)
        self.assertIn({"metric": "cloud_cover", "op": "gte", "value": 70},
                      CONFIGS["overcast_soft_light"]["conditions"]["required"])


class EndToEndContractTrialTests(unittest.TestCase):
    """試算：把 quality-config 貼到契約式（place+window+metrics）快照上，
    分級必須落在攝影常理範圍（窗口外必被擋；好條件 recommend、爛條件 marginal）。"""

    def _tag_score(self, tag, metrics, windows, seasonal=None):
        cfg = json.loads(json.dumps(CONFIGS[tag]))
        cfg["opportunity_id"] = "trial"
        cfg["place_id"] = "trial-place"
        if seasonal is not None:
            cfg["windows"]["seasonal"] = seasonal
        return qe.score_opportunity(cfg, metrics, set(windows), DAY)

    def test_water_reflection_good_morning(self):
        res = self._tag_score("water_reflection",
                              {"wind_speed_10m": 0.5, "precipitation": 0.0,
                               "cloud_cover": 35.0},
                              ["civil_daylight", "golden_hour"])
        self.assertTrue(res.eligible)
        self.assertEqual(res.tier, "recommend")  # calm wind + clouds in window

    def test_water_reflection_windy_noon(self):
        res = self._tag_score("water_reflection",
                              {"wind_speed_10m": 2.5, "precipitation": 0.0,
                               "cloud_cover": 35.0},
                              ["civil_daylight"])
        self.assertFalse(res.eligible)  # wind gate fails

    def test_sunrise_sunset_clear_sky_is_marginal_not_recommend(self):
        res = self._tag_score("sunrise_sunset",
                              {"cloud_cover_mid_high": 0.0, "cloud_cover_low": 0.0,
                               "aerosol_optical_depth": 0.0},
                              ["sunrise"])
        self.assertTrue(res.eligible)
        self.assertEqual(res.tier, "marginal")  # cloudless sunrise = no colour

    def test_golden_hour_noon_is_ineligible(self):
        res = self._tag_score("golden_hour",
                              {"golden_hour_match": 0.0, "cloud_cover_low": 10.0,
                               "cloud_cover_mid_high": 30.0, "aerosol_optical_depth": 0.1},
                              ["civil_daylight"])
        self.assertFalse(res.eligible)  # §1.3: golden window required

    def test_astrophotography_full_moon_high_is_ineligible_winter_dark_ok(self):
        bad = self._tag_score("astrophotography",
                              {"cloud_cover": 10.0, "moon_altitude_deg": 50.0,
                               "moon_illumination": 0.95, "moon_target_separation_deg": 15.0,
                               "galactic_core_altitude_deg": 0.0,
                               "aerosol_optical_depth": 0.05},
                              ["astronomical_darkness"])
        self.assertFalse(bad.eligible)  # bright moon near target vetoes
        good = self._tag_score("astrophotography",
                               {"cloud_cover": 3.0, "moon_altitude_deg": -30.0,
                                "moon_illumination": 0.95, "moon_target_separation_deg": 15.0,
                                "galactic_core_altitude_deg": 0.0,  # winter: core below horizon
                                "aerosol_optical_depth": 0.05},
                               ["astronomical_darkness"])
        self.assertTrue(good.eligible)
        self.assertEqual(good.tier, "recommend")  # galactic_core is bonus-only (§1.2)

    def test_snow_ice_bare_ground_is_ineligible(self):
        res = self._tag_score("snow_ice",
                              {"snow_depth_cm": 0.0, "snowfall_cm_h": 0.0,
                               "precipitation": 0.0, "wind_speed_10m": 1.0},
                              ["civil_daylight"])
        self.assertFalse(res.eligible)  # §1.3: snow must be present

    def test_seasonal_foliage_out_of_season_ineligible(self):
        summer_cfg = json.loads(json.dumps(CONFIGS["seasonal_foliage"]))
        summer_cfg["opportunity_id"] = "trial"
        summer_cfg["place_id"] = "trial-place"
        summer_cfg["windows"]["seasonal"] = [{"start": "10-15", "end": "12-05"}]
        # patch gate date by scoring with a July snapshot via score_opportunity
        res2 = qe.score_opportunity(summer_cfg,
                                    {"cloud_cover": 40.0, "wind_speed_10m": 1.0},
                                    {"civil_daylight"}, date(2026, 7, 10))
        self.assertFalse(res2.eligible)
        self.assertTrue(any("seasonal_closed" in r for r in res2.failed_reasons))

    def test_overcast_needs_clouds_present(self):
        res = self._tag_score("overcast_soft_light",
                              {"cloud_cover": 30.0, "wind_speed_10m": 1.0,
                               "precipitation": 0.0},
                              ["civil_daylight"])
        self.assertFalse(res.eligible)  # owner 雲量_min: 30% overcast is not overcast
        good = self._tag_score("overcast_soft_light",
                               {"cloud_cover": 95.0, "wind_speed_10m": 1.0,
                                "precipitation": 0.0},
                               ["civil_daylight"])
        self.assertTrue(good.eligible)
        self.assertEqual(good.tier, "recommend")

    def test_scenic_lookout_haze_is_marginal(self):
        res = self._tag_score("scenic_lookout",
                              {"visibility_km": 12.0, "aerosol_optical_depth": 0.5,
                               "cloud_cover_low": 60.0},
                              ["civil_daylight"])
        self.assertTrue(res.eligible)
        self.assertEqual(res.tier, "marginal")  # hazy lookout is shootable but poor


class EngineBypassTests(unittest.TestCase):
    """Phase 2 engine bypass: official contract evaluation untouched."""

    def test_official_contracts_do_not_reference_quality_v2(self):
        opps = ROOT / "data/v2/opportunities"
        for path in sorted(opps.glob("*.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            blob = json.dumps(doc)
            self.assertNotIn("quality-v2", blob, path.name)
            self.assertNotIn("abcd", blob, path.name)

    def test_engine_module_not_imported_by_evaluator(self):
        eb_src = (ROOT / "packages/core-v2/tools/evaluate_batch.py").read_text(encoding="utf-8")
        self.assertNotIn("quality_engine", eb_src)


if __name__ == "__main__":
    unittest.main(verbosity=2)
