# B148 WeatherGrid Wind Vectors

Date: 2026-09-30

## Goal

Add an interpretable 10 m wind-vector overlay to the browser WeatherGrid while
preserving the existing scalar wind-speed and meteorological-direction fields.

## Data contract

B117 already publishes:

- `wind_speed_10m_m_s`
- `wind_direction_10m_deg`

The direction uses meteorological convention: it reports the direction the wind
is **coming from**.

The browser arrow is intentionally drawn toward the air-motion direction:

```text
arrow bearing = meteorological direction + 180°
```

The numeric wind-direction readout remains unchanged and continues to mean
"coming from".

## UI behavior

The "目前圖層" inspector adds a `顯示 10 m 風向箭頭` toggle.

Default page load keeps vectors off so the low-cloud overview remains clean.

When the user first selects either wind-speed or wind-direction as the active
layer, vectors automatically turn on. After the user manually touches the
toggle, that explicit preference is preserved while switching layers.

This also allows wind vectors to be overlaid on cloud, visibility or
precipitation when desired.

## Density

Vector density adapts to map zoom:

- zoom < 6.4: every third GFS grid point;
- 6.4 <= zoom < 8: every second grid point;
- zoom >= 8: every grid point in the visible viewport.

Cells below 0.5 m/s are omitted to avoid meaningless direction arrows near
calm conditions.

Arrow length increases modestly with wind speed. A dark halo plus pale inner
stroke keeps vectors readable over both the cartographic basemap and weather
fills.

## Layer order

Vectors are drawn:

1. above WeatherGrid scalar cells;
2. below Camera / Subject / Environment coverage geometry;
3. below Place markers.

Photography geometry therefore remains visually authoritative.

## Production validation

The production smoke now switches to the 10 m wind-speed layer, verifies that
wind vectors auto-enable, selects the known `tw-073` coverage, and captures
that state in the screenshot artifact.

The CI screenshot environment also installs Noto CJK fonts so Traditional
Chinese UI labels are readable in the diagnostic artifact.

## Guardrails

- no GFS fetch changes;
- no wind-value changes;
- no scoring changes;
- no coverage geometry changes;
- arrows are presentation-only;
- direction readout remains meteorological "from".
