# B144 WeatherGrid Cartographic Basemap

Date: 2026-09-30

## Goal

Replace the coordinate-only WeatherGrid background with a real interactive cartographic basemap while preserving the existing GFS browser bundle, subject-aware coverage overlays, and Photography Opportunity scoring boundary.

B143 is already assigned to the mobile administrative-area picker work, so this cartographic batch uses B144.

## Rendering stack

The browser preview now uses:

1. MapLibre GL JS 6.11.2 for interactive map projection and navigation;
2. the documented OpenFreeMap Liberty style as the cartographic basemap;
3. the existing ChaseLights Canvas renderer as a translucent GFS overlay;
4. ChaseLights Camera / Subject / Environment overlays above the weather layer.

The weather data remains ChaseLights-owned decoded GFS data. The basemap is geographic context only.

## Why MapLibre

The old B119 Canvas projected latitude/longitude linearly and intentionally had no cartographic basemap. That was sufficient for validating decoding and sampling, but it made coastlines, islands, roads and place context hard to interpret.

MapLibre provides the map camera, Web Mercator projection, pan/zoom and labels without changing the WeatherGrid provider contract.

## Projection contract

When the basemap is available, every GFS cell corner, Place marker, Camera Zone and subject/environment geometry is projected with:

```text
map.project([lon, lat])
```

The weather Canvas is resized to the displayed map surface and redraws during map movement. This avoids placing an equirectangular weather overlay on top of a Web Mercator basemap.

## Weather opacity

The preview adds a weather-layer opacity control.

Default:

```text
62%
```

The basemap remains readable underneath the GFS cells while Camera / Subject / Environment geometry stays fully opaque above the weather layer.

## Fail-soft behavior

MapLibre and OpenFreeMap are presentation dependencies, not weather-data dependencies.

If the MapLibre module or basemap cannot load:

- the GFS browser bundle still loads;
- the original dark Canvas background and latitude/longitude grid remain available;
- Place selection, time switching, sampling and coverage geometry continue working;
- the UI labels the state as `Canvas fallback`.

No weather or scoring result is allowed to depend on successful basemap loading.

## Provider choice

The first production-preview implementation uses the OpenFreeMap public Liberty style:

```text
https://tiles.openfreemap.org/styles/liberty
```

No API key is required. This is suitable for the current preview stage. A later production-hardening batch may self-host tiles or switch to a provider with an explicit SLA without changing the ChaseLights overlay contract.

## Scope guardrails

- no Photography Opportunity scoring changes;
- no GFS field or fetch changes;
- no change to subject-aware coverage geometry;
- no use of basemap features as scoring evidence;
- MapLibre version is pinned instead of using `latest`;
- OpenFreeMap failure must degrade to the existing Canvas renderer.

## Regression requirements

CI verifies that:

1. the basemap container renders below the weather Canvas;
2. MapLibre is version-pinned;
3. the OpenFreeMap style URL is explicit;
4. map projection and fitBounds are used by the WeatherGrid renderer;
5. the opacity control exists and defaults to 62%;
6. Canvas fallback remains present;
7. B117 WeatherGrid CI executes this contract test.

## Next work

After visual smoke testing on desktop and mobile:

- tune basemap label density against cloud/precipitation colors;
- consider weather-specific palette refinements for readability;
- add wind-vector rendering;
- evaluate self-hosted or SLA-backed basemap delivery before treating the preview as a production-critical map.
