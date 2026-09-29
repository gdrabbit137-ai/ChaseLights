# B123 Subject-aware WeatherGrid Scoped Fetch

Date: 2026-09-29

## Goal

Make the WeatherGrid provider request itself follow the B120/B121 photography coverage contract.

B122 changed the browser viewport. B123 changes the upstream GFS spatial subset for explicit scoped validation requests so the fetched weather area is derived from:

```text
Camera Zone(s)
  + photographed Subject Geometry
  + required Environmental Geometry
  -> coverage bbox
  -> display padding
  -> one full GFS grid-cell interpolation halo
  -> provider fetch bbox
```

A Place center is not used as a substitute for missing coverage.

## Strict scope rules

### Opportunity scope

`--coverage-opportunity <opportunity_id>` is accepted only when:

- the Opportunity exists in the runtime catalog;
- it has a B120/B121 coverage registry entry;
- the coverage plan is `verified` or `provisional` and structurally complete;
- a Camera Zone resolves;
- a Subject or Environmental Geometry exists;
- the provider bbox can be represented as one non-antimeridian NOMADS bbox.

Otherwise the fetch is refused.

Example:

```bash
python gfs_multilayer_poc.py \
  --forecast-hours 0,3,6 \
  --coverage-opportunity tw-036-P03 \
  --output-dir gfs_scoped_qixingtan
```

This request must include the七星潭 Camera Zone and the researched northward subject/environment sector, plus display padding and the interpolation halo.

### Place scope

`--coverage-place <spot_id>` is stricter.

A Place-scoped request is accepted only when **every active Photography Opportunity at that Place**:

- has migrated coverage; and
- has complete coverage.

This directly enforces the product requirement that a Place-level weather map cover all topics' cameras and photographed subjects.

At the current B121 migration stage, many Places intentionally fail this gate. That is correct behavior.

## GFS integration

`gfs_multilayer_poc.py` now:

- resolves a subject-aware request bbox before download;
- passes that bbox to every NOMADS request in the selected GFS cycle;
- writes the actual request bbox into frame JSON and manifest;
- stores `fetch_scope` metadata for replay/audit;
- filters Place sampling to coordinates inside the downloaded grid;
- renders the validation overview using the actual request extent.

The default workflow remains unchanged:

> no scope argument = full Taiwan POC bbox

This preserves the current live preview/publication behavior.

## Provider halo

GFS uses a 0.25° grid.

B120 requires at least one complete source-grid cell outside the viewport for bilinear interpolation. B123 therefore adds a conservative one-cell halo to the subject-aware viewport before converting it to the NOMADS request bbox.

Interpolation does not increase GFS model resolution.

## Antimeridian

The B120 planner supports antimeridian-aware geometry.

The current GFS NOMADS integration sends one ordinary west/east subset request, so a scoped plan that wraps ±180° is refused instead of being expanded into an almost-global request.

A future provider adapter can split such coverage into two requests.

## Sampling safety

A scoped GFS file does not contain all Taiwan Places.

B123 therefore filters Place sampling to coordinates inside the actual fetched bbox. It must not sample an outside Place by clamping/falling back to the nearest edge grid cell.

## Manual workflow

The **B117 GFS Multilayer POC** workflow gains optional inputs:

- `coverage_opportunity`
- `coverage_place`

They are mutually exclusive.

Scoped runs are validation artifacts only. `publish_preview=true` is rejected when either scoped input is present because the public preview currently expects the full Taiwan WeatherGrid.

## Acceptance criteria

B123 passes when:

1. `tw-036-P03` produces a scoped NOMADS bbox derived from its Camera + northward subject/environment sector;
2. the provider bbox contains the full viewport plus interpolation halo;
3. `tw-082-P01` is refused because its subject geometry is still `needs_research`;
4. an unmigrated Opportunity is refused;
5. a partially migrated Place is refused;
6. default no-scope runs still use the existing Taiwan bbox;
7. frame JSON / manifest record the actual bbox and fetch scope;
8. outside Places are not sampled from a scoped grid;
9. scoped validation cannot accidentally publish a partial WeatherGrid as the public preview.

## Next work

Two tracks continue from here:

1. **B121 migration** — curate real Subject Geometry for remaining Opportunities, especially 鯉魚潭 lake/reflection/sunset.
2. **Provider architecture** — once migration coverage is broad enough, allow browser/API requests to select a Place/Opportunity and fetch/cache only its required WeatherGrid area rather than the full Taiwan subset.
