# B32 QA Status — jp-026 continuation

Date: 2026-09-25

The `codex/jp026` continuation has passed all four release gates for the
26/35 Japan research checkpoint.

| Gate | Result | Run |
|---|---|---:|
| Opportunity Adapter | PASS | 36128165281 |
| Japan Candidate Weather QA | PASS | 36128522907 |
| Browser Smoke | PASS | 36128731623 |
| Taiwan Candidate Weather QA | PASS | 36128226766 |

## Time-window QA correction

The first Japan Candidate and Browser Smoke runs exposed assertions that
assumed every researched daylight Opportunity remained available on the
current partial day. After local daylight hours had elapsed, the runtime
correctly omitted those expired Opportunities.

The corrected gates now:
- allow a local day to contain only the researched Opportunities whose time
  windows remain viable;
- reject any Opportunity ID outside the curated Place contract;
- require the complete researched Opportunity set to appear across the
  forecast period;
- use tomorrow, a complete future local day, for deterministic browser score
  assertions.

## Navigation regression coverage

Browser Smoke verifies that:
- 加羅湖 is `needs_review` and has no clickable keyword-search fallback;
- 南雅奇岩 opens an exact-coordinate provisional map pin;
- 等等力溪谷 and 萩城下町 use verified exact-coordinate Directions;
- 出雲大社 is `multiple_access_routes` and exposes no misleading single route;
- free-text `map_query` is absent from production Navigation URLs.

Adapter and candidate tests cover:
- 26 researched Japan Places and 9 research-pending Places;
- all Places expose a valid `navigation_target.status`;
- verified targets contain numeric coordinates;
- weather summary/detail metadata carries `navigation_target`;
- schema v10 and the 26/35 Opportunity catalog remain consistent.
