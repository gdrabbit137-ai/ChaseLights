# ChaseLights R4.2 B32 — Handoff README

Date: 2026-09-25 (Asia/Taipei)

## Continuation after this handoff

The original handoff below records the `jp-025` checkpoint on `r4.2-b32-jp025-hagi`.
An isolated continuation branch, `codex/jp026`, adds `jp-026 出雲大社` without merging the navigation correction into `main`. See `B32_JP_RESEARCH_BATCH14.md` for sources, Camera Zone uncertainty, arrival-route decision and formula scope.

- Japan research on the continuation: 26/35; nine pending.
- Additive Japan catalog: 26 Places / 34 Opportunities / 34 Condition Variants / 34 viewpoint relations.
- Schema: `v0.04-r4.2-b32-jp-batch01-25`; weather output remains v10.
- `jp-026` uses the public approach and Haiden exterior; its navigation target is `multiple_access_routes` because Seidamari and parking are distinct arrivals. The legacy shrine centroid is never used as a Directions destination.
- Local adapter tests pass. Candidate weather and browser QA for this continuation are pending; the four green runs below apply to the prior `jp-025` checkpoint only.
- Next research target after candidate QA: `jp-027 神戶六甲山`.

## Authoritative development branch

- Branch: `r4.2-b32-jp025-hagi`
- Production `main` baseline: `70277c685521fe50a3119de23880be5e90a19b68`
- Production currently contains the 24/35 Japan checkpoint through jp-024.
- Development branch is ahead of main and not behind.

Do not continue from `r4.2-b32-jp-research-batch01`. Continue from `r4.2-b32-jp025-hagi`.

## Current development state

Japan research on this branch:
- researched: 25 / 35
- pending: 10
- latest researched Place: `jp-025 萩城下町・菊屋橫町`
- additive Japan catalog: 25 Places / 33 Opportunities / 33 Condition Variants / 33 profile-viewpoint relations
- catalog schema: `v0.04-r4.2-b32-jp-batch01-24`

Detailed jp-025 research:
- `B32_JP_RESEARCH_BATCH13.md`

## R4.2 Navigation Target correction

A production navigation flaw was found: the old V5.2 UI preferred `map_query` and opened Google Maps Search. Ambiguous Place keywords could therefore show several unrelated map results.

This branch changes the product contract.

Authoritative spec:
- `NAVIGATION_SPEC_R4_2.md`

Core rule:
- Camera Zone != Navigation Target.
- `map_query` is search/display metadata only.
- free-text `map_query` MUST NOT construct the Navigation URL.

New `navigation_target` statuses:
- `verified`: exact-coordinate Google Maps Directions
- `provisional_camera_anchor`: exact-coordinate Map pin only; not presented as verified navigation
- `needs_review`: no clickable keyword fallback
- `multiple_access_routes`: do not silently select one arrival route

Initial explicit cases:
- 加羅湖: `needs_review`
- 新穗高・西穗高口展望台: `needs_review`
- 彌彥山: `multiple_access_routes`
- 等等力溪谷 Golf Bridge: `verified`
- 萩城下町・菊屋橫町: `verified`

Weather output schema is now v10 and exports `navigation_target`.

Frontend:
- verified target -> `/maps/dir/?api=1&destination=<lat>,<lon>`
- provisional exact anchor -> `/maps/search/?api=1&query=<lat>,<lon>`
- needs-review / multi-route -> disabled Navigation-pending control
- no production Navigation URL is built from `map_query`

The old screenshot case for 加羅湖 therefore no longer searches Google Maps for the text “加羅湖”.

## jp-025 Hagi research

Primary normal Outcome:
- `jp-025-P01`
- Kikuya Yokocho white / namako walls and preserved historic lane
- close-range local-scene minimum-sufficient contract
- low cloud / long-range visibility do not incorrectly suppress the street scene
- material precipitation/access problems remain blockers

Event Outcome:
- `jp-025-P02`
- verified 2026 Hagi Bamboo Lamp Festival dates: 2026-10-09 through 2026-10-11, 18:00–21:00 JST
- event-state runtime remains pending, therefore ordinary nights cannot be treated as bamboo-lantern nights

Navigation Target:
- verified street-access anchor: `34.4119363, 131.3932271`

## QA at this handoff

- Adapter CI: PASS — run 36100446591
- Japan Candidate Weather QA: PASS — run 36100403517
- Browser Smoke: PASS — run 36100369665
- Taiwan Candidate Weather QA: PASS — run 36100640799

Browser Smoke explicitly covers:
- 加羅湖 has no clickable broad keyword navigation
- a provisional Place opens only an exact-coordinate map pin
- 等等力溪谷 verified target uses Directions coordinates
- 萩城下町 verified target uses Directions coordinates
- keyword names do not leak into Navigation hrefs

## Existing production checkpoint

The previous 24/35 checkpoint was merged via PR #10.

Production:
- B32 merge commit: `242fa40b0550b0f184b2cc3228df04702f554f76`
- post-merge weather commit: `70277c685521fe50a3119de23880be5e90a19b68`
- Pages deployment for refreshed weather: PASS
- production Japan data: 24 researched / 11 pending

The current jp-025 + Navigation Target branch has NOT yet been merged to production.

## Core product rules

1. Place-first homepage.
2. Card click opens researched Place Guide.
3. Weather Forecast / Navigation or Map / Radar remain peer tools.
4. Shooting/access times use Place-local timezone; Last Updated uses browser/device timezone.
5. No researched Opportunity => no photography score.
6. Legacy Theme score is compatibility/weather baseline only.
7. Clear Theme weather alone may not create an 80+ recommendation.
8. Missing research fields remain absent.
9. Dynamic access uncertainty fails closed.
10. Camera Zone must not be assumed to be a navigation destination.
11. `map_query` must never be the production routing source.

## Next work after Navigation QA

1. Finish/confirm Taiwan Navigation Target regression QA.
2. Decide whether to deploy this navigation fix + jp-025 checkpoint.
3. Continue Japan research from `jp-026 出雲大社`.
4. As Places are researched, separately verify their Navigation Target instead of inheriting the Camera Zone.
