# ChaseLights R4.2 B64 — US Research Batch 03 (us-011 through us-015)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates:

- us-011 Grand Teton National Park
- us-012 Mount Rainier National Park
- us-013 Crater Lake National Park
- us-014 Death Valley National Park
- us-015 Golden Gate Bridge

Canonical runtime data remains in `runtime_catalog_v004_r4_2.json`.

## Modeling boundary

- NPS / bridge-authority sources prove the subject and public viewpoint.
- Weather and astronomy estimate when an admitted subject may work.
- Reflection quality uses the existing `water_surface_state` only as a calm-surface proxy.
- Seasonal road access is not inferred from calendar month; Rainier and Watchman access remain fail-closed until a live access provider exists.
- Commercial filming/still-photo permits at Golden Gate Bridge are not treated as a requirement for ordinary personal visitor photography.

## us-011 — Grand Teton National Park

Official sources:
- NPS Oxbow Bend:
  https://home.nps.gov/thingstodo/oxbowbend.htm
- NPS Oxbow Bend Turnout:
  https://www.nps.gov/places/000/oxbow-bend-turnout.htm
- NPS Snake River Overlook:
  https://www.nps.gov/places/000/snake-river-overlook.htm

Verified:
- Oxbow Bend is an iconic pullout where Mount Moran can reflect on calm water.
- NPS explicitly says sunrise and sunset are popular with photographers.
- Snake River Overlook is the iconic Snake River + central Teton Range scene associated with Ansel Adams, while NPS also notes the exact historic camera point is not known today.

Opportunities:
- P01 Oxbow Bend sunrise + Mount Moran reflection.
- P02 Snake River Overlook classic Teton/Snake panorama.

Runtime:
- P01 uses directional_horizon + water_surface_state + visibility.
- P02 uses minimum-sufficient visibility.
- No exact Ansel Adams tripod location is claimed.

## us-012 — Mount Rainier National Park

Official sources:
- NPS Reflection Lakes:
  https://www.nps.gov/places/reflection-lakes.htm
- NPS Reflection Lakes Exhibit Panel:
  https://www.nps.gov/places/reflection-lakes-exhibit-panel.htm
- NPS Tipsoo Lake:
  https://www.nps.gov/places/tipsoo-lake.htm
- NPS Mount Rainier Park Brochure:
  https://home.nps.gov/mora/planyourvisit/park-brochure.htm
- NPS Road Status:
  https://www.nps.gov/mora/planyourvisit/road-status.htm

Verified:
- Reflection Lakes is a Scenic View/Photo Spot named for Mount Rainier reflections.
- NPS states still air and water, usually early morning, can perfectly mirror Mount Rainier.
- Vehicle access via Stevens Canyon Road is seasonal, typically late June through September.
- Tipsoo Lake is a Scenic View/Photo Spot and vehicle access via SR410 is summer-only, typically June–October.
- The official park brochure directly depicts Mount Rainier mirrored in Tipsoo Lake under warm sunrise light.

Opportunities:
- P01 Reflection Lakes early-morning mirror.
- P02 Tipsoo Lake sunrise + Rainier reflection.

Runtime:
- P01 requires water_surface_state + visibility + dynamic_access.
- P02 requires directional_horizon + water_surface_state + dynamic_access + visibility.
- Both remain `module_pending` because ChaseLights does not yet have an authoritative Mount Rainier seasonal road-status adapter.
- Month alone must not make either location appear accessible.

## us-013 — Crater Lake National Park

Official sources:
- NPS Overlooks:
  https://www.nps.gov/crla/planyourvisit/overlooks.htm
- NPS Hiking / Watchman Peak:
  https://www.nps.gov/crla/planyourvisit/hiking.htm
- NPS Current Conditions:
  https://www.nps.gov/crla/planyourvisit/conditions.htm
- NPS Rim Village:
  https://www.nps.gov/crla/planyourvisit/rim-village-walking-tour.htm

Verified:
- Rim Village and Rim Drive are official public lake-view areas.
- NPS says Watchman Peak has 360-degree lake/landscape views and is especially crowded at sunset.
- Rim Drive access is seasonal / weather dependent; current road status is published separately.

Opportunities:
- P01 Rim Village Crater Lake panorama.
- P02 Watchman Peak sunset panorama.

Runtime:
- P01 uses minimum-sufficient visibility.
- P02 requires dynamic_access + directional_horizon + visibility and remains pending until a road/trail-status provider is connected.
- Sunset popularity proves the subject/time pairing but does not prove Watchman is accessible on any given date.

## us-014 — Death Valley National Park

Official sources:
- NPS Zabriskie Point:
  https://www.nps.gov/places/zabriskie-point-scenic-viewpoint.htm
- NPS Mesquite Flat Sand Dunes:
  https://home.nps.gov/places/mesquite-flat-sand-dunes.htm
- NPS Night Exploration:
  https://home.nps.gov/deva/night-exploration.htm

Verified:
- Zabriskie Point is an iconic, heavily photographed vista and NPS favorite for both sunrise and sunset.
- Mesquite Flat Sand Dunes are known for dramatic shadows near sunrise/sunset and are explicitly recommended for Death Valley dark-sky viewing.
- Death Valley has no general closing time, but extreme heat remains a safety boundary.

Opportunities:
- P01 Zabriskie sunrise badlands.
- P02 Zabriskie sunset badlands / Panamint layers.
- P03 Mesquite Dunes stars / Milky Way with dune foreground.

Runtime:
- P01 / P02 use directional_horizon + visibility.
- P03 uses astronomy_ephemeris.
- Astro evidence proves the night-sky subject, not an exact Milky Way Core/dune alignment.
- Heat risk is documented separately from photographic quality.

## us-015 — Golden Gate Bridge

Official sources:
- NPS Golden Gate Overlook:
  https://www.nps.gov/places/000/golden-gate-overlook.htm
- NPS Marin Headlands Scenic Vistas:
  https://home.nps.gov/goga/planyourvisit/marin-headlands-scenic-vistas.htm
- Golden Gate Bridge District photography locations / commercial permits:
  https://www.goldengate.org/district/permits/filming-photography-permits/

Verified:
- NPS classifies Golden Gate Overlook as a Scenic View/Photo Spot and explicitly describes sunset views with the bridge.
- NPS identifies Battery Spencer as one of the most popular scenic overlooks for the Golden Gate Bridge.
- Bridge District pages list multiple photo locations and clarify jurisdiction / commercial-use permit rules.

Opportunities:
- P01 Golden Gate Overlook sunset + bridge.
- P02 Battery Spencer bridge / bay panorama.

Runtime:
- P01 uses directional_horizon + visibility.
- P02 uses minimum-sufficient visibility.
- Fog is treated as a visibility/quality condition: thin fog may add atmosphere if the bridge remains readable, while bridge-obscuring fog is a penalty.
- Commercial-use permit rules are not converted into a personal-tourist access gate.

## Catalog delta

Adds:
- 5 US Places
- 11 Opportunities
- 11 Condition Variants
- 11 viewpoint relations

Expected totals after B64:
- 133 curated Places
- 297 Opportunities
- 312 Condition Variants
- 303 viewpoint relations

US:
- us-001 through us-015 migrated
- 15 Places / 27 Opportunities / 27 variants / 27 viewpoint relations
- us-016 through us-070 remain research-pending

Expected runtime-policy totals:
- module_pending: 88
- preview_module_available: 102
- minimum_sufficient_available: 101
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

## QA

B64 updates:
- Adapter assertions for us-011 through us-015.
- Evidence registry for Oxbow / Rainier reflection and Death Valley astro.
- US Candidate Weather researched range through us-015.
- Browser Smoke researched-card expectations: 15 researched / 55 pending.
