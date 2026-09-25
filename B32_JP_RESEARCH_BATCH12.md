# ChaseLights R4.2 B32 — Japan Research Migration Batch 12

Date: 2026-09-25 (Asia/Taipei)
Branch: `r4.2-b32-jp-research-batch01`

## Scope

This batch researches:

- `jp-014 等等力溪谷 / Todoroki Valley`

The Place is now research-complete, but **photographic recommendation remains on hold** because the current Setagaya City notice states that photography is not being accepted due to expected congestion.

## Current official access state

Setagaya City confirms:
- the riverside path reopened on **2026-03-24**;
- the path is narrow and some sections have poor footing / no railing;
- parts of the park have no night lighting and visitors are told **not to enter after dark**;
- during heavy rain, visitors are told to stay away from the river;
- because congestion is expected, the current park notice says **「撮影は受け付けておりません」**.

Source:
- https://www.city.setagaya.lg.jp/02075/9082.html

The wording of the current photography notice is broader than the normal commercial/permit workflow. ChaseLights therefore fails closed: it does not infer that ordinary visitor photography is acceptable while this notice remains in force.

## Photographic value

Setagaya City officially identifies Todoroki Valley as a Tokyo-designated scenic place with:
- the ravine formed by Yazawa River;
- dense woodland / deep-ravine atmosphere;
- seasonal cherry blossom, evergreen woodland and autumn foliage;
- Golf Bridge as a named landmark;
- Fudo waterfall as a separate landmark.

Source:
- https://www.city.setagaya.lg.jp/02059/3482.html

Tokyu's official Todoroki-area guide explicitly describes Golf Bridge as a symbolic red bridge whose contrast with the ravine greenery is photogenic.

Source:
- https://www.tokyu.co.jp/area/todoroki/article/arti-01JV1TBVVPWS0PQT6SSXW3H45C/

## Camera Zone

Primary researched Camera Zone:

- Name: 等々力渓谷 Golf Bridge／谷沢川入口 Camera Zone
- Anchor: `35.607857, 139.646545`
- Geometry: small-area public-path / bridge entrance zone, ~120 m extent
- Confidence: high

Coordinate cross-check:
- https://www.djq.jp/bridge_liblary/river_senkawa/tokyo_bridge_yazawa025_golf.php

This is not a mandatory tripod point.

## Opportunity contract

### jp-014-P01 — 等等力溪谷・Golf Bridge 紅橋與綠蔭溪谷

- Theme baseline: `mountain_view` as a daylight compatibility baseline.
- Mode: `area_opportunity`.
- Best time: daylight only, Place-local JST.
- Required photographic outcome:
  - red Golf Bridge;
  - Yazawa River / ravine context;
  - green woodland readable as the primary scene.
- Seasonal boosters:
  - spring green;
  - cherry blossom where actually present;
  - autumn foliage where actually present.
- Safety / access penalties:
  - after dark;
  - heavy rain / sudden river rise risk;
  - crowding;
  - official photography restriction.

### Runtime decision

Current formula status:

`access_hold_current_photography_not_accepted`

Current runtime policy:

`hold`

Therefore:
- research is complete;
- the Place is no longer `research_pending`;
- Opportunity score is hard-capped to **0** while the official notice remains in force;
- weather quality cannot override the access / photography hold;
- no 80+ recommendation is possible.

## Re-activation criteria

The hold may be reconsidered only when an authoritative Setagaya City source:
1. removes the current photography-not-accepted notice, or
2. clearly limits it to a narrower category that does not prohibit the ordinary visitor-photography use case ChaseLights serves.

At that time:
- re-check current access/safety notices;
- decide whether the Opportunity can become a minimum-sufficient visibility contract;
- re-run Adapter CI, Japan Candidate Weather QA and Browser Smoke.

## Time-zone contract

- shooting and access semantics use `Asia/Tokyo` (JST);
- website Last Updated remains the user's browser/device timezone.
