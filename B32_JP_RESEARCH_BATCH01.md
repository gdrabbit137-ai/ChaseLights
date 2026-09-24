# ChaseLights R4.2 B32 — Japan Research Migration Batch 01

Date: 2026-09-24 (Asia/Taipei)
Branch: `r4.2-b32-jp-research-batch01`

## Purpose

Begin the Japan Place-specific research migration without enabling photography scores from legacy Scene/Theme tags.

This batch covers:
- jp-001 美瑛青池 / Shirogane Blue Pond
- jp-002 旭岳 / Mt. Asahidake
- jp-003 釧路濕原 / Kushiro Shitsugen
- jp-004 函館山夜景 / Mt. Hakodate
- jp-005 小樽運河 / Otaru Canal

## Time-zone display contract

- Every shooting-time field, including `best_time`, daily best windows, hourly Weather Forecast rows, access windows, sunrise/sunset windows, and research notes, is interpreted and displayed in the **Place's local time zone**.
- Do not convert a Japan shooting window into the viewer's Taiwan/US/etc. device time.
- The website header's **Last Updated** timestamp is different: it is formatted in the **user device/browser time zone**.
- UI copy must make the distinction explicit so users do not confuse forecast/shooting time with data-refresh time.

Status in this document is **research definition only**. No Place becomes score-eligible until:
1. Opportunity text is evidence-backed,
2. at least one Camera Zone / Viewpoint is verified,
3. access semantics are machine-readable where they materially gate the Opportunity,
4. the runtime dependency profile is explicitly chosen,
5. regression tests confirm that no unsupported legacy score leaks through.

---

## jp-001 — 美瑛青池 / Shirogane Blue Pond

### Evidence

Official Biei Tourism Association:
- Open all year.
- Parking access is time-bounded.
- Official description explicitly identifies the blue water + larch forest landscape.
- Official visitor notice states that after snowmelt or heavy rain, the pond can become turbid or may not appear blue.
- Official winter notice states that accumulated snow can hide the blue water surface; winter illumination is operated seasonally instead.
- Peak congestion is strongest in daytime/afternoon; early morning and late afternoon are easier access windows.

Sources:
- https://www.biei-hokkaido.jp/en/facility/shirogane-blue-pond
- https://www.biei-hokkaido.jp/en/shirogane-blue-pond
- https://www.biei-hokkaido.jp/en/22426

### Candidate Opportunities

**jp-001-P01 — 青池藍色水面與落葉松景觀**
- legacy_theme: `mountain_view` or a future neutral landscape/forest-water baseline; do not force lake reflection semantics.
- best_time: daylight within effective access window.
- best_season: all year only for the Place; actual visible blue-water Outcome is not guaranteed in snow-cover period.
- hard gates:
  - legal visitor access;
  - daylight;
  - no known closure.
- required conditions:
  - visibility sufficient to resolve pond + larch forest;
  - no precipitation/low-cloud state severe enough to obscure the scene.
- evidence-backed penalty:
  - recent heavy rain / snowmelt may reduce blue appearance, but ChaseLights currently has no direct recent-water-turbidity provider. Treat this as **research fact, not machine-scored condition** until a suitable signal exists.
- winter rule:
  - do not recommend this Opportunity merely because weather is clear when the blue surface is seasonally snow-covered.

**jp-001-P02 — 冬季青池點燈雪景**
- Separate seasonal/night Opportunity.
- Must be gated by an official illumination schedule provider or curated effective-date window.
- Do not infer year-to-year illumination dates automatically.

### Remaining work

- Verify public walkway Camera Zone and exact anchor coordinates.
- Decide whether P01 uses a dedicated seasonal-ground-state gate or remains module-pending for winter.
- Build machine-readable parking/access hours only if they reliably map to visitor access.

---

## jp-002 — 旭岳 / Mt. Asahidake

### Evidence

Official Daisetsuzan Asahidake Ropeway:
- Ropeway operation status and daily hours are published.
- Sugatami Station is around 1,600 m.
- The official summer walking course around Sugatami Pond is approximately 1.7 km / 1 hour.
- The official page warns that mountain weather can change rapidly and visibility can deteriorate.
- Winter climbing requires appropriate planning/equipment and avalanche/weather checks.

Hokkaido official tourism also identifies Asahidake as a scenic alpine destination and publishes ropeway/visitor-center access.

Sources:
- https://asahidake.hokkaido.jp/en/
- https://www.visit-hokkaido.jp/en/spot/detail_10173.html

### Candidate Opportunities

**jp-002-P01 — 姿見池周邊旭岳火山高山景觀**
- legacy_theme: `mountain_view`.
- mode: area_opportunity.
- Camera Zone should be the legal Sugatami Pond walking-course area, not the legacy generic mountain coordinate.
- best_time: ropeway-access daylight window.
- best_season: walking-course season must follow official seasonal/access guidance rather than generic all-year availability.
- hard gates:
  - ropeway/access available if the route depends on ropeway;
  - sufficient daylight;
  - no access/operation closure.
- required conditions:
  - usable horizontal visibility;
  - low cloud/fog not materially hiding the mountain/volcanic terrain;
  - precipitation/wind within safe visitor conditions.
- boosters:
  - clear air and seasonal alpine color may improve photographic value, but vegetation/color phenology should not be machine-claimed without a seasonal provider.

### Remaining work

- Verify Sugatami Pond / main observation-area coordinates and legal Camera Zone geometry.
- Define whether separate winter snow-mountain Opportunity is justified; do not merge normal walking-course and winter-mountaineering access assumptions.
- Add ropeway operation provider semantics before any high-confidence recommendation that depends on ropeway access.

---

## jp-003 — 釧路濕原 / Kushiro Shitsugen

### Evidence

Japan Ministry of the Environment identifies multiple distinct observation points rather than one generic wetland viewpoint:
- **Hosooka Viewpoint**: panoramic Kushiro River meanders, wetland, Akan mountains; official page specifically recommends the sunset view.
- **Hokuto Observation Area**: official Kushiro tourism source identifies it as a strong sunrise-viewing location.
- The park contains other observatories with different visual outcomes; therefore the current single generic Place coordinate must not be treated as a verified camera point.

Sources:
- https://www.env.go.jp/nature/nationalparks/list/kushiro-shitsugen/spot/
- https://en.kushiro-lakeakan.com/things_to_do/3766/

### Candidate Opportunities

**jp-003-P01 — 細岡展望台釧路川濕原夕景**
- legacy_theme: `sunset`.
- viewpoint: Hosooka Viewpoint.
- best_time: sunset / late daylight.
- hard gates:
  - legal viewpoint access;
  - sunset timing valid.
- required conditions:
  - sufficient visibility for the broad wetland + river view;
  - western sky / landscape not fully obscured by low cloud/fog.
- boosters:
  - usable middle/high cloud at sunset;
  - clean air.

**jp-003-P02 — 北斗展望區濕原朝景**
- legacy_theme: `sunrise`.
- viewpoint: Hokuto Observation Area.
- best_time: sunrise / early daylight.
- hard gates:
  - legal viewpoint access;
  - sunrise timing valid.
- required conditions:
  - wetland panorama visible;
  - low cloud/fog not fully obscuring the scene.
- note:
  - atmospheric mist may sometimes be photographically valuable, but current official evidence used here does not justify a dedicated fog Outcome; do not auto-generate one.

### Remaining work

- Verify exact coordinates for Hosooka and Hokuto Camera Zones.
- Decide whether the legacy single `jp-003` Place remains a multi-viewpoint Place or should later split by observatory. Initial preference: one Place with multiple researched Viewpoints unless product UX demonstrates the observatories should rank independently.

---

## jp-004 — 函館山夜景 / Mt. Hakodate

### Evidence

Official Hakodate tourism:
- Mt. Hakodate is explicitly operated as a summit/night-view destination.
- Ropeway is the main access mode and operating hours are published.
- Road traffic restrictions and seasonal winter road closure are published.
- Nighttime viewing congestion is an operational consideration.
- The official page publishes 2026 access periods and warns of annual ropeway inspection suspension in late October/early November.

Source:
- https://www.hakodate.travel/en/information/mt-hakodate/

### Candidate Opportunities

**jp-004-P01 — 函館山暮色至夜間雙灣城市景觀**
- legacy_theme: `city_night`.
- viewpoint: summit observation area.
- best_time: blue hour into night, while legal summit access remains available.
- hard gates:
  - summit access route available;
  - viewing time inside effective access/transport window.
- required conditions:
  - city/coast panorama visibility sufficient;
  - low cloud/fog not materially obscuring the city basin and bays.
- boosters:
  - blue-hour transition can add sky/city contrast.
- penalties:
  - dense fog / low cloud;
  - access suspension/maintenance;
  - closure.
- do not model crowd level as weather score unless a dedicated congestion provider is intentionally added.

### Remaining work

- Verify summit Camera Zone coordinate/extent.
- Encode ropeway/road availability semantics without treating the road as the only access path.
- Keep annual maintenance windows source-driven.

---

## jp-005 — 小樽運河 / Otaru Canal

### Evidence

Official Otaru Tourism Association:
- Canal is walkable year-round.
- 63 gas lamps line the promenade.
- Gas lamps are lit from sunset to 24:00 on the main canal promenade.
- Warehouse illumination runs from sunset to 22:30.
- Official page explicitly names **Asakusa Bridge Garden (浅草橋街園)** as a representative photography spot.
- Kitahama Bridge and Asahi Bridge are also officially recommended photo points.

Source:
- https://otaru.gr.jp/shop/otarucanal

### Candidate Opportunities

**jp-005-P01 — 小樽運河暮色・瓦斯燈與石造倉庫**
- legacy_theme: `blue_hour` / `city_night` compatibility.
- primary viewpoint: Asakusa Bridge Garden Camera Zone.
- optional secondary researched viewpoints: Kitahama Bridge, Asahi Bridge.
- best_time: sunset through illuminated evening period.
- hard gates:
  - legal public promenade access;
  - lighting schedule active for the intended illuminated Outcome.
- required conditions:
  - canal/warehouse visibility usable;
  - precipitation/fog not severe enough to obscure the scene.
- boosters:
  - blue-hour ambient light before full darkness.
- do not require a perfect water reflection; wind/reflection quality is not necessary for the basic Opportunity.

### Remaining work

- Verify exact Camera Zone coordinates for Asakusa Bridge Garden and optional bridge viewpoints.
- Consider separate winter event Opportunity only if Snow Light Path dates/lighting are source-controlled; do not bake a recurring festival assumption into the generic canal Opportunity.

---

## Batch 01 migration gate

Before runtime integration:
- [ ] exact Camera Zone / Viewpoint coordinates verified
- [ ] source rows recorded for every Opportunity
- [ ] IDs reserved without colliding with existing Taiwan IDs
- [ ] access windows represented only where authoritative
- [ ] no unsupported seasonal/visibility claim promoted to a machine condition
- [ ] Japan cards remain score=null / research_pending until the selected Place has complete curated Opportunity data
- [ ] enabling a researched Japan Place must not enable legacy scoring for the other Japan Places

## Proposed implementation order

1. jp-005 Otaru Canal — strongest official photography-point + lighting-hour evidence.
2. jp-003 Kushiro Shitsugen — two official observation outcomes with sunrise/sunset evidence.
3. jp-004 Mt. Hakodate — clear night-view Outcome, but access-source integration matters.
4. jp-001 Shirogane Blue Pond — strong Place evidence, but winter surface-state semantics require care.
5. jp-002 Mt. Asahidake — strong scenic value but mountain/access/season modeling is the most safety-sensitive in this batch.
