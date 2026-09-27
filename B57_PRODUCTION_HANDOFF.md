# ChaseLights R4.2 B57 Production / Maintenance Handoff

Date: 2026-09-27 (Asia/Taipei)

## Start here

This file supersedes `B49_PRODUCTION_HANDOFF.md` as the current production / maintenance checkpoint.

Before changing production:
1. inspect GitHub `main` and all open PRs,
2. read this file,
3. read `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md`, `RESEARCH_EVIDENCE_SPEC_R4_2.md`, and the relevant batch research document,
4. preserve the Place -> Photography Opportunity -> Condition Variant -> Viewpoint/Camera Zone model,
5. use `runtime_catalog_v004_r4_2.json` as the canonical production Opportunity catalog,
6. use `runtime_catalog_manifest_r4_2.json` as the expected-state validation snapshot.

## Verified repository state

- Repository: `gdrabbit137-ai/ChaseLights`
- Production branch: `main`
- Public site: <https://chaselights.app/>
- Open PRs at this checkpoint: **0**
- Main checkpoint after B56: `5ea35c8b7d980514139eeb890a3fae5fda45ae78`
- Latest B55 production weather commit observed: `4d5b8c08aa83eb87bb41b58f3ffc3a156ba4dd7e`
- Re-check main before every release; these SHAs are checkpoints, not permanent assumptions.

## Canonical catalog checkpoint

Current curated catalog:

| Region | Curated Places | Opportunities | Variants | Viewpoint relations |
|---|---:|---:|---:|---:|
| Taiwan | 83 | 217 | 227 | 222 |
| Japan | 35 | 53 | 58 | 54 |
| US migrated | 0 | 0 | 0 | 0 |
| **Total** | **118** | **270** | **285** | **276** |

Important:
- Taiwan `tw-063` remains retired.
- Japan production research migration is now complete: **jp-001 through jp-035**.
- The 70 US production Place cards remain intentionally research-pending; do not restore legacy tag scoring as a shortcut.

## Work completed since B49

### B50 — Japan research migration jp-027 through jp-031

Migrated:
- 六甲山
- 高野山
- 伊賀上野城
- 鳴門海峽
- 倉敷美觀地區

Key boundary:
- seasonal foregrounds remain pending unless current season state proves presence,
- Naruto whirlpool strength is not approximated with the shoreline relative sea-level tide module,
- unmanaged prior-year event dates are not copied forward.

Research record:
- `B50_JP_RESEARCH_BATCH15.md`

### B51 — Japan migration completed through jp-035

Migrated:
- jp-032 福岡城跡
- jp-033 唐津城
- jp-034 長崎哥拉巴園
- jp-035 福岡塔

Japan now has no research-pending production Place cards.

Research record:
- `B51_JP_RESEARCH_BATCH16.md`

### B52 — weather summary/detail version-race recovery

Root cause:
summary JSON and per-Place detail shards are committed together, but CDN/browser cache turnover can briefly expose different generations.

The frontend no longer surfaces the raw:
`Weather detail version mismatch`

Recovery contract:
1. request detail against the expected summary version,
2. re-fetch the region summary once,
3. never downgrade to an older summary,
4. accept a detail that now matches the refreshed summary,
5. otherwise retry the detail once through a versioned/cache-busted URL,
6. only then show a localized “weather data is synchronizing” message.

Browser Smoke explicitly injects an old summary version and verifies recovery.

### B53 — Browser Smoke acceleration

Frontend-only PRs no longer regenerate Taiwan + Japan weather before Selenium.

The workflow:
- detects changed PR files through the GitHub API,
- regenerates weather only when runtime/model/data inputs changed,
- uses committed summary/shards for UI-only work,
- retains coverage for spatial weather, marine, tide and taxonomy inputs.

This reduces UI iteration time without weakening model/runtime validation.

### B54 — favorite migration sentinel

Canonical favorite state remains:
- `chaselights_favs_v2` — spot-ID favorites.

Legacy migration input remains:
- `chaselights_favs` — name-based favorites.

A versioned per-region migration sentinel now prevents rescanning unresolved legacy names on every render/load.

Do not remove legacy compatibility yet. Observe at least one release period before deciding whether to retire it.

Favorite removal still deletes matching legacy names, preventing canceled favorites from reappearing after reload.

### B55 — detail-shard duplicate runtime removal

Internal fetch/scoring still keeps:
`opportunity_runtime[opportunity_id]`

Published detail shards now omit that duplicated top-level map because the identical runtime diagnostic remains available at:
`opportunity_scores[opportunity_id].runtime`

No score, runtime policy, theme score, tag score or summary behavior changed.

Production refresh after merge completed successfully.

Measured committed raw-detail impact:

| Region | Before B55 | After B55 | Change |
|---|---:|---:|---:|
| Taiwan | 85.48 MB | 74.60 MB | **-12.7%** |
| Japan | 23.26 MB | 20.47 MB | **-12.0%** |
| US | 34.21 MB | 34.03 MB | ~-0.5% |

Taiwan largest shard:
- before: ~2.96 MB
- after: ~2.21 MB
- reduction: ~25%

US changes little because US Opportunities are still research-pending, so there were few Opportunity runtime diagnostics to duplicate.

### B56 — production weather trigger modernization

`.github/workflows/update_weather.yml` now listens to current runtime sources instead of retired batch fragments.

Required push inputs now include:
- `runtime_catalog_v004_r4_2.json`
- `runtime_event_calendar_r4_2.json`
- `shinhotaka_access.py`
- `yahiko_access.py`
- existing runtime/model inputs

Retired B15/B33 catalog fragments were removed from production refresh triggers.

Workflow-only changes no longer trigger an expensive full TW+JP+US weather refresh. Adapter tests now validate the production-trigger contract and run whenever `update_weather.yml` changes.

## Current product / model contracts

- Place-specific evidence proves what can actually be photographed, except explicitly documented narrow derived-condition policies.
- Runtime/provider data estimates **when** an admitted Opportunity may work.
- Terrain, Theme tags, Scene tags, elevation or one-point weather data must not create new Opportunities by themselves.
- High-risk subjects remain evidence-gated.
- Cloud sea is a narrow derived-condition exception only where the spatial profile and Camera Zone contract qualify.
- Camera Zone, weather sample coordinate and Navigation Target remain separate concepts.
- Exact Directions links require verified Navigation Targets.
- Missing optional research stays absent; do not generate filler.
- Annual events do not inherit prior-year dates without current official evidence.
- Seasonal foregrounds do not become active from month alone.
- Legacy Theme scoring remains compatibility output, not the primary product model.

## Next optimization queue

Recommended order:

### 1. Remove registry magic-count maintenance

Recent Japan expansion exposed remaining hard-coded validation such as:
- exact dynamic-access profile count,
- exact local-scene registry set,
- directional/spatial/marine/tide registry counts,
- selected exact module-ready ID sets.

Goal:
- validate registry entries against the canonical catalog and dependency contract,
- preserve fail-closed protection,
- stop requiring unrelated numeric edits every time a legitimate researched Opportunity is added.

Do not simply delete validation. Replace brittle count assertions with semantic invariants wherever possible.

### 2. Continue payload consumer audit

B55 removed one proven duplicate.

Next candidate:
- `tag_scores` is currently emitted as a V4 compatibility copy of `theme_scores`.

Current frontend order is:
`opportunity_scores -> theme_scores -> tag_scores`

Do **not** remove `tag_scores` yet. First verify:
- all production/browser consumers,
- any historical cached frontend compatibility requirement,
- schema-version expectations,
- actual byte savings.

### 3. Audit summary payload size

Current raw committed summary sizes observed around the B55 checkpoint:
- Taiwan: ~2.11 MB
- Japan: ~0.58 MB
- US: ~0.93 MB

Analyze complete, non-truncated JSON before removing any field. GitHub connector reads of the Taiwan summary may be truncated; do not make field-size conclusions from incomplete content.

### 4. Begin US research migration in small batches

All 70 US production Places remain research-pending.

Start with small, evidence-heavy batches, e.g. 5 Places at a time. Use NPS/official land-manager/local-authority sources where possible.

Suggested first batch:
- us-001 Grand Canyon National Park
- us-002 Horseshoe Bend
- us-003 Antelope Canyon
- us-004 Monument Valley
- us-005 Arches National Park

Do not auto-promote their legacy tags.

### 5. Favorite legacy retirement — later

B54 added the migration sentinel. Do not remove `chaselights_favs` compatibility until an observation period has passed and regression risk is acceptable.

## Release gates

For catalog/runtime changes:
- `validate_curated_opportunities() == []`
- Adapter/integration test passes
- Evidence Audit passes when evidence/catalog semantics change
- Candidate Weather passes when runtime/output semantics change
- Browser Smoke passes
- compare generated weather changes so PRs do not accidentally commit candidate data

For frontend-only changes:
- Adapter passes
- Browser Smoke passes
- no weather regeneration unless changed-file classification says runtime/model input changed

For weather-publishing changes:
- production `update_weather` completes
- generated weather commit appears on main
- per-Place shard count remains TW 83 / JP 35 / US 70
- no regional `*_weather_details.json` files reappear
- Pages deployment reaches the final generated-weather commit

## Operational note

The production weather workflow runs every 3 hours and on relevant runtime/model pushes.

B52 means a short CDN turnover race should normally self-heal instead of showing a raw version mismatch. If users still report repeated synchronization messages after several retries, inspect summary/detail `updated_at`, Pages deployment state and CDN behavior before weakening version matching.
