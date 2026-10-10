# ChaseLights V2 — independent research preview

Worker 4 owns only `apps/web-v2/`. This is an isolated research explorer, not a selected-date forecast or a production launch. Legacy entry, weather data, runtime, workflows and deployment are unchanged.

## Fixed real data and provenance

The default `catalog.v2.json` is W2's real `tw-026-P01` research-only preview, with explicit Git provenance fields added. It is pinned to W2 branch `v2/worker2-canonical-batch03-20261009` at `7f10e9bd2757449d72546155c66714880c6d3ab1`:

- Canonical path: `data/v2/opportunities/tw-026-P01.json`, blob `abb9222e2c2ca974f271b08d497313d402f911b9`.
- Preview path: `data/v2/previews/tw-026-P01.research-only.v21.json`, blob `6a1e009e76d79de6d45b5360d746cc4932b9c6f7`.
- `tests/fixtures/worker2/` retains byte-exact W2 records `tw-016-P01`, `tw-026-P01`, `tw-026-P02` and the original preview. `manifest.json` records each path, commit, Git blob and SHA-256. These are read-only test inputs, not a second canonical source. Tests verify their bytes, including explicit `WORKER2_DATA_DIR` overrides; missing or changed inputs fail instead of SKIP.

The canonical records are R1 / evidence_review. All 12 conditions are non-AUTO and provisional, with null thresholds and model bindings. Geometry remains unknown, and no independently verified NavigationTarget exists. Three-language source copy is retained unchanged; automated presence and display tests do not establish human semantic approval.

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

## W5 handoff

Task A is based on W4 `e931981a31d2ade1a94f921edd66f069027ec47c`, with latest main specs reviewed at `68907dc2b21e6ef774cad18684917b1895818bd8`. W1 EvaluationResult PR #431 and W3 PR #435 were Draft, not merged contracts. Recheck these and worker HEADs before integration.

Use a Draft PR against the W4 source branch so the Task A diff contains only this directory's changes; W5 must coordinate the W4 integration/base and review actual latest-main specs, checks and unresolved evidence/semantic gates. No merge, live deployment, Legacy link or production recommendation is authorized by these tests. The candidate public path is not verified by local browser checks.
