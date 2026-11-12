"""CL-DATA-68: venue_open_window condition — deterministic operating-hour gate.

Round16 challenger findings: jp-034-P01 good_hours at 07:00 preceded Glover
Garden's 8:00 opening; jp-036-P03's 07:00-08:00 hours preceded the rental-boat
8:30 opening; jp-057-P01's 22:00-23:00 hours contradicted the ropeway's 21:00
last uphill car. The contract now declares a REQUIRED venue_open_window
condition (threshold [open, close] HH:MM in the venue's local display clock)
and the evaluator judges it deterministically per hour bucket: the bucket
START must sit inside [open, close). Offline tests, no network.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

spec = importlib.util.spec_from_file_location(
    "evaluate_batch", ROOT / "packages/core-v2/tools/evaluate_batch.py")
eb = importlib.util.module_from_spec(spec)
sys.modules["evaluate_batch"] = eb
spec.loader.exec_module(eb)


def _cond(threshold, role="REQUIRED"):
    return {"id": "C-vw-1", "metric": "venue_open_window", "role": role,
            "operator": "between", "threshold": threshold,
            "unknown_policy": "propagate_unknown", "claim_refs": []}


def _verdict(threshold, hour, minute=0):
    cond = _cond(threshold)
    return eb.condition_verdict(cond, {}, {}, month=11,
                                local_start_min=hour * 60 + minute)[0]


class VenueOpenWindowVerdictTests(unittest.TestCase):
    def test_glover_garden_opening_clamp(self):
        # jp-034-P01: 08:00-18:00 — the 07:00 bucket must FAIL, 08:00 PASS.
        self.assertEqual(_verdict(["08:00", "18:00"], 7), "FAIL")
        self.assertEqual(_verdict(["08:00", "18:00"], 8), "PASS")
        self.assertEqual(_verdict(["08:00", "18:00"], 17), "PASS")
        self.assertEqual(_verdict(["08:00", "18:00"], 18), "FAIL")

    def test_boat_window_half_hour_open(self):
        # jp-036-P03: 08:30-17:00 — bucket start before 08:30 fails.
        self.assertEqual(_verdict(["08:30", "17:00"], 8), "FAIL")
        self.assertEqual(_verdict(["08:30", "17:00"], 8, minute=30), "PASS")
        self.assertEqual(_verdict(["08:30", "17:00"], 16), "PASS")
        self.assertEqual(_verdict(["08:30", "17:00"], 17), "FAIL")

    def test_ropeway_last_uphill_clamp(self):
        # jp-057-P01: 09:00-21:00 — late-night and pre-dawn buckets fail.
        for hour in (21, 22, 23, 0, 2, 5):
            self.assertEqual(_verdict(["09:00", "21:00"], hour), "FAIL", hour)
        self.assertEqual(_verdict(["09:00", "21:00"], 9), "PASS")
        self.assertEqual(_verdict(["09:00", "21:00"], 20), "PASS")

    def test_malformed_windows_fail_closed(self):
        self.assertEqual(_verdict(["21:00", "09:00"], 12), "UNKNOWN")
        self.assertEqual(_verdict("08:00-18:00", 12), "UNKNOWN")
        self.assertEqual(_verdict(["08:00"], 12), "UNKNOWN")
        self.assertEqual(_verdict(["08:00", "25:00"], 12), "UNKNOWN")
        # Missing local time propagates UNKNOWN, never a fabricated verdict.
        detail = eb.venue_open_verdict(_cond(["08:00", "18:00"]), None)
        self.assertEqual(detail[0], "UNKNOWN")

    def test_quality_role_never_gates(self):
        # ROLE semantics are honoured by hour_status: a QUALITY FAIL does not
        # make the hour UNFAVORABLE (advisory only).
        roles = {"C-vw-1": "QUALITY"}
        verdicts = {"C-vw-1": "FAIL"}
        self.assertEqual(eb.hour_status(roles, verdicts)[0],
                         "GUIDANCE_SATISFIED")


class ContractWiringTests(unittest.TestCase):
    """The four round16 contracts must carry the round16 conditions."""

    def _conditions(self, oid):
        path = ROOT / f"data/v2/opportunities/{oid}.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        return doc["condition_contract"]["conditions"]

    def test_jp_090_carries_crux_season_window(self):
        cs = self._conditions("jp-090-P01")
        s1 = [c for c in cs if c["metric"] == "seasonal_state"]
        self.assertEqual(len(s1), 1)
        self.assertEqual(s1[0]["role"], "REQUIRED")
        self.assertEqual(s1[0]["threshold"], "window_open")
        self.assertIn("12", s1[0]["rationale_i18n"]["zh-TW"])
        # The mismatch note: galactic core governs only the milky-way layer.
        self.assertIn("milky_way", s1[0]["rationale_i18n"]["en"])

    def test_jp_034_p01_opening_window(self):
        cs = self._conditions("jp-034-P01")
        vw = [c for c in cs if c["metric"] == "venue_open_window"]
        self.assertEqual(len(vw), 1)
        self.assertEqual(vw[0]["role"], "REQUIRED")
        self.assertEqual(vw[0]["threshold"], ["08:00", "18:00"])

    def test_jp_036_p03_boat_window(self):
        cs = self._conditions("jp-036-P03")
        vw = [c for c in cs if c["metric"] == "venue_open_window"]
        self.assertEqual(len(vw), 1)
        self.assertEqual(vw[0]["threshold"], ["08:30", "17:00"])

    def test_jp_057_ropeway_window(self):
        cs = self._conditions("jp-057-P01")
        vw = [c for c in cs if c["metric"] == "venue_open_window"]
        self.assertEqual(len(vw), 1)
        self.assertEqual(vw[0]["threshold"], ["09:00", "21:00"])

    def test_jp_034_p02_lantern_semantics_removed(self):
        path = ROOT / "data/v2/opportunities/jp-034-P02.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        self.assertNotIn("Lantern Night", doc["name_i18n"]["zh-TW"])
        self.assertNotIn("Lantern Night", doc["description_i18n"]["en"]
                         .split("Subject semantics corrected")[0])
        self.assertIn("洋館夜間燈光", doc["name_i18n"]["zh-TW"])
        # The February festival correction must be documented.
        blob = json.dumps(doc, ensure_ascii=False)
        self.assertIn("2026-02-06", blob)
        self.assertIn("Lantern Night", blob)  # kept only as the corrected note

    def test_metric_vocabulary_covers_venue_open_window(self):
        vocab = json.loads((ROOT / "data/v2/templates/metric-vocabulary.json")
                           .read_text(encoding="utf-8"))
        self.assertIn("venue_open_window", vocab["metrics"])

    def test_unique_condition_ids_preserved(self):
        for oid in ("jp-090-P01", "jp-034-P01", "jp-034-P02",
                    "jp-036-P03", "jp-057-P01"):
            ids = [c["id"] for c in self._conditions(oid)]
            self.assertEqual(len(ids), len(set(ids)), oid)


if __name__ == "__main__":
    unittest.main()
