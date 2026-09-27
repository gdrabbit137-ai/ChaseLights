# ChaseLights R4.2 B71 — US Research Batch 08 (us-036 through us-040)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates the next five United States production Places into the canonical Opportunity catalog:

- us-036 Manhattan Skyline — moved to Gantry Plaza State Park
- us-037 Niagara Falls — Terrapin Point / public falls overlooks
- us-038 Great Smoky Mountains National Park — narrowed to Newfound Gap Overlook
- us-039 Miami Beach — South Pointe Beach / Beachwalk / waterfront
- us-040 Boston Skyline — moved to Piers Park, East Boston

Canonical production data remains in `runtime_catalog_v004_r4_2.json`. This document records the evidence and modeling decisions.

## Modeling rules preserved

B71 continues the R4.2 boundaries:

- Place-specific evidence proves what can actually be photographed.
- Runtime/provider data estimates when an admitted Opportunity may work.
- Camera Zone, weather sample and Navigation Target remain separate concepts.
- Broad city-center or park-center coordinates are not reused when the researched subject is photographed from another location.
- Favorable weather never overrides a current road / access closure.
- Managed lighting and event state remain fail-closed until a current provider exists.
- Reflection, seasonal appearance, ships, rainbow, snow and other optional foregrounds are boosters unless separately runtime-gated.

## us-036 — Manhattan Skyline / Gantry Plaza

Official source:
- New York State Parks — Gantry Plaza State Park:
  https://parks.ny.gov/visit/state-parks/gantry-plaza-state-park

Verified:
- Gantry Plaza is a public East River waterfront park.
- New York State Parks directly documents spectacular views of the Midtown Manhattan skyline, including the Empire State Building and United Nations.

Opportunity:
- P01 Gantry Plaza + Midtown Manhattan skyline + East River.

Runtime:
- minimum-sufficient visibility.
- B71 moves weather/map sampling away from Manhattan itself to the actual cross-river Gantry Plaza Camera Zone.
- No nighttime-lighting state is required for the base skyline Opportunity.
- River reflections and special lighting are optional boosters only.

## us-037 — Niagara Falls

Official sources:
- New York State Parks — Niagara Falls State Park:
  https://parks.ny.gov/visit/state-parks/niagara-falls-state-park
- Niagara Falls State Park — Overlooks & Vistas:
  https://www.niagarafallsstatepark.com/attractions/overlooks-vistas/
- Niagara Falls State Park — Park Map:
  https://www.niagarafallsstatepark.com/park-information/niagara-state-park-map/

Verified:
- Terrapin Point is an official public Horseshoe Falls overlook.
- The park provides year-round waterfall viewpoints.
- Official park material separately documents nightly Falls illumination.

Opportunities:
- P01 Terrapin Point + Horseshoe Falls / waterfall mist.
- P02 illuminated Niagara Falls at night.

Runtime:
- P01 uses the minimum-sufficient local-scene contract because the near waterfall itself is a persistent subject; no generic waterfall-flow provider is required.
- Mist / whiteout remains a scene-quality penalty rather than a proof that the waterfall is absent.
- P02 requires `managed_lighting_state` and remains `module_pending`; ChaseLights must not infer tonight's lighting from static general descriptions.
- B71 moves the Place/weather anchor to Terrapin Point.

## us-038 — Great Smoky Mountains / Newfound Gap

Official sources:
- NPS Newfound Gap Overlook:
  https://www.nps.gov/places/newfound-gap-overlook.htm
- NPS seasonal road schedule:
  https://home.nps.gov/grsm/planyourvisit/seasonalroads.htm
- NPS current road / facility closures:
  https://www.nps.gov/grsm/planyourvisit/temproadclose.htm

Verified:
- NPS classifies Newfound Gap Overlook as a Scenic View / Photo Spot.
- Newfound Gap Road / US 441 is normally open year-round but weather permitting.
- Snow, ice, high winds or other hazards can close the road.

Opportunity:
- P01 Newfound Gap layered Smoky Mountains ridges.

Runtime:
- visibility + dynamic_access.
- B71 remains fail-closed until ChaseLights has a current authoritative road-status provider.
- Clear forecast weather does not prove US 441 / Newfound Gap Road is currently open.
- The exact overlook area is used for Camera Zone/weather sampling and as a verified navigation reference because NPS identifies public overlook/parking access there.

## us-039 — Miami Beach / South Pointe

Official sources:
- City of Miami Beach — South Pointe Park:
  https://www.miamibeachfl.gov/city-hall/parks-and-recreation/parks-facilities-directory/south-pointe-park/
- City of Miami Beach — Beachwalk:
  https://www.miamibeachfl.gov/city-hall/parks-and-recreation/parks-facilities-directory/beachwalk/
- Greater Miami Convention & Visitors Bureau — Miami in 1 Day:
  https://www.miamiandbeaches.com/plan-your-trip/miami-itineraries/miami-in-1-day
- Greater Miami Convention & Visitors Bureau — South Pointe Park:
  https://www.miamiandbeaches.com/l/outdoor-experiences/south-pointe-park/2966

Verified:
- Official destination guidance recommends sunrise on Miami Beach.
- South Pointe provides panoramic coastline, PortMiami, Downtown Miami skyline and Fisher Island views.
- South Pointe Park itself uses sunrise-to-sunset hours.
- The oceanfront Beachwalk provides continuous public pedestrian access, so the sunrise Opportunity is modeled from South Pointe Beach / Beachwalk rather than assuming early access to every park facility.

Opportunities:
- P01 Atlantic sunrise from South Pointe Beach / Beachwalk.
- P02 South Pointe + Downtown Miami / PortMiami panorama.

Runtime:
- P01 uses directional_horizon + visibility.
- P02 uses minimum-sufficient visibility.
- Cruise ships are optional foregrounds, never guaranteed from a timetable.
- Coastal safety closures override photographic conditions.
- B71 moves the broad South Beach weather/map anchor to the South Pointe area.

## us-040 — Boston Skyline / Piers Park

Official sources:
- Massachusetts Port Authority — Piers Park / public waterfront documentation:
  https://www.massport.com/
- Meet Boston — East Boston / waterfront:
  https://www.meetboston.com/explore/neighborhoods/

Verified:
- Massport documents Piers Park as a public East Boston waterfront park overlooking Boston Harbor and downtown Boston with skyline views.
- Boston's official destination organization identifies East Boston as a waterfront skyline-view area.

Opportunity:
- P01 Piers Park + Downtown Boston skyline + Boston Harbor.

Runtime:
- minimum-sufficient visibility.
- B71 moves the weather/map anchor from downtown Boston to the actual East Boston Camera Zone.
- Harbor boats, reflections and special events remain optional boosters.

## Catalog delta

B71 adds:
- 5 curated US Places
- 7 Opportunities
- 7 Condition Variants
- 7 viewpoint relations

Expected canonical totals:
- 158 curated Places
- 333 Opportunities
- 348 Condition Variants
- 339 viewpoint relations

US migrated after B71:
- us-001 through us-040
- 40 Places / 63 Opportunities / 63 variants / 63 viewpoint relations

US research-pending:
- us-041 through us-070
- 30 Places

## Runtime-policy delta

Relative to B70:

`minimum_sufficient_available` +4:
- us-036-P01 Gantry Plaza skyline
- us-037-P01 Terrapin Point waterfall
- us-039-P02 South Pointe Miami panorama
- us-040-P01 Piers Park Boston skyline

`preview_module_available` +1:
- us-039-P01 South Pointe sunrise

`module_pending` +2:
- us-037-P02 Niagara managed illumination
- us-038-P01 Newfound Gap road access + visibility

Expected policy totals:
- module_pending: 99
- preview_module_available: 112
- minimum_sufficient_available: 116
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

Minimum-sufficient visibility profile count:
- 78

## QA

B71 updates:
- Adapter researched-US coverage through us-040.
- Runtime-policy / dependency assertions for all seven new Opportunities.
- US Candidate Weather researched range through us-040 and pending count to 30.
- Browser Smoke researched-US count to 40 and pending count to 30.
- Manhattan weather sampling from Manhattan center to Gantry Plaza.
- Niagara weather sampling to Terrapin Point.
- Great Smoky Mountains weather/navigation anchor to Newfound Gap with dynamic-access classification.
- Miami weather sampling to South Pointe, while keeping sunrise tied to beach / Beachwalk access semantics.
- Boston weather sampling from downtown to Piers Park.
- South Pointe sunrise directional-horizon registry.

Existing canonical us-001 through us-035 and all TW/JP curated Places must remain semantically unchanged.
