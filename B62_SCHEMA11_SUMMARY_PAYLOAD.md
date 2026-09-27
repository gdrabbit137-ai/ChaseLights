# ChaseLights R4.2 B62 — Schema 11 Summary Payload Migration

Date: 2026-09-27 (Asia/Taipei)

## Goal

Complete the reader-first payload migration by advancing newly published weather
files to schema 11 after the frontend was already prepared to accept schema 11.

B60 removed the legacy published daily Theme compatibility map from regional
summaries. This batch makes that payload-contract change explicit in the writer
version instead of silently continuing to label the new shape as schema 10.

## Writer contract

The weather writer now emits schema 11 for both:

- `<region>_weather.json`
- `weather_details/<region>/<spot_id>.json`

Summary and per-Place detail shards share the same `base_meta`, therefore a
single generation keeps the same schema and `updated_at` across both sides.

Regional summaries keep:
- `daily[*].date`
- `daily[*].all`
- `daily[*].opportunities`

and continue to omit:
- `daily[*].themes`

Internal `_build_day_summaries()` still constructs Theme summaries for
internal/regression compatibility. The omission is a publication projection.

## Why schema 11

The deployed B60 reader-readiness change already accepts schemas 7 through 11.

Removing a published compatibility field is still a payload-shape change even
when the current UI no longer consumes that field. Advancing the writer to
schema 11 preserves the intended reader-first migration boundary and avoids
having two different published shapes both labeled schema 10.

## Stale fallback

Older committed summary rows may still contain `daily.themes`.

When a provider fetch fails, the existing summary projection is applied before
the stale row is republished, so a schema-10-era fallback cannot reintroduce the
retired field into a new schema-11 summary.

Detail fallback rows remain wrapped by the current schema-11 shard envelope.

## QA

Taiwan, Japan and US Candidate Weather QA require:
- regional summary schema = 11,
- every generated detail shard schema = 11,
- published summaries continue to omit `daily.themes`,
- existing region-specific catalog/research boundaries stay unchanged.

Adapter regression requires:
- frontend maximum supported schema remains 11,
- writer declares schema 11,
- the summary publication projection still preserves `all` and
  `opportunities` while removing only the retired daily Theme map.

Browser Smoke remains the end-to-end reader gate.

## Non-goals

B62 does not:
- remove top-level Place `themes`,
- remove hourly `theme_scores`,
- remove published `tag_scores` yet,
- change scoring or Opportunity admission,
- change access/navigation,
- change B61 US research content.

Published `tag_scores` retirement is a separate post-schema-11 cleanup.
