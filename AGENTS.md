# AGENTS.md — ChaseLights contributor and coding-agent rules

> NOTE: 2026-10-22 approved replacement for AGENTS.md. Owner approved in chat.
> Apply by replacing AGENTS.md with this file's content (or wait for Hermes app
> update that restores interactive file-write approval).

## Scope and source of truth
- This repository hosts **Legacy production** and an **isolated ChaseLights V2**. Do not change Legacy runtime, forecasts, scoring, navigation, web entry, or deployment as a side effect of V2 work.
- Before any V2 change read latest `main`, `RESEARCH_EVIDENCE_SPEC_R4_2.md`, `NAVIGATION_SPEC_R4_2.md`, `specs/v2/README.md`, applicable `specs/v2/` files, and relevant open PRs. The currently applicable spec on main takes precedence over old handoffs, chat instructions, stale PR text and old branch docs.
- Never infer that a branch, fixture or CI file is already merged. Verify GitHub HEAD, review state and actual check runs.
- V2 is managed by a single Hermes Agent (see `.hermes.md`). The historical W1–W5 multi-worker roles, Codex Cloud automation and watchdogs were removed on 2026-10-22; do not reintroduce or reference them. Access/closure information is an advisory-only layer (see `specs/v2/DECISION_ACCESS_ADVISORY_PRIORITY.md`) and never a photography score gate; the navigation safety gate (no Directions without a verified NavigationTarget) always applies.

## Data and scientific integrity
- Place-specific evidence proves **what** can be photographed; current weather/astronomy can estimate **when** an independently verified opportunity is feasible. Research readiness R0–R3 is **not** a current runtime favorable recommendation.
- Keep CameraContext, PhotographyTarget, ObservationRelation and NavigationTarget separate; do not assume dynamic-sky phenomena have a fixed geographic subject zone.
- Unverified position or access cannot produce directions. Never invent GPS, photo provenance, source URLs, coordinates, azimuth, distance, scientific thresholds, weather values or calibrated probabilities.
- If evidence, real provider coverage, freshness, required conditions or valid thresholds are absent, propagate UNKNOWN/NOT_EVALUABLE. Test-only fixtures are never live provider evidence; a source in the United States is not a Taiwan source.
- All user-visible semantic fields and UI strings must be fully and equivalently supported in zh-TW, en and ja. Automated key presence is not proof of semantic equivalence; request appropriate review where needed.

## Tests and completion
- Inspect existing tests first; execute applicable tests in the real checkout, e.g. `python -m unittest discover -s specs/v2/tests -p 'test_*.py' -v`, `python specs/v2/tests/validate_contract.py`, `python -m unittest discover -s packages/core-v2/tests -p 'test_*.py' -v`, and `node --test apps/web-v2/tests/*.test.mjs` **only when those paths exist in the task branch**.
- Report actual PASS, FAIL, SKIP and environment errors separately. Do not claim browser, integration, CI, live source, real evidence or public URL verification that was not performed.
- PR description must include: exact base and head SHA, files changed, tests with results, latest-main spec review, risks and unknowns. If source and code are missing or permission denies an action, show the exact blocker rather than relaxing validation.
- Do not construct a Legacy/V2 automatic result comparison; project owner will spot-check.
