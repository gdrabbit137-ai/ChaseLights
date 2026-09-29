# B124 WeatherGrid Coverage Expansion — Spatial Cloud-sea Batch

Date: 2026-09-29

## Goal

Continue the B121 subject-aware WeatherGrid migration using only geometry semantics that already exist in ChaseLights' spatial-weather runtime.

This batch does **not** infer new photographed subjects from terrain or generic theme labels.

## Added coverage

B124 adds provisional WeatherGrid coverage for these existing spatial-cloud Opportunities:

- `tw-004-P03` 不厭亭山谷雲海＋露出山頭
- `tw-008-P03` 硬漢嶺雲海
- `tw-014-P02` 雲洞山莊山谷雲海／雲瀑
- `tw-020-P02` 金龍山下方雲海＋晨曦
- `tw-022-P02` 二延平下方雲海／雲瀑＋茶園山稜
- `tw-023-P02` 頂石棹山凹雲海＋茶園山稜
- `tw-024-P02` 祝山日出雲海
- `tw-035-P06` 六十石山觀景點下方縱谷雲海
- `tw-040-P04` 排雲山莊下方雲海與山稜
- `tw-043-P03` 奇萊主稜雲海
- `tw-047-P01` 喜多麗秋冬雲海
- `tw-049-P03` 桃山雲海

Together with the existing `tw-019-P04`, these Opportunities already use ChaseLights' `lower_cloud_below_camera` spatial-weather topology.

## Geometry interpretation

For these Opportunities, the photographed phenomenon itself is the lower cloud / cloud-sea field below the Camera Zone.

The existing runtime profile samples an 8 km full ring around the Camera Zone. B124 reuses that same researched runtime topology as a broad:

```text
cloud_sea_subject_environment_zone
```

WeatherGrid coverage geometry.

This is intentionally **provisional**.

It means:

- the WeatherGrid includes the Camera Zone;
- the map includes the lower-terrain cloud-sea environment that the runtime already evaluates;
- the provider Fetch BBox includes the same broad weather-relevant subject zone;
- the map does not pretend to know the exact cloud boundary or exact visible foreground polygon.

## Why some spatial profiles are not migrated here

Not every Opportunity using `spatial_weather.py` is automatically safe to mark complete.

B124 deliberately excludes:

- `tw-004-P02` fog/mist — photographed valley/road composition still needs a dedicated subject extent;
- `tw-020-P03` glass-light city night — requires the lit basin/settlement subject, not only lower-cloud environment;
- `tw-023-P03` glass-light city night — same reason;
- `tw-043-P02` sunset cloud sea — still needs the sunset/horizon subject sector;
- `tw-047-P02` sunset cloud sea — still needs the sunset/horizon subject sector;
- `tw-032-P02` 見晴午後雲海 — current Camera Zone coordinate remains pending in the canonical catalog.

This is intentional. Existing weather sample geometry is not automatically equivalent to complete photographic-subject geometry.

## Registry state

The coverage registry advances from:

```text
B121.1
7 entries
4 complete/provisional
3 needs_research
```

to:

```text
B121.2
19 entries
16 complete/provisional
3 needs_research
```

The three explicit incomplete entries remain the initial 鯉魚潭 lake/reflection/sunset coverage items.

## Guardrails

- no production scoring changes
- no new subject invented from Theme or Scene
- no Place-center fallback counted as complete
- Camera Zone coordinates remain browser-generalized
- full-ring cloud-sea coverage is a planning envelope, not an observed cloud polygon
- Opportunities with additional required subjects remain unmigrated until those subjects are researched

## Next migration priority

The next subject-geometry batch should cover two categories:

1. 鯉魚潭 lake/reflection/mountain/sunset geometry
2. directional sunrise/sunset Opportunities where the actual horizon sector can be supported by existing Place-specific research

After that, Place-level scoped GFS fetches can begin becoming safe for Places whose entire Opportunity set has migrated.
