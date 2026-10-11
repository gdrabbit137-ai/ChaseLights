"""Pinned W2 canonical fail-closed tests; synthetic observations are never live."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
# The fixture filename is historical. Its bytes are the canonical record at
# W2 #444's verified head, not the earlier W2 revision named in that filename.
W2_SOURCE_COMMIT = "8725bf13348dfae371ae8358930a25dd424a3361"
FIXTURE = ROOT / "fixtures" / "tw-026-P01.w2-fe52720.json"
BLOB_SHA = "3459ee2afd51ffa48c5b986aaf86d00bac80999e"
AT = "2026-10-09T12:00:00+00:00"
spec = importlib.util.spec_from_file_location("core_v2_evaluator", ROOT.parent / "evaluator.py")
evaluator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluator)


def test_observation(value):
    return {"test_only": True, "value": value, "provider": None,
            "source": None, "issued_at": None, "valid_at": None,
            "freshness": "unknown"}


class W2P01FailClosed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not FIXTURE.is_file():
            raise AssertionError("Pinned W2 canonical JSON is unavailable: " + str(FIXTURE))
        raw = FIXTURE.read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if actual != BLOB_SHA:
            raise AssertionError("W2 canonical Git blob mismatch: " + actual)
        cls.record = json.loads(raw)
        cls.contract = cls.record["condition_contract"]
        cls.condition = next(c for c in cls.contract["conditions"]
                             if c["id"] == "C-tw-026-P01-02")

    def assert_closed(self, result):
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertTrue(result["unknown"])
        self.assertIs(result["live_recommendation"], False)
        self.assertIsNone(result.get("score"))
        self.assertTrue(all(t["state"] == "UNKNOWN" for t in result["conditions"]))

    def test_real_condition_is_not_auto_ready(self):
        self.assertEqual(self.record["opportunity_id"], "tw-026-P01")
        self.assertEqual(self.condition["evaluation_mode"], "GUIDANCE")
        self.assertEqual(self.condition["validation_status"], "provisional")
        self.assertIsNone(self.condition["threshold"])
        self.assertIsNone(self.condition["model_binding"])

    def test_real_contract_has_no_auto_binding_or_threshold(self):
        self.assertEqual(self.record["lifecycle_status"], "evidence_review")
        self.assertEqual(self.contract["status"], "review")
        for condition in self.contract["conditions"]:
            with self.subTest(condition=condition["id"]):
                self.assertNotEqual(condition["evaluation_mode"], "AUTO")
                self.assertIsNone(condition["threshold"])
                self.assertIsNone(condition["model_binding"])
                self.assertNotEqual(condition["validation_status"], "validated")

    def test_foreign_provider_cannot_promote_taiwan_research_record(self):
        # The NWS is outside this Taiwan record's geographic coverage. A
        # caller-supplied provider name and test boolean cannot authenticate
        # local weather, establish a model binding, or promote research data.
        observations = {c["id"]: dict(test_observation(True),
                                     provider="NOAA_NWS", source="api.weather.gov")
                        for c in self.contract["conditions"]}
        result = evaluator.evaluate(self.contract, observations,
                                    {"lifecycle_status": "evidence_review",
                                     "research_only": True, "evaluated_at": AT})
        self.assert_closed(result)
        self.assertIn("CONTRACT_OR_OPPORTUNITY_NOT_APPROVED", result["reasons"])

    def test_guidance_rejects_any_synthetic_boolean(self):
        # Only the outer approval flags are varied to isolate the mode gate.
        contract = {"status": "approved", "conditions": [self.condition]}
        ready = {"lifecycle_status": "approved", "research_only": False,
                 "evaluated_at": AT}
        for value in (True, False, None):
            with self.subTest(value=value):
                result = evaluator.evaluate(contract,
                                            {self.condition["id"]: test_observation(value)},
                                            ready)
                self.assert_closed(result)
                self.assertEqual(result["conditions"][0]["reason"], "NON_AUTO_MODE")

    def test_provisional_gate_without_changing_w2(self):
        # Isolated TEST_ONLY input; never mutates W2's real GUIDANCE claim.
        synthetic = {"id": "TEST_ONLY_PROVISIONAL_GATE", "role": "REQUIRED",
                     "evaluation_mode": "AUTO", "unknown_policy": "propagate_unknown",
                     "validation_status": self.condition["validation_status"]}
        ready = {"lifecycle_status": "approved", "research_only": False,
                 "evaluated_at": AT}
        for value in (True, False):
            result = evaluator.evaluate({"status": "approved", "conditions": [synthetic]},
                                        {synthetic["id"]: test_observation(value)}, ready)
            self.assert_closed(result)
            self.assertEqual(result["conditions"][0]["reason"], "UNVALIDATED_CONDITION")

    def test_real_research_contract_has_no_live_or_provenance(self):
        ready = {"lifecycle_status": self.record["lifecycle_status"],
                 "research_only": True, "evaluated_at": AT}
        for value in (True, False, None):
            obs = {c["id"]: test_observation(value) for c in self.contract["conditions"]}
            result = evaluator.evaluate(self.contract, obs, ready)
            self.assert_closed(result)
            self.assertIn("CONTRACT_OR_OPPORTUNITY_NOT_APPROVED", result["reasons"])
            for trace in result["conditions"]:
                self.assertIsNone(trace.get("provider"))
                self.assertIsNone(trace.get("source"))
                self.assertIsNone(trace.get("issued_at"))
                self.assertIsNone(trace.get("valid_at"))
                self.assertIn(trace.get("freshness"), (None, "unknown"))


if __name__ == "__main__":
    unittest.main()
