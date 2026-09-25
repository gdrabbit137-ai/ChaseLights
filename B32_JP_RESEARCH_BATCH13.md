# ChaseLights R4.2 B32 — Japan Research Migration Batch 13

Date: 2026-09-25 (Asia/Taipei)
Branch: `r4.2-b32-jp025-hagi`

## Scope

This batch researches:

- `jp-025 萩市城下町`

The legacy city-wide Place has been narrowed to the photographically specific **菊屋横町 / Kikuya Yokocho** historic lane.

## Why Kikuya Yokocho

Authoritative evidence identifies Kikuya Yokocho as a representative and highly photographable part of Hagi Castle Town.

Sources:
- JNTO — Hagi Castle Town: https://www.japan.travel/en/spot/169/
- JNTO — Kikuya Yokocho: https://www.japan.travel/en/spot/867/
- Hagi City — preserved historic townscape: https://www.city.hagi.lg.jp/soshiki/55/h3297.html
- Hagi City — castle-town walking course: https://www.city.hagi.lg.jp/site/machihaku/kochizu-jokamachi.html

The researched subject is not a generic Hagi city-centre coordinate. It is the preserved white-wall / namako-wall lane, gates, historic street context and seasonal orange-tree details where actually present.

## Camera Zone

Primary researched Camera Zone:

- Name: 萩城下町・菊屋横町 Historic Lane Camera Zone
- Navigation anchor: `34.4119363, 131.3932271`
- Geometry: public historic lane, approximately 500 m
- Confidence: high
- Map query: `菊屋横町 萩市`

Coordinate sources:
- MapFan mapped Kikuya Yokocho POI: https://mapfan.com/spots/SCYH3%2CJ%2C7
- Geotagged photographed point cross-check: https://commons.wikimedia.org/wiki/File:Kikuya_Lane_in_Hagi_Castle_Town_5.jpg

The coordinate is a representative lane anchor, not a mandatory tripod point.

## Opportunity contracts

### jp-025-P01 — 萩城下町・菊屋橫町白壁與江戶街景

This is the normal all-year researched photographic Outcome.

- Mode: `area_opportunity`
- Compatibility Theme: `mountain_view` only as a daylight baseline.
- Best time: visible daylight, Place-local JST.
- Successful Outcome:
  - historic white / namako walls readable;
  - gates and street context readable;
  - no material rain preventing ordinary walking / handheld photography.
- Seasonal details such as summer oranges are boosters only.

### Dedicated local-scene minimum-sufficient contract

A close-range historic lane must not be scored like a distant mountain panorama.

Therefore P01 uses:

`minimum_sufficient_local_scene`

The runtime contract intentionally:
- does **not** make low cloud a blocker;
- does **not** require long-range atmospheric visibility;
- requires precipitation/access data;
- treats material precipitation or access closure as blockers;
- may return a curated score hint of 82/88 when the local scene itself is photographically usable.

The legacy Theme remains only a compatibility/time baseline and cannot override the researched local-scene contract.

### jp-025-P02 — 2026 萩・竹灯路物語・菊屋橫町竹燈夜景

Official 2026 event sources:
- Hagi Tourism Association — Bamboo Lamp Festival:
  https://www.hagishi.com/search/detail.php?d=900030
- Hagi Tourism Association — 2026 night-tour route:
  https://www.hagishi.com/kimono/kimonoweek2026_kikaku/

Verified 2026 event window:
- 2026-10-09
- 2026-10-10
- 2026-10-11
- 18:00–21:00 JST

The official night-tour route explicitly passes through Kikuya Yokocho.

P02 therefore uses:

`needs_event_state_module`

Current runtime decision:
- the event has been researched;
- generic clear-night weather is **not** enough;
- ordinary nights must not be treated as bamboo-lantern nights;
- `event_state` is not yet a connected runtime component;
- P02 remains `module_pending` and cannot enter the 80+ recommendation band.

This deliberately prevents the annual event from leaking into normal-night scoring.

## Place naming / navigation

Frontend display override:
- zh-TW: `萩城下町・菊屋橫町`
- en: `Hagi Castle Town · Kikuya Yokocho`
- ja: `萩城下町・菊屋横町`

Navigation:
- `菊屋横町 萩市`

## Time-zone contract

- shooting/event times: `Asia/Tokyo` (JST)
- website Last Updated: browser/device timezone

## Migration result

After this batch:
- Japan researched: 25 / 35
- Japan research-pending: 10
- B32 Japan additive catalog:
  - 25 Places
  - 33 Opportunities
  - 33 Condition Variants
  - 33 profile-viewpoint relations

Next target:
- `jp-026 出雲大社`
