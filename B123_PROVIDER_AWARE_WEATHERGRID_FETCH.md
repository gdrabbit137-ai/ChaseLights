# B123 Provider-aware WeatherGrid Fetch Planning

Date: 2026-09-29

## Goal

Make the raw GFS fetch honor the B120/B121 subject-aware coverage contract when a request is scoped to a Photography Opportunity or Place.

The provider request must never shrink to a nominal Place center when subject geometry is missing.

## Scope modes

The B117/B123 live workflow supports:

```text
region
opportunity
place
```

### region

Uses the existing Taiwan-wide NOMADS request:

```text
117.5–123.5°E
20.5–26.75°N
```

This remains the only mode that may publish the public WeatherGrid preview snapshot.

### opportunity

Looks up the requested Opportunity in:

- `runtime_catalog_v004_r4_2.json`
- `weathergrid_coverage_registry_r4_2.json`

If the Opportunity has a complete `verified` or `provisional` coverage plan, B123 uses the derived **Fetch BBox**, including the provider sampling halo.

Example first-batch candidate:

```text
tw-036-P03
```

The GFS request then covers the researched Camera Zone + subject/environment sector + display padding + one source-grid-cell interpolation halo, rather than all of Taiwan.

### place

A Place-scoped request is allowed to shrink only when **every active researched Opportunity at that Place** has a complete coverage entry.

If even one active topic is unmigrated or `needs_research`, the request does not shrink.

This directly enforces the product rule:

> a Place-level weather map must cover all active photographic subjects and Camera Zones, not only whichever topics have already been migrated.

## Safe fallback

Default behavior is fail-safe rather than fail-small.

If a requested Place/Opportunity has incomplete subject-aware geometry:

```text
requested scope
  -> coverage incomplete
  -> Taiwan regional bbox
```

The generated fetch-plan JSON records:

- requested scope
- effective scope
- coverage completeness
- fallback reason
- provider request bbox

With `--strict-coverage`, the same condition becomes an error instead of a regional fallback.

## Provider-grid snapping

Coverage planning already adds a full GFS source-grid-cell halo for interpolation.

B123 additionally snaps the final request outward to the 0.25° GFS grid.

Snapping may enlarge the request, but MUST never crop the derived Fetch BBox.

## Antimeridian

The provider planner is antimeridian-aware.

A wrapped coverage bbox is split into two provider rectangles:

```text
west → 180°
-180° → east
```

The B123 planner validates this now.

The current GFS POC downloader still accepts only one rectangle per run, so an actual dateline-crossing scoped download fails explicitly instead of silently requesting the wrong area. Multi-segment download/merge is future work.

## Output

Every B123 GFS run writes:

```text
gfs_tw_weather_fetch_plan.json
```

The frame JSON and manifest also include:

```json
"fetch_scope": {
  "requested": {},
  "effective": {},
  "coverage_complete": true,
  "fallback_reason": null
}
```

and their `bbox` is the actual provider request bbox, not always the Taiwan-wide constant.

## Spot sampling

For a scoped Place/Opportunity request, the output time series samples only the requested Place.

The regional workflow continues to sample every active Taiwan Place.

## Publish guard

`publish_preview=true` is allowed only when:

```text
coverage_scope = region
```

A scoped artifact must never overwrite the public regional WeatherGrid snapshot.

## Manual validation examples

Full public-style regional run:

```text
coverage_scope = region
publish_preview = false
```

Scoped complete Opportunity:

```text
coverage_scope = opportunity
coverage_id = tw-036-P03
strict_coverage = true
publish_preview = false
```

Explicit incomplete/fallback test:

```text
coverage_scope = opportunity
coverage_id = tw-082-P01
strict_coverage = false
publish_preview = false
```

The second should use a smaller subject-aware bbox.

The third should report incomplete coverage and keep the Taiwan regional bbox.

## Guardrails

- no Photography Opportunity score changes
- no coverage geometry inferred from Place center
- no Place-level shrinking until every active topic is covered
- no scoped artifact can publish over the regional preview
- provider snapping only expands
- incomplete geometry is visible in the fetch plan
- antimeridian requests fail explicitly until multi-segment merge support exists

## Next work

After a successful scoped live GFS run:

1. compare scoped and regional values on overlapping grid cells;
2. verify the scoped request still contains all B120 Camera/Subject/Environment geometry;
3. continue B121 geometry migration so more Places become safe for Place-level scoped fetch;
4. add provider-plan visualization/debug info to the WeatherGrid UI;
5. later allow scheduled regional publication only after refresh/caching policy is decided.
