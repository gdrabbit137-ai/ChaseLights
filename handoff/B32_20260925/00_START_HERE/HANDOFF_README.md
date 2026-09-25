# ChaseLights R4.2 B32 — Handoff README

Date: 2026-09-25 (Asia/Taipei)

## Authoritative branch

- Branch: `r4.2-b32-jp-research-batch01`
- Synced against production `main`: branch is ahead and not behind.
- Production main baseline at checkpoint: `dae5a12f8a4efbd35b73f5dd7e03975a4424fa43`
- Last functional-code checkpoint before handoff-document packaging: `231422ed0b9fa8c078b9bc38e1c6d53aae334160`

Do not continue from the old B29 branch or from `r4.2-b32-jp021-access-provider`. Continue from `r4.2-b32-jp-research-batch01`.

## Current Japan migration state

Japan catalog: 35 Places total.

Research-complete: 24 / 35:
- jp-001 through jp-014, except none skipped in that range now
- jp-015 through jp-024

Research-pending: 11:
- jp-025 萩市城下町
- jp-026 出雲大社
- jp-027 神戶六甲山
- jp-028 高野山
- jp-029 伊賀上野城
- jp-030 鳴門海峽漩渦
- jp-031 倉敷美觀地區
- jp-032 福岡城跡
- jp-033 唐津城
- jp-034 長崎哥拉巴園
- jp-035 福岡塔

Current B32 Japan additive catalog:
- 24 researched Places
- 31 Opportunities
- 31 Condition Variants
- 31 profile-viewpoint relations
- schema: `v0.04-r4.2-b32-jp-batch01-23`

Composite active catalog:
- Taiwan: 80 researched active Places
- Japan: 24 researched Places
- US: still research-pending

## Latest completed work — jp-014 Todoroki Valley

`jp-014 等等力溪谷` is now research-complete.

Primary researched Outcome:
- `jp-014-P01`
- Golf Bridge red bridge + Yazawa River ravine + green woodland
- Camera Zone anchor: `35.607857, 139.646545`
- navigation query: `等々力渓谷 ゴルフ橋`

Important current official state:
- Setagaya City reopened the riverside path on 2026-03-24.
- Official guidance says do not enter after dark.
- Heavy-rain guidance says stay away from the river.
- The current park notice says photography is not being accepted because of expected congestion.

Therefore ChaseLights uses:
- formula status: `access_hold_current_photography_not_accepted`
- runtime policy: `hold`
- score cap: 0
- research_pending: false

Do not reinterpret good weather as permission to recommend photography while this official notice remains active.

Detailed research: `B32_JP_RESEARCH_BATCH12.md`

## Existing dynamic access providers

### jp-021 Shinhotaka
- Provider: `shinhotaka_access.py`
- P01 and P02 runtime-ready
- official live ropeway status + timetable / maintenance + annual Stargazing Service semantics
- stale/ambiguous status fails closed

### jp-022 Mt. Yahiko
- Provider: `yahiko_access.py`
- P01/P02/P03 runtime-ready
- current official ropeway state plus multi-route / annual night-event semantics
- annual Night View & Stargazing Cruise dates are not projected into future years

## QA gates at handoff

Todoroki checkpoint:
- Adapter CI: PASS — run 36095613147
- Japan Candidate Weather QA: PASS — run 36095459006
- Browser Smoke: PASS — run 36095483843
- Taiwan Candidate Weather QA after region/runtime changes: PASS — run 36095396799

The earlier red Adapter runs during incremental commits are superseded by run 36095613147.

## Core product rules that must remain unchanged

1. Place-first homepage.
2. Card click opens researched Place Guide, not weather details.
3. Weather Forecast / Navigation / Radar remain peer tools.
4. Shooting/access times use Place-local timezone; Last Updated uses browser/device timezone.
5. No researched Opportunity => no photography score; research_pending=true.
6. Legacy Theme score is only a compatibility/weather baseline.
7. A clear Theme score alone may not create an 80+ Place recommendation.
8. Missing research fields remain absent; never synthesize generic shooting advice.
9. Dynamic access uncertainty fails closed.
10. Retired IDs remain retired.

## Next work

Proceed with `jp-025 萩市城下町`.

Research it individually:
- verify the actual photographable subject/composition, not generic city-center coordinates;
- find authoritative Place evidence first;
- establish a legal Camera Zone;
- research current access / shooting restrictions;
- decide whether the Outcome is minimum-sufficient, needs a dedicated module, or must remain held;
- only then add it to the B32 catalog and scoring runtime.

After each migration:
- Adapter CI
- Japan Candidate Weather QA
- Browser Smoke
- Taiwan QA when shared runtime/region logic changes

## Do not do

- Do not enable all remaining Japan Places from legacy Scene/Theme tags.
- Do not infer seasonal Outcomes from tags.
- Do not treat an attraction POI centroid as the camera position.
- Do not infer commercial/visitor shooting permission when an official notice is ambiguous.
- Do not reuse a current live-open transport snapshot for distant forecast hours beyond its freshness contract.
