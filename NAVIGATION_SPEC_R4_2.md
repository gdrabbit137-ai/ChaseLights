# ChaseLights R4.2 — Navigation Target Specification

Date: 2026-09-25

## Problem being corrected

The previous V5.2 navigation behavior preferred `map_query` and opened Google Maps Search.

That is unsafe for photography Places because:
- a keyword can resolve to multiple map results;
- a Place name can refer to a large area rather than the researched shooting location;
- the Camera Zone can be different from the practical arrival point;
- a mountain summit / lake / internal viewpoint is not necessarily a valid road-navigation destination.

A researched Camera Zone must therefore never be assumed to be the navigation destination.

## Three distinct location concepts

### 1. Camera Zone

Where the researched photograph can actually be made.

Owned by the researched Opportunity/Viewpoint model.

Examples:
- summit observation deck;
- section of a historic lane;
- shoreline camera area;
- bridge/river entrance photo zone.

### 2. Navigation Target

Where a user should actually ask a map application to route them.

Examples:
- public entrance;
- trailhead;
- parking area;
- ropeway base station;
- visitor centre;
- station;
- legally accessible street point;
- the Camera Zone itself only when it has been explicitly verified as a practical arrival target.

A Navigation Target requires explicit evidence. It must not be inferred from `map_query`, Place name, Scene/Theme, or Camera Zone coordinates alone.

### 3. map_query

`map_query` is retained only as search/display metadata.

It may support:
- internal place-name search;
- human-readable map/search labels;
- research cross-checks.

It MUST NOT be used to construct the production Navigation URL.

## Data contract

Each Place exposes:

```json
"navigation_target": {
  "status": "verified | provisional_camera_anchor | needs_review | multiple_access_routes",
  "lat": 0.0,
  "lon": 0.0,
  "target_type": "entrance | trailhead | parking | station | street_access | viewpoint | camera_zone_or_place_anchor",
  "label_i18n": {
    "zh-TW": "...",
    "en": "...",
    "ja": "..."
  },
  "source": "...",
  "confidence": "high | medium | low",
  "note_i18n": {
    "zh-TW": "...",
    "en": "...",
    "ja": "..."
  }
}
```

### Status semantics

#### verified

A practical arrival point has been individually verified.

UI:
- label: Navigation / 導航 / ナビ
- Google Maps URL type: Directions
- destination: exact latitude/longitude
- keyword search is forbidden.

#### provisional_camera_anchor

No independent arrival point has yet been verified, but an exact Camera Zone / Place anchor exists.

UI:
- label: Map / 地圖 / 地図
- Google Maps URL type: exact coordinate map pin, NOT Directions
- this is not presented as verified navigation.

This transitional state preserves map usefulness without claiming that a road route can reach the photographed point.

#### needs_review

A safe single Navigation Target is not verified.

UI:
- navigation control is disabled / marked pending;
- no keyword search fallback;
- no route is generated.

#### multiple_access_routes

The Place has materially different arrival modes/routes and a single target would be misleading.

UI:
- do not silently choose one route;
- until route selection is implemented, do not create a Directions URL.

## URL contract

Verified target:

`https://www.google.com/maps/dir/?api=1&destination=<lat>,<lon>`

Provisional exact map pin:

`https://www.google.com/maps/search/?api=1&query=<lat>,<lon>`

Forbidden:

`https://www.google.com/maps/search/?api=1&query=<map_query>`

The frontend must never construct a navigation URL from a free-text `map_query`.

## Research workflow requirement

For every newly researched Place:
1. establish the Camera Zone;
2. separately determine the practical arrival/navigation target;
3. classify the navigation target status;
4. record source/confidence;
5. only `verified` may expose the Directions action.

For mountain / trail / ropeway / restricted-access Places, do not reuse summit/viewpoint GPS as a road destination unless explicitly verified.

## Initial migration policy

Existing Places are not automatically declared verified.

- explicit reviewed Navigation Targets use `verified`;
- existing exact Place/Camera coordinates without arrival evidence become `provisional_camera_anchor`;
- known problematic cases may be forced to `needs_review` or `multiple_access_routes`.

Initial explicit cases:
- 加羅湖: `needs_review` — hiking access target must be researched; the ambiguous keyword behavior is removed.
- 新穗高・西穗高口展望台: `needs_review` — Camera Zone is at the summit, while practical navigation should lead to an appropriate ropeway/base access point.
- 彌彥山頂公園: `multiple_access_routes` — ropeway, skyline and hiking access differ.
- 等等力溪谷 Golf Bridge: `verified` street/public-path access anchor.
- 萩城下町・菊屋橫町: `verified` public historic-lane access anchor.

## QA requirements

Browser smoke must verify:
- no Navigation/Map href contains an encoded Place keyword from `map_query`;
- a `verified` target uses Google Maps Directions with exact coordinates;
- a `provisional_camera_anchor` uses an exact-coordinate map pin;
- a `needs_review` Place does not expose a clickable map-search fallback;
- 加羅湖 specifically no longer opens a broad Google Maps keyword search.
