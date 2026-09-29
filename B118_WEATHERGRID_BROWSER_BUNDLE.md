# B118 WeatherGrid Browser Bundle

## Purpose

B117 proved that ChaseLights can decode multiple GFS weather layers from raw GRIB2. B118 prepares those decoded layers for a future browser map without making the browser parse GRIB2 or carry unnecessary floating-point precision.

This batch is still validation-only and does not change production scoring or the public UI.

## Inputs

B118 consumes the existing B117 output directory:

- `gfs_tw_weather_manifest.json`
- per-frame `gfs_tw_weather_fXXX.json`

It does not fetch NOAA data itself.

## Browser bundle

The new file:

```text
gfs_tw_weather_browser.json
```

contains:

- model/provider/cycle metadata
- Taiwan bounding box
- one shared latitude/longitude grid
- active ChaseLights Place coordinates
- forecast frames
- compact encoded arrays for:
  - low cloud
  - middle cloud
  - high cloud
  - visibility
  - precipitation rate
  - 10 m wind speed
  - 10 m wind direction

Fields use simple integer scaling rather than full floating-point JSON:

| Field | Browser step |
| --- | --- |
| Cloud cover | 1 % |
| Visibility | 0.1 km |
| Precipitation rate | 0.01 mm/h |
| Wind speed | 0.1 m/s |
| Wind direction | 1 degree |

The bundle includes the scale needed to decode each array.

## QC report

The new file:

```text
gfs_tw_weather_qc.json
```

checks each frame for:

- missing values
- constant fields
- near-constant fields
- visibility fields dominated by a common ceiling
- coordinate-grid consistency
- expected cell counts
- stable Place set/order

QC flags are diagnostics, not automatic rejection rules.

This matters because the first B117 live run showed a realistic example: some clear-air GFS visibility frames saturate around the model's upper visibility value. That is useful data behavior to expose rather than silently treating every repeated maximum as highly precise local visibility.

## Workflow

The existing **B117 GFS Multilayer POC** workflow now does:

```text
NOAA GFS GRIB2
  -> B117 decode/render
  -> B118 browser bundle
  -> B118 QC report
  -> GitHub Actions artifact
```

PR runs remain offline contract tests only.

## Coverage extent contract

WeatherGrid geographic extent is governed by `WEATHERGRID_COVERAGE_SPEC_R4_2.md`.

A Place/Opportunity map must not be framed from the Place center alone. Subject-aware views must contain all researched Camera Zones plus the photographed Subject/Environment Geometry for the selected Opportunity; Place-level views use the union across all active researched Opportunities at that Place. Provider fetch bounds must also include the sampling/interpolation halo required by the source grid.

## Guardrails

- no production score changes
- no public UI changes
- no scheduled NOAA traffic
- source frame JSON remains available for audit
- browser quantization is presentation/storage precision only
- GFS 0.25 degree remains a coarse synoptic model layer

## Next step

After one successful B118 live artifact:

1. verify the compact bundle matches source frame values within its declared quantization step
2. build a standalone ChaseLights WeatherGrid preview viewer
3. add time slider + layer selector + Place centering
4. only after UI validation decide whether to publish the WeatherGrid feed on a schedule
