# ChaseLights V2 — photography home and research browser

## W4 — Qixingtan archived hourly weather view (Issue #526)

The separate home panel shows the 2026-10-19 Open-Meteo one-shot for `tw-036` as
an **offline historical sample**. Its 72 hourly rows and ten original fields
come from W5's accepted one-shot replay; W4's copy is byte-pinned by SHA-256.
The original provider response SHA-256 remains visible in the W3/W5 evidence,
while the W4 display copy has its own digest. The panel fetches only its
same-origin JSON file, never Open-Meteo. It always says historical/expired and
not evaluable, even if a row's old valid time happens to fall in the future for
a viewer with an earlier clock. A failed file, digest, identity, unit, time or
clock check displays no weather cells.

Times are formatted in `Asia/Taipei` from UTC instants. Rain and rain
probability describe the preceding hour; the other eight fields are instant
values. Missing/invalid cells say unavailable, and a genuine zero stays zero.
Retrieval completion and the original valid times are separate; the provider's
model issue/update time remains unknown. The source, CC BY 4.0 licence,
transformations and coastal/grid limitations are visible in zh-TW, en and ja.
No current-source transport, photography result, score, Directions, API call,
scheduled collection or Legacy/WeatherGrid change is included.

Run W4 tests from the repository root:

```sh
node --test --test-isolation=none --test-reporter=tap apps/web-v2/tests/*.test.mjs
CHROMIUM_EXECUTABLE=/usr/bin/chromium node --test --test-isolation=none --test-timeout=120000 --test-reporter=tap apps/web-v2/tests/browser-smoke.mjs apps/web-v2/tests/task-s-browser.mjs apps/web-v2/tests/photography-topics-browser.mjs apps/web-v2/tests/hourly-weather-browser.mjs
```

W5 must independently accept and pin this exact W4 tree and add the new
module/fixture to its static build and browser discovery before any merge.
Current-weather TTL, permissions, provider usage, cache/cadence and redistribution
are separate W3/W5 gates. The archived sample never upgrades `RAW_ONLY` or
`NOT_EVALUABLE` to a shooting recommendation.

## W4 — Photography Topics First (2026-10-19)

The research browser now opens each Place with a localized “What can you
photograph here?” list. Each subject shows the existing Canonical name,
description and targets, followed by special conditions and a separate future
assessment section. The exact seven-Place/eight-Opportunity catalog and index
bytes are unchanged. The existing home, search, OR topic selection, access
warnings and advanced source disclosures remain available.

Condition role and evaluation mode are independent: REQUIRED describes what
the subject needs; QUALITY describes factors that may improve its appearance
without producing a score. GUIDANCE is a shooting reference; VERIFY needs
separate verification. Neither is a current successful result. AUTO metadata
alone also cannot establish a connected evaluation. This research import has
no trusted result transport, so it shows no PASS/FAIL/UNKNOWN condition badges,
photography scores or new Directions. Missing optional descriptions or
conditions receive localized placeholders without hiding other subjects.
This is research awaiting review, not an approved photography Guide.

Repeatable checks from the repository root:

```sh
node --test apps/web-v2/tests/*.test.mjs
node --test --test-isolation=none --test-timeout=120000 --test-reporter=tap apps/web-v2/tests/browser-smoke.mjs apps/web-v2/tests/task-s-browser.mjs
node --test --test-isolation=none --test-timeout=120000 --test-reporter=tap apps/web-v2/tests/photography-topics-browser.mjs
```

Actual local results: 56 Node cases, 82 existing browser cases and 6 new browser
cases PASS; zero FAIL or SKIP in these suites. The new browser suite visits all
seven Places/eight subjects in zh-TW/en/ja at 360px touch/mobile and 1440px
desktop, including source text, role/mode labels, keyboard jumps, filters,
locale preservation, independent warnings and absent invented results.
Set `W4_TOPICS_SCREENSHOT_DIR` to retain its screenshots. Chromium emulation
does not establish physical-phone/Safari or human translation approval.

Source base: main `67a154b163c3e9a868d07eccc35f46d37580be38`; prior W4 tree
`70eb22ad22f3cad08aafab9ac71032ee8278139b` and W2 index commit
`cf29288ce47e2cccb2fb2e1453ad193200996a95`. Full per-record provenance remains
in `catalog.v2.json` and is checked by the existing canonical tests. Evidence
and exact commands are under `tests/logs/photography-topics-first-20261019/`.
W5 must independently review this Draft, deliberately pin its final W4 tree
and file discovery, register the additional seven Node/six browser cases, and
rerun integration/build/release checks. Existing immutable W4 pins and counts
are intentionally unchanged; local W4 PASS is not Release Gate approval.
No runtime dependency was added to the ten-file static bundle.

Next bounded extensions are source-backed detail for missing subjects,
additional W2-reviewed topics, and independently approved condition-result
transport after W1/W2/W3 validation. No provider, scientific threshold,
photography scoring or production publication is introduced here.

## Task S — multi-Place research browsing (Draft W4)

The default static bundle now contains the exact eight W2 R1 canonical Opportunities
over seven Places. `browse-index.v2.json` packages W2 #490's manifest, Place,
topic and status documents pinned to `c10976eb5e88fd32ec0adc58a1317ed70015821d`.
`catalog.v2.json` carries per-Opportunity source commit/path/blob pins (the three
Batch03 and five Batch04 source commits remain distinct). `browse-index.mjs`
checks exact IDs, revisions, publication, unknown region/time-zone metadata and
joins; both distributed JSON files have fixed SHA-256 checks, and canonical
fixture tests check Git blob bytes. A changed/missing default bundle fails closed.

The visible workspace searches names in all three languages and stable Place IDs
with literal partial-text matching. Topic selections are **OR** within the set;
search and topics combine with **AND**. The filter first retains matching
Opportunities, then groups them by Place; it never includes an unmatched
Opportunity from the same Place. Clearing filters preserves the user's selected
Place. The mobile panel has separate open/close controls. Name ordering uses
deterministic normalized code-point order plus Place ID, not inferred region.
Local file imports remain available but are explicitly not the verified indexed
bundle and cannot receive its topic classification.

All eight records remain Research-only; the home has no selected-date forecast,
and access notices never alter a photography verdict. Region/time-zone fields
remain UNKNOWN, no GPS or subject geometry is fabricated, and no Directions,
score, distance or date selection is inferred. Name semantic review and human
release approval remain pending. Favorites, stored preferences, complete
administrative filters, local dates, and score/distance sort require later owner
work. This is not permission to merge or deploy.

Run `node --test apps/web-v2/tests/*.test.mjs` and the existing
`node --test apps/web-v2/tests/browser-smoke.mjs` plus
`node --test apps/web-v2/tests/task-s-browser.mjs` with actual Chromium.
For W5, accept #487's W4 base and #489/#490 exact dependencies, deliberately
repin the W4 tree and static build/runtime dependency list (including
`browse-index.mjs` and both JSON files), then run the full source/release gates.
Do not treat W4's local tests or this bundled research catalog as live forecast
approval. Task R #496 remains planning-only and unmerged.

Worker 4 owns only `apps/web-v2/`. The home page answers forecast availability first and opens the existing research browser only on request. Date selection and date-specific forecast transport are not connected; no recommendation, shooting period or score is synthesized. Legacy entry, weather data, runtime, workflows and deployment are unchanged.

## Fixed real data and provenance

The former single-record preview is retained as an immutable historical test fixture. The default `catalog.v2.json` now contains all eight source-pinned records. Its `tw-026-P01` member is pinned to W2 `2177bd8c8b6c18e0a4b284e50b55d0ff12697ddd`:

- Canonical path: `data/v2/opportunities/tw-026-P01.json`, blob `001a3380231e3d073e900bf2b415aac7dcc5fd79`.
- Preview path: `data/v2/previews/tw-026-P01.research-only.v21.json`, blob `282297ca41be835517a22ea312f9898e9e5e8435`.
- `tests/fixtures/worker2/` retains byte-exact W2 records `tw-016-P01`, `tw-026-P01`, `tw-026-P02` and the original preview. `manifest.json` records each path, commit, Git blob and SHA-256. These are read-only test inputs, not a second canonical source. Tests verify their bytes, including explicit `WORKER2_DATA_DIR` overrides; missing or changed inputs fail instead of SKIP.

The canonical records are R1 / evidence_review. All six photography conditions are non-AUTO and provisional, with null thresholds and model bindings. Geometry remains unknown, and no independently verified NavigationTarget exists. Three-language source copy is retained unchanged; automated presence and display tests do not establish human semantic approval.

W2's latest evidence audits at this pin (`worker2_tw026p01_e026b_source_scope_20261010_0325.json` and `worker2_tw026p01_e026c_yonghua_scope_20261010_1325.json`) retain important limits: the original lookout closure does not prove whole-site closure or whole-site openness, the actual permitted camera area/geometry is unverified, opening-hour conflicts remain unresolved, and the Japanese wording/three-language semantic signoff still needs W2/W5 review. This change does not resolve those research gates.

## Development and repeatable checks

Use the existing checkout; cloud tasks are isolated and do not need a worktree. From repository root:

```sh
python -m http.server 8000 --bind 127.0.0.1
node --test apps/web-v2/tests/*.test.mjs
node --test apps/web-v2/tests/browser-smoke.mjs
node --test apps/web-v2/tests/task-s-browser.mjs
```

The browser runner starts its own temporary HTTP server on an unused loopback port and closes its browser/server afterward. It requires Playwright and Chromium; by default it uses this cloud image's `/opt/codex/cua_node/lib/node_modules/playwright` and `/usr/bin/chromium`. Elsewhere set `PLAYWRIGHT_MODULE` to a resolvable installed module name/path and `CHROMIUM_EXECUTABLE` to the browser path. Missing tooling is an explicit error, never a silent passing/zero-test result.

The original browser suite covers desktop and mobile across zh-TW/en/ja: automatic/local imports, translated source/ARIA, keyboard, search, research warnings, no unverified Directions or synthetic verdict, transport errors and overflow. The Task S suite adds seven-Place browsing, multilingual name search, OR topic filters, combined queries, mobile open/close, locale persistence and tampered-index rejection. Mobile means Chromium viewport/touch emulation, not physical-phone or Safari verification.

For canonical validation, use the latest main `specs/v2/tests/validate_contract.py` and pinned #489 schema for all eight W2 records. Node's adapter is a defensive reader, not a replacement for W1's authoritative JSON Schema.

Original command outputs and diagnosed pre-fix failures are retained under `tests/logs/task-a/`. Future changes should rerun the commands, rather than treat saved logs as fresh CI results.

## Runtime, navigation and language boundaries

Local imports stay in the browser. Importing canonical research always discards evaluations; `runtimeEvaluation` remains fail-closed pending an approved W3/W1 runtime contract and genuine provider/freshness pipeline. Generated research time, research import time and local load time are distinct; none is forecast validity.

Claim types and audit statuses are retained as metadata, not relabeled as resolved source authority. Unresolved evidence references have no fabricated publisher or public URL. Missing relation distance, azimuth and elevation remain null. Only independently evidenced verified arrival targets can create exact-coordinate Directions; no name, subject, camera anchor or `map_query` fallback is used.

Existing three-language skip/ARIA translation keys are reused. Missing semantic translations are not silently substituted. Human geographic/evidence and translation review remain required.

## U-W4-01 behavior and validation

The default screen explicitly says no photography forecast is available and no date is selected. “Explore places and photography subjects” opens an inline research section, labeled research information rather than a selected-date forecast. Closing restores focus to the opening button; there is no modal or focus trap. Search, selection and the full source descriptions/conditions/unknowns remain available. Missing source-backed Place names use a localized “Place name not provided”; stable IDs remain searchable and available in advanced information. Names are never inferred from IDs or opportunity titles.

`catalog-state.mjs` owns operational loading/ready/unavailable/error/invalid/empty states only. Pending requests clear old cards and provenance; 404 is distinguished from server/network failures. Empty transports are recognized at the UI boundary without passing them off as schema-valid canonical data. Unsupported schemas, malformed JSON and missing localization clear cards and navigation. Retry performs a genuine fetch, deduplicates concurrent attempts, and rejects late results using a request generation and abort signal. Local file reads supersede pending fetches and older file reads; they stay in the browser and imported evaluations remain discarded. No cache or offline freshness promise is made.

Data tools and source details are user-opened native disclosures. R1, revision, review status, SHA, evidence and geometry remain inspectable. Research generation/import/local load time are not forecast update or validity time. Access advisories stay visibly outside photography conditions. Changing locale preserves stable selection and open advanced panels; invalidated focused cards move focus to the research heading.

All new product copy, dynamic statuses, button names, title and landmarks have zh-TW/en/ja text. Automated tests do not replace accountable human translation review; #465 and #474 remain pending. W3's deterministic solar WINDOW model and NOAA raw adapter exist on main; this UI has no approved live result-store/provider/AUTO integration. The research importer is deliberately not a forecast transport.

Run the two task commands above. For individual case discovery on Node 24, use:

```sh
node --test --test-isolation=none --test-reporter=tap apps/web-v2/tests/*.test.mjs
node --test --test-isolation=none --test-reporter=tap apps/web-v2/tests/browser-smoke.mjs
```

The original 31 Node cases are retained (accessibility expectations follow the new home title/provenance label). Twelve state regressions raise discovery to 43. The original six Chromium cases retain source meaning, warnings, security, keyboard and import checks, and now explicitly open research/data tools. Added transport tests cover delay ≥2 seconds, 404, 500, network failure, invalid JSON, incompatible schema, incomplete localization, empty data and recovery across 3 languages × 2 devices; refresh failure and import races are also covered. 360/390/1440 × 3-language tests capture home/research screenshots and verify native Tab/Enter, 44px controls and overflow. Chromium emulation is not physical Safari/iPhone review. `W4_SCREENSHOT_DIR` selects the screenshot output directory; by default it is `/workspace/work/u01/screenshots`.

## W5 handoff — U-W4-01

Implementation starts at reviewed main `380c36f6ce8cbc795990f19696801455d1cde9d0`, with W4 source #460 already merged (tree `8427cb75fdb433a58d3a4941769a6c06f6f5dc3b`). Task evidence records exact tested commit and the final source tree separately. This is a separate W4 Draft PR; W5 must deliberately repin the new W4 tree and raise discovery for actual additional cases, preserving every existing W1/W2/W3/W4/W5 guard. No W5 pin, workflow, build or deploy file is edited here. Existing 157-case integration expects 31 Node + 6 browser and the old W4 tree; its failure remains a real integration blocker, not a waived check.

The new runtime dependency is `catalog-state.mjs`; W5's #486 seven-file static build/dependency allowlist must include it in a separate W5 change. W5 public browser smoke assumes research is initially visible, the old headline/advanced summary and old landmark copy; it must follow the explicit research/tools entry while retaining exact pinned P01, all source descriptions, no-score, access-warning and no-Directions checks. Public postdeployment smoke requires a separately authorized release; this PR does not verify a changed public website.

Task 02A needs a W1-reviewed Place/index/date contract plus W2-sourced localized names, country/admin index and publication eligibility (including cross-region identity). Task 02B needs an approved date/query interface and verified IANA Place timezone, with local-day/DST tests. Task 02C needs the W1 taxonomy and W2 index, plus preference/favorite semantics; unsupported score/distance sort remains disabled. Seven-place/eight-opportunity publication is a later #471/Task 03 scope with per-record provenance, not part of Task 01. Re-read latest main and actual owner branches before each task; do not assume this Draft has merged.

## Closure advisory policy (W1 #457 / W2 #458)

Access/closure/safety warnings remain conspicuous and translated in all three languages, separate from WEATHER/ASTRONOMY condition evaluation. The projection defensively quarantines old ACCESS_SAFETY REQUIRED/BLOCKER records as `access_advisories`; neither opening status nor closure changes photographic suitability. Verified Directions still require separately evidenced lawful arrival targets. The default P01 catalog and all W2 fixtures are pinned to W2 #458; the original historical W4 #448 tree no longer matches this corrected tree.
