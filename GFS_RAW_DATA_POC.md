# GFS Raw Data POC

## Goal

Prove that ChaseLights can ingest global numerical-weather-model raw data directly, render its own weather layer, and keep that path independent from the existing production scoring engine.

The first POC is intentionally narrow:

1. NOAA/NCEP GFS 0.25° GRIB2
2. Taiwan regional subset
3. Low-cloud cover only
4. ChaseLights active Place coordinates overlaid
5. Outputs a GRIB2 file, a browser-friendly JSON grid, and a PNG rendering

No production score or Opportunity logic is changed in this batch.

## Why GFS first

GFS is global, open, documented, and available through NOAA NOMADS. NOMADS Grib Filter supports coordinate-based regional subsetting so ChaseLights does not need to download the full global GRIB2 file.

The POC requests only:

- `TCDC`
- `low cloud layer`
- Taiwan bounding box: 117.5–123.5°E, 20.5–26.75°N

This keeps the download small enough for repeatable development.

## Files

- `gfs_raw_poc.py`
  - chooses a recent GFS cycle
  - builds the NOMADS Grib Filter URL
  - downloads a regional GRIB2 subset
  - validates the response begins with the GRIB signature
  - extracts low-cloud cover using cfgrib/ecCodes
  - exports JSON
  - renders PNG
  - overlays active Taiwan ChaseLights Places

- `test_gfs_raw_poc.py`
  - offline tests only
  - validates file naming, cycles, bbox and NOMADS query contract
  - does not consume NOAA network capacity

- `.github/workflows/b113_gfs_raw_poc.yml`
  - PR: runs offline contract tests
  - manual workflow dispatch: performs a real GFS download/render and uploads the result as a GitHub Actions artifact

## Running locally

Dry run, no network fetch:

```bash
python gfs_raw_poc.py --dry-run
```

Real POC:

```bash
python -m pip install requests xarray cfgrib eccodes numpy matplotlib
python gfs_raw_poc.py --forecast-hour 0 --output-dir gfs_poc_output
```

Expected outputs:

```text
gfs_poc_output/
  gfs_tw_low_cloud.grib2
  gfs_tw_low_cloud.json
  gfs_tw_low_cloud.png
```

## Data contract

The JSON output contains:

- provider
- model
- run date/cycle/forecast hour
- bbox
- source URL
- decoded field metadata
- latitude coordinates
- longitude coordinates
- low-cloud percentage grid
- active ChaseLights Taiwan Place coordinates

This gives the next stage a stable intermediate format without making the browser parse GRIB2 directly.

## Guardrails

- This POC does not feed production scoring.
- Live network fetches are manual only.
- Automatic PR tests do not contact NOAA.
- Candidate-run retries wait 10 seconds between NOMADS requests.
- The code requests a regional/variable subset instead of full global GFS files.
- Generated artifacts are not committed to the repository.

## Next stage after validation

If the live artifact verifies that GFS low-cloud positioning is correct:

1. add additional layers: mid/high cloud, precipitation, wind and visibility
2. generate compact map tiles or grid chunks suitable for the browser
3. add a ChaseLights weather-map viewer centered on a selected Place
4. support model/run replay
5. compare GFS with ECMWF/ICON behind a common WeatherGrid provider interface
6. only after validation, evaluate whether model-grid data should influence Opportunity confidence/scoring
