# B150 ICON Global Cloud Primary + GFS Fallback

Date: 2026-09-30

## Goal

Upgrade the WeatherGrid cloud visualization from GFS-only to a provider-aware
stack:

1. ICON Global is the preferred source for low / middle / high cloud cover.
2. GFS remains the automatic fallback when a matching ICON valid time is not
   published or the ICON refresh fails.
3. GFS remains the source for the existing visibility, precipitation and wind
   layers in this batch.
4. Both regular browser grids use spatial interpolation for display, while
   keeping native-model provenance visible.

This batch does not change Photography Opportunity scoring.

## Provider selection

The network-free resolver in weathergrid_model_resolver.py records the intended
global policy:

- ICON Global: preferred while the target valid time is inside an available
  ICON run.
- ICON 00Z / 12Z cycles: up to about +180 h.
- ICON 06Z / 18Z cycles: up to about +120 h.
- GFS: fallback and long-range coverage through +384 h.

The browser uses the same conservative principle. It selects an ICON cloud frame
only when the published ICON bundle contains the exact valid_time_utc shown by
the baseline timeline. Otherwise it renders the GFS frame for that time.

This prevents a model switch from silently shifting the forecast clock.

## ICON source and remapping

DWD distributes ICON Global forecast fields on the native R03B07 icosahedral
grid. ChaseLights downloads only these cloud parameters:

- CLCL: low cloud cover
- CLCM: middle cloud cover
- CLCH: high cloud cover

The source files are bzip2-compressed GRIB2 from DWD Open Data.

For browser use, the workflow follows DWD's documented conversion path and uses
the official ICON_GLOBAL2WORLD_0125_EASY package:

- target_grid_world_0125.txt
- weights_icogl2world_0125.nc

CDO remaps the native triangular field to a regular 0.125 degree lat/lon grid.
The Taiwan regional subset is written as a small NetCDF intermediary and then
converted to the same compact WeatherGrid field contract used by the browser.

The stable DWD remapping package is cached by GitHub Actions.

## Resolution and interpolation semantics

ICON provenance is retained as:

- native model: ICON Global R03B07
- native nominal resolution: about 13 km
- interchange/remap grid: 0.125 degree
- browser display interpolation: bilinear subcells

GFS provenance remains:

- native/output grid: 0.25 degree
- browser display interpolation: bilinear subcells

The browser currently renders approximately 0.0625 degree visual subcells:

- GFS 0.25 degree cells: 4 x 4 display subdivision
- ICON 0.125 degree cells: 2 x 2 display subdivision

This makes the overlay visually continuous without claiming that interpolation
creates new meteorological information. The UI explicitly says that display
interpolation does not increase the model's true forecast resolution.

Wind direction is circular data and is therefore excluded from linear
interpolation; it keeps nearest-cell rendering.

## Failure behavior

The scheduled WeatherGrid workflow always refreshes GFS first.

ICON refresh then runs with continue-on-error. If DWD download, decompression,
CDO remapping, decoding or bundle generation fails:

- the fresh GFS snapshot is still publishable;
- stale published ICON browser/QC files are removed;
- the browser immediately falls back to GFS instead of presenting old ICON
  data as current.

A successful ICON bundle must have at least one exact valid time in common with
the current GFS browser bundle before publication.

## Browser metadata

When a cloud layer is backed by ICON, the preview labels it LIVE ICON Global
and shows:

- cycle time
- grid dimensions
- native resolution
- 0.125 degree remap
- display interpolation

When ICON is unavailable for that valid time, it labels the cloud source LIVE
GFS fallback.

## Current geographic scope

ICON Global is a global numerical model, but B150 intentionally keeps the
published browser artifact Taiwan-regional so the first production change is
small and auditable.

This means B150 is not yet a full-world tile service.

The next global-map batch should replace a single regional JSON grid with a
tile/pyramid or request-scoped regional artifact strategy so Japan, the United
States and other catalog regions can use the same ICON-primary policy without
shipping a global 0.125 degree array to every browser.

## Current forecast horizon in the public preview

The existing scheduled public WeatherGrid preview still publishes the compact
f000 / f003 / f006 / f009 / f012 window. The resolver already defines the
ICON-to-GFS long-range policy, but expanding the public timeline through the
full GFS +384 h horizon is intentionally deferred because doing so with the
current monolithic multi-layer JSON would be unnecessarily large.

Long-range publication should be implemented together with the global
tile/request-scoped storage design.

## Regression requirements

B117 WeatherGrid CI now verifies:

- ICON cycle/horizon resolution and GFS fallback;
- DWD ICON native filename construction;
- official CDO 0.125 degree remap command construction;
- optional ICON browser loading;
- exact-valid-time provider selection;
- bilinear display interpolation for both regular grids;
- nearest rendering for circular wind direction;
- non-blocking ICON refresh and stale-ICON removal;
- unchanged scoring boundary.

## External references

- DWD ICON Open Data:
  https://opendata.dwd.de/weather/nwp/icon/grib/
- DWD CDO helper files:
  https://opendata.dwd.de/weather/lib/cdo/
- DWD ICON triangular-to-lat/lon conversion guidance:
  https://www.dwd.de/DE/leistungen/opendata/help/modelle/Opendata_cdo_EN.pdf
