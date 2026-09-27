# ChaseLights R4.2 B72 — US Research Batch 09 (us-041 through us-045)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates the first Alaska-focused block of the United States production inventory:

- us-041 Denali National Park — Mountain Vista
- us-042 Fairbanks Aurora — Creamer's Field
- us-043 Chena Hot Springs — resort grounds
- us-044 Anchorage — Point Woronzof
- us-045 Seward — Waterfront Park / Resurrection Bay

Canonical production data remains in `runtime_catalog_v004_r4_2.json`. This document records evidence and modeling decisions only.

## Critical aurora boundary introduced in B72

Legacy ChaseLights weather output already fetches NOAA planetary Kp and can display a broad aurora-oriented Theme score. B72 does **not** promote that legacy heuristic into the canonical Opportunity runtime contract.

A researched aurora Opportunity requires a dedicated `aurora_state` dependency because:
- planetary Kp is a global geomagnetic index, not a location-specific guarantee of visible aurora,
- local auroral oval position / forecast, darkness, cloud obstruction and site-specific sky geometry matter,
- strong Kp does not prove a photographed display exists at the user's Camera Zone,
- weak or unavailable Kp does not by itself prove a display is impossible,
- official Alaska destination guidance repeatedly states aurora is a natural phenomenon and cannot be guaranteed.

B72 therefore adds dependency declarations:
- `needs_aurora_state_module`
- `needs_aurora_state_dynamic_access_module`

`aurora_state` is intentionally **not runtime-implemented in B72**. Aurora Opportunities remain `module_pending` until a location-aware authoritative provider contract is designed and connected.

This is a fail-closed product decision, not a removal of the existing NOAA Kp display data.

## us-041 — Denali National Park / Mountain Vista

Official sources:
- NPS Photography in Denali:
  https://www.nps.gov/dena/planyourvisit/photography.htm
- NPS Mountain Vista:
  https://www.nps.gov/places/dena-mountain-vista.htm
- NPS Mountain Vista access:
  https://www.nps.gov/dena/planyourvisit/mountain-vista.htm
- NPS 2026 road opening:
  https://www.nps.gov/dena/learn/news/road-open-to-mtn-vista-2026.htm
- NPS Aurora Borealis and Star Gazing:
  https://www.nps.gov/dena/planyourvisit/night-sky.htm

Verified:
- NPS classifies Mountain Vista as a Scenic View / Photo Spot.
- Mountain Vista near Mile 13 provides clear-day Denali / Alaska Range views.
- The public rest area and short loop provide a practical Camera Zone.
- Vehicle access can change with snow, ice and current Denali Park Road conditions.
- NPS directly supports aurora / night-sky viewing in Denali but does not guarantee aurora occurrence.
- NPS explains that aurora visibility requires actual activity, darkness and sufficiently clear skies.

Opportunities:
- P01 Mountain Vista + Denali / Alaska Range panorama.
- P02 Mountain Vista aurora / dark-night foreground.

Runtime:
- P01 requires `dynamic_access + visibility`.
- P02 requires `aurora_state + dynamic_access`.
- Both remain fail-closed on Mountain Vista road access.
- P02 additionally remains fail-closed on the new unimplemented local aurora-state provider.
- The broad Denali Visitor Center weather anchor is replaced by Mountain Vista.
- Mountain Vista receives a separate verified Navigation Target; current road closure state overrides that navigation target.

## us-042 — Fairbanks Aurora / Creamer's Field

Official sources:
- Explore Fairbanks Aurora Tracker:
  https://www.explorefairbanks.com/explore-the-area/aurora-season/aurora-tracker/
- Explore Fairbanks Aurora Viewing Locations:
  https://www.explorefairbanks.com/explore-the-area/aurora-season/aurora-viewing-locations/
- Alaska Department of Fish and Game — Creamer's Field:
  https://www.adfg.alaska.gov/index.cfm?adfg=creamersfield.permits

Verified:
- Explore Fairbanks identifies Creamer's Field as a favorite in-town aurora location.
- The open fields provide a practical wide-sky Camera Zone.
- Explore Fairbanks defines an official Aurora Season of August 21 through April 21.
- Its own tracker combines UAF aurora information, local weather and daylight rather than relying on Kp alone.
- ADF&G identifies compatible public uses at Creamer's Field, subject to refuge rules.

Opportunity:
- P01 Creamer's Field + Aurora Borealis.

Runtime:
- requires `aurora_state`.
- remains `module_pending`.
- August 21–April 21 is a useful darkness/season boundary, not a promise that aurora will occur on a given night.
- Generic Fairbanks city weather sampling is moved to the actual Creamer's Field Camera Zone.

## us-043 — Chena Hot Springs

Official sources:
- Chena Hot Springs Resort — Aurora Borealis:
  https://www.chenahotsprings.com/aurora-borealis/
- Chena Hot Springs Resort:
  https://www.chenahotsprings.com/
- Chena Hot Springs Resort — Aurora Viewing Tour:
  https://www.chenahotsprings.com/aurora-viewing-tour/

Verified:
- Chena's official material identifies Northern Lights viewing as a signature activity.
- The resort describes its low-light-pollution setting under the auroral oval.
- Official guidance states aurora viewing can begin on the resort grounds.
- The resort explicitly states aurora is a natural phenomenon and cannot be guaranteed.

Opportunity:
- P01 Chena resort grounds + Aurora Borealis.

Runtime:
- requires `aurora_state`.
- remains `module_pending`.
- B72 deliberately uses the verified resort location as Camera Zone/weather sample.
- The paid Charlie Dome tour is a different access/elevation/microclimate contract and is **not** silently substituted as this Opportunity's weather sample.
- Being beneath the auroral oval does not itself satisfy the Opportunity.

## us-044 — Anchorage / Point Woronzof

Official sources:
- Visit Anchorage — scenic overlooks:
  https://www.anchorage.net/blog/post/top-anchorage-scenic-overlooks/
- Visit Anchorage — On Wheels itinerary:
  https://www.anchorage.net/plan-your-trip/itineraries/on-wheels/
- Visit Anchorage — Aurora Borealis viewing itinerary:
  https://www.anchorage.net/winter/plan-your-trip/winter-itineraries/aurora-borealis-viewing/

Verified:
- Visit Anchorage documents Point Woronzof panoramic Cook Inlet / Alaska Range views.
- Official destination guidance explicitly calls out Point Woronzof for sunset.
- Official aurora guidance recommends Point Woronzof for northern views away from city lights.

Opportunities:
- P01 Point Woronzof + Cook Inlet / Alaska Range sunset.
- P02 Point Woronzof + Anchorage aurora.

Runtime:
- P01 requires `directional_horizon + visibility` and is preview-ready.
- P02 requires `aurora_state` and remains module-pending.
- The generic Anchorage city coordinate is replaced by Point Woronzof for this Place's weather sampling.
- Seasonal snow, sea ice and Denali visibility are boosters only.
- No exact parking Navigation Target is asserted in B72 because the researched evidence supports the Camera Zone better than a single surveyed arrival point.

## us-045 — Seward / Waterfront Park

Official sources:
- Visit Seward Alaska — Plan Your Visit:
  https://www.seward.com/plan-your-visit/
- Visit Seward Alaska — Campgrounds & RV Parks:
  https://www.seward.com/lodging/campgrounds-and-rv-parks/
- City of Seward / Qutekcak Native Tribe Hazard Mitigation Plan:
  https://www.cityofseward.us/home/showpublisheddocument/2148/637469154378300000

Verified:
- Visit Seward describes Seward at the head of Resurrection Bay between mountains and ocean.
- Official destination guidance identifies waterfront views of Resurrection Bay and Mt. Alice.
- City material identifies Seward Waterfront Park and provides a practical municipal facility coordinate.

Opportunity:
- P01 Seward Waterfront + Resurrection Bay + Mt. Alice / surrounding mountains.

Runtime:
- minimum-sufficient visibility contract.
- boats, wildlife, calm reflections, snow and special light remain boosters rather than guaranteed subjects.
- the generic Seward city coordinate is replaced by Waterfront Park.
- a representative public Waterfront Park coordinate is used as the verified Navigation Target, while compositions can be refined on foot along the legal shoreline / trail.

## Catalog delta

B72 adds:
- 5 curated US Places
- 7 Opportunities
- 7 Condition Variants
- 7 viewpoint relations

Expected canonical totals:
- 163 curated Places
- 340 Opportunities
- 355 Condition Variants
- 346 viewpoint relations

US migrated after B72:
- us-001 through us-045
- 45 Places / 70 Opportunities / 70 variants / 70 viewpoint relations

US research-pending:
- us-046 through us-070
- 25 Places

## Runtime-policy delta

Relative to B71:

`module_pending` +5:
- us-041-P01 Denali Mountain Vista access + visibility
- us-041-P02 Denali aurora + access
- us-042-P01 Fairbanks / Creamer's Field aurora
- us-043-P01 Chena aurora
- us-044-P02 Anchorage / Point Woronzof aurora

`preview_module_available` +1:
- us-044-P01 Point Woronzof sunset

`minimum_sufficient_available` +1:
- us-045-P01 Seward Waterfront panorama

Expected policy totals:
- module_pending: 104
- preview_module_available: 113
- minimum_sufficient_available: 117
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

Minimum-sufficient visibility profile count:
- 79

## QA / release expectations

B72 updates:
- dependency inventory with the unimplemented `aurora_state` component and its two formula statuses,
- canonical catalog and manifest through us-045,
- Denali current-access classification,
- Denali, Fairbanks, Anchorage and Seward Camera Zone/weather anchors,
- Denali and Seward verified Navigation Targets,
- Anchorage sunset directional-horizon profile,
- Seward minimum-sufficient visibility profile,
- Adapter researched-US coverage through us-045,
- both Adapter researched-US guard locations,
- US Candidate Weather researched range through us-045 and pending count to 25,
- Browser Smoke researched-US count to 45 and pending count to 25.

Release gates:
- Adapter must pass with `aurora_state` still missing from `IMPLEMENTED_COMPONENTS`.
- All four canonical aurora Opportunities must report `module_pending`.
- Evidence Audit must pass.
- TW / JP / US Candidate Weather must pass.
- Browser Smoke must pass.
- Generated candidate weather must not be committed in the PR.

Existing us-001 through us-040 and all Taiwan/Japan curated Opportunities must remain semantically unchanged.
