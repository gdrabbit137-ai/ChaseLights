# ChaseLights R4.2 B29 Research-Gated Place Guide + Opportunity-Linked Scoring Handoff

Date: 2026-09-24 (Asia/Taipei)

## Authoritative candidate state

- Branch: `r4.2-b28-p0-missing-places`
- Validated code head: `ff19ff0cfcb97fa1c9df63e7ca1c573b2c7bd0b5`
- Adapter/integration CI: PASS, run `35917201993`
- Branch relation to main at checkpoint: ahead, behind 0
- Draft PR: #4
- Governing specification: ChaseLights Specification v0.05 (handoff package)
- Weather schema remains 9; new Opportunity fields are additive.
- Production main is NOT changed by this checkpoint.

## Candidate Taiwan catalog

- 80 active Places
- 189 researched Photography Opportunities
- 199 Condition Variants
- 194 profile-viewpoint relations
- tw-063 remains retired.
- tw-078-P02 and tw-081-P02 remain retired and MUST NOT be reused.

## Research gate

Taiwan is eligible for the new Place Guide because every active Place has place-specific photography research:
- B26/B27 baseline: 70/70 active Places have >=1 shooting profile, >=1 evidence row, and >=1 Grade-A evidence row in the master SQLite.
- B28 additions: 10/10 were researched individually before addition.

Japan and US are not yet R4 Opportunity-migrated. They MUST NOT receive generated shooting advice or a photography recommendation score merely from legacy Scene/Theme tags. Their UI state is research-pending until curated Opportunities exist.

## UI contract

### Homepage
The homepage is Place-first:
Region/subregion -> Day -> ranked Places -> optional Place-name search.

Scene/Theme are not homepage intersecting filters.

### Card click
Clicking a Place card opens the researched Place Guide, NOT weather details.

The Place Guide may display only fields that exist in curated Place-specific Opportunities:
- Opportunity title
- selected-day Opportunity score/status
- best_time, when researched
- best_season, when researched
- curated Viewpoint/Camera Zone names
- Condition Variant title
- required_conditions, boosters, penalties, only when those fields were researched

Missing optional research fields MUST remain absent. Do not fill them with generic prose.

### Card tools
Card footer tools are peers:
- Weather Forecast
- Navigation
- Radar

No user-facing UI label should call Weather Forecast "96H details". The forecast may internally cover past 24h + future 72h.

## Opportunity-linked scoring contract

Legacy Theme score is only a weather/time baseline and compatibility output. Place ranking is Opportunity-first.

Daily output:
- `daily[].all`: researched Opportunity winner
- `daily[].opportunities`: per-Opportunity daily snapshots
- `daily[].themes`: legacy compatibility only

Hourly output includes:
- `opportunity_scores`
- `best_opportunity_id`
- `best_opportunity_name`

Safety caps:
- hold = 0
- data_insufficient <= 35
- module_pending <= 64
- preview runtime data missing <= 45
- preview dedicated-condition miss <= 54
- prototype_pending_certification <= 79
- only a researched `preview_module_available` Opportunity with all dedicated conditions available + eligible may use its weather baseline and enter 80+

Therefore a clear-weather Theme score alone can never produce an 80+ Place recommendation.

If a Place has no curated Opportunity:
- photography score = null
- `research_pending=true`
- card score shows dash / research pending
- Weather Forecast, Navigation and Radar remain usable

## Forecast-hint semantics

Visible hint copy must be backed by provider weather values, explicit model thresholds, or Opportunity-specific condition results.

Do not claim visible scene facts such as:
- city lights
- fog-free
- peaks
- forest mist
- waterfall
- perfect reflection

unless that semantic claim is actually supported by the Place research and the corresponding data/model.

## Secondary/simple Places

- tw-078 建功嶼: one simple tidal-causeway Opportunity only.
- tw-081 南竿鐵堡: one simple daytime fort/coast Opportunity only.
- Do not rebuild removed complex Outcomes unless new product evidence justifies it.

## Release gate before merge/deploy

Do not merge merely because CI is green.

Before release:
1. verify branch is not behind production main; reconcile without force push if it is,
2. run compile/integration QA,
3. generate candidate Taiwan weather with all 80 active Places,
4. require summary/detail completeness 80/80 or valid stale fallback,
5. verify new `daily[].opportunities` / `opportunity_scores` fields,
6. smoke-test Place Guide and Weather Forecast links in browser,
7. confirm retired IDs absent,
8. then review/merge PR explicitly.

## Next priorities

1. Merge/release review for B28/B29 candidate and 80/80 candidate-weather smoke test.
2. Migrate Japan and US Place research before enabling photography scores there.
3. Complete remaining Taiwan dedicated modules that materially unlock high-value Opportunities.
4. P1 missing Places remain 水漾森林 and 加路蘭.
5. Continue source-specific access providers only for core Opportunities where access materially gates photography value.
