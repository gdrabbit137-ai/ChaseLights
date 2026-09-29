# B140 — Qinbi Village Subject-aware WeatherGrid Coverage

Date: 2026-09-30 (Asia/Taipei)

## Goal

Make `tw-067` 芹壁聚落 an all-topic-complete WeatherGrid Place without changing Photography Opportunity scoring or pretending WeatherGrid can reconstruct exact building, shoreline, local-horizon, access, or Sun-visibility geometry.

## Existing catalog contract

`tw-067-P01`:

```text
name:          芹壁石屋海灣夕照
Camera Zone:   芹壁聚落高台觀景區
sampling:      directional_sector
formula:       needs_directional_horizon_visibility_module
best time:     sunset
```

Camera Zone anchor:

```text
26.22478, 119.98366
```

It is site-verified but has no reconstructable exact standing-area extent, so WeatherGrid keeps the Camera Zone generalized.

## Official evidence

Matsu National Scenic Area official guidance states that:

- the elevated Qinbi viewpoint can frame the layered stone houses and bay together;
- sunset light on the bay and stone houses creates a classic Qinbi photography scene;
- the settlement is built along the seafront and is known for its traditional stone-house landscape;
- North Gan guidance explicitly identifies Qinbi as a place to watch the sea and sunset.

Sources:

- https://www.matsu-nsa.gov.tw/zh-TW/attractions/1447
- https://www.matsu-nsa.gov.tw/zh-TW/topics/8
- https://www.matsu-nsa.gov.tw/zh-TW/islands

## Subject geometry

Because no exact photographed settlement polygon is curated, B140 uses a conservative local envelope:

```text
origin:  tw-067-VP01
azimuth: 0°–360°
range:   0–1.0 km
```

This covers the near settlement/bay context without claiming exact building or shoreline geometry.

## Sunset environment geometry

At latitude ~26.225°N, geometric annual sunset azimuth extremes are approximately:

```text
summer solstice: ~296.3°
winter solstice: ~243.7°
```

B140 pads this to:

```text
origin:  tw-067-VP01
azimuth: 240°–300°
range:   0–15 km
```

The sector represents western sunset-atmosphere coverage only. It is not an exact visible-horizon mask or guaranteed solar alignment.

## Dynamic conditions remain separate

WeatherGrid does not decide:

- whether a particular pedestrian area is open;
- whether a temporary local closure applies;
- whether haze, cloud or terrain blocks the sunset;
- whether marine conditions affect the coastal scene;
- whether a specific building or private area may be entered.

## Registry result

```text
registry_version: B121.14 -> B121.15
entries:          40 -> 41
complete:         40 -> 41
needs_research:   0
```

## Provider result

B123 may safely request:

```text
coverage_scope = place
coverage_id    = tw-067
```

## Regression requirements

CI must prove:

1. registry count is 41;
2. `tw-067-P01` is provisional-complete;
3. Camera Zone anchor is contained in coverage;
4. western sunset sector materially expands coverage;
5. browser payload marks `tw-067` all-topic-complete;
6. subject/environment geometries are explicit;
7. Camera Zone remains generalized;
8. Place-scoped GFS fetch is safe and smaller than Taiwan-wide;
9. prior complete Places remain complete;
10. scoring remains unchanged.

## Guardrails

- no Place-center fallback;
- no exact building / shoreline polygon claim;
- no exact local-horizon claim;
- no Photography Opportunity scoring changes.

## Next work

After merge:

- run one live `place/tw-067` scoped NOAA/NOMADS validation;
- continue only with single-Opportunity Places whose photographed subject geometry is supported by reliable evidence.
