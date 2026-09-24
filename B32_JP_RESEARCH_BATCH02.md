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
