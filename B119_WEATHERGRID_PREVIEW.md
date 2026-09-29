# B119 WeatherGrid Preview UI

## Goal

Turn the validated compact GFS WeatherGrid bundle into an interactive ChaseLights browser preview without changing production photography scoring.

## Preview page

`weather-map.html` provides:

- weather-layer selector
- forecast-time slider and time buttons
- Place selector
- click-to-select Place markers
- Place-focused zoom and full-Taiwan reset
- client-side grid decoding
- client-side bilinear Place sampling for scalar fields
- nearest-cell sampling for wind direction to avoid circular-angle interpolation
- QC warnings for the selected layer / forecast hour

The page is linked from the ChaseLights header as **WeatherGrid**.

## Rendering

B119 intentionally uses a self-contained Canvas renderer rather than adding a third-party map SDK during this stage.

The Canvas renders:

- the GFS grid in geographic longitude/latitude coordinates
- active Place markers
- selected Place label
- lat/lon reference grid
- layer legend

This validates ChaseLights' own layer decoding, time switching and Place sampling before a later cartographic basemap is introduced.

## Data loading

The preview first requests:

```text
weathergrid/gfs_tw_weather_browser.json
weathergrid/gfs_tw_weather_qc.json
```

If a live snapshot has not been published yet, it explicitly falls back to:

```text
weathergrid_sample.json
```

and displays a **DEMO** badge so sample data cannot be mistaken for live forecast data.

## Publishing a live preview snapshot

The existing **B117 GFS Multilayer POC** manual workflow gains a boolean input:

```text
publish_preview
```

When enabled, the workflow:

1. fetches and decodes GFS
2. builds B118 compact browser/QC JSON
3. commits only those two compact JSON files to `weathergrid/`
4. keeps the larger GRIB/frame/PNG outputs as GitHub Actions artifacts

This avoids committing raw GRIB files or large validation PNGs into the website repository.

## Wind-direction quantization

B119 also closes a B118 edge case around 360°.

Wind direction is circular. Values that quantize to 360 are now wrapped to 0, and the browser field metadata carries `wrap: 360`. This keeps quantization error bounded around north instead of clipping 359.9° to 359°.

## Scope and guardrails

- no production scoring change
- no Opportunity logic change
- B119 originally had no automatic scheduled GFS publication; B132 now refreshes the live WeatherGrid four times daily
- no third-party map SDK
- DEMO fallback is visibly labeled
- B119's manual publish path remains available, while B132 is now the production scheduled publication path
- GFS 0.25° remains a coarse synoptic layer

## Next stage

After the live preview is published and visually checked (publication automation is now implemented by B132):

1. add a proper cartographic basemap
2. add wind-vector display in the browser
3. add opacity / animation controls
4. decide the production refresh cadence
5. extend the same WeatherGrid provider contract beyond Taiwan and beyond GFS
