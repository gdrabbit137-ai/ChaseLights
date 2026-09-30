# B158 — Himawari-9 observed WeatherGrid UI

## Goal

Expose the B157 Himawari-9 Taiwan observation bundle in the public WeatherGrid
without mixing satellite observations with forecast-model cloud layers.

## User-facing model

WeatherGrid now has a top-level data-mode switch:

- **Forecast** — existing JMA MSM / CWA WRF / ICON Global / GFS behavior.
- **Satellite observed · Himawari-9** — current observed cloud mask and
  cloud-top height.

Himawari-9 is intentionally **not** another option in the forecast-model
selector.

## Observation layers

### Observed cloud mask

- source field: `observed_cloud_mask`
- semantics: categorical, 0 = clear, 1 = cloudy
- source product: `CloudMaskBinaryAWIPS`
- presentation: nearest-neighbour only

It must never be relabeled as low/mid/high cloud percentage.

### Cloud-top height

- source field: `cloud_top_height_m`
- source product: `CldTopHghtAWIPS`
- browser encoding is decoded with its declared scale
- missing/no-successful-retrieval cells remain missing
- presentation and point sampling use nearest-neighbour only

The source bundle uses NOAA parallax-corrected geolocation for cloud-top
height when available.

## Time semantics

Observation mode has one current snapshot rather than a forecast timeline.

The UI displays:

- observation end time in Asia/Taipei
- observation age
- disabled previous/next/slider controls
- a disabled **single observation** play control

Forecast mode keeps the existing multi-frame navigator unchanged.

## QC

The inspector exposes the published B157 QC rather than forecast QC flags:

- nearest-neighbour p99 and maximum distance
- count beyond the 5 km gate
- observed cloud fraction for the cloud-mask layer
- successful cloud-top retrieval count, with remaining cells explicitly
  described as missing

B157's fail-closed freshness gate remains authoritative; if the public
Himawari bundle is absent, the observation mode is disabled instead of showing
stale/demo satellite data.

## Guardrails

- no Photography Opportunity scoring changes
- no forecast provider-selection changes
- no conversion of satellite observations into low/mid/high forecast cloud
- no bilinear interpolation of categorical cloud mask or cloud-top retrievals
- Place / Camera / Subject / Environment coverage remains available as an
  independent geographic overlay

## Validation

B158 adds an offline UI contract to B117 CI and extends the deployed B145
browser smoke to exercise the observation mode whenever the fail-closed
Himawari bundle is currently available.

The production smoke verifies:

- separate data-mode selector
- Himawari source state
- observed-cloud-mask and cloud-top-height layers
- single-observation time semantics
- model selector disabled during observation mode
- B158 debug source kind and Himawari availability
- observation QC text

## Follow-up

After B158 is stable, the next useful batch is a visual/performance pass for
satellite display, including panning/zooming behavior on the 276 × 301
presentation grid and an optional forecast-vs-observation comparison workflow.
