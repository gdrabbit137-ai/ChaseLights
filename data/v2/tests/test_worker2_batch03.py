"""Worker 2 batch03 independent crosswalk and schema gates.

Run: python -m unittest discover -s data/v2/tests -p 'test_worker2_batch03.py' -v
The crosswalk gate runs even when Worker 1's schema is not yet merged.
"""
import copy
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "v2"
SCHEMA = ROOT / "specs" / "v2" / "schema" / "opportunity-v2.1.schema.json"
IDS = ("tw-016-P01", "tw-026-P01", "tw-026-P02")
CROSSWALK_FILES = tuple(sorted((
    "worker2_batch03_tw-016-P01.jsonl",
    "worker2_batch03_tw-026-P01.jsonl",
    "worker2_batch03_tw-026-P02_2.jsonl",
)))
LANGS = ("zh-TW", "en", "ja")
BASE_PATHS = {
    "name": "/name_i18n",
    "description": "/description_i18n",
    "camera": "/camera_contexts/0/access_notes_i18n",
    "safety": "/camera_contexts/0/safety_notes_i18n",
    "subject": "/targets/0/name_i18n",
    "camera-kind": "/camera_contexts/0/kind",
    "camera-geometry-status": "/camera_contexts/0/geometry/status",
    "camera-verification": "/camera_contexts/0/verification_status",
    "subject-geometry-kind": "/targets/0/geometry/kind",
    "subject-geometry-status": "/targets/0/geometry/status",
    "relation-type": "/observation_relations/0/type",
    "view": "/observation_relations/0/geometry_mode",
    "view-distance_m": "/observation_relations/0/distance_m",
    "view-azimuth_deg": "/observation_relations/0/azimuth_deg",
    "view-elevation_deg": "/observation_relations/0/elevation_deg",
    "navigation": "/navigation_targets/0/status",
    "navigation-type": "/navigation_targets/0/target_type",
    "navigation-label": "/navigation_targets/0/label_i18n",
    "navigation-lat": "/navigation_targets/0/lat",
    "navigation-lon": "/navigation_targets/0/lon",
    "navigation-confidence": "/navigation_targets/0/confidence",
    "readiness": "/readiness/research_level",
    "research-gap-1": "/readiness/gaps/0",
    "research-gap-2": "/readiness/gaps/1",
}


def resolve_pointer(document, pointer):
    if not pointer.startswith("/"):
        raise AssertionError("JSON pointer must start with /: " + pointer)
    result = document
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        result = result[int(token)] if isinstance(result, list) else result[token]
    return result


def expected_paths(document):
    paths = dict(BASE_PATHS)
    for number, _ in enumerate(document["condition_contract"]["conditions"], start=1):
        root = f"/condition_contract/conditions/{number - 1}"
        paths[f"condition-{number}"] = root
        paths[f"condition-{number}-threshold"] = root + "/threshold"
        paths[f"condition-{number}-unknown-policy"] = root + "/unknown_policy"
    return paths


def validate_crosswalk(docs, rows_by_file, evidence_ids):
    """Return all problems; missing/duplicate/mismatched claims never silently pass."""
    problems = []
    seen = {}
    expected = {}
    for oid, document in docs.items():
        for suffix, ptr in expected_paths(document).items():
            claim_id = f"H-{oid}-{suffix}"
            expected[claim_id] = f"data/v2/opportunities/{oid}.json#{ptr}"

    for filename in CROSSWALK_FILES:
        if filename not in rows_by_file:
            problems.append("missing crosswalk file: " + filename)
            continue
        for row in rows_by_file[filename]:
            cid = row.get("human_claim_id")
            if not isinstance(cid, str) or not cid:
                problems.append(f"{filename}: missing human_claim_id")
                continue
            if cid in seen:
                problems.append("duplicate human_claim_id: " + cid)
                continue
            seen[cid] = filename
            if row.get("consistency_status") not in ("OK", "PARTIAL", "UNKNOWN"):
                problems.append("MISMATCH/invalid status: " + cid)
            if cid not in expected:
                problems.append("unexpected claim: " + cid)
                continue
            machine_path = row.get("machine_path_or_fields")
            if machine_path != expected[cid]:
                problems.append("wrong machine path: " + cid)
                continue
            oid = machine_path.split("#", 1)[0].split("/")[-1][:-5]
            if not filename.startswith(f"worker2_batch03_{oid}"):
                problems.append("claim in wrong JSONL: " + cid)
            if not isinstance(row.get("evidence_refs"), list):
                problems.append("invalid evidence_refs: " + cid)
            elif not set(row["evidence_refs"]) <= evidence_ids:
                problems.append("unknown evidence reference: " + cid)
            try:
                value = resolve_pointer(docs[oid], machine_path.split("#", 1)[1])
            except (KeyError, IndexError, TypeError, ValueError, AssertionError) as exc:
                problems.append(f"broken pointer {cid}: {exc}")
                continue
            if isinstance(value, dict) and all(lang in value for lang in LANGS):
                actual_text = value["zh-TW"]
                if not all(isinstance(value[lang], str) and value[lang].strip() for lang in LANGS):
                    problems.append("missing locale: " + cid)
            elif isinstance(value, dict) and "role" in value:
                actual_text = value["role"] + "｜" + value["notes_i18n"]["zh-TW"]
                if value["role"] not in ("REQUIRED", "BLOCKER", "QUALITY"):
                    problems.append("invalid condition role: " + cid)
                if not all(isinstance(value["notes_i18n"].get(lang), str) and value["notes_i18n"][lang].strip() for lang in LANGS):
                    problems.append("condition missing locale: " + cid)
            elif value is None:
                actual_text = "unknown"
            else:
                actual_text = str(value)
            if str(row.get("human_text")) != actual_text:
                problems.append("human/machine text mismatch: " + cid)

    for cid in sorted(set(expected) - set(seen)):
        problems.append("missing human claim: " + cid)
    return problems


class CrosswalkGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = {oid: json.loads((DATA / "opportunities" / f"{oid}.json").read_text(encoding="utf-8")) for oid in IDS}
        cls.audit = json.loads((DATA / "audits" / "worker2_batch03_evidence.json").read_text(encoding="utf-8"))
        cls.rows = {}
        for name in CROSSWALK_FILES:
            path = DATA / "crosswalk" / name
            cls.rows[name] = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        cls.evidence_ids = {item["id"] for item in cls.audit["evidence"]}

    def test_crosswalk_exact_coverage_paths_and_text(self):
        errors = validate_crosswalk(self.docs, self.rows, self.evidence_ids)
        self.assertEqual([], errors, "\n".join(errors))

    def test_negative_duplicate_and_mismatch_fail(self):
        baseline = copy.deepcopy(self.rows)
        first = CROSSWALK_FILES[0]
        baseline[first].append(copy.deepcopy(baseline[first][0]))
        self.assertTrue(any("duplicate" in e for e in validate_crosswalk(self.docs, baseline, self.evidence_ids)))
        baseline = copy.deepcopy(self.rows)
        baseline[first][0]["consistency_status"] = "MISMATCH"
        self.assertTrue(any("MISMATCH" in e for e in validate_crosswalk(self.docs, baseline, self.evidence_ids)))
        baseline = copy.deepcopy(self.rows)
        baseline[first].pop()
        self.assertTrue(any("missing human claim" in e for e in validate_crosswalk(self.docs, baseline, self.evidence_ids)))
        baseline = copy.deepcopy(self.rows)
        baseline[first][0]["machine_path_or_fields"] = "data/v2/opportunities/tw-016-P01.json#/missing"
        self.assertTrue(any("wrong machine path" in e for e in validate_crosswalk(self.docs, baseline, self.evidence_ids)))

    def test_conditions_references_geometry_and_readiness(self):
        for oid, doc in self.docs.items():
            with self.subTest(oid=oid):
                self.assertEqual(oid, doc["opportunity_id"])
                self.assertEqual("2.1.0", doc["schema_version"])
                self.assertEqual("R1", doc["readiness"]["research_level"])
                self.assertEqual(["GEOMETRY_GAP", "RESEARCH_GAP"], doc["readiness"]["gaps"])
                self.assertNotIn("runtime_availability", doc["readiness"])
                self.assertNotEqual("approved", doc["lifecycle_status"])
                claims = {c["claim_id"] for c in doc["evidence_claims"]}
                cameras = {c["id"] for c in doc["camera_contexts"]}
                targets = {t["id"] for t in doc["targets"]}
                for field in ("name_i18n", "description_i18n"):
                    self.assertTrue(all(doc[field].get(lang, "").strip() for lang in LANGS))
                for claim in doc["evidence_claims"]:
                    self.assertNotEqual("MISMATCH", claim["audit_status"])
                    self.assertTrue(set(claim["evidence_refs"]) <= self.evidence_ids)
                for rel in doc["observation_relations"]:
                    self.assertIn(rel["camera_context_id"], cameras)
                    self.assertIn(rel["target_id"], targets)
                    self.assertTrue(set(rel["evidence_refs"]) <= self.evidence_ids)
                    if rel["geometry_mode"] == "unknown":
                        for key in ("distance_m", "azimuth_deg", "elevation_deg"):
                            self.assertIsNone(rel.get(key))
                for cam in doc["camera_contexts"]:
                    self.assertTrue(set(cam["evidence_refs"]) <= self.evidence_ids)
                    if cam["geometry"]["status"] == "unknown":
                        self.assertIsNone(cam["geometry"].get("geojson"))
                for nav in doc["navigation_targets"]:
                    self.assertTrue(set(nav["evidence_refs"]) <= self.evidence_ids)
                    if nav["status"] == "needs_review":
                        self.assertIsNone(nav.get("lat"))
                        self.assertIsNone(nav.get("lon"))
                for condition in doc["condition_contract"]["conditions"]:
                    self.assertIn(condition["role"], ("REQUIRED", "BLOCKER", "QUALITY"))
                    self.assertIn(condition["evaluation_mode"], ("AUTO", "GUIDANCE", "VERIFY"))
                    self.assertEqual("propagate_unknown", condition["unknown_policy"])
                    self.assertTrue(condition["claim_refs"] and set(condition["claim_refs"]) <= claims)
                    self.assertTrue(all(condition["notes_i18n"].get(lang, "").strip() for lang in LANGS))
                    if condition.get("threshold") is None:
                        self.assertEqual("none", condition.get("operator"))

    def test_audit_release_hold(self):
        manifest = self.audit["legacy_catalog_manifest"]
        self.assertEqual((216, 428), (manifest["places"], manifest["opportunities"]))
        self.assertFalse(manifest["canonical_import_complete"])
        self.assertEqual(0, self.audit["release_gate"]["approved"])
        self.assertEqual(set(IDS), set(self.audit["staged_opportunity_ids"]))


class SchemaGate(unittest.TestCase):
    def test_worker1_v21_schema(self):
        self.assertTrue(SCHEMA.is_file(), "BLOCKED: Worker 1 PR #428 schema is not merged in this branch")
        try:
            from jsonschema import Draft202012Validator, FormatChecker
        except ImportError as exc:
            self.fail("BLOCKED: install jsonschema>=4.23: " + str(exc))
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for oid in IDS:
            with self.subTest(opportunity=oid):
                errors = list(validator.iter_errors(json.loads((DATA / "opportunities" / f"{oid}.json").read_text(encoding="utf-8"))))
                self.assertEqual([], errors, "\n".join(str(e) for e in errors))


if __name__ == "__main__":
    unittest.main()
