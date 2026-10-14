# ChaseLights V2 — photography home and research browser

Worker 4 owns only `apps/web-v2/`. The home page answers forecast availability first and opens the existing research browser only on request. Date selection and date-specific forecast transport are not connected; no recommendation, shooting period or score is synthesized. Legacy entry, weather data, runtime, workflows and deployment are unchanged.

## Fixed real data and provenance

The default `catalog.v2.json` is W2's real `tw-026-P01` research-only preview, with explicit Git provenance fields added. It is pinned to W2 branch `fix/v2-access-advisory-w2-20261012` at `2177bd8c8b6c18e0a4b284e50b55d0ff12697ddd`:

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
```

The browser runner starts its own temporary HTTP server on an unused loopback port and closes its browser/server afterward. It requires Playwright and Chromium; by default it uses this cloud image's `/opt/codex/cua_node/lib/node_modules/playwright` and `/usr/bin/chromium`. Elsewhere set `PLAYWRIGHT_MODULE` to a resolvable installed module name/path and `CHROMIUM_EXECUTABLE` to the browser path. Missing tooling is an explicit error, never a silent passing/zero-test result.

The six browser cases cover desktop 1440×1000 and mobile 390×844 across zh-TW/en/ja: real automatic and local-file imports, visible source translations, title/landmark ARIA updates, native keyboard locale switching, locale persistence, skip-link focus, keyboard place selection with retained focus, search/empty search, expandable translated conditions/access notes, no unverified Directions, no synthetic live verdict, incomplete-localization rejection, no horizontal overflow and no import upload. Mobile means Chromium viewport/touch emulation, not physical-phone or Safari verification.

For canonical validation, use the latest main `specs/v2/tests/validate_contract.py` and schema (these may be absent from the W4 base); validate all three pinned opportunity files. Node's adapter is a defensive reader, not a replacement for W1's authoritative JSON Schema.

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
