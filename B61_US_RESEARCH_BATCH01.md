# ChaseLights R4.2 B61 — US Research Batch 01 (us-001 through us-005)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch starts the United States Opportunity migration with:

- us-001 大峽谷國家公園 / Grand Canyon National Park
- us-002 馬蹄灣 / Horseshoe Bend
- us-003 羚羊峽谷 / Antelope Canyon
- us-004 紀念碑谷 / Monument Valley
- us-005 拱門國家公園 / Arches National Park

The canonical production source remains `runtime_catalog_v004_r4_2.json`. This document records research/evidence and runtime decisions only.

## Evidence boundary

- NPS/Navajo official sources prove the place/subject/access facts.
- Weather/astronomy components only estimate when a verified subject may work.
- Guided-tour availability is not inferred from daylight or weather.
- Milky Way/night-sky evidence does not imply exact Galactic Core alignment.
- Navajo Tribal Park operating/permit rules are separate from photographic weather quality.

## us-001 — Grand Canyon National Park

Official sources:
- NPS sunrise/sunset: https://www.nps.gov/grca/planyourvisit/sunrise_set_moon.htm
- NPS photography: https://www.nps.gov/grca/planyourvisit/photography.htm
- NPS night skies: https://www.nps.gov/grca/learn/nature/night-skies.htm
- NPS hours: https://www.nps.gov/grca/planyourvisit/hours.htm

Verified:
- South Rim is open 24h / 365 days.
- NPS recommends Mather/Yaki for sunrise.
- NPS specifically identifies Desert View Watchtower + canyon/river as a sunset composition.
- NPS recommends South Rim night-sky sites and explicitly identifies Desert View Watchtower as a Milky Way-core foreground.

Opportunities:
- P01 Mather Point sunrise.
- P02 Desert View sunset / Watchtower foreground.
- P03 South Rim stars / Milky Way.

Runtime:
- P01/P02: directional_horizon + visibility, both configured.
- P03: astronomy_ephemeris, configured.
- No exact tripod point is invented; official public viewpoint zones are used.

## us-002 — Horseshoe Bend

Official source:
- NPS Horseshoe Bend Overlook:
  https://www.nps.gov/thingstodo/take-a-stroll-to-horseshoe-bend-overlook.htm

Verified:
- Colorado River horseshoe-bend overlook is the actual subject.
- Trail/overlook is open sunrise to sunset only.
- 1.5-mile round trip, exposed desert conditions, and unsafe unrailed cliff edges are material access/safety context.

Opportunity:
- P01 broad river/canyon overlook.

Runtime:
- minimum-sufficient visibility.
- static `daylight_only` access prevents night recommendations.
- low-angle light is a booster, not a required invented sunrise/sunset subject.

## us-003 — Upper Antelope Canyon

Official / place-specific sources:
- Navajo Nation Parks:
  https://navajonationparks.org/guided-tour-operators/antelope-canyon-tour-operators/
- Antelope Canyon Tours FAQ:
  https://www.antelopecanyon.com/faq/

Verified:
- all Antelope Canyon locations require a guided tour,
- visitors cannot enter independently,
- general canyon reflected-light photography is possible across tour times,
- classic direct beams occur only under appropriate sun/cloud geometry; the authorized operator identifies clear sunny days, an around-11:20 tour opportunity, and a primary Apr–Sep season.

Opportunities:
- P01 sandstone curves / reflected light.
- P02 seasonal direct sunbeams.

Runtime:
- P01 new `needs_dynamic_access_module`.
- P02 new `needs_radiation_dynamic_access_module`.
- both are classified as managed booking/access contracts.
- no authoritative live booking provider is connected, so both remain `module_pending`.
- this is intentional fail-closed behavior: favorable weather cannot invent tour availability.

## us-004 — Monument Valley Navajo Tribal Park

Official sources:
- Navajo Nation Parks park page:
  https://navajonationparks.org/tribal-parks/monument-valley/
- Navajo Nation Parks hours/tour operators:
  https://navajonationparks.org/guided-tour-operators/monument-valley-tour-operators/

Verified:
- official sandstone butte/mesa/desert-floor landscape,
- official park GPS N37.00414 W110.09889,
- seasonal public operating windows,
- Navajo rules/permits and designated-route boundaries matter.

Opportunity:
- P01 iconic butte/mesa landscape.

Runtime:
- minimum-sufficient visibility.
- seasonal access schedule is modeled conservatively.
- Feb 1–Mar 7 falls back to the official regular 08:00–17:00 window rather than inventing seasonal dates.
- fixed Christmas/New Year closures are encoded; moving-date Thanksgiving/Navajo Family Day remains a user-visible official-check boundary.
- no night-sky Opportunity is activated in this batch because access/permit semantics require separate research.

## us-005 — Arches National Park

Official sources:
- NPS photography:
  https://www.nps.gov/arch/planyourvisit/photography.htm
- NPS Balanced Rock:
  https://www.nps.gov/arch/planyourvisit/balancedrock.htm
- NPS operating hours:
  https://www.nps.gov/arch/planyourvisit/basicinfo.htm

Verified:
- Delicate Arch sunset is an explicit NPS photography subject.
- Balanced Rock is explicitly described by NPS as ideal for stargazing/night photography.
- Arches is generally open 24h year-round.
- artificial light may not be used to illuminate landscapes/rock formations.

Opportunities:
- P01 Delicate Arch sunset.
- P02 Balanced Rock stars / Milky Way night photography.

Runtime:
- P01 directional_horizon + visibility, configured.
- P02 astronomy_ephemeris, configured.
- artificial-light prohibition is recorded in the condition contract.

## Catalog delta

B61 adds:
- 5 curated US Places
- 9 Opportunities
- 9 Condition Variants
- 9 viewpoint relations

Expected canonical totals:
- 123 Places
- 279 Opportunities
- 294 Condition Variants
- 285 viewpoint relations

US migrated:
- us-001 through us-005
- 5 Places / 9 Opportunities / 9 Variants / 9 viewpoint relations

US research-pending after B61:
- us-006 through us-070

## Runtime delta

New dependency statuses:
- `needs_dynamic_access_module`
- `needs_radiation_dynamic_access_module`

Configured reusable profiles:
- directional_horizon: us-001-P01, us-001-P02, us-005-P01
- astronomy_ephemeris: us-001-P03, us-005-P02
- minimum-sufficient visibility: us-002-P01, us-004-P01
- dynamic-access classification: us-003-P01, us-003-P02 (not runtime-ready)

Expected policy totals:
- module_pending: 84
- preview_module_available: 92
- minimum_sufficient_available: 97
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2
