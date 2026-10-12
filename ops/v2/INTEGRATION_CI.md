# W5 Task J pinned integration and merge rehearsal (2026-10-12)

Draft research-only integration. This distinct W5 branch starts at #449 `55d685dc58dba3a9b0ab1955266320d651853f67` and targets main. It changes only `ops/v2/` and the W5 integration workflow. #437 and #445 are historical W5 ancestors, not independent final merge candidates.

## Reviewed sources and assembly

- Latest reviewed main: `a1704f6ba0566c7c4388e67d7829ec8a769491c4`. Its only change after #450's main base was WeatherGrid data; reviewed AGENTS, R4.2 and V2 baseline spec blobs remain pinned in `integration-sources.json`. A later normative spec drift fails the gate.
- W1 consolidated #450: `bf60a497e5338a45bda63d9bc24b33e9ea1d3b43`, replacing #431, #438 and #439 as one source. The runner compares the entire W1 `specs/v2/` tree to current main and requires exactly the ten reviewed Git Blob changes in the manifest. It then copies the complete, byte-verified W1 tree, including EvaluationResult schema, three fixtures, four EvaluationResult tests, six free-composition tests, reconciled README and both policies. No old `w1_free` checkout is used.
- W2 #444: `8725bf13348dfae371ae8358930a25dd424a3361`; reviewed canonical content ancestor `452ff5a79e0e4617d6ddb834b5dbecdd0e896b55`. Both commits must have the exact four reviewed canonical/preview blobs, with W3 fixture and W4 manifest, preview and catalog matching current W2.
- W3 #447: `b26a014fec9705d40f794ae3ddb02530d3cb5574`. W4 #448: `ddf9f2c4bd2eeb556bf0aa3b244f01de3256b05f`.

The W1 #450 final-head Actions run 38184788428 discovered 25 unittest cases (15 canonical, four EvaluationResult, six free composition). This integration expects 113 counted cases: W1 25 + W2 6 + W3 29 + W4 Node 30 + browser 6 + W5 contract 7, runner 7 and watchdog 3. Counts are independently parsed from real unittest/Node discovery at the integration HEAD; any count drift, zero tests, FAIL, ERROR, SKIP or expected failures fails. Real W2 record schema checks, provenance, compilation and Legacy isolation are additional gates, not counted cases.

## Pending gates and safe sequence

Research-only fixtures cannot authorize live FAVORABLE, score, selected-date forecast or Directions. UNKNOWN/NOT_EVALUABLE, provider/time/evidence/threshold/AUTO-binding and verified access remain fail closed. Structural schema checks do not authenticate provider evidence. Three-locale automated checks do not replace human semantic signoff. W2 evidence and legal shooting-area/access, navigation GPS, required reviews and public preview smoke remain pending independently of CI.

Review #450 first, then W2 #440→#444, W3 #435→#441→#447, W4 owner base (no PR and absent from main)→#436→#442→#443→#446→#448, and finally this W5 integration branch after accepted owner heads are repinned to their post-merge SHAs. Consider consolidating each cumulative owner stack into a reviewed main-based PR to avoid merging obsolete draft tips twice. Recheck actual Git merge result, branch rules, reviews, latest main and exact-head CI before every merge. No merge or deployment is authorized by this document.

## Task J merge rehearsal and release decision

The W5 workflow now runs `simulate_merges.py` in a separate detached checkout of current main. It applies the exact W1, W2, W3, W4 (including the unmerged owner base), and W5 heads in order; every step rejects conflicts, empty/duplicate merges and unexpected owner paths. It compares final owner subtree Git hashes to their source tips and proves Legacy entry files retain their main blobs. Logs and source SHAs are retained as an Actions artifact. The 113 tests run on the separately assembled identical owner subtrees; this rehearsal cannot replace post-merge CI when accepted owner heads or main change.

W4's owner base has no PR targeting main. This is a real release blocker despite a green pinned integration: create and independently review its base PR or a traceable main-based W4 consolidation before trying to merge #436 onward. No owner path is modified in W5. `RELEASE_GATE.md` records research-only publication conditions and pending human decisions. A green CI run is never a human approval, live-provider authentication or deployment authorization.
