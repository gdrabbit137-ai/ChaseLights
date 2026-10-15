"""Task T controls around the existing Task P executor; no model/network fallback."""
import datetime as dt
from decimal import Decimal
import re
import signal
from contextlib import contextmanager

MODEL = "gpt-6.1-sol"
APPROVER = "gdrabbit137-ai"
APPROVED_PATHS = (
    "ops/v2/automation/runner.py", "ops/v2/automation/activate.py",
    "ops/v2/automation/pilot_guard.py", "ops/v2/automation/single-pilot-policy.json",
    ".github/workflows/v2-codex-executor.yml",
    ".github/workflows/v2-integration.yml", "ops/v2/postmerge_verify.py",
    "ops/v2/run_integration.py", "ops/v2/integration_gate.py", "ops/v2/integration-sources.json",
    "ops/v2/automation/test_runner.py", "ops/v2/automation/test_pilot_guard.py",
)


@contextmanager
def request_deadline(seconds):
    """Total wall time, including connect/headers/body, on the Linux runner."""
    def expired(signum, frame):
        raise TimeoutError("REQUEST_DEADLINE")
    previous = signal.signal(signal.SIGALRM, expired)
    timer = signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
        if timer[0]:
            signal.setitimer(signal.ITIMER_REAL, *timer)


def validate_single(policy, stop, today=None):
    today = today or dt.datetime.now(dt.timezone.utc).date()
    if policy.get("single_pilot") is not True:
        raise stop("SINGLE_PILOT_POLICY_REQUIRED")
    if policy.get("model") != MODEL:
        raise stop("CODEX_MODEL_NOT_CONFIGURED")
    expected = {"max_runs_per_day": 1, "max_requests_per_run": 1, "max_retries": 0,
                "max_total_model_requests": 1, "max_concurrency": 1,
                "service_tier": "default", "reasoning_effort": "high", "approver_login": APPROVER}
    if any(policy.get(k) != v for k, v in expected.items()) or len(policy.get("tasks", [])) != 1:
        raise stop("SINGLE_PILOT_LIMITS_INVALID")
    if type(policy.get("max_input_tokens")) is not int or not 1000 <= policy["max_input_tokens"] <= 240000:
        raise stop("INPUT_TOKEN_LIMIT_INVALID")
    if policy["max_output_tokens"] > 4096 or policy["request_timeout_seconds"] > 90 or policy["max_ci_polls"] > 3:
        raise stop("SINGLE_PILOT_LIMITS_INVALID")
    # Rates pinned from official Standard short-context pricing; reserve all
    # input at the cache-write price and include a 10% processing margin.
    rates = {"input_usd_per_million": "2.00", "cached_input_usd_per_million": "0.10",
             "cache_write_usd_per_million": "2.50", "output_usd_per_million": "10.00",
             "processing_multiplier": "1.10"}
    if any(str(policy.get(k)) != v for k, v in rates.items()):
        raise stop("OFFICIAL_RATE_PROFILE_MISMATCH")
    try:
        checked = dt.date.fromisoformat(policy["pricing_verified_on_utc"])
        expiry = dt.date.fromisoformat(policy["pricing_expires_on_utc"])
        budgets = [Decimal(str(policy[k])) for k in ("daily_budget_usd", "run_budget_usd", "lifetime_budget_usd")]
    except (ValueError, KeyError, ArithmeticError):
        raise stop("PILOT_PRICE_REVIEW_INVALID") from None
    if not checked <= today <= expiry or not 0 <= (expiry - checked).days <= 1:
        raise stop("PILOT_PRICE_REVIEW_EXPIRED")
    if any(not n.is_finite() or not Decimal("0") < n <= Decimal("0.75") for n in budgets):
        raise stop("PILOT_BUDGET_INVALID")


def mutation_guard(path, method, data, stop):
    if method == "GET":
        return
    value = data or {}
    safe_task_ref = lambda x: isinstance(x, str) and re.fullmatch(r"refs/heads/codex/v2-auto-[a-z0-9][a-z0-9-]{1,60}", x)
    if method == "POST" and path == "/git/trees":
        entries = value.get("tree", [])
        safe = lambda p: p == "ops/v2/automation/state.json" or bool(re.fullmatch(r"ops/v2/automation/pilots/[a-z0-9][a-z0-9-]{1,60}\.json", str(p)))
        if len(entries) == 1 and safe(entries[0].get("path")) and entries[0].get("mode") == "100644" and entries[0].get("type") == "blob" and isinstance(entries[0].get("content"), str):
            return
    if method == "POST" and path == "/git/commits" and len(value.get("parents", [])) == 1:
        return  # An unreferenced Git object cannot update any branch.
    if method == "POST" and path == "/git/refs" and (safe_task_ref(value.get("ref")) or value.get("ref") == "refs/heads/automation/v2-autodev-state"):
        return
    if method == "PATCH" and path == "/git/refs/heads/automation/v2-autodev-state" and value.get("force") is False:
        return
    if method == "POST" and path == "/pulls" and value.get("draft") is True and value.get("base") == "main" and safe_task_ref("refs/heads/" + str(value.get("head"))):
        return
    raise stop("GITHUB_MUTATION_NOT_ALLOWED", "FAIL")


def authorize(gh, policy, environ, stop):
    validate_single(policy, stop)
    if policy.get("enabled") is not True:
        raise stop("EXECUTOR_DISABLED")
    if environ.get("GITHUB_EVENT_NAME") != "workflow_dispatch" or environ.get("GITHUB_REF") != "refs/heads/main" or environ.get("GITHUB_REPOSITORY") != "gdrabbit137-ai/ChaseLights" or environ.get("GITHUB_ACTOR") != APPROVER:
        raise stop("MANUAL_OWNER_APPROVAL_REQUIRED")
    if environ.get("V2_TASK_ID") != policy["tasks"][0]["id"] or environ.get("V2_OPERATION") not in {"run_pilot", "assess_ci"}:
        raise stop("APPROVED_TASK_OR_OPERATION_MISMATCH")
    source = environ.get("V2_APPROVED_MAIN_SHA", "")
    if not re.fullmatch(r"[0-9a-f]{40}", source) or gh.main() != source:
        raise stop("APPROVED_MAIN_SHA_MISMATCH")
    branch = gh.api("/branches/main")
    if branch.get("protected") is not True or branch.get("commit", {}).get("sha") != source:
        raise stop("MAIN_BRANCH_PROTECTION_UNVERIFIED")
    try:
        pr_id, comment_id = int(environ.get("V2_APPROVAL_PR", "")), int(environ.get("V2_APPROVAL_COMMENT_ID", ""))
        if min(pr_id, comment_id) <= 0:
            raise ValueError()
    except ValueError:
        raise stop("APPROVAL_COMMENT_REQUIRED") from None
    pr = gh.api("/pulls/" + str(pr_id))
    comment = gh.api(f"/issues/comments/{comment_id}")
    policy_blob = gh.file("ops/v2/automation/single-pilot-policy.json", source)[1]
    expected = f"APPROVE_SINGLE_W5_PILOT task={policy['tasks'][0]['id']} main={source} usd=0.75 model={MODEL} policy={policy_blob}"
    human = comment.get("user", {}).get("login") == APPROVER and comment.get("user", {}).get("type") == "User"
    if not pr.get("merged") or pr.get("draft") or pr.get("base", {}).get("ref") != "main" or pr.get("base", {}).get("repo", {}).get("full_name") != "gdrabbit137-ai/ChaseLights" or not human or comment.get("body", "").strip() != expected or comment.get("issue_url") != f"https://api.github.com/repos/gdrabbit137-ai/ChaseLights/issues/{pr_id}":
        raise stop("APPROVAL_NOT_CURRENT_OWNER_COMMENT")
    for path in APPROVED_PATHS:
        if gh.file(path, source)[1] != gh.file(path, pr["head"]["sha"])[1]:
            raise stop("APPROVED_EXECUTOR_OR_POLICY_DRIFT")
    checks = gh.api("/commits/" + pr["head"]["sha"] + "/check-runs?per_page=100")
    if checks.get("total_count", 101) > 100:
        raise stop("APPROVAL_CI_UNVERIFIED")
    latest_checks = {x["name"]: x for x in sorted(checks.get("check_runs", []), key=lambda x: x.get("id", 0))}
    for name in policy["required_checks"]:
        check = latest_checks.get(name, {})
        if check.get("head_sha") != pr["head"]["sha"] or check.get("status") != "completed" or check.get("conclusion") != "success" or check.get("app", {}).get("slug") != "github-actions":
            raise stop("APPROVAL_CI_UNVERIFIED")
    return {"operation": environ["V2_OPERATION"], "source_main_sha": source,
            "approval_pr": pr_id, "approval_comment_id": comment_id, "approver": APPROVER,
            "approval_head_sha": pr["head"]["sha"], "approved_policy_blob": policy_blob}
