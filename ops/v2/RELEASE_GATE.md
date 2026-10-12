# ChaseLights V2 Research-only Preview release gate

Status: corrected W1–W5 integration candidate, 2026-10-12. **No merge, deployment, human-approval or live-weather authorization**. Always validate current PR HEADs, CI and main immediately before a merge decision.

## Corrected candidate chain and merge order

| Owner | Accepted candidate chain | Latest corrected tip | Release note |
| --- | --- | --- | --- |
| W1 | #450 → **#457** | `ee1a660b0de1bb452d05539236c1834a32140d32` | Enforce access-warning separation in specs/schema |
| W2 | #440 → #444 → #456 → **#458** | `2177bd8c8b6c18e0a4b284e50b55d0ff12697ddd` | Canonical, evidence, Crosswalk and localized access warnings |
| W3 | #435 → #441 → #447 → **#459** | `656c1e8919f5f720cd8e1e2f56b26e81d4b0dcc8` | Quarantine legacy access conditions; keep genuine weather blockers |
| W4 | #454 → **#460** | `ec5dc9609596135ba1b2634dfa7d6c07a54fabdc` | Explicit independent access-note section, verified W2 fixtures, three locales |
| W5 | #455 → **#461** | Check actual latest HEAD | Last, pinned full CI, provenance and 13-step detached merge rehearsal |

The original #448 W4 stack is **historical only**. Do not merge #448 or its stacked predecessors. W4 #454 is the accepted main-based ancestor of corrected #460. #460's reviewed `apps/web-v2/` tree `8427cb75fdb433a58d3a4941769a6c06f6f5dc3b` must deliberately **differ** from #454's pre-correction tree `a0438fb0f372b0e0e124b5ec3385d5184d9fbb2e`. Keep those source provenance checks; never require byte-parity with superseded #448.

These are owner-isolated Git histories and the **simulated** safe merge order, not permission to merge all PRs or to deploy. #453's missing-main-based W4 technical problem has a traceable candidate (#454 → #460), but the issue remains open until human acceptance and completed integration. The latest successful predecessor run for corrected access warning logic was #461 run 38294110996 (123 PASS, 13-step rehearsal), which precedes the independent W4 UI warning-section patch. The newest #460/#461 HEADs need their own full GitHub Actions success and saved logs/artifacts. Any main/spec source drift requires an explicit new verification, never a presumed pass.

## Required human and evidence gates

1. Obtain formal PR reviews and project-owner merge decision for W1–W5. An AI audit or green Actions run is supporting technical evidence, never a submitted human Approval.
2. Audit W2 research claims against their actual source scope and human-readable Crosswalk. All three records remain R1/evidence_review; no unverified item is promoted to approved/canonical release merely because its JSON is staged. Obtain human zh-TW, en and ja semantic signoff for subject, conditions, access, safety and UI wording.
3. Recheck tw-026-P01 original-lookout closure and lawful camera area. An official alternate viewing platform does not prove an exact camera polygon or navigation point. Review tw-026-P02's short camera wording against its explicit access uncertainty. Recheck dated restrictions before public Preview.
4. Verify NavigationTarget as a lawful, practical arrival point with evidence and current access before showing Directions. Keep camera context and photographed subject separate. Do not infer GPS from a Place name, map query, photo or unverified viewpoint.
5. Maintain a visible, equivalent research-only warning in all three languages. No selected-date recommendation, live score, current conditions or formal FAVORABLE from this preview. Require `research_only=true`, `selected_date_recommendation_eligible=false`, `forecast_available=false`, and empty `evaluations`. Missing real provider/coverage/issue and valid times, evidence, threshold or approved AUTO binding propagates UNKNOWN/NOT_EVALUABLE.
6. After reviews and merge authorization, deploy V2 separately at a verified URL, then smoke real content/assets, 1440px and 390px behavior and the three locales. A minimal Legacy-to-V2 link requires its own verified URL and approval. Do not change Legacy forecast, scoring or navigation.

## Current candidate status and remaining blockers

| Check | Current interpretation |
| --- | --- |
| W4 submission | #454 → #460 are main-based and a corrected descendant; three-language and human UI review pending |
| W2 evidence / Crosswalk | Automated byte and reference tests are necessary; human evidence scope and localization pending |
| P01/P02 lawful area and access | Pending; no inferred GPS or Directions |
| Navigation GPS | Pending independent arrival-target evidence |
| Runtime | Research-only; test fixtures do not authenticate real provider or AUTO conditions |
| Governance | Owner PRs remain Draft until submitted reviews and project-owner decision |
| Preview publication | Pending the foregoing gates and post-merge public URL smoke |

## 2026-10-12 — Access advisories are independent of photo suitability

**Owner-approved product requirement:** a closed/restricted road, trail, viewpoint or area, or unknown legal access, is a **warning only**. It MUST NOT be an environmental photography REQUIRED/BLOCKER/QUALITY, score penalty, critical UNKNOWN gate or reason to classify the weather as unfavorable. Nevertheless the interface MUST show accurate, sourced and fully localized warnings and MUST NOT navigate users to an unverified, unsafe or closed arrival point. This correction does not assert that any closed area is safe to visit.

The original W5 #455 113 PASS / eight-step rehearsal and corrected pre-UI #461 123 PASS / 13-step rehearsal do **not** prove the *latest* W4 UI warning-section patch passed. New target full discovery is 123 counted tests, with 0 FAIL, ERROR or SKIP; verify raw logs before asserting success. Human research/evidence/translation review, legal access and navigation validation, project-owner merge and Preview publication decisions remain pending and are **separate** from the photography-weather verdict. Legacy runtime and scoring remain unchanged.
