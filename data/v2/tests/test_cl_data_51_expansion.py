"""CL-DATA-51 — Gemini TW photography list intake (22 places tw-099..tw-120, 22 opportunities).

Owner directive: 參考 Gemini 台灣攝影名點清單把適合的加進去 (2026-11-09).
Admission: rubric v2 (subject25/weather_light20/verifiability20/differentiation15/scenic_beauty20,
>=3.8) + 5km geo dedupe per CL-DATA-25 institution; web-verified geometry with
source URLs recorded in data/v2/audits/cl-data-51_web_evidence.json.

Pins:
- regions.py tw list grows to 120 active tuples (tw-001..tw-120, no removals);
- every new opportunity contract schema-validates and carries the batch
  evidence claim ref e-d51-web-<slug>;
- all-day subjects carry a civil light_window (sun elevation > -6 deg);
- night subjects carry NO light_window;
- 5km dedupe: the two sub-5km admissions (tw-101 林口水牛坑 3.29km / tw-104
  忘憂森林 2.16km) are documented subject-differentiation overrides in
  cl-data-51-dedupe.json (CL-DATA-25R precedent), everything else >= 5km;
- seasonal windows present in seasonal-calendar.json;
- runtime catalog counts, manifest tw counts, runtime_dependencies gap sets.
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

NEW_IDS = [f"tw-{n:03d}" for n in range(99, 121)]
NEW_CONTRACTS = [f"tw-{n:03d}-P01" for n in range(99, 121)]
ALL_DAY_GENRES = {"overlook", "reflection", "mountain_view", "overcast_soft", "golden_hour",
                  "cloud_sea", "geological_landform", "waterfall", "blue_hour_city"}
NIGHT_GENRES = {"night_sky", "city_night"}
DEDUPE_OVERRIDES = {"tw-101": 3.29, "tw-104": 2.16}


def load(p):
    with open(os.path.join(REPO, p), encoding="utf-8") as f:
        return json.load(f)


class TestRegions(unittest.TestCase):
    def test_tw_catalog_grew_and_nothing_removed(self):
        spots = regions.REGIONS["tw"]["spots"]
        self.assertEqual(len(spots), 120)
        self.assertEqual(spots[97][2], "渭水之丘／櫻花陵園")  # tw-098 untouched
        self.assertEqual(spots[98][2], "桃源谷（灣坑頭山草原）")  # first new (tw-099)
        self.assertEqual(spots[-1][2], "武陵農場")  # tw-120

    def test_new_admin_areas(self):
        for pid in NEW_IDS:
            self.assertIn(pid, regions.TW_ADMIN_AREAS)

    def test_coordinate_overrides_web_verified(self):
        for pid in NEW_IDS:
            spot = regions.get_spots("tw")[int(pid.split("-")[1]) - 1]
            self.assertIn("CL-DATA-51", spot.get("coordinate_source", ""), pid)

    def test_elevation_overrides_or_honest_unknown(self):
        self.assertEqual(regions.ELEVATION_OVERRIDES.get("太魯閣燕子口"), None)  # honest unknown
        self.assertEqual(regions.ELEVATION_OVERRIDES.get("加里山"), 2220)  # corrected from dossier 2492
        self.assertEqual(regions.ELEVATION_OVERRIDES.get("清境農場"), 1748)


class TestDedupe(unittest.TestCase):
    def test_dedupe_registry_and_distances(self):
        reg = load("data/v2/audits/discovery/cl-data-51-dedupe.json")
        self.assertEqual(set(reg), set(NEW_IDS))
        for pid, row in reg.items():
            km = row["km"]
            if km < 5.0:
                self.assertIn(pid, DEDUPE_OVERRIDES, f"{pid} sub-5km without documented override")
                self.assertAlmostEqual(km, DEDUPE_OVERRIDES[pid], places=1)
                self.assertIn("override", row)
            else:
                self.assertGreaterEqual(km, 5.0)


class TestContracts(unittest.TestCase):
    def test_all_batch_contracts_exist_and_validate(self):
        try:
            from validate_task_w_contracts import validate_record
        except ImportError:
            self.skipTest("validator not importable in this env")
        for oid in NEW_CONTRACTS:
            doc = load(f"data/v2/opportunities/{oid}.json")
            errs = validate_record(doc)
            self.assertEqual(errs, [], f"{oid} schema errors: {errs}")

    def test_unique_condition_ids(self):
        for oid in NEW_CONTRACTS:
            doc = load(f"data/v2/opportunities/{oid}.json")
            ids = [c["id"] for c in doc["condition_contract"]["conditions"]]
            self.assertEqual(len(ids), len(set(ids)), f"{oid} duplicate condition id")

    def test_all_day_subjects_carry_civil_light_window(self):
        for oid in NEW_CONTRACTS:
            doc = load(f"data/v2/opportunities/{oid}.json")
            cc = doc["condition_contract"]
            if cc["genre_template"] in ALL_DAY_GENRES:
                lw = [c for c in cc["conditions"]
                      if c["metric"] in ("light_window", "sunrise_time_window", "sunset_window",
                                         "blue_hour_window", "golden_hour_window")]
                self.assertTrue(lw, f"{oid} ({cc['genre_template']}) lacks a light-window condition")
                self.assertTrue(any(c["role"] == "REQUIRED" for c in lw), oid)  # ≥1 REQUIRED light-semantics window; QUALITY golden-hour modifiers allowed

    def test_no_night_subjects_without_darkness_window(self):
        for oid in NEW_CONTRACTS:
            doc = load(f"data/v2/opportunities/{oid}.json")
            if doc["condition_contract"]["genre_template"] in NIGHT_GENRES:
                metrics = [c["metric"] for c in doc["condition_contract"]["conditions"]]
                self.assertNotIn("light_window", metrics, oid)

    def test_batch_evidence_claim_refs(self):
        ev = load("data/v2/audits/cl-data-51_web_evidence.json")
        self.assertEqual(len(ev["places"]), 22)
        self.assertEqual(len(ev["evidence"]), 22)
        ids = {e["id"] for e in ev["evidence"]}
        for doc, adm in zip([load(f"data/v2/opportunities/{oid}.json") for oid in NEW_CONTRACTS], ids):
            refs = doc["evidence_claims"][0]["evidence_refs"]
            self.assertTrue(refs and refs[0] in ids, refs)

    def test_seasonal_calendar_windows(self):
        cal = load("data/v2/seasonal-calendar.json")
        have = {e["plant_id"] for e in cal["entries"]}
        for sid in ("shiding_mist", "qingjing_unkai", "taiping_unkai", "daylily_chike",
                    "balloon_festival", "daylily_taimali", "lisong_dry", "sakura_wuling"):
            self.assertIn(sid, have, sid)
        for e in cal["entries"]:
            if e["plant_id"] == "daylily_chike":
                self.assertEqual(e["typical_window"], {"start": "08-01", "end": "10-15"})


class TestRuntime(unittest.TestCase):
    def test_runtime_catalog_counts(self):
        cat = load("runtime_catalog_v004_r4_2.json")
        self.assertEqual(cat["counts"]["spots"], 301)
        self.assertEqual(cat["counts"]["opportunities"], 528)
        tw = [s for s in cat["spots"] if s["spot_id"].startswith("tw-")]
        self.assertEqual(len(tw), 115)

    def test_manifest_tw_counts(self):
        mf = load("runtime_catalog_manifest_r4_2.json")
        self.assertEqual(mf["regions"]["tw"]["numeric_id_end"], 120)
        self.assertEqual(mf["regions"]["tw"]["counts"]["spots"], 115)
        self.assertEqual(mf["totals"], load("runtime_catalog_v004_r4_2.json")["counts"])

    def test_runtime_dependencies_gaps(self):
        src = open(os.path.join(REPO, "runtime_dependencies.py"), encoding="utf-8").read()
        for oid in ("tw-100-P01", "tw-103-P01", "tw-105-P01", "tw-119-P01"):  # cloud_sea batch
            self.assertIn(f'"{oid}"', src, oid)
        for oid in ("tw-099-P01", "tw-102-P01", "tw-109-P01", "tw-115-P01"):  # directional_horizon (sunrise/sunset/overlook)
            self.assertIn(f'"{oid}"', src, oid)
        for oid in ("tw-114-P01", "tw-116-P01", "tw-120-P01"):  # seasonal_foreground (seasonal_plant)
            self.assertIn(f'"{oid}"', src, oid)


if __name__ == "__main__":
    unittest.main()
