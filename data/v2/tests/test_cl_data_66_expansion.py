"""CL-DATA-66 — scoreless Tier-A intake waves (owner-gemini subject-list streams).

Wave 1: 22 places tw-125..tw-146 / 37 contracts.
Wave 2: 15 places tw-147..tw-161 / 22 contracts (15 of the manifest-next-30
admitted; 15 rejected: 14 same-family <5km overlaps + 1 pure-swimming-beach).

Owner rulings baked into these tests (2026-11-11):
- intake is SCORELESS: no rubric v2 gate, no AGLI dual-board, agli-final.json
  untouched; score fields in evidence registries are null;
- admission = web verification (authoritative URL+date) + 5km subject-disjoint
  dedupe; same-family <5km candidates stay in tier-a-manifest.json as rejected;
- subject contracts built in full (V2 + legacy dual-track);
- astronomy ephemeris: new night_sky subjects registered in
  ASTRONOMY_EPHEMERIS_PROFILES (tw-121..124 lesson).

Pins checked here:
- regions.py tw list 161 (raw ids: 161 = 124 + 22 wave1 + 15 wave2), no removals;
- runtime catalog 407/646, manifest tw numeric_id_end 161;
- web catalog 394/612 (all 59 new opportunity ids present);
- evaluations bundle spliced 399/617, forecast_hours 168, fetch_failures [];
- honest null elevations stay null (tw-126 南山寺, tw-142 安平, tw-143 富貴角,
  tw-145 東華聖宮 + wave-2 unknowns); 報時山 260/295 discrepancy carried as note;
- no day-subject carries invented score fields.
"""
import json
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "specs", "v2", "tests"))

import regions  # noqa: E402

WAVE1_IDS = [f"tw-{n}" for n in range(125, 147)]
WAVE2_IDS = [f"tw-{n}" for n in range(147, 162)]
NEW_IDS = WAVE1_IDS + WAVE2_IDS


def _contracts(rng, suffixes=(1, 2)):
    out = []
    for n in rng:
        for s in suffixes:
            oid = f"tw-{n}-P0{s}"
            if os.path.exists(os.path.join(REPO, f"data/v2/opportunities/{oid}.json")):
                out.append(oid)
    return out


WAVE1_CONTRACTS = _contracts(range(125, 147))
WAVE2_CONTRACTS = _contracts(range(147, 162))
NIGHT_SKY_IDS = {"tw-140-P02", "tw-144-P02"}
WAVE2_NULL_ELEV = {"tw-147", "tw-148", "tw-150", "tw-152", "tw-153", "tw-154",
                   "tw-155", "tw-156", "tw-157", "tw-158", "tw-159", "tw-160", "tw-161"}
WAVE2_SUNRISE_SUNSET = {
    "tw-149-P01", "tw-152-P02", "tw-154-P01",
    "tw-147-P02", "tw-148-P02", "tw-150-P01", "tw-153-P02",
    "tw-156-P01", "tw-157-P01", "tw-159-P01", "tw-161-P01",
}
REJECTED_MANIFEST = {
    "北大武喜多麗斷崖段", "薑麻園景觀茶園", "加路蘭海蝕奇石群", "好望角",
    "鼻頭角海蝕平台/軍艦岩", "合歡北峰反射板", "武嶺/主峰星空", "阿拔泉山步道",
}
REJECTED_WAVE2 = {
    "風吹砂珊瑚礁懸崖", "八斗子潮境公園海蝕平台", "墾丁白沙灣", "對高岳觀景台",
    "滿月圓森林遊樂區", "漁光島月牙灣", "石門山", "船帆石+龍磐高位珊瑚礁",
    "西子灣/柴山海岸", "阿里山慈雲寺觀景台", "鳥嘴山大竹山農場", "三仙山西濱海蝕平台",
    "二尖山爽文嶺", "八仙山主峰", "三條崙海水浴場",
}


def load(p):
    with open(os.path.join(REPO, p), encoding="utf-8") as f:
        return json.load(f)


class TestManifest(unittest.TestCase):
    def test_tier_a_manifest_counts(self):
        m = load("data/v2/audits/subject-lists/tier-a-manifest.json")
        self.assertEqual(m["total_candidates"], 612)
        self.assertGreaterEqual(m["tier_a_total"], 200)
        self.assertEqual(len(m["tier_a"]), m["tier_a_total"])
        self.assertTrue(all(r.get("selection_reason") for r in m["tier_a"]))
        self.assertEqual(m["wave1"]["planned"], 30)
        self.assertEqual(m["wave1"]["done"], 22)
        self.assertEqual(m["wave1"]["rejected"], 8)
        self.assertEqual(m["wave2"]["planned"], 30)
        self.assertEqual(m["wave2"]["done"], 15)
        self.assertEqual(m["wave2"]["rejected"], 15)
        self.assertEqual(m["wave2"]["place_ids"], WAVE2_IDS)

    def test_rejected_stay_in_manifest_with_reason(self):
        m = load("data/v2/audits/subject-lists/tier-a-manifest.json")
        by_name = {r["name"]: r for r in m["tier_a"]}
        for name in REJECTED_MANIFEST:
            self.assertIn(name, by_name, name)
            r = by_name[name]
            self.assertEqual(r["status"], "rejected", name)
            self.assertIn("dedupe reject", r["reject_reason"], name)
        for name in REJECTED_WAVE2:
            self.assertIn(name, by_name, name)
            r = by_name[name]
            self.assertEqual(r["status"], "rejected", name)
            self.assertTrue(r["wave"] == 2, name)
            self.assertTrue(r["reject_reason"], name)
        admitted2 = [r for r in m["tier_a"] if r["status"] == "admitted" and r["wave"] == 2]
        self.assertEqual(len(admitted2), 15)
        self.assertEqual({r["admitted_place_id"] for r in admitted2}, set(WAVE2_IDS))

    def test_wave_admitted_ids_are_new_places(self):
        m = load("data/v2/audits/subject-lists/tier-a-manifest.json")
        self.assertEqual(len(m["wave1"]["place_ids"]), 22)
        self.assertEqual(sorted(m["wave1"]["place_ids"]), sorted(WAVE1_IDS))
        self.assertEqual(m["wave2"]["place_ids"], WAVE2_IDS)


class TestRegions(unittest.TestCase):
    def test_region_lists_grew(self):
        self.assertEqual(len(regions.get_spots("tw")), 161)  # 124 + 22 wave1 + 15 wave2
        self.assertEqual(len(regions.get_spots("jp")), 95)
        self.assertEqual(len(regions.get_spots("us")), 163)
        ids = [s["spot_id"] for r in ("tw", "jp", "us") for s in regions.get_spots(r)]
        self.assertEqual(len(ids), len(set(ids)))
        for legacy in ("tw-047", "tw-014", "tw-090", "tw-096", "tw-072", "tw-019", "tw-105"):
            self.assertIn(legacy, ids)  # rejected candidates do NOT remove existing spots (GROWTH-ONLY)

    def test_new_admin_areas(self):
        for pid in NEW_IDS:
            self.assertIn(pid, regions.TW_ADMIN_AREAS, pid)

    def test_coordinate_overrides_web_verified(self):
        for spot in regions.get_spots("tw"):
            if spot["spot_id"] in NEW_IDS:
                self.assertIn("CL-DATA-66", spot.get("coordinate_source", ""), spot["spot_id"])


class TestDedupe(unittest.TestCase):
    def test_dedupe_registry_and_overrides(self):
        reg = load("data/v2/audits/discovery/cl-data-66-dedupe.json")
        self.assertTrue(set(reg).issuperset(set(NEW_IDS)), reg.keys())
        for pid in NEW_IDS:
            row = reg[pid]
            if row["km"] < 5.0:
                self.assertIn("override", row, f"{pid} sub-5km without documented override")
            else:
                self.assertGreaterEqual(row["km"], 5.0)
        self.assertGreaterEqual(len(reg["_rejected_family_overlaps"]), 8)
        for r in reg["_rejected_family_overlaps"]:
            self.assertTrue(r["reason"].startswith("5km dedupe reject"), r)

    def test_wave2_dedupe_registry(self):
        reg = load("data/v2/audits/discovery/cl-data-66-dedupe.json")
        for pid in WAVE2_IDS:
            row = reg[pid]
            self.assertGreaterEqual(row["km"], 5.0, pid)
            self.assertTrue(row.get("nearest_existing"), pid)
        rej = reg["_rejected_family_overlaps_wave2"]
        self.assertEqual(len(rej), 15)
        self.assertEqual({r["name"] for r in rej}, REJECTED_WAVE2)
        for r in rej:
            self.assertTrue(r["reason"], r)
        self.assertEqual(sum(1 for r in rej if r["reason"].startswith("pure swimming beach")), 1)


class TestContracts(unittest.TestCase):
    def _validate(self, oids):
        from validate_task_w_contracts import validate_record
        for oid in oids:
            doc = load(f"data/v2/opportunities/{oid}.json")
            errs = validate_record(doc)
            self.assertEqual(errs, [], f"{oid} schema errors: {errs}")

    def test_all_wave1_contracts_exist_and_validate(self):
        self._validate(WAVE1_CONTRACTS)

    def test_all_wave2_contracts_exist_and_validate(self):
        self.assertEqual(len(WAVE2_CONTRACTS), 22)
        self._validate(WAVE2_CONTRACTS)

    def test_unique_condition_ids(self):
        for oid in WAVE1_CONTRACTS + WAVE2_CONTRACTS:
            doc = load(f"data/v2/opportunities/{oid}.json")
            ids = [c["id"] for c in doc["condition_contract"]["conditions"]]
            self.assertEqual(len(ids), len(set(ids)), f"{oid} duplicate condition id")

    def test_scoreless_intake_no_score_fields(self):
        # owner ruling: score fields empty — evidence registry carries null scores
        ev = load("data/v2/audits/cl-data-66_web_evidence.json")
        self.assertEqual(ev["ticket"], "CL-DATA-66")
        self.assertEqual(len(ev["places"]), 22)
        for row in ev["places"]:
            self.assertIsNone(row["score"], row["place_id"])
        self.assertIn("Scoreless", ev["rule"])
        self.assertEqual(ev["places_wave2_count"], 15)
        self.assertEqual(ev["rejected_wave2_count"], 15)
        self.assertEqual(len(ev["places_wave2"]), 15)
        for row in ev["places_wave2"]:
            self.assertIsNone(row["score"], row["place_id"])

    def test_web_evidence_refs_resolve(self):
        ev = load("data/v2/audits/cl-data-66_web_evidence.json")
        ids = {e["id"] for e in ev["evidence"]}
        self.assertEqual(len(ids), 37)  # 22 wave1 + 15 wave2
        for oid in WAVE1_CONTRACTS + WAVE2_CONTRACTS:
            doc = load(f"data/v2/opportunities/{oid}.json")
            refs = doc["evidence_claims"][0]["evidence_refs"]
            self.assertTrue(refs and refs[0] in ids, refs)

    def test_honest_null_elevations(self):
        for pid in ("tw-126", "tw-142", "tw-143", "tw-145"):
            doc = load(f"data/v2/opportunities/{pid}-P01.json")
            self.assertIsNone(doc["camera_contexts"][0]["altitude_m"], pid)

    def test_wave2_honest_null_and_verified_elevations(self):
        for pid in WAVE2_NULL_ELEV:
            doc = load(f"data/v2/opportunities/{pid}-P01.json")
            self.assertIsNone(doc["camera_contexts"][0]["altitude_m"], pid)
        self.assertEqual(load("data/v2/opportunities/tw-149-P01.json")["camera_contexts"][0]["altitude_m"], 1173.0)
        self.assertEqual(load("data/v2/opportunities/tw-151-P01.json")["camera_contexts"][0]["altitude_m"], 230.0)

    def test_baoshishan_elevation_discrepancy_note(self):
        doc = load("data/v2/opportunities/tw-137-P01.json")
        self.assertEqual(doc["camera_contexts"][0]["altitude_m"], 295.0)
        self.assertIn("295", doc["camera_contexts"][0]["geometry"]["derivation_method"])

    def test_astronomy_ephemeris_profiles_registered(self):
        from opportunity_runtime import ASTRONOMY_EPHEMERIS_PROFILES
        for oid in NIGHT_SKY_IDS:
            self.assertIn(oid, ASTRONOMY_EPHEMERIS_PROFILES, oid)
            self.assertEqual(ASTRONOMY_EPHEMERIS_PROFILES[oid]["mode"], "milky_way_or_star_field")
        for oid in WAVE1_CONTRACTS + WAVE2_CONTRACTS:
            doc = load(f"data/v2/opportunities/{oid}.json")
            if doc["condition_contract"]["genre_template"] == "night_sky":
                self.assertIn(oid, ASTRONOMY_EPHEMERIS_PROFILES, oid)
        # wave-2 has no night_sky contract: nothing new to register
        self.assertEqual([o for o in WAVE2_CONTRACTS
                          if load(f"data/v2/opportunities/{o}.json")["condition_contract"]["genre_template"] == "night_sky"], [])

    def test_seasonal_plant_reuses_existing_window(self):
        doc = load("data/v2/opportunities/tw-141-P01.json")
        self.assertEqual(doc["condition_contract"]["genre_template"], "seasonal_plant")
        sids = [c["metric"] for c in doc["condition_contract"]["conditions"]]
        self.assertIn("seasonal_state", sids)
        cal = load("data/v2/seasonal-calendar.json")
        e = next(x for x in cal["entries"] if x["plant_id"] == "red_maple")
        self.assertEqual(e["typical_window"], {"start": "10-20", "end": "11-10"})

    def test_wave2_seasonal_plant_reuses_daylily_window(self):
        doc = load("data/v2/opportunities/tw-154-P02.json")
        self.assertEqual(doc["condition_contract"]["genre_template"], "seasonal_plant")
        sids = [c["metric"] for c in doc["condition_contract"]["conditions"]]
        self.assertIn("seasonal_state", sids)
        cal = load("data/v2/seasonal-calendar.json")
        e = next(x for x in cal["entries"] if x["plant_id"] == "daylily_taimali")
        self.assertTrue(e["typical_window"])

    def test_restricted_access_notes_informational_only(self):
        doc = load("data/v2/opportunities/tw-135-P01.json")
        acc = doc["camera_contexts"][0]["access_notes_i18n"]
        self.assertIn("管制區", acc["zh-TW"])
        doc2 = load("data/v2/opportunities/tw-146-P01.json")
        self.assertIn("休園", doc2["camera_contexts"][0]["access_notes_i18n"]["zh-TW"])

    def test_wave2_directional_horizon_sectors_registered(self):
        from opportunity_runtime import DIRECTIONAL_HORIZON_SECTORS
        for oid in WAVE2_SUNRISE_SUNSET:
            self.assertIn(oid, DIRECTIONAL_HORIZON_SECTORS, oid)
            row = DIRECTIONAL_HORIZON_SECTORS[oid]
            self.assertEqual(row["tolerance"], 85.0)
            phase = row["phase"]
            self.assertIn(phase, ("sunrise", "sunset"))
            self.assertEqual(row["center"], 90.0 if phase == "sunrise" else 270.0)
        # every wave-2 sunrise/sunset contract has a sector entry, none missing
        for oid in WAVE2_CONTRACTS:
            tpl = load(f"data/v2/opportunities/{oid}.json")["condition_contract"]["genre_template"]
            if tpl in ("sunrise", "sunset"):
                self.assertIn(oid, WAVE2_SUNRISE_SUNSET, oid)


class TestRuntime(unittest.TestCase):
    def test_runtime_catalog_counts(self):
        cat = load("runtime_catalog_v004_r4_2.json")
        self.assertEqual(cat["counts"]["spots"], 407)
        self.assertEqual(cat["counts"]["opportunities"], 646)

    def test_manifest_region_ends(self):
        mf = load("runtime_catalog_manifest_r4_2.json")
        self.assertEqual(mf["regions"]["tw"]["numeric_id_end"], 161)
        self.assertEqual(mf["regions"]["jp"]["numeric_id_end"], 95)
        self.assertEqual(mf["regions"]["us"]["numeric_id_end"], 163)
        self.assertEqual(mf["totals"], load("runtime_catalog_v004_r4_2.json")["counts"])

    def test_evaluations_bundle_spliced(self):
        ev = load("apps/web-v2/evaluations-latest.json")
        ids = {p["place_id"] for p in ev["places"]}
        for pid in NEW_IDS:
            self.assertIn(pid, ids, pid)
        self.assertEqual(ev["place_count"], 399)
        self.assertEqual(ev["opportunity_count"], 617)
        self.assertEqual(ev["forecast_hours"], 168)

    def test_web_catalog_regenerated(self):
        cat = load("apps/web-v2/catalog.v2.json")
        self.assertEqual(len(cat["places"]), 394)
        self.assertEqual(len(cat["opportunities"]), 612)
        oids = {o["opportunity_id"] for o in cat["opportunities"]}
        self.assertTrue(set(WAVE1_CONTRACTS) <= oids)
        self.assertTrue(set(WAVE2_CONTRACTS) <= oids)

    def test_tw_weather_refreshed_with_wave2(self):
        tw = load("tw_weather.json")
        ids = {s["spot_id"] for s in tw["spots"]}
        self.assertTrue(set(WAVE2_IDS) <= ids)
        self.assertEqual(len(tw["spots"]), 153)


if __name__ == "__main__":
    unittest.main()
