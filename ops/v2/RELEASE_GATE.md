> Task R: current reviewed-main `f8a1f83bfeda5dc75f7e00c847e7728a0cef79ec`. The existing Research-only Preview is deployed; a live photography release is **NOT READY**. The current source-pinned technical gate is 169 tests (all previous 157 retained plus 12 W5 regressions), not the historical 123 count below. Hosting/environment protections and human/scientific gates are not implied by CI. Current executable plan and audit: `deployment_plan.json`, `release_readiness.py`, `reviews/TASK_R_RELEASE_READINESS.md`. This PR grants no merge/deploy permission.

# ChaseLights V2 — Release state, residual review and next gates

Last verified: 2026-10-12. Owner: W5 integration. This file is the **post-release state** of V2 Research-only Preview, not authority to enable live photographic forecasts, scores or Directions. Historical merge planning and reviewed pins remain in `ops/v2/INTEGRATION_CI.md` and `ops/v2/integration-sources.json`.

## Completed, verified deployment

- **Real GitHub main merged** the accepted W1 #450 → #457, W2 #440 → #444 → #456 → #458, W3 #435 → #441 → #447 → #459, W4 main-based #454 → #460, and W5 #461. Do **not** replay obsolete W4 #448 or older stacked W4 branches.
- Accepted W1–W5 main merge commit: `185bb6f2cddceb0a9c5a850f4b1df9cbbbbdc078`.
- **Actual post-merge main** GitHub Actions [38311276969](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38311276969): **123 PASS / 0 FAIL / 0 ERROR / 0 SKIP**, real-record provenance and Legacy-isolation checks. The earlier [38310763386](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38310763386) independently passed the 13-step detached merge rehearsal **and another 123 tests on the simulated merged tree**.
- GitHub Pages [38311277030](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38311277030) deployed V2. **Public URL verified:** https://chaselights.app/apps/web-v2/.
- Owner-authorized Legacy→V2 trilingual header entry merged in #463 and delivered by Pages [38312337784](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38312337784); permanent public V1→V2 smoke hardgate merged in #464.
- [Public smoke 38312808479](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38312808479): **public V1 entry PASS** and V2 Chromium desktop/mobile × zh-TW/en/ja **6/6 PASS**; actual HTTP/CSS/JS/JSON assets returned 200. Later WeatherGrid automatic data updates to main are **not** proof of V2 software changes.
- [Issue #453](https://github.com/gdrabbit137-ai/ChaseLights/issues/453) (orphaned W4 branch) and [#462](https://github.com/gdrabbit137-ai/ChaseLights/issues/462) (Preview publication) are closed after verified implementation.

## What is published and what remains pending

| Gate | Post-release status | Interpretation |
| --- | --- | --- |
| V1 production weather/runtime | **Unchanged** | V1 remains the original forecasting website; only a translated V2 entry was added. No automated V1/V2 comparison required. |
| V2 static website | **Published and smoke-tested** | Independent Research-only Preview; does not claim calibrated forecasts. |
| W2 Batch03 opportunities | **R1 / evidence_review** | One default research-preview opportunity in the public Catalog; three canonical candidate records remain in `data/v2/`. Their presence in GitHub is not human approval. |
| W2 legal Camera Area / navigation | **UNKNOWN / needs_review** | No asserted open camera polygon, arrival coordinates, or verified Directions for the three records. |
| Three-language automated UI checks | **PASS** | Key/display parity and six browser cases; **not** a human translation-semantic signoff. |
| Evidence scope and permitted shooting areas | **PENDING human review** | [Issue #465](https://github.com/gdrabbit137-ai/ChaseLights/issues/465). The independent 2026-10-12 source recheck is documented in `ops/v2/reviews/BATCH03_EVIDENCE_RECHECK_2026-10-12.md`. |
| W2 human semantic approval | **PENDING** | Keep `apps/web-v2/tests/fixtures/worker2/manifest.json` `human_semantic_signoff=PENDING`; do not assert an approver. |
| Live V2 meteorology, astronomical model and photography scoring | **NOT RELEASED** | No trusted live provider/issued-at/valid-at/coverage/threshold/approved AUTO binding; no selected-date FAVORABLE/score, fabricated probability or Navigation Directions. |

## Permanent product invariants

- Closed/restricted camera areas, viewpoints, access roads/trails, unclear lawful entry, opening hours and construction hazards are **visible independent Access Advisories, NOT photography REQUIRED/BLOCKER/QUALITY, score changes or environmental UNKNOWN gates**. Genuine environmental impossibility/hazards remain in the photographic condition contract. W2 keeps sourced zh-TW/en/ja warnings; W3 quarantines old ACCESS_SAFETY; W4 presents `access-advisories` as an independent section.
- A warning does not grant lawful access. No inferred Navigation Target from a Place name, photographed subject, WeatherGrid sample or camera location. No Directions without independently verified practical arrival-point evidence.
- Ordinary/free composition does **not** demand an exact tripod GPS; geometry is required only for geometry-specific claims. Dynamic events need not have fixed geographical target polygons.
- R4.2 place-specific evidence determines **what exists**; tested astronomical/weather models may later determine **when conditions are favorable**. UNKNOWN remains UNKNOWN; Research-only R1 is not a live recommendation.
- The published research Catalog must retain `research_only=true`, `forecast_available=false`, `selected_date_recommendation_eligible=false`, and `evaluations=[]` until independently authorized and verified.

## Next-development and regression requirements

1. Resolve [#465](https://github.com/gdrabbit137-ai/ChaseLights/issues/465) by source-scoped, claim-by-claim and **real human** zh-TW/en/ja review. Do not silently mark an evidence finding as a photography permission, exact Camera Zone or lawful Directions.
2. **Repin intentionally and retest** whenever any owner subtree or canonical opportunity changes. The original W5 `postmerge_verify.py` freezes the tested W1–W4 Git trees by design; proposed research or scientific updates will fail until an explicit new owner-approved tree pin, Source Manifest/Fixture/Catalog/Crosswalk sync (when canonical bytes change), and full 123+ case CI are reviewed. Never bypass checks by deleting provenance assertions or lowering test discovery thresholds.
3. Add real provider data, run/freshness/validity, phenomenon-specific scientifically justified thresholds, provenance and confidence separately from W2 research evidence. Never reuse synthetic/test data as forecast evidence.
4. Preserve Legacy, translated V2 link, public URL smoke, mobile/desktop browser coverage and source-safe Navigation. Every release must test **its own actual HEAD** and be verified publicly after Pages deployment.

Previous pre-merge restrictions such as “V2 must not be deployed” referred only to the **then-pending** PR stack; they must not be mistaken for the present published Research-only state. A new **live-forecast production** release still requires its own explicit scientific and human acceptance gates.
