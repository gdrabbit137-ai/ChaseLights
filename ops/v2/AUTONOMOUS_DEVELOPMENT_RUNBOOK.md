# W5 autonomous development and release gates (proposal)

Status: **proposal / non-executable**. Owner: W5. This document does not grant GitHub Actions or Codex permissions and does not alter the production deployment. Owner authorized conditional auto-merge/deploy on 2026-10-13, subject to all existing required reviews, evidence, CI and repository policies.

## Worker contract
- W1: specs/v2/; W2: data/v2/; W3: packages/core-v2/ and packages/models-v2/; W4: apps/web-v2/; W5: ops/v2/, .github/workflows/, integration and deployment.
- Scheduled ChatGPT workers coordinate, but must not claim to invoke Codex Cloud or GitHub Actions unless a real trigger/action and permissions are verified.
- Coding executor must use an isolated task branch; never directly push main, reuse a worker branch for writes, or bypass a tool safety refusal. A refused operation is not an invitation to retry through another tool.
- Before any task, read latest main AGENTS.md, R4.2, specs/v2/ and relevant PRs. Record base SHA and owner. One task, one narrowly scoped PR.

## Required end-to-end workflow
1. **Intake:** W5 chooses a single owner-specific issue, validates dependencies, deduplicates by issue and task key, records exact main SHA and input artifact SHA. Concurrency group per owner/path prevents simultaneous edits.
2. **Execute:** an explicitly installed and permissioned coding executor checks out an isolated branch, applies narrow changes and runs owner tests. If executor is absent, report BLOCKED and stop; a ChatGPT schedule alone is not proof of execution.
3. **PR:** open a PR with task key, owner, changed paths, exact base/head SHA, source provenance, evidence, test logs, unknowns and rollback strategy. Never accept direct changes to Legacy.
4. **Gate:** verify latest-main spec review, source SHA, data/schema/crosswalk, provenance, lawful navigation, zh-TW/en/ja semantic parity, all applicable checks on exact PR HEAD, required human reviews and branch protection. Fail closed for missing, pending, stale, skipped or untrusted checks. Do not substitute synthetic PR-merge CI for post-merge main CI.
5. **Merge:** only W5 may merge after all gates pass, using GitHub API expected_head_sha; serialize merges and re-evaluate after main moves. Human evidence signoff is never auto-generated.
6. **Release:** deploy only via verified GitHub workflow for the merged main SHA. Confirm completed main CI, deployment success and public desktop/mobile smoke tests; preserve Legacy isolation. If validation fails, stop promotion and initiate documented rollback/escalation rather than claiming success.
7. **Audit:** append immutable task key, owner, input SHA, PR number, exact tested HEAD, check run URLs, reviews, merge SHA, deploy run URL, public verification and blockers. Idempotent reruns must not duplicate PRs.

## Release integrity
- Research R0–R3 or RAW_ONLY weather is not a live favorable forecast. UNKNOWN/NOT_EVALUABLE stays fail-closed until actual provider coverage, freshness, evidence, thresholds and calibration exist.
- Access/closure warnings do not alter photography scores, but unverified NavigationTarget must not generate directions.
- Keep all user-facing zh-TW, en, ja semantically equivalent. Never infer human evidence approval from CI alone.
- Do not publish or auto-merge if current branch protection or required reviewer approvals cannot be inspected.

## Implementation prerequisites (not yet verified)
- Confirm actual GitHub Actions workflow inventory, branch protection/rulesets, permissions, deployment environments, required status checks, CODEOWNERS and current Pages release path.
- Establish approved Codex executor identity, invocation interface, least-privilege token, secret handling, timeout, budget, concurrency and kill switch. No speculative API endpoints or undocumented automatic Work triggering.
- Add a dry-run-only W5 gate workflow with fixtures for stale SHA, missing review, failed/skipped checks, provenance mismatch, translation mismatch and blocked deployment; test before enabling write or release permissions.
- Explicitly distinguish orchestrator schedule, executor, merge gate and deploy workflow. If any component cannot be proven, report its limitation and do not advance release.

## Rollout
Phase 0: read-only inventory and baseline.
Phase 1: deterministic dry-run gate with failing-case tests.
Phase 2: isolated Codex execution to draft PR only.
Phase 3: W5 conditional auto-merge on verified policy and human gates.
Phase 4: post-merge main CI, gated deployment and public smoke with rollback.
