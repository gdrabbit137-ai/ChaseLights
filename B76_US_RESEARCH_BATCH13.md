# ChaseLights R4.2 B76 — Alaska Research Batch 13 (us-061 through us-065)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates the next five Alaska production Places into the canonical R4.2 Opportunity catalog:

- us-061 Kodiak Island — narrowed to Fort Abercrombie State Historical Park
- us-062 Eklutna Lake — Lakeside Trail / shoreline
- us-063 Talkeetna — Riverfront Park / Susitna River
- us-064 Alyeska Resort — Mountain Station / observation deck
- us-065 Chugach State Park — Glen Alps / Anchorage Overlook

Canonical production data remains in `runtime_catalog_v004_r4_2.json`. This file records the research evidence and modeling boundaries.

## Modeling rules preserved

- Place-specific evidence proves what is actually photographable.
- Camera Zone, weather sample and Navigation Target remain separate concepts.
- A broad inventory coordinate is not retained when the researched photographic scene is materially elsewhere.
- Reflection, snow, wildflowers, wildlife and other optional foreground/state details are boosters unless independently runtime-gated.
- A facility, tram, road or trail access requirement is never overridden by favorable weather.
- Aurora remains fail-closed on location-aware `aurora_state`; planetary Kp alone is insufficient.

## us-061 — Kodiak Island / Fort Abercrombie State Historical Park

Official sources:
- Alaska DNR / State Parks — Fort Abercrombie:
  https://dnr.alaska.gov/parks/aspunits/kodiak/fortabercrombieshp.htm
- Alaska State Parks — facility details:
  https://alaskastateparks.reserveamerica.com/camping/fort-abercrombie-state-historic-park/r/facilityDetails.do?contractCode=AK&parkId=1180732
- Alaska State Parks — Fort Abercrombie brochure:
  https://dnr.alaska.gov/parks/brochures/ftabercrombiebrochure.pdf

Verified:
- The park combines surf-pounded coastal cliffs, spruce forest, meadows and public trails.
- Official State Parks material documents scenic ocean-cliff overlooks.
- WWII coastal-defense remains / bunkers are a distinct historic photography subject.
- The official State Parks facility listing publishes GPS 57.82759, -152.35664.

Opportunities:
- P01 coastal cliffs + spruce / Monashka Bay scene.
- P02 WWII coastal-defense structures + coastal/forest context.

Runtime:
- both use minimum-sufficient local-scene contracts.
- Long-range visibility is not a hard blocker for these close-range scenes.
- B76 moves Kodiak's broad city/island weather anchor to Fort Abercrombie.
- No cliff-edge or closed-structure access is implied.

## us-062 — Eklutna Lake

Official sources:
- Alaska State Parks — Chugach Recreational Opportunities:
  https://dnr.alaska.gov/parks/aspunits/chugach/recops.htm
- Alaska State Parks — Eklutna Lake Campground:
  https://dnr.alaska.gov/parks/aspunits/chugach/eklutnalkcamp.htm

Verified:
- Alaska State Parks explicitly recommends Eklutna Lake for reflective lake shots, canyon walls, wildflowers and mountainous views.
- The Lakeside Trail provides views of steep canyon walls, waterfalls and Eklutna Glacier.
- Photography is documented as a year-round activity.

Opportunity:
- P01 Eklutna Lake + canyon walls / Chugach mountain backdrop.

Runtime:
- minimum-sufficient visibility.
- Reflection is a booster, not a hard `water_surface_state` requirement.
- Wildflowers and snow are current-state boosters rather than month-derived guarantees.
- Weather sampling moves to the Lakeside Trail / shoreline scene at a cross-mapped trailhead-area anchor.

## us-063 — Talkeetna / Riverfront Park

Official sources:
- Travel Alaska — Denali National Park by Rail:
  https://www.travelalaska.com/explore-alaska/itineraries/denali_national_park_by_rail
- Travel Alaska — 7 Things to Do in Talkeetna:
  https://www.travelalaska.com/explore-alaska/articles/7-things-do-talkeetna

Verified:
- Travel Alaska explicitly recommends Talkeetna Riverfront Park for clear-day views of Denali and the Susitna River.
- Official state tourism guidance identifies the Susitna River area as one of Talkeetna's best Denali-view settings.

Opportunity:
- P01 Susitna / Talkeetna river foreground + Denali / Alaska Range panorama.

Runtime:
- minimum-sufficient visibility.
- B76 does not invent a precise sunrise/sunset alignment.
- Low-angle light, snow and reflections are boosters only.
- Weather sampling moves from town center to Riverfront Park.

## us-064 — Alyeska Resort / Mountain Station

Official sources:
- Alyeska Resort — Aerial Tram Summer:
  https://www.alyeskaresort.com/aerial-tram-summer/
- Alyeska Resort — Hotel Amenities / Mountain Station:
  https://www.alyeskaresort.com/hotel-amenities/
- Alyeska Resort — Aerial Tram Winter:
  https://www.alyeskaresort.com/aerial-tram-winter/

Verified:
- Alyeska directly documents bird's-eye views of Turnagain Arm, seven hanging glaciers and the Chugach Mountain Range.
- The Mountain Station observation deck is a public panoramic subject when accessible.
- Tram operation is a managed, condition- and maintenance-dependent transport contract.

Opportunity:
- P01 Mountain Station / observation deck panorama.

Runtime:
- `dynamic_access + visibility`.
- P01 remains `module_pending` until an authoritative current Alyeska tram/access provider is connected.
- Static seasonal hours or favorable visibility cannot imply that the upper Camera Zone is reachable.
- B76 moves weather sampling from the resort base to the upper tram / Mountain Station area.
- The summit coordinate is not promoted to a road-navigation destination.

## us-065 — Chugach State Park / Glen Alps

Official sources:
- Alaska State Parks — Chugach Recreational Opportunities:
  https://dnr.alaska.gov/parks/aspunits/chugach/recops.htm
- Alaska State Parks — Glen Alps:
  https://dnr.alaska.gov/parks/aspunits/chugach/glenalps.htm
- Alaska State Parks — Accessibility:
  https://dnr.alaska.gov/parks/asp/access.htm

Verified:
- Glen Alps / Anchorage Overlook provides views over Anchorage, Cook Inlet and the Alaska Range.
- Alaska State Parks explicitly calls the overlook good for sunsets.
- Alaska State Parks' photography guidance identifies Anchorage Hillside for northern-lights photography.

Opportunities:
- P01 Glen Alps / Anchorage Overlook sunset panorama.
- P02 Anchorage Hillside / Glen Alps aurora.

Runtime:
- P01 uses `directional_horizon + visibility` and is preview-module available.
- P02 uses `aurora_state` and remains module-pending.
- B76 does not infer aurora from Kp alone.
- B76 narrows the broad Chugach State Park weather anchor to the Glen Alps viewpoint area.
- Denali visibility, snow and alpine flora remain optional current-state boosters.

## Catalog delta

B76 adds:
- 5 curated US Places
- 7 Opportunities
- 7 Condition Variants
- 7 viewpoint relations

Expected canonical totals:
- 183 curated Places
- 373 Opportunities
- 388 Condition Variants
- 379 viewpoint relations

US migrated after B76:
- us-001 through us-065
- 65 Places / 103 Opportunities / 103 variants / 103 viewpoint relations

US research-pending:
- us-066 through us-070
- 5 Places

## Runtime-policy delta

Relative to B75:

`minimum_sufficient_available` +4:
- us-061-P01 Fort Abercrombie coastal scene
- us-061-P02 Fort Abercrombie WWII historic scene
- us-062-P01 Eklutna Lake panorama
- us-063-P01 Talkeetna / Denali panorama

`preview_module_available` +1:
- us-065-P01 Glen Alps sunset panorama

`module_pending` +2:
- us-064-P01 Alyeska Mountain Station tram access + visibility
- us-065-P02 Chugach / Glen Alps aurora state

Expected policy totals:
- module_pending: 121
- preview_module_available: 114
- minimum_sufficient_available: 132
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

Minimum-sufficient visibility profile count:
- 88

## QA

B76 updates:
- both Adapter researched-US guards through us-065,
- Adapter policy/dependency assertions for all seven new Opportunities,
- US Candidate Weather researched range through us-065 and pending count to 5,
- Browser Smoke researched-US count to 65 and pending count to 5,
- Alyeska dynamic-access classification,
- Chugach directional-horizon profile,
- Kodiak / Eklutna / Talkeetna / Alyeska / Glen Alps Camera Zone and weather anchors.

Existing canonical us-001 through us-060 and all TW/JP curated Places must remain semantically unchanged.
