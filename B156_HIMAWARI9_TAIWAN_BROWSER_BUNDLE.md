# B156 — Himawari-9 Taiwan browser bundle

## Goal

Convert the proven B155 anonymous Himawari-9 Taiwan range-read into a compact
regular lon/lat browser artifact.

This batch is still **observation-only**. It does not change Photography
Opportunity scoring and it does not pretend satellite cloud-top height is a
forecast low/mid/high cloud-cover layer.

## Source path

```text
JMA Himawari-9 / AHI
  -> NOAA NODD AWS Open Data
  -> same-slot AHI-CMSK + AHI-CHGT
  -> fixed 5500 x 5500 Full Disk
  -> B155 Taiwan range-read (~0.32% of Full Disk pixels)
  -> B156 regular Taiwan browser grid
```

No AWS account, API key or paid weather subscription is required.

## Browser grid

B156 publishes a regular geographic grid covering:

- longitude: 118.0–124.0 E
- latitude: 21.5–27.0 N
- step: 0.02 degrees

This is a presentation grid. It does not claim that 0.02 degree spacing
increases the native satellite resolution beyond roughly 2 km at nadir.

## Fields

### `observed_cloud_mask`

- source: `CloudMaskBinaryAWIPS`
- categories: 0 clear / 1 cloudy
- nearest-neighbour resampling
- source geolocation: `Latitude` / `Longitude`

### `cloud_top_height_m`

- source: `CldTopHghtAWIPS`
- browser encoding: 100 m integer step
- missing means no successful cloud-top retrieval
- nearest-neighbour resampling
- source geolocation: `Latitude_Pc` / `Longitude_Pc` when available
- the `_Pc` coordinates are parallax-corrected and are preferred for high
  cloud placement

## Semantic guardrail

Cloud-top height identifies the retrieved top of an observed cloud pixel. It
cannot prove that lower cloud layers do or do not exist below that cloud top.

Therefore B156 does **not** label satellite data as forecast:

- low cloud %
- middle cloud %
- high cloud %

Those remain model-specific forecast diagnostics (GFS/ICON/JMA MSM).

## Outputs

Live CI writes:

- `himawari9_tw_cloud_browser.json`
- `himawari9_tw_cloud_qc.json`

The QC report records source object paths/sizes, HDF5 chunking, target-grid
nearest-neighbour distances, missing counts, cloud fraction, and height
statistics.

## Next step

After the live artifact is proven:

1. schedule the Himawari Taiwan bundle refresh at an appropriate cadence;
2. publish the current snapshot under `weathergrid/`;
3. add a separate **Observed / Himawari-9** source mode to WeatherGrid;
4. keep observation time/age visually distinct from forecast cycle/lead time.
