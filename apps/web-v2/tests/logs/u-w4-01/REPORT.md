# U-W4-01 — real implementation evidence

Owner: W4, `apps/web-v2/` only. User explicitly approved execution U-W4-01. No merge, auto-merge, deployment or schedule change.

Base and effective main reviewed: `380c36f6ce8cbc795990f19696801455d1cde9d0`; second fetch before commit found no drift. Latest W4 source #460 `ec5dc9609596135ba1b2634dfa7d6c07a54fabdc` is merged, and base `apps/web-v2/` tree is `8427cb75fdb433a58d3a4941769a6c06f6f5dc3b`. No open W4 PR or matching U-W4-01 implementation was found. #471/#467/#465/#474 are open; #486 remains Draft/open/unmerged, head `0837dd555df9d8f647b9042223d5e766d6fd6afc`. Its related GitHub workflow snapshots show success, not a merge or a live forecast.

Read latest-main AGENTS.md, both R4.2 specifications, specs/v2 README, Architecture, Governance, Free Composition, Access Advisory, Camera Area policy, current W4 README and existing tests. Task U's old main SHA is not used as the execution base. No new W1 contract or speculative Place metadata is introduced.

## Actual local tests

| Run | Discovery | PASS | FAIL | SKIP | Scope |
| --- | ---: | ---: | ---: | ---: | --- |
| Baseline Node, explicit isolation=none | 31 | 31 | 0 | 0 | Exact base checkout |
| Baseline Chromium | 6 | 6 | 0 | 0 | Exact base checkout, 3 locales × 2 devices |
| Updated Node | 43 | 43 | 0 | 0 | Working implementation, all original 31 retained + 12 state cases |
| Updated full Chromium | 75 | 75 | 0 | 0 | Working implementation, original 6 retained + 69 meaningful cases |
| W1 real canonical schema validation | 3 files | 3 | 0 | 0 | Immutable real W2 records, no schema relaxation |

Commands were actually executed. Node's default process isolation on this environment reports test-file totals (baseline 7 files); `--test-isolation=none --test-reporter=tap` is used for honest individual-case counts. Node cases are not browser counts. Logs here are working-tree runs: `source-integrity.json` records SHA-256 of each tested runtime/test file. The final committed HEAD will be rerun and recorded in the PR and downloadable delivery evidence; these logs do not claim they were run on a then-nonexistent commit.

Browser: Node v24.19.0, Playwright 1.57.0 at `/opt/codex/cua_node/lib/node_modules/playwright`, actual `/usr/bin/chromium` 154.0.8037.57, headless Linux. Same-origin ephemeral loopback server; network scenarios intercept only test-page catalog requests with pinned research bytes. No provider/weather/score fixture becomes live. Tests verify actual two-second delay, response lifecycle, visibility, request counts, retry, locale switch while pending, failure clearing, local import races, search zero-result versus transport state and no fake runtime. 18 actual screenshots are retained for 360/390/1440 × zh-TW/en/ja × home/research. Screenshots at expanded research state preserve full source detail; not physical-phone or Safari evidence.

## Failure history retained

`browser-development.log` is an interrupted first development run. Old `mode` element was removed from HTML but still updated in render, causing ready-state waits to time out. It was fixed by removing that stale binding, and the existing DOM test now rejects missing actual HTML IDs. This partial run was interrupted with exit 130; its test failures are retained and are not counted as PASS. The next full original-six run and subsequent 75-case run passed. Initial shell fetch without supported network access failed to connect to proxy:8080; using the environment's existing network route succeeded. No destination-policy, GitHub scope or credentials were changed, and no auto-review rejection occurred.

## Integrity and product boundaries

`catalog.v2.json`, all five W2 fixture/manifest files, `catalog-loader.mjs`, `model.mjs`, `v21-adapter.mjs` are byte-identical to the real base (`source-integrity.json`). All changed committed paths must be under apps/web-v2. Source commit/hash declarations and W2 canonical data remain unchanged. Full original descriptions/condition notes, subject text, unknowns and evidence scope remain in research, visible access warnings stay outside Required/Blocker/Quality, no Directions or keyword fallback is added, local import makes zero POST, forged evaluations do not create a score or favorable result.

Title, primary headline, advanced-summary and provenance-landmark literals in two existing test files follow the new information architecture. No security/source/translation/warning assertion was removed, no test was deleted or skipped, and discovery increased. Missing Place names use explicit localized unavailable copy; IDs remain searchable and in advanced details. W4 framing guidance now explicitly tells the photographer to confirm access/safety before choosing a composition; W2 source text is not edited.

## W5 integration and Task 02 dependencies

W5 must repin this PR's exact source commit/tree. The existing main gate pins the old W4 tree and expects Node 31 + browser 6 / total 157. The new actual W4 discovery is 43 + 75, so a separately accepted W5 gate retaining other suites would discover 238; if #486's 12 additions are independently accepted, 250. These are handoff arithmetic, not claims that the full suite passed. Do not bypass the current gate. Add catalog-state.mjs to the static-build runtime/dependency manifest (current #486 seven-file list), and adapt W5 public smoke to explicit research/tools entry and translated headline/summary/landmark; retain source, no-score, warnings and navigation checks. An unchanged old public site cannot certify this unpublished UI.

#465/#474 human evidence and tri-locale signoff remain pending. #467 still needs genuine production provider/runtime/approved AUTO integration; the existing W3 WINDOW and raw NOAA source are not a selected-date photography forecast. #471 seven-place/eight-record publication is separate Task 03 scope.

Task 02A: W1-approved index/metadata contract plus W2 localized Place identity, country/admin index, cross-region dedup and visibility rules. Task 02B: approved date/query interface and verified Place IANA timezone; local date/DST semantics must be tested. Task 02C: W1 taxonomy plus W2 sourced index, preference/favorite policy; absent score/distance inputs cannot enable those sorts. All three can proceed with explicit unknown/disabled states after contracts exist, without inventing forecasts. Re-read main and this PR's actual owner status; do not assume merge.
