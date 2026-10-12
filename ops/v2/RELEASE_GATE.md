# ChaseLights V2 Research-only Preview release gate

Status: W5 Task K candidate, 2026-10-12. This review inventory grants no merge, deployment or live forecast approval. Recheck latest main and accepted owner heads at decision time.

## Candidate chain and technical order

| Owner | Candidate | Dependency and action |
| --- | --- | --- |
| W1 | #450 `bf60a497e5338a45bda63d9bc24b33e9ea1d3b43` | Main-based, replaces old W1 drafts |
| W2 | #440 `a816c833ac4f83f440d1d76350cb46da74f43013` → #444 `8725bf13348dfae371ae8358930a25dd424a3361` | Preserve the parent, then repaired Crosswalk child |
| W3 | #435 `d24af0dbea61c158482bea9522ac36eac016843d` → #441 `77b040fd1af806a564282eea7e3a7c7166a180d3` → #447 `b26a014fec9705d40f794ae3ddb02530d3cb5574` | Preserve both parent PRs before child |
| W4 | **#454** `32f557d998a4d12ec37af4d963f0f410030b1cc1` | Main-based consolidation; identical 52-file `apps/web-v2/` Git Tree to #448. Original owner base and #436/#442/#443/#446/#448 are historical only; do not merge them again |
| W5 | Task K PR from #452 `d69953997d561a19f54330b652dd8c43ea904258` | Last, after accepted owners. Earlier W5 PRs are cumulative ancestors, not separate merges |

#454 resolves the **technical missing owner-base submission** identified in #453 by providing a main-based W4 PR. This does not close human review or access gates. W5 pins #454, compares both actual old/new Trees in CI and runs a detached latest-main merge rehearsal. Check its exact HEAD Actions run, job, raw logs and artifact; earlier #452 results do not validate Task K. The rehearsal is a candidate simulation, not post-merge-main CI. If main or owner HEADs change, repin and rerun. Close superseded historical PRs only after their accepted replacement has been merged; do not merge both routes.

## Required human and evidence gates

1. Obtain formal PR reviews and project-owner merge decision for W1–W5. An AI audit or green Actions run is supporting technical evidence, never a submitted human Approval.
2. Audit W2 research claims against their actual source scope and human-readable Crosswalk. All three records remain R1/evidence_review; no unverified item is promoted to approved/canonical release merely because its JSON is staged. Obtain human zh-TW, en and ja semantic signoff for subject, conditions, access, safety and UI wording.
3. Recheck tw-026-P01 original-lookout closure and lawful camera area. An official alternate viewing platform does not prove an exact camera polygon or navigation point. Review tw-026-P02's short camera wording against its explicit access uncertainty. Recheck dated restrictions before public Preview.
4. Verify NavigationTarget as a lawful, practical arrival point with evidence and current access before showing Directions. Keep camera context and photographed subject separate. Do not infer GPS from a Place name, map query, photo or unverified viewpoint.
5. Maintain a visible, equivalent research-only warning in all three languages. No selected-date recommendation, live score, current conditions or formal FAVORABLE from this preview. Require `research_only=true`, `selected_date_recommendation_eligible=false`, `forecast_available=false`, and empty `evaluations`. Missing real provider/coverage/issue and valid times, evidence, threshold or approved AUTO binding propagates UNKNOWN/NOT_EVALUABLE.
6. After reviews and merge authorization, deploy V2 separately at a verified URL, then smoke real content/assets, 1440px and 390px behavior and the three locales. A minimal Legacy-to-V2 link requires its own verified URL and approval. Do not change Legacy forecast, scoring or navigation.

## Status to update from the Task K Actions artifact

| Check | Current interpretation |
| --- | --- |
| W4 submission | #454 provides the exact-tree main-based candidate; independent human review pending |
| W2 evidence / Crosswalk | Automated byte and reference tests are necessary; human evidence scope and localization pending |
| P01/P02 lawful area and access | Pending; no inferred GPS or Directions |
| Navigation GPS | Pending independent arrival-target evidence |
| Runtime | Research-only; test fixtures do not authenticate real provider or AUTO conditions |
| Governance | Owner PRs remain Draft until submitted reviews and project-owner decision |
| Preview publication | Pending the foregoing gates and post-merge public URL smoke |
