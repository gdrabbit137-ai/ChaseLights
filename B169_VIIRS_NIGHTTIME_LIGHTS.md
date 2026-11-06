# B169 NASA Black Marble / VIIRS Nighttime Lights

Date: 2026-10-01

## CL-CI-20 UPDATE (2026-11-07): LAADS VNP46A4 is a DEAD END — pipeline moved to NASA GIBS

The annual-composite source below is retired as a live pipeline:

- Suomi NPP data supply was TERMINATED 2026-11-01 (owner ruling + LAADS evidence).
- VNP46A4 is an Suomi NPP (SNPP) product, so the annual cloud-free composite can
  no longer be sourced — the product lifecycle has ended. The LAADS download
  path is marked DEAD END (`viirs_lads_download.py` fails closed).

Replacement live pipeline (primary source per owner ruling: NOAA-20):

- NASA GIBS public WMTS layer `VIIRS_NOAA20_DayNightBand_At_Sensor_Radiance`
  (EPSG:4326 "500m" tile matrix, levels 0-7; daily PNG tiles, no authentication).
- Time range served by GIBS: 2024-03-25 onward, updated daily.
- Suomi NPP DNB GIBS layers (`VIIRS_SNPP_DayNightBand_At_Sensor_Radiance`,
  `VIIRS_SNPP_DayNightBand_ENCC`) survive only as a HISTORICAL archive with
  gaps; they are not used as a live source.
- Daily raw DNB is CLOUD-AFFECTED: this is NOT a cloud-free composite and the
  rendered GIBS layer carries no per-pixel quality flags. This limitation is
  stated in every bundle's provenance/QC and in the UI.
- Radiance values are recovered by inverting the published GIBS colormap
  (bin midpoints, nW/(cm²·sr)) — colormap-bin-quantized approximations, not raw
  HDF5 radiance.
- Ingest: `viirs_gibs_download.py` (tiles, fail-closed on missing days) +
  `viirs_nightlights_ingest.py` (mosaic + bundle). Region bboxes: tw/jp/us/ak/hi.

The historical VNP46A4 contract below is kept for provenance of previously
published artifacts; new snapshots come from the GIBS pipeline.

## Source decision

Primary source: NASA Black Marble VNP46A4 Collection 2 yearly nighttime-lights composite.

- Product: VNP46A4
- DOI: 10.5067/VIIRS/VNP46A4.002
- Level: L3
- Native grid: 15 arc-second (~500 m at the equator)
- Temporal semantics: annual composite
- Primary radiance SDS: `AllAngle_Composite_Snow_Free`
- Quality SDS: `AllAngle_Composite_Snow_Free_Quality`
- Radiance unit: nW/(cm²·sr)

NASA describes VNP46A4 as a yearly moonlight- and atmosphere-corrected nighttime-lights product. Collection 2 provides ancillary quality information and is distributed through LAADS DAAC. NASA Earth science data are open; downloading archive files may still require an Earthdata Login.

Official references:
- https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP46A4/
- https://ladsweb.modaps.eosdis.nasa.gov/filespec/VIIRS/1/VNP46A4
- https://www.earthdata.nasa.gov/engage/open-data-services-software/data-use-policy

## ChaseLights semantics

The WeatherGrid field is `nighttime_lights_radiance_nw_cm2_sr`.

It means satellite-observed upward nighttime-light radiance. It does **not** mean:
- Bortle class;
- zenith sky brightness;
- limiting stellar magnitude;
- a direct prediction of astrophotography quality.

Those require a later skyglow / scattering model and calibration.

## Quality contract

Quality flags remain explicit:
- 0: good
- 1: poor
- 2: gap-filled
- 255: fill

B169 does not silently turn fill values into zero radiance. Poor and gap-filled values remain visible with their quality flag so downstream policy can decide whether to use them.

## Delivery split

B169a (this contract) establishes source semantics, compact encoding and QC without requiring credentials in CI.

B169b adds HDF5 preprocessing: crop a VNP46A4 tile by geographic bbox, decode source scale/offset/fill metadata, preserve quality flags, and emit the compact browser/QC contract. CI uses a synthetic HDF5 tile and therefore needs no Earthdata credentials. Authenticated LAADS download plus a real Taiwan artifact remains the next gate; UI integration follows only after that artifact passes QC.


## B169c LAADS discovery/download

`viirs_lads_download.py` uses LAADS API-V2 `content/details` for VNP46A4 discovery by year + bounding box, then downloads selected HDF5 files through `content/archives` with an `Authorization: Bearer` header.

The token is read from `EARTHDATA_TOKEN` by default and is never committed to the repository. CI tests URL construction, filename extraction and authorization-header behavior without making authenticated network requests.

LAADS documentation states that scripted data downloads require a download token. An Earthdata Download token can be used on LAADS, although LAADS-specific tokens may provide faster download handling.

The next live gate is intentionally manual: configure `EARTHDATA_TOKEN` as a GitHub Actions secret, run discovery for the Taiwan bbox, verify the returned tile set, then wire the discovered file(s) into B169b ingestion. Multi-tile mosaicking will be added if discovery shows Taiwan spans more than one VNP46A4 tile.


## B169d live workflow

A manual GitHub Actions workflow now wires discovery → authenticated download → HDF5 crop/decode → WeatherGrid browser/QC artifact.

Safety gates:
- requires repository secret `EARTHDATA_TOKEN`;
- never prints or commits the token;
- fails closed if the Taiwan bbox resolves to anything other than one source tile;
- validates NASA product/DOI semantics and rejects an all-missing QC result;
- uploads the generated JSON only as an Actions artifact in this batch; it does not publish to production automatically.

This keeps first-live-data inspection separate from production deployment.


## B169e multi-tile mosaic

The live Taiwan path no longer assumes the requested bbox fits one VNP46A4 tile. Every discovered tile is downloaded, cropped independently to the requested bbox, and mosaicked onto a single latitude/longitude union grid before browser encoding.

The mosaic:
- preserves the native 15 arc-second coordinate axes;
- records `source_tile_count` and source filenames in provenance/QC;
- fills genuine uncovered union cells as missing, never zero radiance;
- fails closed on conflicting overlapping cells;
- keeps the single-tile `ingest()` entry point for compatibility.

The downloader now uses the canonical LAADS Collection 2 archive tree `/archive/allData/5200/VNP46A4/YYYY/DDD/<filename>` after discovery. This matches the published LAADS archive layout and avoids assuming that a bare filename is a valid API-V2 archive resource path.


## B169f WeatherGrid UI publication gate

WeatherGrid now knows how to render the annual nighttime-light radiance field, but the source is deliberately **not** hard-coded into the HTML model menu.

At page load the browser attempts to load both:
- `weathergrid/viirs_nightlights_tw_browser.json`
- `weathergrid/viirs_nightlights_tw_qc.json`

The model option is inserted only when the browser artifact declares `source=nasa_black_marble_vnp46a4`, contains the radiance field, and QC has no flags. Missing data, missing QC, or failed contract validation leaves no VIIRS option in the UI.

When published, the UI labels it as an annual static environment background. Its timeline is disabled and the attribution explicitly states that satellite nighttime-light radiance is not Bortle class or sky brightness.


## B169g browser artifact budget

The NASA source contract remains **15 arc-second**. ChaseLights no longer describes this as a fixed "~500 m" resolution because physical east-west spacing varies with latitude.

The browser JSON has an explicit default budget of 250,000 cells. If a cropped/mosaicked source grid exceeds that budget, the browser builder applies a deterministic row/column stride and records:
- native source resolution;
- browser sampling stride;
- source cell count;
- browser cell budget.

This is presentation sampling only. It does not redefine the native NASA product and it does not alter the source HDF5 preprocessing archive. The initial policy favors predictable mobile/browser payload size over pretending that the web renderer is displaying every native VNP46A4 cell.
