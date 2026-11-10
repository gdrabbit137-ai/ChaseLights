"""CL-DATA-56: day pass_hours for window metrics come from own verdicts.

The evaluator's per-day condition summary counted every condition's
pass_hours from the ROLE-GATED hour_status lists (only REQUIRED failures
and REQUIRED/BLOCKER unknowns are recorded there). QUALITY/BONUS window
metrics such as golden_hour_window therefore read verdict=PASS with
pass_hours == 24 — physically impossible for a solar elevation window
(-6..+6 deg gives at most ~2-3 h/day at mid-latitudes). The summary must
tally each condition's own per-hour verdicts instead.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "evaluate_batch", ROOT / "packages/core-v2/tools/evaluate_batch.py")
eb = importlib.util.module_from_spec(spec)
sys.modules["evaluate_batch"] = eb
spec.loader.exec_module(eb)

spec_astro = importlib.util.spec_from_file_location(
    "astro_hourly", ROOT / "packages/models-v2/astro_hourly.py")
astro = importlib.util.module_from_spec(spec_astro)
sys.modules["astro_hourly"] = astro
spec_astro.loader.exec_module(astro)

CONDITION = {"id": "C-x-LW1", "metric": "golden_hour_window",
             "role": "QUALITY", "condition_tier": "BONUS"}


def _tally(states):
    tally = {"PASS": 0, "FAIL": 0, "UNKNOWN": 0}
    for s in states:
        tally[s] += 1
    return tally


class GoldenHourDayVerdictTests(unittest.TestCase):
    def test_quality_window_failing_all_day_is_fail_not_pass_24(self):
        # 24 buckets, condition FAIL in every one (the CL-DATA-56 symptom
        # published PASS / pass_hours=24 here).
        rows = eb.conditions_day_rows(
            {CONDITION["id"]: CONDITION},
            {CONDITION["id"]: _tally(["FAIL"] * 24)}, 24)
        self.assertEqual(rows[0]["day_verdict"], "FAIL")
        self.assertEqual(rows[0]["pass_hours"], 0)

    def test_quality_window_partial_day_counts_own_passes(self):
        # 3 golden buckets out of 24 -> PARTIAL with pass_hours=3.
        states = ["PASS"] * 3 + ["FAIL"] * 21
        rows = eb.conditions_day_rows(
            {CONDITION["id"]: CONDITION},
            {CONDITION["id"]: _tally(states)}, 24)
        self.assertEqual(rows[0]["day_verdict"], "PARTIAL")
        self.assertEqual(rows[0]["pass_hours"], 3)

    def test_full_pass_day_still_reports_pass(self):
        rows = eb.conditions_day_rows(
            {CONDITION["id"]: CONDITION},
            {CONDITION["id"]: _tally(["PASS"] * 24)}, 24)
        self.assertEqual(rows[0]["day_verdict"], "PASS")
        self.assertEqual(rows[0]["pass_hours"], 24)

    def test_unknown_day_propagates_unknown(self):
        rows = eb.conditions_day_rows(
            {CONDITION["id"]: CONDITION},
            {CONDITION["id"]: _tally(["UNKNOWN"] * 24)}, 24)
        self.assertEqual(rows[0]["day_verdict"], "UNKNOWN")
        self.assertEqual(rows[0]["pass_hours"], 0)

    def test_role_gated_hour_lists_never_inflate_pass_hours(self):
        # The hour gate records only REQUIRED failures; a QUALITY FAIL must
        # not be silently re-counted as a pass hour.
        rows = eb.conditions_day_rows(
            {CONDITION["id"]: CONDITION},
            {CONDITION["id"]: _tally(["PASS"] * 4 + ["FAIL"] * 20)}, 24)
        self.assertEqual(rows[0]["pass_hours"], 4)

    def test_golden_hour_daily_minutes_within_physical_cap(self):
        # End-to-end astro pin: at The Wave (36.9561, -111.9043, ~37 N) in
        # November the sun spends well under 3 h/day between -6 and +6 deg
        # elevation. Pin the sub-hour sampled golden minutes per 24 h span
        # (the old bug published pass_hours=24 = 1440 min).
        lat, lon = 36.9561, -111.9043
        base = datetime(2026, 11, 10, tzinfo=timezone.utc)
        events = astro.sun_events_span(
            lat, lon, (base - timedelta(days=1)).timestamp(),
            (base + timedelta(days=2)).timestamp())
        step_min = astro.WINDOW_SAMPLE_OFFSETS[1] - astro.WINDOW_SAMPLE_OFFSETS[0]
        for day_shift in (0, 1):
            minutes = 0
            for h in range(24):
                at = base + timedelta(days=day_shift, hours=h)
                profiles = astro.window_pass_profiles(at, lat, lon,
                                                      events=events)
                minutes += sum(profiles["golden_hour_window"]) * step_min
            self.assertLessEqual(
                minutes, 180,
                f"golden minutes={minutes} on day {day_shift}")
            self.assertGreater(minutes, 0)


if __name__ == "__main__":
    unittest.main()
