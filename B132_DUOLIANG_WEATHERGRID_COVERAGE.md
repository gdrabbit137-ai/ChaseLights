# B132 Duoliang Station Subject-aware WeatherGrid Coverage

Date: 2026-09-30

## Goal

Make `tw-037` 多良火車站觀景台 an all-topic-complete WeatherGrid Place without changing Photography Opportunity scoring or pretending that weather can determine train presence.

The photographed scene is:

- the official Duoliang Station viewing area;
- the nearby station / passing-train subject;
- the Pacific coastal atmosphere behind the railway scene.

## Existing catalog contract

`tw-037-P01` is the canonical Opportunity:

```text
name:          多良火車＋太平洋經典構圖
Camera Zone:   多良火車站觀景台
formula:       needs_timetable_access_module
best time:     depends on train passage
```

The catalog viewpoint `tw-037-VP01` is a high-confidence point at:

```text
22.50753, 120.95888
```

## Official evidence

Taiwan Tourism Administration publishes Duoliang Station at:

```text
22.507487, 120.95888
```

and explicitly describes the elevated station as overlooking the Pacific, with visitors watching moving trains against the blue sea / mountain scene.

The Tourism Administration also exposes an official live-camera page describing the view of moving trains and the Pacific.

Sources:

- https://www.taiwan.net.tw/m1.aspx?id=A12-00377&sNo=0001016
- https://www.taiwan.net.tw/m1.aspx?keystring=&sNo=0042331&uid=25011

## Local subject geometry

B132 does not invent an exact track polygon or a train position.

The station / nearby passing-train subject is represented provisionally by:

```text
origin:  tw-037-VP01
azimuth: 0°–360°
range:   0–0.6 km
```

This deliberately over-covers the local station, nearby railway and immediate photographed foreground.

It does not claim:

- exact rail alignment;
- exact tunnel geometry;
- a current train position;
- a train timetable;
- that every point inside the envelope is public standing space.

## Pacific environment geometry

The official attraction description establishes the Pacific as the main background.

B132 uses a broad eastern coastal-atmosphere envelope:

```text
origin:  tw-037-VP01
azimuth: 30°–160°
range:   0–15 km
```

The sector is intentionally broad because it is WeatherGrid framing, not an exact visible-horizon model.

It does not claim:

- an exact ocean boundary;
- exact local horizon obstruction;
- exact train / ocean compositional alignment.

## Registry result

```text
registry_version: B121.9 -> B121.10
entries:          35 -> 36
complete:         35 -> 36
needs_research:   0
```

`tw-037` has one active Opportunity, so it becomes all-topic-complete.

## Provider result

B123 may safely request:

```text
coverage_scope = place
coverage_id    = tw-037
```

The derived GFS request must contain:

- the official Camera Zone point;
- the local station / passing-train subject envelope;
- the Pacific coastal-atmosphere sector;
- display padding;
- the GFS interpolation halo.

The snapped provider rectangle must remain smaller than the Taiwan regional bbox.

## Regression requirements

CI must prove:

1. registry count is 36;
2. `tw-037-P01` is provisional-complete;
3. the official Tourism Administration coordinate is inside coverage;
4. the Pacific sector extends meaningfully east of the station;
5. browser payload marks `tw-037` all-topic-complete;
6. subject/environment are exported as explicit sectors;
7. the public official Camera Zone remains publicly exposed;
8. B123 Place-scoped fetch is safe and smaller than Taiwan-wide;
9. existing all-topic-complete Places remain complete;
10. Photography Opportunity scoring remains unchanged.

## Guardrails

- no Place-center fallback;
- no exact track polygon claim;
- no train-position claim;
- no timetable inference from weather;
- no assumption that favorable weather means a train will pass;
- no assumption that the viewing area is currently open;
- no Photography Opportunity scoring changes.

## Next work

After merge:

- run one live `place/tw-037` scoped NOAA/NOMADS validation;
- continue migrating single-Opportunity Places only when subject geometry can be conservatively bounded from existing evidence;
- keep timetable/access eligibility separate from WeatherGrid coverage geometry.
