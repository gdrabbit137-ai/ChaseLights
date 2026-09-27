# ChaseLights R4.2 B65 — US Research Batch 04 (us-016 through us-020)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates the next five United States production Places into the canonical Opportunity catalog:

- us-016 Las Vegas Strip
- us-017 Mount St. Helens
- us-018 Glacier National Park
- us-019 Olympic National Park
- us-020 Redwood National Park

Canonical production data remains in `runtime_catalog_v004_r4_2.json`. This file records evidence and modeling decisions only.

## Evidence / weather-sample boundary

This batch preserves the B64 rule:

- Place-specific official evidence proves the subject exists.
- Weather / astronomy / marine modules estimate when an admitted subject may work.
- A Camera Zone that is far from the current Place weather coordinate must not silently inherit that Place weather as a hard local condition.
- Reflection / mist / event subjects are not promoted from legacy tags without Place-specific evidence.
- Access is fail-closed where an authoritative live provider is required but not connected.

For Olympic National Park, this batch intentionally migrates Ruby Beach only. Hurricane Ridge, Hoh Rain Forest and other distant subregions are researched subjects, but they are not added to the scoring catalog until ChaseLights supports an explicit per-Opportunity weather-sample coordinate or an equivalent safe contract.

## us-016 — Las Vegas Strip

Official sources:
- Las Vegas Convention and Visitors Authority — Strip:
  https://www.visitlasvegas.com/las-vegas-strip/
- Las Vegas Convention and Visitors Authority — Fountains of Bellagio:
  https://www.visitlasvegas.com/listing/fountains-of-bellagio/34849/

Verified:
- The Strip is officially described as a famous neon corridor / after-dark destination.
- Bellagio fountains are an official recurring choreographed water show.
- Official tourism publishes recurring showtimes and states times may vary or shows may be cancelled due to inclement weather.

Opportunities:
- P01 central Strip neon / LED night streetscape.
- P02 Bellagio fountain show with Strip lighting.

Runtime:
- P01 uses minimum-sufficient local-scene scoring.
- P02 remains module_pending under event_state because ChaseLights does not yet ingest the live recurring-show schedule/cancellation state.
- Static published hours are not treated as proof that a particular show is running.

## us-017 — Mount St. Helens

Official sources:
- USDA Forest Service — Johnston Ridge / Boundary Trail:
  https://www.fs.usda.gov/r06/giffordpinchot/recreation/trails/trail-1-boundary-johnston-ridge-truman-trail
- USDA Forest Service — South Coldwater Slide Information:
  https://www.fs.usda.gov/r06/giffordpinchot/recreation/south-coldwater-slide-information

Verified:
- Johnston Ridge / Boundary Trail is a documented crater / Spirit Lake / blast-zone viewpoint.
- Current ordinary road access to Johnston Ridge remains blocked by the SR 504 landslide closure.

Opportunity:
- P01 Johnston Ridge crater + blast-zone landscape.

Runtime:
- visibility + dynamic_access.
- `road_viewpoint_status` is registered with an official USFS source hint.
- No authoritative runtime provider is connected yet, so the Opportunity remains module_pending.
- Clear weather must never imply the closed Johnston Ridge route is open.

The current Place/Camera anchor remains the existing Johnston Ridge coordinate; it is not advertised as a routable destination while access is closed.

## us-018 — Glacier National Park

Official sources:
- NPS — Sunset at Lake McDonald:
  https://www.nps.gov/tours/view.htm?id=98F832BE-9093-2A45-DE1EDC615F095FA1
- NPS — Photo Tips:
  https://www.nps.gov/glac/planyourvisit/photo-tips.htm
- NPS — Night Sky:
  https://www.nps.gov/glac/learn/nature/night-sky.htm

Verified:
- NPS directly recommends Lake McDonald sunset and the Apgar public boat dock / shoreline as a popular viewing area.
- Glacier is an official dark-sky destination.
- NPS explicitly supports night-sky photography and astronomy activities at Apgar.
- NPS photo guidance notes Lake McDonald can provide a northern view for aurora when aurora independently occurs.

Opportunities:
- P01 Lake McDonald / Apgar sunset.
- P02 Lake McDonald / Apgar dark night sky.

Runtime:
- P01: directional_horizon + visibility.
- P02: astronomy_ephemeris.
- P02 does not guarantee aurora.
- P02 does not claim exact Galactic Core alignment with a fixed foreground.

## us-019 — Olympic National Park / Ruby Beach

Official sources:
- NPS — Ruby Beach:
  https://www.nps.gov/places/000/ruby-beach.htm
- NPS — Ruby Beach Overlook:
  https://www.nps.gov/places/000/ruby-beach-overlook.htm
- NPS — Day Hiking at Olympic:
  https://www.nps.gov/olym/planyourvisit/day-hiking-at-olympic.htm

Verified:
- Ruby Beach is a documented sea-stack / tide-pool coastal destination.
- Ruby Beach Overlook is an official Scenic View/Photo Spot.
- Official NPS imagery directly documents Ruby Beach at sunset.
- Coastal hiking requires tide awareness.

Opportunities:
- P01 sea stacks + driftwood coast.
- P02 Pacific sunset + sea stacks.

Runtime:
- P01: minimum-sufficient visibility.
- P02: marine_state + directional_horizon.
- The existing high-confidence Ruby Beach coordinate represents this batch's Camera Zone and weather sample reasonably well.
- Marine-state output remains coarse model-scale context and must not be presented as local shoreline-safety certification.
- Tide remains a separate safety/planning input for walking farther along the coast; this Opportunity does not infer a safe local crossing from marine-state alone.

Deferred:
- Hurricane Ridge mountain panorama.
- Hoh Rain Forest / Hall of Mosses.
- Rialto / other coast Camera Zones.

They require either their own weather-sample coordinate or another explicit safe sampling contract before production scoring.

## us-020 — Redwood National Park / Lady Bird Johnson Grove

Official sources:
- NPS — Lady Bird Johnson Grove Trail:
  https://www.nps.gov/places/lbjtrailhead.htm
- NPS — Lady Bird Johnson Nature Trail Stop #6:
  https://www.nps.gov/places/lady-bird-johnson-nature-trail-stop-6.htm
- NPS — Lady Bird Johnson Nature Trail Stop #11:
  https://www.nps.gov/places/lady-bird-johnson-nature-trail-stop-11.htm

Verified:
- Lady Bird Johnson Grove is an official old-growth redwood trail.
- NPS marks trail stops as Scenic View/Photo Spots and explicitly documents towering redwoods as the subject.
- NPS directly documents ground cloud / fog blanketing the redwood forest at the Grove.

Opportunities:
- P01 old-growth redwood forest + trail depth.
- P02 fog-layered redwood forest.

Runtime:
- P01 uses minimum-sufficient local-scene scoring.
- P02 requires a new reusable `mist_state` dependency.
- `mist_state` is known but not implemented, therefore P02 remains module_pending.
- Month / generic coastal climate does not prove the current Grove is foggy.

## Catalog delta

B65 adds:
- 5 curated US Places
- 9 Opportunities
- 9 Condition Variants
- 9 viewpoint relations

Expected canonical totals:
- 138 curated Places
- 306 Opportunities
- 321 Condition Variants
- 312 viewpoint relations

US migrated after B65:
- us-001 through us-020
- 20 Places / 36 Opportunities / 36 variants / 36 viewpoint relations

US research-pending:
- us-021 through us-070

## Runtime-policy delta

Relative to B64:

module_pending +3:
- us-016-P02 Bellagio recurring fountain show state
- us-017-P01 Johnston Ridge dynamic access
- us-020-P02 Redwood fog / mist state

preview_module_available +3:
- us-018-P01 Lake McDonald sunset
- us-018-P02 Lake McDonald night sky
- us-019-P02 Ruby Beach sunset

minimum_sufficient_available +3:
- us-016-P01 Strip night streetscape
- us-019-P01 Ruby Beach sea-stack coast
- us-020-P01 Lady Bird Johnson Grove old-growth forest

Expected policy totals:
- module_pending: 91
- preview_module_available: 105
- minimum_sufficient_available: 104
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

## QA

B65 updates:
- Adapter / integration coverage through us-020.
- Evidence registry for Glacier night sky and Lady Bird Johnson Grove fog.
- US Candidate Weather researched range to us-001 through us-020.
- Browser Smoke researched US card count to 20.
- Dynamic-access classification for Johnston Ridge.
- Marine-state profile for Ruby Beach sunset.
- Dependency inventory with standalone `needs_mist_state_module`.

Existing canonical Places us-001 through us-015 and all TW/JP Places must remain semantically unchanged.
