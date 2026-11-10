"""CL-DATA-53 — Gemini US photography list intake (40 places us-119..us-158, 41 opportunities).

Owner directive: US third-round photography-spot intake (2026-11-09), GROWTH-ONLY
PM-judgment admission per the CL-DATA-51/52 flow; 5km geo dedupe (CL-DATA-25 institution,
subject-differentiation overrides documented); web-verified coordinates/elevations/seasons
with source URLs in data/v2/audits/cl-data-53_web_evidence.json.
Excluded as near-duplicates of existing catalog spots: Steptoe Butte (us-094),
HalemaumaU lava-glow night (us-112), Turnagain Arm sunset (us-109), Bentonite Hills
(coordinates unverifiable, <6 km from an existing Canyonlands point).
Stage-1b also backfilled the 22 CL-DATA-42/43 legacy runtime spots us-097..118.

Pins:
- regions.py us list grows to 158 ids (us-119..us-158 appended; no removals);
- every new contract schema-validates, unique condition ids, evidence ref e-d53-web-<slug>;
- all-day subjects carry a civil light-window; night subjects carry NO light_window;
- permit/physical access restrictions (The Wave daily lottery, Navajo rim permit,
  NPS closed alcove, ferry-only, strenuous trails) are recorded in access notes and NOT scored;
- seasonal windows present in seasonal-calendar.json (5 entries);
- AGLI v2 dual-board records in agli-final.json (L/P, zero 90+, anchor comparandum for L>75);
- runtime catalog counts (incl. us-097..118 backfill), manifest us counts (numeric_id_end 158),
  runtime-deps gap sets, evaluations bundle spliced 353/550.
"""
import json
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "specs", "v2", "tests"))

import regions  # noqa: E402

NEW_IDS = [f"us-{n}" for n in range(119, 159)]
NEW_CONTRACTS = [f"us-{n}-P01" for n in range(119, 159)]  # us-152-P02 removed (CL-DATA-54 ghost-opportunity deletion)
ALL_DAY_GENRES = {"overlook", "reflection", "mountain_view", "cloud_sea",
                  "geological_landform", "waterfall", "blue_hour_city"}
NIGHT_GENRES = {"night_sky", "city_night"}
PERMIT_PLACE_IDS = {"us-119", "us-130", "us-132", "us-134", "us-147", "us-148", "us-155", "us-158"}  # access-restricted, honestly labeled


def load(p):
    with open(os.path.join(REPO, p), encoding="utf-8") as f:
        return json.load(f)


class TestRegions(unittest.TestCase):
    def test_us_catalog_grew(self):
        spots = regions.get_spots("us")
        self.assertEqual(len(spots), 163)  # re-anchored CL-DATA-64 (us-159..160 Yellowstone geothermal + us-161..163 Kilauea lava; growth-only)
        self.assertEqual(spots[-1]["name_i18n"]["zh-TW"], "基勞亞伊奇火山口熔岩地表")  # us-163

    def test_new_admin_areas(self):
        for pid in NEW_IDS:
            self.assertIn(pid, regions.US_ADMIN_AREAS)

    def test_coordinate_overrides_web_verified(self):
        for spot in regions.get_spots("us"):
            if spot["spot_id"] in NEW_IDS:
                self.assertIn("CL-DATA-53", spot.get("coordinate_source", ""), spot["spot_id"])

    def test_no_removals(self):
        ids = [s["spot_id"] for s in regions.get_spots("us")]
        self.assertEqual(len(ids), len(set(ids)))
        for legacy in ("us-094", "us-109", "us-112"):
            self.assertIn(legacy, ids)  # near-duplicate candidates STAY in catalog (GROWTH-ONLY)


class TestDedupe(unittest.TestCase):
    def test_dedupe_registry_and_distances(self):
        reg = load("data/v2/audits/discovery/cl-data-53-dedupe.json")
        self.assertTrue(set(reg).issuperset(set(NEW_IDS)), reg.keys())
        for pid in NEW_IDS:
            row = reg[pid]
            if row["km"] < 5.0:
                self.assertIn("override", row, f"{pid} sub-5km without documented override")
            else:
                self.assertGreaterEqual(row["km"], 5.0)


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

    def test_night_subjects_carry_no_daylight_light_window(self):
        for oid in NEW_CONTRACTS:
            doc = load(f"data/v2/opportunities/{oid}.json")
            if doc["condition_contract"]["genre_template"] in NIGHT_GENRES:
                metrics = [c["metric"] for c in doc["condition_contract"]["conditions"]]
                self.assertNotIn("light_window", metrics, oid)

    def test_access_restricted_places_labeled(self):
        ev = load("data/v2/audits/cl-data-53_web_evidence.json")
        for pid in PERMIT_PLACE_IDS:
            row = next(x for x in ev["places"] if x["place_id"] == pid)
            self.assertTrue(row.get("access_restricted"), pid)

    def test_batch_evidence_claim_refs(self):
        ev = load("data/v2/audits/cl-data-53_web_evidence.json")
        self.assertEqual(len(ev["places"]), 40)
        ids = {e["id"] for e in ev["evidence"]}
        for oid in NEW_CONTRACTS:
            doc = load(f"data/v2/opportunities/{oid}.json")
            refs = doc["evidence_claims"][0]["evidence_refs"]
            self.assertTrue(refs and refs[0] in ids, refs)

    def test_seasonal_calendar_windows(self):
        cal = load("data/v2/seasonal-calendar.json")
        have = {e["plant_id"]: e for e in cal["entries"]}
        for sid, win in (("apostle_ice_caves", ("01-01", "03-15")),
                         ("newengland_foliage", ("09-29", "10-27")),
                         ("blueridge_foliage", ("10-10", "11-05")),
                         ("joshua_tree_bloom", ("02-15", "04-30")),
                         ("lastdollar_aspen", ("09-20", "10-10"))):
            self.assertIn(sid, have, sid)
            self.assertEqual(have[sid]["typical_window"],
                             {"start": win[0], "end": win[1]}, sid)


class TestAgli(unittest.TestCase):
    def test_dual_board_records(self):
        fin = load("data/v2/audits/agli/agli-final.json")
        have = {p["place_id"]: p for p in fin["places"]}
        for pid in NEW_IDS:
            self.assertIn(pid, have, pid)
            r = have[pid]
            self.assertLess(r["agli_l"], 90, pid)
            self.assertLess(r["agli_p"], 90, pid)
            self.assertGreater(r["agli_l"], 40, pid)
            self.assertTrue(0 <= r["diversity"] <= 95, pid)
            self.assertTrue(10 <= r["certainty"] <= 90, pid)
        # anchor discipline: an L>75 record must name a global comparandum
        top = max((have[p] for p in NEW_IDS), key=lambda r: r["agli_l"])
        self.assertGreaterEqual(top["agli_l"], 75)
        self.assertIn("anchor_comparandum", top, top["place_id"])
        self.assertEqual(have["us-119"]["anchor_comparandum"], top["anchor_comparandum"])

    def test_access_not_scored(self):
        fin = load("data/v2/audits/agli/agli-final.json")
        have = {p["place_id"]: p for p in fin["places"]}
        for pid in PERMIT_PLACE_IDS:
            self.assertIn("NOT SCORED", have[pid]["derivation_basis"], pid)


class TestRuntime(unittest.TestCase):
    def test_runtime_catalog_counts(self):
        cat = load("runtime_catalog_v004_r4_2.json")
        self.assertEqual(cat["counts"]["spots"], 376)  # re-anchored CL-DATA-64
        self.assertEqual(cat["counts"]["opportunities"], 608)
        us = [s for s in cat["spots"] if s["spot_id"].startswith("us-")]
        self.assertEqual(len(us), 163)  # 96 legacy + 22 CL-DATA-42/43 backfill + 40 new + 5 CL-DATA-64

    def test_manifest_us_counts(self):
        mf = load("runtime_catalog_manifest_r4_2.json")
        self.assertEqual(mf["regions"]["us"]["numeric_id_end"], 163)
        self.assertEqual(mf["regions"]["us"]["counts"]["spots"], 163)
        self.assertEqual(mf["totals"], load("runtime_catalog_v004_r4_2.json")["counts"])

    def test_runtime_dependencies_gaps(self):
        src = open(os.path.join(REPO, "runtime_dependencies.py"), encoding="utf-8").read()
        for oid in ("us-121-P01", "us-138-P01", "us-155-P01"):  # directional_horizon (sunset/overlook)
            self.assertIn(f'"{oid}"', src, oid)
        for oid in ("us-125-P01", "us-149-P02"):  # seasonal_foreground
            self.assertIn(f'"{oid}"', src, oid)

    def test_evaluations_bundle_spliced(self):
        ev = load("apps/web-v2/evaluations-latest.json")
        ids = {p["place_id"] for p in ev["places"]}
        for pid in NEW_IDS:
            self.assertIn(pid, ids, pid)
        self.assertEqual(ev["place_count"], 360)  # merged: 347 on main + 13 CL-DATA-64 places  # re-anchored CL-DATA-64: scoped 168h evals for 13 new places spliced into the 2026-11-09T22:40:40Z bundle
        self.assertEqual(ev["opportunity_count"], 550)  # merged: 537 on main + 13
        self.assertEqual(ev["forecast_hours"], 168)


if __name__ == "__main__":
    unittest.main()
