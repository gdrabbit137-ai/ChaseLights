"""CL-DATA-77: river_flow_state derivation + spring_tide_state gate (offline).

Covers the audit-stage fixes: the waterfall family's decisive condition is now
derived per the waterfall template's own declared mapping (trailing 72h
accumulated precipitation -> low/mid/high, fail-closed), and the Naruto
whirlpool subject carries a spring-tide band gate proxied by the syzygy moon
illumination. Also verifies the copy-layer sync (fail word / vocabulary) and
the mounted contracts.
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

VOCAB = json.loads((ROOT / "data/v2/templates/metric-vocabulary.json")
                   .read_text(encoding="utf-8"))
FAIL_SHORT = json.loads((ROOT / "data/v2/copy/fail_reason_short.json")
                        .read_text(encoding="utf-8"))
CALENDAR = json.loads((ROOT / "data/v2/seasonal-calendar.json")
                      .read_text(encoding="utf-8"))


def hours(precips):
    return [{"valid_at_utc": "2026-11-20T00:00:00Z",
             "values": {"precipitation": {"value": p, "state": "AVAILABLE"}}}
            for p in precips]


def cond(metric="river_flow_state", role="REQUIRED"):
    return {"id": "C-t-01", "metric": metric, "role": role, "operator": "none",
            "threshold": None, "unit": "level" if metric == "river_flow_state" else None}


class RiverFlowDerivationTest(unittest.TestCase):
    def test_exact_windows_from_past_series(self):
        # 72 past hours of 1 mm each (72 mm trailing at horizon start) followed
        # by a dry horizon: the FIRST hour is wet (72 mm trailing), and the
        # level decays as the window rolls past the wet hours.
        past = [1.0] * eb.RIVER_FLOW_TRAILING_HOURS
        horizon = hours([0.0] * 70)
        levels = eb.river_flow_levels(horizon, past)
        self.assertTrue(all(lv["state"] == "AVAILABLE" for lv in levels))
        # hour 0 window = 72 past hours -> 72 mm -> high
        self.assertEqual(levels[0]["value"], "high")
        # each later hour drops one wet hour from the window; past wet hours
        # 33..71 = 39 mm -> mid, and 68..71.. = 4 mm -> low
        self.assertEqual(levels[1]["value"], "high")
        self.assertEqual(levels[33]["value"], "mid")
        self.assertEqual(levels[68]["value"], "low")

    def test_dry_and_wet_mappings(self):
        past = [0.0] * 72
        levels = eb.river_flow_levels(hours([0.0]), past)
        self.assertEqual(levels[0]["value"], "low")  # 0 mm -> low (dry veto)
        past = [0.0] * 70 + [2.5, 3.0]
        levels = eb.river_flow_levels(hours([0.0]), past)
        self.assertEqual(levels[0]["value"], "mid")  # 5.5 mm -> mid
        past = [0.0] * 70 + [20.0, 21.0]
        levels = eb.river_flow_levels(hours([0.0]), past)
        self.assertEqual(levels[0]["value"], "high")  # 41 mm -> high (still passes)

    def test_fail_closed_on_missing_cells(self):
        levels = eb.river_flow_levels(hours([None]), [0.0] * 72)
        self.assertEqual(levels[0]["state"], "UNKNOWN")
        levels = eb.river_flow_levels(hours([0.0]), None)  # fetch failed
        self.assertEqual(levels[0]["state"], "UNKNOWN")

    def test_condition_verdict_semantics(self):
        cond77 = {"id": "C", "metric": "river_flow_state", "role": "REQUIRED",
                  "operator": "none", "threshold": None}
        astro = {}
        for level, expect in (("low", "FAIL"), ("mid", "PASS"), ("high", "PASS")):
            values = {"river_flow_state": {"state": "AVAILABLE", "value": level}}
            verdict, _ = eb.condition_verdict(cond77, values, astro)[0:2] if False else \
                eb.condition_verdict(cond77, values, astro)
            self.assertEqual(verdict, expect, level)
        values = {"river_flow_state": {"state": "UNKNOWN", "value": None}}
        verdict, reason = eb.condition_verdict(cond77, values, astro)
        self.assertEqual(verdict, "UNKNOWN")
        self.assertEqual(reason, "RIVER_FLOW_STATE_DERIVATION_UNAVAILABLE")


class SpringTideGateTest(unittest.TestCase):
    COND = {"id": "C", "metric": "spring_tide_state", "role": "REQUIRED",
            "operator": "none", "threshold": None}

    def verdict(self, illum):
        astro = {"moon_illumination_fraction": illum}
        return eb.condition_verdict(self.COND, {}, astro)

    def test_band_edges(self):
        self.assertEqual(self.verdict(0.02)[0], "PASS")   # new moon
        self.assertEqual(self.verdict(0.97)[0], "PASS")   # full moon
        self.assertEqual(self.verdict(0.08)[0], "PASS")   # inclusive edge
        self.assertEqual(self.verdict(0.92)[0], "PASS")
        self.assertEqual(self.verdict(0.5)[0], "FAIL")    # quarter moon (neap)
        self.assertEqual(self.verdict(0.3)[0], "FAIL")

    def test_fail_closed_on_unknown_illumination(self):
        astro = {"moon_illumination_fraction": None}
        verdict, reason = eb.condition_verdict(self.COND, {}, astro)
        self.assertEqual(verdict, "UNKNOWN")
        self.assertEqual(reason, "MOON_ILLUMINATION_UNAVAILABLE")
        verdict, reason = eb.condition_verdict(self.COND, {}, {})
        self.assertEqual(verdict, "UNKNOWN")

    def test_malformed_operator_unknown(self):
        bad = dict(self.COND, operator="gte", threshold=0.5)
        verdict, reason = eb.condition_verdict(
            bad, {}, {"moon_illumination_fraction": 0.5})
        self.assertEqual(verdict, "UNKNOWN")

    def test_display_value_is_boolean(self):
        value = eb.condition_value(
            self.COND, {}, {"moon_illumination_fraction": 0.97})
        self.assertIs(value, True)
        value = eb.condition_value(
            self.COND, {}, {"moon_illumination_fraction": 0.5})
        self.assertIs(value, False)


class ContractAndCopySyncTest(unittest.TestCase):
    def test_spring_tide_state_registered_in_vocabulary(self):
        self.assertIn("spring_tide_state", VOCAB["metrics"])
        entry = VOCAB["metrics"]["spring_tide_state"]
        self.assertEqual(entry["domain"], "ASTRONOMY")

    def test_fail_word_registered_trilingual(self):
        self.assertIn("spring_tide_state", FAIL_SHORT["words"])

    def test_jp030_p01_carries_spring_tide_and_light_window(self):
        doc = json.loads((ROOT / "data/v2/opportunities/jp-030-P01.json")
                         .read_text(encoding="utf-8"))
        metrics = [c["metric"] for c in doc["condition_contract"]["conditions"]]
        self.assertIn("spring_tide_state", metrics)
        self.assertIn("light_window", metrics)
        self.assertNotIn("legacy_long_exposure", metrics)
        self.assertIn("claim-02", " ".join(
            ref for c in doc["condition_contract"]["conditions"]
            for ref in c["claim_refs"]))

    def test_jp041_p01_seasonal_gate_mounted(self):
        doc = json.loads((ROOT / "data/v2/opportunities/jp-041-P01.json")
                         .read_text(encoding="utf-8"))
        metrics = [c["metric"] for c in doc["condition_contract"]["conditions"]]
        self.assertIn("seasonal_state", metrics)
        self.assertNotIn("legacy_drift_ice", metrics)
        entry = next(e for e in CALENDAR["entries"]
                     if e.get("plant_id") == "drift_ice")
        self.assertIn("jp-041-P01", entry["spots"])
        self.assertEqual(entry["typical_window"]["start"], "01-20")
        self.assertEqual(entry["typical_window"]["end"], "03-15")

    def test_azimuth_backfills_are_static_verified(self):
        for oid, az in (("us-075-P01", 280), ("us-075-P02", 283),
                        ("us-076-P01", 70), ("us-076-P02", 70),
                        ("us-077-P01", 325), ("us-077-P02", 325),
                        ("jp-030-P99", 236), ("tw-059-P01", 96),
                        ("tw-060-P01", 27), ("tw-078-P01", 284)):
            doc = json.loads((ROOT / f"data/v2/opportunities/{oid}.json")
                             .read_text(encoding="utf-8"))
            rel = doc["observation_relations"][0]
            self.assertEqual(rel["geometry_mode"], "static_verified", oid)
            self.assertEqual(rel["azimuth_deg"], az, oid)
            self.assertTrue(rel.get("derivation_method"), oid)
            claim = next(c for c in doc["evidence_claims"]
                         if c["claim_id"] == f"{oid}-claim-77geo")
            self.assertTrue(claim["scope_note"], oid)
        # tw-060-P01 camera corrected to the OSM viewing platform
        doc = json.loads((ROOT / "data/v2/opportunities/tw-060-P01.json")
                         .read_text(encoding="utf-8"))
        cam = doc["camera_contexts"][0]
        self.assertEqual(cam["geometry"]["geojson"]["coordinates"],
                         [119.4465494, 23.2194319])
        self.assertEqual(cam["geometry"]["status"], "verified")

    def test_waterfall_contracts_still_template_conformant(self):
        for oid in ("jp-070-P01", "jp-081-P01", "jp-083-P01", "jp-091-P01",
                    "tw-151-P01", "tw-224-P01"):
            doc = json.loads((ROOT / f"data/v2/opportunities/{oid}.json")
                             .read_text(encoding="utf-8"))
            metrics = [c["metric"] for c in doc["condition_contract"]["conditions"]]
            self.assertIn("river_flow_state", metrics, oid)
            self.assertIn("precipitation", metrics, oid)
            self.assertEqual(doc["condition_contract"]["genre_template"],
                             "waterfall", oid)


if __name__ == "__main__":
    unittest.main()
