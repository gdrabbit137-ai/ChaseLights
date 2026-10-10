# W5 Integration CI

Owner: W5. This change runs isolated research integration and does not merge owner PRs, enable live recommendations, modify Legacy, or deploy anything.

## Verified sources (2026-10-10)

The remote task branch starts at latest main `b136261c35ba5cf3f7dc290b21e231013e9d1ac0`. Initial local base was `7ff3ef03968c47a8c6f6ec1206a9553731e45420`; all reviewed specification/schema/test blobs were rechecked and identical on the newer main before remote branch creation. Latest-main AGENTS, R4.2 research/navigation, all V2 Markdown specifications, canonical schema and validator/test entry points were reviewed. `integration-sources.json` records their Git blob fingerprints. The workflow reads current main and fails if those reviewed contracts have changed; W5 must review and repin rather than silently accept drift.

| Source | Fixed commit | Test entry |
|---|---|---|
| W1 #431, `v2/w1-evaluation-result-v01-20261010` | `62591034f0969d68ee68ba6e9839585c058ea3f4` | Main canonical schema suite (15) plus only the five EvaluationResult extension files from W1 (2 tests) |
| W2 `v2/worker2-canonical-batch03-20261009` | `7f10e9bd2757449d72546155c66714880c6d3ab1` | `data/v2/tests/test_worker2_batch03.py` (5), three actual canonical records through `validate_contract.py` |
| W3 #435, `w3/v2-m3-evaluator-20261009` | `d24af0dbea61c158482bea9522ac36eac016843d` | `packages/core-v2/tests/test_*.py` (20) and compile check |
| W4 #436, `codex/v2-w4-contract-smoke-20261010` | `7cc1ac237f806c737113bc753e1e8d1996b07c43` | Six `*.test.mjs` files (22 test cases), explicit `browser-smoke.mjs` (6) |
| Reused W5 `worker5/v2-integration-ci-20261009-0659` | `7cff8d1fd7dc714093ba521a4c599e980c11e136` | `integration_gate.py`, seven contract tests, existing public browser script preserved |

PRs #436, #435, #431, #429 were open Drafts, not merged, when inspected. #429 (`572574e3514ea143b666cca13e55aeef815d63ab`) contains historical blockers; its old W3-missing diagnosis is superseded by executable #435. No W5 acceptance is implied. `worker5/v2-integration-gate-20261009-b` at `d5a8268095fee9a7778cc035e3ac9d0c913e057e` has no `ops/v2` integration program/tests or V2 integration workflow to reuse. The CI branch has no committed V2 integration workflow, consistent with the historical write blocker.

## What runs

The workflow checks out W5 task HEAD, current main, and all four owner sources with read-only contents permission and no persisted checkout credentials. `run_integration.py` copies checked-in, blob-verified owner files into an absent scratch directory. Only the W1 EvaluationResult extension is overlaid; older W1 architecture/schema/test files never replace current main contracts. Source directories and business code in the task branch are not modified.

The original **64** cases remain: main Schema 15 + W3 20 + W4 Node 22 + W5 contract 7. W1 EvaluationResult 2, main watchdog 3, W2 crosswalk/schema 5, W5 runner regression 6, and real browser smoke 6 bring the total to **86**. The three real-record validations, valid schema fixture, compile and local isolation commands are additional gates, not inflated unittest counts.

Every mandatory suite has an expected nonzero count. Zero discovery, FAIL, ERROR, SKIP, expected failure, cancellation/todo leaving fewer passes than cases, missing tooling, timeout, missing source or modified source blocks the gate. All groups run after successful assembly even if another group fails. Raw logs and JSON counts are saved, summarized in the Actions job, and uploaded with `if: always()`. Source/installation failure can stop earlier and must remain a failed job.

W4 fixtures and W3's P01 fixture must match the independently checked-out W2 Git blobs byte-for-byte. W4 Node tests use `WORKER2_DATA_DIR` pointing at those actual W2 canonical files. The browser consumes the existing pinned W2 originals/preview and asserts the no-live, no-Directions, localization, keyboard, import and unknown boundaries. Adversarial inputs in existing owner regression tests remain explicitly test-only; they do not replace real W2 validation.

The local browser test binds only 127.0.0.1, covers desktop/mobile and all three locales, and does not access or publish a production preview. The preserved old `v2_browser_smoke.mjs` is a separate public-deployment check; it is not run by this research CI. Production URL and human geographic/evidence/translation acceptance remain unverified.

The workflow tests these pinned source revisions. New worker revisions require explicit review and updating both the lock and workflow refs; green does not certify unseen worker commits or that these PRs are merged. W1's structural EvaluationResult schema cannot authenticate providers; W3 is test-only and still lacks a live Taiwan provider pipeline. Research-only, UNKNOWN/NOT_EVALUABLE and no-live-recommendation restrictions remain mandatory.

## Reproduce and hand off

With source checkouts under `work/sources/{main,w1,w2,w3,w4}`, Python 3.12/jsonschema 4.26.0, Node 24 and Playwright 1.57.0:

```sh
PLAYWRIGHT_MODULE=/absolute/path/to/playwright CHROMIUM_EXECUTABLE=/absolute/path/to/chromium \
python ops/v2/run_integration.py --sources-root work/sources --work-root work/integration --logs-dir work/logs
```

`work/integration` must not exist. Node uses `--test-isolation=none` so the Codex runtime reports individual test cases, not only test-file completion. All suites have bounded timeouts. CI installs Playwright's bundled Chromium; local execution may use the environment's system Chromium, which is recorded separately in the environment report.

The Codex environment's normal git fetch failed to connect to its injected proxy. Local sources were obtained via the authorized GitHub connector and reconstructed into sparse Git checkouts, verifying every copied blob, all tree hashes and the exact Git commit hashes. These are partial object stores, not complete clone/history downloads. The GitHub job must independently perform normal Actions checkouts. A local sandbox socket EPERM required the normal execution approval path for Chromium and the local server; this is unrelated to GitHub workflow-write authorization.

W5 must inspect the Draft PR, source manifest, latest-main gate, raw logs and actual GitHub run/job/check-run links, then independently accept. Keep these four statuses separate: local test result; workflow successfully written on GitHub; actual GitHub Check Run execution/conclusion; W5 acceptance. A draft workflow file or local green result establishes neither of the last two.

If GitHub denies `.github/workflows/` writes, stop that operation. Use GitHub Settings → Applications → Installed GitHub Apps → the actual Codex/ChatGPT GitHub app → Configure, with access to this repository and Workflows write permission if the app offers it. A repository owner must accept a permission-update request from the app publisher. Reconnecting alone cannot add a permission the app does not request. Alternatively, the owner can commit the reviewed patch through GitHub's branch editor or an explicitly configured authorized Git client. A fine-grained PAT used in that client needs Contents and Workflows read/write (and Pull requests write to create the PR); a classic PAT requires repository access plus `workflow`. Never paste credentials into chat or commit them. GitHub's job `permissions: contents: read` does not authorize the external client to write workflow files.
