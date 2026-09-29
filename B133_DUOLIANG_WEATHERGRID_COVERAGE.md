# B133 Duoliang Station Subject-aware WeatherGrid Coverage

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

Taiwan Tourism Administration publishes Duoliang Station at approximately:

```text
22.507487, 120.95888
```

and describes the elevated station as overlooking the Pacific, with visitors watching moving trains against the blue sea / mountain scene.

Sources:

- https://www.taiwan.net.tw/m1.aspx?id=A12-00377&sNo=0001016
- https://www.taiwan.net.tw/m1.aspx?keystring=&sNo=0042331&uid=25011

## Subject geometry

B133 does not invent an exact track polygon or train position.

The local station / passing-train subject is represented provisionally as:

```text
origin:  tw-037-VP01
azimuth: 0°–360°
range:   0–0.6 km
```

This is a conservative local envelope around the official high-confidence viewing-area anchor. It does not assert the exact railway alignment, tunnel geometry, timetable or current train position.

## Pacific environment geometry

The Pacific background is represented as:

```text
origin:  tw-037-VP01
azimuth: 30°–160°
range:   0–15 km
```

This broad sector exists only to prevent WeatherGrid from cropping the coastal atmosphere relevant to the photographed scene. It is not an exact ocean boundary or local-horizon model.

## Registry result

```text
registry_version: B121.10 -> B121.11
entries:          36 -> 37
complete:         36 -> 37
needs_research:   0
```

`tw-037` has one active Opportunity, so it becomes all-topic-complete.

## Provider result

B123 may safely request:

```text
coverage_scope = place
coverage_id    = tw-037
```

The derived request must contain the Camera Zone anchor, the local station/train envelope, the Pacific atmosphere sector, display padding and the GFS interpolation halo while remaining smaller than Taiwan-wide.

## Regression requirements

CI must prove:

1. registry count is 37;
2. `tw-037-P01` is provisional-complete;
3. the official Tourism Administration coordinate is inside coverage;
4. the Pacific sector extends meaningfully east of the station;
5. browser payload marks `tw-037` all-topic-complete;
6. subject/environment export as explicit sectors;
7. B123 Place-scoped fetch is safe and smaller than Taiwan-wide;
8. existing complete Places, including `tw-066`, remain complete;
9. scoring remains unchanged.

## Guardrails

- no Place-center fallback;
- no exact track polygon claim;
- no train-position or timetable claim;
- no inference that favorable weather guarantees a passing train;
- no inference that the viewing area is currently open;
- no Photography Opportunity scoring changes.

## Next work

After merge:

- run one live `place/tw-037` scoped NOAA/NOMADS validation;
- continue with single-Opportunity Places only when the photographed subject can be conservatively bounded;
- keep timetable/access eligibility separate from WeatherGrid coverage geometry.
