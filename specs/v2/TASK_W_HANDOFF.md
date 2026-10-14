# Task W — W1 shared-contract handoff

Owner W1; one task branch, one Draft PR. This handoff is implementation input, not permission to merge or deploy. All changed repository files are under `specs/v2/`. Existing Opportunity, EvaluationResult, solar-window and weather-source schemas remain unchanged.

## Reviewed sources and scope

Reviewed latest main/base: `dcb1a22f1af6f1d07f0e0e1fa1233c1d0f5d069f` (2026-10-14). Local initial checkout was `c75cb5736253f5e848a40a81dfabc78ced19367d`; GitHub compare and complete tree inventory prove the only drift was two generated `weathergrid/himawari9_tw_cloud_{browser,qc}.json` files. AGENTS, R4.2 Research/Navigation and all V2 owner sources/specs matched. Read current V2 index, architecture, governance, access advisory, free composition, worker contracts, M6a/M6b and related tests before defining additive formats.

Git fetch failed with `Failed to connect to proxy port 8080`. The connected GitHub tool supplied the latest main commit and complete tree. A separate shared local checkout reconstructed and hash-verified **the exact base commit and root tree `5cfa2391b87d799d7cbd9b3e95242a152f6a1f12`**, using sparse checkout to exclude WeatherGrid. No generated/Legacy bytes were edited. Remote GitHub operations use the existing connector; no alternate credentials or network-policy bypass.

Related actual sources reviewed:

| Source | Observed state / implication |
| --- | --- |
| W1 #478 `3bdcac69086f1e74850cb23515780d617fd754fa` | Merged raw-weather contract; retain its RAW_ONLY/no-score rules. |
| W1 #473 `86b8b08a79a2056a5a22d183ffffbd456800217f` | Merged solar WINDOW contract; reuse local-date/IANA semantics without upgrading to a recommendation. |
| W2 #468 `509a7c206413a4f8d13350ddb50c2a7ad075ca4a` | Merged five-record addition; current main has eight Opportunities/seven Places, not a schema maximum. Original P01 history remains distinct. |
| W4 #487 `f0da51f30252328f82babba7d90dd17f1559c68e` | Open Draft, unmerged. U-W4-01 home/loading states and explicit 02A/B/C handoff; do not assume UI is on main. |
| W5 #486 `0837dd555df9d8f647b9042223d5e766d6fd6afc` | Open Draft, unmerged; independent build/release work, not changed here. |
| W5 #488 `bfd7afa14e6c416518592bf48d3dcbd5677d60d7` | Open Draft, unmerged. Its 267-case report is historical evidence for its own candidate, not this W1 change. |
| Issue #471 | Separate seven-Place/eight-Opportunity research Catalog publication task, not eight taxonomy definitions or authorization to implement W4 here. |

Task U's original 40-item feature matrix/Roadmap was not found in latest main, the #487 tree, or repository issue search for Task U/U-W4. Its location was requested while proceeding. Use the existing #487/#488 02A/B/C handoffs and this task's explicit scope; no new 40-item inventory was performed. Link/reconcile the original artifact when supplied; do not claim it was read. There were no open W1 file changes among the observed relevant PRs.

## Contract map

| Contract | Consumer artifacts / field semantics | Missing data / acceptance |
| --- | --- | --- |
| [02A Place index](PLACE_INDEX_CONTRACT_V0_1.md) | `place-index-v0.1.schema.json`; stable identity, multi-valued country/admin1 membership, multilingual names, exact canonical joins and derived publication. | Partial/unknown explicit; no invented name/admin/timezone. Real canonical byte/hash/revision negatives, multi-country/admin tests and separate human publication gate. |
| [02B Date query](DATE_QUERY_CONTRACT_V0_1.md) | `date-query-v0.1.schema.json`; verified IANA local day, query versions/loading state and exact artifact references. | UNKNOWN zone → NOT_EVALUABLE; 23/25h DST, date line, skipped date, stale identity and no forecast fabrication tests. |
| [02C Topics/favorites/sort](TOPICS_FAVORITES_SORT_CONTRACT_V0_1.md) | Four schemas: topic index, local preferences, browse query, sort capabilities. | Unknown joins rejected; unavailable favorites preserved; score/distance disabled with three-language explanations. Filter/grouping truth tables never promote research. |

## W2 — smallest data task

Create an independent `data/v2/` owner PR with an initial **research-only** Place index and topic registry/bindings from existing Canonical; do not change W4 Catalog or evaluator. First validate the four joins demonstrated by W1, then cover the actual seven Places/eight Opportunities without treating that count as permanent. Preserve existing IDs, exact per-record commit/path/blob/revision, original P01 provenance and canonical bytes. Supply sourced Place names/aliases in three languages, sourced ISO country/admin1 registry and multi-membership, Place-scope timezone evidence and metadata completeness. Use UNKNOWN/PARTIAL honestly rather than blocking the whole index on an incomplete Place.

Supply complete definitions for the eight proposed topic IDs, review semantic overlap and map only evidenced canonical subjects. `topic:contract-a/b` in fixtures are synthetic and must not ship as taxonomy. Human evidence/crosswalk/semantic release artifacts control GUIDE_ELIGIBLE; pending R1 records stay RESEARCH_ONLY. No new coordinate, score, threshold, API or legal-access assertion is required to complete this first index. Return explicit unresolved rows to W1 via handoff rather than silently changing the schema.

## W4 — UI task inputs

Start from latest main plus the **actual accepted** U-W4-01 source, checking #487/#488 status. Implement 02A/B/C against the six schemas; retain default no-forecast home and explicit research entry. Use stable IDs across locale/filter/favorite changes; OR within region/topic, AND across groups; filter Opportunities before grouping Places. Do not render R1 as a selected-date recommendation or mix unavailable score/distance into zeroes.

Implement date generation/cancellation/cache identity as 02B, localStorage lifecycle as 02C, and disabled sort reasons/fallback. Missing names/admin need localized honest fallbacks; schema failure, loading, error and empty are distinct. No IANA zone from the device. Any EVALUATION result still needs W3's owned semantic decision; schema/query availability is not forecast approval. Render sourced closures independently and guard navigation under R4.2. W1 reference validators/oracle are test tools, not an application module to import or a replacement for W4 tests.

## W3 — date/evaluation dependencies

Provide a deterministic local-day resolver using verified zone evidence and auditable tzdb version. Validate nonexistent dates, midnight gap/fold boundaries, repeated-hour offsets and cross-midnight periods. Match native provider intervals to the true UTC coverage, including D+1 end/freshness and unsupported provider horizons. Bind returned artifacts to query identity, exact canonical/condition-contract hash, provider/model/data revisions and bytes. Reuse existing solar WINDOW and raw source schemas with their no-recommendation flags. No new selected-date score until authentic provider coverage, approved AUTO thresholds and owned recommendation policy exist. Lack of timezone affects time-dependent evaluation only; access advisories never become scoring blockers.

## W5 — integration requirements

1. Intentionally repin the accepted W1 commit and **entire** `specs/v2/` tree, verify reviewed main blobs and all other owners. Do not lower the existing source-tree gate to accept an unreviewed delta. Recheck open #487/#488 separately; do not repin them by inference from this task.
2. Retain existing tests/thresholds. Add the real Task W discovery count (see test results) and standalone `validate_task_w_contracts.py` gate. Its canonical provenance CLI needs pinned source Git objects; fetch the explicitly declared source commits in the W5 checkout. Unit tests validate current canonical bytes against pinned blob hashes and run in shallow PR checkouts; they do not authenticate history by themselves.
3. Run combined exact-head integration after W2/W3/W4 implementation. W1 source checks passing alone do not prove integration, browser behavior, live weather or release readiness. Expect an intentional W1 pin mismatch until W5 adopts these files; do not hide it as PASS or waive the gate.
4. Add desktop/mobile × zh-TW/en/ja browser cases for multiple countries/admin selections, cross-region dedup, two Opportunities at one Place, null metadata/empty results, rapid date races and DST-local display; favorites corruption/quota/future version/unavailable IDs/cross-tab edits; missing/incomparable scores, denied/stale/untrusted distances and explicit sorting fallback.
5. Retain original P01 canonical/preview hash checks, current research-source parity, no invented Directions/live recommendations, independent access advisories and Legacy isolation. No automatic Legacy/V2 output comparison. No Release Gate edits are made by W1.

## Explicit human confirmations still pending

- Source-backed stable Place identity, split/merge handling, exact administrative extent and ISO code/name registry, especially cross-boundary or multi-zone Places.
- zh-TW/en/ja Place names/aliases, all taxonomy definitions and subject assignments, and photographer-facing missing/disabled-state copy. Automated keys are not semantic approval.
- Place-specific IANA timezone/evaluation scope and evidence; not just zoneinfo membership.
- Opportunity-existence evidence/crosswalk, canonical release and exact human semantic publication approval artifacts (#465/#474 remain separate work); R1 is not approval.
- Any trusted representative coordinate/distance semantics/uncertainty and user-origin privacy before DISTANCE can enable; no coordinates were invented here.
- Approved provider coverage/freshness/license, thresholds/model bindings/calibrated comparable scores and owned recommendation policy before SCORE/live recommendations can enable (#467).
- Lawful camera-area boundaries, refreshed closure/access notices and separately verified practical arrival targets. They control warning/navigation, not weather scores.
- Original Task U artifact location and project-owner release decisions. This task requests no merge, deployment or paid API.

Actual W1 results and reproducible commands are retained in [tests/logs/task-w/RESULTS.md](tests/logs/task-w/RESULTS.md). The next minimum executable task is the W2 research-only index/registry PR above; human approvals can remain explicitly pending.
