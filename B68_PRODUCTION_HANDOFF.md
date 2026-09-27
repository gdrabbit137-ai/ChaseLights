# ChaseLights R4.2 B68 Production / Maintenance Handoff

Date: 2026-09-27 (Asia/Taipei)

## Start here

This file supersedes `B62_PRODUCTION_HANDOFF.md` as the current production / maintenance checkpoint.

Before changing production:
1. inspect GitHub `main` and all open pull requests,
2. read this file,
3. read `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md`, `RESEARCH_EVIDENCE_SPEC_R4_2.md`, and the relevant batch research document,
4. preserve the Place -> Photography Opportunity -> Condition Variant -> Viewpoint/Camera Zone model,
5. use `runtime_catalog_v004_r4_2.json` as the canonical production Opportunity catalog,
6. use `runtime_catalog_manifest_r4_2.json` as the expected-state validation snapshot,
7. preserve the Camera Zone / weather-sample / Navigation Target separation introduced and enforced during B64+.

## Verified production checkpoint

- Repository: `gdrabbit137-ai/ChaseLights`
- Production branch: `main`
- Public site: <https://chaselights.app/>
- B67 release PR: #123 — MERGED
- Main checkpoint after B67: `d4980693152aba42f76128294eba5c3faec79d6a`
- Latest production weather commit observed before B67 merge: `931d213c6cb449c546ad6bcfebb3a760a1bd2d9e`
- Open PRs after B67 merge and before starting B68: 0
- Post-B67 main Adapter run: `36300745859` — PASS
- Post-B67 Pages deployment: `36300745622` — PASS
- Re-check `main`, open PRs, and workflow state before every release.

B67 only changed CI workflow logic plus `ci_weather_impact.py`. It did not change a production weather/model input watched by `.github/workflows/update_weather.yml`, so no immediate production weather regeneration was required by the merge.

## Canonical catalog checkpoint

Current curated catalog:

| Region | Curated Places | Opportunities | Variants | Viewpoint relations |
|---|---:|---:|---:|---:|
| Taiwan | 83 | 217 | 227 | 222 |
| Japan | 35 | 53 | 58 | 54 |
| US migrated | 25 | 44 | 44 | 44 |
| **Total** | **143** | **314** | **329** | **320** |

Research state:
- Taiwan: active curated set complete; `tw-063` remains retired.
- Japan: production migration complete, `jp-001` through `jp-035`.
- US: `us-001` through `us-025` are Opportunity-migrated.
- US research-pending: `us-026` through `us-070` — 45 Places.

Current runtime-policy totals from the manifest:
- `module_pending`: 93
- `preview_module_available`: 110
- `minimum_sufficient_available`: 105
- `prototype_pending_certification`: 2
- `hold`: 2
- `data_insufficient`: 2

## Work completed after B62

### B63 — US research batch 02

Research record:
- `B63_US_RESEARCH_BATCH02.md`

Migrated:
- us-006 Bryce Canyon National Park
- us-007 Zion National Park
- us-008 Yosemite Half Dome
- us-009 Yosemite Tunnel View
- us-010 Yellowstone Grand Prismatic Spring

Important boundaries:
- sunrise/sunset claims require Place-specific evidence,
- Half Dome reflection uses the admitted water-surface contract but does not invent live Merced River level,
- Grand Prismatic remains fail-closed where geothermal steam and dynamic access are not runtime-ready,
- seasonal access is not inferred from month alone.

### B64 — Camera Zone weather-sample guard + US research batch 03

Research record:
- `B64_US_RESEARCH_BATCH03.md`

Migrated:
- us-011 Grand Teton National Park
- us-012 Mount Rainier National Park
- us-013 Crater Lake National Park
- us-014 Death Valley National Park
- us-015 Golden Gate Bridge

B64 formalized an important production boundary:
- Camera Zone = where the photograph is made,
- weather sample = where forecast/runtime conditions are sampled,
- Navigation Target = where routing may safely send the user.

A broad Place coordinate must not silently become a hard local weather sample for a distant photographic subject. Reflection, fog, access, sunrise/sunset and similar conditions remain evidence/runtime-gated.

### B65 — US research batch 04

Research record:
- `B65_US_RESEARCH_BATCH04.md`

Migrated:
- us-016 Las Vegas Strip
- us-017 Mount St. Helens
- us-018 Glacier National Park
- us-019 Olympic National Park / Ruby Beach
- us-020 Redwood National Park / Lady Bird Johnson Grove

Important boundaries:
- recurring event/show availability is not assumed from static schedules,
- closed/blocked road access cannot be overridden by clear weather,
- Olympic migration intentionally admitted Ruby Beach only where the Camera Zone/weather sample is safe enough,
- distant Olympic subregions remain deferred until they have their own explicit weather-sample contract.

### B66 — US research batch 05

Research record:
- `B66_US_RESEARCH_BATCH05.md`

Migrated:
- us-021 Canyonlands National Park / Mesa Arch
- us-022 Joshua Tree National Park / Cholla Cactus Garden
- us-023 Saguaro National Park / Cactus Forest Loop sunset pull-off
- us-024 Seattle Space Needle
- us-025 Santa Monica Pier

Key corrections:
- Joshua Tree weather/map anchor moved from a broad park-center coordinate to the researched Cholla Cactus Garden area.
- Saguaro moved to the exact NPS Cactus Forest Loop sunset pull-off.
- Space Needle exterior photography and ticketed observation-deck access remain separate Opportunities.
- Santa Monica Pier sunset is runtime-capable; managed Pacific Wheel lighting state remains module-pending.

### B67 — region-aware weather CI

PR:
- #123 `B67 make weather CI region-aware`

B67 introduced shared `ci_weather_impact.py` detection and wired it into:
- Taiwan Candidate Weather,
- Japan Candidate Weather,
- US Candidate Weather,
- Browser Smoke,
- Adapter self-test/compile coverage.

Intent:
- a normal US-only research PR should only regenerate/validate US weather where safe,
- TW/JP committed weather can remain the Browser Smoke input when their model/runtime inputs did not change,
- shared weather/scoring/runtime logic still expands to TW + JP + US,
- ambiguous classification fails safe to all three regions,
- manual workflows preserve their full required behavior.

PR #123 passed:
- Opportunity Adapter,
- Taiwan Candidate Weather,
- Japan Candidate Weather,
- US Candidate Weather,
- Browser Smoke.

After merge, main Adapter and Pages deployment also passed.

## Current product / model contracts

These remain authoritative:

- Place-specific evidence proves what can actually be photographed, except explicitly documented narrow derived-condition policies.
- Runtime/provider data estimates **when** an admitted Opportunity may work.
- Terrain, Theme tags, Scene tags, elevation, month, or one-point weather data must not create new Opportunities by themselves.
- High-risk subjects remain evidence-gated.
- Cloud sea remains only the documented narrow derived-condition exception and must reject local whiteout / saturated camera air.
- Camera Zone, weather sample coordinate, and Navigation Target are distinct concepts.
- Exact Directions links require verified Navigation Targets.
- A broad Place coordinate must not be reused as a hard local weather sample for a distant Camera Zone without an explicit safe contract.
- Missing optional research stays absent; do not generate filler.
- Annual events do not inherit prior-year dates without current official evidence.
- Seasonal foregrounds do not become active from month alone.
- Legacy Theme scoring remains compatibility output, not the primary product model.
- Favorable weather must never override a known or unresolved access restriction.
- Local marine/tide output must not be presented as shoreline-safety certification.

## Next optimization / research queue

Recommended order:

### 1. B69 — US research batch 06, us-026 through us-030

Next five production Places, in current inventory order:

- us-026 Seattle Pike Place Market
- us-027 Sawtooth Mountains
- us-028 Griffith Observatory, Los Angeles
- us-029 White Sands National Park
- us-030 Chicago Skyline

Research each Place individually before catalog admission.

Required process:
- prefer official land-manager / city / attraction / tourism authority evidence,
- prove actual photographable subjects and legal/public Camera Zones,
- separate exterior/public access from ticketed/facility access,
- verify sunset/sunrise/night/event claims instead of inheriting legacy tags,
- establish or correct Camera Zone/weather-sample coordinates where needed,
- do not promote seasonal, event, reflection, astro, skyline-lighting, snow, fog or access claims without evidence/runtime support,
- update catalog, manifest, evidence registry, runtime/dependencies, QA expectations, Browser Smoke research count, and US Candidate Weather range together.

### 2. Continue US migration in five-Place batches

After B69, continue `us-031` onward in controlled batches. Do not mass-promote the remaining legacy inventory.

### 3. Finish staged `tag_scores` producer cleanup only after compatibility review

B59 removed current frontend/analysis dependence, but producer compatibility may still emit `tag_scores`.

Before removing it:
- re-confirm production/browser consumers,
- decide cached schema compatibility,
- measure actual detail-shard savings,
- update Candidate Weather / Browser Smoke expectations.

Do not remove `theme_scores` as part of this cleanup.

### 4. Continue detail-shard payload audit

Inspect complete generated JSON rather than truncated connector snippets.

Prioritize:
- repeated compatibility maps,
- identical fields repeated across hourly rows,
- fields already available in the canonical static catalog.

### 5. Favorite legacy retirement remains deferred

Keep:
- `chaselights_favs_v2` as canonical state,
- `chaselights_favs` as migration input for now.

Retire legacy compatibility only after a deliberate observation/release window.

## Release gates

For catalog/runtime/evidence changes:
- `validate_curated_opportunities() == []`
- Adapter/integration passes
- Evidence Audit passes when evidence/catalog semantics change
- relevant Candidate Weather passes
- Browser Smoke passes
- region-aware CI classification must not skip an affected region
- generated candidate weather must not be accidentally committed in the PR

For frontend-only changes:
- Adapter passes
- Browser Smoke passes
- weather regeneration only when changed-file classification says runtime/model input changed

For weather-publishing changes:
- production `update_weather` completes
- generated weather commit appears on `main`
- per-Place shard inventory remains TW 83 / JP 35 / US 70
- no regional `*_weather_details.json` files reappear
- `usa_weather.json` remains absent
- Pages deployment reaches the final generated-weather commit

## Operational notes

- Production weather refresh remains scheduled every 3 hours.
- `update_weather.yml` regenerates TW + JP + US together for production publishing.
- B67 optimizes PR validation, not the authoritative production weather publication contract.
- Published US inventory remains 70 Place cards even though only 25 currently have curated Opportunities; `us-026` through `us-070` must remain research-pending rather than receiving legacy-derived photography scores.
- Re-check current access/provider behavior whenever research depends on time-sensitive park/facility conditions.
