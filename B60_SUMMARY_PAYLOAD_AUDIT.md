# ChaseLights R4.2 B60 — Summary Payload Compatibility Audit

Date: 2026-09-27 (Asia/Taipei)

## Goal

Reduce published `<region>_weather.json` payloads without changing scoring,
Opportunity admission, runtime policy, detail-shard behavior, or frontend UI.

## Candidate audited

Published daily summary compatibility map:

`spots[*].daily[*].themes`

This is distinct from:
- top-level `spot.themes`, which remains useful metadata/filtering,
- detail-shard hourly `theme_scores`, which remains a compatibility scoring view,
- `daily[*].opportunities`, which is the authoritative Place Guide / Opportunity-first daily score map,
- `daily[*].all`, which is the authoritative daily winning Opportunity summary.

## Consumer audit

Current frontend:
- ranking reads `day.all`,
- Place Guide reads `day.opportunities`,
- no current frontend consumer reads `day.themes`.

Historical check:
- sampled B31-era frontend commits also showed no `day.themes` consumer.

Internal compatibility:
- `analyze_weather._build_day_summaries()` continues to construct Theme summaries,
- B60 removes them only in a publication projection,
- Theme scoring itself is unchanged,
- detail hourly `theme_scores` remains unchanged.

## Full-file size evidence

Current committed summary file sizes at the audit checkpoint:
- Taiwan: 2,114,054 bytes
- Japan: 577,923 bytes
- US: 929,291 bytes

The GitHub connector can parse the complete Japan and US JSON files. The Taiwan
summary exceeds the connector's full raw-file read limit, so no field-size
conclusion is made from a truncated Taiwan response.

Complete-file structural simulation (compact JSON serialization, removing only
`daily[*].themes`):

| Region | Before | After | Savings |
|---|---:|---:|---:|
| Japan | ~577 KB | ~337 KB | ~240 KB / **41.6%** |
| US | ~927 KB | ~194 KB | ~733 KB / **79.1%** |

US benefits disproportionately because all 70 US production Places remain
research-pending; their legacy daily Theme compatibility maps dominate the
summary even though they intentionally have no Opportunity recommendations.

Taiwan savings must be measured from generated B60 candidate output instead of
estimated from incomplete connector content.

## Publication contract

B60 adds `_summary_daily_projection()`:

- source/internal day objects retain `themes`,
- published summary day objects omit `themes`,
- `date`, `all`, and `opportunities` are preserved unchanged.

No schema-version bump is required because:
- the removed field is legacy compatibility output,
- current and checked historical frontends do not consume it,
- the authoritative Opportunity-first fields remain unchanged,
- no reader is required to reject a payload merely because the optional legacy
  daily Theme map is absent.

## QA

Adapter:
- verifies the projection removes only `themes`,
- verifies source/internal day objects retain the Theme map,
- verifies `all` and `opportunities` are unchanged.

Taiwan Candidate Weather:
- every published daily summary must omit `themes`.

Japan Candidate Weather:
- every published daily summary must omit `themes`.

Browser Smoke:
- must continue to validate ranking, Place Guide, date selection, weather modal,
  Japan region switch, and other existing frontend behavior.

## Non-goals

B60 does not:
- remove top-level Place `themes`,
- remove detail-shard `theme_scores`,
- change legacy scoring internals,
- activate US research-pending Places,
- alter Opportunity scores or winner selection.
