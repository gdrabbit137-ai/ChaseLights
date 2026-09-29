# B125 Liyu Lake All-topic WeatherGrid Coverage

Date: 2026-09-29

## Goal

Complete subject-aware WeatherGrid coverage for all ten active 鯉魚潭 (`tw-082`) Photography Opportunities so a Place-level scoped GFS request can safely cover every current subject and Camera Zone.

This batch keeps every entry `provisional`: the geometry is intentionally conservative and designed for weather-map coverage, not exact cartographic shoreline/trail/wildlife boundaries.

## Place-specific geometry basis

Existing ChaseLights research already establishes:

- official north-lakeside Camera Zone around `23.93493, 121.50803`;
- official Tannan wharf / south-lakeside reference around `23.9230, 121.5086`;
- individual researched Camera Zone extents for firefly, ecology, light-art, loop-trail, water-activity and wetland subjects;
- lake / reflection / surrounding-mountain / sunset / mist subjects in B33/B35.

The 花東縱谷國家風景區 official material additionally describes Liyu Lake as approximately:

- 1,640 m north-south;
- 930 m east-west;
- about 104 hectares;
- surrounded by mountains on three sides.

Official references:

- https://www.erv-nsa.gov.tw/zh-tw/attractions/detail/30
- https://theme.erv-nsa.gov.tw/edu/zh-tw/about/intro
- https://www.erv-nsa.gov.tw/file/2013/

## Conservative lake envelope

B125 derives a conservative broad lake bbox from the researched north/south waterfront anchors plus enough margin to exceed the official 1.64 km × 0.93 km dimensions:

```text
west   121.502625
south   23.920754
east   121.514005
north   23.937176
```

This is **not** an exact shoreline polygon.

It is intentionally oversized so WeatherGrid cannot crop a part of the lake surface relevant to reflection, mist or water activity.

## Immediate mountain context

For subjects that explicitly include surrounding mountains / partial mountain silhouettes, B125 uses a second conservative context bbox around the whole-lake envelope:

```text
west   121.473141
south   23.893805
east   121.543489
north   23.964125
```

The extra context is approximately 3 km around the lake envelope.

It is not a claim that every point inside the bbox is a photographed mountain. It is a safe weather-coverage envelope for the officially described three-sides-mountain setting.

## Opportunity coverage

### P01 — 湖光山景與平靜倒影

Coverage contains:

- Camera Zone;
- whole-lake water-surface envelope;
- immediate surrounding-mountain context;
- lake-surface weather zone for wind / precipitation.

### P02 — 湖光山色與水岸風景

Coverage contains:

- Camera Zone;
- whole lake;
- surrounding-mountain context.

### P03 — 日落、晚霞與湖面光影

Coverage contains:

- Camera Zone;
- whole lake;
- a conservative west-facing horizon sector:
  - azimuth 225°–315°;
  - range 0–20 km.

The sector is intentionally broader than the expected annual sunset azimuth range at Liyu Lake latitude so seasonal sunset/afterglow cannot be cropped.

### P04 — 春季螢火蟲生態

Uses a conservative 0.9 km full-circle subject zone around the researched firefly Camera Zone.

### P05 — 鳥類、水鳥與自然生態

Uses a conservative 1.8 km full-circle ecology subject zone around the researched wetland/ecology Camera Zone.

### P06 — 水岸光影節

Uses a conservative 0.6 km full-circle subject zone around the researched waterfront light-art Camera Zone.

### P07 — 環潭步道與森林步道

Uses a conservative 2.5 km full-circle subject zone around the researched trail Camera Zone.

### P08 — 遊湖與水上活動

Uses the full conservative lake envelope because boats / paddle / SUP subjects can move away from the wharf Camera Zone.

### P09 — 湖岸薄霧、低雲與山影

Coverage contains:

- Tannan wharf Camera Zone;
- whole lake;
- immediate surrounding-mountain context;
- the same broad mist environment zone.

### P10 — 人工濕地與水岸近景

Uses a conservative 1.8 km full-circle wetland / close-scene subject zone around the researched wetland Camera Zone.

## Why full-circle local zones are acceptable here

The radii are not invented from theme labels.

Each radius reuses the existing curated `geometry_extent_m` on that specific Liyu Lake Camera Zone.

For WeatherGrid coverage, using the full extent as a radius intentionally over-covers rather than risk cropping a subject.

The UI must continue to describe these as broad/provisional coverage, not exact public trails or exact subject positions.

## Registry result

After B125:

```text
weathergrid_coverage_registry_r4_2.json
registry_version = B121.3

entries = 26
provisional = 26
needs_research = 0
complete = 26
```

This count refers only to Opportunities currently migrated into the coverage registry, not all 384 catalog Opportunities.

## Place-level result

All ten current `tw-082` Opportunities now have complete provisional coverage.

Therefore B123 can safely create:

```text
coverage_scope = place
coverage_id = tw-082
```

without falling back to the Taiwan-wide bbox.

The resulting provider request still includes:

- all ten Camera Zones;
- all subject/environment envelopes;
- display padding;
- one GFS source-grid-cell interpolation halo;
- outward 0.25° provider-grid snapping.

## Guardrails

- no scoring changes;
- no exact shoreline claim;
- no exact mountain-silhouette claim;
- no exact wildlife position claim;
- no generic theme-to-geometry inference;
- no Place-center-only fallback counted as complete;
- all Camera Zone browser exposure remains generalized;
- broad coverage may be refined later without changing the Opportunity identity.

## Next work

After CI:

1. merge B124 first, then B125;
2. run a live `place / tw-082` scoped GFS fetch and compare it with the regional run on overlapping grid cells;
3. continue all-topic migration for 七星潭 and 清水斷崖;
4. then extend mountain/sunrise/sunset coverage to more Places.
