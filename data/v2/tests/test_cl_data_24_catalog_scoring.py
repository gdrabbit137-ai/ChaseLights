#!/usr/bin/env python3
"""CL-DATA-24 — catalog scoring determinism & completeness tests.

Verifies the full-catalog mechanical scoring pipeline (catalog_scoring.py) is
re-runnable, deterministic (byte-identical JSON/MD on rerun), covers the whole
catalog (197 places / 374 opportunities), and that weakness lists are consistent
with the opportunity scores.
"""
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
TOOL = REPO_ROOT / "data/v2/tools/catalog_scoring.py"
OUT_JSON = REPO_ROOT / "data/v2/audits/discovery/catalog-scoring.json"
OUT_MD = REPO_ROOT / "data/v2/audits/discovery/catalog-scoring.md"


def run_tool():
    r = subprocess.run([sys.executable, str(TOOL)], capture_output=True, text=True)
    assert r.returncode == 0, f"scoring tool failed: {r.stderr[-800:]}"
    return json.loads(r.stdout)


class TestClData24CatalogScoring(unittest.TestCase):
    def test_catalog_scoring_deterministic_and_complete(self):
        run_tool()
        first_json = OUT_JSON.read_bytes()
        first_md = OUT_MD.read_bytes()
        run_tool()
        assert OUT_JSON.read_bytes() == first_json, "catalog-scoring.json not deterministic"
        assert OUT_MD.read_bytes() == first_md, "catalog-scoring.md not deterministic"

        rep = json.loads(first_json.decode("utf-8"))
        # schema + full coverage (re-anchored CL-DATA-25R: rubric v2, honest unknown)
        assert rep["schema_version"] == "cl-data-24-catalog-scoring-2"
        assert "safe_access" not in rep["rubric_weights"]
        assert rep["rubric_weights"]["scenic_beauty"] == 20
        s = rep["summary"]
        assert s["places"] == 249, f"expected 249 places, got {s['places']}"
        assert s["opportunities"] == 448, f"expected 448 opportunities, got {s['opportunities']}"
        assert s["canonical_locked_opportunities"] == 448
        assert len(rep["ranking"]) == 249
        assert len(rep["opportunity_scores"]) == 448
        assert s["places_with_unknown_scenic_beauty"] == sum(
            1 for p in rep["ranking"] if p["rubric"]["scenic_beauty"] == "unknown")
        # weighted totals in valid range (None = honest unknown), ranking ordered by (total, id)
        totals = [p["weighted_total"] for p in rep["ranking"] if p["weighted_total"] is not None]
        assert all(1.0 <= t <= 5.0 for t in totals)
        assert totals == sorted(totals, reverse=True)
        for a, b in zip(rep["ranking"], rep["ranking"][1:]):
            if a["weighted_total"] == b["weighted_total"]:
                assert a["place_id"] < b["place_id"]
        ranked_unknown = [p for p in rep["ranking"] if p["weighted_total"] is None]
        assert rep["ranking"][-len(ranked_unknown):] == ranked_unknown
        # rubric dimensions complete and in range for every place
        for p in rep["ranking"]:
            assert set(p["rubric"]) == {"subject_strength", "weather_light_dependency",
                                        "verifiability", "differentiation", "scenic_beauty"}
            known = [v for v in p["rubric"].values() if v != "unknown"]
            assert all(1 <= v <= 5 for v in known)
            if p["rubric"]["scenic_beauty"] != "unknown":
                assert p["weighted_total"] is not None
        # weakness lists consistent with opportunity scores
        low_wl = {o["opportunity_id"] for o in rep["weakness_lists"]["low_weather_light"]}
        low_vf = {o["opportunity_id"] for o in rep["weakness_lists"]["low_verifiability"]}
        for o in rep["opportunity_scores"]:
            assert set(o["scores"]) == {"subject_strength", "weather_light_dependency",
                                        "verifiability"}
            if o["scores"]["weather_light_dependency"] <= 2:
                assert o["opportunity_id"] in low_wl
            else:
                assert o["opportunity_id"] not in low_wl
            if o["scores"]["verifiability"] <= 2.0:
                assert o["opportunity_id"] in low_vf
            else:
                assert o["opportunity_id"] not in low_vf
        # clusters must equal the 5km connected components, recomputed independently
        def hav(a, b):
            r = 6371.0
            p1, p2 = math.radians(a[0]), math.radians(b[0])
            dp = p2 - p1
            dl = math.radians(b[1] - a[1])
            x = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
            return 2 * r * math.asin(math.sqrt(x))

        coords = {p["place_id"]: p["coords"] for p in rep["ranking"] if p["coords"]}
        ids = sorted(coords)
        parent = {p: p for p in ids}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                if hav(coords[a], coords[b]) <= 5.0:
                    ra, rb = find(a), find(b)
                    if ra != rb:
                        parent[rb] = ra
        expected = {}
        for p in ids:
            expected.setdefault(find(p), set()).add(p)
        got = {frozenset(m["place_id"] for m in c["members"])
               for c in rep["weakness_lists"]["clusters_within_5km"]}
        assert got == {frozenset(v) for v in expected.values() if len(v) >= 2}
        # md report carries the headline numbers
        md = first_md.decode("utf-8")
        assert f"**{s['mean_weighted_total']} / 5**" in md
        assert f"**{s['median_weighted_total']} / 5**" in md
        assert "低 weather_light" in md and "低 verifiability" in md and "高重叠區" in md


if __name__ == "__main__":
    unittest.main()
