# W5 bounded executor: main-based safety consolidation (2026-10-20)

**Current branch status: Draft / disabled.** This is a prerequisite review,
not permission to run a billable OpenAI call or to publish any generated code.

- Reviewed main at integration time: `20dff7cf087d91799e18a06ca2d4e9e3a58fbf9e`; active W5 main-based
  Open-Meteo pilot via #525, **444-case** merged-tree acceptance.
- Source immutable Task P #497 HEAD `bec25989330f1dec555b29c86e0d65f6b95e43c3`
  plus Task T #499 HEAD `27bc6d1aed763d71e7738e6f52a26fe794146c3a`.
- Import **only previously absent W5-owned files** from Task T, byte-for-byte,
  then minimally adjust the check string to the actual **444-case** job.
  Do not copy historical `ops/v2/integration-sources.json`,
  `postmerge_verify.py`, current `v2-integration.yml` or any W1–W4,
  Legacy or WeatherGrid files. Do not replay old stacked PRs.
- Executor remains **manually dispatched only** (no scheduled trigger).
  `policy.json` and `single-pilot-policy.json` remain `enabled=false`.
- Existing cost rule for `gpt-6.1-sol` Standard: input USD 2.00/M,
  cache write USD 2.50/M, output USD 10.00/M. Total worst-case
  reserved USD 0.705056 versus USD 0.75 limit, one lifetime model
  request, zero retries. Verify live model entitlement/price anew.
  Price review in the imported disabled policy **expired 2026-10-16**;
  must be renewed in a *later owner-reviewed activation PR*, not patched
  open or assumed valid.
- Current main GitHub branch status from GET: `protected=false`;
  rulesets `[]`. Pre-activation FAIL CLOSED. Repository Actions
  variables/secrets, App install effective permissions and OpenAI
  billing configuration are **UNVERIFIED**, not presumed absent.
- **No paid OpenAI request, workflow dispatch, model-generated output,
  model-linked GitHub PR, main merge, deployment or background
  unattended coding has happened in this change.**

## Required independent gates

1. Review actual complete diff and verify only W5 ownership.
2. At PR exact HEAD, GitHub Actions: bounded executor/security tests,
   legacy offline gate, full modern **444/444** W1–W5 Integration and
   available Release Readiness/Schema checks, without a SKIP substitute.
3. Keep this candidate Draft until owner approval. GitHub main
   protection/rules without App bypass must be active before *any*
   live activation.
4. Owner verifies GitHub App installation with repository-only permissions
   (Contents/Pull requests write, Checks/statuses read) and configures
   `V2_CODEX_APP_ID`, `V2_CODEX_APP_PRIVATE_KEY`, and
   `OPENAI_API_KEY` in GitHub settings **without pasting secrets to chat**.
5. Separately review/merge an activation policy with fresh official
   prices/current main, source SHA and check names; owner-authored exact
   single task approval comment; then manual `workflow_dispatch` on
   `main` for **one test-only W5 provenance receipt**. Do not allow
   automatic merging, deployment or W1–W4 general coding.
6. Validate real Responses API usage, new Draft PR on isolated W5
   task branch, exact-head GitHub Actions and actual ledger. Any
   refusal/uncertain cost is terminal, not retryable.

## Important boundaries

- `W4` Issue #526 (offline trilingual Qixingtan hourly view)
  is a **separate normal coding task** and is NOT implemented by this
  JSON-only executor. General W1–W5 adapters need independent
  isolation, approval, cost and actual source/CI reviews.
- #517 NOAA/NWS Research-only runtime remains isolated.
- Published V2 remains 7 places/8 subjects; no current weather,
  photo recommendations/scores, route directions, or commercial
  Open-Meteo usage is enabled.
