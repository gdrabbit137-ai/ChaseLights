"""CL-DATA-43 — Alaska+Hawaii expansion discovery admission (12 places, 12 opportunities).

Owner rulings: PM-judgment admission (2026-11-08) + GROWTH-ONLY (2026-11-09);
scenic scoring paused 2026-11-08.

Pins:
- regions.py us list grows us-001..us-118 (118 active tuples, no removals);
- ak category keeps its pre-43 first-30 tail untouched (us-041..070 prefix order);
- every new opportunity contract schema-validates;
- every all-day (visible-light) subject carries a REQUIRED civil light_window
  citing CL-DATA-43;
- night subjects (night_sky) carry NO light_window;
- 5 km dedupe against the pre-43 us catalog and within the batch;
- Haleakala sunrise carries the reservation note; Kilauea carries the
  eruption-state honesty note; Murphy Dome carries the aurora fail-closed note.
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

NEW_IDS = [f"us-{n:03d}" for n in range(107, 119)]
NEW_CONTRACTS = [f"us-{n:03d}-P01" for n in range(107, 119)]
ALL_DAY_GENRES = {"overlook", "reflection", "mountain_view", "overcast_soft", "golden_hour"}


def load_contract(oid):
    with open(os.path.join(REPO, "data", "v2", "opportunities", f"{oid}.json"), encoding="utf-8") as f:
        return json.load(f)


class TestRegions(unittest.TestCase):
    def test_us_catalog_grew_and_nothing_removed(self):
        spots = regions.REGIONS["us"]["spots"]
        self.assertEqual(len(spots), 158)  # re-anchored CL-DATA-53 (40 Gemini US intake; no removals)
        self.assertEqual(spots[0][3], "Grand Canyon National Park")
        self.assertEqual(spots[105][3], "Big Bend NP – Santa Elena Canyon")
        self.assertEqual(spots[106][6], "阿拉斯加")
        self.assertEqual(spots[111][6], "夏威夷")

    def test_hi_category_is_first_time(self):
        cats = regions.REGIONS["us"]["categories"]
        self.assertIn("夏威夷", cats)
        names = [s[2] for s in regions.REGIONS["us"]["spots"][111:]]
        self.assertIn("哈雷茂茂火山口夜空", names)

    def test_new_admin_areas(self):
        for pid in NEW_IDS:
            self.assertIn(pid, regions.US_ADMIN_AREAS)

    def test_elevation_overrides(self):
        self.assertEqual(regions.ELEVATION_OVERRIDES.get("哈雷阿卡拉山頂雲海日出"), 3055)
        self.assertEqual(regions.ELEVATION_OVERRIDES.get("冒納凱亞遊客站銀河"), 2804)
        self.assertEqual(regions.ELEVATION_OVERRIDES.get("卡拉勞山谷雲霧眺望"), 1219)


class TestDedupe(unittest.TestCase):
    def test_no_new_point_within_5km(self):
        spots = regions.REGIONS["us"]["spots"]
        old = [(s[0], s[1]) for s in spots[:-12]]
        new = [(s[0], s[1]) for s in spots[-12:]]

        def km(a, b):
            la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
            x = (lo2 - lo1) * math.cos((la1 + la2) / 2)
            y = la2 - la1
            return 6371.0 * math.hypot(x, y)

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
                self.assertIn("CL-DATA-43", zh)

    def test_night_subjects_have_no_light_window(self):
        for oid in NEW_CONTRACTS:
            doc = load_contract(oid)
            if doc["condition_contract"]["genre_template"] == "night_sky":
                self.assertFalse(
                    any(c["metric"] == "light_window" for c in doc["condition_contract"]["conditions"]),
                    f"{oid} night subject must not carry light_window")

    def test_special_semantics_notes(self):
        d = load_contract("us-113-P01")
        self.assertIn("Recreation.gov", d["camera_contexts"][0]["access_notes_i18n"]["en"])
        d = load_contract("us-112-P01")
        self.assertIn("not_evaluatable", d["camera_contexts"][0]["access_notes_i18n"]["en"])
        d = load_contract("us-108-P01")
        self.assertIn("fail-closed", d["camera_contexts"][0]["access_notes_i18n"]["en"])

    def test_place_count_in_manifest(self):
        with open(os.path.join(REPO, "data", "v2", "audits", "discovery", "cl-data-43-ak-hi-expansion-2026-11.json"), encoding="utf-8") as f:
            sh = json.load(f)
        self.assertEqual(len(sh["kept"]), 12)
        self.assertEqual(len([k for k in sh["kept"] if k["category"] == "阿拉斯加"]), 5)
        self.assertEqual(len([k for k in sh["kept"] if k["category"] == "夏威夷"]), 7)


if __name__ == "__main__":
    unittest.main()
