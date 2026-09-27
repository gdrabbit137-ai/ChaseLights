# ChaseLights R4.2 B75 — Alaska Research Batch 12 (us-056 through us-060)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates the next five Alaska production Places into the canonical Opportunity catalog:

- us-056 Brooks Range / Atigun Pass
- us-057 Arctic Circle Wayside
- us-058 Nome
- us-059 Katmai National Park / Brooks Falls
- us-060 Glacier Bay National Park / Bartlett Cove

Canonical production data remains in `runtime_catalog_v004_r4_2.json`.

## Modeling rules preserved

- Camera Zone, weather sample, and Navigation Target remain separate.
- Aurora requires location-aware `aurora_state`; planetary Kp alone is not accepted as proof.
- Remote-road safety / closure state is independent of favorable weather.
- Wildlife presence is not inferred from month or legacy tags.
- Managed boat/tour availability requires current timetable/access state.
- Snow, sea ice, wildlife, salmon, reflections and ships remain boosters unless independently gated.

## us-056 — Brooks Range / Atigun Pass

Official sources:
- BLM Atigun Pass:
  https://www.blm.gov/visit/atigun-pass
- BLM Dalton Highway FAQ:
  https://www.blm.gov/learn/interpretive-centers/arctic-interagency-visitor-center/frequently-asked-questions
- Travel Alaska Brooks Range:
  https://www.travelalaska.com/destinations/regions/arctic/brooks-range

Verified:
- Atigun Pass is the road-accessible Dalton Highway crossing of the Brooks Range.
- BLM documents the remote alpine setting and warns visitors to check current road conditions.
- BLM documents the Dalton corridor as a northern-lights viewing area during the dark season.

Opportunities:
- P01 Atigun Pass Brooks Range alpine panorama.
- P02 Brooks Range / Atigun Pass aurora.

Runtime:
- P01 = visibility + dynamic_access.
- P02 = aurora_state + dynamic_access.
- Both remain module-pending until current road state is connected.
- No unsafe roadside tripod position or exact Directions target is invented.

## us-057 — Arctic Circle Wayside

Official sources:
- BLM Dalton Highway / Arctic Circle Wayside listing:
  https://www.blm.gov/visit/search?field_activities=All&field_location=100041&search_api_fulltext=
- Travel Alaska Dalton Highway tips:
  https://www.travelalaska.com/explore-alaska/articles/insiders-tips-exploring-dalton-highway-alaskas-arctic
- BLM Dalton Highway FAQ:
  https://www.blm.gov/learn/interpretive-centers/arctic-interagency-visitor-center/frequently-asked-questions

Verified:
- Travel Alaska identifies the official Arctic Circle sign as a photo-op.
- BLM explicitly states northern lights can be viewed from Arctic Circle Wayside in winter.
- Winter driving can be difficult and current road conditions must be checked.

Opportunities:
- P01 Arctic Circle sign landmark photograph.
- P02 Arctic Circle sign / wayside + aurora.

Runtime:
- P01 = dynamic_access.
- P02 = aurora_state + dynamic_access.
- The existing sign coordinate is retained as a cross-mapped wayside anchor.
- Road safety cannot be overridden by a favorable weather or aurora forecast.

## us-058 — Nome

Official sources:
- Travel Alaska Nome:
  https://www.travelalaska.com/destinations/cities-towns/nome
- Travel Alaska beaches:
  https://www.travelalaska.com/explore-alaska/articles/beaches-alaska
- Travel Alaska 7 Things to Do in Nome:
  https://www.travelalaska.com/explore-alaska/articles/7-things-do-nome

Verified:
- Middle Beach is directly behind Historic Front Street and is an accessible Bering Sea coastal subject.
- Nome is an official state-tourism northern-lights destination with prime viewing areas close to town.

Opportunities:
- P01 Middle Beach / Front Street Bering Sea coastal-town scene.
- P02 Nome-area aurora.

Runtime:
- P01 uses the minimum-sufficient local-scene contract.
- P02 requires aurora_state and remains module-pending.
- No precise aurora tripod location is invented because the official source supports an area, not one fixed site.
- Sea-ice access is never implied.

## us-059 — Katmai / Brooks Falls

Official sources:
- NPS Brooks Falls Platform:
  https://www.nps.gov/places/brooks-falls-platform.htm
- NPS Watch Bears at Brooks Camp:
  https://www.nps.gov/thingstodo/watch-bears-at-brooks-camp.htm
- NPS Bear Safety:
  https://www.nps.gov/katm/planyourvisit/bear-safety-brooks-camp.htm

Verified:
- NPS classifies Brooks Falls Platform as a Scenic View / Photo Spot.
- Platform capacity, seasonal nighttime closures, ranger controls and tripod restrictions are documented.
- Brown-bear concentrations vary strongly by date; July and September are often productive but month does not guarantee a bear subject.

Opportunities:
- P01 Brooks Falls / Brooks River natural scene.
- P02 brown bears fishing / interacting at Brooks Falls.

Runtime:
- P01 = dynamic_access.
- P02 = wildlife_state + dynamic_access.
- B75 adds the explicit canonical formula dependency `needs_wildlife_state_access_module`.
- `wildlife_state` remains unimplemented, so bear photography is fail-closed rather than calendar-derived.
- Weather sampling moves from the broad legacy Katmai coordinate to the actual Brooks Falls platform area.

## us-060 — Glacier Bay / Bartlett Cove

Official sources:
- NPS Bartlett Cove Public Use Dock:
  https://www.nps.gov/places/bartlett-cove-public-use-dock.htm
- NPS Tour Glacier Bay:
  https://www.nps.gov/glba/planyourvisit/tour.htm
- NPS Bartlett Cove:
  https://www.nps.gov/places/bartlett-cove.htm

Verified:
- NPS classifies Bartlett Cove Public Use Dock as a Scenic View / Photo Spot and publishes an exact coordinate.
- Clear-day views include Beartrack Mountains, Excursion Ridge, Mount Bertha, Mount Crillon and Mount Fairweather.
- During the summer visitor season, a day tour boat departs Bartlett Cove for tidewater glaciers.

Opportunities:
- P01 Bartlett Cove dock / bay + mountain panorama.
- P02 Glacier Bay Day Tour tidewater-glacier scene.

Runtime:
- P01 uses minimum-sufficient visibility.
- P02 uses timetable + dynamic_access and remains module-pending.
- The exact public-dock coordinate is the frontcountry weather/embarkation anchor, not a fake fixed tidewater-glacier coordinate.
- Wildlife and calving remain opportunistic boosters.

## Catalog delta

B75 adds:
- 5 curated US Places
- 10 Opportunities
- 10 Condition Variants
- 10 viewpoint relations

Expected canonical totals:
- 178 curated Places
- 366 Opportunities
- 381 Condition Variants
- 372 viewpoint relations

US migrated:
- us-001 through us-060
- 60 Places / 96 Opportunities / 96 variants / 96 viewpoint relations

US research-pending:
- us-061 through us-070
- 10 Places

## Runtime-policy delta

Relative to B74:

`minimum_sufficient_available` +2:
- us-058-P01 Nome Middle Beach / Front Street
- us-060-P01 Bartlett Cove panorama

`module_pending` +8:
- us-056-P01 Atigun Pass access + visibility
- us-056-P02 Atigun aurora + access
- us-057-P01 Arctic Circle sign + road access
- us-057-P02 Arctic Circle aurora + road access
- us-058-P02 Nome aurora
- us-059-P01 Brooks Falls platform access
- us-059-P02 Brooks Falls wildlife state + access
- us-060-P02 Glacier Bay Day Tour timetable + access

Expected policy totals:
- module_pending: 119
- preview_module_available: 113
- minimum_sufficient_available: 128
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

Minimum-sufficient visibility profile count:
- 86

## QA

B75 updates:
- Adapter researched-US guards through us-060.
- Runtime policy / dependency assertions for all 10 new Opportunities.
- Adds and validates `needs_wildlife_state_access_module`.
- US Candidate Weather researched range through us-060; pending count becomes 10.
- Browser Smoke researched-US count becomes 60; pending count becomes 10.
- Camera/weather anchors move to Atigun Pass, Arctic Circle Wayside, Nome coastal area, Brooks Falls, and Bartlett Cove Public Use Dock.
- Access classifications cover Atigun/Arctic Circle road state, Brooks Falls current access, and Glacier Bay day-tour transport state.

Existing canonical us-001 through us-055 and all TW/JP curated Places must remain semantically unchanged.
