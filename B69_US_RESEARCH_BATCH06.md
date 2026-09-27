# ChaseLights R4.2 B69 — US Research Batch 06 (us-026 through us-030)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates the next five United States production Places into the canonical Opportunity catalog:

- us-026 Seattle Pike Place Market
- us-027 Sawtooth Mountains — narrowed to Redfish Lake North Shore
- us-028 Griffith Observatory, Los Angeles
- us-029 White Sands National Park — Sunset Stroll / Dunes Drive dune area
- us-030 Chicago Skyline — Adler Planetarium / Solidarity Drive lakefront

Canonical production data remains in `runtime_catalog_v004_r4_2.json`. This document records evidence and modeling decisions only.

## B64 Camera Zone / weather-sample boundary

This batch preserves the production boundary introduced in B64:

- Place-specific evidence proves the photographic subject.
- Weather/runtime data estimates when that admitted subject may work.
- Camera Zone, weather sample, and Navigation Target are separate concepts.
- Broad regional coordinates must not silently become hard local weather samples for distant subjects.

B69 therefore changes the weather/map anchor for:
- us-027 from a broad Sawtooth-region coordinate to Redfish Lake North Shore,
- us-029 from White Sands Visitor Center to the official Sunset Stroll / Dunes Drive dune area,
- us-030 from a broad downtown Chicago coordinate to the Adler / Solidarity Drive skyline Camera Zone.

The existing us-028 Griffith Observatory override is already near the actual Observatory and remains unchanged.

## us-026 — Pike Place Market

Official sources:
- Pike Place Market Visitor FAQ:
  https://www.pikeplacemarket.org/about-pike-place-market/market-visitor-faq/
- Pike Place Market official photo-op guidance:
  https://www.pikeplacemarket.org/cute-couple-photo-ops-in-pike-place-market-just-in-time-for-valentines-day/
- Pike Place Market MarketFront:
  https://www.pikeplacemarket.org/get-to-know-the-pike-place-marketfront/

Verified:
- Personal photography is welcomed.
- Personal-use tripods are not allowed within the nine-acre historic district.
- Drones are prohibited.
- Commercial / non-personal filming and photography require PDA authorization.
- The Public Market Center Clock & Sign is explicitly identified as an iconic photo subject.
- MarketFront is a public waterfront viewing area with Puget Sound / distant mountain views.

Opportunities:
- P01 Public Market Center Clock & Sign + historic Market streetscape.
- P02 MarketFront Puget Sound / distant Olympic Mountains view.

Runtime:
- P01 uses the explicit minimum-sufficient local-scene contract.
- P02 uses minimum-sufficient visibility.
- No event or seasonal decoration is inferred from month.
- The compact Market district allows the existing Market weather anchor to represent both Camera Zones without a material spatial-weather mismatch.

## us-027 — Sawtooth Mountains / Redfish Lake North Shore

Official sources:
- USDA Forest Service Sawtooth National Forest Visitor Guide:
  https://www.fs.usda.gov/Internet/FSE_DOCUMENTS/fseprd929006.pdf
- Recreation.gov / Sawtooth National Forest North Shore Picnic Area:
  https://www.recreation.gov/camping/campgrounds/232076

Verified:
- Forest Service material describes Redfish Lake as the heart of the Sawtooth NRA.
- Its waters are officially documented reflecting Mt. Heyburn and Grand Mogul.
- The Forest Service explicitly describes Sawtooth terrain as appealing to photographers.
- North Shore provides public waterfront day-use access at the foot of the Sawtooth Range.
- North Shore opening and closing dates are weather permitting.

Opportunity:
- P01 Redfish Lake + Mt. Heyburn / Grand Mogul Sawtooth skyline.

Runtime:
- visibility + dynamic_access.
- Reflection is an evidence-backed booster, not a hard `water_surface_state` requirement.
- North Shore is fail-closed until ChaseLights has an authoritative current access provider.
- Calendar month or favorable weather must not imply the day-use site is open.
- The broad legacy Sawtooth coordinate is replaced by the North Shore Camera Zone/weather anchor.

## us-028 — Griffith Observatory

Official sources:
- City of Los Angeles — Griffith Observatory Visit:
  https://griffithobservatory.lacity.gov/visit/
- City of Los Angeles — Griffith Observatory Roof & Terraces:
  https://griffithobservatory.lacity.gov/exhibits/exterior-exhibits/roof-terraces/

Verified:
- Official Observatory guidance directly supports spectacular Los Angeles and Hollywood Sign views.
- Exterior terraces provide panoramic views in multiple directions.
- Terraces are generally available daily from sunrise until 22:00; roof access follows building hours.
- The existing Griffith Observatory coordinate is already near the actual facility and does not need a B69 coordinate correction.

Opportunity:
- P01 Griffith Observatory exterior terraces + Los Angeles / Hollywood Sign panorama.

Runtime:
- minimum-sufficient visibility.
- The background panorama is part of the promised subject, so B69 requires visibility rather than treating this as a close-range local-scene-only Opportunity.
- No separate sunset Opportunity is created in this batch.
- Temporary closures remain operational constraints and are not overridden by weather.
- Existing high-confidence Griffith Observatory coordinate is retained.

## us-029 — White Sands National Park

Official sources:
- NPS White Sands Photography:
  https://home.nps.gov/whsa/planyourvisit/photography.htm
- NPS 2026 Sunset Stroll:
  https://www.nps.gov/planyourvisit/event-details.htm?id=AC221D58-E77A-3272-6B18E7C27671C1FD
- NPS White Sands operating hours:
  https://www.nps.gov/whsa/planyourvisit/hours.htm

Verified:
- NPS explicitly promotes White Sands as a photography destination.
- NPS identifies the golden hours before sunset, surrounding mountain views, and mountain afterglow as valid photographic subjects.
- The current 2026 Sunset Stroll page explicitly describes panoramic sunset photographic opportunities.
- NPS publishes the current Sunset Stroll parking-area coordinate as 32.811370, -106.265010.
- Current park closing time is tied to local sunset, with seasonal exceptions.
- Temporary closures, including missile-range activity, remain possible and must not be inferred away from favorable weather.

Opportunity:
- P01 gypsum dunes + surrounding mountains during sunset / immediate afterglow.

Runtime:
- visibility + dynamic_access.
- B69 does not invent a precise sun-to-foreground alignment.
- The Place weather/map anchor moves from the visitor center to the exact current NPS Sunset Stroll area.
- The same exact NPS parking coordinate is a verified Navigation Target for this batch.
- NPS documents temporary Dunes Drive closures for missile testing and other safety conditions, so this Opportunity is fail-closed until an authoritative current-access provider is connected.
- Favorable weather, calendar month, or a static hours table must never imply the dune Camera Zone is open.

## us-030 — Chicago Skyline / Adler lakefront

Official sources:
- Choose Chicago — best Chicago skyline photo spots:
  https://www.choosechicago.com/blog/tours-attractions/7-photo-spots-for-the-best-chicago-skyline-views/
- Choose Chicago — Chicago photo locations:
  https://www.choosechicago.com/articles/itineraries/chicagos-best-spots-for-selfies/
- Adler Planetarium official address:
  https://www.adlerplanetarium.org/

Verified:
- Chicago's official destination organization directly identifies the area in front of Adler Planetarium as a skyline photography location.
- The Solidarity Drive stretch between Shedd Aquarium and Adler provides Lake Michigan + Chicago skyline views.
- The subject is an exterior public-lakefront view; museum interior hours are not used as the sole gate for the exterior Camera Zone.

Opportunity:
- P01 Adler / Solidarity Drive lakefront + Chicago skyline.

Runtime:
- minimum-sufficient visibility.
- Blue hour / city lights may improve the scene but are not a managed-lighting hard gate.
- The broad downtown coordinate is replaced by the actual Adler / Solidarity Drive camera/weather area.

## Catalog delta

B69 adds:
- 5 curated US Places
- 6 Opportunities
- 6 Condition Variants
- 6 viewpoint relations

Expected canonical totals:
- 148 curated Places
- 320 Opportunities
- 335 Condition Variants
- 326 viewpoint relations

US migrated after B69:
- us-001 through us-030
- 30 Places / 50 Opportunities / 50 variants / 50 viewpoint relations

US research-pending:
- us-031 through us-070

## Runtime-policy delta

Relative to B66:

minimum_sufficient_available +4:
- us-026-P01 Pike Place Clock & Sign
- us-026-P02 MarketFront distant view
- us-028-P01 Griffith Observatory exterior
- us-030-P01 Chicago skyline

module_pending +2:
- us-027-P01 Redfish Lake North Shore access + visibility
- us-029-P01 White Sands current park / Dunes Drive access + visibility

Expected policy totals:
- module_pending: 95
- preview_module_available: 110
- minimum_sufficient_available: 109
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

Minimum-sufficient visibility profile count:
- 75

## QA

B69 updates:
- Adapter coverage through us-030.
- US Candidate Weather researched range through us-030.
- Browser Smoke researched-US count from 25 to 30.
- Redfish North Shore and White Sands dynamic-access classifications.
- Redfish Lake, White Sands and Chicago Camera Zone/weather anchors, including the exact current NPS White Sands Sunset Stroll navigation target.
- Regression assertions that Griffith keeps the already-correct Observatory anchor.

Existing canonical us-001 through us-025 and all TW/JP curated Places must remain semantically unchanged.
