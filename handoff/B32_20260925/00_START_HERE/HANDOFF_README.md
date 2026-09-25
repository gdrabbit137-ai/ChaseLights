# ChaseLights R4.2 B32 — Handoff README

Date: 2026-09-25 (Asia/Taipei)

## Authoritative continuation

Continue from `codex/jp026`, whose integration base is
`r4.2-b32-jp025-hagi`. Do not continue from the older B32 branches.

Current continuation state:
- Japan research: 26 / 35; nine pending;
- latest researched Place: `jp-026 出雲大社`;
- additive Japan catalog: 26 Places / 34 Opportunities / 34 Condition
  Variants / 34 viewpoint relations;
- catalog schema: `v0.04-r4.2-b32-jp-batch01-25`;
- weather output schema: v10;
- all four release gates are green.

Production `main` contains the 24/35 checkpoint through jp-024. Its two newer
commits after the development merge base are generated weather updates, so
integrate current production data before a release to `main`.

Detailed research:
- `B32_JP_RESEARCH_BATCH13.md` — jp-025 Hagi;
- `B32_JP_RESEARCH_BATCH14.md` — jp-026 Izumo Taisha.

Next research target: `jp-027 神戶六甲山`.

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

- Adapter CI: PASS — run 36128165281
- Japan Candidate Weather QA: PASS — run 36128522907
- Browser Smoke: PASS — run 36128731623
- Taiwan Candidate Weather QA: PASS — run 36128226766

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

The jp-025 Navigation Target checkpoint and jp-026 continuation have not been
merged to production. PR #11 is a clean draft from `codex/jp026` into
`r4.2-b32-jp025-hagi`.

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

## Next work

1. Review and merge PR #11 into the jp-025 integration branch.
2. Reconcile the integration branch with current production data before release.
3. Research `jp-027 神戶六甲山` individually.
4. For each new Place, verify the Navigation Target separately from the Camera
   Zone.
