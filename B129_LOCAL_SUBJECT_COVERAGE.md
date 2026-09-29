# B129 Local-subject WeatherGrid Coverage Batch

Date: 2026-09-29

## Goal

Expand subject-aware WeatherGrid coverage to two secondary/simple Places whose photographed subjects are local and already have high-confidence curated Camera Zone extents:

- `tw-078` 建功嶼／退潮石板道
- `tw-081` 南竿鐵堡／海防礁岩

Each Place currently has one active Photography Opportunity, so completing that one subject-aware coverage entry also makes the Place safe for B123 Place-scoped GFS fetching.

No Photography Opportunity scoring changes are made.

## tw-078 — 建功嶼退潮石板道景觀

### Existing curated model

The canonical Opportunity already has:

- Camera Zone: `tw-078-VP01`
- geometry type: `linear_corridor`
- curated extent: 450 m
- high coordinate and geometry confidence
- tide/access as the primary runtime gate

Official Taiwan Tourism and Kinmen tourism material describe:

- the stone path appearing at low tide;
- the intertidal zone;
- walking the exposed path to Jianggong Islet;
- Jianggong Islet as the destination/subject.

Sources:

- https://www.taiwan.net.tw/m1.aspx?id=A12-00478&sNo=0001016
- https://www.kinmen.travel/zh-tw/live-camera/1

The official Taiwan Tourism attraction coordinate for the islet is approximately:

```text
24.42746, 118.30005
```

while the existing Camera Zone anchor is:

```text
24.426386, 118.304369
```

### Coverage geometry

B129 models the photographed local subject as a buffered corridor:

```text
Camera Zone anchor
    ->
official Jianggong Islet point

half-width: 0.08 km
```

This deliberately over-covers the exposed stone path and nearby intertidal subject.

It is **not** an exact walkway polygon, tide line or access route.

The Camera Zone remains independently represented through `camera_zone_refs`.

## tw-081 — 南竿鐵堡海防景觀

### Existing curated model

The canonical Opportunity already states:

```text
subject = fort + rocky coast
```

and its Camera Zone `tw-081-VP01` has:

- high coordinate confidence;
- high geometry confidence;
- a curated 150 m small-area extent.

Official Matsu / Taiwan Tourism material describes Tieb堡 as:

- a coastal defensive position;
- built on a rock projecting into the sea;
- surrounded by sea / rocky coast;
- containing the fortifications and high observation area.

Sources:

- https://media.taiwan.net.tw/en-us/portal/travel/details/attraction_a15010500h_002790
- https://www.matsu-nsa.gov.tw/zh-TW/travel-map
- https://www.taiwan.net.tw/m1.aspx?id=C100_406&sNo=0001016

### Coverage geometry

B129 reuses the already-curated 150 m Camera Zone extent as a conservative full-circle subject envelope:

```text
origin: tw-081-VP01
azimuth: 0°–360°
range: 0–0.15 km
```

This is intentionally a local over-covering envelope for:

- the fort;
- immediate rocky coast;
- immediate near-sea context.

It is not an exact building, rock or shoreline polygon.

## Registry result

B129 advances the sidecar to:

```text
registry_version = B121.7
entries          = 33
provisional      = 33
complete         = 33
needs_research   = 0
```

The all-topic-complete Place set now includes:

```text
tw-014  雲洞山莊觀景平台
tw-034  清水斷崖／崇德遊憩區
tw-036  七星潭
tw-078  建功嶼／退潮石板道
tw-081  南竿鐵堡／海防礁岩
tw-082  鯉魚潭
```

## Provider-fetch result

B123 may now safely use:

```text
coverage_scope = place
coverage_id    = tw-078
```

or:

```text
coverage_scope = place
coverage_id    = tw-081
```

without falling back to the Taiwan-wide bbox.

Both Places have exactly one active Opportunity, and that Opportunity now has complete provisional coverage.

## Regression requirements

CI must prove:

1. registry count is 33;
2. both new entries validate as provisional-complete;
3. Jianggong coverage contains both the Camera Zone and official islet coordinate;
4. Tieb堡 coverage extends around its Camera Zone rather than collapsing to a point;
5. browser payload marks each Place `all_topics_complete=true`;
6. B123 Place-scoped fetch remains smaller than the Taiwan region bbox;
7. existing all-topic Places remain complete;
8. an incomplete multi-topic Place such as `tw-035` still falls back region-wide;
9. scoring remains unchanged.

## Guardrails

- no generic Theme-to-geometry inference;
- only pre-existing Camera Zone extent and Place-specific official subject evidence are reused;
- no exact tide-line claim;
- no exact causeway-route claim;
- no exact fort / shoreline polygon claim;
- Camera Zone browser exposure remains generalized;
- map coverage remains separate from scoring sample topology.

## Next work

1. continue with single-Opportunity Places whose subject geometry is already well constrained;
2. separately research sunrise/horizon Places that need celestial + foreground coverage;
3. keep large multi-topic Places incomplete until every subject is explicitly represented;
4. live-validate scoped provider fetches when a manual GFS run is available.
