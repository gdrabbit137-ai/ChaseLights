"""Offline tests for the batch GUIDANCE evaluator (no network)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "evaluate_batch", ROOT / "packages/core-v2/tools/evaluate_batch.py")
eb = importlib.util.module_from_spec(spec)
sys.modules["evaluate_batch"] = eb
spec.loader.exec_module(eb)

import unittest


class HourStatusTests(unittest.TestCase):
    def test_required_fail_is_unfavorable(self):
        roles = {"a": "REQUIRED", "b": "QUALITY"}
        verdicts = {"a": "FAIL", "b": "FAIL"}
        status, fails, unknowns = eb.hour_status(roles, verdicts)
        self.assertEqual(status, "UNFAVORABLE")
        self.assertEqual(fails, ["a"])

    def test_quality_never_gates(self):
        roles = {"a": "REQUIRED", "b": "QUALITY"}
        verdicts = {"a": "PASS", "b": "FAIL"}
        status, fails, _ = eb.hour_status(roles, verdicts)
        self.assertEqual(status, "GUIDANCE_SATISFIED")
        self.assertEqual(fails, [])

    def test_blocker_pass_blocks(self):
        roles = {"a": "REQUIRED", "x": "BLOCKER"}
        verdicts = {"a": "PASS", "x": "PASS"}
        status, fails, _ = eb.hour_status(roles, verdicts)
        self.assertEqual(status, "UNFAVORABLE")

    def test_required_unknown_not_evaluable(self):
        roles = {"a": "REQUIRED"}
        status, _, _ = eb.hour_status(roles, {"a": "UNKNOWN"})
        self.assertEqual(status, "NOT_EVALUABLE")


class ConditionVerdictTests(unittest.TestCase):
    def test_no_source_metric_unknown(self):
        condition = {"metric": "water_surface_state", "operator": "none",
                     "threshold": None, "role": "REQUIRED"}
        verdict, reason = eb.condition_verdict(condition, {}, {})
        self.assertEqual((verdict, reason), ("UNKNOWN", "NO_LIVE_OBSERVATION_SOURCE"))

    def test_declared_metric_passes(self):
        condition = {"metric": "landform_present", "operator": "none",
                     "threshold": None, "role": "REQUIRED"}
        verdict, reason = eb.condition_verdict(condition, {}, {})
        self.assertEqual((verdict, reason), ("PASS", "OWNER_DECLARED_PRESENCE"))

    def test_forecast_threshold(self):
        condition = {"metric": "cloud_cover_low", "operator": "lte",
                     "threshold": 55, "role": "REQUIRED"}
        values = {"cloud_cover_low": {"value": 40, "state": "AVAILABLE"}}
        self.assertEqual(eb.condition_verdict(condition, values, {}), ("PASS", "FORECAST_THRESHOLD"))
        values = {"cloud_cover_low": {"value": 80, "state": "AVAILABLE"}}
        self.assertEqual(eb.condition_verdict(condition, values, {}), ("FAIL", "FORECAST_THRESHOLD"))
        values = {"cloud_cover_low": {"value": None, "state": "UNAVAILABLE"}}
        self.assertEqual(eb.condition_verdict(condition, values, {}), ("UNKNOWN", "CELL_NOT_AVAILABLE"))

    def test_astro_window_membership(self):
        condition = {"metric": "sunrise_time_window", "operator": "none",
                     "threshold": None, "role": "REQUIRED"}
        self.assertEqual(eb.condition_verdict(condition, {}, {"sunrise_time_window": True}),
                         ("PASS", "ASTRO_WINDOW_MEMBERSHIP"))
        self.assertEqual(eb.condition_verdict(condition, {}, {"sunrise_time_window": False}),
                         ("FAIL", "ASTRO_WINDOW_MEMBERSHIP"))
        self.assertEqual(eb.condition_verdict(condition, {}, {"sunrise_time_window": None}),
                         ("UNKNOWN", "ASTRO_UNAVAILABLE_AT_INSTANT"))

    def test_astro_numeric(self):
        condition = {"metric": "galactic_core_altitude", "operator": "gte",
                     "threshold": 20, "role": "REQUIRED"}
        self.assertEqual(eb.condition_verdict(condition, {}, {"galactic_core_altitude": 30.0}),
                         ("PASS", "ASTRO_THRESHOLD"))
        self.assertEqual(eb.condition_verdict(condition, {}, {"galactic_core_altitude": 5.0}),
                         ("FAIL", "ASTRO_THRESHOLD"))

    def test_unmapped_metric_unknown(self):
        condition = {"metric": "mystery_metric", "operator": "gt", "threshold": 1}
        self.assertEqual(eb.condition_verdict(condition, {}, {}), ("UNKNOWN", "METRIC_NOT_MAPPED"))


class BundleShapeTests(unittest.TestCase):
    def test_generated_bundle_validates(self):
        import json
        import jsonschema
        schema = json.loads((ROOT / "specs/v2/schema/evaluation-bundle-v0.1.schema.json")
                            .read_text(encoding="utf-8"))
        bundle_path = ROOT / "apps/web-v2/evaluations-latest.json"
        if not bundle_path.exists():
            self.skipTest("no published bundle yet")
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        errors = list(jsonschema.Draft202012Validator(schema).iter_errors(bundle))
        self.assertEqual(errors, [])
        self.assertIs(bundle["guidance_only"], True)
        self.assertIs(bundle["live_recommendation"], False)


if __name__ == "__main__":
    unittest.main()
