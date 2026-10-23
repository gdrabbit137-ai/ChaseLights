"""First-batch ConditionContract evaluation bridge tests (offline, test-only)."""
from __future__ import annotations

import functools
import importlib.util
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages/core-v2"))

from adapters import threshold_observations as bridge  # noqa: E402
from adapters.open_meteo_hourly import PilotFailure  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "evaluate_condition_contract",
    ROOT / "packages/core-v2/tools/evaluate_condition_contract.py")
tool = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool)

ARTIFACT = json.loads((ROOT / "apps/web-v2/weather-pilot-tw036.json").read_text(encoding="utf-8"))
OPPORTUNITY = json.loads((ROOT / "data/v2/opportunities/tw-036-P01.json").read_text(encoding="utf-8"))
EVALUATED_AT = datetime(2026, 10, 23, 18, 30, tzinfo=timezone.utc)


def auto_condition(**overrides):
    condition = {"id": "C-test", "role": "REQUIRED", "domain": "WEATHER",
                 "evaluation_mode": "AUTO", "capability": "CONDITIONS",
                 "metric": "precipitation", "operator": "lte", "threshold": 0.0,
                 "unit": "mm", "unknown_policy": "propagate_unknown",
                 "claim_refs": ["x"], "model_binding": None,
                 "notes_i18n": None, "validation_status": "validated"}
    condition.update(overrides)
    return condition


class BridgeTests(unittest.TestCase):
    def test_only_validated_auto_numeric_conditions_are_observable(self):
        self.assertIsNone(bridge.comparable(auto_condition(evaluation_mode="GUIDANCE")))
        self.assertIsNone(bridge.comparable(auto_condition(validation_status="provisional")))
        self.assertEqual(
            bridge.comparable(auto_condition()),
            ("precipitation", "lte", 0.0))

    def test_invalid_thresholds_fail_closed(self):
        with self.assertRaises(bridge.BridgeFailure):
            bridge.comparable(auto_condition(threshold="heavy"))
        with self.assertRaises(bridge.BridgeFailure):
            bridge.comparable(auto_condition(operator="between", threshold=[0.0]))
        with self.assertRaises(bridge.BridgeFailure):
            bridge.comparable(auto_condition(unknown_policy="ignore"))

    def test_comparison_semantics(self):
        self.assertTrue(bridge.compare(0.0, "lte", 0.0))
        self.assertFalse(bridge.compare(0.1, "lte", 0.0))
        self.assertTrue(bridge.compare(5.0, "gt", 4.9))
        self.assertTrue(bridge.compare(3.0, "between", [2.0, 4.0]))
        self.assertFalse(bridge.compare(4.1, "between", [2.0, 4.0]))

    def test_missing_or_invalid_cells_never_become_booleans(self):
        condition = auto_condition()
        unknown = bridge.cell_observation(condition, {"state": "NOT_PROVIDED"},
                                          at_iso="2026-10-23T20:00:00Z",
                                          provider="p", source="s",
                                          issued_at="2026-10-23T18:00:00Z",
                                          freshness="fresh")
        self.assertIsNone(unknown["value"])
        self.assertEqual(unknown["state"], "UNKNOWN")
        forged = bridge.cell_observation(condition, {"state": "AVAILABLE", "value": "0"},
                                         at_iso="2026-10-23T20:00:00Z", provider="p",
                                         source="s", issued_at="2026-10-23T18:00:00Z",
                                         freshness="fresh")
        self.assertEqual(forged["state"], "UNKNOWN")

    def test_pass_and_fail_carry_provenance(self):
        condition = auto_condition()
        passed = bridge.cell_observation(
            condition, {"state": "AVAILABLE", "value": 0.0, "unit": "mm"},
            at_iso="2026-10-23T20:00:00Z", provider="open-meteo", source="https://x",
            issued_at="2026-10-23T18:00:00Z", freshness="fresh")
        self.assertEqual((passed["state"], passed["value"], passed["test_only"]),
                         ("PASS", True, True))
        failed = bridge.cell_observation(
            condition, {"state": "AVAILABLE", "value": 1.5, "unit": "mm"},
            at_iso="2026-10-23T20:00:00Z", provider="open-meteo", source="https://x",
            issued_at="2026-10-23T18:00:00Z", freshness="fresh")
        self.assertEqual((failed["state"], failed["value"]), ("FAIL", False))


_RUNTIME_TZDB = None
try:
    from adapters.open_meteo_hourly import taipei_zone as _tz
    _RUNTIME_TZDB = _tz()[1]
except Exception:  # pragma: no cover - environment without usable tzdata
    _RUNTIME_TZDB = None
_TZ_ALIGNED = _RUNTIME_TZDB == ARTIFACT["tzdb_version"]


class ToolTests(unittest.TestCase):
    @functools.lru_cache(maxsize=1)
    def _bundle():
        return tool.evaluate_hours(OPPORTUNITY, ARTIFACT, "2026-10-24", EVALUATED_AT)

    bundle = property(lambda self: type(self)._bundle())

    @unittest.skipUnless(_TZ_ALIGNED,
                         "runtime tzdb does not match the artifact's declared version")
    def test_full_local_day_is_evaluated_and_schema_valid(self):
        self.assertEqual(len(self.bundle["results"]), 24)
        self.assertEqual(self.bundle["time_zone"], "Asia/Taipei")
        self.assertEqual(self.bundle["selected_local_date"], "2026-10-24")

    @unittest.skipUnless(_TZ_ALIGNED,
                         "runtime tzdb does not match the artifact's declared version")
    def test_every_result_is_honest_test_only_not_evaluable(self):
        for result in self.bundle["results"]:
            self.assertEqual(result["status"], "NOT_EVALUABLE")
            self.assertFalse(result["live_recommendation"])
            self.assertTrue(result["provenance"]["test_only"])
            self.assertIn("NON_AUTO_MODE", result["unknown_reasons"])
            self.assertIn("PROVIDER_ISSUE_TIME_UNKNOWN", result["unknown_reasons"])

    @unittest.skipUnless(_TZ_ALIGNED,
                         "runtime tzdb does not match the artifact's declared version")
    def test_provider_run_cannot_claim_freshness_after_the_bound(self):
        stale = tool.evaluate_hours(
            OPPORTUNITY, ARTIFACT, "2026-10-24",
            EVALUATED_AT.replace(hour=23))
        self.assertEqual(stale["provider_run"]["freshness"], "STALE")
        self.assertEqual(stale["results"][0]["freshness"], "STALE")

    def test_tzdb_mismatch_yields_honest_empty_not_evaluable(self):
        """Deterministic in every environment: a zone that cannot be aligned
        with the artifact's declared tzdb version must stop evaluation
        instead of silently assuming a different zone definition."""
        original = tool.adapter.select_local_date

        def misaligned(artifact_value, selected_date, inputs):
            raise PilotFailure("TZDB_VERSION_MISMATCH")

        tool.adapter.select_local_date = misaligned
        try:
            bundle = tool.evaluate_hours(OPPORTUNITY, ARTIFACT, "2026-10-24", EVALUATED_AT)
        finally:
            tool.adapter.select_local_date = original
        self.assertEqual(bundle["state"], "NOT_EVALUABLE")
        self.assertEqual(bundle["reason_code"], "TZDB_VERSION_MISMATCH")
        self.assertEqual(bundle["results"], [])
        self.assertIsNone(bundle["provider_run"])
        self.assertTrue(bundle["test_only"])

    @unittest.skipUnless(_TZ_ALIGNED,
                         "date alignment requires the declared tzdb version")
    def test_outside_horizon_dates_fail_closed(self):
        with self.assertRaises(PilotFailure):
            tool.evaluate_hours(OPPORTUNITY, ARTIFACT, "2026-11-20", EVALUATED_AT)
        with self.assertRaises(PilotFailure):
            tool.evaluate_hours(OPPORTUNITY, ARTIFACT, "not-a-date", EVALUATED_AT)

    def test_contract_hash_is_canonical_and_deterministic(self):
        first = tool.contract_sha256(OPPORTUNITY["condition_contract"])
        second = tool.contract_sha256(json.loads(json.dumps(
            OPPORTUNITY["condition_contract"], sort_keys=True)))
        self.assertEqual(first, second)
        self.assertRegex(first, r"^[a-f0-9]{64}$")
        self.assertEqual(self.bundle["condition_contract_sha256"], first)

    def test_bundle_is_deterministic_for_fixed_inputs(self):
        again = tool.evaluate_hours(OPPORTUNITY, ARTIFACT, "2026-10-24", EVALUATED_AT)
        self.assertEqual(json.dumps(self.bundle, sort_keys=True),
                         json.dumps(again, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
