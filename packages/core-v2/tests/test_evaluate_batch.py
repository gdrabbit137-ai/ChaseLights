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


class ConditionValueContractTests(unittest.TestCase):
    """CL-UI-06: condition.value must never be a raw JSON boolean."""

    def test_astro_window_bool_maps_to_enum(self):
        condition = {"metric": "sunset_window", "operator": "none",
                     "threshold": None, "role": "QUALITY"}
        self.assertEqual(eb.condition_value(condition, {}, {"sunset_window": True}),
                         "satisfied")
        self.assertEqual(eb.condition_value(condition, {}, {"sunset_window": False}),
                         "unsatisfied")

    def test_astro_bool_metrics_never_emit_raw_boolean(self):
        condition = {"metric": "astronomical_darkness", "operator": "none",
                     "threshold": None, "role": "REQUIRED"}
        for raw in (True, False):
            self.assertIn(eb.condition_value(condition, {}, {"astronomical_darkness": raw}),
                          ("satisfied", "unsatisfied"))

    def test_astro_numeric_passes_through(self):
        condition = {"metric": "moon_altitude", "operator": "gte",
                     "threshold": 10, "role": "REQUIRED"}
        self.assertEqual(eb.condition_value(condition, {}, {"moon_altitude": 25.5}), 25.5)
        self.assertIsNone(eb.condition_value(condition, {}, {"moon_altitude": None}))

    def test_no_source_metric_value_none(self):
        condition = {"metric": "water_surface_state", "operator": "none",
                     "threshold": None, "role": "REQUIRED"}
        self.assertIsNone(eb.condition_value(condition, {}, {}))

    def test_declared_metric_value_enum(self):
        condition = {"metric": "landform_present", "operator": "none",
                     "threshold": None, "role": "REQUIRED"}
        self.assertEqual(eb.condition_value(condition, {}, {}), "declared")

    def test_weather_boolean_cell_maps_to_enum(self):
        condition = {"metric": "river_flow_state", "operator": "is_true",
                     "threshold": None, "role": "REQUIRED"}
        cell = {"value": True, "state": "AVAILABLE"}
        self.assertEqual(eb.condition_value(condition, {"river_flow_state": cell}, {}),
                         "satisfied")
        cell["value"] = False
        self.assertEqual(eb.condition_value(condition, {"river_flow_state": cell}, {}),
                         "unsatisfied")

    def test_unavailable_weather_cell_value_none(self):
        condition = {"metric": "cloud_cover_low", "operator": "lte",
                     "threshold": 55, "role": "REQUIRED"}
        cell = {"value": None, "state": "UNAVAILABLE"}
        self.assertIsNone(eb.condition_value(condition, {"cloud_cover_low": cell}, {}))

    def test_enum_constants_are_strings(self):
        self.assertEqual(eb.BOOLEAN_VALUE_SATISFIED, "satisfied")
        self.assertEqual(eb.BOOLEAN_VALUE_UNSATISFIED, "unsatisfied")
        self.assertNotIsInstance(eb.BOOLEAN_VALUE_SATISFIED, bool)


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
