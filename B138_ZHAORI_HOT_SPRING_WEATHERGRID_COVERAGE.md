# B138 — Zhaori Hot Spring Subject-aware WeatherGrid Coverage

Date: 2026-09-30 (Asia/Taipei)

## Goal

Make `tw-068` 朝日溫泉 an all-topic-complete WeatherGrid Place without changing Photography Opportunity scoring or pretending that WeatherGrid can decide seasonal opening hours, access, or whether the Sun is actually visible above the local horizon.

## Existing catalog contract

`tw-068-P01` is the canonical Opportunity:

```text
name:          朝日溫泉臨海日出
Camera Zone:   朝日溫泉臨海露天池觀景區
sampling:      directional_sector
formula:       needs_directional_horizon_dynamic_access_module
best time:     sunrise
```

The existing Camera Zone anchor is:

```text
22.63703, 121.50418
```

It is site-verified but has no reconstructable exact standing-area extent, so WeatherGrid keeps the Camera Zone generalized rather than inventing a pool/deck polygon.

## Official evidence

East Coast National Scenic Area official material states that:

- 朝日溫泉位於綠島東南海岸礁岩潮間帶；
- the site faces the Pacific Ocean;
- the seaside pools can be used to watch sunrise;
- the early opening window is seasonally adjusted to match sunrise.

Source:

- https://www.eastcoast-nsa.gov.tw/zh-tw/attractions/detail/95/

## Subject geometry

The photographed foreground is local: seaside hot-spring pools, immediate shore and intertidal rocks around the Camera Zone.

B138 intentionally does not invent exact pool, walkway, shoreline or intertidal polygons. It uses a conservative local envelope:

```text
origin:  tw-068-VP01
azimuth: 0°–360°
range:   0–0.5 km
```

This is a WeatherGrid coverage envelope, not a claim that every point inside the circle is a photographed subject.

## Sunrise environment geometry

At latitude ~22.637°N, the geometric annual sunrise azimuth extremes are approximately:

```text
summer solstice: ~64.5°
winter solstice: ~115.5°
```

B138 pads this to:

```text
origin:  tw-068-VP01
azimuth: 60°–120°
range:   0–15 km
```

The sector represents eastern dawn-atmosphere coverage only. It is not an exact visible-horizon mask, Sun ground coordinate, or guaranteed alignment.

## Dynamic conditions remain separate

WeatherGrid coverage does not decide:

- whether the attraction is open at the requested sunrise;
- whether access is currently permitted;
- whether cloud or local terrain blocks the Sun;
- whether sea spray, waves or on-site conditions are safe;
- whether the sunrise is actually visible from a specific pool position.

Those remain separate runtime/access/forecast concerns.

## Registry result

```text
registry_version: B121.12 -> B121.13
entries:          38 -> 39
complete:         38 -> 39
needs_research:   0
```

`tw-068` has one active Opportunity, so the Place becomes all-topic-complete.

## Provider result

B123 may safely request:

```text
coverage_scope = place
coverage_id    = tw-068
```

The provider bbox must contain the Camera Zone, local foreground envelope and eastward dawn sector while remaining smaller than the Taiwan regional bbox.

## Regression requirements

CI must prove:

1. registry count is 39;
2. `tw-068-P01` is provisional-complete;
3. the Camera Zone anchor is contained in coverage;
4. the eastward dawn sector materially expands the coverage bbox;
5. browser payload marks `tw-068` all-topic-complete;
6. subject and environment geometries are exported explicitly;
7. Camera Zone exposure remains generalized;
8. Place-scoped GFS fetch is safe and smaller than Taiwan-wide;
9. prior all-topic-complete Places remain complete;
10. Photography Opportunity scoring remains unchanged.

## Guardrails

- no Place-center fallback;
- no exact pool / shoreline / intertidal polygon claim;
- no exact local horizon claim;
- no assumption that sunrise visibility implies attraction access;
- no Photography Opportunity scoring changes.

## Next work

After merge:

- run one live `place/tw-068` scoped NOAA/NOMADS validation;
- continue with other single-Opportunity Places only when official evidence supports a conservative photographed-subject or horizon envelope;
- keep dynamic access and safety gates separate from WeatherGrid geometry.
