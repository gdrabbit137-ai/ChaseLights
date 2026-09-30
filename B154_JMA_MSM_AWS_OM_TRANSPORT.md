# B154 — JMA MSM AWS Open Data OM transport

## Goal

Replace the paid/rate-limited Open-Meteo Forecast API transport introduced in
B153 with direct anonymous reads from the public Open-Meteo AWS Open Data
bucket, while keeping the JMA MSM WeatherGrid schema and UI stable.

## Source

- model/provider: Japan Meteorological Agency (JMA) MSM
- transport/distribution: Open-Meteo AWS Open Data
- bucket: `s3://openmeteo`, region `us-west-2`
- layout: `data_spatial/jma_msm/<run>/<valid-time>.om`
- subscription/API key: none
- OM reader: `omfiles` 1.x + anonymous `s3fs` / `fsspec`

The AWS distribution is a transport mirror. It does not change the
meteorological identity of the data.

## Native JMA MSM grid

Open-Meteo's JMA ingest implementation defines MSM surface data as:

- 481 × 505 cells
- longitude origin 120°E, dx = 0.0625°
- latitude origin 22.4°N, dy = 0.05°
- hourly forecast output
- model refresh every 3 hours
- standard runs through f039
- 00/12 UTC extended runs through f078

The initial ChaseLights Taiwan browser window remains:

- 120.0625–122.5°E
- 22.45–25.6°N
- 40 × 64 native cells = 2,560 cells

No spatial interpolation is performed while ingesting the OM files.

## Cloud fields

Each spatial OM file is read for the native arrays:

- `cloud_cover` → `total_cloud_percent`
- `cloud_cover_low` → `low_cloud_percent`
- `cloud_cover_mid` → `mid_cloud_percent`
- `cloud_cover_high` → `high_cloud_percent`

JMA low/mid/high vertical-definition metadata from B153 is preserved.

## Cycle and timeline improvement

Unlike the point Forecast API adapter, `data_spatial/jma_msm/latest.json`
exposes the model `reference_time` and native `valid_times`.

B154 therefore changes JMA provenance to:

- `forecast_hour_semantics = hours_from_model_cycle`
- `cycle_timestamp_available = true`

The UI can show real JMA `fNNN` lead times instead of the previous
`+Nh · API 發布時間軸` label.

## Production behavior

`Update JMA MSM WeatherGrid` remains provider-owned on a 3-hour cadence.
It now installs `omfiles`, `fsspec`, and `s3fs`, reads AWS anonymously,
builds the existing compact browser/QC artifacts, and publishes only those
compact files.

No `OPEN_METEO_API_KEY` is read by the workflow.

If the current AWS refresh fails, stale JMA browser files are removed, retaining
the B153 fail-closed behavior.

## Validation gates

Before merge:

1. Offline tests verify exact native-grid index mapping and S3 URI construction.
2. B117 live smoke reads a 3×3 native Taiwan subset from real AWS OM files for
   four native hourly valid times.
3. Browser bundle tests verify AWS provenance survives compaction.
4. UI tests verify true `fNNN` labels and Open-Meteo AWS attribution.
5. Existing B30/B145 contracts remain green.

After merge, the first provider workflow must publish the full 64×40 / 40-hour
snapshot and B145 must select JMA on the public site.
