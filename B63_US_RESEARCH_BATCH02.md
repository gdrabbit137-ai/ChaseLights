# ChaseLights R4.2 B63 — US Research Batch 02 (us-006 through us-010)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates the next five United States production Places into the canonical Opportunity catalog:

- us-006 Bryce Canyon National Park
- us-007 Zion National Park
- us-008 Yosemite Half Dome
- us-009 Yosemite Tunnel View
- us-010 Yellowstone Grand Prismatic Spring

Canonical production data remains in `runtime_catalog_v004_r4_2.json`. This file records research and modeling decisions only.

## Evidence boundary

- NPS pages prove the subject/viewpoint/access facts.
- Weather/astronomy modules estimate when a verified subject may work.
- Sunrise/sunset recommendations use directional-horizon timing only where NPS explicitly ties the Place to that daypart.
- Water reflection uses the existing `water_surface_state`; low river level remains a quality caveat because ChaseLights does not have a live Merced River level contract.
- Grand Prismatic is not scored with generic visibility alone because local geothermal steam can obscure the pool even when regional visibility is good.
- Seasonal road/trail access is not inferred from month alone.

## us-006 — Bryce Canyon National Park

Official sources:
- NPS Bryce viewpoints:
  https://www.nps.gov/brca/planyourvisit/viewpoints.htm
- NPS Bryce stargazing:
  https://www.nps.gov/thingstodo/stargazing-at-bryce-canyon.htm
- NPS Bryce operating hours:
  https://www.nps.gov/brca/planyourvisit/hours.htm

Verified:
- Sunrise Point / Bryce Point are official Bryce Amphitheater sunrise locations.
- Sunrise Point is a major Bryce Amphitheater viewpoint.
- Bryce is an International Dark Sky Park.
- NPS explicitly supports Milky Way/star photography and recommends multiple viewpoints for night-sky viewing.
- The park is open 24h year-round, with temporary winter road closures possible.

Opportunities:
- P01 Sunrise Point sunrise + hoodoo layers.
- P02 dark-sky / Milky Way + hoodoo foreground.

Runtime:
- P01: directional_horizon + visibility, configured.
- P02: astronomy_ephemeris, configured.
- Milky Way subject is evidence-registered; runtime does not claim an exact Galactic Core/hoodoo alignment.

## us-007 — Zion National Park

Official sources:
- NPS Zion sunrise/sunset:
  https://www.nps.gov/zion/planyourvisit/sunrise-and-sunset.htm
- NPS Zion operating hours:
  https://www.nps.gov/zion/planyourvisit/hours.htm

Verified:
- Canyon Overlook Trail is explicitly recommended by NPS for sunrise, with sunlight beginning to enter Zion Canyon.
- Pa'rus Trail is explicitly recommended by NPS for sunset golden light on the Watchman.
- NPS warns not to stop in roads or on Canyon Junction Bridge to make the Watchman photograph.
- Zion is open 24h year-round; access modes and parking constraints can vary.

Opportunities:
- P01 Canyon Overlook sunrise light.
- P02 Pa'rus Trail Watchman sunset.

Runtime:
- both use directional_horizon + visibility.
- parking scarcity is documented but not modeled as a guaranteed parking-availability signal.

## us-008 — Yosemite Half Dome

Official source:
- NPS Sentinel Bridge:
  https://www.nps.gov/places/000/sentinel-bridge.htm

Verified:
- Sentinel Bridge is an official Scenic View/Photo Spot.
- NPS directly describes the Half Dome view and its mirrored reflection on the Merced River.
- Sunset is explicitly highlighted.
- NPS states reflection is best when water is low and relatively still, especially fall/winter.
- Sentinel Bridge is reachable by car year-round.

Opportunity:
- P01 Half Dome sunset + Merced River reflection.

Runtime:
- new reusable formula combination:
  `needs_directional_horizon_water_surface_visibility_module`
- components are all existing runtime modules:
  directional_horizon + water_surface_state + visibility.
- low river level is not modeled and remains a documented quality boundary.
- reflection subject is evidence-registered.

## us-009 — Yosemite Tunnel View

Official source:
- NPS Tunnel View:
  https://www.nps.gov/places/000/tunnel-view.htm

Verified:
- NPS calls Tunnel View one of Yosemite's most famous views.
- Subject includes El Capitan, Half Dome, Sentinel Rock, Cathedral Rocks, and Bridalveil Fall.
- NPS says it is particularly spectacular at sunset or after a clearing storm.
- It is reachable by vehicle year-round.

Opportunity:
- P01 Yosemite Valley classic panorama.

Runtime:
- minimum-sufficient visibility.
- sunset / clearing-storm conditions are boosters, not hard invented requirements.
- no generic storm-clearing detector is claimed.

## us-010 — Yellowstone Grand Prismatic Spring

Official sources:
- NPS Yellowstone photography:
  https://www.nps.gov/yell/planyourvisit/photography.htm
- NPS Grand Prismatic Overlook Trail:
  https://www.nps.gov/thingstodo/yell-trail-grand-prismatic-overlook.htm
- NPS Yellowstone operating dates:
  https://www.nps.gov/yell/planyourvisit/operating-dates.htm

Verified:
- NPS explicitly identifies Grand Prismatic as a major photography subject.
- NPS identifies the Fairy Falls Trailhead route as the elevated overlook.
- Off-trail travel is prohibited.
- Parking is limited.
- Interior Yellowstone road/trail access is seasonal and can change quickly.

Opportunity:
- P01 elevated view of the colorful Grand Prismatic pool/bacterial mats.

Runtime:
- new dependency contract:
  `needs_geothermal_steam_visibility_access_module`
- required components:
  geothermal_steam_state + visibility + dynamic_access.
- `geothermal_steam_state` is intentionally unimplemented.
- Grand Prismatic access is classified as a public-attraction/current-notice dependency and is not runtime-ready.
- therefore P01 remains `module_pending`.

This is deliberate: good regional visibility does not prove that local geothermal steam is not obscuring the pool.

## Catalog delta

B63 adds:
- 5 curated US Places
- 7 Opportunities
- 7 Condition Variants
- 7 viewpoint relations

Expected canonical totals:
- 128 Places
- 286 Opportunities
- 301 Condition Variants
- 292 viewpoint relations

US migrated after B63:
- us-001 through us-010
- 10 Places / 16 Opportunities / 16 variants / 16 viewpoint relations

US research-pending:
- us-011 through us-070

## Expected runtime-policy delta

Relative to B61:
- module_pending: +1 (Grand Prismatic)
- preview_module_available: +5
  - Bryce sunrise
  - Bryce astro
  - Zion sunrise
  - Zion sunset
  - Half Dome sunset/reflection
- minimum_sufficient_available: +1 (Tunnel View)

Expected policy totals:
- module_pending: 85
- preview_module_available: 97
- minimum_sufficient_available: 98
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

## QA

B63 updates:
- Adapter/integration coverage for us-006 through us-010.
- US Candidate Weather researched range to us-001 through us-010.
- Browser Smoke researched-card expectations to 10 US Places.
- Evidence registry for Bryce astro and Half Dome reflection.
