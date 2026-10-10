# AGENTS.md — ChaseLights contributor and coding-agent rules

## Scope and source of truth
- This repository hosts **Legacy production** and an **isolated ChaseLights V2**. Do not change Legacy runtime, forecasts, scoring, navigation, web entry, or deployment as a side effect of V2 work.
- Before any V2 change read latest `main`, `RESEARCH_EVIDENCE_SPEC_R4_2.md`, `NAVIGATION_SPEC_R4_2.md`, `specs/v2/README.md`, applicable `specs/v2/` files, and relevant open PRs. The currently applicable spec on main takes precedence over old handoffs, chat instructions, stale PR text and old branch docs.
- Never infer that a branch, fixture or CI file is already merged. Verify GitHub HEAD, review state and actual check runs. Existing V2 W2/W3/W4 code may live **only on worker branches**, not main.

## V2 ownership and isolated work
| Owner | Paths |
|---|---|
| W1 | `specs/v2/` |
| W2 | `data/v2/` |
| W3 | `packages/core-v2/`, `packages/models-v2/` |
| W4 | `apps/web-v2/` |
| W5 / integration | `ops/v2/`, `.github/workflows/`, deployment, minimal verified Legacy-to-V2 link |

- Codex Cloud is a coding executor, **not a sixth autonomous worker**. For every task: identify the owning worker, inspect their latest branch and pending work, then create a *distinct codex task branch* from the appropriate existing code (not blindly main). Do not write to or force-push a worker's own branch. If another worker is concurrently changing the same files, stop and coordinate rather than overwrite or cherry-pick indiscriminately.
- One task = one clear code/test result and one PR. No auto-merge or deployment without verified checks and project-owner gates. Keep diffs narrow; preserve runnable failure logs and exact tested HEAD SHA.

## Data and scientific integrity
- Place-specific evidence proves **what** can be photographed; current weather/astronomy can estimate **when** an independently verified opportunity is feasible. Research readiness R0–R3 is **not** a current runtime favorable recommendation.
- Keep CameraContext, PhotographyTarget, ObservationRelation and NavigationTarget separate; do not assume dynamic-sky phenomena have a fixed geographic subject zone.
- Unverified position or access cannot produce directions. Never invent GPS, photo provenance, source URLs, coordinates, azimuth, distance, scientific thresholds, weather values or calibrated probabilities.
- If evidence, real provider coverage, freshness, required conditions or valid thresholds are absent, propagate UNKNOWN/NOT_EVALUABLE. Test-only fixtures are never live provider evidence; a source in the United States is not a Taiwan source.
- All user-visible semantic fields and UI strings must be fully and equivalently supported in zh-TW, en and ja. Automated key presence is not proof of semantic equivalence; request appropriate review where needed.

## Tests and completion
- Inspect existing tests first; execute applicable tests in the real checkout, e.g. `python -m unittest discover -s specs/v2/tests -p 'test_*.py' -v`, `python specs/v2/tests/validate_contract.py`, `python -m unittest discover -s packages/core-v2/tests -p 'test_*.py' -v`, and `node --test apps/web-v2/tests/*.test.mjs` **only when those paths exist in the task branch**.
- Report actual PASS, FAIL, SKIP and environment errors separately. Do not claim browser, integration, CI, live source, real evidence or public URL verification that was not performed.
- PR description must include: owning worker/paths, exact base and head SHA, files changed, tests with results, latest-main spec review, risks/unknowns and handoff to W5. If source and code are missing or permission denies an action, show the exact blocker rather than relaxing validation.
- Do not construct a Legacy/V2 automatic result comparison; project owner will spot-check.
