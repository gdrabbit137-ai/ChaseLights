# ChaseLights R4.2 B77 — Alaska Research Batch 14 (us-066 through us-070)

Date: 2026-09-27 (Asia/Taipei)

## Scope

This batch completes the remaining five US production Places in the canonical R4.2 Opportunity catalog:

- us-066 Bering Land Bridge National Preserve — narrowed to Serpentine Hot Springs
- us-067 Yukon River — narrowed to Yukon Crossing
- us-068 Noatak River
- us-069 Lake Clark National Park — narrowed to Port Alsworth / Lake Clark
- us-070 Independence Mine State Historical Park

After this batch, every US production Place from `us-001` through `us-070` has researched Opportunities.

## Modeling rules preserved

- Official / authoritative Place evidence proves what can actually be photographed.
- Legacy themes do not create Opportunities.
- Camera Zone, weather sample, landing/arrival point and Navigation Target remain separate concepts.
- Remote aviation, river-trip, highway and winter access are independent of favorable photography weather.
- `aurora_state` remains location-aware and fail-closed; planetary Kp alone is not proof.
- Reflection, snow, autumn color, wildlife and other optional foreground states remain boosters unless independently gated.
- A representative remote-wilderness weather coordinate must never become a fake road/airstrip Directions target.

## us-066 — Bering Land Bridge / Serpentine Hot Springs

Official sources:
- NPS Serpentine Hot Springs overview:
  https://www.nps.gov/places/serpentine-hot-springs-an-overview.htm
- NPS Reaching Serpentine Hot Springs:
  https://www.nps.gov/bela/planyourvisit/shs_travel.htm
- NPS Northern Lights:
  https://www.nps.gov/bela/learn/nature/northern-lights.htm

Verified:
- NPS publishes the exact Serpentine Hot Springs coordinate 65.8569N, 164.7142W.
- The official subject includes the granite tors, Serpentine valley and the remote bathhouse/bunkhouse setting.
- There are no roads into or within the preserve; Serpentine is commonly reached by air taxi / small plane and the gravel strip is unmaintained.
- NPS explicitly states northern lights can be witnessed from Bering Land Bridge National Preserve.

Opportunities:
- P01 Serpentine granite tors + hot-spring / bunkhouse wilderness landscape.
- P02 Serpentine / preserve aurora.

Runtime:
- P01 = `dynamic_access + visibility`.
- P02 = `aurora_state + dynamic_access`.
- Both remain `module_pending`.
- Access uses the remote transport/facility classification; static park hours or clear weather cannot prove an air taxi / landing / snow-travel route exists.
- No road Navigation Target is created.

## us-067 — Yukon River / Yukon Crossing

Official sources:
- BLM Central Yukon Field Office:
  https://www.blm.gov/office/central-yukon-field-office
- BLM Dalton Highway Visitor Guide:
  https://www.blm.gov/sites/default/files/docs/2022-04/AK-Dalton_Highway_Visitor_Guide_2022.pdf
- Coordinate cross-check only:
  https://www.alaska.org/detail/yukon-river-bridge

Verified:
- BLM identifies Yukon Crossing Visitor Contact Station at Dalton Highway mile 56.
- BLM states a short walk leads to riverbank viewing decks.
- The station is just north of the Yukon River bridge and is closed in winter.
- The researched Camera Zone is therefore the Yukon Crossing riverbank / bridge area rather than the old broad regional Yukon coordinate.

Opportunity:
- P01 Yukon River + E. L. Patton / Dalton Highway bridge and riverbank scene.

Runtime:
- `dynamic_access + visibility`.
- Current Dalton Highway / ice / construction / remote-driving safety remains a hard access dependency.
- B77 intentionally does **not** create a Yukon Crossing aurora Opportunity from the legacy aurora tag because the available official evidence is not sufficiently Place-specific.
- The coordinate is a cross-mapped planning anchor; no unsafe roadside tripod point is claimed.

## us-068 — Noatak River

Official sources:
- NPS The Noatak River:
  https://www.nps.gov/noat/learn/nature/noatakriver.htm
- NPS Floating:
  https://home.nps.gov/noat/planyourvisit/floating.htm
- NPS Noatak National Preserve:
  https://www.nps.gov/noat/index.htm
- NPS Gallery representative Noatak River asset:
  https://npgallery.nps.gov/AssetDetail/39311647-1DD8-B71C-070473883ABF3B36

Verified:
- NPS documents a mountain-ringed Wild and Scenic river basin with tundra, canyons, snow-capped peaks and glacial valleys.
- River access is primarily by air taxi from Bettles or Kotzebue, with no facilities or services once visitors depart.
- NPS directly publishes a northern-lights photograph reflected in the Noatak River.
- NPS media metadata provides an audited representative Noatak River location at 68.1814422607422, -159.394500732422.

Opportunities:
- P01 Noatak River wilderness + Brooks Range / canyon / tundra scene.
- P02 Noatak River aurora.

Runtime:
- P01 = `dynamic_access + visibility`.
- P02 = `aurora_state + dynamic_access`.
- Both remain `module_pending`.
- The NPS media coordinate is a representative weather/Camera Zone anchor only; it is not an airstrip, landing site or Directions target.
- Aurora reflection is a booster, not a guaranteed water-state result.

## us-069 — Lake Clark / Port Alsworth

Official sources:
- NPS Qizhjeh Vena (Lake Clark):
  https://www.nps.gov/lacl/learn/nature/lake-clark.htm
- NPS Port Alsworth:
  https://home.nps.gov/lacl/planyourvisit/port-alsworth.htm
- NPS Places To Go:
  https://www.nps.gov/lacl/planyourvisit/placestogo.htm

Verified:
- NPS describes Lake Clark as a glacial lake surrounded by mountains.
- NPS publishes Port Alsworth at 60°11.842N, 154°19.357W.
- The official Lake Clark page directly includes an aurora photograph from Port Alsworth.
- Port Alsworth is not connected to a road system and most visitors arrive by small plane.

Opportunities:
- P01 Port Alsworth / Lake Clark lake + surrounding mountain panorama.
- P02 Port Alsworth / Lake Clark aurora.

Runtime:
- P01 uses the minimum-sufficient visibility contract.
- P02 requires `aurora_state` and remains `module_pending`.
- Reflection, snow and autumn color remain optional current-state boosters.
- B77 replaces the old broad Lake Clark regional weather coordinate with the exact NPS Port Alsworth coordinate.
- Private shoreline ownership must not be interpreted as public Camera Zone access.

## us-070 — Independence Mine

Official sources:
- Alaska State Parks — Independence Mine State Historical Park:
  https://dnr.alaska.gov/parks/aspunits/matsu/indepmineshp.htm
- Alaska State Parks — Hatcher Pass East Management Area:
  https://dnr.alaska.gov/parks/aspunits/matsu/hatcherpassema.htm
- Alaska State Parks — current conditions:
  https://dnr.alaska.gov/parks/asp/curevnts.htm

Verified:
- Alaska State Parks documents Independence Mine as a historic gold-mining camp with public trails and historic features.
- Pedestrians can access the park after the upper parking gate closes by parking at Independence Bowl and walking.
- Hatcher Pass road / winter vehicle access changes seasonally, and Alaska State Parks publishes current condition reports.
- The site is a close-range historic/alpine subject.

Opportunity:
- P01 historic mining structures + Talkeetna Mountain setting.

Runtime:
- `dynamic_access` only; it remains `module_pending`.
- B77 does not add long-range visibility as a hard requirement to this close-range historic subject.
- B77 intentionally does **not** add an Independence Mine aurora Opportunity from the legacy tag because current official Place-specific evidence is insufficient.
- Current road, parking, snow and avalanche/access conditions remain independent of favorable photography weather.

## Catalog delta

B77 adds:
- 5 curated US Places
- 8 Opportunities
- 8 Condition Variants
- 8 viewpoint relations

Expected canonical totals:
- 188 curated Places
- 381 Opportunities
- 396 Condition Variants
- 387 viewpoint relations

Final US catalog:
- us-001 through us-070: all Opportunity-migrated
- 70 Places / 111 Opportunities / 111 variants / 111 viewpoint relations
- research-pending production Places: 0

## Runtime-policy delta

Relative to B76:

`minimum_sufficient_available` +1:
- us-069-P01 Lake Clark / Port Alsworth panorama

`module_pending` +7:
- us-066-P01 Serpentine remote access + visibility
- us-066-P02 Serpentine aurora + remote access
- us-067-P01 Yukon Crossing road access + visibility
- us-068-P01 Noatak River remote transport + visibility
- us-068-P02 Noatak River aurora + remote transport
- us-069-P02 Port Alsworth aurora
- us-070-P01 Independence Mine current access

Expected policy totals:
- module_pending: 128
- preview_module_available: 114
- minimum_sufficient_available: 133
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

Minimum-sufficient visibility profile count:
- 89

## QA

B77 updates:
- both Adapter researched-US guards to `us-001..us-070`,
- Adapter policy/dependency assertions for all eight new Opportunities,
- US Candidate Weather researched range to all 70 production Places and pending count to 0,
- Browser Smoke researched-US count to 70 and pending count to 0,
- remote transport access classifications for Serpentine and Noatak,
- road/access classifications for Yukon Crossing and Independence Mine,
- Lake Clark minimum-sufficient visibility registry,
- final Alaska Camera Zone/weather anchors.

Existing canonical us-001 through us-065 and all TW/JP curated Places must remain semantically unchanged.
