# B132 Dongyin Lighthouse Subject-aware WeatherGrid Coverage

Date: 2026-09-30

## Goal

Make `tw-066` 東湧燈塔（東引島燈塔） an all-topic-complete WeatherGrid Place while preserving the existing access/safety boundary and without changing Photography Opportunity scoring.

The weather-relevant scene is:

- the researched lighthouse-grounds Camera Zone anchor;
- the fixed Dongyin Lighthouse building as the primary terrestrial subject;
- the nearby cape, cliff and sea atmosphere that controls landmark visibility and the surrounding coastal scene.

## Existing catalog contract

`tw-066-P01` is the canonical `東湧燈塔海岬建築景觀` Opportunity.

The current Camera Zone is:

```text
id:                  tw-066-VP01
anchor:              26.365636, 120.510408
geometry_type:       small_area
geometry_extent_m:   not yet curated
coordinate confidence: high_exif_camera_point
geometry confidence:   high
```

Because no reconstructable Camera Zone extent exists, B132 does not invent one. The WeatherGrid planner must keep its explicit anchor-only warning.

## Official subject evidence

Taiwan Tourism Administration lists Dongyin Island Lighthouse at:

```text
26.365429, 120.51049
```

and describes the fixed lighthouse landmark on Dongyin Island.

The Matsu National Scenic Area describes the lighthouse as standing on the cape with broad sea and cliff scenery.

Sources:

- https://www.taiwan.net.tw/m1.aspx?id=a12-00213&sno=0001016
- https://www.matsu-nsa.gov.tw/zh-TW/attractions/lookMore/1433
- https://www.matsu-nsa.gov.tw/zh-TW

## Subject geometry

The lighthouse itself is represented by the official attraction coordinate:

```json
{
  "type": "point",
  "lat": 26.365429,
  "lon": 120.51049
}
```

This is a photographed subject coordinate. It does not replace the Camera Zone or Directions target.

## Cape / coastal environment geometry

The surrounding weather-relevant coastal context is represented provisionally as:

```text
origin:  tw-066-VP01
azimuth: 0°–360°
range:   0–3 km
```

This full-circle local envelope intentionally over-covers the nearby cape, cliffs and sea atmosphere.

It does **not** claim:

- an exact coastline polygon;
- an exact cliff boundary;
- an exact visible horizon;
- a public walking polygon;
- a safe standing area.

## Dynamic access and safety boundary

The Matsu National Scenic Area publishes dynamic scenic-area control information. Strong gusts and long-wave conditions may close Dongyin Lighthouse / related coastal areas.

B132 therefore keeps:

```text
WeatherGrid coverage != access permission
WeatherGrid coverage != safety clearance
good weather score != proof the site is open
```

Dynamic access, strong-wind and long-wave state remain separate gates.

## Coverage result

```text
registry_version: B121.9 -> B121.10
entries:          35 -> 36
complete:         35 -> 36
needs_research:   0
```

`tw-066` has one active Opportunity, so it becomes all-topic-complete.

## Provider result

B123 may safely request:

```text
coverage_scope = place
coverage_id    = tw-066
```

The request must contain:

- the Camera Zone anchor;
- the official lighthouse subject point;
- the 3 km local cape/coastal environment;
- display padding;
- the GFS interpolation halo.

The provider rectangle must remain smaller than the Taiwan regional bbox.

## Regression requirements

CI must prove:

1. registry count is 36;
2. `tw-066-P01` is provisional-complete;
3. the official lighthouse coordinate lies inside coverage;
4. the local cape/coastal envelope expands beyond the fixed subject;
5. the missing Camera Zone extent remains visible as an anchor-only warning;
6. browser payload marks `tw-066` all-topic-complete;
7. subject exports as a point and environment as a sector;
8. B123 Place-scoped fetch is safe and smaller than Taiwan-wide;
9. existing complete Places remain complete;
10. Photography Opportunity scoring remains unchanged.

## Guardrails

- no Place-center fallback;
- no invented Camera Zone extent;
- no exact coastline / cliff polygon claim;
- no access or safety inference from WeatherGrid coverage;
- no scoring changes.

## Next work

After merge:

- run one live `place/tw-066` scoped GFS validation;
- continue migrating fixed or tightly constrained single-Opportunity subjects;
- keep dynamic access, strong-wind and long-wave closure logic separate from WeatherGrid geometry.
