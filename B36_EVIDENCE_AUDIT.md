# B36 Opportunity Evidence Audit — Initial Queue

Generated from the production Opportunity catalog using `audit_opportunity_evidence.py`.

## Scope

This audit does **not** declare an Opportunity false.

It asks a narrower question:

> For evidence-sensitive photographic subjects, does the current runtime catalog contain machine-verifiable Place-specific provenance that proves the subject exists at that Place?

Initial calibrated baseline:

- Opportunities: 251
- documented high-risk: 2
- review_required high-risk: 76
- lower-risk legacy: 173

After Batch 01A evidence backfill:

- Opportunities: 251
- documented high-risk: 7
- review_required high-risk: 71
- lower-risk legacy: 173

Batch 01A newly verified five cloud-sea Opportunities: tw-001-P02, tw-004-P03, tw-008-P03, tw-014-P02, tw-019-P04.

The low documented count primarily reflects historical catalog schema: older Opportunities were researched before explicit provenance fields were standardized. B36 converts that historical research debt into a review queue.

## Review queue by risk class

| Risk class | Review items |
|---|---:|
| reflection | 22 |
| cloud_sea | 18 |
| astro | 12 |
| mist | 8 |
| seasonal_flora | 6 |
| wildlife | 5 |
| snow_ice | 4 |
| waterfall | 3 |
| event | 2 |
| sunbeam | 1 |

An Opportunity may appear in more than one risk class, so risk-class totals can exceed the number of unique review items.

## Priority order

### Batch 1 — mist / cloud sea

Start here because fog/mist/cloud-sea claims are especially easy to infer incorrectly from elevation, terrain, humidity, cloud base or low visibility.

Review targets include:

- tw-001-P02 大屯山台北盆地下方雲海
- tw-004-P02 不厭亭山谷雲霧層次
- tw-004-P03 不厭亭山谷雲海＋露出山頭
- tw-008-P03 觀音山硬漢嶺雲海
- tw-014-P02 雲洞山莊山谷雲海／雲瀑
- tw-019-P04 合歡主峰下方雲海與露出群峰
- tw-020-P02 金龍山下方雲海＋晨曦
- tw-021-P02 武界高山茶園下方雲海／雲瀑
- tw-022-P02 二延平下方雲海／雲瀑＋茶園山稜
- tw-023-P02 頂石棹山凹雲海＋茶園山稜
- tw-024-P02 祝山日出雲海
- tw-025-P01/P02 二寮霧氣／層巒題材
- tw-031-P02 抹茶山雲霧層巒
- tw-032-P02/P03 見晴雲海／雲霧森林
- tw-035-P06 六十石山縱谷雲海
- tw-040-P04 玉山排雲山莊下方雲海
- tw-043-P02/P03 奇萊主稜雲海
- tw-044-P03 南湖圈谷霧淞／雪景
- tw-047-P01/P02 北大武山喜多麗雲海
- tw-049-P03 桃山雲海
- tw-053-P02 杉林溪青龍瀑布＋森林水景
- tw-056-P01 松蘿湖湖面＋草澤森林晨景

For each item, classify:
- **verified**: Place-specific Grade A/B evidence proves the subject.
- **narrow_scope**: subject is valid but only for a more specific Camera Zone / season / direction.
- **insufficient_evidence**: keep research-pending; do not let terrain/weather prove existence.
- **remove_or_rewrite**: evidence contradicts or does not support the current subject claim.

### Batch 2 — reflection

Review 22 reflection / mirror-like composition claims. Confirm that the geometry and legal Camera Zone support the reflection composition; calm wind alone is not evidence.

### Batch 3 — astro

Review 12 Milky Way / star-field claims. Confirm legal nighttime access, horizon/orientation and Place-specific photographic evidence; low light pollution alone is not sufficient.

### Batch 4 — biological / seasonal / event

Review seasonal flora, wildlife/fireflies and recurring events against official schedules, habitat records or repeated Place-specific observations.

### Batch 5 — waterfall / snow / sunbeam

Review water-flow claims, snow/ice compositions and crepuscular-ray subjects. These require direct Place-specific evidence plus explicit separation between subject existence and forecast conditions.

## Enforcement phases

1. **B36 discovery mode** — current phase. Audit reports `review_required` but does not block production.
2. **Provenance backfill** — add evidence status/grade/scope/source metadata to reviewed Opportunities.
3. **New-Opportunity gate** — CI rejects newly added high-risk Opportunities without explicit provenance.
4. **Legacy gate** — after backlog is reviewed, optionally require all production high-risk Opportunities to be documented.

## Important boundary

Weather can say conditions are favorable for an already verified subject.

Weather cannot prove the subject exists.
