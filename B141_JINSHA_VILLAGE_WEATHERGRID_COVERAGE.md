# B141 — Jinsha Village Subject-aware WeatherGrid Coverage

Date: 2026-09-30 (Asia/Taipei)

## Goal

Make `tw-065` 南竿津沙聚落 an all-topic-complete WeatherGrid Place without changing Photography Opportunity scoring or inventing exact settlement, beach, horizon, or solar-alignment geometry.

## Existing catalog contract

`tw-065-P01`:

```text
name:          津沙聚落海灣夕照
Camera Zone:   津沙聚落海岸夕照公共區
sampling:      directional_sector
formula:       needs_directional_horizon_visibility_module
best time:     sunset
```

Camera Zone anchor:

```text
26.146118, 119.91321
```

The coordinate comes from the official-site place anchor, but tripod offset / exact standing-area extent remain pending, so WeatherGrid keeps it generalized.

## Official evidence

Matsu National Scenic Area official material states that:

- Jinsha is an old settlement characterized by a golden beach and stone houses;
- official itineraries recommend walking to Jinsha at dusk to watch sunset;
- the Jinsha / Jinren trail area provides broad sea-sky views.

Sources:

- https://www.matsu-nsa.gov.tw/zh-TW/attractions/1472
- https://www.matsu-nsa.gov.tw/zh-TW/trips/4
- https://www.matsu-nsa.gov.tw/zh-TW/trips/3032

## Subject geometry

B141 uses a conservative local envelope around the public Camera Zone:

```text
origin:  tw-065-VP01
azimuth: 0°–360°
range:   0–0.8 km
```

It covers the near settlement / beach context without claiming exact building or shoreline geometry.

## Sunset environment geometry

At latitude ~26.146°N, geometric annual sunset azimuth extremes are approximately 243.7°–296.3°. B141 pads this to:

```text
origin:  tw-065-VP01
azimuth: 240°–300°
range:   0–15 km
```

The sector represents sunset-atmosphere coverage only.

## Dynamic conditions remain separate

WeatherGrid does not decide temporary access, pedestrian conditions, marine safety, local haze/cloud obstruction, or actual sunset visibility.

## Registry result

```text
registry_version: B121.15 -> B121.16
entries:          41 -> 42
complete:         41 -> 42
needs_research:   0
```

## Provider result

```text
coverage_scope = place
coverage_id    = tw-065
```

## Guardrails

- no Place-center fallback;
- no exact settlement / beach polygon claim;
- no exact local-horizon claim;
- no Photography Opportunity scoring changes.

## Next work

After merge, run one live `place/tw-065` NOAA/NOMADS validation.
