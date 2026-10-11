# W4 Task F — actual local acceptance (2026-10-11)

Owner W4; test basis PR #446 `ff11d330884be5fdc90853f9dc100b012278c2f3`, stacked on #443. This task changes only `apps/web-v2/tests/logs/task-f-20261011/`; no W1/W2/W3/W5/Legacy, workflow or deployment changes. The code under test remains byte-identical to #446. The local checkout was materialized by exact GitHub file contents because the shell GitHub proxy refused `git ls-remote`; `git hash-object` confirmed all four W2 bytes. No source or test was changed to obtain a PASS.

Latest main at final spec gate: `91f4e30a3ac5f83c111fbeac933d77f160b40e59`. Read `AGENTS.md`, both R4.2 specs, `specs/v2/README.md`, architecture, governance and worker contracts. Their Git blobs match #444's tree; W4 is an isolated research-only preview. Main advanced from `ec0e0b7571beca0bc2d2821c0bc65a192995ad58` only in four WeatherGrid files during testing; the applicable specs remained byte-identical. Reviewed PRs #436, #442, #443, #446, W2 #440/#444 and W5 #445.

W2 PR #444 HEAD inspected: `8725bf13348dfae371ae8358930a25dd424a3361`; manifest pins canonical source commit `452ff5a79e0e4617d6ddb834b5dbecdd0e896b55`. The latest PR HEAD retains identical four canonical blobs. `source-comparison.log` checks fixture bytes, SHA-1 Git blobs, SHA-256, current W2 source bytes, preview/canonical equality, and catalog/preview equality modulo exactly five declared provenance fields. P01 blob is `3459ee2afd51ffa48c5b986aaf86d00bac80999e`; preview blob is `4e0da88cd60bb9aaad010a1ef4ab6e28d876f4bb`.

The P01 zh-TW/en/ja description, access, safety and first REQUIRED condition exactly match current W2. All three say permitted shooting-area boundaries have not been independently verified; the original lookout closure does not prove other areas open. No unverified Directions, exact shooting GPS, fabricated FAVORABLE, score, selected-date forecast, or verified runtime evaluation appears. Language key and projected content checks pass; independent human semantic/access signoff is still PENDING under governance.

## Actual tests

| Gate | PASS | FAIL | ERROR | SKIP | Evidence |
| --- | ---: | ---: | ---: | ---: | --- |
| Seven Node test files, each executed directly with real `WORKER2_DATA_DIR` | 30 | 0 | 0 | 0 | `node-cases.log` |
| Additional adapter smoke | 1 | 0 | 0 | 0 | `adapter-smoke.log` |
| Chromium 1440x1000 desktop / 390x844 mobile x zh-TW/en/ja | 6 | 0 | 0 | 0 | `browser.log` |

The required `node --test apps/web-v2/tests/*.test.mjs` command additionally completed with seven file-level PASS on this runner (`node-test-runner.log`). Direct execution supplies the actual 30 case count. Browser test covers initial real catalog, source SHA, locale switching/reload, keyboard and ARIA, touch, local import, safety text, missing translations and forged runtime rejection. Browser execution used Playwright 1.62.1 and Chromium 153.0.8010.0 from the official npm package. `environment.log` has versions. No test case was skipped. An initial official Playwright CDN browser download returned an invalid zero-byte archive; an empty initial extraction also caused a browser launch error. The npm Chromium was unpacked correctly and the final six browser tests all passed; these setup failures are not product test failures.

## GitHub Actions and W5 handoff

At #446's exact tested HEAD, GitHub reports zero check runs and zero PR workflow runs. This local PASS is not GitHub CI. W5 #445 ran against older W4 #443 and cannot certify #446. W5 should pin this task's new HEAD (logs-only on #446) or #446's identical code tree, update the source gate to W2 #444, run its dedicated CI at the updated head and inspect jobs/artifacts. W3's separate stale test SHA must be handled by W3, not W4. Keep stacked PRs Draft; no merge or deploy until W5's integration and project owner gates are satisfied. No Safari, physical handset, live provider or deployed URL was tested.

Raw logs: `node-cases.log`, `node-test-runner.log`, `adapter-smoke.log`, `browser.log`, `source-comparison.log`, `source-git-blobs.log`, `source-sha256.log`, `environment.log`.
