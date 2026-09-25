# ChaseLights R4.2 B32 — Japan Research Migration Batch 09

Date: 2026-09-25 (Asia/Taipei)

Scope:
- jp-021 新穗高高空纜車 / Shinhotaka Ropeway
- jp-022 彌彥山 / Mt. Yahiko
- jp-024 大阪城公園 / Osaka Castle Park

This batch is research-only until the current Batch08 Japan Candidate QA and Browser Smoke are green.

## Time-zone contract

All Opportunity shooting windows and access windows are expressed in Place local time.
Japan Places use `Asia/Tokyo` (JST).
The website Last Updated timestamp remains user-device-local time.

---

## jp-021 — 新穗高高空纜車 / Shinhotaka Ropeway

### Official evidence

Shinhotaka Ropeway official facility information identifies:
- Nishi-Hotakaguchi Station at 2,156 m;
- a rooftop observation deck with a 360-degree panoramic view;
- visible subjects including Mount Nishihotaka, Mount Yari and Mount Kasagatake;
- adjacent Itadaki no Mori viewpoints/terraces.

The official operating page states:
- open year-round in principle;
- ropeway service can be suspended because of adverse weather, strong wind or scheduled maintenance;
- 2026 full-system maintenance closures include 2026-06-15 to 2026-06-26 and 2026-11-24 to 2026-11-27.

The official 2026 stargazing service is explicitly date-limited and must not be treated as a normal nightly access condition.

Sources:
- https://shinhotaka-ropeway.jp/en/info01/
- https://shinhotaka-ropeway.jp/en/
- https://shinhotaka-ropeway.jp/en/price/
- https://shinhotaka-ropeway.jp/%E3%80%902026%E5%B9%B4%E5%BA%A6%E3%80%91%E6%96%B0%E7%A9%82%E9%AB%98%E3%83%AD%E3%83%BC%E3%83%97%E3%82%A6%E3%82%A7%E3%82%A4%E3%81%AE%E9%81%8B%E8%A1%8C%E8%A8%88%E7%94%BB%E3%81%AB%E3%81%A4%E3%81%84/
- https://shinhotaka-ropeway.jp/play/%E6%98%9F%E7%A9%BA%E8%A6%B3%E8%B3%9E%E4%BE%BF/

### Candidate Opportunity

**jp-021-P01 — 西穗高口站屋頂・北阿爾卑斯360°山岳景觀**
- Camera Zone: Nishi-Hotakaguchi Station rooftop observation deck.
- current cross-checked anchor: approximately `36.267961, 137.601357`.
- best time: ropeway-access daylight / visible-light window in JST.
- best season: all operational seasons; seasonal snow/foliage are visual variants, not hard requirements.
- hard gates:
  - observation-deck/ropeway access available;
  - no maintenance closure;
  - visible-light shooting window valid.
- required:
  - Northern Alps ridges readable;
  - sufficient visibility;
  - low cloud/fog not materially hiding the mountain panorama.
- penalties:
  - ropeway suspension;
  - strong-wind operational closure;
  - dense low cloud/fog;
  - severe precipitation.
- runtime decision:
  - do NOT enable as a simple visibility-only Opportunity until dynamic ropeway access status is integrated or a safe access state can be established.
  - initial runtime policy should remain access/module-pending.

### Separate seasonal Opportunity

**jp-021-P02 — 西穗高口特別星空觀賞便**
- valid only on officially announced special-operation dates.
- requires astronomy conditions + official event/access date.
- MUST NOT be enabled from generic starlight tags or assumed to recur on the same dates every year.

---

## jp-022 — 彌彥山 / Mt. Yahiko

### Official evidence

Niigata Prefecture official tourism identifies the Mt. Yahiko summit area as a panoramic photography destination:
- summit elevation 634 m;
- views across Echigo Plain, Sea of Japan and Sado Island;
- sunset over the Sea of Japan;
- night view and starry sky;
- Yahikoyama Summit Park includes the rotating Panorama Tower.

Access evidence:
- standard ropeway hours are seasonal and may change with weather;
- Mt. Yahiko Skyline is typically open 05:00–23:00 in Apr-Nov, subject to residual snow/conditions;
- Panorama Tower has winter closure; official prefectural tourism states annual closure beginning around Nov 6;
- 2026 Night View & Stargazing Cruise is a special-date operation, not a year-round nightly service.

Sources:
- https://niigata-kankou.or.jp/spot/7461
- https://niigata-kankou.or.jp/spot/7462
- https://niigata-kankou.or.jp/spot/7484
- https://niigata-kankou.or.jp/spot/7478
- https://niigata-kankou.or.jp/experience/11966

### Coordinate cross-check

Current generic summit anchor has only medium confidence.
Panorama Tower cross-check:
- approximately `37.710125, 138.809994`.
- use this as a candidate Camera Zone anchor only after the runtime catalog explicitly identifies the Panorama Tower / summit observation area.

Cross-check source:
- https://stamp.funakiya.com/yahiko-panoramatower.html

### Candidate Opportunities

**jp-022-P01 — 彌彥山頂公園・越後平野與日本海全景**
- Camera Zone: summit park observation area / Panorama Tower vicinity.
- best time: visible light in JST.
- required:
  - broad plain/coast panorama readable;
  - adequate visibility;
  - low cloud/fog not obscuring the view.
- access:
  - must not assume one transport route is the only legal access.
  - ropeway, skyline and walking routes have different operating constraints.
- runtime:
  - keep module/access-pending until multi-route access semantics are represented safely.

**jp-022-P02 — 日本海夕日**
- official evidence explicitly supports sunset.
- requires directional-horizon + visibility.
- access window must still be valid for the chosen summit Camera Zone.

**jp-022-P03 — 夜景／星空特別運行**
- official 2026 night service supports this Outcome only on explicit dates.
- do not create a generic nightly score.
- requires event-date access + city-night / astronomy conditions.

---

## jp-024 — 大阪城公園 / Osaka Castle Park

### Official evidence

Osaka Castle's official guidebook explicitly identifies **Gokurakubashi Bridge** as a popular place for beautiful photographs of the Main Tower over the Inner Moat.

Osaka Castle's own photography-spot series also documents several real camera positions rather than generic castle-center coordinates, including:
- Aoyamon-area view toward the Main Tower;
- Tamatsukuri-guchi view, described as suitable in the morning and also visually strong at evening / illumination;
- Otemon-area compositions;
- Nishinomaru compositions.

For the first ChaseLights migration, Gokurakubashi is the cleanest public, easy-to-explain composition with direct official guidebook support.

Sources:
- https://www.osakacastlepark.jp/pdf/osakacastle_guidebook_english2024.pdf
- https://www.osakacastle.net/toyotomi_stone_wall/column/1906.html
- https://www.osakacastle.net/toyotomi_stone_wall/column/1910.html
- https://www.osakacastle.net/toyotomi_stone_wall/column/1911.html
- https://osaka-info.jp/en/spot/osaka-castle-park/

### Camera Zone

**Gokurakubashi north-side / Inner Moat camera area**
- official guidebook: popular Main Tower-over-moat photo spot.
- cross-checked photographed camera positions cluster around approximately:
  - `34.68920, 135.52675`.
- this is a Camera Zone anchor, not a mandatory tripod point.

Cross-check:
- https://commons.wikimedia.org/wiki/File:Tenshu_and_Gokurakubashi_Bridge_of_Osaka_Castle.jpg
- https://commons.wikimedia.org/wiki/File:Osaka_Castle_and_Gokurakubashi_Bridge.jpg

### Candidate Opportunity

**jp-024-P01 — 極樂橋・內護城河與大阪城天守閣**
- Camera Zone: north side of Gokurakubashi / Inner Moat public path.
- best time: visible light in JST.
- basic park access: Osaka Castle Park is officially always open, though internal facilities have separate hours.
- required:
  - Main Tower + bridge/moat composition readable;
  - adequate visibility;
  - no severe precipitation/fog.
- boosters:
  - clean air;
  - seasonal foliage/cherry blossoms may add value but are not required.
- reflection:
  - water reflection is optional, not a hard requirement.
- runtime:
  - strong candidate for minimum-sufficient visibility because the basic public-park architectural composition itself is a valid photographic Outcome.
- do not require Osaka Castle Museum opening hours for an exterior Gokurakubashi composition.
- do not create a year-round illumination/night Opportunity until managed-lighting semantics are separately researched.

---

## Proposed implementation order

1. **jp-024 Osaka Castle / Gokurakubashi** — strongest official photo-spot evidence, simple public access, minimum-sufficient runtime fits current engine.
2. **jp-021 Shinhotaka** — excellent official Camera Zone but access is operationally dynamic; implement only with a safe access contract.
3. **jp-022 Mt. Yahiko** — strong photographic evidence, but multiple access modes and event-only night operation require careful modeling.

## Remaining Japan research after Batch09

Still research-pending:
- jp-014 等等力溪谷
- jp-025 萩市城下町
- jp-026 出雲大社
- jp-027 神戶六甲山
- jp-028 高野山
- jp-029 伊賀上野城
- jp-030 鳴門海峽漩渦
- jp-031 倉敷美觀地區
- jp-032 福岡城跡
- jp-033 唐津城
- jp-034 長崎哥拉巴園
- jp-035 福岡塔
