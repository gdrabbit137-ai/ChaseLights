# W5 Task I final pinned integration (2026-10-11)

Draft research-only integration. This distinct W5 branch starts at #449 `55d685dc58dba3a9b0ab1955266320d651853f67` and targets main. It changes only `ops/v2/` and the W5 integration workflow. #437 and #445 are historical W5 ancestors, not independent final merge candidates.

## Reviewed sources and assembly

- Latest reviewed main: `afb6f82cdd812a6cf8dab4465e471b6b03af4a98`. Its only change after #450's main base was WeatherGrid data; reviewed AGENTS, R4.2 and V2 baseline spec blobs remain pinned in `integration-sources.json`. A later normative spec drift fails the gate.
- W1 consolidated #450: `065fe5d27bcd33d492357321674c267e707b640d`, replacing #431, #438 and #439 as one source. The runner compares the entire W1 `specs/v2/` tree to current main and requires exactly the nine reviewed Git Blob changes in the manifest. It then copies the complete, byte-verified W1 tree, including EvaluationResult schema, three fixtures, four EvaluationResult tests, six free-composition tests, reconciled README and both policies. No old `w1_free` checkout is used.
- W2 #444: `8725bf13348dfae371ae8358930a25dd424a3361`; reviewed canonical content ancestor `452ff5a79e0e4617d6ddb834b5dbecdd0e896b55`. Both commits must have the exact four reviewed canonical/preview blobs, with W3 fixture and W4 manifest, preview and catalog matching current W2.
- W3 #447: `b26a014fec9705d40f794ae3ddb02530d3cb5574`. W4 #448: `ddf9f2c4bd2eeb556bf0aa3b244f01de3256b05f`.

The W1 #450 own Actions run 38182973713 discovered 25 unittest cases (15 canonical, four EvaluationResult, six free composition). This integration expects 113 counted cases: W1 25 + W2 6 + W3 29 + W4 Node 30 + browser 6 + W5 contract 7, runner 7 and watchdog 3. Counts are independently parsed from real unittest/Node discovery at the integration HEAD; any count drift, zero tests, FAIL, ERROR, SKIP or expected failures fails. Real W2 record schema checks, provenance, compilation and Legacy isolation are additional gates, not counted cases.

## Pending gates and safe sequence

Research-only fixtures cannot authorize live FAVORABLE, score, selected-date forecast or Directions. UNKNOWN/NOT_EVALUABLE, provider/time/evidence/threshold/AUTO-binding and verified access remain fail closed. Structural schema checks do not authenticate provider evidence. Three-locale automated checks do not replace human semantic signoff. W2 evidence and legal shooting-area/access, navigation GPS, required reviews and public preview smoke remain pending independently of CI.

Review #450 first, then W2 #440→#444, W3 #435→#441→#447, W4 owner base→#436→#442→#443→#446→#448, and finally this W5 integration branch after accepted owner heads are repinned to their post-merge SHAs. Consider consolidating each cumulative owner stack into a reviewed main-based PR to avoid merging obsolete draft tips twice. Recheck actual Git merge result, branch rules, reviews, latest main and exact-head CI before every merge. No merge or deployment is authorized by this document.
