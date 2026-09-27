# ChaseLights R4.2 B62 Production / Maintenance Handoff

Date: 2026-09-27 (Asia/Taipei)

## Start here

This file supersedes `B57_PRODUCTION_HANDOFF.md` as the current production / maintenance checkpoint.

Before changing production:
1. inspect GitHub `main` and all open pull requests,
2. read this file,
3. read `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md`, `RESEARCH_EVIDENCE_SPEC_R4_2.md`, and the relevant research batch document,
4. preserve the Place -> Photography Opportunity -> Condition Variant -> Viewpoint/Camera Zone model,
5. use `runtime_catalog_v004_r4_2.json` as the canonical production Opportunity catalog,
6. use `runtime_catalog_manifest_r4_2.json` as the expected-state validation snapshot.

## Verified production checkpoint

- Repository: `gdrabbit137-ai/ChaseLights`
- Production branch: `main`
- Main checkpoint before B62: `94f2b466ebaca9802a13bae789cf13f57006a6d1`
- Open PRs observed before B62: 0
- Public site: <https://chaselights.app/>
- Re-check main before each release.

## Canonical catalog

| Region | Curated Places | Opportunities | Variants | Viewpoint relations |
|---|---:|---:|---:|---:|
| Taiwan | 83 | 217 | 227 | 222 |
| Japan | 35 | 53 | 58 | 54 |
| US migrated | 5 | 9 | 9 | 9 |
| **Total** | **123** | **279** | **294** | **285** |

Research state:
- Taiwan: active curated set complete; `tw-063` retired.
- Japan: production migration complete, `jp-001` through `jp-035`.
- US: `us-001` through `us-005` migrated; `us-006` through `us-070` remain research-pending.

## Work completed after B57

### B58 — semantic runtime registry validation

Brittle exact-count and exact-ID registry assertions were replaced where possible with semantic validation against the canonical catalog/dependency contracts.

Goal preserved:
- fail closed on invalid runtime wiring,
- do not require unrelated magic-number edits when legitimate researched Opportunities are added.

### B59 — legacy detail compatibility consumer deprecation

Current production/browser consumers no longer depend on published detail `tag_scores`.

Important:
- producer compatibility may still emit `tag_scores`,
- do not remove it until the staged compatibility/observation window is intentionally closed.

### B60 — summary payload slimming

Published regional summaries no longer include legacy `daily[].themes`.

Authoritative summary fields remain:
- `daily[].all`
- `daily[].opportunities`

Internal Theme compatibility scoring remains available where still required.

### B61 — US research migration batch 01

Research record:
- `B61_US_RESEARCH_BATCH01.md`

Migrated:
- us-001 Grand Canyon National Park
- us-002 Horseshoe Bend
- us-003 Antelope Canyon
- us-004 Monument Valley
- us-005 Arches National Park

Key runtime boundaries:
- guided-tour access is not inferred from weather/daylight,
- Antelope Canyon remains dynamic-access pending without an authoritative booking/access provider,
- night-sky evidence does not imply exact Galactic Core alignment,
- Navajo Tribal Park access/permit rules remain separate from weather quality.

## B62 — legacy USA weather artifact retirement

The root file `usa_weather.json` was an orphaned legacy artifact:
- size at B62 cleanup: 2,766,370 bytes,
- current writer produces `us_weather.json`,
- frontend loads `./${region}_weather.json` with region key `us`,
- production workflow stages `us_weather.json`,
- repository code search found no current `usa_weather.json` consumer.

B62 removes the legacy file and updates `.github/workflows/update_weather.yml` to remove it if it ever reappears.

Do not restore `usa_weather.json`; `us_weather.json` is the production US summary contract.

## Current optimization queue

Recommended order:

### 1. Continue US research migration in small batches

Next batch should cover `us-006` through `us-010` only after place-specific official evidence is collected.

Do not auto-promote legacy tags.

### 2. Finish staged detail payload cleanup after observation window

B59 removed consumer dependence on `tag_scores`, but producer compatibility remains.

Before writer removal:
- confirm no current production/browser consumer reads `tag_scores`,
- confirm cached schema compatibility plan,
- measure exact detail-shard savings,
- update Candidate Weather / Browser Smoke contracts.

Do not remove `theme_scores` as part of this work.

### 3. Continue detail-shard payload audit

After B55 duplicate runtime removal and B59 consumer deprecation, inspect remaining large fields using complete generated JSON.

Prioritize:
- repeated compatibility maps,
- fields duplicated identically across hourly rows,
- fields already available from canonical static catalog.

Do not remove fields based on truncated connector reads.

### 4. Favorite legacy retirement remains deferred

B54 added a per-region migration sentinel.

Keep:
- `chaselights_favs_v2` as canonical state,
- `chaselights_favs` as migration input for now.

Retire the legacy key only after a deliberate observation/release window.

### 5. Repository-history size is separate from current-tree size

Deleting current generated artifacts improves checkout/deployment tree size but does not rewrite Git history.

Do not history-rewrite `main` merely to reduce repository metadata size unless explicitly planned, backed up, and coordinated.

## Release gates

Catalog/runtime:
- `validate_curated_opportunities() == []`
- Adapter passes
- Evidence Audit passes when evidence/catalog semantics change
- Candidate Weather passes when runtime/output semantics change
- Browser Smoke passes
- generated candidate weather is not accidentally committed in the PR

Frontend-only:
- Adapter passes
- Browser Smoke passes
- UI-only Browser Smoke should use the B53 fast path

Weather-publishing:
- production `update_weather` completes
- per-Place shard inventory remains TW 83 / JP 35 / US 70
- no regional `*_weather_details.json` files reappear
- `usa_weather.json` must remain absent
- Pages/deployment reaches the final generated-weather commit

## Product contracts that remain authoritative

- Place-specific evidence proves what can actually be photographed, except documented narrow derived-condition policies.
- Runtime/provider data estimates when an admitted Opportunity may work.
- Terrain/Theme/Scene/elevation alone must not create an Opportunity.
- Seasonal presence is not guaranteed by month alone.
- Annual events do not inherit prior-year dates.
- Camera Zone, weather sample coordinate, and Navigation Target are distinct.
- Only verified Navigation Targets may become exact Directions links.
- Missing optional research fields remain absent rather than filled with generic prose.
