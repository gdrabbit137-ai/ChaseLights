# B156 WeatherGrid UI Polish

Date: 2026-10-01

## Goal

Turn the WeatherGrid browser from an engineering-preview layout into a clearer
photography-facing weather map without changing forecast values, model
selection policy, Photography Opportunity scoring, or provider fetch behavior.

## Changes

### Responsive controls

The control bar now uses a three-column responsive grid with explicit
`min-width: 0` guards. Long Place/Opportunity selectors therefore stay inside
the map panel instead of overlapping the inspector.

### Unified forecast-time navigation

The duplicated top slider and bottom button strip are replaced by one navigator:

- previous frame;
- forecast-time slider;
- next frame;
- play/pause.

The visible timestamp is Taiwan local time and shows forecast lead as `+Nh`.
Model cycle metadata is also shown in Taiwan local time instead of raw UTC ISO.

### Layer-aware wind vectors

Before the user manually touches the wind-vector toggle:

- wind speed / wind direction layers automatically show vectors;
- cloud / rain / visibility and other scalar layers keep vectors off.

After an explicit toggle action, the user's choice is preserved across layers.

### Circular wind-direction interpolation

Direction degrees are never interpolated as ordinary scalar numbers.
The browser converts meteorological direction plus wind speed to `u/v`,
bilinearly interpolates the vectors, then converts back to meteorological
"from" direction.

This keeps 359° and 1° close to north rather than producing a false 180°
southerly interpolation. The direction palette and legend are explicitly
cyclic, with 0° and 360° both represented as north.

### Rain-rate readability

Hourly precipitation uses a nonlinear threshold scale:

`0 / 0.1 / 0.5 / 1 / 2 / 5 / 10 / 20 mm/h`

This preserves cross-time comparability while making light rain visible.

### Place-marker decluttering

Low zoom levels cluster nearby Place markers. Individual unselected markers are
smaller and partially transparent; the selected Place remains visually
dominant. Clicking a cluster zooms toward its member locations.

### Inspector and QC wording

The inspector now leads with layer identity and model/vertical metadata. Raw
min/max values move to a secondary "畫面資料範圍" line.

Known internal QC flags are translated into user-facing explanations while the
technical flag remains available as a small diagnostic code.

### Provider boundary

A subtle dashed outline marks the active model's data bbox so unpainted areas
are not mistaken for valid clear weather.

## Guardrails

- no forecast values are changed;
- no model auto-selection policy is changed;
- no provider/fetch pipeline is changed;
- no Photography Opportunity score is changed;
- no coverage geometry is changed;
- rendering changes are browser-only.

## Regression requirements

CI verifies responsive containment, unified time navigation, layer-aware vector
defaults, u/v circular interpolation, cyclic direction legend, nonlinear rain
scale, low-zoom marker clustering, user-facing QC text, local-time cycle labels,
and provider-boundary rendering.
