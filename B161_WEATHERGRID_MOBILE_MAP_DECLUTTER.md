# B161 — WeatherGrid mobile map declutter

Date: 2026-10-01

## Goal

Reduce map clutter on phone-sized WeatherGrid views without removing any Place
data or changing desktop behavior.

The mobile screenshot showed many nearby Place cluster bubbles competing with
basemap labels across Taiwan. B160 reduced surrounding UI chrome; B161 focuses
on the map itself.

## Responsive Place clustering

When the rendered map width is 600 px or less, Place clustering uses larger
screen-space radii:

- zoom < 6.2: 44 px
- zoom < 7.5: 32 px
- zoom < 8.4: 20 px
- zoom >= 8.4: individual points

Desktop keeps the existing 24 / 16 px clustering thresholds.

The fallback Canvas view uses the same idea with map-span thresholds.

## Marker treatment

On compact maps:

- cluster circles and count text are slightly smaller;
- click/tap behavior is unchanged;
- the selected Place always remains separate from clusters;
- the selected Place label uses 16 px instead of 20 px;
- selected labels automatically flip to the left when they would overflow the
  right edge of the map.

## Map controls

On phones, MapLibre +/- controls are reduced to 34 px square and the basemap
status badge is narrower. This leaves more usable map surface for weather and
Place content.

## Guardrails

- no Place records are removed;
- no coordinates change;
- no weather values or model behavior change;
- no coverage geometry changes;
- no scoring changes;
- desktop Place clustering thresholds remain unchanged.

## Regression requirements

The WeatherGrid UI polish contract verifies mobile-specific cluster thresholds,
compact marker typography, edge-aware selected labels, and smaller MapLibre
controls.
