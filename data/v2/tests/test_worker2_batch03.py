"""Worker 2 canonical batch03 release gates. Run after Worker 1 PR #428 schema lands."""
import json
import pathlib
import unittest

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:
    raise RuntimeError("Install jsonschema>=4.23 to run V2 schema gate") from exc

ROOT = pathlib.Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "v2"
SCHEMA = ROOT / "specs" / "v2" / "schema" / "opportunity-v2.1.schema.json"

class Worker2Batch03Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SCHEMA.exists():
            raise AssertionError("BLOCKED: Worker 1 schema PR #428 must land before this gate can pass")
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(cls.schema)
        cls.records = {}
        for path in sorted((DATA / "opportunities").glob("*.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            cls.records[path.name] = doc
        cls.audit = json.loads((DATA / "audits" / "worker2_batch03_evidence.json").read_text(encoding="utf-8"))
        cls.crosswalk = [json.loads(line) for line in (DATA / "crosswalk" / "worker2_batch03.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]

    def test_v21_schema_and_refs(self):
        registry = {x["id"] for x in self.audit["evidence"]}
        validator = Draft202012Validator(self.schema, format_checker=FormatChecker())
        for filename, doc in self.records.items():
            with self.subTest(filename=filename):
                self.assertEqual([], list(validator.iter_errors(doc)))
                cameras = {x["id"] for x in doc["camera_contexts"]}
                targets = {x["id"] for x in doc["targets"]}
                claims = {x["claim_id"] for x in doc["evidence_claims"]}
                for relation in doc["observation_relations"]:
                    self.assertIn(relation["camera_context_id"], cameras)
                    self.assertIn(relation["target_id"], targets)
                for claim in doc["evidence_claims"]:
                    self.assertTrue(set(claim["evidence_refs"]) <= registry)
                for condition in doc["condition_contract"]["conditions"]:
                    self.assertTrue(set(condition["claim_refs"]) <= claims)
                    self.assertEqual("propagate_unknown", condition["unknown_policy"])
                    if condition.get("threshold") is None:
                        self.assertEqual("none", condition.get("operator"))
                for cam in doc["camera_contexts"]:
                    if cam["geometry"]["status"] == "unknown":
                        self.assertIsNone(cam["geometry"].get("geojson"))
                for relation in doc["observation_relations"]:
                    if relation["geometry_mode"] == "unknown":
                        for key in ("azimuth_deg", "elevation_deg", "distance_m"):
                            self.assertIsNone(relation.get(key))
                for nav in doc["navigation_targets"]:
                    if nav["status"] == "needs_review":
                        self.assertIsNone(nav.get("lat"))
                        self.assertIsNone(nav.get("lon"))
                if doc["readiness"]["gaps"]:
                    self.assertNotEqual("approved", doc["lifecycle_status"])

    def test_crosswalk_machine_paths_and_roles(self):
        self.assertFalse(any(x["consistency_status"] == "MISMATCH" for x in self.crosswalk))
        condition_coverage = set()
        for row in self.crosswalk:
            file_name, pointer = row["machine_path_or_fields"].split("#", 1)
            doc = self.records[pathlib.Path(file_name).name]
            value = doc
            for part in pointer.lstrip("/").split("/"):
                value = value[int(part)] if isinstance(value, list) else value[part]
            suffix = row["human_claim_id"].split("-")[-1]
            if isinstance(value, dict) and "zh-TW" in value:
                self.assertEqual(value["zh-TW"], row["human_text"])
                self.assertTrue(all(value[lang].strip() for lang in ("zh-TW", "en", "ja")))
            elif isinstance(value, dict) and "role" in value:
                self.assertEqual(value["role"] + "｜" + value["notes_i18n"]["zh-TW"], row["human_text"])
                condition_coverage.add(value["id"])
            else:
                self.assertEqual(value, row["human_text"])
        all_conditions = {c["id"] for d in self.records.values() for c in d["condition_contract"]["conditions"]}
        self.assertEqual(all_conditions, condition_coverage)

    def test_audit_release_hold(self):
        self.assertEqual(216, self.audit["legacy_catalog_manifest"]["places"])
        self.assertEqual(428, self.audit["legacy_catalog_manifest"]["opportunities"])
        self.assertFalse(self.audit["legacy_catalog_manifest"]["canonical_import_complete"])
        self.assertEqual(0, self.audit["release_gate"]["approved"])
        self.assertEqual({"tw-016", "tw-021", "tw-026", "tw-031", "tw-036"}, {p["id"] for p in self.audit["audited_places"]})

if __name__ == "__main__":
    unittest.main()
