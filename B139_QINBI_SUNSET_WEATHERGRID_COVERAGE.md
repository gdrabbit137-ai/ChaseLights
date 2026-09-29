# B139 — Qinbi Village Sunset Subject-aware WeatherGrid Coverage

Date: 2026-09-30 (Asia/Taipei)

## Goal

Make `tw-067` 芹壁聚落 an all-topic-complete WeatherGrid Place without changing Photography Opportunity scoring or pretending that WeatherGrid can decide crowding, pedestrian access, local obstruction, or whether sunset is actually visible.

## Existing catalog contract

`tw-067-P01` is the canonical Opportunity:

```text
name:          芹壁石屋海灣夕照
Camera Zone:   芹壁聚落高台觀景區
sampling:      directional_sector
formula:       needs_directional_horizon_visibility_module
best time:     sunset
```

The existing Camera Zone anchor is:

```text
26.22478, 119.98366
```

It is site-verified but has no reconstructable exact standing-area extent, so WeatherGrid keeps the Camera Zone generalized rather than inventing a platform polygon.

## Official evidence

Matsu National Scenic Area official material states that:

- the high observation platform gives a representative view containing the stone houses and bay;
- sunset lights the bay and stone houses with a golden atmosphere;
- evening sunset is a classic photography time for Qinbi.

Source:

- https://matsu-nsa.gov.tw/zh-TW/attractions/1447

## Subject geometry

The photographed foreground is local: Qinbi's stone-house cluster and nearby bay as seen from the high platform.

B139 intentionally does not invent an exact village, building, shoreline or bay polygon. It uses a conservative local envelope:

```text
origin:  tw-067-VP01
azimuth: 0°–360°
range:   0–1.0 km
```

This is a WeatherGrid coverage envelope, not a claim that every point inside the circle is a photographed subject.

## Sunset environment geometry

At latitude ~26.225°N, the geometric annual sunset azimuth extremes are approximately:

```text
winter solstice: ~243.7°
summer solstice: ~296.3°
```

B139 pads this to:

```text
origin:  tw-067-VP01
azimuth: 235°–305°
range:   0–15 km
```

The sector represents western sunset-atmosphere coverage only. It is not an exact visible-horizon mask, Sun ground coordinate, or guaranteed alignment.

## Dynamic conditions remain separate

WeatherGrid coverage does not decide:

- whether local buildings or terrain block the Sun;
- whether the high platform is crowded or temporarily inaccessible;
- whether haze or cloud obscures the sunset;
- whether a specific composition is possible from a specific standing point.

Those remain separate runtime/on-site concerns.

## Registry result

```text
registry_version: B121.13 -> B121.14
entries:          39 -> 40
complete:         39 -> 40
needs_research:   0
```

`tw-067` has one active Opportunity, so the Place becomes all-topic-complete.

## Provider result

B123 may safely request:

```text
coverage_scope = place
coverage_id    = tw-067
```

The provider bbox must contain the Camera Zone, local stone-house/bay foreground envelope and westward sunset sector while remaining smaller than the Taiwan regional bbox.

## Regression requirements

CI must prove:

1. registry count is 40;
2. `tw-067-P01` is provisional-complete;
3. the Camera Zone anchor is contained in coverage;
4. the western sunset sector materially expands the coverage bbox;
5. browser payload marks `tw-067` all-topic-complete;
6. subject and environment geometries are exported explicitly;
7. Camera Zone exposure remains generalized;
8. Place-scoped GFS fetch is safe and smaller than Taiwan-wide;
9. prior all-topic-complete Places remain complete;
10. Photography Opportunity scoring remains unchanged.

## Guardrails

- no Place-center fallback;
- no exact village / building / shoreline / bay polygon claim;
- no exact local horizon claim;
- no assumption that favorable sunset weather guarantees a usable composition;
- no Photography Opportunity scoring changes.

## Next work

After merge:

- run one live `place/tw-067` scoped NOAA/NOMADS validation;
- continue migrating single-Opportunity Places only when official evidence supports a conservative photographed-subject or horizon envelope.
