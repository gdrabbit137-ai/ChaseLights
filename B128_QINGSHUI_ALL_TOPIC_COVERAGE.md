# B128 Qingshui / Chongde All-topic WeatherGrid Coverage

Date: 2026-09-29

## Goal

Make 清水斷崖／崇德遊憩區 (`tw-034`) the fourth Place whose complete active Photography Opportunity set has subject-aware WeatherGrid coverage.

The three current Opportunities are:

1. `tw-034-P01` — 清水斷崖日出曙光
2. `tw-034-P02` — 清水斷崖山海遠眺
3. `tw-034-P03` — 清水斷崖晨霧、雲霧山海

P03 was already migrated. B128 adds P01 and P02.

No Photography Opportunity score changes are made.

## Official Place-specific basis

Taroko National Park explicitly describes Chongde Recreation Area / Chongde Trail as a Qingshui Cliff viewing area.

Official material says the Chongde platform:

- looks north toward Qingshui Cliff;
- overlooks the Pacific and its broad sea/sky scenery;
- is a current recommended place to view Qingshui Cliff;
- after reopening is promoted for the east-coast sunrise/dawn and moonlight sea.

Sources:

- https://www.taroko.gov.tw/ch/trailsAttractions/trail-list/40
- https://www.taiwan.nps.gov.tw/home/zh-tw/attractions/21010.html
- https://www.taroko.gov.tw/ch/trailsAttractions/attractions/8
- https://www.taroko.gov.tw/ch/titlelist/news/54

Therefore both the cliff/mountain subject and the Pacific/sunrise subject are Place-specific researched components, not geometry inferred only from a Theme label.

## P01 — cliff + Pacific dawn

P01 is not only a generic sunrise.

The canonical Condition Variant is:

```text
斷崖＋太平洋曙光
```

so WeatherGrid coverage must contain both:

1. the Qingshui Cliff / mountain coast;
2. the Pacific sunrise horizon.

### Cliff component

B128 reuses the already-researched P03 broad north-facing geometry:

```text
origin: tw-034-VP01
azimuth: 330°–30°
range: 0–5 km
```

This is a provisional broad subject sector, not an exact cliff polygon.

### Sunrise component

The Sun is celestial and receives no fake terrestrial coordinate.

At the Camera Zone latitude (~24.19°N), geometric sunrise azimuth over the annual solar-declination range is approximately:

```text
summer-solstice extreme  ~64.1°
equinox                  90.0°
winter-solstice extreme ~115.9°
```

B128 pads that to:

```text
azimuth: 60°–120°
range: 0–20 km
```

The 20 km range is a broad near-horizon marine-weather envelope. It is not the physical distance to the Sun.

The provider planner adds its own GFS interpolation halo beyond this geometry.

## P02 — Qingshui Cliff + Pacific mountain-sea view

Official Chongde Trail descriptions establish two simultaneous subjects:

- Qingshui Cliff to the north;
- Pacific sea / sea-sky panorama from the platform.

B128 therefore uses two Subject Geometries.

### North-facing cliff

```text
azimuth: 330°–30°
range: 0–5 km
```

### Pacific marine panorama

```text
azimuth: 30°–150°
range: 0–10 km
```

The second sector is deliberately over-covering. It prevents an east-facing Pacific composition from being cropped while exact shoreline/framing polygons remain uncurated.

Neither sector is presented as an exact visible-boundary polygon.

## Result

After B128:

```text
tw-034 catalog Opportunities = 3
coverage entries             = 3
all_topics_complete          = true
```

The all-topic-complete Place set becomes:

```text
tw-014  雲洞山莊觀景平台
tw-034  清水斷崖／崇德遊憩區
tw-036  七星潭
tw-082  鯉魚潭
```

B123 can therefore safely request:

```text
coverage_scope = place
coverage_id    = tw-034
```

without falling back to the full Taiwan bbox.

## Registry state

B128 advances the sidecar to:

```text
registry_version = B121.6
entries          = 31
provisional      = 31
complete         = 31
needs_research   = 0
```

These are migrated-entry counts, not full catalog coverage.

## Regression requirements

CI must prove:

1. P01/P02/P03 all resolve complete for `tw-034`;
2. P01 contains both cliff and sunrise geometry;
3. P02 contains both cliff and Pacific geometry;
4. browser payload reports `tw-034 all_topics_complete=true`;
5. B123 Place-scoped `tw-034` remains smaller than the Taiwan regional request;
6. `tw-014`, `tw-036`, and `tw-082` remain all-topic complete;
7. a genuinely incomplete Place such as `tw-035` still falls back region-wide;
8. scoring remains unchanged.

## Guardrails

- no fake Sun ground coordinate;
- no exact cliff polygon claim;
- no exact shoreline polygon claim;
- no assumption that one sector is the actual current camera framing;
- the provider request may over-cover, but must not under-cover the researched subject;
- Camera Zone remains browser-generalized;
- map coverage remains separate from scoring sample topology.

## Next work

1. live-run `place / tw-034` and compare overlapping GFS cells with the regional snapshot;
2. continue all-topic completion for Places with small remaining migration gaps;
3. prioritize directional sunrise/sunset and mountain panorama subjects with strong Place-specific evidence;
4. keep large multi-topic Places such as 六十石山 incomplete until every required subject is individually covered.
