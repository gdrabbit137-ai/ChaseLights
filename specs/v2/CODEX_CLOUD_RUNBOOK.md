# ChaseLights V2 — Codex Cloud mobile onboarding and first batch

Status: onboarding instructions and task briefs, **not evidence Codex Cloud has been authorized or has run tasks**.

## Connect from an iPhone
1. Open [Codex](https://chatgpt.com/codex) in Safari or the ChatGPT-supported Codex Cloud interface, sign in to your ChatGPT account.
2. If prompted, connect GitHub and approve **only** the `gdrabbit137-ai/ChaseLights` repository for the Codex Cloud integration. GitHub access within ChatGPT alone does not confirm Codex Cloud authorization.
3. In Codex Cloud on the web, create **and publish** a reusable personal environment for `gdrabbit137-ai/ChaseLights`. Name it `ChaseLights-V2`. Verify Python 3, `jsonschema`, Node.js, git and test commands. Use no secrets or production API tokens for the first batch; standard cloud compute is sufficient. Then Codex Cloud tasks can start or continue on mobile.
4. Choose a dedicated task branch (instructions below), not an existing worker branch. Do not grant automatic merge/deploy permission. If the Codex environment UI does not allow branch selection, ask Codex to report and stop rather than changing main.
5. Start with **Task A only**. Submit its PR and ask W5 to verify before commissioning Task B.

Cloud environment setup command (optional if jsonschema absent): `python -m pip install 'jsonschema>=4.18,<5'`. JavaScript tests use Node's built-in test runner.

## Preflight: critical branch facts
- `specs/v2/` Schema v2.1 is on main (PR #428 merged). Read the current main SHA each run.
- `data/v2/`, `packages/core-v2/`, and `apps/web-v2/` may **not** be on main. Inspect the true latest W2/W3/W4 branches before starting. Never build a W3/W4 feature from main without bringing in its owner branch code safely.
- Five hourly ChatGPT workers remain active. Do not concurrently edit the same paths as a worker; create a separate `codex/v2-<task>-<date>` branch and coordinate merge/rebase with W5. If the owner has already completed the selected item, choose the next issue supported by actual evidence rather than recreating it.

## Task A — W4: real-data and localization/browser regression (first)
Owner: W4 (`apps/web-v2/` only).
Starting code: `worker4/v2-website-v21-m4-20261009` at **latest** fetched HEAD (not an old memorized SHA).
New branch: `codex/v2-w4-contract-smoke-<date>`.

Copy/paste to Codex:
> Investigate the latest W4 V2 research-preview website from `worker4/v2-website-v21-m4-20261009`, plus latest main specs and W2 `v2/worker2-canonical-batch03-20261009` canonical data. First report current W4 branch SHA and whether zh-TW/en/ja skip-link and ARIA updates already exist; do not repeat completed work. Create an isolated Codex task branch from the latest W4 code. Only change `apps/web-v2/`. Build a non-SKIP regression using a **real, fixed-SHA W2 research-only preview/catalog** and verify three-language switch (visible text and ARIA/keyboard interaction), no verified NavigationTarget → no Directions, no synthetic runtime recommendation, and mobile/desktop browser behavior when available. Preserve actual evidence and unknowns. Run `node --test apps/web-v2/tests/*.test.mjs`, record exact PASS/FAIL/SKIP, and do a real browser smoke if the browser is available; otherwise report browser check UNVERIFIED. Create a PR with test logs. Do not modify another worker's branch, main, Legacy code or GitHub workflows. Do not merge.

Acceptance: a GitHub PR with a fresh branch, real test output, actual source fixture ID+SHA, no unsafely promoted research-only state, and W5 review.

## Task B — W3: deterministic fail-closed evaluation regression (after A)
Owner: W3 (`packages/core-v2/`, `packages/models-v2/` only).
Starting code: `w3/v2-m3-evaluator-20261009` at current HEAD.
New branch: `codex/v2-w3-unknown-regression-<date>`.

Copy/paste to Codex:
> Read latest main V2 specs, W2's real `tw-026-P01` canonical condition contract (fixed verified W2 commit), and W3 branch current evaluator. Create a distinct Codex task branch from latest `w3/v2-m3-evaluator-20261009`. Only change W3-owned `packages/` files. Add a repeatable negative test proving research-only/non-AUTO/provisional/no-threshold conditions yield UNKNOWN/NOT_EVALUABLE, not FAVORABLE, with test-only or unsupported-provider inputs. Preserve genuine source IDs and do not invent Taiwan observation values. Run unit tests and compile checks with actual logs. Create PR; do not merge or touch worker/main branches. If required real W2 files are unavailable, report BLOCKED/SKIP rather than substituting fake research data.

Acceptance: actual unit test execution, traceable W2 source ID/SHA, explicit fail-closed result, PR for W5.

## W5 handoff and anti-conflict gate
1. Confirm Codex Cloud GitHub access and new task PR; never infer Codex execution from an instruction file.
2. Snapshot worker branch HEAD before starting. If W4 is working on Task A's files, have W4 work on a nonoverlapping task or temporarily pause **only after the Codex task is actually running**; restore promptly.
3. Review actual diff, latest-main specs, correct branch base, localized semantics, and CI/test logs before merge. Do not approve purely on Codex claims.
4. Publish only a verified, clearly labeled V2 research preview independently of Legacy. Forecast goes live only with genuine W2/W3 evidence and valid inputs.
5. Track Codex usage; initial batch is only two bounded tasks, not unattended bulk dispatch. Never place GitHub credentials or weather API secrets in prompts or repository.
