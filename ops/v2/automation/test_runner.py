#!/usr/bin/env python3
"""Offline tests with explicit fakes. These are NOT live Codex/GitHub E2E evidence."""
import argparse
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runner as r
from activate import activate

MAIN, HEAD = "a" * 40, "b" * 40
POLICY = json.loads(Path(__file__).with_name("policy.json").read_text())


def policy():
    p = copy.deepcopy(POLICY)
    p.update(enabled=True, model="approved-codex-model", pricing_review="https://github.com/gdrabbit137-ai/ChaseLights/issues/1",
             input_usd_per_million="1", output_usd_per_million="2")
    return p


class MemoryLedger:
    def __init__(self):
        self.data, self.saves = {"days": {}, "tasks": {}}, 0

    def save(self):
        self.saves += 1

    def read(self):
        return self


class FakeGitHub:
    def __init__(self, task=None):
        self.token = "test-github-secret"
        self.task = task or policy()["tasks"][0]
        self.calls = []
        self.source = MAIN
        self.receipt = {"source_main_sha": MAIN, "spec_blobs": {}, "status": "TEST_ONLY", "merge_allowed": False, "deployment_allowed": False}
        self.text = json.dumps(self.receipt)
        self.pr = {"head": {"sha": HEAD}, "base": {"ref": "main"}, "draft": True, "state": "open", "merged": False}
        self.checks = [{"id": i, "name": name, "status": "completed", "conclusion": "success", "head_sha": HEAD, "app": {"slug": "github-actions"}} for i, name in enumerate(policy()["required_checks"])]
        self.files = [{"filename": self.task["path"], "status": "added"}]
        self.statuses = {"state": "success", "total_count": 0, "statuses": []}
        self.existing_prs = []
        self.branch_exists = False
        self.compare_wrong = False

    def main(self):
        return self.source

    def file(self, path, sha):
        return self.text, "c" * 40

    def api(self, path, method="GET", data=None):
        self.calls.append((method, path, data))
        if path.startswith("/pulls?state="):
            return self.existing_prs
        if path.startswith("/git/ref/heads/"):
            if self.branch_exists:
                return {"object": {"sha": HEAD}}
            raise r.HTTPFailure(404)
        if path.startswith("/compare/"):
            return {"files": self.files if not self.compare_wrong else [{"filename": "index.html", "status": "modified"}]}
        if "/check-runs?" in path:
            return {"total_count": len(self.checks), "check_runs": self.checks}
        if "/status?" in path:
            return self.statuses
        if path == "/pulls" and method == "POST":
            return {"number": 123, "html_url": "https://github.com/example/pull/123"}
        if path.startswith("/pulls/"):
            return self.pr
        raise AssertionError((method, path))

    def commit_files(self, parent, files, message):
        self.calls.append(("COMMIT", parent, files))
        return HEAD

    def create_ref(self, branch, sha):
        self.calls.append(("REF", branch, sha))

    def record(self):
        return {"task_id": self.task["id"], "head_sha": HEAD, "source_main_sha": MAIN,
                "spec_blobs": {}, "receipt_sha256": hashlib.sha256(self.text.encode()).hexdigest()}


def response(**changes):
    obj = {"status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": '{"summary":"Current specs require exact source provenance and independent W5 review."}'}]}],
           "usage": {"input_tokens": 100, "output_tokens": 30}}
    obj.update(changes)
    return obj


class ExecutorTests(unittest.TestCase):
    def setUp(self):
        self.p = policy()
        self.task = self.p["tasks"][0]
        self.ledger = MemoryLedger()
        r.claim(self.ledger, self.p, self.task, MAIN, "2026-10-15")

    def blocked(self, code, fn, *args, **kwargs):
        with self.assertRaises(r.Stop) as caught:
            fn(*args, **kwargs)
        self.assertEqual(code, caught.exception.code)
        return caught.exception

    def generate(self, request):
        return r.generate(self.p, {"AGENTS.md": "Reference rules"}, {"AGENTS.md": "c" * 40}, self.task, MAIN, self.ledger,
                          "test-openai-secret", ("test-github-secret",), request=request, pause=lambda n: None, today=lambda: "2026-10-15")

    def test_default_disabled_and_missing_secrets(self):
        report = activate(POLICY, {})
        self.assertFalse(report["ready"])
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(len(report["missing_configuration"]), 3)

    def test_enabled_policy_still_requires_credentials(self):
        self.assertEqual(activate(self.p, {})["code"], "MISSING_EXECUTOR_CREDENTIALS")

    def test_missing_pricing_blocks(self):
        self.p["input_usd_per_million"] = None
        self.blocked("PRICING_NOT_REVIEWED", r.validate_policy, self.p, True)

    def test_missing_model_blocks(self):
        self.p["model"] = None
        self.blocked("CODEX_MODEL_NOT_CONFIGURED", r.validate_policy, self.p, True)

    def test_non_codex_model_blocks(self):
        self.p["model"] = "general-model"
        self.blocked("CODEX_MODEL_NOT_CONFIGURED", r.validate_policy, self.p, True)

    def test_unreviewed_pricing_link_blocks(self):
        self.p["pricing_review"] = "https://example.com/review"
        self.blocked("PRICING_NOT_REVIEWED", r.validate_policy, self.p, True)

    def test_nonfinite_and_negative_prices_block(self):
        for value in ("NaN", "Infinity", "-1", "0"):
            with self.subTest(value=value):
                self.p["output_usd_per_million"] = value
                self.blocked("PRICING_NOT_REVIEWED", r.validate_policy, self.p, True)

    def test_no_unbounded_retry_or_budget(self):
        self.p["max_retries"] = 3
        self.blocked("INVALID_LIMIT_MAX_RETRIES", r.validate_policy, self.p)
        self.p = policy()
        self.p["daily_budget_usd"] = "6"
        self.blocked("BUDGET_ABOVE_PILOT_CAP", r.validate_policy, self.p, True)

    def test_retry_request_limit_consistency(self):
        self.p["max_requests_per_run"] = 1
        self.blocked("INVALID_RETRY_LIMIT", r.validate_policy, self.p)

    def test_owner_allowlist(self):
        for owner, prefix in r.OWNERS.items():
            self.assertTrue(r.owner_path(owner, prefix[0] + "test.json"))
            self.assertFalse(r.owner_path(owner, "index.html"))

    def test_traversal_absolute_empty_and_windows_paths_rejected(self):
        for path in ("ops/v2/../x", "/ops/v2/x", "ops/v2//x", "ops/v2/./x", "ops/v2/x\\y", "ops/v2/x\n"):
            self.assertFalse(r.owner_path("W5", path), path)

    def test_no_cross_owner_or_workflow_output(self):
        for key, value in (("owner", "W1"), ("path", ".github/workflows/x.yml"), ("path", "index.html"), ("kind", "shell")):
            task = {**self.task, key: value}
            self.blocked("TASK_OUTSIDE_PILOT_SCOPE", r.validate_task, task)

    def test_invalid_dependency_pin_rejected(self):
        self.task["dependencies"] = [{"pr": 494, "sha": "latest"}]
        self.blocked("INVALID_DEPENDENCY_PIN", r.validate_task, self.task)

    def test_unmerged_dependency_not_assumed(self):
        self.task["dependencies"] = [{"pr": 494, "sha": HEAD}]
        self.blocked("DEPENDENCY_UNMERGED_OR_MOVED", r.dependencies, FakeGitHub(), self.task)

    def test_closed_or_open_pr_duplicate_blocks(self):
        gh = FakeGitHub()
        gh.existing_prs = [{"state": "closed"}]
        self.blocked("TASK_PR_EXISTS", r.duplicate, gh, self.task)

    def test_orphan_branch_prevents_replay(self):
        gh = FakeGitHub()
        gh.branch_exists = True
        self.blocked("TASK_BRANCH_EXISTS", r.duplicate, gh, self.task)

    def test_claim_never_replayed(self):
        self.blocked("TASK_ALREADY_CLAIMED", r.claim, self.ledger, self.p, self.task, MAIN, "2026-10-16")

    def test_daily_run_limit(self):
        task = {**self.task, "id": "second-task"}
        self.blocked("DAILY_RUN_LIMIT", r.claim, self.ledger, self.p, task, MAIN, "2026-10-15")

    def test_budget_reservation_before_call(self):
        def request(*a, **kw):
            self.assertGreater(self.ledger.saves, 1)
            self.assertGreater(float(self.ledger.data["days"]["2026-10-15"]["reserved_usd"]), 0)
            self.assertNotIn("test-github-secret", json.dumps(a[3]))
            self.assertNotIn("test-openai-secret", json.dumps(a[3]))
            return response()
        result = self.generate(request)
        self.assertFalse(result["merge_allowed"])
        self.assertEqual(result["source_main_sha"], MAIN)

    def test_insufficient_budget_never_calls_api(self):
        self.p["daily_budget_usd"] = "0.000001"
        self.blocked("DAILY_BUDGET_LIMIT", self.generate, lambda *a, **k: self.fail("API called"))

    def test_utc_rollover_never_bills_previous_day(self):
        self.ledger.data["tasks"][self.task["id"]]["day"] = "2026-10-14"
        self.blocked("UTC_DAY_CHANGED_REPLAN_REQUIRED", self.generate, lambda *a, **k: self.fail("API called"))

    def test_failed_ledger_persistence_never_calls_api(self):
        self.ledger.save = lambda: (_ for _ in ()).throw(r.Stop("LEDGER_CAS_CONFLICT"))
        self.blocked("LEDGER_CAS_CONFLICT", self.generate, lambda *a, **k: self.fail("API called"))

    def test_refusal_stops_without_retry_or_rephrase(self):
        calls = []
        def request(*a, **k):
            calls.append(a)
            return response(output=[{"type": "message", "content": [{"type": "refusal", "refusal": "safety refusal"}]}])
        self.blocked("SAFETY_REFUSAL", self.generate, request)
        self.assertEqual(len(calls), 1)
        self.assertEqual(self.ledger.data["tasks"][self.task["id"]]["attempts"], 1)

    def test_429_retries_bounded_with_separate_reservations(self):
        calls = []
        def request(*a, **k):
            calls.append(a[3])
            raise r.HTTPFailure(429)
        self.blocked("HTTP_429", self.generate, request)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0], calls[1])
        self.assertEqual(self.ledger.data["tasks"][self.task["id"]]["attempts"], 2)

    def test_server_retry_can_recover(self):
        calls = []
        def request(*a, **k):
            calls.append(1)
            if len(calls) == 1:
                raise r.HTTPFailure(503)
            return response()
        self.assertEqual(self.generate(request)["status"], "TEST_ONLY")
        self.assertEqual(len(calls), 2)

    def test_401_does_not_retry(self):
        calls = []
        def request(*a, **k):
            calls.append(1)
            raise r.HTTPFailure(401)
        self.blocked("HTTP_401", self.generate, request)
        self.assertEqual(len(calls), 1)

    def test_timeout_retains_reservation_and_does_not_retry(self):
        def request(*a, **k):
            raise r.Stop("TRANSPORT_UNCERTAIN")
        self.blocked("TRANSPORT_UNCERTAIN", self.generate, request)
        self.assertGreater(float(self.ledger.data["days"]["2026-10-15"]["reserved_usd"]), 0)
        self.assertEqual(self.ledger.data["tasks"][self.task["id"]]["attempts"], 1)

    def test_missing_usage_is_fail(self):
        self.assertEqual(self.blocked("USAGE_UNVERIFIABLE", self.generate, lambda *a, **k: response(usage={})).status, "FAIL")

    def test_over_output_limit_is_fail(self):
        self.blocked("USAGE_UNVERIFIABLE", self.generate, lambda *a, **k: response(usage={"input_tokens": 1, "output_tokens": 999999}))

    def test_secret_echo_rejected(self):
        obj = response()
        obj["output"][0]["content"][0]["text"] = '{"summary":"test-openai-secret"}'
        self.blocked("SECRET_IN_MODEL_OUTPUT", r.parse_response, obj, ("test-openai-secret",))

    def test_tool_output_rejected(self):
        self.blocked("UNEXPECTED_MODEL_TOOL_OUTPUT", r.parse_response, response(output=[{"type": "function_call"}]), ())

    def test_incomplete_and_model_error_not_retried(self):
        self.blocked("MODEL_INCOMPLETE", r.parse_response, response(status="incomplete"), ())
        self.blocked("MODEL_REJECTED_RESPONSE", r.parse_response, response(error={"code": "safety"}), ())

    def test_invalid_model_json_and_added_keys_rejected(self):
        for text, code in (("oops", "MODEL_OUTPUT_NOT_JSON"), ('{"summary":"ok","path":"index.html"}', "MODEL_OUTPUT_CONTRACT")):
            obj = response()
            obj["output"][0]["content"][0]["text"] = text
            self.blocked(code, r.parse_response, obj, ())

    def test_source_movement_blocks_publication(self):
        gh = FakeGitHub()
        gh.source = "c" * 40
        self.blocked("MAIN_MOVED_REPLAN_REQUIRED", r.publish, gh, self.task, MAIN, {})
        self.assertFalse(gh.calls)

    def test_cross_owner_diff_never_creates_branch(self):
        gh = FakeGitHub()
        gh.compare_wrong = True
        self.blocked("OWNER_DIFF_MISMATCH", r.publish, gh, self.task, MAIN, {})
        self.assertFalse(any(x[0] == "REF" for x in gh.calls))

    def test_publication_is_draft_only_no_merge_deploy(self):
        gh = FakeGitHub()
        result = r.publish(gh, self.task, MAIN, {"status": "TEST_ONLY"})
        self.assertEqual(result["head_sha"], HEAD)
        posts = [x for x in gh.calls if x[0] == "POST"]
        self.assertEqual(len(posts), 1)
        self.assertTrue(posts[0][2]["draft"])
        self.assertEqual(posts[0][2]["base"], "main")

    def test_w5_pass_is_technical_only(self):
        gh = FakeGitHub()
        report = r.assess(gh, 123, self.p, gh.record())
        self.assertEqual(report["status"], "PASS")
        self.assertFalse(report["merge_allowed"])

    def test_w5_failure_is_fail(self):
        gh = FakeGitHub()
        gh.checks[0]["conclusion"] = "failure"
        self.assertEqual(self.blocked("CI_FAILURE", r.assess, gh, 123, self.p, gh.record()).status, "FAIL")

    def test_w5_skipped_or_pending_is_blocked(self):
        for conclusion, status in (("skipped", "completed"), (None, "in_progress")):
            gh = FakeGitHub()
            gh.checks[0].update(conclusion=conclusion, status=status)
            self.blocked("REQUIRED_CI_NOT_SUCCESS", r.assess, gh, 123, self.p, gh.record())

    def test_w5_missing_check_is_blocked(self):
        gh = FakeGitHub()
        gh.checks.pop()
        self.blocked("REQUIRED_CI_NOT_SUCCESS", r.assess, gh, 123, self.p, gh.record())

    def test_w5_stale_source_and_head_block(self):
        gh = FakeGitHub()
        gh.source = "d" * 40
        self.blocked("MAIN_MOVED_REPLAN_REQUIRED", r.assess, gh, 123, self.p, gh.record())
        gh.source = MAIN
        gh.pr["head"]["sha"] = "d" * 40
        self.blocked("PR_HEAD_MOVED", r.assess, gh, 123, self.p, gh.record())

    def test_w5_changed_receipt_fail(self):
        gh = FakeGitHub()
        rec = gh.record()
        gh.text += " "
        self.assertEqual(self.blocked("RECEIPT_BLOB_MISMATCH", r.assess, gh, 123, self.p, rec).status, "FAIL")

    def test_w5_untrusted_check_app_blocks(self):
        gh = FakeGitHub()
        gh.checks[0]["app"]["slug"] = "untrusted"
        self.blocked("CHECK_APP_UNVERIFIED", r.assess, gh, 123, self.p, gh.record())

    def test_w5_status_failure_not_ignored(self):
        gh = FakeGitHub()
        gh.statuses = {"state": "failure", "total_count": 1, "statuses": [{"state": "failure"}]}
        self.assertEqual(self.blocked("COMMIT_STATUS_FAILURE", r.assess, gh, 123, self.p, gh.record()).status, "FAIL")

    def test_w5_latest_check_wins(self):
        gh = FakeGitHub()
        gh.checks.append({**gh.checks[0], "id": 999, "conclusion": "failure"})
        self.blocked("CI_FAILURE", r.assess, gh, 123, self.p, gh.record())

    def test_ledger_writes_are_fast_forward_only(self):
        class GH:
            def __init__(self): self.seen = []
            def api(self, path, method, data): self.seen.append((path, method, data))
        gh = GH()
        r.GitHub.advance(gh, "automation/v2-autodev-state", HEAD)
        self.assertEqual(gh.seen[0][2], {"sha": HEAD, "force": False})

    def test_redirects_and_untrusted_endpoints_rejected(self):
        self.blocked("UNTRUSTED_ENDPOINT", r.http_json, "https://example.org", "secret")
        self.blocked("REDIRECT_REJECTED", r.NoRedirect().redirect_request, None, None, 302, "", {}, "https://example.org")

    def test_read_specs_rejects_truncated_tree(self):
        class GH:
            def api(self, path): return {"truncated": True}
        self.blocked("SOURCE_TREE_TRUNCATED", r.read_specs, GH(), MAIN, 1000)

    def test_read_specs_rejects_missing_required_files(self):
        class GH:
            def api(self, path): return {"truncated": False, "tree": []}
        self.blocked("REQUIRED_SPECS_MISSING", r.read_specs, GH(), MAIN, 1000)

    def test_read_specs_rejects_symlink(self):
        class GH:
            def api(self, path):
                return {"truncated": False, "tree": [{"path": p, "mode": "120000", "type": "blob", "sha": HEAD} for p in [*r.REQUIRED_DOCS, "specs/v2/README.md"]]}
        self.blocked("SPEC_NOT_REGULAR_FILE", r.read_specs, GH(), MAIN, 1000)

    def run_with_fake_io(self, generate=None):
        gh = FakeGitHub()
        original_file = gh.file
        gh.file = lambda path, sha: (json.dumps(self.p), HEAD) if path.endswith("policy.json") else original_file(path, sha)
        ledger = MemoryLedger()
        with patch.object(r, "Ledger", return_value=ledger), patch.object(r, "read_specs", return_value=({"AGENTS.md": "rules"}, {})), patch.object(r, "generate", side_effect=generate or (lambda *a, **k: {"status": "TEST_ONLY"})):
            outcome = r.run(gh, self.p, "fake-key", "2026-10-15")
        return outcome, ledger, gh

    def test_fake_orchestration_claims_once_and_waits_for_real_ci(self):
        result, ledger, gh = self.run_with_fake_io()
        self.assertEqual(result["code"], "AWAITING_REAL_CI")
        self.assertEqual(ledger.data["tasks"][self.task["id"]]["status"], "AWAITING_CI")
        self.assertEqual(ledger.data["days"]["2026-10-15"]["runs"], 1)

    def test_fake_orchestration_refusal_is_terminal_and_recorded(self):
        gh = FakeGitHub()
        ledger = MemoryLedger()
        gh.file = lambda path, sha: (json.dumps(self.p), HEAD)
        with patch.object(r, "Ledger", return_value=ledger), patch.object(r, "read_specs", return_value=({}, {})), patch.object(r, "generate", side_effect=r.Stop("SAFETY_REFUSAL")):
            self.blocked("SAFETY_REFUSAL", r.run, gh, self.p, "fake-key", "2026-10-15")
            self.blocked("NO_UNCLAIMED_TASK", r.run, gh, self.p, "fake-key", "2026-10-15")
        self.assertEqual(ledger.data["tasks"][self.task["id"]]["code"], "SAFETY_REFUSAL")
        self.assertFalse(any(x[0] in {"COMMIT", "REF", "POST"} for x in gh.calls))

    def test_ci_poll_limit_terminal_without_model_calls(self):
        gh = FakeGitHub()
        gh.checks[0]["status"] = "in_progress"
        self.ledger.data["tasks"][self.task["id"]] = {**gh.record(), "status": "AWAITING_CI", "pr": 123, "ci_polls": self.p["max_ci_polls"] - 1}
        with patch.object(r, "Ledger", return_value=self.ledger), patch.object(r, "generate", side_effect=AssertionError("model called")):
            self.blocked("REQUIRED_CI_NOT_SUCCESS", r.run, gh, self.p, "fake-key", "2026-10-15")
        self.assertEqual(self.ledger.data["tasks"][self.task["id"]]["status"], "BLOCKED")

    def test_ledger_cas_conflict_stops_second_writer(self):
        class Store:
            def __init__(self):
                self.head, self.parents, self.contents, self.n = MAIN, {}, {MAIN: '{"days":{},"tasks":{}}'}, 0
            def main(self): return MAIN
            def api(self, path): return {"object": {"sha": self.head}}
            def file(self, path, sha): return self.contents[sha], HEAD
            def commit_files(self, parent, files, message):
                self.n += 1
                sha = str(self.n) * 40
                self.parents[sha] = parent
                self.contents[sha] = next(iter(files.values()))
                return sha
            def advance(self, branch, sha):
                if self.parents[sha] != self.head: raise r.HTTPFailure(422)
                self.head = sha
        gh = Store()
        first, stale = r.Ledger(gh, self.p["state_branch"]).read(), r.Ledger(gh, self.p["state_branch"]).read()
        r.claim(first, self.p, self.task, MAIN, "2026-10-15")
        self.blocked("HTTP_422", r.claim, stale, self.p, self.task, MAIN, "2026-10-15")
        self.assertEqual(r.Ledger(gh, self.p["state_branch"]).read().data["days"]["2026-10-15"]["runs"], 1)

    def test_spec_context_bound_and_hash(self):
        class GH:
            def api(self, path): return {"truncated": False, "tree": [{"path": p, "mode": "100644", "type": "blob", "sha": HEAD} for p in [*r.REQUIRED_DOCS, "specs/v2/README.md"]]}
            def file(self, path, sha): return "x" * 300, HEAD
        self.blocked("SPEC_CONTEXT_TOO_LARGE", r.read_specs, GH(), MAIN, 1000)
        gh = GH()
        gh.file = lambda path, sha: ("text", MAIN)
        self.blocked("SOURCE_TREE_BLOB_MISMATCH", r.read_specs, gh, MAIN, 2000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="work/task-p-tests.json")
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ExecutorTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {"kind": "OFFLINE_UNIT_TESTS_NOT_LIVE_E2E", "PASS": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
              "FAIL": len(result.failures), "ERROR": len(result.errors), "SKIP": len(result.skipped)}
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))
    sys.exit(0 if result.wasSuccessful() and not result.skipped else 1)
