import importlib.util
import pathlib
import unittest

MODULE = pathlib.Path(__file__).with_name("release_gate_snapshot.py")
spec = importlib.util.spec_from_file_location("release_gate_snapshot", MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def valid():
    return {
        "owner": "W5",
        "changed_paths": ["ops/v2/release_gate_snapshot.py"],
        "base_sha": "base",
        "current_main_sha": "base",
        "head_sha": "head",
        "tested_head_sha": "head",
        "draft": False,
        "mergeable": True,
        "branch_protection_satisfied": True,
        "required_reviews_satisfied": True,
        "human_evidence_signoff_required": False,
        "safety_refusal": False,
        "checks": {k: "success" for k in gate.REQUIRED_CHECKS},
        "source_sha_verified": True,
        "latest_main_spec_verified": True,
        "provenance_verified": True,
    }


class ReleaseGateTests(unittest.TestCase):
    def test_valid_snapshot(self):
        self.assertEqual(gate.validate(valid()), [])

    def test_missing_checks(self):
        x = valid()
        x["checks"].pop("localization")
        self.assertTrue(gate.validate(x))

    def test_skipped_check(self):
        x = valid()
        x["checks"]["tests"] = "skipped"
        self.assertTrue(gate.validate(x))

    def test_stale_main(self):
        x = valid()
        x["current_main_sha"] = "new"
        self.assertTrue(gate.validate(x))

    def test_stale_head(self):
        x = valid()
        x["tested_head_sha"] = "other"
        self.assertTrue(gate.validate(x))

    def test_missing_review(self):
        x = valid()
        x["required_reviews_satisfied"] = False
        self.assertTrue(gate.validate(x))

    def test_human_signoff(self):
        x = valid()
        x["human_evidence_signoff_required"] = True
        self.assertTrue(gate.validate(x))
        x["human_evidence_signoff"] = True
        self.assertEqual(gate.validate(x), [])

    def test_refusal(self):
        x = valid()
        x["safety_refusal"] = True
        self.assertTrue(gate.validate(x))

    def test_owner_escape(self):
        x = valid()
        x["changed_paths"] = ["apps/web-v2/app.js"]
        self.assertTrue(gate.validate(x))

    def test_missing_provenance(self):
        x = valid()
        x["provenance_verified"] = False
        self.assertTrue(gate.validate(x))

    def test_draft(self):
        x = valid()
        x["draft"] = True
        self.assertTrue(gate.validate(x))

    def test_missing_snapshot(self):
        self.assertTrue(gate.validate({}))


if __name__ == "__main__":
    unittest.main()
