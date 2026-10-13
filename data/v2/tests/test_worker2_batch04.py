"""Batch04 five-place V2 Research-only admission contracts, independent of Batch03.

All five new legacy IDs are tested for actual Draft2020-12 schema validity,
same-text Crosswalk, scoped source evidence and explicit non-live unknowns.
This does NOT confer human review, site permission, GPS or live forecastability.
"""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/v2"
IDS = ("tw-082-P01", "tw-036-P01", "tw-034-P02", "jp-010-P01", "us-071-P01")
LANGS = ("zh-TW", "en", "ja")
EXPECTED = {
    "tw-082-P01": ("WEATHER", "WEATHER"),
    "tw-036-P01": ("ASTRONOMY", "WEATHER"),
    "tw-034-P02": ("WEATHER", "WEATHER"),
    "jp-010-P01": ("WEATHER", "SEASON_TIME"),
    "us-071-P01": ("WEATHER", "ASTRONOMY"),
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def pointer(document, path):
    if not path.startswith("/"):
        raise ValueError("Invalid JSON pointer")
    result = document
    for token in path[1:].split("/"):
        key = token.replace("~1", "/").replace("~0", "~")
        result = result[int(key)] if isinstance(result, list) else result[key]
    return result


def text_value(value):
    if value is None:
        return "unknown"
    if isinstance(value, dict) and "zh-TW" in value:
        return value["zh-TW"]
    if isinstance(value, dict) and "role" in value:
        return value["role"] + "｜" + value["notes_i18n"]["zh-TW"]
    return str(value)


class Batch04Gate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = {id_: read_json(DATA / "opportunities" / (id_ + ".json"))
                    for id_ in IDS}
        cls.audit = read_json(DATA / "audits/worker2_batch04_evidence.json")
        cls.rows = {id_: [json.loads(line) for line in
                    (DATA / "crosswalk" / f"worker2_batch04_{id_}.jsonl").read_text(
                        encoding="utf-8").splitlines() if line.strip()]
                    for id_ in IDS}
        cls.review = (DATA / "reviews/worker2_batch04_human_zh-TW.md").read_text(encoding="utf-8")
        schema = read_json(ROOT / "specs/v2/schema/opportunity-v2.1.schema.json")
        Draft202012Validator.check_schema(schema)
        cls.validator = Draft202012Validator(schema, format_checker=FormatChecker())

    def test_01_records_match_schema_and_canonical_legacy_ids(self):
        self.assertEqual(set(IDS), set(self.docs))
        self.assertEqual(len(IDS), len({doc["place_id"] for doc in self.docs.values()}))
        for id_, doc in self.docs.items():
            with self.subTest(id=id_):
                self.assertEqual("2.1.0", doc["schema_version"])
                self.assertEqual(id_, doc["opportunity_id"])
                self.assertEqual(id_.split("-P")[0], doc["place_id"])
                errors = sorted(e.message for e in self.validator.iter_errors(doc))
                self.assertEqual([], errors, errors)
                self.assertEqual(["REQUIRED", "QUALITY"],
                                 [c["role"] for c in doc["condition_contract"]["conditions"]])
                self.assertEqual(EXPECTED[id_], tuple(
                    c["domain"] for c in doc["condition_contract"]["conditions"]))

    def test_02_sources_and_all_references_are_declared_with_narrow_scope(self):
        sources = {s["id"]: s for s in self.audit["source_records"]}
        self.assertEqual(9, len(sources))
        self.assertEqual(set(IDS), set(self.audit["canonical_opportunity_ids"]))
        for id_, doc in self.docs.items():
            with self.subTest(id=id_):
                claims = {c["claim_id"]: c for c in doc["evidence_claims"]}
                self.assertEqual(5, len(claims))
                self.assertFalse(any(c["audit_status"] == "MISMATCH" for c in claims.values()))
                for claim in claims.values():
                    self.assertTrue(set(claim["evidence_refs"]).issubset(sources))
                self.assertEqual("OK", claims[f"{id_}-existence"]["audit_status"])
                self.assertEqual("PARTIAL", claims[f"{id_}-camera"]["audit_status"])
                self.assertEqual("UNKNOWN", claims[f"{id_}-navigation"]["audit_status"])
                for name in ("camera_contexts", "targets", "observation_relations", "navigation_targets"):
                    for item in doc[name]:
                        self.assertTrue(set(item["evidence_refs"]).issubset(sources))
                for c in doc["condition_contract"]["conditions"]:
                    self.assertTrue(set(c["claim_refs"]).issubset(claims))
                for source in doc["camera_contexts"][0]["evidence_refs"]:
                    self.assertTrue(sources[source]["url"].startswith("https://"))
                    self.assertTrue(sources[source]["limits"])

    def test_03_research_only_no_misleading_live_navigation_or_access_score(self):
        for id_, doc in self.docs.items():
            with self.subTest(id=id_):
                self.assertEqual("R1", doc["readiness"]["research_level"])
                self.assertEqual(["GEOMETRY_GAP", "RESEARCH_GAP"], doc["readiness"]["gaps"])
                self.assertEqual("evidence_review", doc["lifecycle_status"])
                self.assertEqual("pending", doc["provenance"]["review_status"])
                for camera in doc["camera_contexts"]:
                    self.assertEqual("unknown", camera["geometry"]["status"])
                    self.assertIsNone(camera["geometry"]["geojson"])
                    self.assertNotEqual("verified", camera["verification_status"])
                    for lang in LANGS:
                        self.assertTrue(camera["access_notes_i18n"][lang].strip())
                        self.assertTrue(camera["safety_notes_i18n"][lang].strip())
                for nav in doc["navigation_targets"]:
                    self.assertEqual("needs_review", nav["status"])
                    self.assertIsNone(nav["lat"])
                    self.assertIsNone(nav["lon"])
                for cond in doc["condition_contract"]["conditions"]:
                    self.assertIn(cond["domain"],
                        ("WEATHER", "ASTRONOMY", "SEASON_TIME", "GEOMETRY_COMPOSITION"))
                    self.assertNotEqual("AUTO", cond["evaluation_mode"])
                    self.assertIsNone(cond["threshold"])
                    self.assertIsNone(cond["model_binding"])
                    self.assertEqual("propagate_unknown", cond["unknown_policy"])
                    self.assertNotEqual("validated", cond["validation_status"])
                    for lang in LANGS:
                        self.assertTrue(cond["notes_i18n"][lang].strip())

    def test_04_crosswalk_exact_coverage_and_negative_conflict(self):
        for id_, doc in self.docs.items():
            rows = self.rows[id_]
            with self.subTest(id=id_):
                self.assertEqual(30, len(rows))
                self.assertEqual(30, len({r["human_claim_id"] for r in rows}))
                for row in rows:
                    self.assertNotIn(row["consistency_status"], ("MISMATCH", "UNSUPPORTED"))
                    expected = f"data/v2/opportunities/{id_}.json#"
                    self.assertTrue(row["machine_path_or_fields"].startswith(expected))
                    actual = pointer(doc, row["machine_path_or_fields"].split("#", 1)[1])
                    self.assertEqual(text_value(actual), row["human_text"])
                    if isinstance(actual, dict) and "zh-TW" in actual:
                        self.assertTrue(all(actual.get(lang, "").strip() for lang in LANGS))
                changed = [dict(x) for x in rows]
                changed[0]["human_text"] = "INJECTED MISMATCH"
                self.assertNotEqual(text_value(pointer(
                    doc, changed[0]["machine_path_or_fields"].split("#", 1)[1])),
                    changed[0]["human_text"])

    def test_05_human_readable_parity_and_original_preview_is_untouched(self):
        self.assertEqual("PENDING", self.audit["review"]["human_geo"])
        self.assertEqual("PENDING", self.audit["review"]["human_trilingual_semantics"])
        for id_, doc in self.docs.items():
            with self.subTest(id=id_):
                self.assertEqual(1, self.review.count("## " + id_ + " "))
                section = self.review.split("## " + id_ + " ", 1)[1].split("\n## ", 1)[0]
                self.assertIn(doc["description_i18n"]["zh-TW"], section)
                self.assertIn(doc["camera_contexts"][0]["access_notes_i18n"]["zh-TW"], section)
                self.assertIn(doc["camera_contexts"][0]["safety_notes_i18n"]["zh-TW"], section)
                for cond in doc["condition_contract"]["conditions"]:
                    self.assertIn(cond["notes_i18n"]["zh-TW"], section)
        preview = read_json(DATA / "previews/tw-026-P01.research-only.v21.json")
        self.assertEqual(["tw-026-P01"], [v["opportunity_id"] for v in preview["opportunities"]])
        self.assertIs(preview["research_only"], True)
        self.assertIs(preview["forecast_available"], False)
        self.assertIs(preview["selected_date_recommendation_eligible"], False)
        self.assertEqual([], preview["evaluations"])


if __name__ == "__main__":
    unittest.main()
