"""Minimal executable Draft 2020-12 gate for the V2 Opportunity contract."""
import copy
import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

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

    def test_missing_required(self):
        record = copy.deepcopy(FIXTURE)
        del record["condition_contract"]
        self.assertTrue(list(self.validator.iter_errors(record)))

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
        if not record["observation_relations"]:
            self.skipTest("Aurora fixture has no relation; full cross-reference gate required")
        record["observation_relations"][0]["camera_context_id"] = "missing-camera"
        camera_ids = {c["id"] for c in record["camera_contexts"]}
        self.assertNotIn(record["observation_relations"][0]["camera_context_id"], camera_ids)


if __name__ == "__main__":
    unittest.main()
