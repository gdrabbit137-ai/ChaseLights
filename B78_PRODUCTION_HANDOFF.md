# ChaseLights R4.2 B78 Production / Maintenance Handoff

> **Historical checkpoint — superseded by `B80_PRODUCTION_HANDOFF.md`.**  
> B78 remains useful for the US-migration history through B77, but its runtime-provider backlog predates the B79 aurora implementation.

Date: 2026-09-27 (Asia/Taipei)

## Start here

This file supersedes `B68_PRODUCTION_HANDOFF.md` as the current production / maintenance checkpoint.

Before changing production:
1. inspect GitHub `main` and all open pull requests,
2. read this file,
3. read `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md`, `RESEARCH_EVIDENCE_SPEC_R4_2.md`, and the relevant research/provider document,
4. preserve the Place -> Photography Opportunity -> Condition Variant -> Viewpoint/Camera Zone model,
5. use `runtime_catalog_v004_r4_2.json` as the canonical production Opportunity catalog,
6. use `runtime_catalog_manifest_r4_2.json` as the expected-state validation snapshot,
7. preserve Camera Zone / weather-sample / Navigation Target / transport-arrival separation,
8. keep unresolved access, event, lighting, aurora and other current-state dependencies fail-closed.

## Verified code checkpoint

- Repository: `gdrabbit137-ai/ChaseLights`
- Production branch: `main`
- Public site: <https://chaselights.app/>
- B77 release PR: #133 — MERGED
- B77 merge checkpoint: `a446d18fb5fabd3e7f1d89daf043ba3448cf53d4`
- B77 PR validation: Adapter, Evidence Audit, TW Candidate Weather, JP Candidate Weather, US Candidate Weather and Browser Smoke all PASS.
- Post-B77 main Adapter: PASS.
- Post-B77 main Evidence Audit: PASS.
- Post-B77 production weather run #186: PASS.
- Final generated-weather commit: `06d7d27c6a5a191e13882943ace7becf26d13381`.
- Final Pages deployment #436 on `06d7d27c`: PASS.

## Canonical catalog checkpoint

Current effective curated catalog after B77:

| Region | Curated Places | Opportunities | Variants | Viewpoint relations |
|---|---:|---:|---:|---:|
| Taiwan | 83 | 217 | 227 | 222 |
| Japan | 35 | 53 | 58 | 54 |
| United States | 70 | 111 | 111 | 111 |
| **Total** | **188** | **381** | **396** | **387** |

Migration state:
- Taiwan: active curated production set complete; `tw-063` remains retired.
- Japan: `jp-001` through `jp-035` Opportunity-migrated — 35 / 35.
- United States: `us-001` through `us-070` Opportunity-migrated — 70 / 70.
- US production research-pending count: **0**.

Current runtime-policy totals:
- `module_pending`: 128
- `preview_module_available`: 114
- `minimum_sufficient_available`: 133
- `prototype_pending_certification`: 2
- `hold`: 2
- `data_insufficient`: 2
- minimum-sufficient visibility profiles: 89

## Major work completed after B68

### B69 — US batch 06, us-026 through us-030

Research record:
- `B69_US_RESEARCH_BATCH06.md`

Key subjects:
- Pike Place Market
- Sawtooth / Redfish Lake North Shore
- Griffith Observatory
- White Sands / Sunset Stroll area
- Chicago skyline / Adler lakefront

Important boundary:
- White Sands current Dunes Drive / missile-test closure state remains independent of favorable weather.

### B70 — US batch 07, us-031 through us-035

Research record:
- `B70_US_RESEARCH_BATCH07.md`

Key subjects:
- Rocky Mountain NP / Sprague Lake
- New Orleans French Quarter
- Denver skyline / City Park
- Gateway Arch
- Fort Worth Stockyards

Important boundaries:
- Sprague Lake Bear Lake Road timed-entry/access remains fail-closed.
- Fort Worth Herd static schedule does not prove a current cattle drive.

### B71 — US batch 08, us-036 through us-040

Research record:
- `B71_US_RESEARCH_BATCH08.md`

Key subjects:
- Manhattan skyline / Gantry Plaza
- Niagara Falls / Terrapin Point
- Great Smoky Mountains / Newfound Gap
- Miami Beach / South Pointe
- Boston skyline / Piers Park

Important boundaries:
- managed Niagara illumination is separate from the persistent waterfall scene,
- Newfound Gap road access can block otherwise favorable weather,
- city/coast weather samples were moved to the researched Camera Zones.

### B72 — Alaska batch 09, us-041 through us-045

Research record:
- `B72_US_RESEARCH_BATCH09.md`

Key subjects:
- Denali / Mountain Vista
- Fairbanks / Creamer's Field
- Chena Hot Springs
- Anchorage / Point Woronzof
- Seward / Waterfront Park

B72 introduced `aurora_state` as an explicit canonical dependency.

Critical rule:
- the existing planetary Kp input is not sufficient to guarantee aurora at a specific Camera Zone,
- canonical aurora Opportunities remain fail-closed until a location-aware aurora-state provider is connected.

### B73 — Alaska batch 10, us-046 through us-050

Research record:
- `B73_US_RESEARCH_BATCH10.md`

This continued the Alaska migration with evidence-first Camera Zones and explicit separation of ordinary landscape/coastal scenes from aurora or managed-access conditions.

### B74 — Alaska batch 11, us-051 through us-055

Research record:
- `B74_US_RESEARCH_BATCH11.md`

The batch continued narrowing broad Alaska inventory entries to actual photographable public scenes and kept remote transport / seasonal access independent of weather quality.

### B75 — Alaska batch 12, us-056 through us-060

Research record:
- `B75_US_RESEARCH_BATCH12.md`

Notable provider boundary:
- Glacier Bay managed day-tour operation remains an access / operation dependency; static seasonal descriptions do not prove a tour is running today.

### B76 — Alaska batch 13, us-061 through us-065

Research record:
- `B76_US_RESEARCH_BATCH13.md`

Key boundaries include:
- Alyeska Mountain Station access depends on current Aerial Tram operation,
- remote/high-elevation access and aurora state remain separate from ordinary weather scoring.

### B77 — final Alaska / US batch 14, us-066 through us-070

Research record:
- `B77_US_RESEARCH_BATCH14.md`

Migrated:
- Bering Land Bridge / Serpentine Hot Springs
- Yukon River / Yukon Crossing
- Noatak River
- Lake Clark / Port Alsworth
- Independence Mine

B77 closes the original US production research queue.

Critical boundaries:
- remote NPS/BLM coordinates are Camera Zone/weather anchors, not fake road or airstrip navigation targets,
- Serpentine and Noatak remain fail-closed on remote transport/access,
- Yukon Crossing remains fail-closed on current Dalton Highway state,
- Independence Mine remains fail-closed on current Hatcher Pass road/parking/trail state,
- aurora remains fail-closed on location-aware `aurora_state`,
- Lake Clark daytime mountain/lake panorama is runtime-available through the minimum-sufficient visibility contract.

## Current core model contracts

These remain authoritative:

- Place-specific evidence proves **what** can be photographed.
- Runtime/provider data estimates **when** an admitted Opportunity may work.
- Legacy Theme tags do not create new Opportunities.
- Terrain, elevation, month or one weather point cannot create unsupported photographic subjects.
- Camera Zone, weather sample, Navigation Target and transport/arrival point are different concepts.
- A remote wilderness weather coordinate must never silently become a Directions endpoint.
- Exact Directions links require a verified Navigation Target.
- Favorable weather must never override known or unresolved access restrictions.
- Static hours, schedules or annual calendars do not prove current operation where cancellation/closure is possible.
- Seasonal foregrounds do not become active from month alone.
- Reflection is not guaranteed by the existence of water.
- Aurora requires a location-aware `aurora_state`; planetary Kp alone is insufficient.
- Cloud sea remains the documented narrow derived-condition exception and must reject local whiteout / saturated camera air.
- Legacy Theme scoring remains compatibility output, not the primary product model.
- Local marine/tide output must not be presented as shoreline-safety certification.

## Current production architecture

Authoritative research/model path:

`Place -> Photography Opportunity -> Condition Variant -> Camera Zone/Viewpoint -> runtime dependency evaluation -> generated regional weather -> Web UI`

Canonical static source:
- `runtime_catalog_v004_r4_2.json`

Expected-state validation snapshot:
- `runtime_catalog_manifest_r4_2.json`

Region inventory / weather anchor / navigation metadata:
- `regions.py`

Runtime dependency registry:
- `runtime_dependencies.py`

Runtime evaluators:
- `opportunity_runtime.py`
- `access_state.py`
- related provider modules

Production weather publication:
- `.github/workflows/update_weather.yml`
- regenerates TW + JP + US together,
- runs on the production schedule and relevant pushes,
- commits generated weather back to `main`,
- final Pages deployment must reach the generated-weather commit.

PR weather validation:
- B67 region-aware impact detection remains active,
- region-only changes can avoid unrelated weather generation when safe,
- shared/runtime/browser-smoke contract changes fail safe to broader regional validation.

## Primary next-work queue

With TW, JP and the original US production inventory fully migrated, the next phase should prioritize runtime/provider completeness and technical-debt cleanup rather than bulk research promotion.

### 1. Runtime provider backlog

Highest-value unresolved canonical dependencies include:
- `aurora_state`
- remote / managed `dynamic_access`
- event-state providers
- managed-lighting state
- specialized mist / geothermal / seasonal state gaps already recorded in the dependency inventory

Do not mark these Opportunities available merely to reduce `module_pending` counts.

### 2. Access-provider coverage

Prioritize Opportunities where a good weather score can currently be misleading without live/current access:
- remote Alaska aviation / transport
- national-park road closures
- timed-entry / booking corridors
- seasonal mountain roads
- managed facilities / tram / boat operation

Providers should remain authoritative-source, fail-closed and profile-specific.

### 3. Aurora runtime design

Before implementing:
- define a location-aware signal rather than reusing planetary Kp as a local guarantee,
- include darkness / solar elevation,
- combine with local cloud cover,
- preserve Camera Zone latitude/longitude,
- define forecast horizon and provider confidence,
- keep exact visibility claims probabilistic and avoid promising a visible aurora outcome.

### 4. Finish staged `tag_scores` producer cleanup only after compatibility review

B59 removed current frontend/analysis dependence, but producer compatibility may still emit `tag_scores`.

Before removal:
- re-confirm browser and downstream consumers,
- decide cached-schema compatibility,
- measure detail-shard payload savings,
- update Candidate Weather / Browser Smoke expectations.

Do not remove `theme_scores` as an incidental part of this cleanup.

### 5. Continue generated detail-shard payload audit

Inspect complete generated JSON and prioritize:
- repeated compatibility maps,
- fields identical across hourly rows,
- static catalog metadata duplicated into weather shards.

### 6. Favorite legacy retirement remains deferred

Keep:
- `chaselights_favs_v2` as canonical state,
- `chaselights_favs` as migration input for now.

Retire legacy compatibility only after a deliberate observation/release window.

## Release gates

For catalog/runtime/evidence changes:
- `validate_curated_opportunities() == []`
- Adapter passes
- Evidence Audit passes
- relevant Candidate Weather passes
- Browser Smoke passes
- region-aware CI classification must not skip an affected region
- generated candidate weather must not be accidentally committed in the PR

For access/provider work:
- fail closed on missing, stale, ambiguous or unparsable provider state,
- include verification/expiry metadata where applicable,
- do not infer current access from a static research page,
- add profile-specific tests.

For weather-publishing changes:
- production `update_weather` completes,
- generated weather commit appears on `main`,
- per-Place shard inventory remains TW 83 / JP 35 / US 70,
- no regional `*_weather_details.json` files reappear,
- `usa_weather.json` remains absent,
- Pages deployment reaches the final generated-weather commit.

## Operational notes

- Production weather refresh remains scheduled every 3 hours.
- `update_weather.yml` remains the authoritative production weather publication path.
- US production now has no research-pending Place cards; any future US Place addition must be researched before it can receive canonical Opportunity scoring.
- Do not treat completion of the migration as completion of all runtime modules. A substantial number of Opportunities intentionally remain `module_pending` because their real-world current-state provider is not yet connected.
