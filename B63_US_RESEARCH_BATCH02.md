# ChaseLights R4.2 B63 — US Research Batch 02 Draft (us-006 through us-010)

Date: 2026-09-27 (Asia/Taipei)

Status: implementation batch. Rebuilt from main after B61 merged.

## Scope

- us-006 布萊斯峽谷國家公園 / Bryce Canyon National Park
- us-007 錫安國家公園 / Zion National Park
- us-008 優勝美地半圓頂 / Yosemite Half Dome
- us-009 優勝美地隧道觀景臺 / Yosemite Tunnel View
- us-010 黃石國家公園 大稜鏡溫泉 / Yellowstone Grand Prismatic Spring

## Evidence/model boundary

Only official NPS material is used for this draft.

Do not create a Photography Opportunity merely because a legacy tag says mountain/starlight.
Each subject below is tied to an official NPS viewpoint/photo/stargazing statement.

## us-006 — Bryce Canyon National Park

Official sources:
- NPS Viewpoints: https://www.nps.gov/brca/planyourvisit/viewpoints.htm
- NPS FAQ: https://www.nps.gov/brca/planyourvisit/faqs.htm
- NPS Stargazing: https://www.nps.gov/thingstodo/stargazing-at-bryce-canyon.htm
- NPS Hours: https://www.nps.gov/brca/planyourvisit/hours.htm

Verified:
- Sunrise Point and Bryce Point are official Bryce Amphitheater viewpoints.
- NPS identifies Sunrise Point and Bryce Point as popular sunrise locations.
- NPS recommends Paria View / Sunrise Point / Sunset Point / Inspiration Point for stargazing.
- NPS explicitly recommends Queen's Garden / Navajo trails for night photography with hoodoo foregrounds.
- Park is open 24h year-round, with temporary winter road closures possible after snow storms.

Proposed Opportunities:
- P01 Bryce Amphitheater hoodoos at sunrise — directional_horizon + visibility.
- P02 Bryce dark sky / Milky Way with hoodoo foreground — astronomy_ephemeris.

Runtime boundary:
- P01 can reuse configured directional-horizon and visibility components.
- P02 can reuse astronomy_ephemeris.
- Temporary snow-road closure remains a current-conditions caveat; do not invent a permanent seasonal closure for the entire park.

## us-007 — Zion National Park

Official sources:
- NPS Sunrise and Sunset: https://www.nps.gov/zion/planyourvisit/sunrise-and-sunset.htm
- NPS Pa'rus Trail: https://www.nps.gov/thingstodo/hike-pa-rus-trail.htm
- NPS Hours: https://www.nps.gov/zion/planyourvisit/hours.htm

Verified:
- Canyon Overlook Trail is explicitly recommended by NPS for sunrise light entering Zion Canyon.
- Pa'rus Trail is explicitly recommended for sunset views of golden light on the Watchman.
- NPS states Pa'rus Trail is also a good location for stargazing and astrophotography.
- Zion is open 24/7 year-round; shuttle/road transport rules vary but the photographic subject itself is not a booked event.

Proposed Opportunities:
- P01 Canyon Overlook sunrise canyon light — directional_horizon + visibility.
- P02 Pa'rus Trail Watchman sunset — directional_horizon + visibility.
- P03 Pa'rus Trail night sky / astrophotography — astronomy_ephemeris.

Runtime boundary:
- Parking scarcity at Canyon Overlook is an operational note, not proof of closure.
- Do not convert shuttle operation into a false whole-park closed state.

## us-008 — Yosemite Half Dome

Official sources:
- NPS Sentinel Bridge: https://www.nps.gov/places/000/sentinel-bridge.htm
- NPS Cook's Meadow Loop: https://www.nps.gov/yose/planyourvisit/cooksmeadowtrail.htm

Verified:
- Sentinel Bridge is an official Scenic View/Photo Spot with an excellent view of Half Dome.
- NPS explicitly identifies Half Dome mirrored in the Merced River, especially at sunset.
- NPS states the reflection is best when water is low and relatively still, such as fall or winter.
- Sentinel Bridge is reachable by car year-round.
- Cook's Meadow also has official Half Dome views.

Proposed Opportunity:
- P01 Sentinel Bridge Half Dome sunset / river foreground.

Runtime design:
- Use directional_horizon + visibility for the base sunset subject.
- Treat a mirror-like Merced River reflection as a documented photographic booster, not a runtime hard gate in this batch.
- Reason: ChaseLights currently fetches ordinary weather from the Place coordinate. The legacy us-008 coordinate is the Half Dome feature itself, while the Camera Zone is Sentinel Bridge on the valley floor. Reusing that mountain-coordinate wind as a river-surface proxy would be physically wrong.
- Do not enable water_surface_state for this Camera Zone until ChaseLights supports an explicit weather-sample coordinate separate from Place identity / Camera Zone / Navigation Target.
- Sentinel Bridge is documented as reachable by car year-round.
- Low seasonal river level is context only; month alone does not prove a reflection.

## us-009 — Yosemite Tunnel View

Official sources:
- NPS Tunnel View: https://www.nps.gov/places/000/tunnel-view.htm
- NPS Stargazing: https://www.nps.gov/yose/planyourvisit/stargazing.htm

Verified:
- Tunnel View is an official scenic/photo viewpoint showing El Capitan, Half Dome, Sentinel Rock, Cathedral Rocks and Bridalveil Fall.
- NPS explicitly says it is spectacular at sunset or after a clearing storm.
- It is reachable by vehicle year-round.
- NPS lists Tunnel View as an accessible Yosemite Valley stargazing location.

Proposed Opportunities:
- P01 Tunnel View iconic Yosemite Valley sunset panorama — directional_horizon + visibility.
- P02 Tunnel View night sky over valley walls — astronomy_ephemeris.

Runtime boundary:
- “after clearing storm” is supported as photographic context but should not be converted into a guaranteed special weather event.
- P01 remains a normal sunset/visibility opportunity.

## us-010 — Yellowstone Grand Prismatic Spring

Official sources:
- NPS Photography: https://www.nps.gov/yell/planyourvisit/photography.htm
- NPS Grand Prismatic Overlook Trail: https://www.nps.gov/thingstodo/yell-trail-grand-prismatic-overlook.htm

Verified:
- NPS explicitly identifies Grand Prismatic Spring as a major photography subject.
- Grand Prismatic Overlook is the only elevated overlook of the spring.
- Midway Geyser Basin boardwalk provides a ground-level view.
- Off-trail travel is prohibited.
- The overlook is reached from Fairy Falls Trailhead; access/road/trail conditions can vary and temporary closures occur.

Proposed Opportunity:
- P01 Grand Prismatic elevated overlook — dynamic_access + visibility, initially module-pending until an authoritative current-access provider exists.

Runtime boundary:
- Do not recommend an inaccessible overlook just because weather is good.
- Do not infer “best colors” from temperature alone without a researched steam/thermal-visibility model.
- Ground-level boardwalk and elevated overlook are distinct Camera Zones; this first Opportunity is specifically the elevated overlook.

## Catalog delta

B63 delta:
- +5 US curated Places
- +9 Opportunities
- +9 Condition Variants
- +9 viewpoint relations

Expected US migrated range after implementation:
- us-001 through us-010
- us-011 through us-070 remain research-pending

## Implementation notes

- Directional profiles are configured for us-006-P01, us-007-P01, us-007-P02, us-008-P01 and us-009-P01.
- Astronomy profiles are configured for us-006-P02, us-007-P03 and us-009-P02.
- Grand Prismatic uses the existing trail_road_status dynamic-access family and remains fail-closed until an authoritative live provider is connected.
- Sentinel Bridge reflection remains a documented booster, not a water-surface hard gate, because the current ordinary weather sample is tied to the legacy us-008 Place coordinate rather than the valley-floor Camera Zone.
- US Candidate QA and Browser Smoke advance the researched range to us-010 while us-011..070 remain explicit research gaps.
