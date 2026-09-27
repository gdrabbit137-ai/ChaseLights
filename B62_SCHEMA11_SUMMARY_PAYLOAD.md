# ChaseLights R4.2 B62 — Schema 11 Summary Payload Migration

Date: 2026-09-27 (Asia/Taipei)

## Goal

Reduce published regional summary payloads while preserving the current Opportunity-first frontend contract.

This batch is intentionally staged after the schema-11 reader deployment from B60 reader-readiness work.

## Writer contract

The weather writer advances from schema 10 to schema 11 for both:

- `<region>_weather.json`
- `weather_details/<region>/<spot_id>.json`

Summary/detail are emitted from the same `base_meta`, so they remain the same generation and schema.

Schema 11 regional summaries omit:

`spots[*].daily[*].themes`

They keep:

- `daily[*].date`
- `daily[*].all`
- `daily[*].opportunities`

Internal `_build_day_summaries()` still constructs Theme summaries. The removal happens only in the publication projection.

## Why this is schema 11

The deployed frontend was intentionally prepared reader-first to accept schema 7 through 11 before any writer removal.

Although `daily.themes` is no longer consumed by the current frontend, removing a published compatibility field is still a payload-contract change. The staged migration therefore advances the writer to schema 11 rather than silently changing schema 10.

This supersedes the earlier draft conclusion in PR #110 that no schema bump was needed.

## Consumer audit

Current frontend:
- ranking reads `day.all`,
- Place Guide reads `day.opportunities`,
- no current frontend reader consumes `day.themes`.

The frontend already accepts schema 11.

## Stale-data behavior

Previous committed summary rows may still be schema-10-era rows containing `daily.themes`.

When provider fetch fails:
- previous summary rows are projected through the schema-11 summary projection,
- the retired `daily.themes` map cannot re-enter a new schema 11 publication through stale fallback,
- previous detail rows remain valid and are wrapped by the new schema-11 shard envelope.

## QA

Taiwan, Japan and US Candidate Weather QA each require:
- summary schema = 11,
- every detail shard schema = 11,
- no published summary day contains `themes`,
- summary/detail `updated_at` generation consistency remains intact where already checked,
- per-region active Place / research-migration contracts remain unchanged.

Adapter regression verifies:
- internal source day retains `themes`,
- publication projection removes only `themes`,
- `all` and `opportunities` survive unchanged,
- stale-summary projection cannot reintroduce the retired field,
- frontend max supported schema remains 11,
- writer schema is 11.

## Non-goals

B62 does not:
- remove top-level Place `themes`,
- remove detail-shard hourly `theme_scores`,
- remove staged producer `tag_scores`,
- change scoring or Opportunity admission,
- change runtime policy,
- change access or navigation,
- change US research migration.

The next detail-payload cleanup should be separately audited after the schema-11 writer is stable in production.
