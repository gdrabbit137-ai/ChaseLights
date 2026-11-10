# CL-DATA-58 fix notes (2026-11-10)

Defect (challenger round11): us-123-P01 / us-132-P01 / us-143-P01 carried
`water_surface_state` as REQUIRED+MAIN with unknown_policy propagate_unknown.
The evaluator maps it into `NO_SOURCE_METRICS` (packages/core-v2/tools/evaluate_batch.py),
so its verdict is always UNKNOWN/NO_LIVE_OBSERVATION_SOURCE; a REQUIRED UNKNOWN
makes every hour NOT_EVALUABLE — the subject could never be honestly evaluated
(permanent black-box card), and "lake frozen" seasonality had no evaluable
criterion at all.

Fix (per contract):
- `C-us-XXX-P01-02` water_surface_state: role REQUIRED→QUALITY,
  condition_tier MAIN→MODIFIER. It stays an honest advisory notice (no source
  exists; UNKNOWN propagates) but no longer gates any hour (QUALITY never
  gates; QUALITY UNKNOWN never produces NOT_EVALUABLE). Rationale updated to
  state the advisory semantics and the CL-DATA-58 change.
- New `C-us-XXX-P01-ICE1`: REQUIRED+MAIN temperature_2m gte 0 °C (freezing
  point of water, formula_derived; GFS temperature_2m binding). Ice-risk proxy
  for "lake frozen": any forecast hour below 0 °C fails the hour honestly.
  Applied year-round with no artificial month window — each lake's climate
  (Maroon Lake 2,884 m / Tahoe 1,897 m / Trillium Lake 1,158 m) is expressed
  by the forecast temperature itself, never by fabricated data.
- Reflection core criteria untouched (wind_speed_10m ≤2 m/s, light_window,
  precipitation).

Regen chain on the same branch: source-lock repin (3 records,
commit_sha = contract commit) → research_index build+validate
(--git-provenance PASS) → task-x fixture re-anchor (browse-query /
date-query index_revision) → build_web_catalog (552 opps) →
make_display_contracts → catalog_scoring (fingerprint only) → scoped
evaluate_batch --only-place-id us-123/us-132/us-143 (168h) spliced into
evaluations-latest.json + evaluations-details.

Post-fix evaluation (2026-11-10 09:58Z bundle): all three places evaluate
honestly — NOT_EVALUABLE hour count 0 for all 7 days; water_surface_state
day_verdict UNKNOWN (advisory, non-gating); ICE1 temperature_2m varies with
the real forecast (e.g. us-132-P01 FAIL all day 2026-11-17 cold snap;
us-143-P01 PASS 23/24 h on 2026-11-10) — honest verdicts, no fabrication.
