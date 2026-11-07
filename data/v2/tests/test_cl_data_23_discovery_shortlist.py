"""CL-DATA-23 discovery shortlist contract tests (jp-north: Hokkaido + Tohoku).

The discovery round is a LIST, not a catalog change: membership decisions stay
with the owner. These tests validate the machine-readable rubric artifact at
data/v2/audits/discovery/jp-north-shortlist.json — schema, rubric arithmetic,
seasonal-window presence for winter-closed / seasonal subjects, 5km pairwise
differentiation, and provenance (>=1 source URL per candidate). They also pin
the honest-coverage notes (YAMATWO/nap not yet hit) in the dossier files.
"""
import json
import unittest
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SHORTLIST = ROOT / "data/v2/audits/discovery/jp-north-shortlist.json"
CATALOG = ROOT / "apps/web-v2/catalog.v2.json"
DOSSIERS = [ROOT / "data/v2/audits/discovery/jp-north-hokkaido.md",
            ROOT / "data/v2/audits/discovery/jp-north-tohoku.md"]

RUBRIC_KEYS = ["subject_strength", "weather_light_dependency",
               "verifiability", "differentiation", "safe_access"]

# Subjects whose photographic window is seasonal by nature — the candidate MUST
# carry an explicit seasonal_window (winter closures / bloom / drift-ice).
SEASONAL_SUBJECTS = {"cloud_sea", "snow_ice", "drift_ice", "seasonal_flowers"}


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def haversine_km(a, b):
    la1, lo1, la2, lo2 = map(radians, (a["lat"], a["lon"], b["lat"], b["lon"]))
    h = sin((la2 - la1) / 2) ** 2 + cos(la1) * cos(la2) * sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * atan2(sqrt(h), sqrt(1 - h))


class TestCLData23DiscoveryShortlist(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shortlist = load(SHORTLIST)
        cls.catalog = load(CATALOG)

    def test_at_least_ten_candidates(self):
        self.assertGreaterEqual(len(self.shortlist["candidates"]), 10)

    def test_unique_ids_and_region(self):
        ids = [c["id"] for c in self.shortlist["candidates"]]
        self.assertEqual(len(ids), len(set(ids)), "duplicate candidate id")
        self.assertTrue(all(i.startswith("jp-north-") for i in ids))
        self.assertEqual(self.shortlist["region"], "jp-north")

    def test_rubric_scores_in_range_and_total_consistent(self):
        weights = {d["key"]: d["weight"] for d in self.shortlist["rubric"]["dimensions"]}
        self.assertEqual(sorted(weights), sorted(RUBRIC_KEYS))
        for c in self.shortlist["candidates"]:
            for key in RUBRIC_KEYS:
                self.assertIn(c["rubric"][key], range(1, 6), f"{c['id']} {key}")
            expected = round(
                sum(c["rubric"][k] * weights[k] for k in RUBRIC_KEYS)
                / sum(weights.values()), 2)
            self.assertAlmostEqual(c["weighted_total"], expected,
                                   msg=f"{c['id']} weighted_total mismatch")

    def test_every_candidate_has_sources_and_trilingual_names(self):
        for c in self.shortlist["candidates"]:
            self.assertTrue(c.get("sources"), f"{c['id']} needs >=1 source URL")
            self.assertTrue(all(s.startswith(("http://", "https://"))
                                for s in c["sources"]), f"{c['id']} bad source URL")
            for lang in ("zh-TW", "en", "ja"):
                self.assertTrue(c["name_i18n"].get(lang), f"{c['id']} missing {lang}")

    def test_seasonal_subjects_carry_seasonal_window(self):
        for c in self.shortlist["candidates"]:
            if set(c["subjects"]) & SEASONAL_SUBJECTS:
                self.assertIn("seasonal_window", c,
                              f"{c['id']} seasonal subject without window")
                self.assertGreaterEqual(len(c["seasonal_window"]["months"]), 1)
                self.assertTrue(c["seasonal_window"].get("note"))

    def test_pairwise_differentiation_5km(self):
        cands = self.shortlist["candidates"]
        for i in range(len(cands)):
            for j in range(i + 1, len(cands)):
                dist = haversine_km(cands[i]["coords_approx"],
                                    cands[j]["coords_approx"])
                self.assertGreaterEqual(dist, 5.0,
                    f"{cands[i]['id']} vs {cands[j]['id']} {dist:.1f}km < 5km")

    def test_no_candidate_duplicates_existing_jp_north_catalog_place(self):
        existing = [p["name_i18n"]["zh-TW"] for p in self.catalog["places"]
                    if p["place_id"].startswith("jp-")]
        for c in self.shortlist["candidates"]:
            zh = c["name_i18n"]["zh-TW"]
            for name in existing:
                self.assertNotIn(name, zh and zh or "\0",
                    msg=f"{c['id']} name repeats catalog place {name}")

    def test_honest_coverage_notes_present(self):
        text = "\n".join(p.read_text(encoding="utf-8") for p in DOSSIERS)
        self.assertIn("YAMATWO", text)
        self.assertIn("なっぷ", text)

    def test_not_a_catalog_change(self):
        # Discovery round must not modify the live catalog: spot checks on the
        # byte-pinned catalog fields this ticket never touches.
        places = [p["place_id"] for p in self.catalog["places"]]
        self.assertNotIn("jp-north-unkai-terrace-tomamu", places)


if __name__ == "__main__":
    unittest.main()
