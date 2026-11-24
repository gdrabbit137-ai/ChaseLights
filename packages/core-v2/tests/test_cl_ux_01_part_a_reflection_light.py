"""CL-UX-01 Part A: a reflection subject must not qualify at night.

Owner report (2026-11-24): 鯉魚潭湖光與水面倒影 showed a 00:00–05:00 window —
a daylight reflection subject passing the weather gates in pitch dark. The fix
adds the existing civil `light_window` metric (sun elevation > -6 deg on every
sampled instant of the hour bucket; CL-DATA-11 / CL-DATA-19 same-source
definition) to tw-082-P01 — a DATA correction, not an engine change.

Scope guards this test pins:
  * tw-082-P01 carries light_window in both the legacy `conditions` list and the
    derived `conditions_v2.required` view, and the display bundle ships it;
  * the published evaluation of tw-082-P01 has no night hour (before 06:00) and
    keeps a CONTINUOUS daylight run (no golden-hour split);
  * the two deliberate exceptions stay as they are: tw-007-P02 (碧潭夜間光雕
    倒影) must NOT grow a daylight window, us-012-P01 keeps sunrise_time_window.

Offline: reads repository JSON only, no network.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OPP_DIR = ROOT / "data" / "v2" / "opportunities"
BUNDLE = ROOT / "apps" / "web-v2" / "opportunity-contracts.json"
EVALS = ROOT / "apps" / "web-v2" / "evaluations-latest.json"


def contract(oid: str) -> dict:
    return json.loads((OPP_DIR / f"{oid}.json").read_text(encoding="utf-8"))


class ReflectionLightWindowTests(unittest.TestCase):
    def test_liyu_lake_gains_the_civil_light_window(self):
        d = contract("tw-082-P01")
        cc = d["condition_contract"]
        metrics = [c["metric"] for c in cc["conditions"]]
        self.assertIn("light_window", metrics)
        lw = [c for c in cc["conditions"] if c["metric"] == "light_window"][0]
        self.assertEqual(lw["role"], "REQUIRED")
        self.assertEqual(lw["domain"], "ASTRONOMY")
        self.assertEqual(lw["operator"], "none")
        # the derived view expresses the light gate as a WINDOW, not a required
        # entry (the migrator's canonical shape — same as every other
        # light_window subject, e.g. jp-001-P01)
        self.assertIn("civil_daylight", cc["windows"]["time_of_day"])
        v2_required = [c["metric"] for c in cc["conditions_v2"]["required"]]
        self.assertNotIn("light_window", v2_required)

    def test_revision_advanced(self):
        d = contract("tw-082-P01")
        self.assertGreaterEqual(int(d["revision"]), 3,
                                "the added condition must advance the contract revision")

    def test_display_bundle_ships_the_condition(self):
        bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
        opp = bundle["opportunities"]["tw-082-P01"]
        self.assertIn("light_window", [c["metric"] for c in opp["conditions"]])

    def test_published_evaluation_has_no_night_window(self):
        evals = json.loads(EVALS.read_text(encoding="utf-8"))
        place = [p for p in evals["places"] if p["place_id"] == "tw-082"][0]
        opp = [o for o in place["opportunities"] if o["opportunity_id"] == "tw-082-P01"][0]
        days = opp.get("days") or []
        self.assertTrue(days, "tw-082-P01 must carry evaluated days")
        checked = 0
        for day in days:
            for hh in day.get("good_hours") or []:
                hour = int(str(hh).split(":")[0])
                self.assertGreaterEqual(
                    hour, 6, f"{day['local_date']} {hh} is before sunrise — night hours must fail light_window")
                self.assertLessEqual(
                    hour, 18, f"{day['local_date']} {hh} is after sunset — light_window must exclude it")
                checked += 1
        self.assertGreater(checked, 0, "at least one daylight hour must still qualify (the subject is not dead)")

    def test_daylight_run_is_continuous_not_a_golden_hour_slice(self):
        evals = json.loads(EVALS.read_text(encoding="utf-8"))
        place = [p for p in evals["places"] if p["place_id"] == "tw-082"][0]
        opp = [o for o in place["opportunities"] if o["opportunity_id"] == "tw-082-P01"][0]
        widest = max((len(d.get("good_hours") or []) for d in opp.get("days") or []), default=0)
        self.assertGreaterEqual(widest, 6,
                                "the daylight window must stay a broad daytime run, not a 1-2 hour slice")

    def test_night_light_sculpture_stays_exempt(self):
        cc = contract("tw-007-P02")["condition_contract"]
        self.assertNotIn("light_window", [c["metric"] for c in cc["conditions"]],
                         "碧潭夜間光雕倒影 is a night subject — a daylight window would kill it")

    def test_sunrise_window_subject_keeps_its_own_mechanism(self):
        cc = contract("us-012-P01")["condition_contract"]
        metrics = [c["metric"] for c in cc["conditions"]]
        self.assertIn("sunrise_time_window", metrics)
        self.assertNotIn("light_window", metrics)


if __name__ == "__main__":
    unittest.main()
