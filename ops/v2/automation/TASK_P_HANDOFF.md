# Task P: bounded Actions → Codex executor

Owner: W5 / integration. **Disabled, live model E2E BLOCKED; no merge/deploy authorization.**

This is executable wiring and failure handling, not proof of an autonomous run. The
first live task is a new TEST_ONLY JSON provenance fixture under
`ops/v2/automation/pilots/`, with its own branch and Draft PR. The API uses a
reviewed **Codex model through the Responses API** with strict structured output,
not the interactive Codex CLI or a native Codex Cloud scheduler. It has no model
tools or shell execution. General W1–W4 code-generation adapters remain out of
the initial live scope; those tasks fail closed, even for otherwise owned paths.

## Verified starting state and reuse

Reviewed main: `5bfad32f31007450496ce10123318ac3e8e37aad`.
Read current AGENTS, R4.2 research/navigation, applicable V2 specs, existing W5
integration runner/watchdog, and actual PR/check snapshots. Generated Legacy
weather updates are not evidence of V2 executor development.

| Source | Exact observed HEAD | State at inspection | Use |
| --- | --- | --- | --- |
| #483 (Task M foundation) | `543169a5e4c6df50a08fcc07c96a700bf49e7b15` | open Draft | Reuse all six added files byte-for-byte; 16 original offline tests retained |
| #485 (earlier Task P validation document) | `b52495c073ab85f96eb97d3160af29ba7eb08e21` | open Draft | Documentation only; not a connected executor |
| #491 | `9710d77dae3338123e4d93a47c720c2f4f929a4e` | merged | Current A/B/C R1 research policy; initial integration run failed, schema passed |
| #492 | `ff944a781741606dc0d34c15374edd1aee057847` | merged | W1 pin integration; 38699547248 integration succeeded |
| #493 | `b8570555c5cb1080b9a18059addadab427ba8c52` | open Draft | W2 disposition handoff; 38699861755 integration failed; not imported |
| #494 | `577f4c31b302c4fd603222bef6dce419e36ea3a0` | open Draft | Stacked W5 pin; 38700042249 succeeded; not assumed merged/imported |
| #495 | `c41567edcfa9efe95111f3306d6410f1934e7062` | open Draft | Concurrent W2 Task Q, data-only; no executor/path overlap |
| #496 | `ba57ede02bfe004f49ac4b14b570d29bf18b96fa` | open Draft | Concurrent W1 Task R planning, no executor/path overlap |

Task N/O original programs/handoffs were **NOT FOUND / UNVERIFIED** in the inspected
main tree, recent PRs/issues/branches and accessible workspace artifacts. #485
records the same limitation. No claim to have read missing source or run Task O.
No Task U inventory is required or repeated. No worker schedules were altered.

The original #483 runbook is a historical proposal. Its conditional future
auto-merge discussion is **not** authorization for this implementation. Task P's
explicit no-merge/no-deploy requirement and current main specs take precedence.
`release_gate_snapshot.py` remains advisory; callers' boolean snapshots cannot
authorize publication. Existing 157-case integration gate/pins remain unchanged.

## Execution and trust boundaries

1. The new workflow runs credential-free validation on PRs. On main only,
   `workflow_dispatch` or six-hour schedule rereads **latest main** code/policy.
   Activation defaults false, validates limits/model/reviewed pricing, and checks
   required variable/secret presence without printing values. A disabled or
   missing setup produces a BLOCKED artifact and nonzero live job, not green E2E.
2. `actions/create-github-app-token@v2` mints a short-lived token restricted to
   this single repository. The workflow GITHUB_TOKEN has contents:read only.
   The App token is used only by trusted Python HTTP code; it is never placed
   in a model input or model-generated command. No model code is executed.
3. The runner reads immutable latest-main AGENTS, both R4.2 specs, **all V2
   Markdown specs and schemas**, verifies Git blob hashes and regular-file modes,
   and includes their actual contents/hash map in the request. A truncated tree,
   missing required spec, symlink or oversized context stops execution. The
   live policy must match this same main. Explicit dependency PR head pins must
   already be merged; no draft/fixture is presumed merged.
4. Only one reviewed W5 JSON pilot can be selected. Task IDs are versioned and
   stable across main changes. Any open/closed matching PR or pre-existing task
   branch stops replay. The persistent `automation/v2-autodev-state` Git branch
   records claims **before API use**, using single-parent commits and non-force
   fast-forward updates. Concurrent stale writers fail, retaining the winner.
   Task branches always start from the inspected source main. The state branch
   is bookkeeping only and must never be merged into main.
5. Default limits: one run/day; two API requests/run; at most one retry; one
   global live workflow at a time; 4096 output tokens; 300000 spec-context bytes;
   90-second requests; 12-minute job. A conservative UTF-8 input token bound plus
   8192 framing tokens and maximum output are reserved at reviewed per-token
   rates before **each** request. Configured daily budget is USD 1, with a hard
   policy ceiling of USD 5. Reservations are not refunded, including uncertain
   failures. Reported usage/cost is separate from reserved worst-case cost;
   neither is a verified billing invoice. Review reasoning-token billing and
   current model availability/rates before enabling. No free/zero-price guess.
6. Only HTTP 429/500/502/503/504 have a bounded identical-request retry after a
   new reservation. Refusal, HTTP 400/401/403, incomplete output, timeout,
   uncertain transport, malformed output and safety errors stop. No prompt
   rephrasing, fallback model/account, redirect or policy bypass. Retry/error
   codes, attempts, source/spec hashes, budget and successful usage are recorded
   in the ledger; raw API bodies/headers/exception strings are never logged.
7. The model returns a short summary only. Trusted code builds a TEST_ONLY JSON
   envelope with exact provenance and `merge_allowed=false`,
   `deployment_allowed=false`. The model cannot select files or edit policy,
   runner, workflows, Legacy or other owners. Final GitHub compare must show
   exactly the allowed file. Latest main/dependency checks repeat before
   publishing a distinct branch and Draft PR. An uncertain publication retains
   the claim/branch for manual recovery; automatic creation is never replayed.
8. Later scheduled invocations assess real exact-head checks/statuses without
   another model call (maximum three CI polls). W5 validates source main,
   unchanged PR head, owner diff, receipt byte digest/data contract, dependency
   pins, GitHub Actions check provenance and configured required checks.
   Required skipped/neutral/pending/missing checks are BLOCKED; failed checks
   are FAIL. Technical success is PASS with merge/deploy still false. Main
   movement, including generated-weather commits, is conservatively BLOCKED
   pending replan; it does not automatically spend again or rebase.

No required CI threshold is reduced. The PR's inapplicable live-executor job is
intentionally not executed; this is not a skipped unit test or live E2E PASS.

## Required manual configuration and first real E2E

No OpenAI key, App ID or App private key is available **in this Codex execution
environment**. GitHub connector GETs for Actions Secrets/Variables are not
supported; repository-side values/installation have not been verified. Existing
connector GitHub access is not the executor App installation. Do not copy its
credentials or substitute a personal token.

After W5 reviews this Draft PR and the user approves merging:

1. Create/install a dedicated GitHub App **only on ChaseLights** with repository
   **Contents: read/write, Pull requests: read/write, Checks: read, Commit
   statuses: read, Metadata: read**. No Administration, Secrets, Workflows-write,
   organization or production deployment permission is needed. Ensure repository
   rulesets allow this App's dedicated `codex/v2-auto-*` task branches and
   `automation/v2-autodev-state`; never grant main protection bypass. The token
   action discovers the repository installation; no installation-ID secret is
   needed. Verify current action permission input support before activation.
2. Configure Actions variable `V2_CODEX_APP_ID`; Actions secrets
   `V2_CODEX_APP_PRIVATE_KEY` (PEM) and `OPENAI_API_KEY` (a project-scoped key).
   Add a provider-side project budget/alert as a second limit. Never paste
   values into PRs, issues, task prompts or logs.
3. In a separate reviewed W5 policy PR, choose an available Codex Responses
   model with structured-output support, record reviewed input/output USD per
   million (including reasoning billing) and a GitHub pricing-review link.
   Confirm the one JSON pilot, task version, dependency pins, required check
   names, budget and one-run/day limits. Set enabled=true only after approval.
   A model name or price is deliberately not invented in this PR.
4. Merge only after user approval and current required checks. Dispatch
   `V2 Bounded Codex Executor` on main. Preserve the actual run URL, immutable
   source/spec hashes, ledger claim/reservations, real API usage, new branch and
   **automatically created Draft PR**. Then inspect that PR's real CI and W5
   outcome; a green unit-test workflow alone is insufficient. Waiting CI exits
   BLOCKED/nonzero intentionally; the next bounded invocation can assess it.
5. Trigger an actual provider refusal/failure only with an approved safe test
   scenario if available; otherwise keep live refusal evidence UNVERIFIED.
   Current refusal/rate-limit/timeout tests are explicit mocked unit tests.
   No fabricated request or fake credentials may be treated as live evidence.
6. W5 independently accepts the exact-head run, data contract and source pins,
   documents FAIL/BLOCKED recovery, and retains the user merge gate. No automatic
   merge or deployment step exists. W1–W4 need separately reviewed branch-aware
   task adapters and trusted tests; do not claim all workers enabled from this
   JSON pilot. Do not reset a failed/claimed ID to retry blindly: inspect state,
   orphan branch/PR and incurred reservations, then approve a new task version.

## Evidence and acceptance

Local raw results: `ops/v2/automation/evidence/local/`. Initial aggregate:
**125 PASS / 0 FAIL / 0 ERROR / 0 SKIP** (56 executor, 16 reused foundation,
17 unchanged W5 regression, 36 current W1 schema tests). Canonical fixture
validation passes separately. Preflight exits 2 with BLOCKED/NOT_RUN; it is
not counted as a failing test or a successful E2E. Existing full 157-case
integration is validated by the real PR Actions run, not claimed from a local
browser that is unavailable. CI run details and tested commit are recorded in
`evidence/github-runs.json` after real runs finish.

W5 acceptance must refresh PR/main heads and actual checks, confirm only W5
owned paths, byte-for-byte #483 provenance (see `sources.json`), required checks
with zero test skips, no Legacy changes, no new API call/cost in this delivery,
and BLOCKED live E2E. Enablement is **NOT READY** until configuration, approved
activation, a real model→Draft PR→CI run, and worker-specific adapters exist.

Next smallest task: W5 verifies the App installation and configures the three
named settings, then proposes the reviewed model/pricing/activation policy for
this one pilot. It must not enable W1–W5 bulk scheduling before live evidence.
