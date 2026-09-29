# B121 WeatherGrid Coverage Migration — Batch 01

Date: 2026-09-29

## Goal

Start moving the B120 subject-aware WeatherGrid coverage contract from specification into curated runtime data without inventing geometry.

This batch uses a sidecar registry:

```text
weathergrid_coverage_registry_r4_2.json
```

The sidecar is keyed by `opportunity_id` and overlays `weather_coverage` onto the existing authoritative Opportunity catalog. Existing `viewpoints[]` remain the canonical Camera Zone source.

The sidecar approach keeps the first migration auditable and avoids rewriting the large runtime catalog before the geometry contract is proven.

## Batch contents

### `tw-034-P03` — 清水斷崖晨霧、雲霧山海

Status: `provisional`

Coverage uses:

- Camera Zone: `tw-034-VP01`
- broad north-facing subject sector: 330° → 30°, 0–5 km
- directional mist environment sector: 330° → 30°, 2.5–5 km

These directions/ranges reuse the existing Qingshui directional-mist runtime contract and documented official north-facing viewing interpretation.

They are **not** an exact cliff polygon.

### `tw-036-P03` — 七星潭北望清水山／清水斷崖＋貼山雲帶

Status: `provisional`

Coverage uses:

- Camera Zone: `tw-036-VP01`
- subject sector: 350° → 20°, 8–22 km
- terrain-attached-cloud environment sector: same broad sector

This directly reuses the existing B83/B85 spatial-weather contract. The subject itself has Grade-A place-specific evidence, while the sector is intentionally broad and does not claim exact cloud/ridge overlap.

### `tw-036-P04` — 七星潭北望清水斷崖／清水山山海遠眺

Status: `provisional`

Coverage uses the same researched 350° → 20°, 8–22 km broad northward mountain-view sector.

### `tw-019-P04` — 合歡主峰下方雲海與露出群峰

Status: `provisional`

Coverage uses:

- Camera Zone: `tw-019-VP01`
- existing full 8 km lower-terrain spatial-weather ring as an Environmental Geometry

The ring is a weather sampling/coverage zone, not an observed cloud-sea boundary.

### `tw-082-P01/P02/P03` — 鯉魚潭倒影／湖光山色／日落

Status: `needs_research`

Camera Zones are already known, but the following photographed-subject geometry has not yet been curated precisely enough:

- lake-surface footprint
- reflected/surrounding mountain subject extent
- sunset/horizon sector

B121 records these as explicitly incomplete instead of pretending the Camera Zone or Place center covers the photographed subject.

This is intentional and directly enforces the user's product requirement.

## Audit contract

`audit_weathergrid_coverage.py` validates the sidecar against the current runtime catalog.

Expected Batch 01 result:

- entries: 7
- provisional: 4
- needs_research: 3
- complete subject-aware coverage plans: 4
- explicit incomplete plans: 3
- missing Opportunity IDs: 0

`needs_research` is migration work, not a CI failure.

Structural problems **are** CI failures, including:

- unknown Opportunity ID
- broken Camera Zone reference
- invalid geometry
- registry/catalog spot mismatch
- duplicate registry entries

## Coverage planner

`weathergrid_coverage.py` now supports:

- point / bbox / polygon / sector / corridor geometry
- Camera Zone resolution
- antimeridian-aware envelopes
- Opportunity coverage bbox
- padded viewport bbox
- provider fetch bbox
- one GFS-grid-cell provider halo for interpolation
- Place-level union of multiple Opportunity coverage plans
- sidecar registry overlay + audit

It remains completely separate from Photography Opportunity scoring.

## Why the first batch is deliberately small

The first migration includes topology types that already have strong geometry semantics in the repository:

- directional coast/mountain view
- directional mist
- cloud-sea environmental ring
- intentionally incomplete reflection/lake coverage

This tests both positive coverage and explicit incompleteness before hundreds of Opportunities are migrated.

## Next batch

B121 Batch 02 should curate photographed-subject geometry for:

1. 鯉魚潭 lake/reflection/sunset coverage
2. additional mountain panorama Opportunities
3. sunrise/sunset horizon sectors with researched direction/range
4. coastal/offshore subjects
5. reflection/water-surface subjects

No geometry should be inferred solely from Theme, Scene, Place center or generic terrain shape.
