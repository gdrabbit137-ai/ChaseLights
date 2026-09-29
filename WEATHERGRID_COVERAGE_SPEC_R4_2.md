# ChaseLights R4.2 — Topic-aware WeatherGrid Coverage Specification

Date: 2026-09-29  
Batch: B120  
Status: normative specification

## 1. Purpose

A photography weather map must cover the weather that matters to the photograph, not only the nominal Place coordinate.

For every researched Photography Opportunity, the WeatherGrid view and the data fetched for that view MUST cover, at minimum:

1. every Camera Zone that can produce the selected Opportunity;
2. every terrestrial subject or subject area required by that Opportunity;
3. any researched environmental zone that is materially part of the Opportunity, such as a basin used for cloud sea / mist, a water surface used for reflection, or an offshore/horizon sector used for coastal light.

The Place center is not a substitute for these geometries.

This specification governs WeatherGrid map extent and browser auto-fit. It does **not** by itself change Photography Opportunity scoring.

## 2. Existing model ownership

ChaseLights already separates Place research from runtime weather.

Existing `opportunities[].viewpoints[]` remain the canonical source for Camera Zone geometry. B120 MUST NOT create a second competing camera-coordinate field.

B120 adds an Opportunity-level `weather_coverage` contract that:

- references existing Camera Zones by `viewpoint_id`;
- describes photographed subject geometry that is not already represented by a Camera Zone;
- describes any additional environmental geometry needed to understand the photograph;
- provides enough information to derive a WeatherGrid coverage envelope.

The research evidence rule remains unchanged: geometry must come from Place-specific research/evidence. Scene/Theme labels or weather alone MUST NOT invent a photographed subject.

## 3. Terms

### Camera Zone

The researched place or area where the photograph is made.

The authoritative object is the existing Opportunity `viewpoints[]` entry.

### Subject Geometry

The terrestrial photographed subject, subject area, or horizon target relevant to an Opportunity.

Examples:

- a mountain summit or mountain range;
- Taipei 101 / a skyline area;
- a waterfall;
- a coastal rock formation;
- an offshore island;
- a lake or reflective water surface;
- a defined horizon sector for sunrise/sunset.

### Environmental Geometry

A researched area whose weather materially controls the Opportunity, even when the area is not itself the primary visual subject.

Examples:

- a valley/basin expected to hold cloud sea;
- a fog-generation zone;
- a lower-elevation cloud sample area;
- a water surface needed for reflection;
- an approach sector for low cloud or precipitation.

### Required Coverage Geometry

The union of all Camera Zones, Subject Geometries and required Environmental Geometries for an Opportunity.

### Coverage BBox

The smallest longitude/latitude envelope that contains Required Coverage Geometry, before display padding.

### Viewport BBox

The coverage envelope plus visual/context padding used by the browser.

### Fetch BBox

The area the WeatherGrid provider must supply. It MUST contain the Viewport BBox plus enough halo for the selected spatial sampling/interpolation method.

## 4. Normative coverage rule

For an Opportunity `O`:

```text
required_geometry(O)
  = union(
      all referenced Camera Zones,
      all Subject Geometries,
      all required Environmental Geometries
    )

coverage_bbox(O)
  = envelope(required_geometry(O))

viewport_bbox(O)
  = pad(coverage_bbox(O), display_padding)

fetch_bbox(O, provider)
  = pad(viewport_bbox(O), provider_sampling_halo)
```

The implementation MUST NOT:

- fit only to the Place center;
- fit only to the first Camera Zone;
- fit only to the first subject;
- silently crop a secondary camera or subject;
- substitute the Navigation Target for a Camera Zone;
- substitute `map_query` for geometry.

For bilinear interpolation, the Fetch BBox MUST include at least one complete source-grid cell outside the Viewport BBox on every available side. Provider-specific implementations may require a larger halo.

## 5. Opportunity-level data contract

Each researched Opportunity may add:

```json
{
  "weather_coverage": {
    "schema_version": 1,
    "status": "verified",
    "camera_zone_refs": [
      "tw-001-VP01"
    ],
    "subject_geometries": [
      {
        "subject_id": "tw-001-SUB01",
        "role": "primary_subject",
        "name": "台北盆地",
        "geometry": {
          "type": "bbox",
          "west": 121.45,
          "south": 24.95,
          "east": 121.62,
          "north": 25.15
        },
        "coord_confidence": "medium",
        "source_evidence_ids": [
          "..."
        ],
        "browser_exposure": "public"
      }
    ],
    "environment_geometries": [
      {
        "environment_id": "tw-001-ENV01",
        "role": "cloud_sea_basin",
        "geometry": {
          "type": "bbox",
          "west": 121.43,
          "south": 24.93,
          "east": 121.65,
          "north": 25.17
        },
        "coord_confidence": "medium",
        "source_evidence_ids": [
          "..."
        ],
        "browser_exposure": "public"
      }
    ],
    "display_padding_km": 10,
    "coverage_confidence": "medium",
    "note": "..."
  }
}
```

The example values above illustrate the schema only; they are not production coordinates.

## 6. Status semantics

`weather_coverage.status` MUST be one of:

### verified

Camera and subject/environment geometry have been individually researched sufficiently for map coverage.

The UI may claim the map is subject-aware for this Opportunity.

### provisional

The geometry is usable for map framing but still has a documented uncertainty, such as an approximate subject extent or a generalized Camera Zone.

The UI may use it for framing but MUST preserve the coverage confidence.

### needs_research

One or more required Camera/Subject/Environment geometries are not known well enough.

The UI MAY still show a regional WeatherGrid, but MUST NOT claim that the Opportunity-specific view covers all relevant subjects.

A Place center fallback may be used only as a generic map anchor. It is not a valid completion of this contract.

## 7. Supported geometry types

The initial contract supports:

### point

```json
{
  "type": "point",
  "lat": 24.0,
  "lon": 121.0
}
```

Use for a compact, well-defined terrestrial subject.

### bbox

```json
{
  "type": "bbox",
  "west": 120.0,
  "south": 23.0,
  "east": 121.0,
  "north": 24.0
}
```

Use for a broad skyline, mountain group, basin, lake, coast segment or other areal subject.

### polygon

```json
{
  "type": "polygon",
  "coordinates": [
    [121.0, 24.0],
    [121.1, 24.0],
    [121.1, 24.1],
    [121.0, 24.1]
  ]
}
```

Use when a simple bbox would materially overstate the researched area.

### sector

```json
{
  "type": "sector",
  "origin_viewpoint_id": "tw-001-VP01",
  "azimuth_start_deg": 70,
  "azimuth_end_deg": 115,
  "min_range_km": 0,
  "max_range_km": 40
}
```

Use for sunrise/sunset horizon, offshore weather, distant directional views, or another subject best represented as a viewing sector.

### corridor

```json
{
  "type": "corridor",
  "coordinates": [
    [121.0, 24.0],
    [121.2, 24.1]
  ],
  "half_width_km": 3
}
```

Use for a linear coast, valley, ridge, road/rail alignment, or other elongated subject/environment.

## 8. Celestial subjects

The Sun, Moon, Milky Way and stars MUST NOT be assigned fake terrestrial latitude/longitude coordinates.

For celestial Opportunities, WeatherGrid coverage is based on:

- the Camera Zone;
- the researched horizon/view sector when horizon clarity matters;
- any terrestrial foreground Subject Geometry;
- any local atmospheric/environmental zone required by the Opportunity.

Example: a Milky Way + mountain foreground Opportunity may require the Camera Zone plus the mountain foreground geometry. A sunrise Opportunity may require the Camera Zone plus an eastern horizon sector.

## 9. Cloud sea, fog and mist

Cloud sea / fog / mist Opportunities require special care because the photographed phenomenon can occupy a materially different place from the camera.

When research supports it, `environment_geometries` SHOULD include:

- the lower basin/valley where cloud/fog is expected;
- camera-level clear-air area when spatially distinct;
- directional sample sectors used by the spatial-weather model.

The WeatherGrid map MUST be able to show both the photographer location and the lower cloud/fog area in the same subject-aware view.

This coverage requirement does not weaken existing scoring guards against camera-level whiteout.

## 10. Reflection and water subjects

Reflection Opportunities SHOULD identify the relevant water surface as a Subject or Environmental Geometry.

A Camera Zone on the shore alone is insufficient when the photographed reflection depends on a materially larger lake/pond/wetland surface.

## 11. Mountain / distant terrestrial subjects

For a distant mountain or skyline, the actual photographed subject MUST be represented separately from the camera.

The WeatherGrid default view MUST contain both.

If a mountain range or skyline cannot be represented accurately by a single point, use a bbox or polygon rather than choosing an arbitrary summit/center.

## 12. Coast / sunrise / sunset subjects

For coast and horizon Opportunities, a Camera Zone on land is not sufficient.

Where the weather over the sea/horizon matters, the Opportunity SHOULD include a sector or offshore Environmental Geometry covering the researched view direction.

The sector range should reflect the photographic/weather decision need, not an arbitrary fixed global distance.

## 13. Place-level default behavior

When the user opens WeatherGrid for a specific Opportunity:

> default viewport = that Opportunity's `viewport_bbox`

When the user opens WeatherGrid for a Place without choosing an Opportunity:

> default viewport = union of `coverage_bbox` for **all active researched Opportunities at that Place**, then apply display padding

Therefore the Place-level view MUST cover all known Camera Zones and photographed subjects for all active topics at that Place.

If one Opportunity is `needs_research`, the UI must indicate that complete all-topic coverage is not yet verified.

## 14. Regional / country overview behavior

A regional WeatherGrid overview may use a larger regional provider bbox.

It is valid for the regional map to contain substantially more area than the Opportunity coverage.

It is not valid for an Opportunity/Place auto-fit to crop required geometry merely because a smaller Place-center bbox is convenient.

## 15. Padding and provider halo

`display_padding_km` is an Opportunity-level presentation/context margin.

Rules:

- it MAY be explicitly researched/curated;
- if omitted, the runtime MAY apply a documented product default;
- it MUST NOT be used to compensate for missing Subject Geometry;
- it MUST NOT shrink Required Coverage Geometry.

`provider_sampling_halo` belongs to the WeatherGrid provider/runtime, not the research catalog.

For a regular gridded model using bilinear interpolation, provider halo MUST be at least one full grid spacing around the viewport where source coverage permits.

## 16. Dateline / longitude handling

ChaseLights is multi-country and must support Opportunities near ±180° longitude.

Coverage computation MUST be antimeridian-aware.

A naive numeric `min(lon) / max(lon)` envelope that turns a short dateline-crossing view into an almost-global bbox is forbidden.

The derived coverage representation MUST preserve whether it wraps the antimeridian.

## 17. Privacy and non-public Camera Zones

Some existing Camera Zones are private, controlled, linear, or intentionally do not expose an exact public tripod coordinate.

B120 MUST preserve that policy.

`browser_exposure` is one of:

- `public`
- `generalized`
- `internal_only`

For referenced Camera Zones, `weather_coverage.camera_zone_browser_exposure`
MUST explicitly map every `camera_zone_ref` to one of the same three values:

```json
"camera_zone_browser_exposure": {
  "tw-001-VP01": "generalized"
}
```

Browser export is fail-closed: an omitted Camera Zone exposure is treated as
`internal_only`, never as public.

Rules:

- browser output MUST NOT reveal an `internal_only` exact coordinate;
- a generalized public area/extent may be used when research permits;
- subject-aware coverage may be computed internally from protected geometry, but the browser payload must expose only the approved generalized extent;
- the map must not turn a non-public Camera Zone into a public navigation target.

Navigation remains governed separately by `NAVIGATION_SPEC_R4_2.md`.

## 18. Evidence and provenance

Every Subject/Environment Geometry admitted as `verified` or `provisional` MUST have:

- Place-specific source evidence or an explicitly curated research basis;
- coordinate/geometry confidence;
- a stable subject/environment ID;
- enough provenance to audit why the geometry exists.

Terrain or generic geographic plausibility alone MUST NOT create a photographed subject.

The governing evidence principle remains:

> Place-specific evidence proves what can be photographed; runtime weather estimates when that researched subject may work.

## 19. Scoring boundary

WeatherGrid coverage metadata is a map/data-coverage contract.

Adding a Subject Geometry MUST NOT automatically make that geometry a scoring sample.

A scoring model may consume subject/environment samples only when:

1. the Opportunity's scoring/runtime module explicitly defines that sampling topology;
2. the variable and threshold semantics have been validated;
3. regression tests cover the new behavior.

Therefore:

```text
map coverage != scoring evidence
map coverage != scoring sample topology
```

B120 must not silently alter Opportunity scores.

## 20. Derived runtime fields

The runtime/browser bundle may derive:

```json
{
  "coverage": {
    "complete": true,
    "coverage_bbox": {
      "west": 120.0,
      "south": 23.0,
      "east": 122.0,
      "north": 25.0,
      "wraps_antimeridian": false
    },
    "viewport_bbox": {
      "west": 119.9,
      "south": 22.9,
      "east": 122.1,
      "north": 25.1,
      "wraps_antimeridian": false
    },
    "camera_zone_count": 2,
    "subject_geometry_count": 3,
    "environment_geometry_count": 1,
    "coverage_confidence": "medium"
  }
}
```

These are derived/cache fields. The authoritative research inputs remain Camera Zone references plus Subject/Environment Geometry.

## 21. UI contract

A subject-aware WeatherGrid view SHOULD visually distinguish:

- Camera Zone / camera area;
- photographed Subject Geometry;
- Environmental Geometry;
- selected Opportunity name;
- incomplete/provisional coverage state.

For a selected Opportunity, the initial map fit MUST include all required geometry.

For a Place-level all-topic view, the initial map fit MUST include the union of all active researched Opportunity coverage.

The user may zoom/pan after initial fit. User-initiated zoom does not violate the coverage contract.

## 22. Data-source coverage failure

If the current WeatherGrid provider cannot supply the full Fetch BBox:

- the runtime MUST set `coverage.complete=false`;
- the browser MUST indicate that the weather layer does not fully cover the researched camera/subject geometry;
- scoring MUST NOT silently assume missing areas are clear/zero;
- the map MUST NOT claim complete subject-aware coverage.

## 23. Validation requirements

A B120-compatible validator MUST verify at least:

1. every `camera_zone_ref` resolves to an Opportunity Viewpoint;
2. every geometry has a supported type and valid coordinates;
3. every `verified` coverage object has at least one Camera Zone and one Subject Geometry, except a documented local/celestial case where the subject is represented by environment/horizon geometry;
4. computed `coverage_bbox` contains every referenced camera geometry;
5. computed `coverage_bbox` contains every subject geometry;
6. computed `coverage_bbox` contains every required environmental geometry;
7. `viewport_bbox` contains `coverage_bbox`;
8. `fetch_bbox` contains the viewport plus provider sampling halo;
9. private/internal Camera Zone coordinates do not leak into browser payloads;
10. dateline-crossing geometry does not explode into an almost-global bbox;
11. Place-level all-topic auto-fit contains every active Opportunity coverage at that Place;
12. missing geometry results in explicit incomplete state, not silent Place-center substitution.

## 24. Browser Smoke acceptance tests

Browser Smoke SHOULD cover representative topology classes:

- remote mountain subject: camera and distant mountain both visible after auto-fit;
- cloud sea: high camera + lower basin both visible;
- coast/horizon: land camera + offshore sector visible;
- reflection: camera + water surface visible;
- multiple Opportunities at one Place: Place-level view contains the union of all topics;
- incomplete geometry: warning shown and no "complete subject-aware" claim;
- private Camera Zone: no protected exact coordinate exposed.

## 25. Migration policy

The catalog may migrate incrementally.

During migration every active Opportunity must be in one of these states:

- `verified`
- `provisional`
- `needs_research`

No missing/implicit state is allowed once the Opportunity has entered the B120 migration set.

A region may claim **complete all-topic WeatherGrid coverage** only when every active researched Opportunity in that region is `verified` or `provisional`, and no required geometry is silently missing.

## 26. Implementation staging

### B120 — specification and validator

- adopt this contract;
- add schema validation helpers;
- compute coverage/viewport/fetch envelopes;
- no production scoring change.

### B121 — curated geometry migration

- populate camera references and Subject/Environment Geometry for priority Taiwan Opportunities;
- audit camera/subject coverage;
- keep `needs_research` explicit.

### B122 — Opportunity-aware WeatherGrid UI

- choose Opportunity;
- auto-fit to its viewport;
- render Camera / Subject / Environment overlays;
- Place-level mode uses all-topic union.

### B123 — provider-aware fetch planning

- derive provider Fetch BBox from coverage + interpolation halo;
- cache/fetch only required grid area when provider supports spatial subsetting;
- surface incomplete provider coverage.

## 27. Product acceptance statement

The requirement is satisfied only when the following statement is true:

> For any Opportunity shown as subject-aware, ChaseLights can identify the researched Camera Zone(s) and photographed subject/environment geometry, and the initial WeatherGrid data/view extent contains all of them.

A map centered on the Place coordinate alone does not satisfy B120.
