# ChaseLights B60 — Schema 11 Reader-First Payload Migration Plan

Date: 2026-09-27 (Asia/Taipei)

## Purpose

Prepare a safe future payload cleanup without forcing old/cached frontend code to consume a new schema before the new reader has been deployed.

B60 is intentionally **reader-only**:
- frontend accepts schema 7 through 11,
- production weather writer remains schema 10,
- no generated weather field is removed in B60.

## B59 prerequisite

B59 removes all current production consumer dependence on the legacy `tag_scores` compatibility field:
- frontend weather modal uses `opportunity_scores -> theme_scores`,
- analysis/window helpers use `theme_scores`,
- producer still emits `tag_scores = theme_scores` during the compatibility window.

## Payload audit

### Detail shards — `tag_scores`

Current committed sample audit found:
- TW large shard: 96/96 rows had `tag_scores == theme_scores`; duplicate raw payload ~224 KB.
- JP large shard: 96/96 identical; duplicate raw payload ~125 KB.
- US large shard: 96/96 identical; duplicate raw payload ~314 KB.

The field is currently detail-only; regional summary payloads do not contain `tag_scores`.

### Summary payload — `daily[].themes`

Current frontend behavior:
- card score/display uses `daily[].all`,
- Place Guide uses `daily[].opportunities`,
- no current browser consumer reads `daily[].themes`.

Measured raw summary contribution at the audit checkpoint:
- Taiwan: ~1.00 MB of a ~2.11 MB summary (~47%),
- Japan: ~239 KB of a ~578 KB summary (~41%),
- US: ~731 KB of a ~929 KB summary (~79%).

US is especially wasteful because all US Places are still research-pending while legacy per-theme daily summaries remain published.

## Safe cutover sequence

1. Merge/deploy B59 so current consumers no longer depend on `tag_scores`.
2. Merge/deploy B60 so current frontend readers accept schema 11 while writer stays schema 10.
3. Observe at least one production release/cache turnover window.
4. In a later writer cutover:
   - bump generated summary/detail schema to 11,
   - remove duplicated `tag_scores` from published detail rows,
   - remove unused `daily[].themes` from published summaries,
   - preserve internal Theme metrics only where scoring still needs them,
   - update Candidate Weather and Browser Smoke contracts,
   - measure final committed payload reductions.
5. Keep schema 10 files readable by the schema-11-capable frontend during CDN/cache turnover.

## Non-goals

This migration must not:
- alter Opportunity scores,
- alter Theme compatibility scoring internally,
- alter runtime eligibility,
- alter event/access rules,
- remove `theme_scores` from detail rows,
- remove `daily[].opportunities` or `daily[].all`,
- change UI behavior.

The schema bump is a transport/payload contract change only.
