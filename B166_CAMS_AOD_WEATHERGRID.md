# B166 — CAMS Global AOD 550 nm WeatherGrid

Date: 2026-10-01

## Goal

Add the first photography-environment layer: aerosol optical depth (AOD) at
550 nm, used as a direct haze indicator.

## Source contract

- source API: Open-Meteo Air Quality API
- requested domain: `cams_global`
- upstream model: Copernicus Atmosphere Monitoring Service (CAMS) Global
- native spatial resolution: about 0.4° / 45 km
- native temporal resolution: 3 hours
- update frequency: about every 12 hours
- API field: `aerosol_optical_depth`
- WeatherGrid field: `aerosol_optical_depth_550nm`
- unit: dimensionless

Open-Meteo exposes hourly API output. B166 deliberately publishes only UTC
hours divisible by three so the public WeatherGrid timeline does not imply
higher native temporal resolution than CAMS Global.

## Presentation grid

B166 samples a regular 0.4° request lattice covering the existing Taiwan
WeatherGrid region. Open-Meteo selects the nearest CAMS grid cell for each
request coordinate.

The browser `grid` therefore describes the ChaseLights **request/presentation
lattice**, not a claim that those coordinates are the native CAMS cell centers.
Provenance records both facts.

## Browser encoding

AOD is stored as integer-scaled values:

- scale: 0.001
- decode: `encoded * 0.001`
- null: missing

The display range is 0–1.5. Values above the display range are clamped only for
colour normalization, not in the stored browser data.

## UI

WeatherGrid gains a manual source:

`CAMS Global · 霧霾`

and layer:

`AOD 550 nm`

The layer is intentionally not inserted into `自動預報` yet. B168 needs to
combine AOD with humidity/visibility/dew-point evidence before it can safely
affect fog/haze interpretation or opportunity scoring.

## Attribution

The UI identifies Copernicus CAMS and Open-Meteo. B166 uses the Open-Meteo
free endpoint for current non-commercial validation; commercialisation requires
a licensed/customer or self-hosted path.

## Guardrails

- no production score changes;
- no fog/haze classifier yet;
- no PM2.5 yet;
- no claim that 0.4° presentation sampling improves CAMS native resolution;
- no use of AOD as a substitute for surface PM2.5;
- no mixing into JMA/CWA/ICON/GFS provenance.
