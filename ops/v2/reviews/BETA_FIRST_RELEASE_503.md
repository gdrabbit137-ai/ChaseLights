# Beta first release · Issue #503

Scope: Research-only Beta on the existing independent `https://chaselights.app/apps/web-v2/` GitHub Pages route. Legacy `/` remains in service with its existing three-language V2 entry. No live forecast, scores, verified navigation, date recommendation or provider activation.

## Accepted immutable sources

See `ops/v2/integration-sources.json` for source commits, exact owner subtrees, the W1 dual-source composition, canonical Batch03/04 provenance and fail-closed checks. The candidate combines W5 #488, W1 #489 and #502, W2 #490, and W4 #498. W4 #498 contains #487; do not merge #487 again. W2 #493/#495 remain separate correction work and are not represented as merged or incorporated into the fixed #490 browse index.

## Release and recovery

1. Review the candidate PR, exact-head Integration (329 cases), release-tool build/rehearsal, and desktop/mobile Chromium in zh-TW/en/ja. PR public smoke confirms only the *existing* site.
2. Merge the exact checked candidate only after reviewing the current main and GitHub Pages source. Main push should publish the isolated `apps/web-v2/` path. Its public smoke builds the exact ten-file source manifest and waits for that published HTML hash before checking all assets and six browser combinations.
3. Record the main merge SHA, Pages run and public smoke run. Fetch the live URL and V1 root independently before declaring the Beta released.
4. If public verification fails, restore only `apps/web-v2/` from the previous healthy main SHA in a reviewed revert PR or emergency revert, preserving Legacy and unrelated generated weather updates. Recheck V1 and V2 URLs. The immutable preceding main SHA is recorded as `reviewed_main` in the source lock; inspect current main again before applying a revert.

W1/W2 semantic and area signoff is pending. Display remains Research-only and access warnings remain separate from photographic conditions. #495's source/access corrections should be integrated in the next small release with regenerated W2 index, W4 bundle, source hashes and full CI. W3 topics may become live only after each topic's provider, threshold, evaluation and release checks pass.
