# ChaseLights R4.2 B70 — US Research Batch 07 (us-031 through us-035)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates the next five United States production Places into the canonical Opportunity catalog:

- us-031 Rocky Mountain National Park — narrowed to Sprague Lake
- us-032 New Orleans French Quarter
- us-033 Denver Skyline — moved to City Park / Ferril Lake
- us-034 Gateway Arch
- us-035 Fort Worth Stockyards

Canonical production data remains in `runtime_catalog_v004_r4_2.json`. This document records evidence and modeling decisions only.

## Modeling rules preserved

B70 continues the R4.2 boundaries established in earlier research batches:

- Place-specific evidence proves what is actually photographable.
- Runtime/provider data estimates when an admitted Opportunity may work.
- Camera Zone, weather sample, and Navigation Target remain separate concepts.
- Broad inventory coordinates do not become hard weather samples for a distant subject.
- Favorable weather never overrides an unresolved access, booking, closure, or event-state requirement.
- Seasonal appearance, event presence, livestock presence, reflection, snow, and lighting are not inferred from legacy tags or calendar month alone.

## us-031 — Rocky Mountain National Park / Sprague Lake

Official sources:
- NPS Sprague Lake:
  https://www.nps.gov/places/sprague-lake.htm
- NPS Bear Lake Road Corridor:
  https://www.nps.gov/romo/planyourvisit/exploring-the-bear-lake-road-corridor.htm
- NPS 2026 Timed Entry + Bear Lake Road:
  https://www.nps.gov/places/rmnp-timed-entry-%2B-bear-lake-road.htm
- Colorado DNR / CPW COTREX Sprague Lake Trailhead:
  https://trails.colorado.gov/trailheads/sprague-lake-1969

Verified:
- NPS classifies Sprague Lake as a Scenic View / Photo Spot.
- The public loop provides lake + Continental Divide mountain views.
- NPS explicitly describes the east shoreline and loop lookouts as photo opportunities.
- In 2026, Timed Entry + Bear Lake Road reservations are required from 05:00–18:00 daily May 22 through October 18 for this corridor.
- Sprague Lake is explicitly within the Bear Lake Road reservation corridor.
- COTREX provides a practical trailhead / arrival coordinate separate from the lakeshore Camera Zone.

Opportunity:
- P01 Sprague Lake + Continental Divide mountain skyline.

Runtime:
- visibility + dynamic_access.
- The Opportunity remains `module_pending` until ChaseLights has an authoritative current-access / entitlement provider.
- Good weather, calendar month, or static annual reservation rules cannot prove the user may currently enter.
- Reflection is an evidence-backed booster, not a hard `water_surface_state` requirement.
- The broad RMNP weather/map anchor is replaced by the actual Sprague Lake Camera Zone.
- Navigation uses the separately verified Sprague Lake Trailhead arrival coordinate.

## us-032 — New Orleans French Quarter

Official sources:
- New Orleans & Company — French Quarter Architecture:
  https://www.neworleans.com/plan/neighborhoods/french-quarter/architecture/
- New Orleans & Company — Royal Street:
  https://www.neworleans.com/plan/streets/royal-street/
- New Orleans & Company — self-guided French Quarter walk:
  https://www.neworleans.com/plan/neighborhoods/self-guided-new-orleans-neighborhood-walking-tours/self-guided-french-quarter-walking-tours/

Verified:
- Official destination guidance documents cast-iron balconies, Creole cottages, townhouses and other historic architectural subjects.
- Royal Street is explicitly presented as a historic street with characteristic architecture.
- Jackson Square, St. Louis Cathedral and surrounding public exterior streets are representative walkable photographic subjects.

Opportunity:
- P01 Royal Street / Jackson Square historic architecture and streetscape.

Runtime:
- minimum-sufficient local-scene contract.
- Long-range visibility is not a hard blocker for this close-range subject.
- Mardi Gras, street performers, decorations and special-event state are not guaranteed by this Opportunity.
- Private courtyards / interiors and commercial production permissions remain outside this general public-street contract.

## us-033 — Denver Skyline / City Park

Official sources:
- VISIT DENVER — photo opportunities:
  https://visitdenver.com/denver_org/visitdenver_com/things-to-do/itineraries/photo-opportunities/
- VISIT DENVER — city parks:
  https://visitdenver.com/things-to-do/sports-recreation/city-parks/
- City and County of Denver — park hours:
  https://denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Parks-Recreation/Urban-Parks-Trails/Park-Rangers

Verified:
- VISIT DENVER explicitly identifies City Park as a Denver skyline panorama framed by the Rocky Mountain Front Range.
- Official destination guidance recommends the magic hour before dusk as the sun descends behind the mountains.
- Denver publishes urban-park hours of 05:00–23:00.

Opportunity:
- P01 City Park / Ferril Lake + Denver skyline + Rocky Mountains sunset.

Runtime:
- directional_horizon + visibility.
- B70 does not invent a precise building-to-sun alignment; the broad west-facing sunset sector contract is sufficient for this researched panorama.
- The broad downtown Denver weather coordinate is replaced by the actual City Park / Ferril Lake camera area.
- Ferril Lake reflection, snow on the Front Range and dramatic clouds are boosters, not hard gates.

## us-034 — Gateway Arch

Official sources:
- NPS Gateway Arch park attractions:
  https://home.nps.gov/jeff/learn/news/gateway-arch-park-attractions.htm
- NPS Gateway Arch operating hours:
  https://www.nps.gov/jeff/planyourvisit/hours.htm

Verified:
- NPS documents many public viewpoints across the Arch grounds.
- NPS explicitly describes the park grounds as a photographic backdrop for the Arch in all seasons.
- The exterior park grounds are open 05:00–23:00 year-round; indoor visitor-center and tram contracts are separate.

Opportunity:
- P01 Gateway Arch + public park grounds / city / river context.

Runtime:
- minimum-sufficient local-scene contract.
- Indoor tickets or tram hours are not used as a gate for exterior grounds photography.
- Morning/evening light, reflecting surfaces and seasonal landscaping are boosters only.

## us-035 — Fort Worth Stockyards

Official sources:
- Fort Worth Stockyards — history:
  https://www.fortworthstockyards.org/history
- Fort Worth Stockyards — Livestock Exchange Building:
  https://www.fortworthstockyards.org/business/livestock-exchange-building
- Fort Worth Stockyards — cattle drive times & locations:
  https://www.fortworthstockyards.org/faq/cattle-drive-times-locations
- Fort Worth Stockyards — current Fort Worth Herd event:
  https://www.fortworthstockyards.org/events/fort-worth-herd-twice-daily-cattle-drive

Verified:
- The preserved historic district, brick streets and Livestock Exchange are official Stockyards subjects.
- The Livestock Exchange at 131 East Exchange Avenue is a central historic landmark.
- The official Fort Worth Herd cattle drive is listed at 11:30 and 16:00, weather permitting.
- The current 2026 listing documents cancellations / exceptions, including Easter Sunday, Thanksgiving and Christmas, and possible weather/site changes.
- Official guidance identifies the area in front of the Livestock Exchange as a primary public viewing location.

Opportunities:
- P01 Livestock Exchange + historic Exchange Avenue streetscape.
- P02 Fort Worth Herd Texas Longhorn cattle drive.

Runtime:
- P01 uses the minimum-sufficient local-scene contract.
- P02 uses `event_state` and remains `module_pending`.
- A static 11:30 / 16:00 timetable is not treated as proof that today's drive will occur.
- Weather/site cancellations and holiday exceptions require current event state before P02 can become a full-confidence recommendation.
- The broad district coordinate is moved to the Livestock Exchange / Exchange Avenue Camera Zone.

## Catalog delta

B70 adds:
- 5 curated US Places
- 6 Opportunities
- 6 Condition Variants
- 6 viewpoint relations

Expected canonical totals:
- 153 curated Places
- 326 Opportunities
- 341 Condition Variants
- 332 viewpoint relations

US migrated after B70:
- us-001 through us-035
- 35 Places / 56 Opportunities / 56 variants / 56 viewpoint relations

US research-pending:
- us-036 through us-070
- 35 Places

## Runtime-policy delta

Relative to B69:

`minimum_sufficient_available` +3:
- us-032-P01 French Quarter historic streetscape
- us-034-P01 Gateway Arch grounds
- us-035-P01 Stockyards historic streetscape

`preview_module_available` +1:
- us-033-P01 Denver City Park sunset panorama

`module_pending` +2:
- us-031-P01 Sprague Lake current access / reservation state + visibility
- us-035-P02 Fort Worth Herd current event state

Expected policy totals:
- module_pending: 97
- preview_module_available: 111
- minimum_sufficient_available: 112
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

Minimum-sufficient visibility profile count remains:
- 75

## QA

B70 updates:
- Adapter researched-US coverage through us-035.
- Adapter runtime policy / dependency assertions for all six new Opportunities.
- US Candidate Weather researched range through us-035 and pending count to 35.
- Browser Smoke researched-US count to 35 and pending count to 35.
- Sprague Lake Camera Zone/weather anchor plus separate verified trailhead Navigation Target.
- Denver weather sampling from broad downtown to City Park / Ferril Lake.
- Fort Worth Stockyards weather sampling from district-center to Livestock Exchange / Exchange Avenue.
- Sprague Lake dynamic-access classification and Denver directional-horizon profile.

Existing canonical us-001 through us-030 and all TW/JP curated Places must remain semantically unchanged.
