# ChaseLights R4.2 B66 — US Research Batch 05 (us-021 through us-025)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates the next five United States production Places into the canonical Opportunity catalog:

- us-021 Canyonlands National Park · Mesa Arch
- us-022 Joshua Tree National Park · Cholla Cactus Garden
- us-023 Saguaro National Park · Cactus Forest Loop sunset pull-off
- us-024 Seattle Space Needle
- us-025 Santa Monica Pier

Canonical production data remains in `runtime_catalog_v004_r4_2.json`. This document records evidence and modeling decisions only.

## B64 Camera Zone / weather-sample boundary

This batch explicitly preserves the B64 contract:

- Place-specific official evidence proves the subject exists.
- Weather/astronomy modules estimate when an admitted subject may work.
- A broad park-center coordinate must not silently act as a hard local weather sample for a distant Camera Zone.
- Camera Zone, weather sample, and Navigation Target remain separate concepts.

B66 therefore corrects two broad legacy Place coordinates:
- us-022 is moved to the official Cholla Cactus Garden photographed area.
- us-023 is moved to the exact NPS Cactus Forest Loop sunset pull-off.

## us-021 — Canyonlands / Mesa Arch

Official source:
- NPS Mesa Arch Trail:
  https://www.nps.gov/places/mesa-arch.htm

Verified:
- Mesa Arch is a Scenic View/Photo Spot.
- NPS explicitly calls it a classic sunrise location and one of the most photographed arches in southeast Utah.
- The arch frames the canyon and distant La Sal Mountains.

Opportunity:
- P01 Mesa Arch sunrise + canyon/La Sal Mountains frame.

Runtime:
- directional_horizon + visibility.
- Existing Mesa Arch coordinate is close to the real Camera Zone and remains the weather/map anchor.
- No unique tripod location is claimed.
- NPS prohibition on climbing/walking/standing on arches remains part of the shooting boundary.

## us-022 — Joshua Tree / Cholla Cactus Garden

Official sources:
- NPS Cholla Cactus Garden:
  https://www.nps.gov/places/cholla-cactus-garden.htm
- NPS Gallery Cholla Cactus Garden sunset asset/location:
  https://npgallery.nps.gov/AssetDetail/3c46fb32-9bf1-4b99-97e7-d343f0241359

Verified:
- Cholla Cactus Garden is a Scenic View/Photo Spot.
- NPS explicitly recommends both sunrise and sunset.
- The Garden contains a dense teddy-bear cholla foreground with Pinto Basin / mountain context.
- Official NPS image metadata provides a photographed coordinate near 33.82705, -115.86010.

Opportunities:
- P01 Cholla Garden sunrise.
- P02 Cholla Garden sunset.

Runtime:
- both use directional_horizon + visibility.
- B66 replaces the former broad park-center coordinate with the Garden coordinate so local forecast data corresponds to the actual Camera Zone.
- Spring blooms are not promoted into a separate seasonal Opportunity in this batch; month alone would not prove bloom state.

## us-023 — Saguaro / Cactus Forest Loop

Official sources:
- NPS exact sunset pull-off:
  https://www.nps.gov/places/pull-off-along-cactus-forest-loop-drive.htm
- NPS Outdoor Activities / Sunsets:
  https://www.nps.gov/sagu/planyourvisit/outdooractivities.htm

Verified:
- NPS provides an exact Scenic View/Photo Spot at 32.183867, -110.710873.
- The pull-off is explicitly used for spectacular sunset viewing.
- The East District Cactus Forest Loop is a preferred sunset area.
- Road/gate timing matters for leaving after sunset.

Opportunity:
- P01 saguaro forest + west-facing sunset.

Runtime:
- directional_horizon + visibility.
- B66 replaces the old Tucson-area center coordinate with the exact NPS Camera Zone/weather sample.
- Road closing time remains an operational/safety boundary; favorable weather does not override a closed road.

## us-024 — Seattle Space Needle

Official sources:
- Space Needle About:
  https://www.spaceneedle.com/about
- Space Needle Plan Your Visit:
  https://www.spaceneedle.com/plan-your-visit

Verified:
- The 605-foot Space Needle is an internationally photographed Seattle landmark.
- The top house provides 360-degree indoor/outdoor views of downtown, Mount Rainier, Puget Sound, the Cascades and Olympics.
- Observation access is ticketed.
- Official operating hours vary by day/date and can include level-specific early closures.

Opportunities:
- P01 Space Needle exterior landmark from Seattle Center public context.
- P02 ticketed observation-deck 360-degree panorama.

Runtime:
- P01 uses minimum-sufficient local-scene scoring.
- P02 uses visibility + dynamic_access and remains module_pending.
- Exterior photography must not inherit ticketed tower-access restrictions.
- Tower admission must not be inferred from favorable weather or a stale static schedule.

## us-025 — Santa Monica Pier

Official sources:
- Visit Santa Monica — Santa Monica Pier at Sunset:
  https://www.santamonica.com/romantic-views-in-santa-monica/
- Pacific Park — Pacific Wheel:
  https://pacpark.com/santa-monica-amusement-park/ferris-wheel/
- Pacific Park — Live Cams:
  https://pacpark.com/santa-monica-pier-live-cams/

Verified:
- Official destination guidance directly identifies Santa Monica Pier at sunset with the sun setting over the Pacific.
- Pacific Park documents the Pacific Wheel and 174,000 LED lights.
- Pacific Park states the wheel illuminates the LA coastline nightly.
- Special holiday/event light designs are date-specific and must not be projected into another year.

Opportunities:
- P01 Pacific sunset + Pier / Pacific Wheel foreground.
- P02 Pacific Wheel nightly LED subject.

Runtime:
- P01 uses directional_horizon + visibility.
- P02 requires managed_lighting_state and remains module_pending.
- Special-event colors are not part of the generic P02 contract.
- A nightly baseline lighting subject is evidence-verified, but maintenance/event state is not assumed live.

## Catalog delta

B66 adds:
- 5 curated US Places
- 8 Opportunities
- 8 Condition Variants
- 8 viewpoint relations

Expected canonical totals:
- 143 curated Places
- 314 Opportunities
- 329 Condition Variants
- 320 viewpoint relations

US migrated after B66:
- us-001 through us-025
- 25 Places / 44 Opportunities / 44 variants / 44 viewpoint relations

US research-pending:
- us-026 through us-070

## Runtime-policy delta

Relative to B65:

preview_module_available +5:
- us-021-P01 Mesa Arch sunrise
- us-022-P01 Cholla Garden sunrise
- us-022-P02 Cholla Garden sunset
- us-023-P01 Cactus Forest Loop sunset
- us-025-P01 Santa Monica Pier sunset

minimum_sufficient_available +1:
- us-024-P01 Space Needle exterior

module_pending +2:
- us-024-P02 Space Needle observation-deck access
- us-025-P02 Pacific Wheel managed lighting state

Expected policy totals:
- module_pending: 93
- preview_module_available: 110
- minimum_sufficient_available: 105
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

## QA

B66 updates:
- Adapter coverage through us-025.
- US Candidate Weather researched range through us-025.
- Browser Smoke researched-US count to 25.
- Space Needle observation access classification as facility-hours notice.
- Joshua Tree and Saguaro exact Camera Zone/weather-sample corrections.

Existing canonical us-001 through us-020 and all TW/JP curated Places must remain semantically unchanged.
