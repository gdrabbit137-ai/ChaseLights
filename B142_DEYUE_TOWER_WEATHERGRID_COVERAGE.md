# B142 — Deyue Tower Subject-aware WeatherGrid Coverage

Date: 2026-09-30 (Asia/Taipei)

## Goal

Make `tw-062` 水頭聚落・得月樓 an all-topic-complete WeatherGrid Place without changing Photography Opportunity scoring or inventing exact building, property, tripod, lighting, or access geometry.

## Existing catalog contract

`tw-062-P01`:

```text
name:          得月樓與水頭洋樓建築外觀
Camera Zone:   得月樓／黃輝煌洋樓公共外觀視點
sampling:      local_area
formula:       needs_lighting_state_module
best time:     daylight/golden hour
```

Camera Zone anchor:

```text
24.40971, 118.29849
```

The coordinate is a working building-area/public-exterior anchor. Exact tripod extent is not curated, so the Camera Zone remains generalized.

## Official evidence

Kinmen Travel official material confirms that:

- Deyue Tower and Huang Huihuang Western-style House are major landmarks within Shuitou settlement;
- the two buildings represent the overseas-influenced architectural character of the settlement;
- both landmarks were restored and reopened to visitors after structural and exhibition work.

Sources:

- https://kinmen.travel/zh-tw/travel/attraction/654
- https://kinmen.travel/zh-tw/travel/attraction/520
- https://www.kinmen.travel/zh-tw/news/details/4191

## Subject geometry

B142 uses a conservative local envelope:

```text
origin:  tw-062-VP01
azimuth: 0°–360°
range:   0–0.3 km
```

This covers the immediate Deyue Tower / Huang Huihuang Western-style House / Shuitou architectural cluster without claiming an exact building footprint, property boundary, private area, or tripod polygon.

## Environment geometry

None.

This Opportunity is a local architectural subject. WeatherGrid does not need a directional sunrise/sunset horizon sector merely because golden hour may improve the light.

Golden-hour quality and night illumination belong to the pending lighting-state module rather than spatial WeatherGrid coverage.

## Dynamic conditions remain separate

WeatherGrid does not decide:

- whether interiors are open;
- whether decorative/night lighting is active;
- whether temporary access restrictions apply;
- whether crowds or local obstructions affect a composition;
- whether golden-hour light actually reaches the chosen facade.

## Registry result

```text
registry_version: B121.16 -> B121.17
entries:          42 -> 43
complete:         42 -> 43
needs_research:   0
```

`tw-062` has one active Opportunity, so the Place becomes all-topic-complete.

## Provider result

B123 may safely request:

```text
coverage_scope = place
coverage_id    = tw-062
```

The provider bbox must contain the public Camera Zone and remain a compact local request substantially smaller than the Taiwan regional bbox.

## Regression requirements

CI must prove:

1. registry count is 43;
2. `tw-062-P01` is provisional-complete;
3. the Camera Zone anchor is contained in coverage;
4. exactly one subject geometry exists;
5. no environment geometry is added;
6. the local coverage bbox stays compact;
7. browser payload marks `tw-062` all-topic-complete;
8. Camera Zone exposure remains generalized;
9. Place-scoped GFS fetch is safe and smaller than Taiwan-wide;
10. prior complete Places remain complete;
11. Photography Opportunity scoring remains unchanged.

## Guardrails

- no Place-center fallback;
- no exact building / parcel polygon claim;
- no fake sunrise/sunset sector;
- no assumption that favorable weather means facade lighting is active;
- no Photography Opportunity scoring changes.

## Next work

After merge:

- run one live `place/tw-062` NOAA/NOMADS validation;
- continue with another single-Opportunity Place only when the photographed subject geometry can be conservatively supported by reliable evidence.
