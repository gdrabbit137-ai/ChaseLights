# ChaseLights R4.2 B29/B30 Production Handoff

Date: 2026-09-24 (Asia/Taipei)

## Authoritative production state

- Production branch: `main`
- R4.2 B28/B29 release PR: #4 — MERGED
- Release merge commit: `62ca229bc45fe0b649ade21d81aceea859051d55`
- Post-release production weather commit: `7decdf443953a56548ae0717f0a5907d75ca8ed0`
- Candidate branch used for release: `r4.2-b28-p0-missing-places`
- Weather schema remains 9; Opportunity fields are additive.
- GitHub Pages deployment after the production weather refresh: PASS, run `36017582468`.
- Production weather refresh: PASS, run `36016673452`.
- Browser smoke: PASS, run `36005909042`.
- Adapter/integration CI on final candidate code: PASS, run `36005939608`.
- Candidate Taiwan weather/release QA: PASS, run `35977644444`.
- Production is now changed: the researched Place-first UI and Opportunity-linked scoring are live on `main`.

## Production Taiwan catalog

- 80 active Places
- 189 researched Photography Opportunities
- 199 Condition Variants
- 194 profile-viewpoint relations
- `tw-063` remains retired.
- `tw-078-P02` and `tw-081-P02` remain retired and MUST NOT be reused.
- Post-merge production weather log confirmed `tw_weather.json: 80 spots`.

## Research gate

Taiwan is eligible for the new Place Guide because every active Place has place-specific photography research:
- B26/B27 baseline: 70/70 active Places have >=1 shooting profile, >=1 evidence row, and >=1 Grade-A evidence row in the master SQLite.
- B28 additions: 10/10 were researched individually before addition.

Japan and US are not yet R4 Opportunity-migrated. They MUST NOT receive generated shooting advice or a photography recommendation score merely from legacy Scene/Theme tags. Their UI state is research-pending until curated Opportunities exist.

The production browser smoke explicitly verifies that Japan and US cards hide legacy scores while their research is pending.

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

### Minimum sufficient condition rule

Do not equate formula complexity with photographic value.

Some individually researched Opportunities are successful whenever the scene is simply clean and readable. For those explicitly curated profiles, ChaseLights uses a **minimum sufficient condition** contract:

- visibility must be usable,
- low cloud must not materially block the subject,
- precipitation must not materially obscure the scene,
- access must not be known closed,
- the legacy Theme baseline still enforces time-of-day semantics such as daylight, blue hour, or night.

These profiles may legitimately enter the high-recommendation band when those simple conditions are strongly met, even if a more elaborate optional/refinement module is not implemented.

The registry is manual and Opportunity-ID-specific. It MUST NOT be inferred automatically from Scene/Theme labels.

Current seed: 41 researched Taiwan Opportunities, including broad mountain/landscape/city views and the two researched Yehliu geology views.

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
- a researched `preview_module_available` Opportunity with all dedicated conditions available + eligible may use its weather baseline and enter 80+
- a researched `minimum_sufficient_available` Opportunity may also enter 80+ when its explicit clear-view minimum sufficient contract matches

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

## B30 release gate — COMPLETED

All release items passed before/at deployment:

1. Candidate branch not behind production main — PASS.
2. Compile/integration QA — PASS.
3. Candidate Taiwan weather generated with all 80 active Places — PASS.
4. Summary/detail completeness 80/80, stale count 0 at candidate QA — PASS.
5. `daily[].opportunities` / `opportunity_scores` and Opportunity winner contract — PASS.
6. Browser smoke for Place Guide / Weather Forecast / Navigation / Radar — PASS.
7. Retired IDs absent from active output/contracts — PASS.
8. PR #4 explicitly reviewed, marked ready, and merged — PASS.
9. GitHub Pages production deployment — PASS.
10. Post-merge production weather refresh — PASS; Taiwan remained 80 spots.
11. Pages redeployment for refreshed production weather — PASS.

Candidate QA report at run `35977644444`:
- summary_count: 80
- details_count: 80
- stale_spot_count: 0
- research_pending_count: 0
- no_viable_day_count: 7
- high_score_day_count: 107
- winner_error_count: 0

Browser smoke at run `36005909042`:
- Taiwan rendered cards: 80
- Place Guide opened with researched Opportunities
- Weather Forecast rendered 96 hourly rows
- Japan rendered cards: 35
- US rendered cards: 70
- unresearched Japan/US legacy scores hidden

## Newly identified production performance issue

The post-release weather push reported:

- `tw_weather_details.json`: approximately 69.66 MB.

This is below GitHub's hard single-file limit but above its recommended 50 MB size.

More importantly, the current UI loads the whole regional details file on the first Weather Forecast click. For Taiwan that means a large network transfer and JSON parse before one Place's 96H forecast is displayed.

Treat this as the next production performance priority. Preferred direction:
- preserve the lightweight regional summary used by homepage cards,
- split 96H detail payloads by Place (or another small addressable shard),
- load only the selected Place's detail on Weather Forecast click,
- keep cache/version consistency with the summary `updated_at`,
- retain the current 96H UI behavior and Opportunity scoring semantics.

Do not solve this by removing forecast fields or lowering research/scoring fidelity unless a separate product decision is made.

## Next priorities

1. B31: reduce Weather Forecast detail payload from the current ~69.66 MB Taiwan regional file to true on-demand Place-level/sharded loading.
2. Migrate Japan and US Place research before enabling photography scores there.
3. Complete remaining Taiwan dedicated modules that materially unlock high-value Opportunities.
4. P1 missing Places remain 水漾森林 and 加路蘭.
5. Continue source-specific access providers only for core Opportunities where access materially gates photography value.
