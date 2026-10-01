# B162 — WeatherGrid mobile map declutter

Date: 2026-10-01

## Goal

Reduce map clutter on phone-sized WeatherGrid views after the B160 layout
optimization and B161 cloud-readability update.

The phone map can contain many nearby Place clusters that compete with basemap
labels and the weather overlay. B162 keeps all Place data while grouping nearby
markers more aggressively on compact maps.

## Responsive Place clustering

When the rendered map width is 600 px or less, clustering uses:

- zoom < 6.2: 44 px
- zoom < 7.5: 32 px
- zoom < 8.4: 20 px
- zoom >= 8.4: individual points

Desktop keeps the existing 24 / 16 px thresholds.

The Canvas fallback uses equivalent span-based thresholds.

## Marker treatment

On compact maps:

- cluster circles and count text are slightly smaller;
- tap/click hit behavior is unchanged;
- the selected Place remains separate from clusters;
- selected Place text uses 16 px rather than 20 px;
- the selected label is measured and flips left when it would overflow the
  right side of the map;
- B161's appended cloud percentage, such as `不厭亭 · 16%`, is preserved.

## Map controls

On phones, MapLibre zoom buttons are reduced to 34 px square and the basemap
status badge is narrower, leaving more map surface for weather and Place data.

## Guardrails

- no Place records are removed;
- no coordinates are changed;
- no weather values or model behavior change;
- no B161 cloud-readability semantics change;
- no coverage geometry changes;
- no Photography Opportunity scoring changes;
- desktop Place clustering remains unchanged.

## Regression requirements

The WeatherGrid UI polish contract verifies mobile cluster thresholds, compact
cluster typography, edge-aware selected labels, preservation of the selected
cloud-percentage label, and smaller MapLibre controls.
