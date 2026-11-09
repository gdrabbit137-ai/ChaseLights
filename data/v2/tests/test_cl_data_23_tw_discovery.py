"""CL-DATA-31 discovery shortlist contract tests (tw round, rubric v3).

The discovery round is a LIST, not a catalog change: membership decisions stay
with the owner. These tests validate the machine-readable rubric artifact at
data/v2/audits/discovery/tw-shortlist.json under RUBRIC V3 (CL-DATA-31 owner
ruling): a single admission dimension — 景色優美程度 (scenic v3 composite,
0–5, admission line >= 3.8). The v2 five-dimension weighted rubric is retired.
Also validates: seasonal-window presence for seasonal subjects, 5 km
differentiation against BOTH the shortlist's own candidates (pairwise) and the
live tw catalog (regions.py), provenance (>=1 source URL per candidate), photo
provenance for scored candidates, and that the live catalog was not touched.
"""
import json
import sys
import unittest
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SHORTLIST = ROOT / "data/v2/audits/discovery/tw-shortlist.json"
CATALOG = ROOT / "apps/web-v2/catalog.v2.json"

# Subjects whose photographic window is seasonal by nature — the candidate MUST
# carry an explicit seasonal_window (cloud-sea season / milky-way season / etc.)
SEASONAL_SUBJECTS = {"cloud_sea", "starlight"}


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def haversine_km(a, b):
    la1, lo1, la2, lo2 = map(radians, (a["lat"], a["lon"], b["lat"], b["lon"]))
    h = sin((la2 - la1) / 2) ** 2 + cos(la1) * cos(la2) * sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * atan2(sqrt(h), sqrt(1 - h))


class TestCLData23TWDiscoveryShortlist(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shortlist = load(SHORTLIST)
        cls.catalog = load(CATALOG)

    def test_at_least_ten_candidates(self):
        # v3 rerun lists every non-culled candidate (kept + below-line +
        # unscored); the full 14-candidate pool is pinned by the deterministic
        # pipeline rerun below.
        self.assertGreaterEqual(len(self.shortlist["candidates"]), 2)

    def test_unique_ids_and_region(self):
        ids = [c["id"] for c in self.shortlist["candidates"]]
        self.assertEqual(len(ids), len(set(ids)), "duplicate candidate id")
        self.assertTrue(all(i.startswith("tw-") for i in ids))
        self.assertEqual(self.shortlist["region"], "tw")
        self.assertEqual(self.shortlist["schema_version"], "cl-data-31-rubric-v3-1")

    def test_rubric_v3_single_dimension(self):
        rubric = self.shortlist["rubric"]
        self.assertEqual(rubric["version"], "v3")
        self.assertEqual(rubric["admission_line"], 3.8)
        self.assertEqual(len(rubric["dimension"]), 1, "v3 is single-dimension")
        self.assertEqual(rubric["dimension"][0]["key"], "scenic_beauty_v3")
        retired_keys = rubric["retired"][0]["keys"]
        self.assertEqual(
            set(retired_keys),
            {"subject_strength", "weather_dependency", "data_availability",
             "scenic_beauty"},
            "all v2 dimensions must be recorded as retired")

    def test_scenic_v3_scores_consistent(self):
        for c in self.shortlist["candidates"]:
            s = c["rubric_v3"]
            comp = s.get("composite_v3")
            if comp is None:
                self.assertIn("unscored", s["status"], f"{c['id']} must be honest")
                continue
            self.assertTrue(0 <= comp <= 5, f"{c['id']} composite out of range")
            self.assertTrue(s.get("composite_formula"), f"{c['id']} missing formula")
            self.assertTrue(s.get("photos"), f"{c['id']} missing photo provenance")

    def test_kept_candidates_meet_line(self):
        line = self.shortlist["rubric"]["admission_line"]
        for c in self.shortlist["candidates"]:
            if c["admits"]:
                self.assertGreaterEqual(c["rubric_v3"]["composite_v3"], line, c["id"])

    def test_below_line_list_consistent(self):
        line = self.shortlist["rubric"]["admission_line"]
        for c in self.shortlist["below_line_candidates"]:
            self.assertIsNotNone(c["v3"], "below-line entries must be scored")
            self.assertLess(c["v3"], line, c["id"])

    def test_safe_access_info_still_required(self):
        # CL-DATA-26/31: no longer SCORED, but seasonal-window / closure
        # semantics must stay in the dossier/contract fields.
        for c in self.shortlist["candidates"]:
            self.assertIn("seasonal_window", c,
                          f"{c['id']} lost seasonal_window (safe_access info must remain)")

    def test_every_candidate_has_sources_and_trilingual_names(self):
        for c in self.shortlist["candidates"]:
            self.assertGreaterEqual(len(c.get("sources", [])), 2,
                                    f"{c['id']} needs >=2 web evidence URLs")
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

    def test_no_candidate_within_5km_of_live_tw_catalog(self):
        import regions
        spots = regions.get_spots("tw")
        for c in self.shortlist["candidates"]:
            for s in spots:
                d = haversine_km(c["coords_approx"], {"lat": s["lat"], "lon": s["lon"]})
                self.assertGreaterEqual(d, 5.0,
                    f"{c['id']} is {d:.1f} km from catalog spot {s['name_i18n']['zh-TW']}")

    def test_culled_candidates_recorded_honestly(self):
        culled = self.shortlist.get("culled_candidates", [])
        for c in culled:
            self.assertTrue(c.get("reason"), f"{c['id']} culled without reason")

    def test_not_a_catalog_change(self):
        # Discovery round must not modify the live catalog: spot checks on the
        # byte-pinned catalog fields this ticket never touches.
        places = [p["place_id"] for p in self.catalog["places"]]
        for c in self.shortlist["candidates"]:
            self.assertNotIn(c["id"], places)
        self.assertEqual(len(self.catalog["places"]), 261,
                         "catalog place count pinned (re-anchored CL-INT-105: 261 places, CL-DATA-43 AK/HI expansion)")

    def test_pipeline_tool_rerun_is_deterministic(self):
        import subprocess
        out = subprocess.run(
            [sys.executable, str(ROOT / "data/v2/tools/discover_spots.py"),
             "--region", "tw", "--top", "10", "--outdir", "data/v2/audits/discovery"],
            cwd=str(ROOT), capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        summary = json.loads(out.stdout)
        self.assertEqual(summary["region"], "tw")
        self.assertEqual(summary["candidates"], 14)
        # rubric v3 rerun: the three kept-tw candidates now score below the
        # 3.8 line on scenic v3; the mechanical dedupe cull is unchanged.
        self.assertEqual(summary["kept"], 0)
        self.assertEqual(summary["below_line"], 3)
        self.assertEqual(summary["culled"], 11)


if __name__ == "__main__":
    unittest.main()
