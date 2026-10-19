# W4 Photography Topics First — independent review handoff

Owner: W4; changes only `apps/web-v2/`. Research-only, no merge/deployment.

## Source and scope

- Base/latest reviewed main: `67a154b163c3e9a868d07eccc35f46d37580be38`.
- Tested implementation commit: `e2ddb85869742d254fc6d84b2ceaaddb053c43de`.
- Tested W4 subtree: `f8318e49e9bdfe95c141cafb38b8deef2028494b`.
- Previous W4 tree: `70eb22ad22f3cad08aafab9ac71032ee8278139b`.
- Prior owner pin: `ca4e59cf5978347f1422fb1fd2d485c188b58edd`.
- W2 index: `cf29288ce47e2cccb2fb2e1453ad193200996a95`.
- All eight per-record source commits, paths and Git blobs plus SHA256 of
  tested runtime/test files are in `source-provenance.json`. Catalog and index
  bytes are identical to base. Evidence-only commits after the tested commit
  do not change runtime/test source; W5 must pin the final PR tree separately.

Read main AGENTS, both R4.2 research/navigation specs, V2 overview, cloud
runbook, governance, topic/filter contract, free-composition and access policies.
Latest main remained the base SHA at final pre-submit review. No overlapping
open W4 implementation PR was found; W1 #496 remains unmerged planning.
W5 #517 head `52074b0590a521a1cc0aaa6666a1fa618606ca40` does not change W4;
its existing W4 tree/count assumptions still need deliberate coordination.

## Behavior

Each of seven Places lists its existing subjects (eight Opportunities total).
Names, descriptions, targets and conditions come from the pinned Canonical
projection. Photographic character, special conditions and future assessment
are separate. Role describes importance; mode describes how a condition would
be checked. REQUIRED/QUALITY never imply observed success. GUIDANCE is a
reference; VERIFY requires separate verification. AUTO metadata also cannot
authenticate a result. This research import has no trusted automatic result
channel, so no new PASS/FAIL/UNKNOWN badges, scores or Directions appear.

Missing optional descriptions/conditions show localized placeholders and do
not suppress other subjects. Research warnings, independent access notices,
home, search, OR topic filters and advanced source disclosures are preserved.
No Canonical redesign, W3/provider change, Legacy change or new runtime module.

## Reproduction

Environment: Node 24.19.0; Python 3.12.14; Playwright 1.57.0;
Chromium 154.0.8037.57 on Linux.

```sh
node --test apps/web-v2/tests/*.test.mjs
node --test --test-isolation=none --test-timeout=120000 --test-reporter=tap apps/web-v2/tests/*.test.mjs
PLAYWRIGHT_MODULE=/opt/codex/cua_node/lib/node_modules/playwright CHROMIUM_EXECUTABLE=/usr/bin/chromium W4_TOPICS_SCREENSHOT_DIR=/workspace/chase-topics-first-20261019/screenshots node --test --test-isolation=none --test-timeout=120000 --test-reporter=tap apps/web-v2/tests/browser-smoke.mjs apps/web-v2/tests/task-s-browser.mjs apps/web-v2/tests/photography-topics-browser.mjs
/workspace/chaselights-venv/bin/python ops/v2/postmerge_verify.py --root . --logs-dir /workspace/chase-topics-first-20261019/integration
/workspace/chaselights-venv/bin/python ops/v2/build_static.py --root . --output /workspace/chase-topics-first-20261019/static-build
```

The standard Node command passed before the implementation commit, with the
same runtime/test bytes. TAP logs below execute at the fixed implementation
commit. Browser cases require actual Chromium; missing tools are errors rather
than silent skips. Browser coverage includes all seven Places/eight subjects
at 360px touch/mobile and 1440px desktop across zh-TW/en/ja, source text,
role/mode labels, keyboard focus/jumps, missing optional data, forged imported
result rejection, filter/language preservation and no horizontal overflow.
Existing cases additionally exercise 390px, transport failures/retry/races,
ARIA and native keyboard controls. Screenshots cover all three languages on
both new-suite viewports. Chromium emulation is not physical Safari/iPhone QA.

## Actual results at the implementation commit

| Check | PASS | FAIL | SKIP | Exit | Raw evidence |
| --- | ---: | ---: | ---: | ---: | --- |
| Node | 56 | 0 | 0 | 0 | `node.log` |
| Chromium: 82 existing + 6 Photography Topics cases | 88 | 0 | 0 | 0 | `browser.log` |
| Immutable integration verification | 0 | 1 gate | 0 | 1 | `integration.log`, `integration-summary.json` |
| Static build | 0 | 1 gate | 0 | 1 | `build.log` |

Applicable Node/browser cases: **144 PASS, 0 FAIL, 0 SKIP**. Separately,
integration and build each FAIL at Source Pin verification; their downstream
suites/package steps were not reached. This is not a full-project/CI PASS.
`git diff --check` passed. The standard-command precommit Node output is
preserved separately as `node-standard.log`; runtime/test hashes are unchanged.

## Integration blockers and follow-up

The unchanged immutable W5 gate and static build each fail before packaging
or suite execution with `Merged w4 subtree differs from tested pin:
apps/web-v2`. See complete raw output, including the integration JSON report.
This is an unresolved integration blocker, not a waived check. No W5 pin,
workflow, test count or gate was lowered or edited to pass this task.

W5 must independently review and pin the final W4 tree/file discovery,
register the seven added Node and six added browser cases, then rerun the
full integration/build/release gates. Keep every existing check. Register
`photography-topics-browser.mjs` explicitly: it is intentionally outside the
Node `*.test.mjs` glob. The ten-file static runtime list needs no additions.
Do not inherit #517's overall case total or claim its Actions results for
this PR. CI status for this PR is reported separately in its description.

W1/W2 must review translated semantics and unresolved subject/evidence,
seasonal, access and geometry claims. W1/W3 must approve a genuine result
contract and scientific eligibility before any future result display.
Research maturity, AUTO labels or provider availability alone never authorize
a score. Existing human semantic/geographic approval remains pending.

Next bounded features: source-backed missing details, additional W2-reviewed
subjects, and approved per-condition capability/result transport with genuine
provenance/freshness and fail-closed handling. They are separate tasks, not
formal forecast approval. No public deployment/Safari/provider acceptance
was performed as part of this W4 UI change.
