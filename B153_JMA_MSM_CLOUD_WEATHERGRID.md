# B153 — JMA MSM 5 km native cloud WeatherGrid

Date: 2026-09-30

## Scope

B153 adds exactly one new forecast model source: **JMA MSM 5 km**.

No LFM or Himawari integration is included in this batch. Those remain the next
sequential steps after MSM is validated and merged.

## Source and transport

JMA's MSM surface GPV natively publishes:

- total cloud cover
- low cloud cover
- middle cloud cover
- high cloud cover

The official surface grid is 0.05° latitude × 0.0625° longitude, approximately
5 km, with hourly surface forecast output. The native domain is
22.4°N–47.6°N / 120°E–150°E. Forecast length is 39 h for ordinary cycles and
78 h for 00/12 UTC cycles.

The JMA GPV files are distributed through the Japan Meteorological Business
Support Center. For ChaseLights B153, the same native JMA MSM fields are read
from Open-Meteo's AWS Open Data spatial mirror:

- model: `jma_msm`
- transport: Open-Meteo AWS Open Data
- license of the mirror distribution: CC-BY-4.0
- cloud fields remain native JMA cloud diagnostics; Open-Meteo is only the
  transport/mirror.

The provider reads the cloud-native OM spatial files directly with `omfiles`
and anonymous S3 access. It does not call a point forecast API or create cloud
cover from relative humidity.

## Initial browser publication

To keep the first production payload small while preserving native resolution:

- published bbox: 120.0–123.0°E / 22.4–26.0°N
- native subset grid: 49 × 73 cells
- published timeline: f000 through f012
- time interval: 1 hour
- native cloud grid is not spatially regridded before publication

This covers the JMA MSM portion of Taiwan. Areas south of 22.4°N and west of
120°E are outside the native MSM domain and must remain blank/unavailable rather
than extrapolated.

## Cloud vertical definitions

JMA calculates model-level cloud amount first, then combines vertical layers
with maximum-random overlap. The official calculation documentation describes
the reference boundaries using the model layers corresponding to 850 hPa and
500 hPa when surface pressure is 1000 hPa.

WeatherGrid stores this as provider-native metadata:

- low cloud: surface to approximately 850 hPa reference boundary
  - approximately ground to 1.5 km
- middle cloud: approximately 850 to 500 hPa reference boundaries
  - approximately 1.5 to 5.6 km
- high cloud: pressure lower than approximately 500 hPa reference boundary
  - approximately above 5.6 km

The pressure/model-layer definition is authoritative. Kilometre heights are
only explanatory standard-atmosphere approximations.

## UI behavior

The model selector gains:

- JMA MSM 5 km
- CWA WRF 3 km
- ICON Global
- GFS 0.25°
- Auto

Manual JMA mode owns its own:

- geographic boundary
- 5 km native resolution metadata
- hourly timeline
- available cloud fields
- vertical-definition text

B153 intentionally leaves Auto unchanged. Auto still uses the current
ICON-cloud / GFS-fallback policy until the manually selectable JMA feed has been
validated in production.

## Guardrails

1. JMA cloud fields are native cloud-cover diagnostics, not RH-derived proxies.
2. Open-Meteo is recorded as transport/mirror, while JMA is recorded as model provider.
3. JMA's native domain boundary is respected; no extrapolation south/west of it.
4. Provider-native vertical definitions are shown instead of forcing ICON/GFS/JMA into one common height scheme.
5. JMA refresh failure is non-blocking and removes stale JMA browser files.
6. Photography opportunity scoring is unchanged in B153.

## Validation

PR validation includes:

- offline grid / run / vertical-definition contracts
- compact browser bundle tests
- UI/model-selector contract tests
- a live JMA MSM smoke test against current Open-Meteo AWS spatial files
- existing WeatherGrid browser smoke tests
