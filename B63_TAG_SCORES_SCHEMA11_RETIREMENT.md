# ChaseLights R4.2 B63 — Schema 11 Published tag_scores Retirement

Date: 2026-09-27 (Asia/Taipei)

## Goal

Remove the redundant V4 `tag_scores` alias from newly published schema-11 detail shards.

This is intentionally staged after:
- B59 consumer deprecation, and
- B62 schema-11 writer migration.

## Why the field is redundant

Internal `fetch_data.py` still emits:

- `theme_scores: theme_scores`
- `tag_scores: theme_scores`

The two maps are the same compatibility data.

A previous full-shard audit of the then-largest Taiwan sample found:
- 96 hourly rows,
- both fields on all rows,
- `tag_scores == theme_scores` on all rows,
- roughly 9.6% of that raw detail payload attributable to the duplicate alias.

Exact savings vary by Place.

## Consumer boundary

The deployed frontend no longer reads `item.tag_scores`.

Current weather/detail consumers use:
- `opportunity_scores` for Opportunity-first output,
- `theme_scores` for retained Theme compatibility.

Therefore a new schema-11 payload does not need `tag_scores`.

## Publication boundary

Removal happens only in:

`analyze_weather._detail_hourly_projection()`

The internal fetch/scoring object remains unchanged for now.

The same projection already removes the duplicated top-level
`opportunity_runtime` map. B63 extends that publication-only cleanup to
`tag_scores`.

## QA

Adapter regression requires:
- source/internal hourly rows may still contain `tag_scores`,
- projected rows omit `tag_scores`,
- projected rows retain `theme_scores`,
- projected rows retain `opportunity_scores`,
- duplicated top-level `opportunity_runtime` remains absent.

Taiwan, Japan and US Candidate Weather QA require every schema-11 detail shard to:
- omit `tag_scores`,
- retain `theme_scores`.

Browser Smoke remains the end-to-end UI gate.

## Non-goals

B63 does not:
- remove internal producer `tag_scores`,
- remove `theme_scores`,
- change scoring,
- change Opportunity admission,
- change access/navigation,
- change summary payloads beyond B62,
- change schema beyond 11.

Internal producer cleanup can be considered later after the schema-11 publication path has been observed in production.
