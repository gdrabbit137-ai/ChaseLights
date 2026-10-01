# B169 NASA Black Marble / VIIRS Nighttime Lights

Date: 2026-10-01

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
