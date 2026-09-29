# B133 Tungyin Lighthouse Subject-aware WeatherGrid Coverage

Date: 2026-09-30

## Goal

Make `tw-066` 東湧燈塔（東引島燈塔） an all-topic-complete WeatherGrid Place without changing Photography Opportunity scoring.

The photographed weather-relevant scene is:

- the researched lighthouse Camera Zone;
- the fixed lighthouse landmark;
- the immediate sea-cliff / nearshore weather context around the lighthouse.

## Existing catalog contract

`tw-066-P01` already defines a single active Opportunity:

```text
Opportunity: 東湧燈塔海岬建築景觀
Theme:       blue_hour
Camera Zone:       tw-066-VP01
Anchor:            26.365636, 120.510408
Geometry type:     small_area
geometry_extent_m: not curated
Coordinate basis:  high-confidence EXIF anchor
Geometry confidence: high
```

The Camera Zone remains the canonical photography reference. Because its `small_area` extent is not reconstructable yet, the planner correctly keeps an `anchor_only` warning. B133 does not replace it with the attraction coordinate or pretend the Camera Zone is an exact point.

## Official evidence

Taiwan Tourism Administration publishes the lighthouse at approximately:

```text
26.365429, 120.51049
```

and describes the fixed white lighthouse on Dongyin's east slope beside steep coastal terrain and reef-filled waters.

Matsu National Scenic Area also identifies Tungyin Tao Lighthouse as a public attraction in the Shihweishan area reached by marked trails.

Sources:

- https://www.taiwan.net.tw/m1.aspx?id=a12-00213&sno=0001016
- https://www.matsu-nsa.gov.tw/zh-TW/attractions/lookMore/1433

## Subject geometry

The fixed terrestrial subject is represented by the official attraction point:

```json
{
  "type": "point",
  "lat": 26.365429,
  "lon": 120.51049
}
```

This is a photographed-subject coordinate. It does not replace the Camera Zone or navigation target.

## Local coastal environment

B133 does not invent an exact shoreline or cliff polygon.

The immediate sea-cliff / nearshore weather context is represented conservatively as:

```text
origin:  tw-066-VP01
azimuth: 0°-360°
range:   0-1 km
```

This deliberately over-covers the local lighthouse / cliff / nearshore scene while the catalog Camera Zone extent is still unknown. It does not convert the `small_area` Camera Zone into an exact 1 km circle; the planner's `anchor_only` warning remains visible.

No directional claim is made for blue-hour sky, sunset, or a specific coastline segment.

## Registry result

```text
registry_version: B121.9 -> B121.10
entries:          35 -> 36
complete:         35 -> 36
needs_research:   0
```

`tw-066` has one active Opportunity, so it becomes an all-topic-complete Place.

## Provider result

B123 may safely request:

```text
coverage_scope = place
coverage_id    = tw-066
```

The derived provider bbox must contain:

- the catalog Camera Zone;
- the official lighthouse subject coordinate;
- the 1 km local coastal environment envelope;
- display padding;
- the GFS interpolation halo.

It must remain smaller than the Taiwan regional request.

## Regression requirements

CI must prove:

1. registry count is 36;
2. `tw-066-P01` is provisional-complete;
3. the official lighthouse coordinate is inside the coverage bbox;
4. the canonical Camera Zone anchor is inside the coverage bbox and its missing extent remains explicitly warned as `anchor_only`;
5. browser payload marks `tw-066` all-topic-complete;
6. subject is exported as a point and environment as a sector;
7. B123 Place-scoped fetch is safe and smaller than Taiwan-wide;
8. existing all-topic-complete Places remain complete;
9. scoring remains unchanged.

## Guardrails

- no Place-center fallback;
- no exact shoreline or cliff polygon claim;
- no invented blue-hour sky direction;
- no inference that WeatherGrid coverage means the grounds/building are currently open;
- no inference that favorable weather overrides wind, long-wave, trail or site restrictions;
- no Photography Opportunity scoring changes.

## Next work

After merge:

- run one live `place/tw-066` scoped GFS validation;
- continue with other single-Opportunity fixed/local subjects;
- keep lighting state, access and coastal safety separate from WeatherGrid coverage geometry.
