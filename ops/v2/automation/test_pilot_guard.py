#!/usr/bin/env python3
"""Task T local negative tests. Fake transports/approvals are NEVER live E2E."""
import argparse
import copy
import datetime as dt
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runner as r
import pilot_guard as g
from activate import activate
from test_runner import MemoryLedger, response

MAIN, HEAD, BLOB = "a" * 40, "b" * 40, "c" * 40
POLICY_PATH = Path(__file__).with_name("single-pilot-policy.json")


def policy():
    value = json.loads(POLICY_PATH.read_text())
    value["enabled"] = True
    today = dt.datetime.now(dt.timezone.utc).date()
    value["pricing_verified_on_utc"] = today.isoformat()
    value["pricing_expires_on_utc"] = (today + dt.timedelta(days=1)).isoformat()
    return value


class ApprovalGitHub:
    def __init__(self, p):
        self.p, self.calls, self.token = p, [], "FAKE_APPROVAL_READ_TOKEN"
        self.source = MAIN
        self.pr = {"merged": True, "draft": False, "head": {"sha": HEAD},
                   "base": {"ref": "main", "repo": {"full_name": r.REPO}}}
        self.comment = {"user": {"login": g.APPROVER, "type": "User"}, "issue_url": "https://api.github.com/repos/" + r.REPO + "/issues/501",
                        "body": f"APPROVE_SINGLE_W5_PILOT task={p['tasks'][0]['id']} main={MAIN} usd=0.75 model={g.MODEL} policy={BLOB}"}
        self.checks = [{"id": n, "name": name, "status": "completed", "conclusion": "success", "head_sha": HEAD,
                        "app": {"slug": "github-actions"}} for n, name in enumerate(p["required_checks"])]
        self.drift = None

    def main(self):
        return self.source

    def file(self, path, sha):
        return "{}", ("d" * 40 if path == self.drift and sha == MAIN else BLOB)

    def api(self, path, method="GET", data=None):
        self.calls.append((path, method))
        if path == "/branches/main": return {"protected": True, "commit": {"sha": self.source}}
        if path == "/pulls/501": return self.pr
        if path == "/issues/comments/123": return self.comment
        if path == "/commits/" + HEAD + "/check-runs?per_page=100": return {"total_count": len(self.checks), "check_runs": self.checks}
        raise AssertionError(path)


class PilotGuardTests(unittest.TestCase):
    def setUp(self):
        self.p = policy()
        self.gh = ApprovalGitHub(self.p)
        self.env = {"GITHUB_EVENT_NAME": "workflow_dispatch", "GITHUB_REF": "refs/heads/main", "GITHUB_REPOSITORY": r.REPO,
                    "GITHUB_ACTOR": g.APPROVER, "V2_TASK_ID": self.p["tasks"][0]["id"], "V2_OPERATION": "run_pilot",
                    "V2_APPROVED_MAIN_SHA": MAIN, "V2_APPROVAL_PR": "501", "V2_APPROVAL_COMMENT_ID": "123"}

    def blocked(self, code, fn, *args, **kwargs):
        with self.assertRaises(r.Stop) as caught: fn(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def auth(self):
        return g.authorize(self.gh, self.p, self.env, r.Stop)

    def test_candidate_is_disabled_with_short_price_expiry(self):
        p = json.loads(POLICY_PATH.read_text())
        self.assertIs(p["enabled"], False)
        self.assertEqual((dt.date.fromisoformat(p["pricing_expires_on_utc"]) - dt.date.fromisoformat(p["pricing_verified_on_utc"])).days, 1)

    def test_current_model_profile_validates(self):
        r.validate_policy(self.p, live=True)

    def test_expired_prices_block(self):
        self.blocked("PILOT_PRICE_REVIEW_EXPIRED", g.validate_single, self.p, r.Stop, dt.date.fromisoformat(self.p["pricing_expires_on_utc"]) + dt.timedelta(days=1))

    def test_future_prices_cannot_preauthorize(self):
        self.blocked("PILOT_PRICE_REVIEW_EXPIRED", g.validate_single, self.p, r.Stop, dt.date.fromisoformat(self.p["pricing_verified_on_utc"]) - dt.timedelta(days=1))

    def test_unreviewed_model_and_rate_changes_block(self):
        self.p["model"] = "gpt-5.3-codex"
        self.blocked("CODEX_MODEL_NOT_CONFIGURED", g.validate_single, self.p, r.Stop)
        self.p = policy(); self.p["cache_write_usd_per_million"] = "2.00"
        self.blocked("OFFICIAL_RATE_PROFILE_MISMATCH", g.validate_single, self.p, r.Stop)

    def test_retry_and_concurrency_cannot_expand(self):
        for key in ("max_total_model_requests", "max_concurrency", "max_requests_per_run", "max_runs_per_day"):
            p = policy();p[key] = 2
            self.blocked("SINGLE_PILOT_LIMITS_INVALID", g.validate_single, p, r.Stop)

    def test_fast_tier_or_low_reasoning_cannot_replace_profile(self):
        for key, val in (("service_tier", "fast"), ("reasoning_effort", "low"), ("max_retries", 1)):
            p = policy();p[key] = val
            self.blocked("SINGLE_PILOT_LIMITS_INVALID", g.validate_single, p, r.Stop)

    def test_no_long_context_surcharge(self):
        self.p["max_input_tokens"] = 272001
        self.blocked("INPUT_TOKEN_LIMIT_INVALID", g.validate_single, self.p, r.Stop)

    def test_budget_above_75_cents_rejected(self):
        self.p["lifetime_budget_usd"] = "0.76"
        self.blocked("PILOT_BUDGET_INVALID", g.validate_single, self.p, r.Stop)

    def test_conservative_worst_case_reservation(self):
        amount, bound = r.reservation(self.p, "x" * 1000)
        expected = (Decimal(bound) * Decimal("2.50") + Decimal(4096) * Decimal(10)) * Decimal("1.10") / Decimal(1000000)
        self.assertEqual(amount, expected)
        maximum = (Decimal(240000) * Decimal("2.50") + Decimal(4096) * Decimal(10)) * Decimal("1.10") / Decimal(1000000)
        self.assertEqual(maximum, Decimal("0.705056"))
        self.assertLess(maximum, Decimal("0.75"))

    def test_oversized_input_rejected_before_api(self):
        self.blocked("INPUT_TOKEN_BUDGET_EXCEEDED", r.reservation, self.p, "x" * 240001)

    def test_run_cost_cap_enforced(self):
        self.p["run_budget_usd"] = "0.001"
        self.blocked("RUN_BUDGET_LIMIT", r.reservation, self.p, "x")

    def test_lifetime_request_limit_survives_another_day(self):
        ledger = MemoryLedger();task = self.p["tasks"][0]
        r.claim(ledger, self.p, task, MAIN, "2026-10-15")
        ledger.data["tasks"]["prior"] = {"attempts": 1}
        self.blocked("LIFETIME_REQUEST_LIMIT", r.reserve, ledger, self.p, task, Decimal("0.1"))

    def test_lifetime_budget_includes_uncertain_prior_reservations(self):
        ledger = MemoryLedger();task = self.p["tasks"][0]
        r.claim(ledger, self.p, task, MAIN, "2026-10-15")
        ledger.data["days"]["2026-10-14"] = {"reserved_usd": "0.70"}
        self.blocked("LIFETIME_BUDGET_LIMIT", r.reserve, ledger, self.p, task, Decimal("0.10"))

    def test_payload_enforces_tier_reasoning_and_one_request(self):
        ledger = MemoryLedger();task = self.p["tasks"][0];day = dt.datetime.now(dt.timezone.utc).date().isoformat()
        r.claim(ledger, self.p, task, MAIN, day)
        calls = []
        def request(url, token, method, data, **kw):
            calls.append(data)
            self.assertEqual(data["service_tier"], "default")
            self.assertEqual(data["reasoning"], {"effort": "high"})
            self.assertEqual(data["max_output_tokens"], 4096)
            self.assertNotIn("tools", data)
            raise r.HTTPFailure(429)
        self.blocked("HTTP_429", r.generate, self.p, {}, {}, task, MAIN, ledger, "FAKE_API_KEY", request=request)
        self.assertEqual(len(calls), 1)
        self.assertEqual(ledger.data["tasks"][task["id"]]["attempt_log"][0]["status"], "HTTP_429")

    def test_real_wall_deadline_interrupts(self):
        with self.assertRaises(TimeoutError):
            with g.request_deadline(0.01): time.sleep(0.05)

    def test_success_preserves_actual_usage_and_response_identifiers(self):
        ledger = MemoryLedger();task = self.p["tasks"][0];day = dt.datetime.now(dt.timezone.utc).date().isoformat()
        r.claim(ledger, self.p, task, MAIN, day)
        obj = response(model=g.MODEL, service_tier="default", id="resp_FAKE_TEST_ONLY")
        result = r.generate(self.p, {}, {}, task, MAIN, ledger, "FAKE_KEY", request=lambda *a, **k: obj)
        rec = ledger.data["tasks"][task["id"]]
        self.assertEqual(rec["response_id"], "resp_FAKE_TEST_ONLY")
        self.assertEqual(rec["model"] if "model" in rec else obj["model"], g.MODEL)
        self.assertEqual(rec["usage"], obj["usage"])
        self.assertFalse(result["merge_allowed"])

    def test_unverified_returned_model_or_tier_blocks(self):
        for model, tier in (("wrong-model", "default"), (g.MODEL, "fast")):
            ledger = MemoryLedger();task = self.p["tasks"][0];day = dt.datetime.now(dt.timezone.utc).date().isoformat()
            r.claim(ledger, self.p, task, MAIN, day)
            self.blocked("RESPONSE_MODEL_OR_TIER_UNVERIFIED", r.generate, self.p, {}, {}, task, MAIN, ledger, "FAKE_KEY", request=lambda *a, **k: response(model=model, service_tier=tier))

    def test_explicit_owner_comment_authorizes_only_bound_task(self):
        result = self.auth()
        self.assertEqual(result["approval_comment_id"], 123)
        self.assertEqual(result["source_main_sha"], MAIN)
        self.assertTrue(all(method == "GET" for _, method in self.gh.calls))

    def test_schedule_pr_other_actor_and_other_repo_block(self):
        for key, val in (("GITHUB_EVENT_NAME", "schedule"), ("GITHUB_EVENT_NAME", "pull_request"), ("GITHUB_ACTOR", "someone-else"), ("GITHUB_REPOSITORY", "other/repo"), ("GITHUB_REF", "refs/heads/worker")):
            saved = self.env[key];self.env[key] = val
            self.blocked("MANUAL_OWNER_APPROVAL_REQUIRED", self.auth)
            self.env[key] = saved

    def test_unknown_task_and_operation_block(self):
        self.env["V2_TASK_ID"] = "another-task"
        self.blocked("APPROVED_TASK_OR_OPERATION_MISMATCH", self.auth)

    def test_main_drift_stops_before_approval_or_ledger_reads(self):
        self.gh.source = "d" * 40
        self.blocked("APPROVED_MAIN_SHA_MISMATCH", self.auth)
        self.assertEqual(self.gh.calls, [])

    def test_unprotected_main_blocks_activation(self):
        original = self.gh.api
        self.gh.api = lambda path, *a, **k: {"protected": False, "commit": {"sha": MAIN}} if path == "/branches/main" else original(path, *a, **k)
        self.blocked("MAIN_BRANCH_PROTECTION_UNVERIFIED", self.auth)

    def test_disabled_profile_never_reaches_approval_or_network(self):
        self.p["enabled"] = False
        report = activate(self.p, {k: "FAKE" for k in ["OPENAI_API_KEY", "GH_APP_ID", "GH_APP_PRIVATE_KEY"]}, self.gh)
        self.assertEqual(report["code"], "EXECUTOR_DISABLED")
        self.assertEqual(self.gh.calls, [])

    def test_approval_comment_id_required(self):
        self.env.pop("V2_APPROVAL_COMMENT_ID")
        self.blocked("APPROVAL_COMMENT_REQUIRED", self.auth)

    def test_comment_cannot_be_bot_or_other_user(self):
        self.gh.comment["user"]["type"] = "Bot"
        self.blocked("APPROVAL_NOT_CURRENT_OWNER_COMMENT", self.auth)

    def test_comment_revocation_or_budget_edit_blocks(self):
        self.gh.comment["body"] = "REVOKED"
        self.blocked("APPROVAL_NOT_CURRENT_OWNER_COMMENT", self.auth)

    def test_comment_on_different_pr_cannot_be_replayed(self):
        self.gh.comment["issue_url"] = "https://api.github.com/repos/" + r.REPO + "/issues/502"
        self.blocked("APPROVAL_NOT_CURRENT_OWNER_COMMENT", self.auth)

    def test_unmerged_activation_pr_blocks(self):
        self.gh.pr["merged"] = False
        self.blocked("APPROVAL_NOT_CURRENT_OWNER_COMMENT", self.auth)

    def test_approved_runner_or_policy_drift_blocks(self):
        for path in g.APPROVED_PATHS:
            self.gh.comment["body"] = f"APPROVE_SINGLE_W5_PILOT task={self.p['tasks'][0]['id']} main={MAIN} usd=0.75 model={g.MODEL} policy={('d' * 40) if path.endswith('single-pilot-policy.json') else BLOB}"
            self.gh.drift = path
            self.blocked("APPROVED_EXECUTOR_OR_POLICY_DRIFT", self.auth)

    def test_approval_ci_failure_skip_missing_and_spoof_block(self):
        for state in ("failure", "skipped", None):
            self.gh.checks[0]["conclusion"] = state
            self.blocked("APPROVAL_CI_UNVERIFIED", self.auth)
        self.gh.checks[0]["conclusion"] = "success"
        self.gh.checks[0]["app"]["slug"] = "spoof"
        self.blocked("APPROVAL_CI_UNVERIFIED", self.auth)

    def test_legacy_policy_cannot_activate_model(self):
        old = json.loads(Path(__file__).with_name("policy.json").read_text())
        self.blocked("SINGLE_PILOT_POLICY_REQUIRED", g.authorize, self.gh, old, self.env, r.Stop)

    def test_missing_credentials_never_performs_approval_network_calls(self):
        report = activate(self.p, {}, self.gh)
        self.assertEqual(report["code"], "MISSING_EXECUTOR_CREDENTIALS")
        self.assertEqual(self.gh.calls, [])

    def test_mutation_api_blocks_main_force_merge_deploy_and_cross_owner(self):
        attempts = [("/git/refs", "POST", {"ref": "refs/heads/main"}),
                    ("/git/refs/heads/main", "PATCH", {"force": False}),
                    ("/git/refs/heads/automation/v2-autodev-state", "PATCH", {"force": True}),
                    ("/pulls/1/merge", "PUT", {}), ("/deployments", "POST", {}),
                    ("/issues/1/comments", "POST", {"body": "approve myself"}),
                    ("/git/trees", "POST", {"tree": [{"path": "apps/web-v2/x", "mode": "100644", "type": "blob", "content": "x"}]}),
                    ("/pulls", "POST", {"draft": False, "base": "main", "head": "codex/v2-auto-test-task"})]
        with patch.object(r, "http_json", side_effect=AssertionError("network reached")):
            gh = r.GitHub("FAKE")
            for path, method, data in attempts:
                self.blocked("GITHUB_MUTATION_NOT_ALLOWED", gh.api, path, method, data)

    def test_mutation_api_allows_only_intended_writes(self):
        g.mutation_guard("/git/refs", "POST", {"ref": "refs/heads/codex/v2-auto-test-task"}, r.Stop)
        g.mutation_guard("/git/refs/heads/automation/v2-autodev-state", "PATCH", {"force": False}, r.Stop)
        g.mutation_guard("/pulls", "POST", {"draft": True, "base": "main", "head": "codex/v2-auto-test-task"}, r.Stop)

    def test_committed_pilot_fixtures_are_real_source_bound_test_data(self):
        # Before a real run there is no fixture; no fake output is synthesized.
        root = Path(__file__).resolve().parents[3]
        for path in Path(__file__).with_name("pilots").glob("*.json"):
            obj = json.loads(path.read_text())
            self.assertEqual(obj["status"], "TEST_ONLY")
            self.assertIs(obj["merge_allowed"], False);self.assertIs(obj["deployment_allowed"], False)
            self.assertEqual(path.stem, obj["task_id"])
            self.assertGreater(len(obj["spec_blobs"]), 3)
            for spec, blob in obj["spec_blobs"].items():
                actual = subprocess.check_output(["git", "-C", str(root), "rev-parse", obj["source_main_sha"] + ":" + spec], text=True).strip()
                self.assertEqual(actual, blob)
            self.assertLessEqual(len(obj["summary"]), 1200)


if __name__ == "__main__":
    parser = argparse.ArgumentParser();parser.add_argument("--out", required=True);args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PilotGuardTests))
    report = {"kind": "OFFLINE_SECURITY_TESTS_NOT_LIVE_E2E", "PASS": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
              "FAIL": len(result.failures), "ERROR": len(result.errors), "SKIP": len(result.skipped)}
    target = Path(args.out);target.parent.mkdir(parents=True, exist_ok=True);target.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report));sys.exit(0 if result.wasSuccessful() and not result.skipped else 1)
