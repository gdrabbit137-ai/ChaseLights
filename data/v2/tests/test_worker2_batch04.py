"""Batch04 five-place V2 Research-only admission contracts, independent of Batch03.

All five new legacy IDs are tested for actual Draft2020-12 schema validity,
same-text Crosswalk, scoped source evidence and explicit non-live unknowns.

CL-DATA-18 human-review gate reform (owner ruling 2026-11-06): the former
human-review precondition is REPLACED by AI verification — a change to a
human-review/byte-pinned geometry or light-window field is admitted when its
provenance is complete (authoritative source URL + verification date +
derivation_method marker, recorded in provenance.reviewed_by). The gate itself
is RETAINED as a provenance admission control: fills without complete
provenance are rejected (see data/v2/tests/test_cl_data_18_ai_verification_gate.py
and the re-anchored assertions below). Validation/calibration stays provisional.
"""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/v2"
IDS = ("tw-082-P01", "tw-036-P01", "tw-034-P02", "jp-010-P01", "us-071-P01")
# CL-DATA-18: these five had their geometry gap filled by AI verification with
# authoritative source URL + date (owner ruling 2026-11-06 gate reform).
AI_VERIFIED_GEOMETRY = set(IDS)
LANGS = ("zh-TW", "en", "ja")
EXPECTED = {
    # 2026-11-02 owner ruling: the four xlsx-rebuilt subjects (tw-082/tw-034/
    # jp-010/us-071) adopt the review-revised template contracts; tw-036-P01
    # keeps its 2026-11-01 manager-reviewed sunrise contract.
    "tw-082-P01": ("WEATHER", "HYDROLOGY", "WEATHER", "WEATHER"),
    "tw-036-P01": ("ASTRONOMY", "WEATHER", "WEATHER", "WEATHER"),
    "tw-034-P02": ("WEATHER", "WEATHER", "WEATHER", "WEATHER", "ASTRONOMY"),  # +light_window CL-CI-27 (CL-DATA-33 f550046eb)
    "jp-010-P01": ("SEASON_TIME", "WEATHER", "WEATHER"),
    "us-071-P01": ("ASTRONOMY", "WEATHER", "WEATHER", "WEATHER"),
}
EXPECTED_ROLES = {
    "tw-082-P01": ("REQUIRED", "REQUIRED", "REQUIRED", "QUALITY"),
    "tw-036-P01": ("REQUIRED", "REQUIRED", "QUALITY", "REQUIRED"),
    "tw-034-P02": ("REQUIRED", "REQUIRED", "REQUIRED", "REQUIRED", "REQUIRED"),  # +light_window CL-CI-27 (CL-DATA-33 f550046eb)
    "jp-010-P01": ("REQUIRED", "REQUIRED", "REQUIRED"),
    "us-071-P01": ("REQUIRED", "REQUIRED", "REQUIRED", "REQUIRED"),
}
# Subjects whose conditions were rebuilt under the 2026-11-02 owner ruling
# (provenance must carry the ruling + the git-history rollback pointer).
OWNER_RULED = ("tw-082-P01", "tw-034-P02", "jp-010-P01", "us-071-P01")


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
                self.assertEqual(EXPECTED_ROLES[id_],
                                 tuple(c["role"] for c in
                                       doc["condition_contract"]["conditions"]))
                self.assertEqual(EXPECTED[id_], tuple(
                    c["domain"] for c in doc["condition_contract"]["conditions"]))

    def test_02_sources_and_all_references_are_declared_with_narrow_scope(self):
        sources = {s["id"]: s for s in self.audit["source_records"]}
        # CL-DATA-18: +5 AI-verified coordinate sources (URL + date required).
        self.assertEqual(14, len(sources))
        self.assertEqual(set(IDS), set(self.audit["canonical_opportunity_ids"]))
        for sid in ("b04c-tw034", "b04c-tw036", "b04c-tw082", "b04c-jp010", "b04c-us071"):
            src = sources[sid]
            self.assertTrue(src["url"].startswith("https://"), sid)
            self.assertTrue(src["date"], sid)
            self.assertTrue(src["limits"], sid)
        for id_, doc in self.docs.items():
            with self.subTest(id=id_):
                claims = {c["claim_id"]: c for c in doc["evidence_claims"]}
                self.assertEqual(5, len(claims))
                self.assertFalse(any(c["audit_status"] == "MISMATCH" for c in claims.values()))
                for claim in claims.values():
                    self.assertTrue(set(claim["evidence_refs"]).issubset(sources))
                self.assertEqual("OK", claims[f"{id_}-existence"]["audit_status"])
                # CL-DATA-18 re-anchor: camera claim is AI-verified OK.
                self.assertEqual("OK", claims[f"{id_}-camera"]["audit_status"])
                self.assertIn("AI-verified 2026-11-06", claims[f"{id_}-camera"]["scope_note"])
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
                # CL-DATA-18 re-anchor: GEOMETRY_GAP resolved by AI-verified fills.
                self.assertEqual(["RESEARCH_GAP"], doc["readiness"]["gaps"])
                self.assertEqual("evidence_review", doc["lifecycle_status"])
                self.assertEqual("reviewed", doc["provenance"]["review_status"])
                self.assertIn("AI-verification 2026-11-06", doc["provenance"]["reviewed_by"])
                for camera in doc["camera_contexts"]:
                    if id_ in AI_VERIFIED_GEOMETRY:
                        # CL-DATA-18 reform: AI-verified fill with complete
                        # provenance (source URL + date in derivation_method).
                        self.assertEqual("derived", camera["geometry"]["status"])
                        self.assertEqual("Point", camera["geometry"]["geojson"]["type"])
                        dm = camera["geometry"]["derivation_method"]
                        self.assertIn("CL-DATA-18", dm)
                        self.assertIn("2026-11-06", dm)
                        self.assertIn("https://", dm)
                        self.assertEqual("representative", camera["verification_status"])
                    else:
                        self.assertEqual("unknown", camera["geometry"]["status"])
                        self.assertIsNone(camera["geometry"]["geojson"])
                        self.assertNotEqual("verified", camera["verification_status"])
                    for lang in LANGS:
                        self.assertTrue(camera["access_notes_i18n"][lang].strip())
                        self.assertTrue(camera["safety_notes_i18n"][lang].strip())
                for nav in doc["navigation_targets"]:
                    self.assertEqual("needs_review", nav["status"])
                    if id_ in AI_VERIFIED_GEOMETRY:
                        # Coordinates of the viewpoint itself are AI-verified;
                        # arrival-route semantics stay needs_review.
                        self.assertIsNotNone(nav["lat"])
                        self.assertIsNotNone(nav["lon"])
                        self.assertTrue(nav["evidence_refs"])
                        self.assertEqual("low", nav["confidence"])
                    else:
                        self.assertIsNone(nav["lat"])
                        self.assertIsNone(nav["lon"])
                for cond in doc["condition_contract"]["conditions"]:
                    self.assertIn(cond["domain"],
                        ("WEATHER", "ASTRONOMY", "SEASON_TIME", "GEOMETRY_COMPOSITION",
                         "HYDROLOGY", "SUBJECT_STATE"))
                    self.assertNotEqual("AUTO", cond["evaluation_mode"])
                    # 2026-11-02 owner ruling: declared windows keep operator
                    # "none"; review-revised numeric gates stay provisional and
                    # never raw booleans.
                    if cond["operator"] == "eq" and \
                            isinstance(cond["threshold"], str):
                        # seasonal/event window sentinel (window_open/closed)
                        self.assertIn(cond["threshold"],
                                      ("window_open", "window_closed"))
                    elif cond["threshold"] is None:
                        self.assertEqual("none", cond["operator"])
                    else:
                        self.assertTrue(
                            isinstance(cond["threshold"], (int, float))
                            or (isinstance(cond["threshold"], list)
                                and len(cond["threshold"]) == 2
                                and all(isinstance(x, (int, float))
                                        for x in cond["threshold"])),
                            cond["metric"])
                    # Registry-carried model_binding strings are declared
                    # dataset/field/role bindings (no geojson geometry claim).
                    self.assertNotEqual("AUTO", cond["evaluation_mode"])
                    self.assertEqual("propagate_unknown", cond["unknown_policy"])
                    self.assertIn(cond["validation_status"],
                                  ("provisional", "unvalidated"))
                    self.assertNotEqual("defined", cond.get("calibration_status"))
                    for lang in LANGS:
                        self.assertTrue(cond["notes_i18n"][lang].strip())
                    if id_ in OWNER_RULED:
                        zh = cond["notes_i18n"]["zh-TW"]
                        # CL-CI-27 2026-11-08: the CL-DATA-33 gap-fill condition
                        # (light_window) carries its own dated CL-DATA-33 note and
                        # is outside the 2026-11-02 owner-ruling provenance.
                        if "2026-11-08 CL-DATA-33" in zh:
                            continue
                        self.assertIn("2026-11-02 owner（Richard）裁決", zh)
                        self.assertIn("34cb70f39", zh)
                        self.assertIn("未校準", zh)

    def test_04_crosswalk_exact_coverage_and_negative_conflict(self):
        expected_rows = {"tw-082-P01": 35, "tw-036-P01": 35, "tw-034-P02": 35,
                         "jp-010-P01": 32, "us-071-P01": 35}
        for id_, doc in self.docs.items():
            rows = self.rows[id_]
            with self.subTest(id=id_):
                self.assertEqual(expected_rows[id_], len(rows))
                self.assertEqual(expected_rows[id_], len({r["human_claim_id"] for r in rows}))
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
        # CL-DATA-18 reform: geometry review is AI_VERIFIED (provenance-complete
        # fills with source URL + date); trilingual copy semantics stays PENDING.
        self.assertEqual("AI_VERIFIED", self.audit["review"]["human_geo"])
        self.assertIn("CL-DATA-18", self.audit["review"].get("human_geo_note", ""))
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
