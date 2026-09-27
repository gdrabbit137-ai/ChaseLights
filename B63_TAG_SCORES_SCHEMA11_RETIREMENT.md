# ChaseLights R4.2 B63 — Schema 11 Published tag_scores Retirement

Date: 2026-09-27 (Asia/Taipei)

## Goal

Remove the redundant V4 `tag_scores` alias from newly published schema-11
per-Place detail shards.

This change is staged after:
- B59 removed current consumer dependence on `tag_scores`,
- B60 deployed a reader that accepts schema 11,
- B62 advances the writer to schema 11.

## Redundancy

Internal `fetch_data.py` still emits:

- `theme_scores: theme_scores`
- `tag_scores: theme_scores`

The second map is a compatibility alias of the first.

A prior complete-shard audit found the two maps equal on every sampled hourly
row and estimated the duplicate alias at roughly 9.6% of the raw largest
Taiwan sample at that checkpoint. Savings vary by Place.

## Publication boundary

The internal producer remains unchanged.

Only `analyze_weather._detail_hourly_projection()` removes `tag_scores`
before schema-11 detail shards are serialized. The same projection already
removes duplicated top-level `opportunity_runtime`.

Published hourly rows retain:
- `opportunity_scores`
- `theme_scores`

and omit:
- `opportunity_runtime`
- `tag_scores`

## Compatibility

The deployed frontend no longer reads `item.tag_scores`; current display
logic uses Opportunity scores first and retained `theme_scores` for Theme
compatibility.

Keeping the producer alias internally minimizes blast radius for debugging and
legacy internal code while preventing the duplicate from being transferred and
parsed by new clients.

## QA

Adapter regression verifies:
- internal/source rows may still contain `tag_scores`,
- published projection removes `tag_scores`,
- published projection retains `theme_scores` and `opportunity_scores`,
- top-level `opportunity_runtime` remains removed.

Taiwan, Japan and US Candidate Weather QA each require every generated
schema-11 detail row to:
- omit `tag_scores`,
- retain `theme_scores`.

Browser Smoke remains the end-to-end UI reader gate.

## Non-goals

B63 does not:
- remove internal producer `tag_scores`,
- remove `theme_scores`,
- change scoring or Opportunity admission,
- change access/navigation,
- change the schema beyond 11,
- change B61 US research content.

Full internal producer retirement can be considered later after the schema-11
publication path has been observed in production.
