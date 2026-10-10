"""All inputs are synthetic TEST-ONLY fixtures, never live forecasts."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("w3_evaluator", Path(__file__).parents[1] / "evaluator.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
evaluate = module.evaluate

AT = "2026-10-09T12:00:00+00:00"


def condition(cid, role, mode="AUTO"):
    return {"id": cid, "role": role, "domain": "WEATHER", "evaluation_mode": mode,
            "capability": "CONDITIONS", "metric": "test_only_precomputed_boolean",
            "unknown_policy": "propagate_unknown", "claim_refs": ["TEST_ONLY"],
            "validation_status": "validated"}


def obs(value, **overrides):
    data = {"value": value, "test_only": True, "provider": "test-fixture",
            "source": "test-only", "issued_at": "2026-10-09T11:00:00+00:00",
            "valid_at": AT, "freshness": "fresh"}
    data.update(overrides)
    return data


class TestEvaluator(unittest.TestCase):
    def setUp(self):
        self.contract = {"status": "approved", "conditions": [condition("req", "REQUIRED"),
                         condition("block", "BLOCKER"), condition("quality", "QUALITY")]}
        self.readiness = {"lifecycle_status": "approved", "research_only": False,
                          "research_level": "R3", "evaluated_at": AT}

    def run_case(self, inputs, contract=None, readiness=None):
        return evaluate(contract or self.contract, inputs, readiness or self.readiness)

    def test_positive_test_only(self):
        result = self.run_case({"req": obs(True), "block": obs(False), "quality": obs(True)})
        self.assertEqual(result["decision"], "TEST_ONLY_CONDITIONS_MET")
        self.assertFalse(result["live_recommendation"])

    def test_area_opportunity_without_fixed_camera_geometry(self):
        # A place-specific, independently approved regional test contract can
        # evaluate without a point GPS, camera-to-target angle or viewpoint.
        readiness = dict(self.readiness, camera_contexts=[{
            "kind": "area", "geometry": {"status": "unknown", "geojson": None},
            "verification_status": "provisional"}],
            observation_relations=[], recommended_viewpoints=[])
        result = self.run_case({"req": obs(True), "block": obs(False)},
                               readiness=readiness)
        self.assertEqual(result["decision"], "TEST_ONLY_CONDITIONS_MET")
        self.assertIs(result["live_recommendation"], False)

    def test_precision_alignment_missing_geometry_is_claim_only_unknown(self):
        precision = condition("solar_alignment", "REQUIRED")
        precision["domain"] = "GEOMETRY_COMPOSITION"
        contract = {"status": "approved", "conditions": [
            condition("req", "REQUIRED"), condition("block", "BLOCKER"),
            precision]}
        result = self.run_case({"req": obs(True), "block": obs(False),
                                "solar_alignment": obs(True)}, contract=contract)
        self.assertEqual(result["decision"], "TEST_ONLY_CONDITIONS_MET")
        trace = next(t for t in result["conditions"]
                     if t["condition_id"] == "solar_alignment")
        self.assertEqual(trace["state"], "UNKNOWN")
        self.assertEqual(trace["reason"], "PRECISION_COMPOSITION_NOT_EVALUABLE")
        self.assertIs(result["live_recommendation"], False)

    def test_only_precision_claim_cannot_be_general_opportunity_pass(self):
        precision = condition("mirror_angle", "REQUIRED")
        precision["domain"] = "GEOMETRY_COMPOSITION"
        contract = {"status": "approved", "conditions": [precision]}
        result = self.run_case({"mirror_angle": obs(True)}, contract=contract)
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertTrue(result["unknown"])
        self.assertEqual(result["conditions"][0]["state"], "UNKNOWN")
        self.assertIs(result["live_recommendation"], False)

    def test_unknown_provider_still_blocks_regional_evaluation(self):
        result = self.run_case({"req": obs(True, provider=None),
                                "block": obs(False)})
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertIs(result["live_recommendation"], False)

    def test_research_only_cannot_be_live_even_without_camera_point(self):
        readiness = dict(self.readiness, research_only=True,
                         camera_contexts=[{"kind": "area", "geometry": None}])
        result = self.run_case({"req": obs(True), "block": obs(False)},
                               readiness=readiness)
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertIs(result["live_recommendation"], False)

    def test_negative_required_fail(self):
        result = self.run_case({"req": obs(False), "block": obs(False)})
        self.assertEqual(result["decision"], "BLOCKED")

    def test_negative_blocker_triggered_overrides_quality(self):
        result = self.run_case({"req": obs(True), "block": obs(True), "quality": obs(True)})
        self.assertEqual(result["decision"], "BLOCKED")

    def test_unknown_missing_blocker(self):
        result = self.run_case({"req": obs(True), "quality": obs(True)})
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertTrue(result["unknown"])

    def test_unknown_stale_required(self):
        result = self.run_case({"req": obs(True, freshness="stale"), "block": obs(False)})
        self.assertEqual(result["decision"], "UNKNOWN")

    def test_guidance_cannot_act_as_auto(self):
        contract = {"status": "approved", "conditions": [condition("req", "REQUIRED", "GUIDANCE")]}
        result = self.run_case({"req": obs(True)}, contract=contract)
        self.assertEqual(result["decision"], "UNKNOWN")

    def test_verify_cannot_act_as_auto(self):
        contract = {"status": "approved", "conditions": [condition("req", "REQUIRED", "VERIFY")]}
        result = self.run_case({"req": obs(True)}, contract=contract)
        self.assertEqual(result["decision"], "UNKNOWN")

    def test_research_only_never_ready(self):
        contract = {"status": "review", "conditions": self.contract["conditions"]}
        result = self.run_case({"req": obs(True), "block": obs(False)}, contract=contract)
        self.assertEqual(result["decision"], "UNKNOWN")

    def test_unapproved_contract_is_unknown_even_when_inputs_pass(self):
        contract = dict(self.contract, status="draft")
        result = self.run_case({"req": obs(True), "block": obs(False)}, contract=contract)
        self.assertEqual(result["decision"], "UNKNOWN")
        self.assertTrue(result["unknown"])

    def test_missing_provenance_is_unknown(self):
        result = self.run_case({"req": obs(True, source=""), "block": obs(False)})
        self.assertEqual(result["decision"], "UNKNOWN")

    def test_issued_after_valid_time_is_unknown(self):
        result = self.run_case({"req": obs(True, issued_at="2026-10-09T13:00:00+00:00"), "block": obs(False)})
        self.assertEqual(result["decision"], "UNKNOWN")

    def test_invalid_time_is_unknown(self):
        result = self.run_case({"req": obs(True, valid_at="2026-10-10T12:00:00+00:00"), "block": obs(False)})
        self.assertEqual(result["decision"], "UNKNOWN")

    def test_non_test_input_is_unknown(self):
        result = self.run_case({"req": obs(True, test_only=False), "block": obs(False)})
        self.assertEqual(result["decision"], "UNKNOWN")

    def test_boolean_not_coerced_from_number(self):
        result = self.run_case({"req": obs(1), "block": obs(False)})
        self.assertEqual(result["decision"], "UNKNOWN")

    def test_research_level_not_runtime_availability(self):
        readiness = dict(self.readiness, research_level="R1")
        result = self.run_case({"req": obs(True), "block": obs(False)}, readiness=readiness)
        self.assertEqual(result["decision"], "TEST_ONLY_CONDITIONS_MET")

    def test_unknown_quality_does_not_override_critical(self):
        result = self.run_case({"req": obs(True), "block": obs(False)})
        self.assertEqual(result["decision"], "TEST_ONLY_CONDITIONS_MET")


if __name__ == "__main__":
    unittest.main()
