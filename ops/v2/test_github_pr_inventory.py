import importlib.util
import pathlib
import unittest

p = pathlib.Path(__file__).with_name("github_pr_inventory.py")
spec = importlib.util.spec_from_file_location("github_pr_inventory", p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class InventoryTests(unittest.TestCase):
    def test_read_only_success_and_unknown_authorization(self):
        seen = []
        def fake(path, token):
            seen.append(path)
            if path.endswith("/pulls/483"):
                return {"head": {"sha": "head"}, "base": {"sha": "base", "ref": "main"}, "draft": True, "mergeable": None}
            if path.endswith("/branches/main"):
                return {"commit": {"sha": "main-new"}}
            return {}
        result = mod.collect("owner", "repo", 483, fake)
        self.assertEqual(result["authorization"], "UNKNOWN")
        self.assertEqual(result["head_sha"], "head")
        self.assertEqual(result["current_main_sha"], "main-new")
        self.assertEqual(len(seen), 7)
        self.assertEqual(result["errors"], [])

    def test_missing_pr_stops(self):
        def fake(path, token):
            raise ValueError("not found")
        result = mod.collect("owner", "repo", 483, fake)
        self.assertIsNone(result["pull_request"])
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["authorization"], "UNKNOWN")

    def test_incomplete_pr_stops(self):
        def fake(path, token):
            return {"head": {}, "base": {}}
        result = mod.collect("owner", "repo", 483, fake)
        self.assertTrue(result["errors"])
        self.assertNotIn("check_runs", result)

    def test_partial_endpoint_failure_is_not_approval(self):
        def fake(path, token):
            if path.endswith("/pulls/483"):
                return {"head": {"sha": "head"}, "base": {"sha": "base", "ref": "main"}}
            if path.endswith("/protection"):
                raise ValueError("forbidden")
            return {}
        result = mod.collect("owner", "repo", 483, fake)
        self.assertEqual(result["authorization"], "UNKNOWN")
        self.assertIsNone(result["branch_protection"])
        self.assertTrue(result["errors"])


if __name__ == "__main__":
    unittest.main()
