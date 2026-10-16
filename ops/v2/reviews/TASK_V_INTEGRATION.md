# Task V — W5 integration of U-W4-01 and release tools

This is a W5 source-integration proposal, not a live forecast or release approval. Latest main reviewed at task start: `15de1a4daf1f1a260cf3a553023d202eee6a0d99`. Re-read main AGENTS/R4.2/applicable V2 specs and all open PRs. Compared with the preceding W4 task's main, only two Himawari generated files changed; all applicable specs and owner code were unchanged.

## Verified sources and isolated integration

- #486 Draft/open/unmerged: `0837dd555df9d8f647b9042223d5e766d6fd6afc`, W5 tree `d94eb74c1c24b1af77df1b3fb89019f0ec71d12e`; exact-head GitHub Integration and Release Tools workflows show success. Its original 12 W5 regressions pass locally.
- #487 Draft/open/unmerged: `f0da51f30252328f82babba7d90dd17f1559c68e`, W4 tree `7ad5210b957e9e184f941a06b714106c528e0b0a`; GitHub Integration fails the old W4 pin; published old Preview smoke succeeds. Those results do not certify the new UI as deployed.
- Readonly `git merge-tree --write-tree` of each source against the real main returned exit 0, with no conflicts. Both sources were integrated on `codex/v2-w5-task-v-u01-integration-20261014`; no owner branch or main ref was changed.
- Initial assembled commit `b9bb469b7c91ffcdd6dac922390961d8dd98affb` has the exact W4 source tree and exact #486 W5 tree. W1/W2/W3 and every non-W5/non-W4 path match the starting main. W5 code changes are confined to ops/v2 and V2 test workflows; the imported W4 bytes are not edited.
- W1 source remains `3bdcac69086f1e74850cb23515780d617fd754fa`; W2 `509a7c206413a4f8d13350ddb50c2a7ad075ca4a` with original P01 Canonical source `2177bd8c8b6c18e0a4b284e50b55d0ff12697ddd`; W3 `8e6f5a1555294ff293a6d7b746b864924f96cfc1`. All source trees/blobs and W2 Canonical/fixture/Catalog checks remain enforced.

## W5 fixes and safeguards

1. Repin the exact #487 source commit/tree and 83-file source inventory. Retain historical owner pins and all Canonical byte/SHA-1/SHA-256 guards; additionally pin current effective specification blobs.
2. Build exactly eight V2 runtime files, including catalog-state.mjs. Verify committed bytes, manifest SHA-256, dependency closure, research-only flags and source trees. Multiline imports, re-exports and literal dynamic dependencies cannot escape the package. Output cannot overwrite repository source or an existing release.
3. Rehearse actual immutable base/candidate Git objects, allowing only a declared independent W4 transition from its pinned predecessor. Require source-owner isolation, ancestry, exact owner trees and known base tree. Reject arbitrary W4 edits, other-owner/Legacy edits, self-pins, conflicting/concurrent owner work, invalid source trees and undocumented transitions. No rehearsal ref updates or merge commit publication.
4. Retain every original test; raise exact W4 discovery 31→43 and 6→75. Add 11 W5 source/packaging/permission regressions and 6 actual Chromium cases against the built package. Enforce 267 discovered cases and zero FAIL/ERROR/SKIP, with every non-counted schema/isolation/build group also passing. There is no ignored failure or count derived from an estimate.
5. Set the W4 runner's existing screenshot-directory input so GitHub captures its 360/390/1440×3-language screenshots inside the artifact, without editing W4 code. New built-package smoke opens the forecast home/research browser, verifies all exact source text, independent warnings, unknowns, no score/Directions, language and overflow, and proves catalog-state.mjs was actually fetched.
6. Existing public smoke explicitly selects existing-preview and continues to verify the real HTTPS/assets/V1 link and old six browser cases. Future candidate public mode requires forecast-home plus an exact eight-file manifest; a green old-site smoke is never a claim that this unpublished candidate is live.
7. Workflows remain contents:read, with no environment/publish/upload-pages/deploy/merge steps, no secret additions and no paid API. Ordinary uploaded CI artifacts are test evidence only. Existing main Pages auto-publish is unchanged, so merging this Draft remains an owner release decision.

## Actual validation and evidence boundaries

Baseline assembled source gate failed `Merged w4 subtree differs from tested pin: apps/web-v2`; old rehearsal failed W5-only scope. These failures are retained. After W5 fixes, 11 new unit cases and all 12 original Release Tools cases pass. Preliminary eight-file build and its six real Chromium cases are development runs on an assembled checkout with pending W5 changes; they are not mislabeled as final-HEAD CI.

Final local/GitHub results, tested candidate/main/checkout SHA and parents, per-group PASS/FAIL/ERROR/SKIP, build manifest and rehearsal output will be preserved in the PR and actual workflow artifacts. This document does not claim the final CI had already completed when it was written. All local failures must remain reported separately from GitHub success; a blocked local public destination is not waived or disguised as PASS.

## Release Readiness and handoff

The original 27-check release assessor and its exit-1 fail-closed release CLI remain unchanged. Genuine pilot/provider/approved AUTO integration, accountable human evidence and three-language signoff (#465/#474), live UI contract and Hosting protection are still missing/unverified. Schema/browser/technical CI green cannot make these PASS. Research-only Catalog still has no live evaluations, no selected-date eligibility and no Directions. Release Readiness stays NOT READY / deployment_allowed=false.

Other open PRs #482–#485 and #483's offline automation tools were inspected and not integrated without need; their evidence/governance documentation is separate. #482 raw Seattle NWS transport is not Taiwan/Japan coverage or a photographic score. #420 is Legacy navigation work and is excluded. No source branch is force-pushed or changed; no main merge, deployment, schedule or privilege change occurs.

The U-W4-02 UI/testing foundation is available after this integration's exact-head CI passes, but production metadata is not invented. 02A still needs W1 index/Place contract and W2 sourced trilingual identity/admin/publication index; 02B needs an approved date/query contract and verified Place IANA timezone with DST/local-day tests; 02C needs taxonomy/index and preferences/favorite semantics, with unsupported score/distance sort disabled. Start the next task from the actual accepted source, not an assumed merge, and re-read latest main/owner branches.
