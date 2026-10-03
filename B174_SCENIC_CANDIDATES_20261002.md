# Scenic candidate research — 2026-10-02

This batch implements two production candidates only. Reviewed Photography Opportunities, fail-closed navigation metadata, runtime catalog entries, manifest counts and regression coverage are required before merge.

## tw-085 南子吝步道 / Nanzilin Trail
- First-level admin area: 新北市.
- Official evidence: New Taipei City Travel explicitly describes the trail as a shutterbug location for sea sunrise, Keelung Mountain sunset, autumn/winter silvergrass, evening vehicle light trails and fishing lights; it also documents a 990 m trail, a 196 m viewing platform, 360-degree mountain/sea views, parking and trail facilities.
- Source: https://newtaipei.travel/en/attractions/detail/403532 (reviewed 2026-10-02).
- Opportunity work required: separate sunrise mountain-seascape, sunset toward Keelung Mountain, seasonal silvergrass, and evening light-trail variants. Do not infer silvergrass from weather alone.
- Navigation verified: New Taipei City Travel’s official How to Get There link resolves to the public arrival/trail-access destination at `25.1201398, 121.887539`. This is not promoted to a ridge Camera Zone.

## jp-036 高千穂峡 / Takachiho Gorge
- First-level admin area: 宮崎県.
- Official evidence: Takachiho Tourism Association documents the ~7 km gorge, columnar-joint cliffs, 17 m Manai Falls, ~1 km walking path, Takachiho Three Bridges photo point, and multiple official parking areas.
- Sources: https://takachiho-kanko.info/sightseeing/18/ and https://takachiho-kanko.info/boat/ (reviewed 2026-10-02).
- Dynamic-access evidence: the official association publishes daily boat operating state and current shuttle / construction notices. Boat operation must therefore remain dynamic and must not be inferred from ordinary weather.
- Opportunity work required: Manai Falls + gorge from walking-path viewpoint; boat-based falls composition as a separate access-gated variant; Three Bridges / columnar-joint composition.
- Navigation remains `multiple_access_routes`. The official tourism page links multiple named parking areas; its #1 Oshioi Parking link resolves to `32.7016613, 131.3003766`, which is used only as the Place/weather anchor, not as a universal Directions target or Camera Zone.

## Guardrails
- Evidence proves photographic subjects, not forecast success.
- Weather gates must remain subject-specific.
- Seasonal/event/access state is not fabricated from weather.
- Cross-boundary administrative metadata remains array-valued.


## Next researched candidates (IDs intentionally unallocated until branch is rebased)



## Duplicate-candidate reconciliation
The research backlog was checked against the current production catalog before further allocation:
- 三仙台 is already `tw-038`.
- 老梅綠石槽 is already `tw-073`.
- 白金青池 / Shirogane Blue Pond is already `jp-001` (美瑛青池).

These are not new candidates and must not receive new IDs.

## Batch-2 allocation note
The Washington candidates formerly staged here were reconciled against merged PR #323. Reflection Lakes is now covered by `us-082` and is intentionally removed from this branch to avoid duplicate production records. Allocate any remaining unassigned IDs only from the current main catalog.



## Batch 3 — researched candidates (IDs intentionally unallocated)


### Japan — 白米千枚田 / Shiroyone Senmaida
- First-level admin area: 石川県.
- Grade-A evidence: JNTO documents 1,004 terraced rice fields descending toward the Sea of Japan, multiple walking perspectives, a large parking lot beside the fields/rest house, and the recurring Aze no Kirameki winter illumination. JNTO's Noto guide explicitly highlights sunset with the terraces and illumination.
- Sources: https://www.japan.travel/en/spot/229/ and https://www.japan.travel/tw/spot/ma_88/ (reviewed 2026-10-02).
- Opportunity work required: rice-terrace/Sea-of-Japan landscape; sunset terrace composition; seasonal illumination as a separate event-state-gated Opportunity. Planting/harvest appearance and illumination dates MUST NOT be inferred from weather.
- Navigation work required: parking/rest-house arrival target can be researched independently; walking paths through the paddies remain Camera Zones.


## Batch-3 allocation note
Sunrise Point is now covered by merged PR #323 as `us-083` and is intentionally removed from this branch. Current main reserves Washington additions through `us-096`; no duplicate US IDs or records should be introduced here.


## Production implementation status
- `tw-085` Nanzilin Trail: admitted with three researched Opportunities (sunrise seascape, Keelung Mountain sunset, autumn/winter silvergrass). Silvergrass presence remains non-forecastable; navigation is `verified` at the official tourism arrival point `25.1201398, 121.887539`; exact ridge Camera Zone coordinates remain intentionally unfilled rather than guessed.
- `jp-036` Takachiho Gorge: admitted with three researched Opportunities (Manai Falls + gorge, Three Bridges, boat-level Manai Falls). Boat photography is fail-closed on official operating state; navigation remains `multiple_access_routes` because walking, parking and boat access differ.
- Washington duplicates were removed after PR #323: Reflection Lakes is `us-082`; Sunrise/Sunrise Point is `us-083`.
