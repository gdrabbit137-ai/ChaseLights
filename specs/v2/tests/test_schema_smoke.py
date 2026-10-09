"""Minimal executable Draft 2020-12 gate for the V2 Opportunity contract."""
import copy
import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from validate_contract import validate_record, validate_references

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schema/opportunity-v2.1.schema.json").read_text(encoding="utf-8"))
FIXTURE = json.loads((ROOT / "tests/fixtures/valid_aurora_draft.json").read_text(encoding="utf-8"))


class ContractSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Draft202012Validator.check_schema(SCHEMA)
        cls.validator = Draft202012Validator(SCHEMA, format_checker=FormatChecker())

    def test_valid_aurora(self):
        self.assertFalse(list(self.validator.iter_errors(FIXTURE)))
        self.assertEqual(validate_record(FIXTURE, SCHEMA), [])
        self.assertEqual(validate_references(FIXTURE), [])

    def test_missing_required(self):
        record = copy.deepcopy(FIXTURE)
        del record["condition_contract"]
        self.assertTrue(validate_record(record, SCHEMA))

    def test_unknown_policy_must_propagate(self):
        record = copy.deepcopy(FIXTURE)
        record["condition_contract"]["conditions"][0]["unknown_policy"] = "ignore"
        self.assertTrue(list(self.validator.iter_errors(record)))

    def test_locale_ja_required(self):
        record = copy.deepcopy(FIXTURE)
        del record["name_i18n"]["ja"]
        self.assertTrue(list(self.validator.iter_errors(record)))

    def test_relation_reference_integrity(self):
        record = copy.deepcopy(FIXTURE)
        self.assertTrue(record["observation_relations"], "fixture must exercise an actual relation")
        record["observation_relations"][0]["camera_context_id"] = "missing-camera"
        errors = validate_record(record, SCHEMA)
        self.assertIn("relation/relation:1: missing camera missing-camera", errors)

    def test_target_reference_integrity(self):
        record = copy.deepcopy(FIXTURE)
        record["observation_relations"][0]["target_id"] = "missing-target"
        errors = validate_record(record, SCHEMA)
        self.assertIn("relation/relation:1: missing target missing-target", errors)

    def test_condition_claim_reference_integrity(self):
        record = copy.deepcopy(FIXTURE)
        record["condition_contract"]["conditions"][0]["claim_refs"] = ["missing-claim"]
        errors = validate_record(record, SCHEMA)
        self.assertIn("condition/cond:1: missing claim missing-claim", errors)

    def test_evidence_reference_integrity(self):
        record = copy.deepcopy(FIXTURE)
        record["camera_contexts"][0]["evidence_refs"] = ["undeclared-evidence"]
        errors = validate_record(record, SCHEMA)
        self.assertIn("camera_contexts/cam:1: undeclared evidence ref undeclared-evidence", errors)

    def test_duplicate_camera_ids_rejected(self):
        record = copy.deepcopy(FIXTURE)
        record["camera_contexts"].append(copy.deepcopy(record["camera_contexts"][0]))
        errors = validate_record(record, SCHEMA)
        self.assertIn("duplicate camera_contexts id", errors)

    def test_duplicate_claim_ids_rejected(self):
        record = copy.deepcopy(FIXTURE)
        claim = {"claim_id": "claim:duplicate", "claim_type": "existence",
                 "evidence_refs": [], "audit_status": "UNKNOWN"}
        record["evidence_claims"].extend([claim, copy.deepcopy(claim)])
        errors = validate_record(record, SCHEMA)
        self.assertIn("duplicate evidence_claims claim_id", errors)

    def test_duplicate_relation_ids_rejected(self):
        record = copy.deepcopy(FIXTURE)
        record["observation_relations"].append(copy.deepcopy(record["observation_relations"][0]))
        errors = validate_record(record, SCHEMA)
        self.assertIn("duplicate observation_relations id", errors)

    def test_target_undeclared_evidence_rejected(self):
        record = copy.deepcopy(FIXTURE)
        record["targets"][0]["evidence_refs"] = ["undeclared-evidence"]
        errors = validate_record(record, SCHEMA)
        self.assertIn("targets/target:1: undeclared evidence ref undeclared-evidence", errors)

    def test_dynamic_aurora_without_observation_relations_is_valid(self):
        record = copy.deepcopy(FIXTURE)
        record["observation_relations"] = []
        self.assertEqual(validate_record(record, SCHEMA), [])

    def test_canonical_runtime_availability_rejected(self):
        """Run the real schema + reference validator; runtime state is not canonical."""
        for parent in ("readiness", None):
            with self.subTest(location=parent or "opportunity_root"):
                record = copy.deepcopy(FIXTURE)
                target = record[parent] if parent else record
                target["runtime_availability"] = "FULL"
                errors = validate_record(record, SCHEMA)
                self.assertTrue(
                    errors,
                    "The canonical schema must reject dynamic availability fields",
                )
                self.assertTrue(
                    any("runtime_availability" in error and "Additional properties" in error
                        for error in errors),
                    f"Expected an actual schema validator failure, got: {errors}",
                )

    def test_valid_declared_evidence_and_claim_reference(self):
        record = copy.deepcopy(FIXTURE)
        record["evidence_claims"].append({
            "claim_id": "claim:1", "claim_type": "camera_location",
            "evidence_refs": ["source:1"], "audit_status": "UNKNOWN"
        })
        record["camera_contexts"][0]["evidence_refs"] = ["source:1"]
        record["condition_contract"]["conditions"][0]["claim_refs"] = ["claim:1"]
        self.assertEqual(validate_record(record, SCHEMA), [])


if __name__ == "__main__":
    unittest.main()
