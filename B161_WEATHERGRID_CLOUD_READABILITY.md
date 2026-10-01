# B161 — WeatherGrid cloud-percentage readability on mobile-ready UI

Date: 2026-10-01

## Goal

Restore the cloud-percentage readability work on top of the current WeatherGrid
UI, including B158 observation semantics and B160 mobile layout.

The forecast-cloud visualization must answer the practical question “below or
above 50% cloud cover?” at a glance without changing forecast values.

## Shared forecast cloud visual contract

Forecast cloud-percentage layers use the same provider-independent breakpoints
across JMA MSM, CWA WRF, ICON Global and GFS:

`0 / 20 / 40 / 50 / 70 / 85 / 100%`

The palette changes hue strongly at 50%, while opacity also increases by band.
Low percentages therefore recede toward the basemap and cloudier regions remain
visually prominent.

## 50% threshold aid

A subtle 50% contour is drawn over forecast cloud-percentage layers. It is
derived from the displayed forecast grid and is a visual reading aid only.

Himawari observation layers do not use this contour or forecast percentage
palette. Satellite cloud mask and cloud-top-height retain their categorical /
retrieval semantics.

## Selected Place label

When a forecast cloud layer is active, the selected Place label appends the
sampled percentage, for example:

`不厭亭 · 16%`

Observation mode keeps its existing label behavior.

## Display strength

The forecast cloud control is labeled **雲層顯示強度**. At 100% display
strength, the cloud raster is capped at 78% opacity so roads, coastlines and
basemap labels remain visible.

Other weather layers use the generic **圖層顯示強度** label.

## Mobile legend

B160's compact mobile legend is preserved. The seven cloud breakpoints are
shown in alternating rows, the 50% tick is emphasized, and the 50% threshold
key is compacted for phone widths.

## Guardrails

- no forecast or observed values are changed;
- no interpolation values are changed;
- no provider-selection policy is changed;
- no Himawari observation semantics are changed;
- no coverage geometry is changed;
- no Photography Opportunity scoring is changed;
- B160 mobile layout remains intact.

## Regression requirements

CI checks the shared breakpoint contract, 50% visual hinge and contour,
selected-Place cloud value, opacity cap, dynamic display-strength wording,
mobile cloud legend, and preservation of observation-mode separation.
