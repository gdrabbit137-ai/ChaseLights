"""CL-DATA-64 — new-subject-family intake (13 places: tw-121..124 Matsu blue tears,
us-159..160 Yellowstone geothermal, jp-092..095 geothermal/hells, us-161..163 Kilauea lava).

Owner directive: three new subject families (2026-11-10), GROWTH-ONLY PM-judgment
admission per the CL-DATA-51/52/53 flow; 5km geo dedupe with subject-disjoint
overrides documented in data/v2/audits/discovery/cl-data-64-dedupe.json; web-verified
coordinates/elevations with authoritative URLs+dates in
data/v2/audits/cl-data-64_web_evidence.json (查無權威源之海拔誠實留空 null).

Owner-confirmed new semantics (CL-DATA-64):
- viewpoint/subject separation expressed with contract-native fields
  (camera_context=觀點, target=subject, observation_relations.distance_m) — the
  W1-pinned opportunity schema gates top-level additions (additionalProperties false);
- REQUIRED volcanic_activity condition (enum erupting/lava-lake/low/dormant,
  operator in, threshold ["erupting","lava-lake"]) on lava subjects, bound to
  USGS HVO current status — feed pending, honest UNKNOWN (fail-closed);
- geothermal color honesty: midday top-light optimum recorded (opposite of golden hour);
- blue tears noctiluca concentration NOT forecastable — REQUIRED honest
  not_evaluatable + moon/cloud gates; seasonal window 04-01..09-30 (official).

Pins:
- regions.py tw/jp/us lists grow to 124/95/163 (no removals);
- every new contract schema-validates (both repo and W1-pinned validators), unique
  condition ids, evidence ref e-d64-web-<slug>;
- night subjects carry NO daylight light_window;
- reservation/boardwalk/eruption-closure access restrictions recorded, NOT scored;
- seasonal-calendar matsu_blue_tears entry (04-01..09-30, official peak 4-6月 note);
- AGLI v2 dual-board records in agli-final.json (zero 90+, anchor comparandum for L>=75);
- runtime catalog counts, manifest region ends (tw 124 / jp 95 / us 163),
  evaluations bundle spliced 366/562.
"""
import json
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "specs", "v2", "tests"))

import regions  # noqa: E402

NEW_IDS = ["tw-121", "tw-122", "tw-123", "tw-124",
           "us-159", "us-160", "jp-092", "jp-093", "jp-094", "jp-095",
           "us-161", "us-162", "us-163"]
NEW_CONTRACTS = [f"{p}-P01" for p in NEW_IDS]
NIGHT_GENRES = {"blue_tears", "volcanic_glow"}
SEPARATION_IDS = {"us-161", "us-163"}  # viewpoint != subject, distance recorded
LAVA_OIDS = {"us-161-P01"}
ACCESS_RESTRICTED = {"tw-122", "us-160", "us-161"}


def load(p):
    with open(os.path.join(REPO, p), encoding="utf-8") as f:
        return json.load(f)


class TestRegions(unittest.TestCase):
    def test_region_lists_grew(self):
        self.assertEqual(len(regions.get_spots("tw")), 227)  # raw regions.py ids: 124 + 103 CL-DATA-66 wave1-7 (retired stay raw; runtime catalog excludes)
        self.assertEqual(len(regions.get_spots("jp")), 95)  # raw regions.py ids
        self.assertEqual(len(regions.get_spots("us")), 163)  # raw regions.py ids
        ids = [s["spot_id"] for r in ("tw", "jp", "us") for s in regions.get_spots(r)]
        self.assertEqual(len(ids), len(set(ids)))
        for legacy in ("tw-065", "tw-066", "tw-067", "us-010", "us-112", "jp-090", "jp-091"):
            self.assertIn(legacy, ids)  # near-duplicate candidates STAY (GROWTH-ONLY)

    def test_new_admin_areas(self):
        for pid in NEW_IDS:
            table = getattr(regions, f"{pid.split('-')[0].upper()}_ADMIN_AREAS")
            self.assertIn(pid, table, pid)

    def test_coordinate_overrides_web_verified(self):
        for r in ("tw", "jp", "us"):
            for spot in regions.get_spots(r):
                if spot["spot_id"] in NEW_IDS:
                    self.assertIn("CL-DATA-64", spot.get("coordinate_source", ""), spot["spot_id"])


class TestDedupe(unittest.TestCase):
    def test_dedupe_registry_and_overrides(self):
        reg = load("data/v2/audits/discovery/cl-data-64-dedupe.json")
        self.assertTrue(set(reg).issuperset(set(NEW_IDS)), reg.keys())
        for pid in NEW_IDS:
            row = reg[pid]
            if row["km"] < 5.0:
                self.assertIn("override", row, f"{pid} sub-5km without documented override")
        self.assertIn("_internal", reg)
        self.assertTrue(all("reason" in r for r in reg["_internal"]))


class TestContracts(unittest.TestCase):
    def test_all_batch_contracts_exist_and_validate(self):
        from validate_task_w_contracts import validate_record
        for oid in NEW_CONTRACTS:
            doc = load(f"data/v2/opportunities/{oid}.json")
            errs = validate_record(doc)
            self.assertEqual(errs, [], f"{oid} schema errors: {errs}")

    def test_unique_condition_ids(self):
        for oid in NEW_CONTRACTS:
            doc = load(f"data/v2/opportunities/{oid}.json")
            ids = [c["id"] for c in doc["condition_contract"]["conditions"]]
            self.assertEqual(len(ids), len(set(ids)), f"{oid} duplicate condition id")

    def test_night_subjects_carry_no_daylight_light_window(self):
        for oid in NEW_CONTRACTS:
            doc = load(f"data/v2/opportunities/{oid}.json")
            if doc["condition_contract"]["genre_template"] in NIGHT_GENRES:
                metrics = [c["metric"] for c in doc["condition_contract"]["conditions"]]
                self.assertNotIn("light_window", metrics, oid)

    def test_volcanic_activity_required_on_lava_subjects(self):
        for oid in LAVA_OIDS:
            doc = load(f"data/v2/opportunities/{oid}.json")
            va = [c for c in doc["condition_contract"]["conditions"]
                  if c["metric"] == "volcanic_activity"]
            self.assertTrue(va, oid)
            c = va[0]
            self.assertEqual(c["role"], "REQUIRED")
            self.assertEqual(c["domain"], "SUBJECT_STATE")
            self.assertEqual(c["operator"], "in")
            self.assertEqual(c["threshold"], ["erupting", "lava-lake"])
            self.assertIn("usgs_hvo", c["model_binding"])
            self.assertIn("USGS HVO", c["rationale_i18n"]["en"])

    def test_blue_tears_noctiluca_honest_not_evaluatable(self):
        for pid in ("tw-121", "tw-122", "tw-123", "tw-124"):
            doc = load(f"data/v2/opportunities/{pid}-P01.json")
            nc = [c for c in doc["condition_contract"]["conditions"]
                  if c["metric"] == "noctiluca_concentration"]
            self.assertTrue(nc, pid)
            self.assertEqual(nc[0]["role"], "REQUIRED")
            self.assertIsNone(nc[0]["model_binding"])
            self.assertIn("not_evaluatable", nc[0]["rationale_i18n"]["zh-TW"])

    def test_geothermal_midday_color_honesty(self):
        for pid in ("us-159", "us-160", "jp-092", "jp-093", "jp-094"):
            doc = load(f"data/v2/opportunities/{pid}-P01.json")
            gh = [c for c in doc["condition_contract"]["conditions"]
                  if c["metric"] == "golden_hour_window"]
            self.assertTrue(gh, pid)
            self.assertIn("midday", gh[0]["notes_i18n"]["en"].lower())

    def test_viewpoint_subject_separation_native_fields(self):
        for pid in SEPARATION_IDS:
            doc = load(f"data/v2/opportunities/{pid}-P01.json")
            cam = doc["camera_contexts"][0]["geometry"]["geojson"]["coordinates"]
            tgt = doc["targets"][0]["geometry"]["geojson"]["coordinates"]
            vr = doc["observation_relations"][0]
            self.assertNotEqual(cam, tgt, pid)
            self.assertIsInstance(vr["distance_m"], (int, float))
            self.assertGreater(vr["distance_m"], 0)
            self.assertIsNotNone(vr["derivation_method"])

    def test_evidence_claim_refs_and_access_labels(self):
        ev = load("data/v2/audits/cl-data-64_web_evidence.json")
        self.assertEqual(len(ev["places"]), 13)
        ids = {e["id"] for e in ev["evidence"]}
        for oid in NEW_CONTRACTS:
            doc = load(f"data/v2/opportunities/{oid}.json")
            refs = doc["evidence_claims"][0]["evidence_refs"]
            self.assertTrue(refs and refs[0] in ids, refs)
        for pid in ACCESS_RESTRICTED:
            row = next(x for x in ev["places"] if x["place_id"] == pid)
            self.assertTrue(row.get("access_restricted"), pid)

    def test_unverified_elevations_left_null(self):
        # jp-092/jp-093 (hells) have no verified elevation - honest nulls
        for pid in ("jp-092", "jp-093"):
            doc = load(f"data/v2/opportunities/{pid}-P01.json")
            self.assertIsNone(doc["camera_contexts"][0]["altitude_m"], pid)

    def test_seasonal_calendar_window(self):
        cal = load("data/v2/seasonal-calendar.json")
        e = next(x for x in cal["entries"] if x["plant_id"] == "matsu_blue_tears")
        self.assertEqual(e["typical_window"], {"start": "04-01", "end": "09-30"})
        self.assertIn("matsu-nsa.gov.tw", e["sources"][0]["url"])


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
        top = max((have[p] for p in NEW_IDS), key=lambda r: r["agli_l"])
        self.assertGreaterEqual(top["agli_l"], 75)
        self.assertIn("anchor_comparandum", top, top["place_id"])

    def test_access_not_scored(self):
        fin = load("data/v2/audits/agli/agli-final.json")
        have = {p["place_id"]: p for p in fin["places"]}
        for pid in ACCESS_RESTRICTED:
            self.assertIn("NOT SCORED", have[pid]["derivation_basis"], pid)


class TestRuntime(unittest.TestCase):
    def test_runtime_catalog_counts(self):
        cat = load("runtime_catalog_v004_r4_2.json")
        self.assertEqual(cat["counts"]["spots"], 473)
        self.assertEqual(cat["counts"]["opportunities"], 726)

    def test_manifest_region_ends(self):
        mf = load("runtime_catalog_manifest_r4_2.json")
        self.assertEqual(mf["regions"]["tw"]["numeric_id_end"], 227)
        self.assertEqual(mf["regions"]["jp"]["numeric_id_end"], 95)
        self.assertEqual(mf["regions"]["us"]["numeric_id_end"], 163)
        self.assertEqual(mf["totals"], load("runtime_catalog_v004_r4_2.json")["counts"])

    def test_evaluations_bundle_spliced(self):
        ev = load("apps/web-v2/evaluations-latest.json")
        ids = {p["place_id"] for p in ev["places"]}
        for pid in NEW_IDS:
            self.assertIn(pid, ids, pid)
        self.assertEqual(ev["place_count"], 465)
        self.assertEqual(ev["opportunity_count"], 697)
        self.assertEqual(ev["forecast_hours"], 168)
        self.assertEqual(ev["fetch_failures"], [])

    def test_web_catalog_regenerated(self):
        cat = load("apps/web-v2/catalog.v2.json")
        self.assertEqual(len(cat["places"]), 460)  # CL-DATA-66 wave7 re-anchor: 460 places
        self.assertEqual(len(cat["opportunities"]), 692)  # CL-DATA-66 wave1-7 re-anchor (86 places / 132 contracts)
        oids = {o["opportunity_id"] for o in cat["opportunities"]}
        self.assertTrue(set(NEW_CONTRACTS) <= oids)


if __name__ == "__main__":
    unittest.main()
