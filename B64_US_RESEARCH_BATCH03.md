# ChaseLights R4.2 B64 — US Research Batch 03 (us-011 through us-015)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates the next five United States production Places into the canonical Opportunity catalog:

- us-011 Grand Teton National Park
- us-012 Mount Rainier National Park
- us-013 Crater Lake National Park
- us-014 Death Valley National Park
- us-015 Golden Gate Bridge

Canonical production data remains in `runtime_catalog_v004_r4_2.json`. This document records evidence and modeling decisions only.

## Evidence boundary

- NPS / official bridge authority pages prove the subject, viewpoint and access facts.
- Weather / astronomy modules estimate when an admitted subject may work.
- A scenic Place does not become a reflection, sunrise, sunset or astro Opportunity merely because legacy tags suggest it.
- Seasonal road access is not inferred from month alone.
- A calm-water forecast estimates reflection quality; it does not guarantee a perfect mirror.
- Golden Gate fog is treated as a visibility/quality modifier in this batch, not as a standalone fog Opportunity, because ChaseLights does not yet model bridge-scale spatial fog geometry reliably.

## us-011 — Grand Teton National Park

Official sources:
- NPS Oxbow Bend:
  https://home.nps.gov/thingstodo/oxbowbend.htm
- NPS Moran and the East:
  https://www.nps.gov/grte/planyourvisit/moranplan.htm
- NPS Snake River Overlook:
  https://www.nps.gov/places/000/snake-river-overlook.htm

Verified:
- Oxbow Bend is an official paved turnout / overlook.
- NPS explicitly states Mount Moran can reflect on calm water.
- NPS explicitly identifies sunrise and sunset as photographer-favored times.
- Snake River Overlook directly supports the iconic Teton Range + Snake River panorama and explicitly notes that the exact historic Ansel Adams tripod location is unknown.

Opportunities:
- P01 Oxbow Bend sunrise + Mount Moran reflection.
- P02 Snake River Overlook classic panorama.

Runtime:
- P01: directional_horizon + water_surface_state + visibility, configured.
- P02: minimum-sufficient visibility.
- No exact Ansel Adams re-creation geometry is claimed.

## us-012 — Mount Rainier National Park

Official sources:
- NPS Reflection Lakes:
  https://www.nps.gov/places/reflection-lakes.htm
- NPS Reflection Lakes exhibit:
  https://www.nps.gov/places/reflection-lakes-exhibit-panel.htm
- NPS Tipsoo Lake:
  https://www.nps.gov/places/tipsoo-lake.htm
- NPS Explore Tipsoo Lake:
  https://www.nps.gov/thingstodo/explore-tipsoo-lake.htm
- NPS park brochure:
  https://home.nps.gov/mora/planyourvisit/park-brochure.htm

Verified:
- Reflection Lakes is an official Scenic View/Photo Spot named for Mount Rainier reflections.
- Early calm conditions are directly supported as favorable to a mirror reflection.
- Tipsoo Lake is an official Scenic View/Photo Spot.
- The NPS brochure directly depicts / describes warm sunrise light and a mirror image of Rainier at Tipsoo.
- Reflection Lakes / Stevens Canyon Road and Tipsoo / SR410 have strong seasonal road-access constraints.

Opportunities:
- P01 Reflection Lakes morning Rainier reflection.
- P02 Tipsoo Lake sunrise + Rainier reflection.

Runtime:
- both require water_surface_state + visibility + dynamic_access.
- P02 additionally requires directional_horizon.
- current authoritative road/viewpoint provider is not connected, so both remain module_pending.
- access does not become “open” from month alone.

## us-013 — Crater Lake National Park

Official sources:
- NPS overlooks:
  https://www.nps.gov/crla/planyourvisit/overlooks.htm
- NPS hiking:
  https://www.nps.gov/crla/planyourvisit/hiking.htm
- NPS operating hours:
  https://www.nps.gov/crla/planyourvisit/hours.htm
- NPS current conditions:
  https://www.nps.gov/crla/planyourvisit/conditions.htm

Verified:
- Rim Village / Rim Drive provide official lake and caldera viewpoints.
- Watchman Peak provides 360-degree lake and surrounding-landscape views.
- NPS specifically notes Watchman Peak is especially popular at sunset.
- The park is open year-round, but many roads and trails are seasonal due to snow.

Opportunities:
- P01 Rim Village Crater Lake panorama.
- P02 Watchman Peak sunset panorama.

Runtime:
- P01: minimum-sufficient visibility.
- P02: directional_horizon + visibility + dynamic_access.
- P02 remains module_pending until current Watchman / West Rim access is backed by an authoritative runtime provider.

## us-014 — Death Valley National Park

Official sources:
- NPS Zabriskie Point:
  https://www.nps.gov/places/zabriskie-point-scenic-viewpoint.htm
- NPS Mesquite Flat Sand Dunes:
  https://www.nps.gov/places/mesquite-flat-sand-dunes.htm
- NPS night sky:
  https://www.nps.gov/deva/learn/nature/lightscape.htm
- NPS Night Exploration:
  https://home.nps.gov/deva/night-exploration.htm

Verified:
- Zabriskie Point is an iconic, heavily photographed Scenic View/Photo Spot.
- NPS explicitly identifies it as a favorite for both sunrise and sunset.
- Mesquite Flat Sand Dunes are directly documented for dramatic sunrise/sunset shadows and dark-night-sky viewing.
- Death Valley is an International Dark Sky Park and NPS explicitly supports night photography.

Opportunities:
- P01 Zabriskie sunrise badlands / Manly Beacon.
- P02 Zabriskie sunset badlands / Panamint layers.
- P03 Mesquite Flat Sand Dunes dark sky / Milky Way foreground.

Runtime:
- P01/P02: directional_horizon + visibility.
- P03: astronomy_ephemeris.
- P03 does not claim exact Galactic Core alignment with a particular dune.
- Extreme heat remains a safety caveat separate from photographic quality.

## us-015 — Golden Gate Bridge

Official sources:
- NPS Golden Gate Overlook:
  https://www.nps.gov/places/000/golden-gate-overlook.htm
- NPS Battery Spencer Overlook:
  https://www.nps.gov/places/000/battery-spencer-overlook.htm
- NPS Marin Headlands Scenic Vistas:
  https://home.nps.gov/goga/planyourvisit/marin-headlands-scenic-vistas.htm
- Golden Gate Bridge Highway & Transportation District photography locations:
  https://www.goldengate.org/district/permits/filming-photography-permits/

Verified:
- Golden Gate Overlook is explicitly classified by NPS as a Scenic View/Photo Spot with sunset views of the bridge.
- Battery Spencer is an official Scenic View/Photo Spot and one of the most popular bridge overlooks.
- Official bridge / park sources document multiple legitimate public viewpoints.
- Commercial filming/photography permit rules are not treated as a blanket personal-travel-photography permit requirement.

Opportunities:
- P01 Golden Gate Overlook bridge sunset.
- P02 Battery Spencer bridge + bay / San Francisco panorama.

Runtime:
- P01: directional_horizon + visibility.
- P02: minimum-sufficient visibility.
- Low fog can improve atmosphere only while the bridge remains readable.
- Dense fog that hides the bridge is a penalty.
- No standalone “fog sea” or bridge-scale fog Opportunity is admitted in this batch because no spatial fog runtime contract is yet certified.

## Catalog delta

B64 adds:
- 5 curated US Places
- 11 Opportunities
- 11 Condition Variants
- 11 viewpoint relations

Expected canonical totals:
- 133 curated Places
- 297 Opportunities
- 312 Condition Variants
- 303 viewpoint relations

US migrated after B64:
- us-001 through us-015
- 15 Places / 27 Opportunities / 27 variants / 27 viewpoint relations

US research-pending:
- us-016 through us-070

## Runtime-policy delta

Relative to B63:
- module_pending: +3
  - Rainier Reflection Lakes
  - Rainier Tipsoo sunrise reflection
  - Crater Lake Watchman sunset access
- preview_module_available: +5
  - Grand Teton Oxbow sunrise reflection
  - Death Valley sunrise
  - Death Valley sunset
  - Death Valley astro
  - Golden Gate sunset
- minimum_sufficient_available: +3
  - Snake River Overlook
  - Crater Lake Rim Village panorama
  - Battery Spencer panorama

Expected policy totals:
- module_pending: 88
- preview_module_available: 102
- minimum_sufficient_available: 101
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

## QA

B64 updates:
- Adapter / integration coverage through us-015.
- Evidence registry for Oxbow, Rainier reflection and Death Valley astro.
- US Candidate Weather researched range to us-001 through us-015.
- Browser Smoke researched US card count to 15.
- Dynamic access classification for Rainier and Watchman seasonal road/viewpoint access.
