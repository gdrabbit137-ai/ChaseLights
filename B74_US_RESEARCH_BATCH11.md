# ChaseLights R4.2 B74 — Alaska Research Batch 11 (us-051 through us-055)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates the next five Alaska production Places into the canonical Opportunity catalog:

- us-051 Mendenhall Glacier
- us-052 Homer Spit
- us-053 Ketchikan / Creek Street
- us-054 Skagway / Arctic Brotherhood Hall
- us-055 Wrangell-St. Elias / Kennecott + Root Glacier

Canonical production data remains in `runtime_catalog_v004_r4_2.json`. This document records evidence and modeling decisions.

## Modeling rules preserved

- Place-specific evidence proves what can actually be photographed.
- Camera Zone, weather sample, and Navigation Target remain separate.
- Long-range mountain/glacier subjects require usable visibility.
- Close-range historic waterfront / streetscape subjects do not inherit arbitrary long-range visibility gates.
- Wildlife, salmon, snow, reflections, ships and seasonal foregrounds are boosters unless independently runtime-gated.
- Favorable weather never overrides a known or unresolved road, trail, closure or transport restriction.
- A public park/visitor-center coordinate is not automatically a road-navigation destination for a remote Camera Zone.

## us-051 — Mendenhall Glacier

Official sources:
- U.S. Forest Service Mendenhall Glacier Visitor Center brochure / trail map:
  https://www.fs.usda.gov/sites/nfs/files/r10/tongass/publication/MendenhallBrochure2025_0.pdf
- U.S. Forest Service destination information:
  https://www.fs.usda.gov/visit/destinations

Verified:
- Photo Point Trail is an official photo-oriented public trail in the Mendenhall Glacier recreation area.
- Nugget Falls Trail is an official public trail.
- The visitor-center recreation area provides Mendenhall Glacier / lake observation.
- Indoor Visitor Center hours are separate from the exterior photographic subjects.

Opportunities:
- P01 Photo Point + Mendenhall Glacier + Mendenhall Lake.
- P02 Nugget Falls + lake / glacial-valley context.

Runtime:
- both use minimum-sufficient visibility.
- no unique Nugget Falls tripod coordinate is invented.
- the existing Mendenhall Visitor Center weather anchor is local enough for both compact-area subjects.
- temporary closure / wildlife-management instructions remain authoritative over a weather score.

## us-052 — Homer Spit

Official sources:
- Travel Alaska — Homer:
  https://www.travelalaska.com/destinations/cities-towns/homer
- Travel Alaska — 6 Things to Do in Homer:
  https://www.travelalaska.com/explore-alaska/articles/6-things-do-homer

Verified:
- Homer Spit is a 4.5-mile public coastal landform extending into Kachemak Bay.
- Official state tourism guidance explicitly documents the Kachemak Bay / mountain / glacier panorama.
- Harbor, boats, beaches, shops and working waterfront activity are established Spit subjects.
- Wildlife and fishing activity vary and are not guaranteed.

Opportunities:
- P01 Kachemak Bay + mountains / glaciers panorama.
- P02 Homer Harbor / Spit shops + working-waterfront local scene.

Runtime:
- P01 uses minimum-sufficient visibility.
- P02 uses the minimum-sufficient local-scene contract.
- tide state is not a hard dependency because the admitted Camera Zone does not require entering the intertidal zone.
- B74 moves weather sampling from the broad Homer city point onto a cross-checked Homer Spit landform anchor.

## us-053 — Ketchikan / Creek Street

Official sources:
- Ketchikan Visitors Bureau — Historic Creek Street:
  https://www.visitktn.com/plan/places-to-discover/creek-street/
- City of Ketchikan — Tourism:
  https://www.ketchikan.gov/Tourism

Verified:
- Creek Street is an official historic public pedestrian subject with wooden boardwalk, stilted waterfront buildings and creek / rainforest context.
- Salmon runs are seasonal and sightings vary.
- Wildlife presence is also variable.

Opportunity:
- P01 Creek Street historic boardwalk + stilted-building waterfront scene.

Runtime:
- minimum-sufficient local-scene.
- salmon and wildlife remain boosters rather than mandatory or calendar-derived subjects.
- the existing downtown Ketchikan point is retained as a local weather anchor because the subject is compact and central.

## us-054 — Skagway / Arctic Brotherhood Hall

Official sources:
- Municipality of Skagway Visitor Department — Visitor Center:
  https://www.skagway.com/plan-your-trip/visitor-center/
- Municipality of Skagway Visitor Department — Fun Facts:
  https://www.skagway.com/plan-your-trip/about-the-area/fun-facts/

Verified:
- Arctic Brotherhood Hall was built in 1899 and has a distinctive driftwood facade.
- The municipal visitor department explicitly describes it as the most photographed building in Alaska.
- The official address is 205 Broadway.

Opportunity:
- P01 Arctic Brotherhood Hall facade + Broadway historic streetscape.

Runtime:
- minimum-sufficient local-scene.
- snow, cruise traffic, decorations and empty-street conditions are boosters only.
- B74 intentionally does not add a separate Dyea Road panorama Opportunity until a sufficiently precise public Camera Zone / weather-sample contract is documented.

## us-055 — Wrangell-St. Elias / Kennecott + Root Glacier

Official sources:
- NPS Kennecott Mines National Historic Landmark:
  https://www.nps.gov/places/kennecott-mines.htm
- NPS Root Glacier:
  https://www.nps.gov/places/root-glacier.htm
- NPS 2026 Root Glacier access reroute:
  https://www.nps.gov/wrst/learn/news/access-restored-to-root-glacier-via-new-trail-reroute.htm
- NPS directions to McCarthy Road & Kennecott:
  https://www.nps.gov/wrst/planyourvisit/directions-mccarthy-rd-and-kennecott.htm

Verified:
- NPS classifies Kennecott Mines as a Scenic View / Photo Spot and publishes an exact coordinate.
- NPS classifies Root Glacier as a Scenic View / Photo Spot and publishes the trailhead coordinate.
- Root Glacier access was temporarily closed in 2026 because of unstable terrain and then restored via a reroute; the original hazardous segment remains closed.
- Public vehicle access does not extend directly into Kennecott. Visitors park near the Kennicott River bridge and continue by foot, bike or seasonal shuttle.
- Winter access differs substantially from summer access.

Opportunities:
- P01 Kennecott Mines historic red buildings + Wrangell mountains / glacier context.
- P02 Root Glacier trail / glacier + mountain scene.

Runtime:
- both use visibility + dynamic_access.
- both remain `module_pending` until an authoritative current-access provider is connected.
- no exact Directions link is created to the Kennecott Camera Zone because public vehicle access ends before the mill town.
- favorable weather cannot imply McCarthy Road, shuttle, reroute or trail availability.

## Catalog delta

B74 adds:
- 5 curated US Places
- 8 Opportunities
- 8 Condition Variants
- 8 viewpoint relations

Expected canonical totals:
- 173 curated Places
- 356 Opportunities
- 371 Condition Variants
- 362 viewpoint relations

US migrated after B74:
- us-001 through us-055
- 55 Places / 86 Opportunities / 86 variants / 86 viewpoint relations

US research-pending:
- us-056 through us-070
- 15 Places

## Runtime-policy delta

Relative to B73:

`minimum_sufficient_available` +6:
- us-051-P01 Mendenhall Photo Point
- us-051-P02 Nugget Falls
- us-052-P01 Homer Spit Kachemak panorama
- us-052-P02 Homer Spit harbor local scene
- us-053-P01 Creek Street
- us-054-P01 Arctic Brotherhood Hall

`module_pending` +2:
- us-055-P01 Kennecott current access + visibility
- us-055-P02 Root Glacier current access + visibility

Expected policy totals:
- module_pending: 111
- preview_module_available: 113
- minimum_sufficient_available: 126
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

Minimum-sufficient visibility profile count:
- 85

## QA

B74 updates:
- Adapter researched-US coverage through us-055.
- Both researched-US guards in Adapter tests.
- Runtime policy / dependency assertions for all eight new Opportunities.
- US Candidate Weather researched range through us-055 and pending count to 15.
- Browser Smoke researched-US count to 55 and pending count to 15.
- Homer weather sampling to the actual Spit.
- Wrangell-St. Elias weather sampling from the broad legacy park coordinate to Kennecott.
- Wrangell-St. Elias dynamic-access classifications for Kennecott and Root Glacier.

Existing canonical us-001 through us-050 and all TW/JP curated Places must remain semantically unchanged.
