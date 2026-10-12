"""Security regression: a self-declared live FAVORABLE is not sufficient evidence.

The fixture models W2 tw-026-P01/C-tw-026-P01-02's GUIDANCE/provisional
condition with no provider, threshold or model binding. W3's evaluator is
test-only and must not be treated as live approval.
"""
import json
import copy
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

    def test_unknown_as_favorable_is_structurally_rejected(self):
        errors = self._errors("invalid_evaluation_unknown_as_favorable.json")
        self.assertTrue(errors, "SECURITY REGRESSION: critical UNKNOWN became FAVORABLE")

    def test_stale_or_test_only_cannot_claim_live_favorable(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        base = json.loads((FIXTURES / "valid_evaluation_unknown.json").read_text(encoding="utf-8"))
        # Structural-only specimen. The invented provider name is deliberately
        # not real approval; live use still needs external semantic verification.
        base.update(
            status="FAVORABLE", live_recommendation=True, freshness="FRESH",
            runtime_availability="FULL", unknown_reasons=[],
            model={"id": "synthetic-structural-only", "version": "0.1"},
            provider_runs=[{
                "run_id": "synthetic:1", "provider": "unverified-test-placeholder",
                "source": "synthetic", "provider_version": "1",
                "issued_at": base["issued_at"], "valid_at": base["valid_at"],
                "freshness": "FRESH",
            }],
        )
        base["provenance"]["test_only"] = False
        base["conditions"][0].update(
            verdict="PASS", unknown_reasons=[], provider_run_refs=["synthetic:1"],
        )
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        self.assertEqual(list(validator.iter_errors(base)), [],
                         "The mutation test requires a structurally valid starting record")
        for field, value in (("freshness", "STALE"), ("test_only", True)):
            with self.subTest(field=field):
                record = copy.deepcopy(base)
                if field == "test_only":
                    record["provenance"]["test_only"] = value
                else:
                    record[field] = value
                errors = list(validator.iter_errors(record))
                self.assertTrue(errors, "SECURITY REGRESSION: invalid live result was accepted")


if __name__ == "__main__":
    unittest.main()
