# B126 Liyu Lake All-topic WeatherGrid Coverage

Date: 2026-09-29

## Goal

Add 鯉魚潭 (`tw-082`) as the second Place whose entire active Photography Opportunity set has subject-aware WeatherGrid coverage, without regressing the existing first complete Place `tw-014`.

This batch is built on the B120 coverage contract, B123 provider-aware fetch planning, B124 cloud-sea migration, and the current B125 `tw-014` all-topic completion.

No photography scoring changes are made.

## Place-specific basis

Existing ChaseLights research already establishes:

- north-lakeside Camera Zone around `23.93493, 121.50803`;
- Tannan wharf / south-lakeside reference around `23.9230, 121.5086`;
- researched Camera Zone extents for firefly, ecology, light-art, loop-trail, water-activity and wetland subjects;
- lake / reflection / surrounding-mountain / sunset / mist subjects in B33/B35.

Official 花東縱谷 material describes Liyu Lake as approximately:

- 1,640 m north-south;
- 930 m east-west;
- about 104 hectares;
- surrounded by mountains on three sides.

References:

- https://www.erv-nsa.gov.tw/zh-tw/attractions/detail/30
- https://theme.erv-nsa.gov.tw/edu/zh-tw/about/intro
- https://www.erv-nsa.gov.tw/file/2013/

## Conservative whole-lake envelope

B126 uses an intentionally oversized broad bbox derived from the researched north/south waterfront anchors plus margins that exceed the official lake dimensions:

```text
west   121.502625
south   23.920754
east   121.514005
north   23.937176
```

This is not an exact shoreline polygon.

Its purpose is to ensure WeatherGrid cannot crop lake surface relevant to reflection, mist or water activity.

## Immediate mountain context

For Opportunities that explicitly include surrounding mountains or partial mountain silhouettes, B126 uses a second conservative context bbox:

```text
west   121.473141
south   23.893805
east   121.543489
north   23.964125
```

This adds roughly 3 km of context around the whole-lake envelope.

It is a weather-coverage envelope, not a claim that every coordinate inside the bbox is a photographed ridge.

## Opportunity coverage

### P01 — 湖光山景與平靜倒影

Contains:

- Camera Zone
- full lake water-surface envelope
- immediate surrounding-mountain context
- water-surface weather zone for wind / precipitation

### P02 — 湖光山色與水岸風景

Contains:

- Camera Zone
- full lake
- surrounding-mountain context

### P03 — 日落、晚霞與湖面光影

Contains:

- Camera Zone
- full lake
- broad west-facing horizon sector:
  - 225°–315°
  - 0–20 km

The horizon sector is deliberately broad so seasonal sunset / afterglow cannot be cropped.

### P04 — 春季螢火蟲生態

Uses a conservative 0.9 km full-circle subject zone around the researched firefly Camera Zone.

### P05 — 鳥類、水鳥與自然生態

Uses a conservative 1.8 km full-circle ecology subject zone.

### P06 — 水岸光影節

Uses a conservative 0.6 km full-circle waterfront light-art subject zone.

### P07 — 環潭步道與森林步道

Uses a conservative 2.5 km full-circle trail/environment subject zone.

### P08 — 遊湖與水上活動

Uses the full whole-lake envelope because boat / paddle / SUP subjects can move away from the wharf Camera Zone.

### P09 — 湖岸薄霧、低雲與山影

Contains:

- Tannan wharf Camera Zone
- full lake
- surrounding-mountain context
- the same broad mist environment zone

### P10 — 人工濕地與水岸近景

Uses a conservative 1.8 km full-circle wetland / close-scene subject zone.

## Why the local full-circle zones are permitted

The radii are not inferred from Theme labels.

Each radius reuses the existing curated `geometry_extent_m` for that specific Liyu Lake Camera Zone.

For WeatherGrid coverage, B126 intentionally treats the full extent as a conservative radius: over-coverage is preferable to cropping part of the researched subject.

These zones remain `provisional` and must not be presented as exact trail, wildlife or exhibit boundaries.

## Registry result

B126 advances the coverage sidecar to:

```text
registry_version = B121.4

entries = 27
provisional = 27
needs_research = 0
complete = 27
```

These counts refer only to migrated coverage entries, not all catalog Opportunities.

The existing `tw-014` coverage remains intact.

## Place-level result

Two Places now satisfy the B123 all-topic requirement:

```text
tw-014  雲洞山莊觀景平台
tw-082  鯉魚潭
```

For `tw-082`:

```text
catalog Opportunities = 10
coverage entries       = 10
all_topics_complete    = true
```

Therefore B123 may safely use:

```text
coverage_scope = place
coverage_id    = tw-082
```

and derive a smaller NOMADS request from the union of all ten Camera / Subject / Environment coverage plans.

## Regression requirements

CI must prove all of the following simultaneously:

1. `tw-014` remains all-topic complete;
2. all ten `tw-082` Opportunities are provisional-complete;
3. `tw-082` browser payload reports `all_topics_complete=true`;
4. `tw-082` Place-level B123 fetch remains scoped instead of falling back region-wide;
5. an actually unmigrated Opportunity such as `tw-036-P01` still falls back to the regional bbox;
6. scoring remains unchanged.

## Guardrails

- no Place-center-only coverage
- no exact shoreline claim
- no exact mountain-silhouette claim
- no exact wildlife position claim
- no generic Theme-to-geometry inference
- Camera Zone browser exposure remains generalized
- exact geometry can later replace these provisional over-covering envelopes without changing Opportunity identity

## Next work

After merge:

1. live-run `place / tw-082` with B123 and compare overlapping cells against the regional GFS run;
2. complete 七星潭 P01/P02 so `tw-036` becomes Place-scope safe;
3. complete 清水斷崖 P01/P02 so `tw-034` becomes Place-scope safe;
4. continue the same all-topic migration pattern across remaining Places.
