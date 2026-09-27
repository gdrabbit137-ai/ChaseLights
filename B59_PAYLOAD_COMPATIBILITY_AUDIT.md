# ChaseLights R4.2 B59 — Published Detail Compatibility / Payload Audit

Date: 2026-09-27 (Asia/Taipei)

## Scope

B59 removes one proven duplicate from published per-Place weather detail shards:

- keep `theme_scores`,
- keep `opportunity_scores`,
- keep internal `fetch_data.py` V4 compatibility output,
- omit the published `tag_scores` alias because it is byte-for-byte the same object as `theme_scores`.

This change does not alter scoring, Opportunity runtime diagnostics, summary ranking, or the internal fetch/scoring pipeline.

## Evidence that tag_scores is redundant

`fetch_data.py` currently emits:

- `theme_scores: theme_scores`
- `tag_scores: theme_scores` (V4 compatibility alias)

A full-blob audit of the largest current Taiwan detail sample at the checkpoint,
`weather_details/tw/tw-082.json`, found:

- 96 hourly rows,
- `theme_scores` present on 96/96 rows,
- `tag_scores` present on 96/96 rows,
- `tag_scores == theme_scores` on 96/96 rows,
- serialized `tag_scores` content was about 193k characters,
- roughly 9.6% of that raw detail payload was attributable to the duplicate tag-score map.

The exact byte reduction varies by Place because the number of Themes and
Opportunities differs.

## Frontend compatibility audit

Current frontend lookup order is:

`opportunity_scores -> theme_scores -> tag_scores`

Historical inspection shows this was already true at the B29 R4.2 Place Guide
merge on 2026-09-24.

The immediate pre-B29 parent also already used:

`theme_scores -> tag_scores`

No Service Worker / CacheStorage implementation exists in this repository, so
there is no repository-controlled long-lived application shell that requires
`tag_scores` as its only hourly score source.

The fallback read of `tag_scores` remains in the frontend for compatibility
with older detail payloads. B59 removes the redundant field only from newly
published detail shards.

## Publishing boundary

The removal is implemented in:

`analyze_weather._detail_hourly_projection()`

The internal `fetch_data.py` object is intentionally unchanged. This preserves
debug/internal compatibility and minimizes the blast radius.

B55 already removes the duplicated top-level `opportunity_runtime` map in the
same projection layer. B59 extends this principle to the V4 `tag_scores` alias.

## QA contract

Regression coverage requires:

- source/internal rows may still contain `tag_scores`,
- projected detail rows must omit `tag_scores`,
- projected detail rows must retain `theme_scores`,
- Opportunity runtime diagnostics remain nested under
  `opportunity_scores[opportunity_id].runtime`,
- Taiwan Candidate Weather verifies all published Taiwan shards,
- Japan Candidate Weather verifies all published Japan shards,
- Browser Smoke verifies the real weather modal still renders through the
  `opportunity_scores -> theme_scores -> tag_scores` compatibility chain.

## Separate summary-payload finding

B59 audit also inspected the complete current Taiwan summary blob rather than a
truncated connector excerpt.

At the audit checkpoint the raw `tw_weather.json` content was about 2.0 MB.
Approximate serialized field shares were:

- per-Place `daily`: ~80.0% of the whole summary,
- top-level per-Place `opportunities`: ~13.0%,
- other metadata: comparatively small.

Inside the 249 daily entries:

- `daily.themes`: ~48.6% of the entire summary,
- `daily.opportunities`: ~18.9%,
- `daily.all`: ~11.8%.

This makes `daily.themes` the next major payload candidate, but it is NOT
removed in B59. It requires a separate consumer/schema compatibility audit.

Current product frontend uses `day.all` for Place ranking and
`day.opportunities` for Opportunity ordering/guide display. No removal of
`daily.themes` should occur until repository and historical-client compatibility
are explicitly validated.
