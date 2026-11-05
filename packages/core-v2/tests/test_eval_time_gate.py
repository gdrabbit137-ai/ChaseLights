"""CL-UI-23: evaluation-layer time-window gate for night subjects.

Root cause fixed here: city_night contracts carry no time-window condition
(owner data-layer gap, owner gate pending), so daytime hours passed every
REQUIRED weather condition and became good_hours — a night skyline advertised
at 11:00-15:00. The evaluation layer now injects a deterministic
city_night_window (whole hour bucket after civil dusk, sun <= -6 deg) REQUIRED
gate for such contracts. Offline tests, no network.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]

spec = importlib.util.spec_from_file_location(
    "evaluate_batch", ROOT / "packages/core-v2/tools/evaluate_batch.py")
eb = importlib.util.module_from_spec(spec)
sys.modules["evaluate_batch"] = eb
spec.loader.exec_module(eb)

spec2 = importlib.util.spec_from_file_location(
    "astro_hourly", ROOT / "packages/models-v2/astro_hourly.py")
ah = importlib.util.module_from_spec(spec2)
sys.modules["astro_hourly"] = ah
spec2.loader.exec_module(ah)

LAT, LON = 25.0288, 121.5722  # Elephant Mountain vicinity (synthetic use)


def _night_contract():
    return {
        "contract_id": "CC-test-night",
        "genre_template": "city_night",
        "conditions": [
            {"id": "C-n-1", "metric": "cloud_cover_total", "role": "REQUIRED",
             "operator": "lte", "threshold": 30},
            {"id": "C-n-2", "metric": "visibility", "role": "REQUIRED",
             "operator": "gte", "threshold": 10},
        ],
    }


def _day_contract():
    return {
        "contract_id": "CC-test-day",
        "genre_template": "blue_hour_city",
        "conditions": [
            {"id": "C-d-1", "metric": "blue_hour_window", "role": "REQUIRED",
             "operator": "none"},
        ],
    }


class GateInjectionTests(unittest.TestCase):
    def test_city_night_contract_gets_window_gate(self):
        conds = eb.eval_conditions_for(_night_contract())
        self.assertEqual(len(conds), 3)
        gate = conds[-1]
        self.assertEqual(gate["id"], eb.GATE_CONDITION_ID)
        self.assertEqual(gate["metric"], "city_night_window")
        self.assertEqual(gate["role"], "REQUIRED")

    def test_contract_with_window_metric_not_gated(self):
        conds = eb.eval_conditions_for(_day_contract())
        self.assertEqual(len(conds), 1)
        self.assertNotEqual(conds[0]["id"], eb.GATE_CONDITION_ID)

    def test_gate_is_evaluation_layer_only(self):
        contract = _night_contract()
        eb.eval_conditions_for(contract)
        # The owner contract object must be untouched (no gate written into
        # data/v2/opportunities, no sha drift).
        self.assertEqual(len(contract["conditions"]), 2)
        self.assertNotIn("EVALGATE", json.dumps(
            [c["id"] for c in contract["conditions"]]))

    def test_gate_condition_id_verdict_membership(self):
        # operator none + astro metric -> window membership verdict.
        self.assertEqual(
            eb.condition_verdict(eb.GATE_CONDITION, {},
                                 {"city_night_window": True})[0], "PASS")
        self.assertEqual(
            eb.condition_verdict(eb.GATE_CONDITION, {},
                                 {"city_night_window": False})[0], "FAIL")


def _fake_alt(dt_utc, lat, lon):
    # Taipei 2026-11-05 local: sun below -6 deg only after ~17:45 local
    # (synthetic monotone curve keyed on UTC hour of day is enough for the
    # gate semantics: daytime buckets must fail).
    hour_local = (dt_utc.hour + 8) % 24
    minute_local = dt_utc.minute
    frac = (hour_local + minute_local / 60.0)
    # altitude proxy: +30 deg at local noon 12:00, -30 deg at local midnight
    import math
    return 30.0 * math.cos((frac - 12.0) / 24.0 * 2 * math.pi)


class CityNightWindowAstroTests(unittest.TestCase):
    def observe(self, hour_local):
        dt = datetime(2026, 11, 5, (hour_local - 8) % 24, 0, tzinfo=timezone.utc)
        with patch.object(ah, "_sun_altitude", _fake_alt):
            return ah.hour_observations(dt, LAT, LON)

    def test_daytime_bucket_fails(self):
        # 11:00-12:00 local: whole bucket in daylight -> gate must be False.
        self.assertFalse(self.observe(11)["city_night_window"])

    def test_full_dark_bucket_passes(self):
        # 20:00-21:00 local: whole bucket well after civil dusk.
        self.assertTrue(self.observe(20)["city_night_window"])

    def test_dusk_bucket_must_not_qualify(self):
        # 17:00-18:00 local: early samples still above -6 deg -> not a
        # night hour (all-sample semantics).
        self.assertFalse(self.observe(17)["city_night_window"])


import json  # noqa: E402  (kept after the class constants above)


class HourAggregationGateTests(unittest.TestCase):
    def test_required_gate_fail_makes_hour_unfavorable(self):
        roles = {"C-n-1": "REQUIRED", eb.GATE_CONDITION_ID: "REQUIRED"}
        verdicts = {"C-n-1": "PASS", eb.GATE_CONDITION_ID: "FAIL"}
        status, fails, _ = eb.hour_status(roles, verdicts)
        self.assertEqual(status, "UNFAVORABLE")
        self.assertEqual(fails, [eb.GATE_CONDITION_ID])


if __name__ == "__main__":
    unittest.main()
