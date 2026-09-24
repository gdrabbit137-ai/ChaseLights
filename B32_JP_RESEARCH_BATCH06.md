# ChaseLights R4.2 B32 — Japan Research Migration Batch 06

Date: 2026-09-25 (Asia/Taipei)
Branch: `r4.2-b32-jp-research-batch01`

Implementation status: **runtime-migrated on the B32 candidate branch** for all three Places:
- jp-011 東京鐵塔 / Tokyo Tower — two Main Deck Opportunities (day / city night), 09:00–22:30 JST arrival-access gate.
- jp-012 鎌倉大佛 / Great Buddha of Kamakura (Kotoku-in) — one daytime exterior Opportunity, seasonal last-entry gate in JST.
- jp-016 橫濱山下公園 / Yamashita Park — daytime harbor + city-night Opportunities from the researched India Water Tower / central-plaza camera area.

All three still require candidate QA / browser smoke before B32 release. Non-migrated Japan Places remain research_pending.

## Time-zone contract

- All shooting windows and access hours in this document are Place-local time.
- These three Places use `Asia/Tokyo` (JST).
- Website `Last Updated` remains user device/browser local time.

---

## jp-011 — 東京鐵塔 / Tokyo Tower

### Evidence

Tokyo Tower official sources state:
- Main Deck is at 150 m and provides a 360-degree panorama of Tokyo.
- Main Deck operating hours are 09:00–23:00, last entry 22:30.
- Top Deck is at 250 m and is a separate tour product with its own last-entry time.
- The official One-Day Pass page explicitly describes daytime and nighttime viewing, and notes that in good weather distant Mount Fuji and the Boso Peninsula can be visible.
- Current operation can change for severe weather or facility reasons; a static schedule must not be treated as proof of live operation.

Sources:
- https://ticket.tokyotower.co.jp/en/
- https://www.tokyotower.co.jp/fee/
- https://en.tokyotower.co.jp/fee/1day/
- https://en.tokyotower.co.jp/

### Candidate Opportunity

**jp-011-P01 — 東京鐵塔 Main Deck・東京城市日間全景**
- Camera Zone: Main Deck, 150 m observation level.
- mode: area_opportunity.
- best_time: daylight through blue hour/night, within visitor access.
- basic Outcome: readable Tokyo urban panorama from the observation deck.
- required conditions:
  - city panorama visibility usable;
  - fog/low cloud not materially hiding the near/mid-distance skyline.
- boosters:
  - exceptional long-range visibility can reveal distant Fuji/Boso, but those distant subjects are boosters, not guaranteed Outcome requirements.
- hard gates:
  - Main Deck visitor access available;
  - recommendation must not extend past last-entry/closing semantics.
- implementation:
  - use the existing Tokyo Tower POI coordinate as Place/vertical Camera Zone anchor;
  - encode Main Deck access conservatively as 09:00–22:30 for arrival/recommendation purposes, while documenting that already-admitted visitors may remain until 23:00;
  - minimum-sufficient visibility is acceptable for the base panorama only after access is represented.
- do not claim a specific Fuji alignment from the generic Main Deck Opportunity.

**jp-011-P02 — 東京鐵塔 Main Deck・東京城市夜景**
- Separate `city_night` Opportunity so daytime and night temporal semantics do not leak into each other.
- Same official 150 m Main Deck horizontal anchor / vertical Camera Zone.
- 22:30 JST is the arrival cutoff for recommendation; 23:00 closing time is not treated as a valid new-arrival time.

### Optional later Opportunity

A separate exterior Tokyo Tower composition should only be added after a real exterior Camera Zone (e.g. a researched park/temple/streetscape viewpoint) is verified. Do not use the tower's own coordinate to pretend it is an exterior photo position.

---

## jp-012 — 鎌倉大佛 / Great Buddha of Kamakura

### Evidence

Kotoku-in official sources state:
- April–September grounds: 08:00–17:30.
- October–March grounds: 08:00–17:00.
- Entry closes 15 minutes before the temple closes.
- Personal-use photography on the grounds is allowed.
- Commercial photography requires prior permission.
- Drones are prohibited.
- Photography inside the Great Buddha is prohibited.
- The official professional/commercial photography rules prefer 08:00–10:00 where possible to reduce interference with visitors; this must not be converted into a claim that ordinary personal photography is only valid then.

Sources:
- https://kotoku-in.jp/en/
- https://kotoku-in.jp/en-site/faq
- https://www.kotoku-in.jp/pdf/en/shinsei.pdf

### Candidate Opportunity

**jp-012-P01 — 高德院境內・鎌倉大佛日間建築／造像景觀**
- Camera Zone: legal visitor grounds facing the Great Buddha; not the statue interior.
- mode: area_opportunity.
- best_time: daytime during official grounds access.
- basic Outcome: readable exterior Great Buddha + temple-ground composition.
- hard gates:
  - temple grounds open;
  - daylight/visible-light composition;
  - no claim of interior photography.
- required conditions:
  - precipitation/fog not severe enough to materially obscure the statue;
  - enough daylight to read the bronze statue and surrounding context.
- boosters:
  - softer light can improve tonal range but is not a hard requirement.
- access schedule:
  - Apr–Sep: arrival cutoff should respect the 17:15 last-entry rule.
  - Oct–Mar: arrival cutoff should respect the 16:45 last-entry rule.
- implementation:
  - use place-local seasonal access schedule;
  - use a neutral visible-light baseline rather than legacy `city_night`/blue-hour semantics, because normal public access closes before a generic night-photo Opportunity is valid.
- do not promote the commercial 08:00–10:00 preference into a public hard gate.

---

## jp-016 — 橫濱山下公園 / Yamashita Park

### Evidence

Yokohama official tourism/city sources state:
- Yamashita Park is a waterfront park with broad harbor views.
- Official tourism describes views of Yokohama Bay Bridge and passing ships.
- Official night-view itinerary specifically names Yamashita Park as a night-view destination.
- The same official itinerary identifies the central plaza and India Water Tower area as recommended view spots and describes illuminated Hikawa Maru / Osanbashi light reflecting on the water.
- The park has free access; Yokohama accessible-tourism material explicitly lists 24-hour admission.
- The city page describes the park's open sea view and major waterfront landmarks.

Sources:
- https://www.yokohamajapan.com/things-to-do/detail.php?bbid=190
- https://www.yokohamajapan.com/tour-itineraries/detail.php?id=1
- https://www.yokohamajapan.com/accessibility/asset/docs/course/en_modelcourse-1_202505.pdf
- https://www.city.yokohama.lg.jp/kurashi/machizukuri-kankyo/midori-koen/koen/koen/daihyoteki/kouen008.html

### Candidate Opportunities

**jp-016-P01 — 山下公園・橫濱港海灣日間景觀**
- best_time: daylight.
- basic Outcome: harbor / Bay Bridge / ship traffic scene readable from the public waterfront.
- required conditions:
  - usable harbor visibility;
  - no severe fog/low cloud obscuring the bay.
- runtime:
  - minimum-sufficient visibility candidate.
- reflection is not required for the base daytime Opportunity.

**jp-016-P02 — 山下公園中央廣場／印度水塔區・港灣夜景**
- best_time: blue hour through night.
- official evidence supports the night-view Outcome.
- primary Camera Zone should be the central plaza / India Water Tower side rather than a generic park-center coordinate.
- required conditions:
  - illuminated harbor elements and skyline remain visible;
  - fog/low cloud not materially obscuring the harbor.
- boosters:
  - calmer water may improve reflected light, but reflection is not a hard requirement.
- access:
  - public park is 24-hour, so no normal opening-hours block is needed.
- implementation:
  - verify the exact Camera Zone anchor for central plaza / India Water Tower before runtime activation;
  - use city-night temporal semantics plus visibility.

---

## Batch06 implementation result

1. jp-016 Yamashita Park — implemented with two Opportunities and 24-hour public access semantics.
2. jp-011 Tokyo Tower — implemented with two Main Deck Opportunities and 22:30 JST last-admission arrival gate.
3. jp-012 Kamakura Great Buddha — implemented with one exterior daytime Opportunity and seasonal JST last-entry windows.

Current Japan researched migration count after Batch06: **16 / 35 Places**.

## Migration gates

- [ ] exact Camera Zone anchors verified for jp-016 P02 and jp-012 P01
- [ ] Tokyo Tower Main Deck access represented conservatively
- [ ] Kamakura seasonal last-entry windows represented in JST
- [ ] no night Opportunity for Kamakura Great Buddha under normal public hours
- [ ] no exterior Tokyo Tower composition without a real external Camera Zone
- [ ] all remaining Japan Places stay research_pending
