# B151 CWA WRF 3 km WeatherGrid

Date: 2026-09-30

## Scope

This batch adds exactly one new numerical-weather source: Taiwan Central Weather
Administration (CWA) WRF 3 km.

No additional external model is added in B151. After CWA is verified and
published, the next model can be chosen separately.

The existing sources remain:

- ICON Global: cloud-focused global source
- GFS 0.25 degree: global fallback / broader fields
- CWA WRF 3 km: new manually selectable Taiwan regional source

B151 does not change photography-opportunity scoring.

## Why CWA WRF 3 km

The official CWA product documentation describes the regional WRF domain as:

- model: WRF regional forecast model
- high-resolution domain: 3 km
- grid: 1158 x 673
- runs: 00 / 06 / 12 / 18 UTC
- operational WRF_D model output: hourly through 126 hours
- public M-A0064 series integrated by ChaseLights: 000 through 084 hours
- public M-A0064 product interval used here: 6 hours
- reference first grid point: 105.2500 E / 14.02224 N
- reference final grid point: 140.91388 E / 32.12021 N

The same documentation lists useful near-surface variables including:

- temperature at 2 m
- relative humidity at 2 m
- U/V wind at 10 m
- total precipitation
- net shortwave solar flux at the surface

These fields complement rather than replace the current ICON/GFS strengths.

Official references:

- CWA WRF product documentation:
  https://www.cwa.gov.tw/Data/data_catalog/7-2-1.pdf
- CWA numerical-model open-data documentation:
  https://opendata.cwa.gov.tw/opendatadoc/Model/M-A0061.pdf
- CWA Open Data on AWS:
  https://registry.opendata.aws/cwa_opendata/

## Download policy

The provider uses dataset IDs M-A0064-000 through M-A0064-084 at six-hour
increments.

Primary transport is the official public AWS Open Data bucket:

- bucket: cwaopendata
- region: ap-northeast-1
- unsigned/public access

The downloader tries the historically documented MIC layout first and retains
Model/ candidates because the AWS numerical-model announcement has also
described the products under that prefix.

A direct CWA public-file URL is retained as a compatibility fallback.

The refresh rejects a series if files cross a CWA model-cycle update while the
snapshot is being downloaded.

## Provider-owned boundary

CWA is not forced into the same browser bbox as GFS or ICON.

Initial CWA browser artifact bbox:

- west: 117.5 E
- east: 125.5 E
- south: 20.0 N
- north: 27.0 N

This covers Taiwan and nearby offshore-island catalog locations while staying
much smaller than the native regional WRF domain.

The bbox is provider-owned. It can be widened or moved later without changing
GFS or ICON.

## Provider-owned resolution

The CWA native model is a projected 3 km WRF grid, not the regular 0.25 degree
GFS grid.

B151 therefore uses:

1. native CWA projected-grid latitude/longitude coordinates decoded from GRIB2;
2. a local subset around the CWA browser bbox;
3. linear native-to-regular regridding;
4. nearest fill only at the interpolation hull edge;
5. a 0.03 degree browser interchange grid.

The browser-grid spacing is an interchange/rendering choice, not a claim that
the model has gained resolution. Provenance keeps native resolution = 3 km.

## Provider-owned time axis

CWA frames are not forced onto the existing GFS three-hour browser timeline.

The current CWA WRF_D product documentation says the operational model itself
produces hourly output through 126 h.  The public M-A0064 GRIB2 series integrated
in B151 is the narrower public product contract used by this provider: f000
through f084 at six-hour product steps.

CWA manual mode therefore reads its own frame list and slider:

- operational model output interval: 1 h
- operational model horizon: 126 h
- integrated public-product interval: 6 h
- integrated public-product horizon: f084
- initial scheduled browser snapshot: f000 / f006 / f012

The initial three-frame scheduled window is deliberately conservative because
each public CWA GRIB2 file contains a large regional model payload. The provider
already validates and accepts every native six-hour lead through f084, so the
published horizon can be expanded independently after download/runtime cost is
measured.

ICON and GFS keep their own timelines.

## Initial CWA fields

Required:

- temperature_2m_c
- relative_humidity_2m_percent
- wind_speed_10m_m_s
- wind_direction_10m_deg

Published when present across the full snapshot:

- precip_total_mm
- shortwave_flux_w_m2

The provider decodes U/V wind and derives:

- 10 m wind speed
- meteorological wind direction ("from" direction)

Browser arrows continue to point toward wind motion.

## UI behavior

WeatherGrid adds a model selector:

- Auto
- CWA WRF 3 km
- ICON Global
- GFS 0.25 degree

Auto intentionally preserves the B150 behavior for this batch:

- cloud layers: ICON when the exact GFS valid time exists in ICON
- otherwise: GFS

CWA is manually selectable first. This isolates the new provider for validation
before any automatic provider-ranking policy is changed.

When the user selects CWA:

- layer options change to fields CWA actually publishes;
- the time slider changes to CWA's six-hour frames;
- the map fits the CWA bbox;
- reset-view returns to the CWA bbox;
- source metadata shows 3 km native resolution and the six-hour public-product interval.

When the user selects ICON or GFS, each model similarly uses its own published
frame list and bbox.

## Sampling and interpolation

For scalar fields:

- browser rendering uses the regular provider grid;
- point sampling uses bilinear interpolation inside the provider bbox;
- points outside the provider bbox return no sample instead of clamping to the
  nearest edge.

Wind direction is circular and remains nearest-cell sampled/rendered rather than
linearly interpolated as degrees.

## Refresh and stale-data safety

The scheduled WeatherGrid workflow refreshes CWA independently with
continue-on-error.

If CWA succeeds:

- build cwa_wrf3_tw_weather_browser.json
- build cwa_wrf3_tw_weather_qc.json
- publish both under weathergrid/

If CWA fails:

- GFS / ICON publication can still succeed;
- old CWA browser/QC files are removed so the selector does not present a stale
  CWA run as current.

## Validation

Offline contracts verify:

- 3 km model resolution;
- 1 h / +126 h operational-model metadata;
- 6 h / +84 h public M-A0064 product contract;
- M-A0064 dataset IDs;
- provider-owned bbox and 0.03 degree browser grid;
- required CWA surface fields;
- compact bundle resolution/time provenance;
- model selector and provider-specific timeline/boundary behavior.

A pull-request live smoke additionally downloads one real f000 CWA frame,
decodes it, builds the compact browser bundle, and asserts the required
temperature, humidity and wind fields.

This live smoke is intentionally one frame so PR validation proves the real
source contract without downloading the entire regional forecast series.
