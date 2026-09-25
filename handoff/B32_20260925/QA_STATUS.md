# B32 QA Status — jp-025 + Navigation Target correction

Date: 2026-09-25

| Gate | Result | Run |
|---|---|---:|
| Opportunity Adapter | PASS | 36100446591 |
| Japan Candidate Weather QA | PASS | 36100403517 |
| Browser Smoke | PASS | 36100369665 |
| Taiwan Candidate Weather QA | RUNNING / retry | 36100640799 |

## Navigation regression coverage

Browser Smoke passed checks that:
- 加羅湖 is `needs_review` and has no clickable keyword-search fallback.
- 南雅奇岩 is transitional `provisional_camera_anchor` and opens an exact-coordinate map pin.
- 等等力溪谷 is a `verified` Navigation Target and uses exact-coordinate Directions.
- 萩城下町・菊屋橫町 is a `verified` Navigation Target and uses exact-coordinate Directions.
- the former `map_query -> Google Maps search` construction is absent.

Adapter tests cover:
- all Places expose a valid `navigation_target.status`;
- verified targets must contain numeric coordinates;
- 加羅湖 does not export navigation coordinates while pending;
- weather summary/detail metadata carries `navigation_target`;
- browser cache accepts weather schema v10.
