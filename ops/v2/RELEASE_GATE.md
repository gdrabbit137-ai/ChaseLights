# ChaseLights V2 Research-only Preview release gate

Status: proposed W5 gate, 2026-10-12. This document is a review checklist, not an approval to merge, deploy, or serve live forecasts. Re-evaluate against current main and final owner heads.

## Candidate chain and merge decision

| Owner | Candidate | Required parent or replacement |
| --- | --- | --- |
| W1 | #450 (final HEAD bf60a497e5338a45bda63d9bc24b33e9ea1d3b43) | Main; supersedes #431, #438, #439 |
| W2 | #444 (8725bf13348dfae371ae8358930a25dd424a3361) | #440 (a816c833ac4f83f440d1d76350cb46da74f43013) |
| W3 | #447 (b26a014fec9705d40f794ae3ddb02530d3cb5574) | #435 (d24af0dbea61c158482bea9522ac36eac016843d), #441 (77b040fd1af806a564282eea7e3a7c7166a180d3) |
| W4 | #448 (ddf9f2c4bd2eeb556bf0aa3b244f01de3256b05f) | owner base e931981a31d2ade1a94f921edd66f069027ec47c, then #436, #442, #443, #446. The owner base is not in main and has no PR. |
| W5 | #452 (d69953997d561a19f54330b652dd8c43ea904258) | All accepted owner content; #437, #445, #449, #451 are cumulative ancestors, never independent final merges. |

For sequential merges, preserve each parent's full change before its child. Do not start at W4 #436 on main. A main-based W4 consolidation is acceptable if its final `apps/web-v2/` tree is byte-identical to #448 and its provenance lists the owner base and every replacement. The same approach may replace other stacked chains; do not merge both the stack and its consolidation. Review path ownership, actual merge output and CI after any new main commit. Keep old PRs open as traceable history until the approved replacement is merged, then close without merging.

The W5 Actions merge rehearsal checks the sequence on a detached main copy; its result and logs must be inspected separately from the 113 counted tests. The checked-out W5 assembly uses exact owner Git blobs, while the merge rehearsal checks that the final Git trees retain those same owner bytes and Legacy entry files. A result from an earlier main or an older source HEAD is historical evidence only.

## Research-only Preview publication conditions

1. The preview must visibly and equivalently state in zh-TW, en and ja that it is research material, not a selected-date forecast or a recommendation to visit. A photographer must understand the practical limits without reading machine status codes. Default cards cannot imply a live score, optimal time, current weather, or formal FAVORABLE.
2. All shown opportunities remain R1/evidence_review until the appropriate human claim, evidence and locale review. Research-only records must remain outside normal selected-date recommendation and verified place-guide surfaces. A separately labeled research preview may expose them with access and safety uncertainty.
3. Require `research_only=true`, `selected_date_recommendation_eligible=false`, `forecast_available=false`, and empty `evaluations` in the published preview. No test-only provider or synthetic boolean can yield live FAVORABLE. Missing provider, time, coverage, evidence, approved AUTO threshold or model binding stays UNKNOWN/NOT_EVALUABLE. The structural EvaluationResult schema by itself is insufficient.
4. Directions appear only for separately verified lawful arrival coordinates, with evidence and current access checks. No keyword or subject-coordinate fallback. Candidate viewpoints and camera/subject geometry remain unknown unless independently verified. The tw-026-P01 original lookout closure and uncertainty about other lawful shooting boundaries must be visible; the official alternate viewing platform is not evidence of an exact camera polygon or navigation coordinate.
5. Perform a human check of all three language versions for photographic claim, conditions, restrictions and safety; automated presence tests and AI review are supporting evidence, not formal signoff. Recheck dated closures before publication.
6. Approve the complete PR ancestry or reviewed consolidation, actual current-head green Actions with original job logs/artifact, exact source pins and no FAIL/ERROR/SKIP, and the independent merge rehearsal. Required human PR reviews and project-owner merge/release decisions remain separate.
7. Deploy V2 at an independently verified URL only after merge/review authorization. Smoke the real URL, content, three locales, mobile/desktop operation, asset paths and absence of unverified Directions or favorable/score. Add a minimal verified Legacy-to-V2 link only in its separately approved W5 deployment change; do not alter Legacy forecast, scoring, navigation or routes as part of this preview.

## Remaining review inventory

| Check | Evidence presently available | Pending acceptance |
| --- | --- | --- |
| Contract and provenance | W5 #452 GitHub Actions run 38186730009 attempt 4: 113 PASS/0 FAIL/ERROR/SKIP, pinned to W1 #450 bf60a497, W2 #444 8725bf13, W3 #447 b26a014f and W4 #448 ddf9f2c4; 13-step detached merge rehearsal PASS on main 84f211c27e426fc6db5bdb6b4bb310a4bf77218b | Re-run against current main or changed owner HEAD; independently review job logs and post-merge CI after accepted heads |
| W2 human/canonical/crosswalk | W2 #444 source, six data tests and W5 byte-provenance gate | Independent full evidence-scope and human zh-TW/en/ja semantic approval |
| tw-026-P01 | Official attraction describes salt-pan sunset; official closure notice says original lookout closed through planned 2026-11-30 | Current closure/access recheck, lawful shooting boundary, substitute platform precision; no invented GPS |
| Navigation | All three staged records retain needs_review/null arrival coordinates | Verified arrival evidence before any Directions |
| Runtime | Test-only W3 evaluator is fail-closed on missing prerequisites | Approved provider coverage, thresholds/bindings, freshness, evidence and genuine EvaluationResult before live use |
| Governance | All final owner PRs and #452 are Draft; no approving reviews seen | Formal review, owner approval, merge and release decision |
| W4 root | Owner branch e931981a differs from main in apps/web-v2 and has no PR | W4 owner must submit base PR or reviewed main-based consolidation |

### Decision requested of the project owner after gates pass

- Approve the W1 #450 contract and its human semantic implications.
- Choose sequential owner-chain merges or a traceable main-based consolidation for W2, W3 and W4; commission the missing W4 base PR. Confirm original PRs to close only after replacement is accepted.
- Obtain designated human evidence/access/localization reviews; accept the research-only UI wording and its publication scope.
- Authorize final merge separately after the updated exact-head and post-merge checks. Authorize V2 preview deployment and Legacy link separately after public URL smoke. No live recommendations are in this release.
