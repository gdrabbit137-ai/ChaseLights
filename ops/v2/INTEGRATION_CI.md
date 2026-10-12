# W5 Task K — main-based W4 integration (2026-10-12)

Owner W5. This branch starts at #452 `d69953997d561a19f54330b652dd8c43ea904258` and changes only `ops/v2/` and `.github/workflows/v2-integration.yml`. It targets main. The former W5 PRs #437/#445/#449/#451/#452 are cumulative history, not additional independent merge candidates. No W1–W4 or Legacy files are edited.

## Exact candidate sources

- Latest reviewed main at construction: `a13c5897dfc7a8c00766267760e08ba6f6ba59f9`. The runner checks pinned Git Blobs for AGENTS.md, both R4.2 specs and every baseline `specs/v2/` file; a normative main drift fails closed. The integration assembly and detached merge checkout must also use the same current main SHA.
- W1 #450 `bf60a497e5338a45bda63d9bc24b33e9ea1d3b43`. The entire W1 specs tree is copied after comparing its ten reviewed changed blobs against main.
- W2 #440 `a816c833ac4f83f440d1d76350cb46da74f43013` → #444 `8725bf13348dfae371ae8358930a25dd424a3361`. The canonical content ancestor `452ff5a79e0e4617d6ddb834b5dbecdd0e896b55` must have the same four source blobs as #444.
- W3 #435 `d24af0dbea61c158482bea9522ac36eac016843d` → #441 `77b040fd1af806a564282eea7e3a7c7166a180d3` → #447 `b26a014fec9705d40f794ae3ddb02530d3cb5574`.
- W4 **main-based #454** `32f557d998a4d12ec37af4d963f0f410030b1cc1`. The workflow checks out historical #448 `ddf9f2c4bd2eeb556bf0aa3b244f01de3256b05f` for comparison only. Both Git Trees must equal `a0438fb0f372b0e0e124b5ec3385d5184d9fbb2e` with exactly 52 files and identical paths. #448 and its earlier owner base/#436/#442/#443/#446 are not separately merged.
- W5: the exact current integration PR HEAD.

The runner compares real W2 canonical bytes with W4 fixtures, manifest Git Blob IDs and SHA-256, W3 fixture, research-only preview and default catalog. Preview/catalog must retain `research_only=true`, `selected_date_recommendation_eligible=false`, `forecast_available=false` and no evaluations; human semantic signoff stays PENDING.

## CI and rehearsal

GitHub Actions uses pinned checkouts for W1–W4, a historical W4 checkout for tree proof, and an independent detached checkout of current main for the merge rehearsal. The rehearsal reads candidate tips from the lock file, verifies the W2/W3 Git ancestry, and merges W1, the W2 and W3 ancestry, the single #454 W4 consolidation, then the current W5 HEAD. The resulting step count comes from the actual candidate chain. At every merge it rejects conflict, duplicate/empty merge, unexpected owner paths, a dirty worktree, an overwritten accepted owner tree or altered Legacy entry blob. It verifies final owner trees and W5 files against the exact source commits and proves #448 ancestry was not replayed. No scratch commit is pushed.

Required discovery is currently 113 counted cases: W1 15+4+6, W2 6, W3 29, W4 Node 30 and six Chromium locale/device cases, W5 7+7+3. The runner reads real test discovery and rejects changed expected counts, zero tests, FAIL, ERROR, SKIP or expected failures. Canonical record schema, cross-owner provenance, compilation and Legacy isolation are additional gates. An actual new-head Actions job, original log, artifact and main SHA must be inspected before accepting any result; the earlier #452 113 PASS is historical.

## Release boundary

This is a research-only preview candidate. No live provider, valid issue/forecast time, coverage, approved threshold or AUTO binding is established merely by CI. Missing prerequisites propagate UNKNOWN/NOT_EVALUABLE and never formal FAVORABLE. Automated localization tests are not human zh-TW/en/ja semantic approval. The human evidence/access review for P01/P02, lawful camera area, current closure and arrival NavigationTarget remains pending. Required PR reviews, project-owner merge decision, public preview URL and live smoke are separate gates. See `RELEASE_GATE.md`. No main merge or deployment occurs in this task.
