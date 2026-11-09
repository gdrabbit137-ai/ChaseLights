"""CL-DATA-52 — Gemini JP photography list intake (27 places jp-065..jp-091, 29 opportunities).

Owner directive: Japan second-round photography-spot intake (2026-11-09), GROWTH-ONLY
PM-judgment admission per the CL-DATA-51 flow; 5km geo dedupe (CL-DATA-25 institution,
subject-differentiation overrides documented); web-verified coordinates/elevations/seasons
with source URLs in data/v2/audits/cl-data-52_web_evidence.json.

Pins:
- regions.py jp list grows to 91 ids (jp-050 retired stays retired; no removals);
- every new contract schema-validates, unique condition ids, batch evidence ref e-d52-web-<slug>;
- all-day subjects carry a civil light-window; night subjects carry NO light_window;
- jp-078-P01 (潮汐限定 sky-mirror) carries the honest legacy_tide not_evaluatable gate
  (CL-DATA-20 tidal semantics) — no fabricated weather-only contract;
- seasonal windows present in seasonal-calendar.json (11 entries);
- AGLI v2 dual-board records in agli-final.json (L/P, zero 90+, anchor comparandum for L>75);
- runtime catalog counts, manifest jp counts (numeric_id_end 91), runtime-deps gap sets.
"""
import json
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "specs", "v2", "tests"))

import regions  # noqa: E402

NEW_IDS = [f"jp-{n:03d}" for n in range(65, 92)]
NEW_CONTRACTS = [f"jp-{n:03d}-P01" for n in range(65, 92)] + ["jp-068-P02", "jp-087-P02"]
ALL_DAY_GENRES = {"overlook", "reflection", "mountain_view", "cloud_sea",
                  "geological_landform", "waterfall", "blue_hour_city"}
NIGHT_GENRES = {"night_sky", "city_night"}
DEDUPE_OVERRIDES = {"jp-067", "jp-076"}  # sub-5km with documented subject-disjoint overrides


def load(p):
    with open(os.path.join(REPO, p), encoding="utf-8") as f:
        return json.load(f)


class TestRegions(unittest.TestCase):
    def test_jp_catalog_grew(self):
        spots = regions.get_spots("jp")
        self.assertEqual(len(spots), 91)
        names = [s["name_i18n"]["zh-TW"] for s in spots]
        self.assertIn("富士山頂（剣ヶ峰）", names)
        self.assertEqual(names[-1], "屋久島白谷雲水峽")  # jp-091

    def test_new_admin_areas(self):
        for pid in NEW_IDS:
            self.assertIn(pid, regions.JP_ADMIN_AREAS)

    def test_coordinate_overrides_web_verified(self):
        for spot in regions.get_spots("jp"):
            if spot["spot_id"] in NEW_IDS:
                self.assertIn("CL-DATA-52", spot.get("coordinate_source", ""), spot["spot_id"])

    def test_elevation_overrides_or_honest_unknown(self):
        self.assertEqual(regions.ELEVATION_OVERRIDES.get("富士山頂"), 3776)
        self.assertEqual(regions.ELEVATION_OVERRIDES.get("大淵笹場"), None)  # honest unknown


class TestDedupe(unittest.TestCase):
    def test_dedupe_registry_and_distances(self):
        reg = load("data/v2/audits/discovery/cl-data-52-dedupe.json")
        self.assertTrue(set(reg).issuperset(set(NEW_IDS)), reg.keys())
        internal = reg.get("_internal", [])
        self.assertEqual([r["pair"] for r in internal], [["jp-065", "jp-066"]])
        for pid in NEW_IDS:
            row = reg[pid]
            if row["km"] < 5.0:
                self.assertIn(pid, DEDUPE_OVERRIDES, f"{pid} sub-5km without documented override")
                self.assertIn("override", row)
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

    def test_no_night_subjects_without_darkness_window(self):
        for oid in NEW_CONTRACTS:
            doc = load(f"data/v2/opportunities/{oid}.json")
            if doc["condition_contract"]["genre_template"] in NIGHT_GENRES:
                metrics = [c["metric"] for c in doc["condition_contract"]["conditions"]]
                self.assertNotIn("light_window", metrics, oid)

    def test_tidal_subject_honest_gate(self):
        doc = load("data/v2/opportunities/jp-078-P01.json")
        metrics = [c["metric"] for c in doc["condition_contract"]["conditions"]]
        self.assertIn("legacy_tide", metrics)  # CL-DATA-20 tidal semantics

    def test_batch_evidence_claim_refs(self):
        ev = load("data/v2/audits/cl-data-52_web_evidence.json")
        self.assertEqual(len(ev["places"]), 27)
        ids = {e["id"] for e in ev["evidence"]}
        for oid in NEW_CONTRACTS:
            doc = load(f"data/v2/opportunities/{oid}.json")
            refs = doc["evidence_claims"][0]["evidence_refs"]
            self.assertTrue(refs and refs[0] in ids, refs)

    def test_seasonal_calendar_windows(self):
        cal = load("data/v2/seasonal-calendar.json")
        have = {e["plant_id"]: e for e in cal["entries"]}
        for sid, win in (("tateyama_snowwall", ("04-20", "05-31")),
                         ("tsubonuma_shoya", ("10-15", "10-31")),
                         ("shirakawa_lightup", ("01-15", "02-28")),
                         ("nemophila", ("04-20", "05-15")),
                         ("kochia_red", ("10-01", "10-31")),
                         ("diamond_fuji_tanuki", ("04-10", "04-25"))):
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
        self.assertEqual(have["jp-065"]["anchor_comparandum"], top["anchor_comparandum"])


class TestRuntime(unittest.TestCase):
    def test_runtime_catalog_counts(self):
        cat = load("runtime_catalog_v004_r4_2.json")
        self.assertEqual(cat["counts"]["spots"], 363)  # re-anchored CL-DATA-53
        self.assertEqual(cat["counts"]["opportunities"], 595)
        jp = [s for s in cat["spots"] if s["spot_id"].startswith("jp-")]
        self.assertEqual(len(jp), 90)  # jp-050 retired

    def test_manifest_jp_counts(self):
        mf = load("runtime_catalog_manifest_r4_2.json")
        self.assertEqual(mf["regions"]["jp"]["numeric_id_end"], 91)
        self.assertEqual(mf["regions"]["jp"]["counts"]["spots"], 90)
        self.assertEqual(mf["totals"], load("runtime_catalog_v004_r4_2.json")["counts"])

    def test_runtime_dependencies_gaps(self):
        src = open(os.path.join(REPO, "runtime_dependencies.py"), encoding="utf-8").read()
        for oid in ("jp-073-P01", "jp-074-P01", "jp-075-P01"):  # cloud_sea batch
            self.assertIn(f'"{oid}"', src, oid)
        for oid in ("jp-037-P02", "jp-041-P02", "jp-045-P01", "jp-080-P01"):  # directional_horizon (sunrise/sunset/overlook)
            self.assertIn(f'"{oid}"', src, oid)
        for oid in ("jp-087-P01", "jp-087-P02"):  # seasonal_foreground
            self.assertIn(f'"{oid}"', src, oid)

    def test_evaluations_bundle_spliced(self):
        ev = load("apps/web-v2/evaluations-latest.json")
        ids = {p["place_id"] for p in ev["places"]}
        for pid in NEW_IDS:
            self.assertIn(pid, ids, pid)
        self.assertEqual(ev["place_count"], 350)  # re-anchored CL-DATA-53
        self.assertEqual(ev["opportunity_count"], 545)


if __name__ == "__main__":
    unittest.main()
