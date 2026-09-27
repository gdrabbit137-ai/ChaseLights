# ChaseLights R4.2 B73 — Alaska Research Batch 10 (us-046 through us-050)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates the next five Alaska production Places into the canonical Opportunity catalog:

- us-046 Hatcher Pass
- us-047 Matanuska Glacier
- us-048 Portage Glacier
- us-049 Valdez
- us-050 Juneau

Canonical production data remains in `runtime_catalog_v004_r4_2.json`.

## Modeling rules preserved

- Place-specific evidence proves what can actually be photographed.
- Runtime/provider data estimates when an admitted Opportunity may work.
- Camera Zone, weather sample, and Navigation Target are separate concepts.
- Current access/closure state always overrides favorable weather.
- Static seasonal schedules do not prove current operation.
- Aurora remains fail-closed behind the location-aware `aurora_state` dependency introduced in B72.
- Reflection, snow, wildlife, boats, foliage and other transient foregrounds remain boosters unless independently modeled.

## us-046 — Hatcher Pass

Official sources:
- Alaska DNR — Summit Lake State Recreation Site:
  https://dnr.alaska.gov/parks/aspunits/matsu/summitlksrs.htm
- Alaska DNR — Hatcher Pass East Management Area:
  https://dnr.alaska.gov/parks/aspunits/matsu/hatcherpassema.htm
- Travel Alaska — Hatcher Pass:
  https://www.travelalaska.com/Destinations/Cities-Towns/Hatcher-Pass
- Travel Alaska — Best Places to See the Northern Lights:
  https://www.travelalaska.com/explore-alaska/articles/best-places-see-northern-lights-alaska

Verified:
- Alaska State Parks explicitly lists photography at Summit Lake and describes the glacially carved alpine scenery.
- Summit road vehicle access is seasonal and generally closed in winter.
- Official state tourism guidance identifies Hatcher Pass as a photographed alpine panorama and aurora-viewing area.
- Winter aurora viewing must use currently accessible public winter parking/recreation areas rather than assuming Summit Lake is reachable.

Opportunities:
- P01 Summit Lake alpine lake + Talkeetna Mountains.
- P02 Hatcher Pass mountain/snow foreground + Aurora Borealis.

Runtime:
- P01 = dynamic_access + visibility.
- P02 = aurora_state + dynamic_access.
- Both remain `module_pending` because current road/public-parking access is not yet connected.
- The summer Summit Lake parking Navigation Target must not be reused as proof of winter summit-road access.

## us-047 — Matanuska Glacier

Official sources:
- Alaska DNR — Matanuska Glacier State Recreation Site:
  https://dnr.alaska.gov/parks/aspunits/matsu/matsuglsrs.htm
- Alaska DNR — Matanuska Glacier Cabin / site GPS:
  https://dnr.alaska.gov/parks/aspcabins/matglaciercabin.htm
- Travel Alaska — Matanuska Glacier:
  https://www.travelalaska.com/destinations/parks-public-lands/matanuska-glacier

Verified:
- The public Mile 101 State Recreation Site provides some of the safest and best public glacier-viewing opportunities.
- Edge Nature Trail leads to glacier-viewing platforms.
- The recreation site does not provide direct glacier access.
- Glacier walking requires a separate guided/private access contract.
- The site can close because of winter snow and ice.
- Alaska DNR publishes an exact site GPS anchor.

Opportunity:
- P01 Matanuska Glacier + Matanuska Valley / Chugach Mountains public overlook.

Runtime:
- dynamic_access + visibility.
- B73 corrects the old broad Place coordinate to the official public viewing site.
- The verified Navigation Target is the public State Recreation Site, not the private glacier entrance.

## us-048 — Portage Glacier

Official sources:
- U.S. Forest Service — Chugach National Forest Visitor Guide:
  https://www.fs.usda.gov/Internet/FSE_DOCUMENTS/fseprd1101873.pdf
- Travel Alaska — Portage Glacier:
  https://www.travelalaska.com/destinations/parks-public-lands/portage-glacier

Verified:
- Trail of Blue Ice is a public Portage Valley trail with glacial-valley views and is described by USFS as always open.
- Portage Glacier has retreated and is no longer visible from the Begich, Boggs Visitor Center.
- The MV Ptarmigan seasonal cruise provides a close Portage Glacier view.

Opportunities:
- P01 Portage Lake / Portage Valley + surrounding alpine glaciers and mountains.
- P02 Portage Glacier face from the authorized MV Ptarmigan / Portage Lake cruise.

Runtime:
- P01 = minimum-sufficient visibility.
- P02 = timetable + dynamic_access and remains `module_pending`.
- The P02 viewpoint is a mobile on-lake Camera Zone; the Begich Boggs coordinate is only a nearby weather/embarkation anchor.
- An old seasonal schedule cannot prove a current sailing.

## us-049 — Valdez

Official sources:
- City of Valdez — Dock Point Trail:
  https://www.valdezak.gov/Facilities/Facility/Details/Dock-Point-Trail-23
- Visit Valdez — Nature Walks:
  https://www.visitvaldez.com/things-to-do/nature-walks
- Visit Valdez — Geography:
  https://www.visitvaldez.com/about-valdez/geography-of-valdez

Verified:
- The City of Valdez explicitly identifies Dock Point's east/west overlooks for harbor and Port of Valdez views.
- The city page explicitly mentions photographic opportunities.
- The broader destination is a fjord setting where steep coastal mountains meet the water.

Opportunity:
- P01 Dock Point + Port Valdez harbor + Chugach coastal mountains.

Runtime:
- minimum-sufficient visibility.
- B73 moves the broad Valdez city weather anchor to the actual Dock Point Camera Zone.
- Boats, birds, snow and reflections remain transient boosters.

## us-050 — Juneau

Official sources:
- Travel Juneau — Downtown Street Tour:
  https://www.traveljuneau.com/things-to-do/top-attractions/downtown-street-tour/
- Travel Juneau — Goldbelt Tram:
  https://www.traveljuneau.com/listing/goldbelt-tram/45489/
- Goldbelt Tram — current operations:
  https://www.goldbelttram.com/

Verified:
- Travel Juneau identifies Marine Park / downtown docks as public waterfront sightseeing space and points visitors to Mt. Juneau views.
- Travel Juneau identifies the upper Goldbelt Tram area as a premier photo spot for Juneau, Stephens Passage and the Chilkat Mountains.
- The tram operator currently reports a temporary closure and states operating hours are weather-sensitive.

Opportunities:
- P01 Juneau waterfront + Gastineau Channel + Mt. Juneau / surrounding mountains.
- P02 Goldbelt Tram upper panorama over Juneau / Stephens Passage / Chilkat Mountains.

Runtime:
- P01 = minimum-sufficient visibility.
- P02 = dynamic_access + visibility and remains `module_pending`.
- Static seasonal opening information must never override a current operator closure.
- The lower-terminal location is not presented as the upper Camera Zone.

## Catalog delta

B73 adds:
- 5 curated US Places
- 8 Opportunities
- 8 Condition Variants
- 8 viewpoint relations

Expected canonical totals:
- 168 curated Places
- 348 Opportunities
- 363 Condition Variants
- 354 viewpoint relations

US migrated after B73:
- us-001 through us-050
- 50 Places / 78 Opportunities / 78 variants / 78 viewpoint relations

US research-pending:
- us-051 through us-070
- 20 Places

## Runtime-policy delta

Relative to B72:

`minimum_sufficient_available` +3:
- us-048-P01 Portage Valley
- us-049-P01 Valdez Dock Point
- us-050-P01 Juneau waterfront

`module_pending` +5:
- us-046-P01 Hatcher Summit Lake access + visibility
- us-046-P02 Hatcher aurora + access
- us-047-P01 Matanuska public site access + visibility
- us-048-P02 Portage Glacier cruise timetable + access
- us-050-P02 Goldbelt Tram access + visibility

Expected policy totals:
- module_pending: 109
- preview_module_available: 113
- minimum_sufficient_available: 120
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

Minimum-sufficient visibility profile count:
- 82

## QA

B73 updates:
- Adapter researched-US guards through us-050.
- Adapter dependency/policy assertions for all eight new Opportunities.
- US Candidate Weather researched range through us-050 and pending count to 20.
- Browser Smoke researched-US count to 50 and pending count to 20.
- Hatcher Pass, Matanuska Glacier, Valdez and Juneau weather/Camera Zone anchors.
- Verified summer Summit Lake and public Matanuska navigation targets.
- Access classifications for Hatcher road state, Matanuska site closure, Portage cruise operation and Goldbelt Tram current operation.

Existing canonical us-001 through us-045 and all TW/JP curated Places must remain semantically unchanged.
