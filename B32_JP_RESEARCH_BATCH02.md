# ChaseLights R4.2 B32 — Japan Research Migration Batch 02 (research-only start)

Date: 2026-09-24 (Asia/Taipei)
Branch: `r4.2-b32-jp-research-batch01`

This file is research-only. It MUST NOT enable scores until Batch01 release gates are green and the relevant Camera Zone/access contracts are implemented.

## Time-zone contract

- Opportunity `best_time`, forecast windows, hourly rows and access windows are expressed in the Place local timezone.
- Japan Places use `Asia/Tokyo` (JST).
- The website header `Last Updated` timestamp is formatted in the user's browser/device timezone.

---

## jp-006 — 摩周湖 / Lake Mashu

Current map anchor:
- `43.556947, 144.507319`
- current map query: 摩周湖第一展望台
- coordinate confidence: high

### Official evidence

Hokkaido official tourism identifies multiple distinct photographic outcomes.

**Lake Mashu First Observatory / Kamuy Terrace**
- official description: unobstructed view over the deep-blue lake;
- calm conditions can produce mirror-like water/sky reflection;
- mist can transform the lake view rather than simply making the Place invalid;
- rooftop terrace remains usable at night and the official page explicitly promotes star/Milky Way viewing;
- visitor facility hours are published separately from the rooftop/viewing context, so do not assume lounge business hours equal outdoor-observation access without source-level confirmation.

Sources:
- https://www.visit-hokkaido.jp/en/spot/detail_10484.html
- https://www.visit-hokkaido.jp/tw/spot/detail_10484.html

**Lake Mashu Third Observatory**
- elevation about 670 m;
- official description explicitly identifies early-morning cloud-sea potential on the Kussharo-caldera side;
- closed from late November to early April.

Source:
- https://www.visit-hokkaido.jp/en/spot/detail_10483.html

### Candidate Opportunities

**jp-006-P01 — 摩周湖第一展望台・摩周藍湖景**
- legacy theme baseline: `mountain_view` or neutral lake/landscape baseline.
- best_time: daylight (JST).
- hard gates:
  - legal viewpoint access;
  - daylight for the blue-lake Outcome.
- required conditions:
  - lake/caldera visible enough to read the landscape.
- boosters:
  - clean visibility;
  - calm water can improve reflection.
- important semantic rule:
  - do NOT automatically treat fog as failure. Official research explicitly presents mist as a valid alternate visual state. A clear-lake Opportunity can be penalized by obscuring fog, but this must not become a generic claim that “fog is bad at Lake Mashu.”

**jp-006-P02 — 第一展望台星空／銀河**
- legacy theme: `milky_way`.
- best_time: astronomical night (JST).
- hard gates:
  - legal outdoor observation access;
  - astronomy window valid.
- required conditions:
  - dark-enough sky;
  - low cloud not blocking the sky.
- runtime:
  - astronomy ephemeris can be reused;
  - exact foreground/Core alignment must NOT be claimed without geometry research.

**jp-006-P03 — 第三展望台屈斜路側清晨雲海**
- legacy theme: `cloud_sea`.
- best_time: early morning/daylight (JST).
- best season/access:
  - Third Observatory is officially closed late Nov–early Apr.
- required conditions:
  - low cloud/fog filling lower Kussharo-caldera terrain while viewpoint remains above/clear enough.
- runtime:
  - requires spatial/vertical-cloud logic plus seasonal/dynamic access state.
- this Opportunity should remain module/access-pending until both are represented.

### Migration decision

Do not collapse the First and Third Observatory Outcomes into one generic coordinate-driven score. Keep `jp-006` as one Place with multiple verified Viewpoints unless later UX research supports splitting them into separate Places.

---

## jp-007 — 十和田湖 / Lake Towada

Current map anchor:
- `40.426538, 140.894325`
- map query: 十和田湖 休屋
- current coordinate represents Yasumiya lakeside, not Kankodai.

### Official evidence

Aomori official tourism describes Lake Towada as a major scenic lake whose still surface can mirror sky, greenery and autumn foliage. Official tourism also identifies mid-to-late October as the typical autumn-color peak period.

Source:
- https://aomori-tourism.com/en/spot/detail_335.html

**Kankodai Observation Deck**
- official tourism specifically describes Kankodai as a panoramic Lake Towada viewpoint and notes the sunset scenery.
- As of 2026-09-24, the official tourism site reports the prefecture-managed Kankodai observation deck and public restroom temporarily closed following a bear attack near the site on 2026-08-22.

Sources:
- https://aomori-tourism.com/spot/detail_370.html
- https://aomori-tourism.com/en/spot/detail_335.html

### Candidate Opportunities

**jp-007-P01 — 休屋湖畔・十和田湖湖景**
- primary current Camera Zone: Yasumiya public lakeside area.
- best_time: daylight (JST).
- best season: all open-access periods; autumn color is a separate seasonal booster, not a hard requirement.
- required conditions:
  - lake and surrounding mountain/forest layers visibly readable.
- boosters:
  - calm surface;
  - autumn color season.
- reflection rule:
  - do not require perfect reflection to recommend the basic lake view.

**jp-007-P02 — 瞰湖台十和田湖夕景**
- Viewpoint: Kankodai Observation Deck, not the current Yasumiya anchor.
- legacy theme: `sunset`.
- best_time: sunset (JST).
- research evidence: official tourism explicitly identifies sunset as a visual strength.
- current access status:
  - **HOLD** while the official closure remains in effect.
- no score should be emitted for this Opportunity until authoritative access state becomes open again.
- when reopened, exact Kankodai coordinate must replace any generic Lake Towada coordinate for this Opportunity.

### Migration decision

Do not repoint the whole `jp-007` Place to Kankodai while it is closed. Retain Yasumiya as the generic navigation anchor; attach Kankodai as an Opportunity-specific Viewpoint after exact coordinate verification.

---

## Batch02 next research targets

- jp-008 松島
- jp-009 磐梯山
- jp-010 富士山（河口湖）

These remain research-pending. Do not generate Opportunities from existing legacy tags.


---

## jp-008 — 松島 / Matsushima

Current map anchor:
- `38.369718, 141.064207`
- map query: 松島 五大堂
- current coordinate is a landmark POI, not the strongest researched landscape Camera Zone.

### Official evidence

Matsushima Tourism Association and Matsushima Town both identify multiple named viewpoints with different photographic outcomes.

**Sokanzan / 双観山**
- summit observation area is a developed public viewpoint;
- both Shiogama Bay and Matsushima Bay are visible;
- official tourism specifically identifies sunrise beyond Oshika Peninsula / Kinkasan as a major scenic strength;
- Matsushima Town likewise describes sunrise between the islands as especially strong.

Sources:
- https://www.matsushima-kanko.com/miru/detail.php?id=136
- https://www.matsushima-kanko.com/miryoku/shima/sokanzan.php
- https://www.town.miyagi-matsushima.lg.jp/page/1267.html

**Saigyo Modoshi no Matsu Park / 西行戻しの松公園**
- official tourism identifies the combination of cherry blossoms + Matsushima Bay;
- official page includes sunrise, winter and bay-view examples;
- Panorama Line is closed in winter, so vehicle-access assumptions cannot be treated as all-year.

Source:
- https://www.matsushima-kanko.com/miryoku/shima/saigyo.php

**Other sunrise/sunset/moon viewpoints**
- official tourism explicitly lists Sokanzan and Saigyo Modoshi for sunrise;
- Tedaru Seaside Park for sunset;
- Karantei for moon viewing.

Source:
- https://www.matsushima-kanko.com/miryoku/shiki/midokoro.php

### Candidate Opportunities

**jp-008-P01 — 双観山・松島湾群島朝景**
- legacy theme: `sunrise`.
- primary Viewpoint: Sokanzan summit observation area.
- best_time: sunrise / early daylight (JST).
- hard gates:
  - legal public viewpoint access;
  - sunrise timing valid.
- required conditions:
  - sufficient visibility to resolve island layers and distant horizon;
  - low cloud/fog not fully obscuring the bay/horizon.
- boosters:
  - usable middle/high cloud near sunrise;
  - clean air.
- runtime direction:
  - directional horizon + visibility.
- do not score from the current Godaido coordinate.

**jp-008-P02 — 西行戻しの松・櫻花與松島灣**
- legacy theme: neutral landscape / future seasonal-flower profile.
- primary Viewpoint: Saigyo Modoshi no Matsu Park observation area.
- best_time: daylight (JST).
- best season:
  - cherry-blossom Outcome must be seasonal and source-controlled;
  - generic bay view may remain broader.
- hard gates:
  - legal public access.
- access note:
  - Panorama Line winter closure affects vehicle approach; do not convert that directly into a total pedestrian-access closure without separate evidence.
- runtime:
  - clear-view minimum-sufficient may support the generic bay view;
  - blossom-specific high score should remain seasonal-phenology pending.

### Migration decision

Keep `jp-008` as one Matsushima Place with multiple researched Viewpoints. The current Godaido POI can remain a navigation fallback only if the product still needs a central Matsushima anchor; it must not be used as the weather geometry for Sokanzan sunrise.

---

## jp-009 — 磐梯山 / Mount Bandai

Current map anchor:
- `37.601111, 140.072222`
- current map query: 磐梯山 山頂
- current coordinate represents the summit and is not appropriate for the easiest researched landscape Outcome.

### Official evidence

Fukushima Prefecture's Green Reconstruction program identifies **Nakasenuma Observation Deck** as a named photography viewpoint:
- clear pond + broad-leaved forest + rugged Mount Bandai composition;
- described as a representative Urabandai viewpoint that has attracted many photographers;
- access is via the Nakasenuma trail, about 15 minutes from the trail entrance;
- listed season: year-round.

Sources:
- https://www.pref.fukushima.lg.jp/w4/fgr/perfectview/p04/
- https://www.pref.fukushima.lg.jp/w4/fgr/en/perfectview/p04/

Urabandai Tourism Association independently identifies the observation deck as the highlight/prime viewing spot:
- Nakasenuma Pond in the foreground;
- Mount Bandai behind;
- trail about 1.2 km, beginner level;
- approximately 15–25 minutes one way from trail entrances.

Sources:
- https://www.urabandai-inf.com/en/?page_id=30933
- https://www.urabandai-inf.com/en/?page_id=24970

Mount Bandai hiking itself is a separate, higher-risk product:
- official guide gives mountain season roughly late May to late October;
- summit/climbing access assumptions must not be mixed with the Nakasenuma landscape viewpoint.

Source:
- https://www.urabandai-inf.com/en/?page_id=25041

### Candidate Opportunities

**jp-009-P01 — 中瀬沼展望台・中瀬沼與磐梯山**
- legacy theme: `mountain_view`.
- mode: area_opportunity.
- Viewpoint: Nakasenuma Observation Deck.
- best_time: daylight (JST).
- season:
  - official prefectural viewpoint page says year-round;
  - winter access may require snow travel considerations, but it is not currently justified as a hard closure.
- required conditions:
  - Mount Bandai silhouette / volcanic wall readable;
  - Nakasenuma foreground and mountain not materially hidden by low cloud/fog;
  - usable horizontal visibility.
- boosters:
  - clear air;
  - autumn color can be a seasonal booster; Fukushima Prefecture publishes typical foliage periods, but phenology should not be promoted to a guaranteed current-state signal without a live/seasonal provider.
- runtime direction:
  - minimum-sufficient visibility is appropriate for the base landscape Outcome.
- safety:
  - do not reuse summit-mountain hiking access gates for this Opportunity.

**jp-009-P02 — 磐梯山登山／山頂景觀**
- separate future Opportunity only.
- must have trailhead-specific access, mountain-season semantics and safety notes.
- current generic summit coordinate is insufficient to enable this Opportunity.
- keep research-pending/module-pending until route and access are explicitly selected.

### Migration decision

For the first production migration, prefer `jp-009-P01` at Nakasenuma Observation Deck. Do not make summit hiking the default photography interpretation of the Place.

---

## jp-010 — 富士山（河口湖） / Mount Fuji from Lake Kawaguchi

Current map anchor:
- `35.523065, 138.746148`
- map query: 大石公園 河口湖
- coordinate matches Oishi Park and is suitable as the initial researched Camera Zone anchor.

### Official evidence

Fujikawaguchiko official tourism identifies Oishi Park as:
- a north-shore Lake Kawaguchi park;
- a photography spot with Lake Kawaguchi + Mount Fuji layered together;
- relatively unobstructed broad views;
- seasonal foregrounds including lavender in early summer and red kochia in autumn;
- park is open continuously / no regular closure.

Source:
- https://fujisan.ne.jp/sightseeing/1652/

The official tourism model course further states:
- early day is recommended for the park;
- late June to mid-July is the lavender period;
- in calm conditions, Mount Fuji may reflect on the lake as `逆さ富士`;
- mornings tend to be less crowded.

Source:
- https://fujisan.ne.jp/model-course/967/

Fujikawaguchiko Town's official municipal page confirms the Oishi Park public-facility location and park amenities.

Source:
- https://www.town.fujikawaguchiko.lg.jp/ka/info.php?if_id=2346

Mapped coordinate cross-check:
- MapFan: `35.5230652, 138.7461483`.

Source:
- https://mapfan.com/spots/SC34A%2CJ%2CQME

### Candidate Opportunities

**jp-010-P01 — 大石公園・河口湖越富士山**
- legacy theme: `mountain_view`.
- primary Viewpoint / Camera Zone: Oishi Park north-shore lakefront.
- best_time: daylight, with morning preference (JST).
- hard gates:
  - public park access;
  - visible-light shooting period.
- required conditions:
  - Mount Fuji sufficiently visible;
  - low cloud/fog not materially obscuring the mountain;
  - usable horizontal visibility.
- boosters:
  - clean air;
  - lower cloud obstruction.
- runtime direction:
  - minimum-sufficient clear-view / visibility profile is appropriate.

**jp-010-P02 — 大石公園・逆さ富士**
- legacy theme: `reflection`.
- same Camera Zone family.
- best_time: daylight / morning preference (JST).
- required conditions:
  - Fuji visible;
  - lake surface sufficiently calm.
- runtime direction:
  - water-surface-state + visibility.
- important rule:
  - reflection is an optional stronger Outcome; failure to get mirror conditions must not suppress P01.

**jp-010-P03 — 薰衣草／季節花景與富士山**
- seasonal foreground Opportunity.
- late June–mid July is officially documented for lavender.
- red kochia is an autumn seasonal foreground.
- do not enable high-confidence seasonal-color scoring until a date/phenology policy is explicitly selected.

### Migration decision

`jp-010-P01` and `jp-010-P02` are strong candidates for direct runtime migration because the Camera Zone, public access, subject geometry and weather dependencies are sufficiently clear. Keep seasonal flowers separate from the base Fuji landscape score.

---

## Batch02 implementation readiness

### Ready for first-pass runtime integration
- jp-010-P01 Oishi Park Fuji landscape — minimum-sufficient visibility
- jp-010-P02 Oishi Park reverse-Fuji reflection — visibility + water-surface-state
- jp-009-P01 Nakasenuma + Mt Bandai — minimum-sufficient visibility after exact Camera Zone coordinate is pinned
- jp-008-P01 Sokanzan Matsushima sunrise — directional horizon + visibility after exact Camera Zone coordinate is pinned

### Hold / further research
- jp-006 cloud-sea / star geometry details
- jp-007 Kankodai sunset while official closure remains active
- jp-008 blossom phenology
- jp-009 summit hiking
- jp-010 seasonal flower phenology

No Batch02 Place should be enabled from legacy Scene/Theme alone.
