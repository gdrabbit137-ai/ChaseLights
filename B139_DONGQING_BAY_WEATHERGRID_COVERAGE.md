# B139 — Dongqing Bay Subject-aware WeatherGrid Coverage

Date: 2026-09-30 (Asia/Taipei)

## Goal

Make `tw-069` 東清灣 an all-topic-complete WeatherGrid Place without changing Photography Opportunity scoring or pretending WeatherGrid can decide cultural photography permission, marine safety, access, or actual Sun visibility.

## Existing catalog contract

`tw-069-P01` is the canonical Opportunity:

```text
name:          東清灣海灣晨曦／拼板舟文化景觀
Camera Zone:   東清灣／東清港澳灘頭公共攝影區
sampling:      directional_sector
formula:       needs_directional_horizon_cultural_permission_module
best time:     sunrise
```

Camera Zone anchor:

```text
22.05299, 121.56363
```

It is site-verified but has no reconstructable exact standing-area extent, so WeatherGrid keeps the Camera Zone generalized.

## Official evidence

Taitung County official tourism material states that Dongqing Bay:

- is on the east side of Lanyu and is the island's largest bay;
- extends roughly 500 m;
- includes Dongqing Harbor, where many traditional tatala / pinban boats are kept;
- is a representative place to wait for sunrise and photograph changing dawn light with the blue bay and traditional boats.

The East Coast National Scenic Area travel guidance separately reminds visitors that photographing traditional boats / tribal cultural subjects should respect local culture and seek permission where appropriate.

Sources:

- https://tour.taitung.gov.tw/zh-tw/attraction/details/924
- https://media.taiwan.net.tw/zh-tw/portal/travel/details/attraction_376540000a_000391
- https://east.taiwan.net.tw/pwa/zh-tw/district/11/

## Subject geometry

The photographed foreground is local bay / harbor / shore / traditional-boat context around the Camera Zone. Because the official bay description is about 500 m long and no exact photographed polygon is curated, B139 uses:

```text
origin:  tw-069-VP01
azimuth: 0°–360°
range:   0–0.6 km
```

This is a conservative WeatherGrid envelope, not an exact beach, boat-position, harbor, or cultural-site polygon.

## Sunrise environment geometry

At latitude ~22.053°N, geometric annual sunrise azimuth extremes are approximately:

```text
summer solstice: ~64.6°
winter solstice: ~115.4°
```

B139 pads this to:

```text
origin:  tw-069-VP01
azimuth: 60°–120°
range:   0–15 km
```

The sector represents eastern dawn-atmosphere coverage only. It is not an exact visible-horizon mask or guaranteed solar alignment.

## Dynamic / cultural conditions remain separate

WeatherGrid coverage does not decide:

- whether photographing a traditional boat / cultural scene is permitted;
- whether a person, ceremony, or culturally sensitive activity may be photographed;
- whether marine or shore conditions are safe;
- whether cloud or local horizon obstruction blocks sunrise;
- whether access to a particular shore position is appropriate.

These remain separate permission, access, safety, marine, and runtime concerns.

## Registry result

```text
registry_version: B121.13 -> B121.14
entries:          39 -> 40
complete:         39 -> 40
needs_research:   0
```

`tw-069` has one active Opportunity, so the Place becomes all-topic-complete.

## Provider result

B123 may safely request:

```text
coverage_scope = place
coverage_id    = tw-069
```

The provider bbox must contain the Camera Zone, local bay/boat foreground envelope and eastward dawn sector while remaining smaller than the Taiwan regional bbox.

## Regression requirements

CI must prove:

1. registry count is 40;
2. `tw-069-P01` is provisional-complete;
3. Camera Zone anchor is contained in coverage;
4. the eastward dawn sector materially expands coverage;
5. browser payload marks `tw-069` all-topic-complete;
6. subject and environment geometries are exported explicitly;
7. Camera Zone remains generalized;
8. Place-scoped GFS fetch is safe and smaller than Taiwan-wide;
9. prior all-topic-complete Places remain complete;
10. Photography Opportunity scoring remains unchanged.

## Guardrails

- no Place-center fallback;
- no exact shore / harbor / boat-position polygon claim;
- no exact local-horizon claim;
- no claim that WeatherGrid grants cultural permission;
- no Photography Opportunity scoring changes.

## Next work

After merge:

- run one live `place/tw-069` scoped NOAA/NOMADS validation;
- continue with other single-Opportunity Places only when official evidence supports a conservative photographed-subject or horizon envelope;
- keep cultural permission, marine safety and access separate from WeatherGrid geometry.
