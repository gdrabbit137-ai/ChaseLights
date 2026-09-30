# B159 — WeatherGrid cloud-percentage readability

Date: 2026-10-01

## Goal

Make forecast cloud amount readable at a glance, especially the practical
question of whether a selected location is below or above 50% cloud cover,
without changing any meteorological values or Photography Opportunity scoring.

## Shared cloud visual contract

All forecast cloud-percentage layers use the same provider-independent visual
scale across JMA MSM, CWA WRF, ICON Global and GFS:

`0 / 20 / 40 / 50 / 70 / 85 / 100%`

The palette intentionally changes hue more strongly at 50% so users can
visually separate lower-cloud-cover and higher-cloud-cover areas instead of
having to infer them from small differences in one blue ramp.

Low cloud percentages also receive much lower raster opacity. This keeps nearly
clear areas close to the basemap while dense cloud remains visually prominent.

## 50% threshold

Forecast cloud layers draw a subtle 50% contour using interpolation along the
native browser grid cells. The line is a reading aid only; it does not create
new forecast information.

The legend shows the same threshold and all seven cloud breakpoints.

## Selected Place label

When a forecast cloud layer is active, the selected Place label appends the
sampled percentage, for example:

`不厭亭 · 16%`

Only the selected Place gets the value label to avoid map clutter.

## Display strength

The control is called **雲層顯示強度** on cloud layers rather than
`圖層透明度`.

At 100% display strength the forecast cloud overlay is capped at 78% opacity.
Roads, coastlines and basemap labels therefore remain visible.

Other weather layers keep their own rendering behavior and use the generic
**圖層顯示強度** label.

## Guardrails

- no forecast values are changed;
- no forecast interpolation values are changed;
- Himawari-9 observed cloud mask / cloud-top height keep their B158 palettes, nearest-neighbour rendering, and observation semantics; the 50% forecast contour never applies to them;
- no provider-selection policy is changed;
- no source data or coverage geometry is changed;
- no Photography Opportunity scoring is changed;
- the change is browser presentation only.

## Regression requirements

CI asserts the shared breakpoint contract, explicit 50% hinge, 50% contour,
selected-Place cloud value, cloud opacity cap, dynamic display-strength label,
and cloud legend styling.
