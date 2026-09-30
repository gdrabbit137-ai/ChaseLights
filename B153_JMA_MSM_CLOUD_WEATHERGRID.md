# B153 — JMA MSM 5 km cloud WeatherGrid

Date: 2026-09-30

## Scope

Add exactly one new forecast model to WeatherGrid: **JMA MSM 5 km**.

This batch is intentionally limited to JMA MSM.  JMA LFM and Himawari are
deferred to later batches so each source can be verified independently.

## Why MSM first

JMA's official MSM surface GPV publishes native:

- total cloud cover;
- low cloud cover;
- middle cloud cover;
- high cloud cover.

The surface grid is 0.05° latitude × 0.0625° longitude (about 5 km), with
hourly output.  Normal runs cover about 39 hours; 00/12 UTC runs extend to
78 hours.

Official MSM surface domain:

- 22.4°N–47.6°N
- 120°E–150°E

The official model domain starts at 22.4°N / 120.0°E.  The initial
ChaseLights browser subset is intentionally inset by one native grid cell from
the south/west edge because the current HTTP transport adapter can reject exact
boundary coordinates:

- 22.45°N–25.6°N
- 120.0625°E–122.5°E

This still covers most of Taiwan's main island, but it deliberately does not
pretend the transport-safe browser product covers the official edge itself.
Southern locations below 22.45°N and islands west of 120.0625°E are outside
this initial browser artifact.

## Transport

The operational JMA GRIB2 feed is distributed through the Japan Meteorological
Business Support Center.  B153 uses the Open-Meteo JMA API as the initial
transport adapter for the native JMA MSM cloud fields.

Provider identity and transport identity are kept separate:

- model/provider: JMA MSM
- transport adapter: Open-Meteo JMA API

Requests use:

- model = `jma_msm`;
- `cell_selection=nearest`;
- one `elevation=nan` value per requested coordinate to disable elevation
  downscaling.

This preserves the model-grid cloud quantity rather than asking Open-Meteo to
statistically adjust the forecast to a terrain elevation.

## Cloud vertical definitions

JMA does not use the same low/mid/high pressure boundaries as ICON or GFS.

JMA's cloud post-processing derives layer boundaries from surface pressure:

- low/mid boundary = surface pressure × 0.85;
- mid/high boundary = the smaller of low/mid × 0.8 and 500 hPa.

At a representative 1000 hPa surface pressure this is approximately:

- low cloud: surface–850 hPa, roughly ground–1.5 km in a standard atmosphere;
- middle cloud: 850–500 hPa, roughly 1.5–5.6 km;
- high cloud: above the 500 hPa boundary, roughly above 5.6 km.

The pressure rule is authoritative.  Height text in the UI is explanatory only.

## Browser product

B153 publishes:

- `weathergrid/jma_msm_tw_cloud_browser.json`
- `weathergrid/jma_msm_tw_cloud_qc.json`

Fields:

- `total_cloud_percent`
- `low_cloud_percent`
- `mid_cloud_percent`
- `high_cloud_percent`

The initial scheduled browser timeline publishes 40 hourly timestamps
(current hour through roughly +39 h).  This matches the standard MSM horizon
without depending on whether the latest upstream run is one of the 00/12 UTC
extended cycles.

The Open-Meteo transport does not expose the exact upstream JMA cycle timestamp
in this response contract.  Therefore the browser's `forecast_hour` field is a
published-window offset from the first valid time, **not** an asserted JMA model
lead time.  The UI labels it as `+Nh · API 發布時間軸` instead of `fNNN`.

## UI policy

JMA MSM is manually selectable as **JMA MSM 5 km**.

When selected:

- JMA owns the map boundary;
- JMA owns the hourly timeline;
- JMA owns the available layer list;
- JMA's vertical definitions are shown in the inspector.

B153 deliberately does **not** change Auto mode.  Auto continues to use the
existing ICON-cloud-first / GFS-fallback policy until JMA MSM has been observed
in production and an explicit provider-selection policy is approved.

## Guardrails

1. Do not spatially blend JMA, ICON and GFS cloud percentages.
2. Do not normalize low/mid/high cloud into one artificial common layer.
3. Preserve the native vertical definition with every cloud field.
4. Do not extend JMA outside 22.4°N–47.6°N / 120°E–150°E.
5. Display interpolation does not increase JMA's ~5 km meteorological
   resolution.
6. If JMA refresh fails, remove stale JMA browser files rather than keep an old
   run selectable.

## Validation

PR validation includes:

- offline provider tests;
- browser-bundle tests;
- WeatherGrid UI contract tests;
- a live JMA MSM API smoke test using a 3×3 interior native-grid subset;
- existing B30 browser smoke;
- scheduled-refresh contract tests.


## Production transport guardrail

A full native-grid Taiwan snapshot contains 2,560 locations.  The Open-Meteo
free endpoint is suitable for evaluation/small live smoke tests, but it has
minutely/daily limits and is not a production transport for this payload.

B153 therefore refuses production-sized free-endpoint requests.  The scheduled
publisher requires `OPEN_METEO_API_KEY` and automatically switches to
`customer-api.open-meteo.com`.  CI still uses the free endpoint only for a
small interior sample.

This keeps the model integration testable without silently relying on a free
service beyond its intended limits.  A future official JMBSC adapter can replace
the transport without changing the JMA MSM browser schema.


## Deployment checklist

Before B153 can publish the full 5 km JMA MSM layer on the public site:

1. Configure the repository Actions secret `OPEN_METEO_API_KEY` with a
   production-capable Open-Meteo customer API key.
2. Merge B153 to `main`.
3. `Update JMA MSM WeatherGrid` runs on the provider's own 3-hour cadence
   and on provider-code pushes.
4. The workflow publishes only the compact browser/QC artifacts.
5. The JMA data commit intentionally does not use `[skip ci]`; B145 then
   validates the deployed public WeatherGrid and, when JMA is available,
   selects JMA MSM and verifies total/low/mid/high cloud layers.
6. If the production JMA refresh fails, stale JMA browser files are removed
   so the model selector cannot silently serve an old run.

The secret value itself must never be committed to the repository.
