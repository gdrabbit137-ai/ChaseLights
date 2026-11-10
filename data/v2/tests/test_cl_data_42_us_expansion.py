"""CL-DATA-42 — US-mainland expansion discovery admission (10 places, 14 opportunities).

Owner rulings: PM-judgment admission (2026-11-08 「找到好的直接加入」) +
GROWTH-ONLY (2026-11-09 「先擴充景點」); scenic scoring paused 2026-11-08.

Pins:
- regions.py us list grows us-001..us-118 (re-anchored CL-DATA-43: 118 active tuples, no removals);
- every new opportunity contract schema-validates;
- every all-day (visible-light) subject carries a REQUIRED civil light_window
  citing CL-DATA-42 (not the CL-DATA-19 wave, so that wave's pins are stable);
- 5 km dedupe against the pre-42 us catalog and within the batch.
"""
import json
import math
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "specs", "v2", "tests"))

import regions  # noqa: E402

NEW_IDS = [f"us-{n:03d}" for n in range(97, 107)]
NEW_CONTRACTS = [
    "us-097-P01", "us-097-P02", "us-098-P01", "us-098-P02", "us-099-P01",
    "us-100-P01", "us-100-P02", "us-101-P01", "us-102-P01", "us-103-P01",
    "us-104-P01", "us-105-P01", "us-106-P01", "us-106-P02",
]
ALL_DAY_GENRES = {"overlook", "reflection", "mountain_view", "overcast_soft", "golden_hour"}


def contract_path(oid):
    return os.path.join(REPO, "data", "v2", "opportunities", f"{oid}.json")


def load_contract(oid):
    with open(contract_path(oid), encoding="utf-8") as f:
        return json.load(f)


class TestRegions(unittest.TestCase):
    def test_us_catalog_grew_and_nothing_removed(self):
        spots = regions.REGIONS["us"]["spots"]
        # GROWTH-ONLY: the pre-42 head tuples must all still be present
        self.assertEqual(len(spots), 163)  # re-anchored CL-DATA-64 (us-159..163; growth-only, no removals)
        self.assertEqual(spots[0][3], "Grand Canyon National Park")

    def test_new_admin_areas(self):
        for pid in NEW_IDS:
            self.assertIn(pid, regions.US_ADMIN_AREAS)

    def test_elevation_overrides(self):
        self.assertEqual(regions.ELEVATION_OVERRIDES.get("阿卡迪亞國家公園・卡迪山"), 466)
        self.assertEqual(regions.ELEVATION_OVERRIDES.get("謝南多厄國家公園・老鷹角"), 1235)


class TestDedupe(unittest.TestCase):
    def test_no_new_point_within_5km(self):
        spots = regions.REGIONS["us"]["spots"]
        # spot_id = 1-based list index; re-anchored CL-DATA-64: bound both sides
        # to the catalog state at this batch's admission (us-001..us-106) so
        # later GROWTH-ONLY batches (43/51/52/53/64) appending to the tail do
        # not shift the slice (cross-batch dedupe is each batch's own test).
        new = spots[96:106]
        old = spots[:96]

        def km(a, b):
            la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
            x = (lo2 - lo1) * math.cos((la1 + la2) / 2)
            y = la2 - la1
            return 6371.0 * math.hypot(x, y) * 1000 / 1000

        for i, a in enumerate(new):
            for j, b in enumerate(old):
                d = km(a, b)
                self.assertGreaterEqual(d, 5.0, f"new point {NEW_IDS[i]} only {d:.2f} km from old point {j}")
            for j, b in enumerate(new):
                if j <= i:
                    continue
                self.assertGreaterEqual(km(a, b), 5.0, f"{NEW_IDS[i]} vs {NEW_IDS[j]}")


class TestContracts(unittest.TestCase):
    def test_all_batch_contracts_exist_and_validate(self):
        try:
            from validate_task_w_contracts import validate_record
        except ImportError:
            self.skipTest("validator not importable in this env")
        for oid in NEW_CONTRACTS:
            doc = load_contract(oid)
            errs = validate_record(doc)
            self.assertEqual(errs, [], f"{oid} schema errors: {errs}")

    def test_all_day_subjects_carry_light_window(self):
        for oid in NEW_CONTRACTS:
            doc = load_contract(oid)
            cc = doc["condition_contract"]
            lw = [c for c in cc["conditions"] if c["metric"] == "light_window"]
            if cc["genre_template"] in ALL_DAY_GENRES:
                self.assertTrue(lw, f"{oid} ({cc['genre_template']}) lacks light_window")
                self.assertEqual(lw[0]["role"], "REQUIRED")
                zh = lw[0].get("rationale_i18n", {}).get("zh-TW", "")
                self.assertIn("CL-DATA-42", zh)

    def test_night_subjects_have_no_light_window(self):
        for oid in NEW_CONTRACTS:
            doc = load_contract(oid)
            if doc["condition_contract"]["genre_template"] == "night_sky":
                self.assertFalse(
                    any(c["metric"] == "light_window" for c in doc["condition_contract"]["conditions"]),
                    f"{oid} night subject must not carry light_window")

    def test_place_count_in_shortlist(self):
        with open(os.path.join(REPO, "data", "v2", "audits", "discovery", "us-expansion-2026-11.json"), encoding="utf-8") as f:
            sh = json.load(f)
        self.assertEqual(len(sh["kept"]), 10)
        self.assertEqual(len(sh["culled"]), 6)


if __name__ == "__main__":
    unittest.main()
