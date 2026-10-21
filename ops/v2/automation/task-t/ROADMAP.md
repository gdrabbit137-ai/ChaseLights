# Task T — staged W1–W5 wiring plan

Owner W5. **Reviewable plan only; every stage disabled until its own approval.**
No stage is enabled by merging a document. One task, owner-specific source
branch, independent Draft PR, actual tests and W5 acceptance remain mandatory.
Do not import another owner's unmerged branch as though it were main.

| Stage | Owner and allowed output | Entry and acceptance gate |
| --- | --- | --- |
| 0 | W5 one existing JSON regression fixture under ops/v2/automation/pilots/ | Resolve Task T blockers; one explicit approved real API call, automatic Draft PR, actual CI and W5 PASS. Keep raw evidence and ledger cost. No merge/deploy. |
| 1 | W4: apps/web-v2/ only | After stage 0 acceptance, review a branch-aware adapter on actual latest W4 code (#487 remains Draft). Start with one low-risk test/localization change; require actual Node/browser coverage, source pins and trilingual semantics. Reuse #489/#490 contracts/index only after proper dependency integration. |
| 2 | W2: data/v2/ only | After W4 adapter acceptance, one maintenance record/test using verified canonical evidence; preserve R1 versus live status, UNKNOWN, safety warnings and semantic review. #495 remains Draft; do not overwrite its corrections. Research requires a separate read-only evidence-fetch boundary; never synthesize sources/GPS/timezones. |
| 3 | W3: packages/core-v2/ and packages/models-v2/ only | Reviewed evaluator adapter, exact W1/W2 inputs and trusted negative tests for UNKNOWN/NOT_EVALUABLE. Scientific thresholds, provider provenance and live promotion require independent gates. No API spend/scoring changes by implication. |
| 4 | W1: specs/v2/ only | Reviewed spec-governance adapter; smallest contract/test change, schema/reference validation and explicit W2/W3/W4 migration handoff. Reconcile #496 planning and #489 contracts with current main policy; do not silently supersede R4.2. |
| 5 | W5: ops/v2/ and .github/workflows/ | Coordinate already accepted worker PRs and source-pin transitions; verify exact merged candidate, dependency heads, all existing 157+ tests and new trusted discovery. No exemption for docs or skipped failures; no automatic merge/deploy. |

Each adapter is a separate W5 infrastructure Draft PR. Worker outputs remain
their own independent PRs; infrastructure never modifies worker-owned files.
Before each task read current main/R4.2/specs, inspect latest owner branch and
pending PRs, reject overlap, pin exact base/dependencies, constrain output paths
and reserve reviewed costs. A missing branch or field is BLOCKED/UNKNOWN.

The current executor only accepts the W5 JSON pilot. It does **not** yet provide
safe general code execution for these stages. Broader adapters must isolate
untrusted generated code/tests from OpenAI keys, GitHub write tokens and App
private keys; publish only from a trusted job after independent checks of
source SHA, patch/artifact digest, paths, modes, tested commit and real CI.
Model-written tests alone cannot approve model-written code. No shell/tool or
new path capability is granted by this roadmap.

For every new owner: begin manual-only, one task, one request, bounded budget,
no retry, no parallel execution. Review real evidence before proposing any
larger limit or schedule. Allow only nonoverlapping work after its own review;
never turn on all five workers at once. Stop on safety refusal, missing evidence,
cost/usage uncertainty, source drift, CI failure or duplicate task state.

W5 promotion packet per stage: owner/base/head/main SHA, applicable spec blobs,
dependency PR states, model/tokens/reserved and estimated cost, actual run URL,
Draft PR/files, raw PASS/FAIL/ERROR/SKIP, source/contract/locale/safety findings,
and explicit user-approved next scope. Public publication is a separate gate.
