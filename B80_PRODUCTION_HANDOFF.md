# ChaseLights R4.2 B80 Production / Maintenance Handoff

> Superseded for current production work by `B85_PRODUCTION_HANDOFF.md`. Keep this file as the B79 aurora-runtime checkpoint and migration-history reference.

Date: 2026-09-27 (Asia/Taipei)

## Start here

This file supersedes `B78_PRODUCTION_HANDOFF.md` as the current production / maintenance checkpoint after the B79 aurora-runtime release.

Before changing production:

1. inspect GitHub `main` and all open pull requests,
2. read this file,
3. read `B79_AURORA_RUNTIME.md` for the aurora provider contract,
4. read `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md` and `RESEARCH_EVIDENCE_SPEC_R4_2.md` for content/evidence rules,
5. preserve the Place -> Photography Opportunity -> Condition Variant -> Camera Zone/Viewpoint model,
6. use `runtime_catalog_v004_r4_2.json` as the canonical production Opportunity catalog,
7. use `runtime_catalog_manifest_r4_2.json` as the expected-state validation snapshot,
8. keep unresolved access, event, managed-lighting, transport and other current-state dependencies fail-closed.

B78 remains the detailed migration-history checkpoint for B69 through B77. B80 focuses on the post-migration runtime-provider phase.

## Verified code checkpoint

- Repository: `gdrabbit137-ai/ChaseLights`
- Production branch: `main`
- Public site: <https://chaselights.app/>
- B79 release PR: #136 — MERGED
- B79 merge checkpoint: `a7a5075c89395ec8f45ad72639fe69a027b7eb4a`
- B79 PR validation:
  - Opportunity Adapter — PASS
  - Evidence Audit — PASS
  - Taiwan Candidate Weather — PASS
  - Japan Candidate Weather — PASS
  - US Candidate Weather — PASS
  - Browser Smoke — PASS
- Post-B79 main Adapter #477 — PASS.
- Post-B79 main Evidence Audit #127 — PASS.
- Initial Pages deployment #438 on the code merge — PASS.
- Post-B79 production weather run #187 — PASS.
- Final generated-weather commit: `bb9e3f7a11b24c856200448a4fb2c5acfb3103aa`.
- Final Pages deployment #439 on `bb9e3f7a` — PASS.

## Canonical catalog checkpoint

B79 does not add or remove Places, Opportunities, Condition Variants or Viewpoint relations.

| Region | Curated Places | Opportunities | Variants | Viewpoint relations |
|---|---:|---:|---:|---:|
| Taiwan | 83 | 217 | 227 | 222 |
| Japan | 35 | 53 | 58 | 54 |
| United States | 70 | 111 | 111 | 111 |
| **Total** | **188** | **381** | **396** | **387** |

Migration state:
- Taiwan active curated production set complete; `tw-063` remains retired.
- Japan `jp-001` through `jp-035`: 35 / 35 migrated.
- United States `us-001` through `us-070`: 70 / 70 migrated.
- US production research-pending count: **0**.

Current runtime-policy totals after B79:
- `module_pending`: **122**
- `preview_module_available`: **120**
- `minimum_sufficient_available`: **133**
- `prototype_pending_certification`: **2**
- `hold`: **2**
- `data_insufficient`: **2**
- minimum-sufficient visibility profiles: **89**

The B79 delta is six aurora-only Opportunities moving from `module_pending` to `preview_module_available`. Aurora Opportunities that also require unresolved `dynamic_access` remain pending.

## B79 — location-aware aurora runtime preview

Implementation record:
- `B79_AURORA_RUNTIME.md`
- `aurora_state.py`

B79 implements the previously explicit but unimplemented canonical `aurora_state` dependency using NOAA SWPC OVATION short-horizon grid data.

### Provider contract

Authoritative source:
- NOAA / NWS Space Weather Prediction Center
- Aurora - 30 Minute Forecast / OVATION
- runtime JSON: `https://services.swpc.noaa.gov/json/ovation_aurora_latest.json`

Canonical behavior:
- sample the NOAA OVATION grid at the researched Place / Camera-Zone weather anchor,
- bind the local sample only to an hourly weather row near NOAA's published `Forecast Time`,
- current B79 maximum target offset: 45 minutes,
- reject stale, malformed, missing, geographically unsampled or out-of-horizon data,
- require valid solar geometry,
- require Sun elevation <= -12 degrees,
- combine the local OVATION signal with local low/mid/high cloud cover,
- keep the result probabilistic,
- always expose `visibility_guaranteed: false`.

Planetary Kp remains compatibility/context data. It is **not** the canonical location gate and must not be promoted back into one.

B79 deliberately does not extrapolate a single OVATION snapshot across the multi-day weather forecast.

### Explicit aurora registry

Current `AURORA_STATE_PROFILES`:
- `us-041-P02` Denali / Mountain Vista
- `us-042-P01` Fairbanks / Creamer's Field
- `us-043-P01` Chena Hot Springs
- `us-044-P02` Anchorage / Point Woronzof
- `us-046-P02` Hatcher Pass
- `us-056-P02` Brooks Range / Atigun Pass
- `us-057-P02` Arctic Circle Wayside
- `us-058-P02` Nome
- `us-065-P02` Chugach / Glen Alps
- `us-066-P02` Bering Land Bridge / Serpentine
- `us-068-P02` Noatak River
- `us-069-P02` Lake Clark / Port Alsworth

Do not auto-register future Places merely because a legacy tag contains `aurora`.

### Runtime-ready aurora-only profiles

These six now have a complete canonical aurora runtime contract:
- `us-042-P01`
- `us-043-P01`
- `us-044-P02`
- `us-058-P02`
- `us-065-P02`
- `us-069-P02`

### Aurora profiles still blocked by access

These remain `module_pending` even when OVATION and weather match:
- `us-041-P02` Denali / Mountain Vista
- `us-046-P02` Hatcher Pass
- `us-056-P02` Brooks Range / Atigun Pass
- `us-057-P02` Arctic Circle Wayside
- `us-066-P02` Bering Land Bridge / Serpentine
- `us-068-P02` Noatak River

The missing component is profile-specific `dynamic_access`, not aurora-state modeling.

## CI / publication changes in B79

`aurora_state.py` is now part of:
- Adapter compile / regression paths,
- Taiwan Candidate Weather paths,
- Japan Candidate Weather paths,
- US Candidate Weather paths,
- Browser Smoke paths,
- production `update_weather.yml` paths,
- `ci_weather_impact.py` shared weather-input classification.

Shared aurora-runtime code fails safe to all-region Candidate Weather + Browser Smoke validation.

The production weather generator fetches OVATION once per generator process when an aurora-capable Place needs it. Provider failure is cached for the process and canonical evaluation fails closed rather than issuing repeated requests or treating missing space-weather data as favorable.

## Current core model contracts

These remain authoritative:

- Place-specific evidence proves **what** can be photographed.
- Runtime/provider data estimates **when** an admitted Opportunity may work.
- Legacy Theme tags do not create new Opportunities.
- Camera Zone, weather sample, Navigation Target and transport/arrival point are different concepts.
- A remote wilderness weather coordinate must never silently become a Directions endpoint.
- Favorable weather must never override unresolved access / entitlement / transport state.
- Static hours or annual schedules do not prove current operation when cancellations or closures are possible.
- Seasonal foregrounds do not become active from month alone.
- Reflection is not guaranteed by the existence of water.
- Aurora requires the location-aware `aurora_state` contract; planetary Kp alone is insufficient.
- A positive aurora runtime match remains probabilistic and must never be described as a visibility guarantee.
- Cloud sea remains the documented narrow derived-condition exception and must reject local whiteout / saturated camera air.
- Legacy Theme scoring remains compatibility output, not the primary product model.
- Local marine/tide output must not be presented as shoreline-safety certification.

## Primary next-work queue

### 1. Dynamic-access provider coverage

This is now the highest-value runtime backlog.

The current access inventory contains many intentionally blocked Opportunities while only the small set of existing profile-specific providers is runtime-ready. Prioritize cases where otherwise-good weather can mislead the user.

Recommended order:

1. national-park / public-road status with authoritative current notices,
2. managed facility / tram / boat operating state,
3. timed-entry / booking corridors where entitlement must stay separate from public closure state,
4. remote Alaska road / aviation / transport state,
5. Taiwan mountain permits / road / trail access,
6. private-property or owner-permission cases only where an authoritative machine-readable source exists.

Do not create a generic "open" provider that silently covers unrelated access classes.

### 2. Event-state providers

High-value examples already in the catalog include:
- Fort Worth Herd current drive / cancellation state,
- managed annual / current-event Opportunities,
- event + access combinations.

A static recurring timetable may supply time context but must not prove today's event is operating.

### 3. Managed-lighting state

Keep managed illumination separate from persistent physical subjects. Examples include observation / attraction lighting and other curated night-scene Opportunities.

### 4. Specialized environmental state gaps

Continue explicit provider/evaluator design for:
- mist state,
- geothermal steam state,
- seasonal foreground state,
- wildlife state,
- waterfall flow,
- lake-water-level and related specialized conditions.

Do not infer these states solely from month, ordinary weather or generic Place tags.

### 5. Finish staged `tag_scores` producer cleanup only after compatibility review

B59 removed current frontend/analysis dependence, but producer compatibility still emits `tag_scores`.

Before removal:
- re-confirm browser and downstream consumers,
- decide cached-schema compatibility,
- measure detail-shard payload savings,
- update Candidate Weather and Browser Smoke expectations.

Do not remove `theme_scores` as an incidental part of this cleanup.

### 6. Continue generated detail-shard payload audit

Prioritize:
- repeated compatibility maps,
- fields identical across hourly rows,
- static catalog metadata duplicated into weather shards.

### 7. Favorite legacy retirement remains deferred

Keep:
- `chaselights_favs_v2` as canonical state,
- `chaselights_favs` as migration input.

Retire legacy compatibility only after a deliberate observation/release window.

## Release gates

For runtime/provider changes:
- `validate_curated_opportunities() == []`
- Adapter PASS
- Evidence Audit PASS where evidence/catalog semantics change
- relevant Candidate Weather PASS
- Browser Smoke PASS
- provider data missing/stale/ambiguous/unparsable => fail closed
- profile registry coverage must exactly match canonical dependency declarations
- generated candidate weather must not be committed in the PR

For access providers:
- use an authoritative source,
- preserve access-class distinctions,
- separate public closure state from user entitlement when required,
- include freshness / expiry logic,
- do not infer current access from a static research page,
- add deterministic parser/evaluator tests,
- keep unresolved profiles `module_pending`.

For weather publishing:
- production `update_weather` completes,
- generated weather commit appears on `main`,
- per-Place shard inventory remains TW 83 / JP 35 / US 70,
- no regional `*_weather_details.json` files reappear,
- `usa_weather.json` remains absent,
- Pages deployment reaches the final generated-weather commit.

## Operational notes

- Production weather refresh remains scheduled every 3 hours.
- `update_weather.yml` remains the authoritative production publication path.
- NOAA OVATION is a short-horizon aurora input; most future hourly rows will intentionally have no canonical aurora sample from a single fetch.
- An unavailable NOAA OVATION fetch must lower runtime availability, not fall back to Kp as a local guarantee.
- US research migration is complete; future work should favor runtime/provider correctness and payload/compatibility cleanup over bulk Place promotion.
