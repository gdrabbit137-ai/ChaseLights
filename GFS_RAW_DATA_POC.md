# GFS Raw Data POC

## Goal

Prove that ChaseLights can ingest global numerical-weather-model raw data directly, render its own weather layers, and keep that path independent from the existing production scoring engine.

The current POC covers:

1. NOAA/NCEP GFS 0.25° GRIB2
2. Taiwan regional subset
3. Low-cloud cover (`LCDC`) on the GFS low-cloud layer
4. Coastline / border / Natural Earth admin-1 reference context when Cartopy data is available
5. Active ChaseLights Place coordinates
6. Nearest-grid low-cloud values for every Place
7. A consistent GFS run across multiple forecast hours
8. Per-frame JSON + PNG, a manifest, and a per-Place time-series JSON

No production score or Photography Opportunity logic is changed by this POC.

## Why GFS first

GFS is global, open, documented, and available through NOAA NOMADS. NOMADS Grib Filter supports coordinate-based regional and variable subsetting, so ChaseLights does not need to download complete global model files.

The request is deliberately narrow:

- `LCDC`
- `low cloud layer`
- Taiwan bounding box: 117.5–123.5°E, 20.5–26.75°N

## Series behavior

The default manual run requests:

```text
f000, f003, f006, f009, f012, f015, f018, f021, f024
```

The POC first checks the furthest requested forecast hour to choose a model cycle that is fully published. All earlier frames then come from that exact same date/cycle. This prevents a visual sequence from accidentally mixing different GFS runs.

Each frame records both:

- model cycle time
- valid forecast time

That distinction is required for later forecast-revision replay.

## Place sampling

B115 live validation confirmed that the 0.25° grid is spatially coarse for point decisions in Taiwan: the reference f000–f024 artifact had an average nearest-cell distance of about 10.3 km and a maximum of about 17.1 km across the active Place set.

B116 therefore keeps **two** values for every Place:

- `low_cloud_percent_nearest`: the raw nearest GFS cell, retained as the audit/reference value
- `low_cloud_percent_bilinear`: bilinear interpolation from the surrounding four cells, used only as the POC display/sample value

Interpolation smooths grid-cell boundaries; it does **not** create higher-resolution weather or solve mountain/coast microclimate limitations.

For each active Taiwan Place, the POC stores the nearest GFS grid-cell value plus trace metadata:

```json
{
  "low_cloud_percent": 42.5,
  "grid_lat": 24.0,
  "grid_lon": 121.75,
  "grid_distance_km": 7.8,
  "grid_row": 11,
  "grid_col": 17
}
```

This is intentionally `nearest_grid_cell` rather than interpolation for the POC. The raw sampled cell stays traceable and easy to verify. Bilinear interpolation can be evaluated later.

## Geographic rendering

The PNG renderer uses a Plate Carrée map when Cartopy is available and adds:

- Natural Earth 10m coastline
- national-border reference lines
- Natural Earth admin-1 reference lines
- all active ChaseLights Taiwan Place markers
- selected Place labels with their sampled low-cloud percentage

Administrative lines are map reference context only and are not a weather-data source or a scoring input.

If geographic context cannot be loaded, the renderer falls back to plain longitude/latitude axes rather than blocking the raw-data pipeline.

## Files

- `gfs_raw_poc.py`
  - chooses a recent GFS cycle
  - builds NOMADS Grib Filter URLs
  - downloads regional GRIB2 subsets
  - validates GRIB payloads
  - extracts low-cloud cover using cfgrib/ecCodes
  - samples every active Taiwan Place
  - exports per-frame JSON
  - renders per-frame PNG
  - writes a manifest and Place time series

- `test_gfs_raw_poc.py`
  - offline contract tests
  - validates naming/cycles/bbox/request shape
  - validates forecast-hour parsing and valid time
  - validates deterministic nearest-grid sampling

- `.github/workflows/b113_gfs_raw_poc.yml`
  - PR: offline contract tests only
  - manual workflow dispatch: real NOAA fetch + multi-hour rendering

## Running locally

Dry run:

```bash
python gfs_raw_poc.py --dry-run
```

Real multi-hour POC:

```bash
python -m pip install requests xarray cfgrib eccodes numpy matplotlib cartopy
python gfs_raw_poc.py \
  --forecast-hours 0,3,6,9,12,15,18,21,24 \
  --output-dir gfs_poc_output
```

A single-hour run remains supported for backward compatibility:

```bash
python gfs_raw_poc.py --forecast-hour 0 --output-dir gfs_poc_output
```

## Expected outputs

```text
gfs_poc_output/
  gfs_tw_low_cloud_f000.grib2
  gfs_tw_low_cloud_f000.json
  gfs_tw_low_cloud_f000.png
  ...
  gfs_tw_low_cloud_f024.grib2
  gfs_tw_low_cloud_f024.json
  gfs_tw_low_cloud_f024.png
  gfs_tw_low_cloud_manifest.json
  gfs_tw_low_cloud_spot_series.json
  gfs_tw_low_cloud_sampling_audit.json
```

The manifest lists the exact cycle and valid time of every frame. The spot-series file reorganizes the frame data by Place so a future browser UI can draw a timeline without re-reading all grid files.

## Guardrails

- This POC does not feed production scoring.
- Live network fetches are manual only.
- Automatic PR tests do not contact NOAA.
- The code requests regional/variable subsets instead of full global GFS files.
- Frames in one series always use one GFS cycle.
- Generated artifacts are not committed to the repository.
- Nearest-cell and bilinear values are both retained; interpolation never masquerades as higher model resolution.
- Generated validation PNG labels use ASCII Place IDs so CI runners do not require bundled CJK fonts.

## Next stages

After multi-hour map validation:

1. add mid/high cloud, precipitation, wind and visibility
2. compare nearest-cell and bilinear sampling against existing point forecasts and field snapshots
3. generate compact browser map layers or tiles
4. add a ChaseLights weather-map viewer centered on a selected Place
5. preserve model/run history for replay and forecast-revision comparison
6. place GFS behind a common WeatherGrid provider interface
7. add ECMWF/ICON comparison
8. only after field validation, evaluate whether raw-grid data should modify Opportunity confidence/scoring
