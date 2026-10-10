"""Security regression: a self-declared live FAVORABLE is not sufficient evidence.

The fixture models W2 tw-026-P01/C-tw-026-P01-02's GUIDANCE/provisional
condition with no provider, threshold or model binding. W3's evaluator is
test-only and must not be treated as live approval.
"""
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema/evaluation-result-v0.1.schema.json"
FIXTURES = ROOT / "tests/fixtures/evaluation"


class EvaluationResultSecurityTests(unittest.TestCase):
    def _errors(self, filename):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        record = json.loads((FIXTURES / filename).read_text(encoding="utf-8"))
        return list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record))

    def test_unknown_research_only_result_is_structurally_valid(self):
        self.assertEqual(self._errors("valid_evaluation_unknown.json"), [])

    def test_forged_favorable_no_provider_is_structurally_rejected(self):
        errors = self._errors("invalid_evaluation_forged_favorable_no_provider.json")
        self.assertTrue(errors, "SECURITY REGRESSION: forged FAVORABLE passed JSON Schema")


if __name__ == "__main__":
    unittest.main()
