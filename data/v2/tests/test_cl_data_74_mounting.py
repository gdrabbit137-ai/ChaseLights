"""CL-DATA-74 stage-2 mounting tests: five owner-approved genres mounted on
existing catalog places (17 canonical opportunity docs), the seasonal-calendar
snow/firefly windows, and the curation classifications."""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "evaluate_batch", ROOT / "packages/core-v2/tools/evaluate_batch.py")
eb = importlib.util.module_from_spec(spec)
sys.modules["evaluate_batch"] = eb
spec.loader.exec_module(eb)

OPPS = ROOT / "data/v2/opportunities"

GENRE_MOUNTS = {
    "alpenglow": ["tw-041-P06", "tw-042-P02", "tw-044-P04", "tw-046-P03",
                  "jp-065-P02"],
    "snow_scene": ["tw-019-P07", "tw-120-P02", "tw-093-P03", "jp-065-P03",
                   "us-009-P02"],
    "firefly": ["tw-151-P02", "tw-144-P03"],
    "star_trails": ["tw-024-P06", "tw-140-P03"],
    "moonlit_scene": ["tw-027-P04", "tw-199-P02", "us-121-P02"],
}


class MountDocTests(unittest.TestCase):
    def test_all_17_mounted_docs_exist(self):
        for genre, oids in GENRE_MOUNTS.items():
            for oid in oids:
                path = OPPS / f"{oid}.json"
                self.assertTrue(path.is_file(), f"{oid} missing")
                doc = json.loads(path.read_text(encoding="utf-8"))
                cc = doc["condition_contract"]
                self.assertEqual(cc["genre_template"], genre, oid)
                self.assertEqual(cc["template_version"], f"{genre}-v0.1", oid)
                self.assertEqual(doc["lifecycle_status"], "draft", oid)
                self.assertEqual(doc["revision"], 1, oid)

    def test_place_semantics(self):
        alpenglow_places = {json.loads((OPPS / f"{o}.json").read_text(encoding="utf-8"))["place_id"]
                            for o in GENRE_MOUNTS["alpenglow"]}
        self.assertEqual(alpenglow_places, {"tw-041", "tw-042", "tw-044",
                                            "tw-046", "jp-065"})
        snow_places = {json.loads((OPPS / f"{o}.json").read_text(encoding="utf-8"))["place_id"]
                       for o in GENRE_MOUNTS["snow_scene"]}
        self.assertEqual(snow_places, {"tw-019", "tw-120", "tw-093",
                                       "jp-065", "us-009"})

    def test_conditions_wellformed(self):
        vocab = json.loads((ROOT / "data/v2/templates/metric-vocabulary.json")
                           .read_text(encoding="utf-8"))["metrics"]
        for genre, oids in GENRE_MOUNTS.items():
            for oid in oids:
                doc = json.loads((OPPS / f"{oid}.json").read_text(encoding="utf-8"))
                cids = set()
                for c in doc["condition_contract"]["conditions"]:
                    self.assertIn(c["metric"], vocab, f"{oid}/{c['id']}")
                    self.assertEqual(c["claim_refs"], [f"{oid}-claim-01"], oid)
                    self.assertTrue((c.get("rationale_i18n") or {}).get("zh-TW"), oid)
                    cids.add(c["id"])
                self.assertEqual(len(cids), len(doc["condition_contract"]["conditions"]))

    def test_seasonal_conditions_carry_spot_windows(self):
        for oid in GENRE_MOUNTS["alpenglow"] + GENRE_MOUNTS["snow_scene"] + GENRE_MOUNTS["firefly"]:
            doc = json.loads((OPPS / f"{oid}.json").read_text(encoding="utf-8"))
            seasonal = [c for c in doc["condition_contract"]["conditions"]
                        if c["metric"] == "seasonal_state"]
            self.assertEqual(len(seasonal), 1, oid)
            self.assertIn("例年窗", seasonal[0]["rationale_i18n"]["zh-TW"], oid)

    def test_geometry_and_claims_reuse_sibling_structure(self):
        for genre, oids in GENRE_MOUNTS.items():
            for oid in oids:
                doc = json.loads((OPPS / f"{oid}.json").read_text(encoding="utf-8"))
                self.assertTrue(doc["camera_contexts"], oid)
                self.assertTrue(doc["targets"], oid)
                self.assertTrue(doc["navigation_targets"], oid)
                self.assertTrue(doc["evidence_claims"], oid)
                self.assertEqual(doc["evidence_claims"][0]["claim_id"],
                                 f"{oid}-claim-01", oid)
                # ids must reference THIS opportunity, not the sibling's
                self.assertTrue(doc["camera_contexts"][0]["id"].startswith(f"CZ-{oid}"), oid)


class SeasonalCalendarBridgeTests(unittest.TestCase):
    def setUp(self):
        self.cal = eb.load_seasonal_calendar()

    def test_all_seasonal_mounts_bound(self):
        for oid in (GENRE_MOUNTS["alpenglow"] + GENRE_MOUNTS["snow_scene"]
                    + GENRE_MOUNTS["firefly"]):
            self.assertIn(oid, self.cal, oid)
            entry = self.cal[oid][0]
            self.assertIn(entry["plant_id"], ("snow_season", "firefly_season"), oid)

    def test_snow_season_real_window(self):
        # TW snow season: open mid-winter, closed mid-summer
        self.assertEqual(eb.seasonal_window_verdict(
            self.cal["tw-019-P07"], date(2026, 1, 15))[0], "PASS")
        self.assertEqual(eb.seasonal_window_verdict(
            self.cal["tw-019-P07"], date(2026, 7, 15))[0], "FAIL")
        # Fuji snow line season runs wider (11-15~04-15)
        self.assertEqual(eb.seasonal_window_verdict(
            self.cal["jp-065-P03"], date(2026, 4, 1))[0], "PASS")
        self.assertEqual(eb.seasonal_window_verdict(
            self.cal["jp-065-P03"], date(2026, 6, 1))[0], "FAIL")

    def test_alpenglow_snow_line_window(self):
        self.assertEqual(eb.seasonal_window_verdict(
            self.cal["tw-041-P06"], date(2026, 1, 15))[0], "PASS")
        self.assertEqual(eb.seasonal_window_verdict(
            self.cal["tw-041-P06"], date(2026, 9, 15))[0], "FAIL")

    def test_firefly_season_window(self):
        self.assertEqual(eb.seasonal_window_verdict(
            self.cal["tw-151-P02"], date(2026, 5, 15))[0], "PASS")
        self.assertEqual(eb.seasonal_window_verdict(
            self.cal["tw-151-P02"], date(2026, 7, 1))[0], "FAIL")
        self.assertEqual(eb.seasonal_window_verdict(
            self.cal["tw-144-P03"], date(2026, 6, 14))[0], "PASS")

    def test_no_sourced_live_window_is_fabricated(self):
        # CL-DATA-74 entries ship climatological typical windows only; any
        # current_season without source_url+retrieved_at is ignored
        for oid in (GENRE_MOUNTS["alpenglow"] + GENRE_MOUNTS["snow_scene"]
                    + GENRE_MOUNTS["firefly"]):
            for entry in self.cal[oid]:
                current = entry.get("current_season")
                if current:
                    self.assertTrue(current.get("source_url")
                                    and current.get("retrieved_at"), oid)


class CurationTests(unittest.TestCase):
    def test_curation_covers_all_17(self):
        cur = json.loads((ROOT / "data/v2/indexes/research/curation.json")
                         .read_text(encoding="utf-8"))
        for genre, oids in GENRE_MOUNTS.items():
            for oid in oids:
                a = cur["classifications"][oid]
                self.assertEqual(a["evidence_claim_id"], f"{oid}-claim-01", oid)
                self.assertEqual(a["topic_ids"], [], oid)
                self.assertIn("CL-DATA-74", a["classification_basis"], oid)

    def test_no_duplicate_mount_ids(self):
        all_mounts = [o for oids in GENRE_MOUNTS.values() for o in oids]
        self.assertEqual(len(all_mounts), len(set(all_mounts)))
        # ids must not collide with any existing canonical doc
        on_disk = {p.stem for p in OPPS.glob("*.json")}
        self.assertEqual(len(on_disk), 717 + 17)  # CL-INT-192 merged-tree re-anchor: base 705 -> 717 (CL-DATA-73 misty mounts already in the union tree) + 17 five-genre


class CopyLayerTests(unittest.TestCase):
    def test_genre_short_names_cover_five(self):
        g = json.loads((ROOT / "data/v2/copy/genre_short_names.json")
                       .read_text(encoding="utf-8"))
        for genre in GENRE_MOUNTS:
            self.assertIn(genre, g["genres"], genre)
            for lang in ("zh-TW", "en", "ja"):
                self.assertTrue(g["genres"][genre][lang], genre)

    def test_fail_reason_words_cover_new_metrics(self):
        f = json.loads((ROOT / "data/v2/copy/fail_reason_short.json")
                       .read_text(encoding="utf-8"))
        for metric in ("alpenglow_window", "snow_cover_state", "snowfall",
                       "snow_depth", "clear_streak_hours", "relative_humidity_2m"):
            self.assertIn(metric, f["words"], metric)
            for lang in ("zh-TW", "en", "ja"):
                self.assertTrue(f["words"][metric][lang], metric)


if __name__ == "__main__":
    unittest.main()
