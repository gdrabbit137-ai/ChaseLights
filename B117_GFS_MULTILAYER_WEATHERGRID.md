# B117 GFS Multi-layer WeatherGrid POC

## Goal

Extend the validated B113–B116 raw-data path from one low-cloud layer into a small photography-oriented WeatherGrid while keeping the experiment isolated from production scoring.

The first multi-layer set is:

- low cloud cover
- middle cloud cover
- high cloud cover
- surface visibility
- surface precipitation rate
- 10 m wind U/V
- derived 10 m wind speed and meteorological direction

The official NOAA/NCEP GFS 0.25° NOMADS filter exposes these variables and the required cloud/surface/10 m levels, so ChaseLights can request a small Taiwan subset instead of downloading the full global file.

## Request

The POC requests these GRIB2 variables:

```text
LCDC
MCDC
HCDC
VIS
PRATE
UGRD
VGRD
```

and these levels:

```text
low cloud layer
middle cloud layer
high cloud layer
surface
10 m above ground
```

The geographic subset remains:

```text
117.5–123.5°E
20.5–26.75°N
```

## Normalized WeatherGrid units

The browser-facing JSON normalizes fields to:

- cloud cover: %
- visibility: km
- precipitation rate: mm/h
- wind components/speed: m/s
- wind direction: degrees, meteorological convention

Source GRIB units remain attached to each field for traceability.

## Sampling

Every active Taiwan Place is sampled from the same model frame.

For scalar fields the POC stores:

- bilinear value for the display/sample value
- nearest-cell value as the raw audit reference
- difference between the two

For wind, U/V are bilinearly sampled first and then speed/direction are derived. This avoids interpolating circular wind-direction degrees directly.

The existing B116 guardrail still applies: bilinear interpolation smooths a 0.25° grid but does not create higher-resolution mountain/coast weather.

## Output

For each forecast hour:

```text
gfs_tw_weather_f000.grib2
gfs_tw_weather_f000.json
gfs_tw_weather_f000.png
...
```

The PNG is a six-panel validation overview:

1. low cloud
2. middle cloud
3. high cloud
4. visibility
5. precipitation rate
6. 10 m wind speed + vectors

The run also writes:

```text
gfs_tw_weather_manifest.json
gfs_tw_weather_spot_series.json
```

The spot-series artifact is shaped for a future Place detail chart without requiring the browser to decode GRIB2.

## Workflow

PR checks are offline only.

Manual live validation:

> Actions → B117 GFS Multilayer POC → Run workflow

Default forecast hours:

```text
0,3,6,9,12
```

This keeps the first live multi-variable run small enough to inspect before extending to 24–72 hours.

## Coverage extent contract

WeatherGrid geographic extent is governed by `WEATHERGRID_COVERAGE_SPEC_R4_2.md`.

A Place/Opportunity map must not be framed from the Place center alone. Subject-aware views must contain all researched Camera Zones plus the photographed Subject/Environment Geometry for the selected Opportunity; Place-level views use the union across all active researched Opportunities at that Place. Provider fetch bounds must also include the sampling/interpolation halo required by the source grid.

## Guardrails

- no production score changes
- no Opportunity logic changes
- no automatic scheduled NOAA traffic yet
- one GFS cycle per time series
- raw/source field metadata retained
- GFS remains a coarse synoptic layer, not a replacement for higher-resolution local guidance

## Next stage after live validation

If the required fields decode correctly and the maps align:

1. inspect each field against current point forecasts at a small set of Places
2. decide which raw layers are useful enough for the browser
3. build compact browser map-layer JSON or tiles
4. add a Weather Map entry in ChaseLights
5. preserve run history for forecast-revision replay
6. then evaluate higher-resolution providers/models for local mountain/coast decisions
