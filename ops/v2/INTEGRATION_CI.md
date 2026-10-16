> Task V current proposal: integrates independent Draft sources #486 and #487 on reviewed main `15de1a4daf1f1a260cf3a553023d202eee6a0d99`. W4 source `f0da51f30252328f82babba7d90dd17f1559c68e`, tree `7ad5210b957e9e184f941a06b714106c528e0b0a`, remains byte-exact. The strict candidate suite now discovers 267 cases: W1 36, W2 15, W3 52, W4 Node 43 + Chromium 75, W5 40 + built-package Chromium 6. These are enforced discovery counts; actual execution results are reported separately. The new eight-file static package includes catalog-state.mjs and is never deployed by these workflows. Existing published Preview smoke and unpublished candidate smoke have explicit separate scopes. All historical records below remain historical. Live Release Readiness remains NOT READY; this proposal grants no merge/deployment or human signoff.

> Task R current-state notice: this document records the historical 123-case/13-step assembly. The current main-based gate retains those checks plus solar/NWS and 12 W5 release-tool regressions (169 counted cases). Use `postmerge_verify.py` and the fixed-SHA `simulate_merges.py` CLI; do not replay already-merged owner branches. See `reviews/TASK_R_RELEASE_READINESS.md` and `deployment_plan.json`.

# W5 Access Advisory Integration — 2026-10-12

W5 only: integrates W1 #457, W2 #458, W3 #459 and W4 #460 on top of the already tested W5 #455, without changing other worker-owned paths.

## Corrected exact-head source chain

- W1 #450 → #457 `ee1a660b0de1bb452d05539236c1834a32140d32`.
- W2 #440 → #444 → #456 → #458 `2177bd8c8b6c18e0a4b284e50b55d0ff12697ddd`.
- W3 #435 → #441 → #447 → #459 `656c1e8919f5f720cd8e1e2f56b26e81d4b0dcc8`.
- W4 #454 → #460 `ec5dc9609596135ba1b2634dfa7d6c07a54fabdc`.
- W4 corrected tree `8427cb75fdb433a58d3a4941769a6c06f6f5dc3b` differs intentionally from parent #454 `a0438fb0f372b0e0e124b5ec3385d5184d9fbb2e` (historical pre-correction). The original #448 stack must never be merged.

## Product rule and gates

Site, road, trail and viewpoint closure or uncertain lawful access remains **visible non-scoring Access Advisory**. It cannot affect Photography Opportunity REQUIRED/BLOCKER/QUALITY, favorable/uncertain score or verdict. No advisory alone constitutes an environmental blocker; unverified/closed arrival targets still cannot yield Directions.

The runner verifies W1's exact revised spec blobs, all three W2 real records have no ACCESS_SAFETY contract conditions, three-language access/safety notes stay present, W3 canonical fixture matches W2, and W4 real-data fixtures, research-only Preview and catalog Git SHA-1/SHA256 provenance match W2. Forged Live Evaluation remains rejected. Research-only must never produce real FAVORABLE.

Expected counted tests: W1 17+4+6, W2 10, W3 32, W4 Node 31 / Chromium 6, W5 7+7+3 = **123**; zero fail/error/skip. Detached real main-based merge rehearsal has **13 ordered steps**, including the corrected successor PRs; original #448 is historical only. No test lowering, automatic merge, deployment or human signoff is authorized.

### W4 warning presentation final review

W4 #460 now renders localized closure/access notes in a standalone `role=note` access section separate from photographic BLOCKER conditions. Desktop/mobile Chromium assertions require the independent warning section to be visible, and the three real R1 research records have no access conditions in photo contracts. The updated W4 HEAD and `apps/web-v2/` tree are independently pinned above. No score or live verdict is manufactured.
