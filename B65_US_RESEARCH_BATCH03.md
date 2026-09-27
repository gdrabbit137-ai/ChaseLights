# ChaseLights R4.2 B65 — US Research Batch 03 (us-011 through us-015)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch migrates the next five US production Places into the canonical Opportunity catalog:

- us-011 大提頓國家公園 / Grand Teton National Park
- us-012 雷尼爾山國家公園 / Mount Rainier National Park
- us-013 火山口湖國家公園 / Crater Lake National Park
- us-014 死亡谷國家公園 / Death Valley National Park
- us-015 舊金山金門大橋 / Golden Gate Bridge

Only official National Park Service material is used for subject admission in this batch.

## Modeling boundary inherited from B64

A verified Camera Zone is not automatically the weather-sample coordinate.

If the Place coordinate does not represent the actual Camera Zone, wind or other local weather derived at the Place coordinate must not become a hard gate for a different local surface.

Therefore:
- Oxbow Bend reflection is a documented booster, not a water-surface hard gate.
- Reflection Lakes reflection is evidence-verified, but this batch gates on access + visibility until a Camera Zone-specific weather sample exists.
- B64 similarly removed Merced River water-surface hard gating from us-008 Sentinel Bridge.

## us-011 — Grand Teton / Oxbow Bend

Official sources:
- NPS Oxbow Bend: https://home.nps.gov/thingstodo/oxbowbend.htm
- NPS Moran and the East: https://www.nps.gov/grte/planyourvisit/moranplan.htm

Verified:
- Oxbow Bend is a photographer-favorite Snake River + Teton Range scene.
- NPS explicitly identifies both sunrise and sunset as favorite times.
- Mount Moran can reflect on calm water.

Opportunities:
- P01 sunrise Mount Moran / Snake River.
- P02 sunset Mount Moran / Snake River.

Runtime:
- both use directional_horizon + visibility;
- calm-water reflection is a researched booster, not a hard runtime condition.

## us-012 — Mount Rainier

Official sources:
- NPS Reflection Lakes: https://www.nps.gov/places/reflection-lakes.htm
- NPS Stargazing at Sunrise: https://www.nps.gov/thingstodo/star-gazing-at-sunrise.htm
- NPS Road Status: https://www.nps.gov/mora/planyourvisit/road-status.htm

Verified:
- Reflection Lakes reflects Mount Rainier and NPS explicitly shows the calm-morning reflection subject.
- Vehicle access via Stevens Canyon Road is seasonal.
- NPS recommends Sunrise / Sunrise Point for stargazing.
- Current access can differ materially from normal season expectations; in September 2026 Sunrise Road is closed to vehicles due to fires.

Opportunities:
- P01 Reflection Lakes Mount Rainier lake/reflection subject.
- P02 Sunrise dark-sky / Milky Way subject.

Runtime:
- P01 = dynamic_access + visibility, module-pending until authoritative current road access is connected.
- P02 = astronomy_ephemeris + dynamic_access, module-pending for the same reason.
- Good weather must not imply the road is open.

## us-013 — Crater Lake

Official sources:
- NPS Hiking: https://www.nps.gov/crla/planyourvisit/hiking.htm
- NPS Current Conditions: https://www.nps.gov/crla/planyourvisit/conditions.htm
- NPS Operating Hours & Seasons: https://www.nps.gov/crla/planyourvisit/hours.htm
- NPS Crater Lake Reflections Summer/Fall 2025 visitor guide:
  https://www.nps.gov/crla/learn/news/upload/Crater_Lake_Reflections_Summer-Fall_2025_Low-Res_508-2.pdf

Verified:
- Watchman Peak is a 360-degree lake panorama and is especially popular at sunset.
- NPS visitor material explicitly promotes Watchman sunset viewing.
- The same official guide promotes moonless Milky Way viewing at Crater Lake.
- The park is open year-round, but Rim Drive / trails / specific overlooks close seasonally or temporarily; the park-open state is not the same as viewpoint access.

Opportunities:
- P01 Watchman Peak / Watchman Overlook sunset.
- P02 rim dark sky / Milky Way.

Runtime:
- P01 = dynamic_access + directional_horizon + visibility, module-pending until current road/trail status is connected.
- P02 = astronomy_ephemeris + dynamic_access, also fail-closed on access.

## us-014 — Death Valley

Official sources:
- NPS Zabriskie Point:
  https://www.nps.gov/places/zabriskie-point-scenic-viewpoint.htm
- NPS Mesquite Flat Sand Dunes:
  https://home.nps.gov/places/mesquite-flat-sand-dunes.htm
- NPS FAQ:
  https://www.nps.gov/deva/faqs.htm

Verified:
- Zabriskie Point is an iconic, highly photographed sunrise/sunset location.
- Mesquite Flat Sand Dunes are known for low-angle sunrise/sunset shadows and texture.
- NPS also identifies the dunes as a strong dark-night-sky location.
- Summer heat is a safety constraint, not a photographic quality score.

Opportunities:
- P01 Zabriskie Point sunrise.
- P02 Mesquite Flat Sand Dunes sunset shadows.
- P03 Mesquite Flat dark sky / Milky Way.

Runtime:
- P01/P02 = directional_horizon + visibility.
- P03 = astronomy_ephemeris.

## us-015 — Golden Gate Bridge

Official sources:
- NPS Battery Spencer Overlook:
  https://www.nps.gov/places/000/battery-spencer-overlook.htm
- NPS Marin Headlands Scenic Vistas:
  https://home.nps.gov/goga/planyourvisit/marin-headlands-scenic-vistas.htm

Verified:
- Battery Spencer is explicitly a Scenic View/Photo Spot.
- NPS identifies Conzelman Road / Battery Spencer as a primary and popular Golden Gate Bridge photo corridor.
- Parking is limited.

Opportunity:
- P01 Battery Spencer Golden Gate Bridge + San Francisco/bay context.

Runtime:
- minimum-sufficient visibility.
- Fog is only a visibility penalty in this batch. It is not promoted into a separate fog-photography Opportunity without Place-specific subject evidence.

## Catalog delta

Expected B65 delta:
- +5 curated US Places
- +10 Opportunities
- +10 Condition Variants
- +10 viewpoint relations

Expected totals after B65:
- 133 curated Places
- 296 Opportunities
- 311 Condition Variants
- 302 viewpoint relations

Expected US migrated state:
- us-001 through us-015 migrated
- us-016 through us-070 research-pending

## QA expectations

- Adapter and semantic registry validation pass.
- Evidence Audit passes for Reflection Lakes and astro subjects.
- US Candidate Weather validates all 70 Place summaries / shards and researched IDs us-001..015.
- Non-migrated us-016..070 remain explicit research gaps with no legacy-score leakage.
- Browser Smoke sees 15 researched US cards and 55 research-pending US cards.
- No generated weather JSON is committed with this research PR.
