# B125 First All-topic Place WeatherGrid Coverage

Date: 2026-09-29

## Goal

Prove the complete Place-level coverage path required by B120/B123.

A Place-level WeatherGrid request may shrink from the regional bbox only when **every active Photography Opportunity at that Place** has complete subject-aware coverage.

B125 makes `tw-014` 雲洞山莊觀景平台 the first migrated Place that satisfies that rule.

## Existing Place model

`tw-014` has two active Opportunities:

1. `tw-014-P01` — 雲洞山莊觀景台層巒遠眺
2. `tw-014-P02` — 雲洞山莊山谷雲海／雲瀑

B124 already migrated P02 using the existing 8 km `lower_cloud_below_camera` spatial-weather ring.

B125 adds the missing P01 subject-aware coverage.

## Place-specific evidence for P01

The Taiwan tourism multimedia record supplied by 苗栗縣政府國際文化觀光局 states that 雲洞山莊 has a broad observation platform facing mountain ranges, overlooks 大湖 and 三義, and exposes layered mountain scenery.

Source:

https://media.taiwan.net.tw/zh-tw/portal/travel/details/attraction_376450000a_000941

The venue's own site likewise describes the elevated view over 大湖／三義 and the broad mountain landscape.

Source:

https://www.yundonghome.com/about_us.aspx

These sources establish the photographed subject as a broad layered-mountain panorama from the existing `tw-014-VP01` Camera Zone.

## Geometry decision

No exact visible-ridgeline polygon is currently curated.

Therefore B125 does **not** invent one.

Instead, P01 receives a deliberately conservative provisional subject envelope:

```text
origin: tw-014-VP01
type: full sector
range: 0–8 km
```

The 8 km radius is not a claim that every bearing is a photographed subject.

It reuses the existing researched 8 km spatial-weather topology already attached to P02 at the same Camera Zone. The full ring is used as an **over-covering WeatherGrid envelope** so the map cannot crop the nearby layered mountain terrain while precise visible ridgelines remain uncurated.

Status remains:

```text
provisional
```

## Why this is acceptable under B120

B120 requires the map to contain the subject; it does not require the default coverage geometry to be the minimum possible polygon.

For a provisional envelope:

- over-coverage is acceptable;
- under-coverage is not;
- the map must not present the 8 km ring as an exact visible ridge boundary;
- the Camera Zone remains the canonical existing viewpoint;
- scoring remains unchanged.

## Result

Coverage registry changes:

```text
B121.2 -> B121.3
19 entries -> 20 entries
16 complete/provisional -> 17 complete/provisional
3 needs_research -> 3 needs_research
```

For `tw-014` specifically:

```text
catalog Opportunities: 2
coverage entries:       2
complete/provisional:   2
all_topics_complete:    true
```

This makes `tw-014` the first Place where B123 may safely derive a Place-scoped provider Fetch BBox.

## B123 acceptance test

`test_weathergrid_fetch_plan.py` now requires:

```text
coverage_scope = place
coverage_id    = tw-014
```

to produce:

- `coverage_complete = true`
- `safe_to_scope = true`
- effective scope remains `place/tw-014`
- no missing registry entries
- one GFS/NOMADS request rectangle
- request width/height smaller than the full Taiwan regional request

This verifies the end-to-end policy:

```text
all Camera + subject/environment coverage complete
    -> union provider Fetch BBox
    -> outward GFS-grid snapping
    -> safe Place-scoped fetch
```

## Guardrails

- no Place-center-only coverage
- no invented exact ridgeline polygon
- no scoring changes
- no claim that the 8 km ring is the exact visible panorama
- Camera Zone remains browser-generalized
- a Place with even one unmigrated/incomplete Opportunity still falls back to regional fetch

## Next work

The next migration priority remains:

1. additional Places that are one or two Opportunities away from complete coverage;
2. researched sunrise/sunset horizon sectors;
3. 七星潭 P01/P02 celestial/horizon coverage;
4. 鯉魚潭 lake/reflection/mountain/sunset subject geometry;
5. continued expansion until Place-level scoped fetch becomes common rather than exceptional.
