# B122 Opportunity-aware WeatherGrid UI

Date: 2026-09-29

## Goal

Make the WeatherGrid preview follow the B120/B121 photography-coverage contract instead of centering only on the nominal Place coordinate.

For a selected Photography Opportunity, the initial map view must include the researched Camera Zone plus every available Subject and Environmental Geometry. When only a Place is selected, the UI uses the union of all migrated Opportunity viewports for that Place and reports whether all catalog Opportunities have actually been migrated.

No photography score is changed by this batch.

## Browser coverage bundle

`build_weathergrid_coverage_browser.py` combines:

- `runtime_catalog_v004_r4_2.json`
- `weathergrid_coverage_registry_r4_2.json`
- B120 geometry planning

into:

```text
weathergrid_coverage_browser.json
```

The browser payload contains only the information needed to render subject-aware coverage:

- Place ID/name
- Opportunity ID/name/status
- Camera Zones approved for browser exposure
- Subject Geometry
- Environmental Geometry
- derived coverage / viewport bbox
- completeness and validation messages
- Place-level migration counts

## Camera Zone privacy

Every `camera_zone_ref` must now have an explicit:

```json
"camera_zone_browser_exposure": {
  "tw-000-VP01": "public | generalized | internal_only"
}
```

Browser export is fail-closed.

If an exposure is missing or invalid:

- coverage validation reports an error;
- the compact browser export treats that Camera Zone as `internal_only`;
- exact latitude/longitude is not emitted.

The first B121 batch uses `generalized` because those existing coordinates are documented representative Camera Zone anchors rather than mandatory tripod positions.

## WeatherGrid UI behavior

The B119 preview now adds a **題材** selector.

### Place selected, no Opportunity selected

The map:

- computes the union of all migrated Opportunity viewports for that Place;
- auto-fits to that union;
- draws all available Camera / Subject / Environment overlays;
- reports `coverage entries / catalog Opportunities`;
- does not claim complete all-topic coverage unless every active catalog Opportunity has migrated and every plan is complete.

### Opportunity selected

The map:

- auto-fits to that Opportunity's `viewport_bbox`;
- draws Camera Zones in yellow;
- draws photographed Subject Geometry in orange;
- draws Environmental Geometry in cyan/dashed styling;
- reports `verified / provisional / needs research`;
- warns if the current WeatherGrid provider bbox does not contain the entire subject-aware viewport.

### Incomplete coverage

A `needs_research` Opportunity may still show its known Camera Zone, but the UI explicitly states that the photographed subject/environment geometry is missing.

It must not present a camera-only or Place-center map as complete subject-aware coverage.

## Geometry rendering

The browser preview understands the B120 geometry types:

- point
- bbox
- polygon
- sector
- corridor

The current Canvas preview remains a validation renderer, not the final cartographic basemap.

## Weather sampling point

When an Opportunity is selected and a browser-safe Camera Zone coordinate exists, the point weather readout samples the Camera Zone instead of the generic Place point.

This does not turn map coverage geometry into scoring inputs.

## Publish workflow

The existing manual **B117 GFS Multilayer POC** workflow now also builds:

```text
weathergrid_coverage_browser.json
```

When `publish_preview=true`, it publishes all three compact browser files:

```text
weathergrid/gfs_tw_weather_browser.json
weathergrid/gfs_tw_weather_qc.json
weathergrid/weathergrid_coverage_browser.json
```

The large GRIB2 / validation outputs remain GitHub Actions artifacts only.

## Demo behavior

Before a live publish exists, `weathergrid_coverage_sample.json` provides an explicitly labeled demo Opportunity with:

- a known Camera Zone
- a subject sector
- an environmental sector
- a second intentionally incomplete Opportunity

Browser Smoke validates both the provisional complete path and the explicit needs-research path.

## Acceptance criteria

B122 passes when:

1. the Opportunity selector appears after selecting a migrated Place;
2. selecting a complete/provisional Opportunity changes the map view to its subject-aware viewport;
3. Camera / Subject / Environment overlays render;
4. the point weather readout uses the selected Camera Zone when available;
5. incomplete coverage displays an explicit warning;
6. live provider bounds are checked against the Opportunity viewport;
7. missing Camera Zone exposure cannot leak exact coordinates;
8. Browser Smoke covers complete and incomplete demo cases;
9. existing ChaseLights scoring remains unchanged.

## Next work

B123 should make the GFS fetch planner use the derived subject-aware Fetch BBox instead of the fixed Taiwan-wide bbox when a scoped Place/Opportunity request is made.

B121 migration should continue in parallel, especially:

- 鯉魚潭 lake / reflection / sunset geometries
- additional mountain panoramas
- researched sunrise/sunset horizon sectors
- offshore/coastal subjects
