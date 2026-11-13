"""CL-UI-62: subject-card derived layer — dictionaries, generator, artifact.

Covers: genre short-name dictionary coverage (every genre_template), failure
short-word coverage (every contract/override/bundle metric), trilingual key
presence, generator determinism (fresh derivation == committed artifact),
dominant-reason rule invariants, LF bytes, CLI regeneration equality.
"""
from __future__ import annotations

import json
import re
import unittest
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COPY_DIR = ROOT / "data/v2/copy"
EVAL_DIR = ROOT / "data/v2/evaluations"
OPP_DIR = ROOT / "data/v2/opportunities"
ARTIFACT = EVAL_DIR / "subject-cards-20261112T202312Z.json"
LANGS = ("zh-TW", "en", "ja")


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bsc = _load_module("build_subject_cards", ROOT / "data/v2/tools/build_subject_cards.py")


class DictionaryCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.genres_doc = json.loads((COPY_DIR / "genre_short_names.json").read_bytes().decode("utf-8"))
        cls.fails_doc = json.loads((COPY_DIR / "fail_reason_short.json").read_bytes().decode("utf-8"))
        cls.genres: set[str] = set()
        cls.metrics: set[str] = set()
        for f in OPP_DIR.glob("*.json"):
            txt = f.read_text(encoding="utf-8")
            cls.genres.update(re.findall(r'"genre_template"\s*:\s*"([^"]+)"', txt))
            cls.metrics.update(re.findall(r'"metric"\s*:\s*"([^"]+)"', txt))
        overrides = json.loads((COPY_DIR / "fail_reason_overrides.json").read_bytes().decode("utf-8"))
        for per_opp in overrides.values():
            cls.metrics.update(per_opp)

    def test_every_genre_has_trilingual_short_name(self):
        self.assertGreaterEqual(len(self.genres), 20)
        for g in self.genres:
            entry = self.genres_doc["genres"].get(g)
            self.assertIsNotNone(entry, g)
            for lang in LANGS:
                self.assertTrue(entry.get(lang), f"{g} missing {lang}")
            self.assertLessEqual(len(entry["zh-TW"]), 3, f"{g} zh-TW short name must be 2-3 chars")

    def test_every_metric_has_trilingual_short_word(self):
        for m in self.metrics:
            entry = self.fails_doc["words"].get(m)
            self.assertIsNotNone(entry, m)
            for lang in LANGS:
                self.assertTrue(entry.get(lang), f"{m} missing {lang}")

    def test_metric_priority_has_no_dangling_entries_and_no_duplicates(self):
        self.assertEqual(len(set(self.fails_doc["metric_priority"])), len(self.fails_doc["metric_priority"]))
        for m in self.fails_doc["metric_priority"]:
            self.assertIn(m, self.fails_doc["words"], m)
        self.assertEqual(self.fails_doc["metric_priority"][0], "precipitation")
        self.assertEqual(self.fails_doc["metric_priority"][1], "visibility")

    def test_dominant_reason_rule_is_documented(self):
        rule = self.fails_doc["dominant_reason_rule"]
        self.assertEqual(rule["rule_version"], "1.0")
        for lang in ("zh-TW", "en"):
            self.assertGreater(len(rule[lang]), 40)


class DerivedArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(ARTIFACT.read_bytes().decode("utf-8"))
        source_name = cls.artifact["derived_from"]["source_bundle"]
        cls.bundle = json.loads((EVAL_DIR / source_name).read_bytes().decode("utf-8"))

    def test_provenance(self):
        d = self.artifact["derived_from"]
        self.assertEqual(d["generator"], "data/v2/tools/build_subject_cards.py")
        self.assertEqual(d["rule_version"], "1.0")
        self.assertTrue((EVAL_DIR / d["source_bundle"]).exists())

    def test_generator_determinism_fresh_derivation_equals_artifact(self):
        genres, fails = bsc.load_copy()
        payload, unknown = bsc.derive_place_days(bsc.read_bundle(EVAL_DIR / self.artifact["derived_from"]["source_bundle"]), genres, fails)
        self.assertEqual(unknown, set())
        self.assertEqual(json.loads(json.dumps(payload, sort_keys=True)), json.loads(json.dumps(self.artifact, sort_keys=True)))

    def test_row_invariants(self):
        genres, fails = bsc.load_copy()
        words = fails["words"]
        rows = 0
        for place in self.bundle["places"]:
            days = self.artifact["places"].get(place["place_id"])
            self.assertIsNotNone(days, place["place_id"])
            for date, row in days.items():
                rows += 1
                self.assertIn(row["status"], ("clear", "failed", "not_evaluable"))
                self.assertIn(date, {d["local_date"] for o in place["opportunities"] for d in o["days"]})
                for s in row["suitable"]:
                    self.assertTrue(s["window"], f"{place['place_id']} {date} empty window")
                    self.assertTrue(s["subject_short"].get("zh-TW"))
                if row["dominant_reason"] is not None:
                    self.assertIn(row["dominant_metric"], words)
                    self.assertEqual(row["dominant_reason"], words[row["dominant_metric"]])
                else:
                    self.assertIsNone(row["dominant_metric"])
        self.assertGreater(rows, 3000)

    def test_dominant_metric_voted_by_failed_subjects(self):
        """dominant_metric must be the highest-vote core violation per the rule."""
        genres, fails = bsc.load_copy()
        priority = {m: i for i, m in enumerate(fails["metric_priority"])}
        for place in self.bundle["places"]:
            dates = {d["local_date"] for o in place["opportunities"] for d in o["days"]}
            for date in dates:
                row = self.artifact["places"][place["place_id"]][date]
                day_votes = {}
                for opp in place["opportunities"]:
                    for day in opp["days"]:
                        if day["local_date"] != date or day["state"] != "UNFAVORABLE":
                            continue
                        conds = list(day["conditions"])
                        for i, c in enumerate(conds):
                            c["_order"] = i
                        metric = bsc._core_violation_metric(conds, priority)
                        if metric is not None:
                            day_votes[metric] = day_votes.get(metric, 0) + 1
                if day_votes and row["dominant_reason"] is not None:
                    expected = min(sorted(day_votes), key=lambda m: (-day_votes[m], priority.get(m, len(priority)), m))
                    self.assertEqual(row["dominant_metric"], expected, f"{place['place_id']} {date}")
                elif not day_votes:
                    self.assertIsNone(row["dominant_reason"], f"{place['place_id']} {date}")

    def test_lf_bytes_for_committed_data_files(self):
        for path in (ARTIFACT, COPY_DIR / "genre_short_names.json", COPY_DIR / "fail_reason_short.json"):
            raw = path.read_bytes()
            self.assertNotIn(b"\r\n", raw, str(path))

    def test_cli_regen_matches_artifact(self):
        import tempfile
        import os
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            out = Path(tmp) / "regen.json"
            rc = bsc.main(["--bundle", str(EVAL_DIR / self.artifact["derived_from"]["source_bundle"]), "--out", str(out)])
            self.assertEqual(rc, 0)
            self.assertEqual(out.read_bytes(), ARTIFACT.read_bytes())


if __name__ == "__main__":
    unittest.main()
