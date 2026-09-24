# ChaseLights R4.2 B32 — Japan Research Migration Batch 10

Date: 2026-09-25 (Asia/Taipei)
Branch: `r4.2-b32-jp-research-batch01`

## Scope

This batch migrates:

- `jp-021 新穗高高空纜車` → **新穗高・西穗高口展望台 / Shinhotaka · Nishi-Hotakaguchi Observatory**

The legacy broad coordinate is retired as the photography/navigation anchor. Research is centered on the real summit visitor photography area at Nishi-Hotakaguchi Station.

## Time-zone contract

- Shooting windows, hourly forecast rows, access windows and event times use the Place local timezone: `Asia/Tokyo` (JST).
- Website `Last Updated` continues to use the user's browser/device timezone.
- Never convert a Shinhotaka shooting window into the user's timezone for display.

## Camera Zone

Primary researched Camera Zone:

- Name: 西穗高口站屋頂展望台／頂之森 Camera Zone
- Anchor: `36.268335, 137.601580`
- Elevation: `2156 m`
- Geometry: small-area visitor observation zone, approximately 120 m extent
- Confidence: high

Cross-check:
- official Shinhotaka Ropeway material identifies Nishi-Hotakaguchi Station rooftop and Itadaki no Mori as summit scenic areas;
- MapFan station coordinate: approximately `36.2678409, 137.6017974`;
- multiple geotagged camera locations cluster within the same summit station area.

This is not a mandatory tripod point. It represents the legal summit visitor photography zone.

## Official research evidence

### Summit panorama

Shinhotaka Ropeway official material states:
- Nishi-Hotakaguchi Station is approximately 2,156 m above sea level;
- the rooftop observation deck offers a 360-degree Northern Alps panorama;
- identifiable landscape subjects include Mt. Nishihotaka, Mt. Yari, Mt. Kasagatake and the deep alpine valley;
- Itadaki no Mori provides additional outdoor viewpoints.

Sources:
- https://shinhotaka-ropeway.jp/en/info01/
- https://shinhotaka-ropeway.jp/en/about/

### Seasonal photography value

Official seasonal material supports:
- spring: remaining snow + new green contrast;
- summer: alpine greenery;
- autumn: foliage, typically with a strong period around mid-October; snow-capped peaks may coexist with autumn color;
- winter: snow-covered Northern Alps.

Source:
- https://shinhotaka-ropeway.jp/en/season/

These are photographic boosters, not guaranteed daily Outcomes. The scorer must not claim autumn foliage or snow is present unless a corresponding seasonal/ground-state signal is available.

### Ropeway access

Official business information states the ropeway is generally operated year-round but may suspend because of:
- adverse weather;
- scheduled maintenance;
- operational notices.

Therefore weather quality alone is not sufficient to recommend the summit.

Source:
- https://shinhotaka-ropeway.jp/en/price/

### Night stargazing access

Night access is **not normal year-round access**.

The official Stargazing Service publishes date-specific night operations. For 2026 autumn the official schedule includes:
- Oct 2–4
- Oct 9–12
- Oct 30–Nov 3
- Nov 6–8

Published special-service timing includes:
- first ascent from Shirakabadaira around 18:00;
- last ascent around 20:20;
- descent service from Nishi-Hotakaguchi until around 21:00.

Only the No. 2 Ropeway operates for the special night service.

Source:
- https://shinhotaka-ropeway.jp/en/2025%E5%B9%B4%E5%BA%A6%E3%81%AE%E6%98%9F%E7%A9%BA%E8%A6%B3%E8%B3%9E%E4%BE%BF%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6/

Do not infer future-year dates from the 2026 schedule.

## Opportunity contracts

### jp-021-P01 — 西穗高口展望台・北阿爾卑斯360°高山景觀

- Theme baseline: `mountain_view`
- Mode: `area_opportunity`
- Runtime status: `needs_dynamic_access_visibility_module`
- Best time: ropeway-accessible daylight, Place-local JST
- Required:
  - Northern Alps mountain/valley landscape readable;
  - sufficient visibility;
  - low cloud/fog not materially obscuring the major mountain mass.
- Hard access gate:
  - required ropeway route actually operating;
  - no official suspension/maintenance closure.
- Boosters:
  - clean air;
  - seasonal snow/foliage contrast when actually present.
- Current runtime policy:
  - `module_pending`
  - score cap `<=64` until authoritative ropeway access provider is connected.

### jp-021-P02 — 西穗高口限定星空觀賞便・北阿爾卑斯星空

- Theme baseline: `milky_way`
- Mode: `area_opportunity`
- Runtime status: `needs_astronomy_ephemeris_access_module`
- Astronomy module: registered and ready
- Dynamic access: pending
- Best time: only official Stargazing Service nights, Place-local JST
- Required:
  - official event date/time is active;
  - special night ropeway actually operating;
  - visitor can still descend on the official last service;
  - astronomy/darkness conditions valid;
  - cloud conditions usable.
- Important:
  - a clear ordinary night is **not** enough;
  - do not claim exact Milky Way foreground alignment without verified geometry.
- Current runtime policy:
  - `module_pending`
  - score cap `<=64` until event/access provider is connected.

## Runtime / QA invariants

- `jp-021` is researched and must no longer be `research_pending`.
- Expected Opportunity IDs:
  - `jp-021-P01`
  - `jp-021-P02`
- Both remain capped at 64 while dynamic access is missing.
- P01 dependency state:
  - ready: visibility
  - missing: dynamic_access
- P02 dependency state:
  - ready: astronomy_ephemeris
  - missing: dynamic_access
- P01 access classification: `transport_facility_status`
- P02 access classification: `event_access_control`
- High-score whitelist must not contain `jp-021` until the access provider is authoritative and tested.
- No legacy `cloud_sea`, sunrise, sunset or snow-scene score may leak into the Place merely because those tags existed in the old catalog.

## Remaining work before high-confidence scoring

1. Connect an authoritative Shinhotaka Ropeway operation-status provider for P01.
2. Connect an authoritative annual Stargazing Service schedule/status provider for P02.
3. Confirm provider freshness / outage semantics.
4. Add provider regression fixtures for:
   - ropeway open;
   - ropeway suspended;
   - maintenance closure;
   - valid Stargazing Service night;
   - ordinary clear night with no event access.
5. Only after these tests pass may `jp-021` enter the 80+ recommendation band.
