"""CL-INT-91: details rows must key every good_hour stamp the summary emits.

CL-DATA-31 stamps qualifying hour buckets at their earliest passing
sub-hour sample (good_hours carry local_precise, e.g. 17:25), while the
details grid was still emitting only hourly bucket rows (17:00) — the
cl-ui-23 lookup missed sub-hour stamps. The fix makes a qualifying
bucket emit an ADDITIONAL sub-hour details row keyed at the precise
stamp. These offline tests pin the writer contract.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "evaluate_batch", ROOT / "packages/core-v2/tools/evaluate_batch.py")
eb = importlib.util.module_from_spec(spec)
sys.modules["evaluate_batch"] = eb
spec.loader.exec_module(eb)


def _bucket(at_local="2026-11-08 17:00"):
    at = datetime.fromisoformat(at_local + "+00:00")
    hour_row = {"valid_at_utc": at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "values": {"cloud_cover_total": 10, "precipitation": 0}}
    conditions_eval = [
        {"id": "c-cloud", "metric": "cloud_cover_total", "operator": "lte",
         "threshold": 55, "role": "REQUIRED", "condition_tier": "MAIN"},
        {"id": "c-window", "metric": "sunrise_time_window", "operator": "none",
         "threshold": None, "role": "REQUIRED", "condition_tier": "MAIN"},
    ]
    astro_row = {"sunrise_time_window": "satisfied"}
    states = {"c-cloud": "PASS", "c-window": "PASS"}
    return at, hour_row, conditions_eval, astro_row, states


class SubHourDetailsRowTests(unittest.TestCase):
    def test_qualifying_bucket_gains_sub_hour_row(self):
        at, hour_row, conds, astro, states = _bucket()
        rows = eb.detail_hour_rows(
            hour_row, at, "GUIDANCE_SATISFIED", conds, astro, states,
            precise_local="17:25", precise_off=25)
        locals_ = [r["local"] for r in rows]
        # BOTH the hourly bucket row and the sub-hour row exist.
        self.assertEqual(locals_, ["17:00", "17:25"])
        sub = rows[1]
        self.assertEqual(sub["sub_hour_of_bucket"], "17:00")
        self.assertEqual(sub["sample_offset_min"], 25)
        self.assertEqual(sub["status"], "GUIDANCE_SATISFIED")
        self.assertEqual(sub["utc"], hour_row["valid_at_utc"])

    def test_bucket_row_shape_unchanged_without_precise_stamp(self):
        at, hour_row, conds, astro, states = _bucket()
        rows = eb.detail_hour_rows(
            hour_row, at, "GUIDANCE_SATISFIED", conds, astro, states,
            precise_local=None, precise_off=None)
        self.assertEqual([r["local"] for r in rows], ["17:00"])
        self.assertEqual(rows[0]["status"], "GUIDANCE_SATISFIED")
        self.assertIn("conditions", rows[0])

    def test_non_qualifying_bucket_never_emits_sub_hour_row(self):
        at, hour_row, conds, astro, states = _bucket()
        rows = eb.detail_hour_rows(
            hour_row, at, "UNFAVORABLE", conds, astro, states,
            precise_local=None, precise_off=None)
        self.assertEqual([r["local"] for r in rows], ["17:00"])
        self.assertEqual(rows[0]["status"], "UNFAVORABLE")

    def test_every_good_hour_stamp_keys_a_details_row(self):
        # The cl-ui-23 invariant, at the writer level: projecting the
        # bucket rows exactly like the summary's good_hours
        # (local_precise or bucket stamp) must yield keys all present in
        # the details rows of the same day.
        at, hour_row, conds, astro, states = _bucket()
        bucket_row = {"local": at.strftime("%H:%M"),
                      "local_precise": "17:25",
                      "status": "GUIDANCE_SATISFIED"}
        rows = eb.detail_hour_rows(
            hour_row, at, bucket_row["status"], conds, astro, states,
            precise_local=bucket_row["local_precise"], precise_off=25)
        details = {r["local"]: r for r in rows}
        stamp = bucket_row.get("local_precise") or bucket_row["local"]
        self.assertIn(stamp, details)
        self.assertEqual(details[stamp]["status"], bucket_row["status"])

    def test_sub_hour_row_stays_inside_the_bucket_day(self):
        # Sample offsets are sub-hour, so the precise stamp can never
        # cross into the next local day of its bucket.
        at, hour_row, conds, astro, states = _bucket("2026-11-08 23:00")
        rows = eb.detail_hour_rows(
            hour_row, at, "GUIDANCE_SATISFIED", conds, astro, states,
            precise_local="23:55", precise_off=55)
        self.assertEqual(rows[1]["sub_hour_of_bucket"], "23:00")
        minute = int(rows[1]["local"].split(":")[1])
        self.assertLess(minute, 60)


if __name__ == "__main__":
    unittest.main()
