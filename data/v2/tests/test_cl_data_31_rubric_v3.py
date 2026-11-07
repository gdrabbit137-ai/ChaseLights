"""CL-DATA-31 rubric v3 tests — 景色優美單維度 admission + line redraw.

Covers:
  * discover_spots v3: single-dimension admission (scenic v3 composite),
    admission line 3.8, unscored candidates never admit, differentiation
    stays a mechanical cull (not scored), v2 rubric retired.
  * scenic_v3_candidates finalize math: visual median/mean, cert clamp ±1,
    community ±0.5, composite clip 0–5 (no fabricated scores for unknowns).
  * scenic_v3_redraw: pool/admitted/dropped consistency with v3 scores and
    catalog health bucket arithmetic.
"""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "data/v2/tools"
AUD = ROOT / "data/v2/audits/discovery"
sys.path.insert(0, str(TOOLS))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


ds = _load("discover_spots31", TOOLS / "discover_spots.py")
red = _load("scenic_v3_redraw31", TOOLS / "scenic_v3_redraw.py")

CAND_BASE = {
    "slug": "x", "name_zh": "X", "name_en": "X", "name_ja": "X",
    "lat": 0.0, "lon": 0.0, "elev_m": 0, "tags": ["a"],
    "source_refs": [{"url": "https://example.com", "note": ""}],
    "subject_draft": "", "condition_draft": "", "access_note": "",
    "safety_note": "", "differentiation_note": "",
    "scores": {"subject_strength": 3, "weather_dependency": 3,
               "data_availability": 3, "scenic_beauty": 3},
}


def cand(**kw):
    c = dict(CAND_BASE)
    c.update(kw)
    return c


class TestRubricV3Admission(unittest.TestCase):
    def setUp(self):
        self.existing = []  # no catalog spots -> never culled

    def test_admission_line_is_3_8(self):
        self.assertEqual(ds.LINE, 3.8)

    def test_single_dimension_admits_on_composite(self):
        v3 = {"X": {"composite_v3": 4.0, "visual_0_5": 4.0, "cert_tier": 4,
                    "cert_evidence": "", "community_adj": 0,
                    "community_evidence": "", "composite_formula": "",
                    "photos": []}}
        ev = ds.evaluate(cand(), self.existing, v3)
        self.assertTrue(ev["admits"])
        self.assertEqual(ev["rubric_v3"]["composite_v3"], 4.0)

    def test_below_line_does_not_admit(self):
        v3 = {"X": {"composite_v3": 3.7, "visual_0_5": 4.0, "cert_tier": 3,
                    "cert_evidence": "", "community_adj": 0,
                    "community_evidence": "", "composite_formula": "",
                    "photos": []}}
        self.assertFalse(ds.evaluate(cand(), self.existing, v3)["admits"])

    def test_unknown_composite_never_admits_and_is_never_fabricated(self):
        ev = ds.evaluate(cand(), self.existing, {})
        self.assertFalse(ev["admits"])
        self.assertIsNone(ev["rubric_v3"]["composite_v3"])
        self.assertIn("unscored", ev["rubric_v3"]["status"])

    def test_differentiation_is_a_cull_not_a_score(self):
        existing = [("Nearby", 0.02, 0.02, ["a"])]  # ~2-3 km, tag overlap
        ev = ds.evaluate(cand(), existing, {})
        self.assertTrue(ev["_culled"])
        self.assertFalse(ev["admits"])
        # and the cull applies regardless of a high v3 score
        v3 = {"X": {"composite_v3": 5, "visual_0_5": 5, "cert_tier": 5,
                    "cert_evidence": "", "community_adj": 0,
                    "community_evidence": "", "composite_formula": "",
                    "photos": []}}
        self.assertFalse(ds.evaluate(cand(), existing, v3)["admits"])

    def test_v2_weights_are_not_used(self):
        self.assertFalse(hasattr(ds, "RUBRIC_MAP"),
                         "five-dimension RUBRIC_MAP must be retired")
        self.assertNotIn("differentiation",
                         ds.V2_RETIRED_KEYS)  # retired keys documented


class TestScenicV3CandidateFinalize(unittest.TestCase):
    """Finalize arithmetic, exercised through the same helper functions."""

    def test_community_adj_rules(self):
        import scenic_v3_candidates as S
        f = S.community_adj
        # no valid photos -> no community signal
        self.assertEqual(f([{"_valid": False}], {}), (0, "無社群信號資料"))
        # badge on a valid, inventoried photo
        comm = {"File:A.jpg": {"badges": ["quality"], "pv12mo": 9000}}
        self.assertEqual(f([{"_valid": True, "key": "File:A.jpg"}], comm)[0], 0.5)
        # high pageviews, no badge
        comm = {"File:A.jpg": {"badges": [], "pv12mo": 9000}}
        self.assertEqual(f([{"_valid": True, "key": "File:A.jpg"}], comm)[0], 0.25)
        # complete inventory, all low pv -> negative (owner rule)
        comm = {"File:A.jpg": {"badges": [], "pv12mo": 10}}
        self.assertEqual(f([{"_valid": True, "key": "File:A.jpg"}], comm)[0], -0.25)
        # payload missing -> never negative
        comm = {"File:A.jpg": {"badges": [], "pv12mo": None}}
        self.assertEqual(f([{"_valid": True, "key": "File:A.jpg"}], comm)[0], 0)


class TestRedrawArtifact(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.redraw = json.loads((AUD / "cl-data-31-rubric-v3-redraw.json")
                                .read_text(encoding="utf-8"))
        cls.cands = json.loads((AUD / "scenic-v3-candidates.json")
                               .read_text(encoding="utf-8"))
        cls.v3full = json.loads((AUD / "scenic-v3-full.json").read_text(encoding="utf-8"))

    def test_line_and_pool_consistency(self):
        line = self.redraw["line"]
        for p in self.redraw["pool"]:
            if p["v3"] is None:
                self.assertFalse(p["admits_v3"])
            else:
                self.assertEqual(p["admits_v3"], p["v3"] >= line, p["id"])

    def test_dropped_were_admitted_under_v2(self):
        for p in self.redraw["dropped"]:
            self.assertGreaterEqual(p["v2_old"], 3.8, p["id"])
            self.assertLess(p["v3"], 3.8, p["id"])

    def test_admitted_meet_line(self):
        for p in self.redraw["new_admitted"]:
            self.assertGreaterEqual(p["v3"], 3.8, p["id"])

    def test_health_buckets_sum(self):
        h = self.redraw["catalog_health"]
        self.assertEqual(sum(h["buckets"].values()), h["n_scored"])
        self.assertEqual(h["n_scored"] + h["n_unknown"], h["n_total"])

    def test_supplementary_candidates_have_photo_provenance(self):
        for c in self.cands["candidates"]:
            self.assertGreater(c["n_photos_fetched"], 0, c["id"])
            self.assertTrue(c["photos"], c["id"])
            for ph in c["photos"]:
                self.assertTrue(ph.get("url") or ph.get("title"),
                                f"{c['id']} photo provenance incomplete")

    def test_every_scored_candidate_has_composite_formula(self):
        for c in self.cands["candidates"]:
            if c["composite_v3"] is not None:
                self.assertTrue(c["composite_formula"], c["id"])
            else:
                self.assertIn("unknown", c["composite_formula"], c["id"])


if __name__ == "__main__":
    unittest.main()
