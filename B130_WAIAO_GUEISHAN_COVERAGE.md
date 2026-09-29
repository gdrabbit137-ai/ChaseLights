# B130 Waiao Gueishan Subject-aware WeatherGrid Coverage

Date: 2026-09-29

## Goal

Make `tw-075` 外澳沙灘／龜山朝日 an all-topic-complete WeatherGrid Place while tightening the Camera Zone coverage behavior introduced by B120.

The photographed weather-relevant geography is not the Place center. It is:

- the researched Waiao beach Camera Zone;
- Gueishan Island as the terrestrial subject;
- the eastern dawn / sunrise atmosphere around the island direction.

No Photography Opportunity score is changed.

## Existing catalog contract

`tw-075-P01` already states:

```text
Camera Zone: 外澳沙灘龜山島朝日 Camera Zone
target:      Gueishan Island + eastern sunrise
sun:         broad east-facing dawn sector
```

The catalog Camera Zone is an `area` with:

```text
anchor:             24.87516, 121.84257
geometry_extent_m:  900
coordinate confidence: high
geometry confidence:   high
```

The catalog note explicitly describes this as a long beach Camera Zone rather than a single tripod.

## Official subject coordinate

The Taiwan Tourism Administration attraction record gives Gueishan Island at:

```text
24.842373, 121.95015
```

and describes Waiao as facing Gueishan Island with the Gueishan sunrise scene.

Sources:

- https://www.tad.gov.tw/m1.aspx?id=C100_164&sNo=0001106
- https://www.tad.gov.tw/m1.aspx?id=A12-00567&sNo=0001106

From the catalog Camera Zone anchor to the official island coordinate, the approximate great-circle relation is:

```text
distance: 11.45 km
bearing:  108.5°
```

These derived values are used only to design an over-covering WeatherGrid envelope.

## Subject geometry

Gueishan Island is represented as an official-coordinate point:

```json
{
  "type": "point",
  "lat": 24.842373,
  "lon": 121.95015
}
```

This is a subject coordinate, not a Camera Zone or navigation substitution.

## Dawn environment geometry

The sunrise atmosphere is represented provisionally by:

```text
origin:  tw-075-VP01
azimuth: 85°–130°
range:   0–15 km
```

The sector:

- contains the ~108.5° camera-to-island line;
- extends beyond the ~11.45 km island distance;
- represents nearby east-facing dawn weather around the island;
- does not claim an exact Sun / island alignment;
- does not replace future ephemeris-aware sunrise modeling.

Status remains `provisional`.

## Camera Zone extent hardening

Before B130, non-point Camera Zones were represented in the coverage planner only by their coordinate anchor, even when the catalog already had `geometry_extent_m`.

That was too weak for the B120 requirement that WeatherGrid contain the Camera Zone, not only one coordinate inside it.

B130 changes the planner:

```text
geometry_type = point
    -> use anchor

geometry_type != point AND geometry_extent_m exists
    -> include anchor
    -> conservatively expand by the full curated extent
       north / east / south / west

geometry_type != point AND extent is missing
    -> keep anchor-only behavior
    -> preserve an explicit warning
```

Using the full catalog extent as a radius intentionally over-covers ambiguous area/corridor geometry. For WeatherGrid framing:

```text
over-coverage is acceptable
under-coverage is not
```

This immediately improves all existing registry entries whose canonical Camera Zone already has a curated extent.

## Registry result

```text
registry_version: B121.7 -> B121.8
entries:          33 -> 34
complete:         33 -> 34
needs_research:   0
```

`tw-075` has one active Opportunity, so it becomes an all-topic-complete Place.

## Provider result

B123 may safely request:

```text
coverage_scope = place
coverage_id    = tw-075
```

The derived GFS request must contain:

- the conservatively expanded Waiao Camera Zone;
- the official Gueishan Island subject coordinate;
- the provisional dawn environment sector;
- display padding;
- the GFS interpolation halo.

The provider rectangle must remain smaller than the Taiwan regional request.

## Regression requirements

CI must prove:

1. registry count is 34;
2. `tw-075-P01` is provisional-complete;
3. its coverage bbox contains the official Gueishan Island coordinate;
4. its coverage bbox contains every conservative Camera Zone extent point produced from the 900 m catalog extent;
5. browser payload marks `tw-075` all-topic-complete;
6. subject is exported as a point and dawn environment as a sector;
7. B123 Place-scoped fetch is safe and smaller than Taiwan-wide;
8. existing all-topic-complete Places remain complete;
9. scoring remains unchanged.

## Guardrails

- no Place-center fallback;
- no fake terrestrial coordinate for the Sun;
- no exact sunrise-alignment claim;
- no exact visible beach polygon claim;
- no reduction of the 900 m Camera Zone to one tripod point for WeatherGrid framing;
- no scoring changes.

## Next work

The same Camera Zone extent hardening can now be used for other catalog entries that already have `geometry_extent_m`.

Next subject migrations should prioritize:

- `tw-073` 老梅綠石槽: local green-groove foreground + researched dawn horizon;
- other single-Opportunity Places with high-confidence local subject geometry;
- live scoped GFS validation for `tw-075` once the branch merges.
