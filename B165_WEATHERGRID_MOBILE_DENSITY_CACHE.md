# B165 — WeatherGrid mobile density and cache freshness

Date: 2026-10-01

## Goal

Address two issues visible in the latest phone screenshot:

1. the display-strength slider still consumes a full vertical row;
2. some phones can continue showing an older WeatherGrid CSS/JS bundle after a
   deployment, which makes already-shipped mobile fixes appear missing.

The same pass also reduces MapLibre attribution clutter on small maps.

## Cache freshness

`weather-map.html` now references:

- `assets/weather-map.css?v=b165`
- `assets/weather-map.js?v=b165`

This deliberately changes the asset URLs so browsers and intermediary caches
request the current UI bundle after the deployment.

The weather JSON fetch path already uses `cache: no-store`; this change is
specifically for the static CSS/JS application shell.

## Mobile display-strength control

At widths up to 720 px, the display-strength control becomes one row:

`雲層 · 62%   [──────── slider ────────]`

The mobile label is shortened from `雲層顯示強度` to `雲層` (or `圖層`
for non-cloud fields). Desktop retains the full wording.

The slider keeps a 30 px interaction height and full horizontal range.

## Map attribution

MapLibre's default expanded attribution bar can overlap the weather legend and
consume a large part of the map on phones. WeatherGrid now instantiates an
explicit compact attribution control in the lower-right corner.

Attribution remains fully available by tapping the control; it is not removed.

## Guardrails

- no weather values change;
- no model selection, source priority, timing, coverage, QC or scoring changes;
- legal map attribution remains accessible;
- desktop display-strength wording and layout remain unchanged;
- B160–B164 mobile behavior remains intact.

## Regression requirements

The WeatherGrid UI contract verifies:

- versioned CSS and JS asset URLs;
- single-row mobile display-strength layout;
- short mobile opacity label with full desktop label retained;
- explicit compact MapLibre attribution control.
