# ChaseLights R4.2 B69 — US Research Batch 06 (us-026 through us-030)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates the next five United States production Places into the canonical Opportunity catalog:

- us-026 Seattle Pike Place Market
- us-027 Sawtooth Mountains — narrowed to Redfish Lake North Shore
- us-028 Griffith Observatory, Los Angeles
- us-029 White Sands National Park — Alkali Flat / tallest-dune area
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
- us-029 from White Sands Visitor Center to the Alkali Flat / tallest-dune area,
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

Official source:
- Griffith Observatory official 2026 visitor map:
  https://griffithobservatory.org/wp-content/uploads/2025/12/Griffith-Observatory-Maps_digital.pdf

Verified:
- Official maps document exterior public terraces, including Hollywood Sign / sunset-oriented viewing areas.
- Personal photography is permitted except specified show/telescope contexts.
- Tripods are prohibited inside the building.
- Commercial photography requires the applicable permit process.
- The Observatory is itself a photographable architectural landmark with Los Angeles / Hollywood Sign context.

Opportunity:
- P01 Observatory exterior architecture + Hollywood Sign / Los Angeles background.

Runtime:
- minimum-sufficient local-scene.
- No separate sunset Opportunity is created in this batch because facility/access state is not connected as a dedicated runtime provider.
- Temporary closures remain operational constraints and are not overridden by weather.
- Existing high-confidence Griffith Observatory coordinate is already appropriate and is retained.

## us-029 — White Sands National Park

Official sources:
- NPS White Sands Photography:
  https://www.nps.gov/whsa/planyourvisit/photography.htm
- NPS Alkali Flat Trail:
  https://www.nps.gov/whsa/planyourvisit/alkali-flat-trail.htm
- NPS Alkali Flat Trailhead activity/location:
  https://www.nps.gov/thingstodo/sledding-at-the-alkali-flat-trailhead.htm

Verified:
- NPS explicitly promotes White Sands as a photography destination.
- NPS identifies golden-hour periods and surrounding mountain views.
- Sacramento Mountains can show strong post-sunset afterglow.
- NPS specifically points photographers toward the tallest dunes near Alkali Flat trailhead.
- Alkali Flat is roughly seven miles deeper into the park than the visitor center.
- Blowing sand can sharply reduce local visibility.
- Trail users must comply with official sunset / closing rules.

Opportunity:
- P01 Alkali Flat tallest gypsum dunes + surrounding mountains in golden-hour / afterglow conditions.

Runtime:
- explicit minimum-sufficient visibility.
- The legacy sunset Theme supplies the time-of-day baseline; B69 does not invent a precise sun-to-foreground alignment.
- The weather/map anchor moves from the visitor center to the Alkali Flat trailhead area.
- Temporary closures, missile-test closures and park operations are not inferred from weather.

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

minimum_sufficient_available +5:
- us-026-P01 Pike Place Clock & Sign
- us-026-P02 MarketFront distant view
- us-028-P01 Griffith Observatory exterior
- us-029-P01 White Sands Alkali Flat
- us-030-P01 Chicago skyline

module_pending +1:
- us-027-P01 Redfish Lake North Shore access + visibility

Expected policy totals:
- module_pending: 94
- preview_module_available: 110
- minimum_sufficient_available: 110
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
- Redfish North Shore dynamic-access classification.
- Redfish Lake, White Sands and Chicago Camera Zone/weather anchors.
- Regression assertions that Griffith keeps the already-correct Observatory anchor.

Existing canonical us-001 through us-025 and all TW/JP curated Places must remain semantically unchanged.
