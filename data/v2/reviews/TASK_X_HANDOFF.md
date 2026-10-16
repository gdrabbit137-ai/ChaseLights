# Task X — W2 Research-only index handoff

Scope: only new files under `data/v2/`; no changes to existing Canonical/audit/crosswalk/preview/review/test bytes. No new Place, evidence search, database reconstruction or Task U inventory. No Legacy, W1/W3/W4/W5 edits, paid API, merge or deployment.

## Reviewed source and exact dependencies

- Latest main/base: `500ec3a76b5f77a0752ecdca5cc1b12fa63d223d`; root tree `5762864474c8480b16f0b9c332047d7f2cb37fbb`; W2 original data tree `9d660c1ebd0fb5a374300972a943de2b8cc5b348`.
- AGENTS assigns W2 `data/v2/`. R4.2 evidence/decision-view/navigation and applicable V2 access/free-composition/canonical/runtime policies reviewed; all match the prior reviewed base aside from generated WeatherGrid. The exact main commit/tree was reconstructed and hash-verified in a distinct sparse task checkout via the existing GitHub connector, excluding WeatherGrid working files; no network-policy bypass.
- #489 actual latest source: **`38b234ba5f4df4a751eaea14dcc79036b45ed180`**, open/Draft/unmerged. Three formal contracts, six schemas and Task W handoff read. Required file hashes are in `../indexes/research/source-lock.json`; W1 files are never edited or imported into this PR. At observation its schema Actions succeeded, integration Actions failed; neither is asserted to validate Task X or waive source pins.
- #487 actual W4 HEAD `f0da51f30252328f82babba7d90dd17f1559c68e` and #488 W5 HEAD `bfd7afa14e6c416518592bf48d3dcbd5677d60d7` remain open Draft/unmerged. Do not treat their UI/build as current main.
- Canonical 3 Batch03 records pinned to #458 **`2177bd8c8b6c18e0a4b284e50b55d0ff12697ddd`**; 5 Batch04 records to #468 **`509a7c206413a4f8d13350ddb50c2a7ad075ca4a`**. Every declared original commit:path byte/hash matches current main. The original P01 accepted blob is **`001a3380231e3d073e900bf2b415aac7dcc5fd79`**; earlier historical `3459ee…` is not substituted for the current source.
- Two audit registries, eight crosswalks, three human-review documents and the original P01 preview are also pinned (14 supporting files). Historical earlier hold lists remain unchanged; current Canonical and later Batch04 evidence determine the present eight-record set. No human approval is inferred from automated `reviewed` strings.

## Deliverable and usable extent

[data/v2/indexes/research/README.md](../indexes/research/README.md) documents manifest-first paths and exact joins. There are **7 indexed Places, 8 existing Opportunities, 8 stable topic IDs and 10 topic associations**; 21 sourced locale-name strings. All eight are RESEARCH_ONLY; GUIDE_ELIGIBLE count0. `regions=0`, verified timezone count0; complete-region-picker eligibility is false.

Names are exact canonical substrings with original locale pointers/code-point ranges; descriptions and safety/access content are retained by canonical reference. Topic labels/English scope copy W1; zh-TW/ja operational-scope translations require human review and add no new Place claim. Source-backed assignments use actual target/descriptions/existence references. The pending three-language vocabulary review is explicit, not a claim of official translation approval.

## W1 precision handoff — safe implementation chosen

1. W1 requests a complete TW22/JP47/US51 picker registry, while Task X restricts input to existing W2 Canonical/evidence and forbids new research/inference. Those sources contain no verified ISO registry/membership dataset. Safest permitted implementation is an empty registry + seven UNKNOWN admin memberships, with a machine-readable incomplete-picker flag. This does not satisfy or lower the complete-picker gate. Please accept a partial research feed or supply/approve a specific pre-existing sourced registry via a later W2 task. Do not infer Taiwan/US/Japan from `tw-`/`us-`/`jp-` IDs.
2. No existing verified Place-scope IANA assignment is available; all UNKNOWN. A syntactically valid Asia/Taipei/Asia/Tokyo/America/Los_Angeles string is not evidence. Supply explicit source/evaluation-scope approval in a later authorized task; current 02B queries remain NOT_EVALUABLE.
3. W1 core schemas forbid extra provenance fields. Name ranges, definition provenance, missing-field/capability status and manifest hashes are W2 sidecars, with unmodified W1 Place/topic documents. Please review this companion transport before W4 treats it as a long-term API; no hidden schema change was made.
4. Topic definitions are W1-scope translations pending human parity review, not new research. If literal reviewed three-language definitions are required before any research vocabulary display, keep definition text behind explicit research/technical disclosure until that review; do not silently claim human approval.

## W4 read and implementation handoff

Read `data/v2/indexes/research/manifest.json` from the accepted exact W2 source, verify its four file hashes plus source-lock/curation hashes, and load `place-index.json`, `topic-index.json`, `field-provenance.json` and `index-status.json` as one revision. Validate against accepted W1 #489, never assume merged. Fetch Canonical from each binding's pinned commit/path; verify Git blob/revision/identity before displaying full descriptions, all localized access/safety warnings and subject information. Preserve original P01 history separately.

Use an explicit Research-only entry, group by stable Place ID, and support two Opportunities at tw-026. OR within regions/topics, AND between dimensions; topics filter eligible Opportunities before Place grouping. No ordinary guide or selected-date recommendation is authorized. Source-preserving proper-name excerpts may be shown with pending semantic review confined to technical context; don't relabel a composition title as an official Place name. Chongde's short label/extent needs human confirmation.

With this data, country/admin controls cannot claim complete TW22/JP47/US51 readiness. Represent unavailable metadata clearly; don't create fabricated options from ID prefixes or Legacy runtime. Missing source registry is distinct from a verified region with no catalogued Places. Name/ID/topic exploration works; explicit nonexistent region filter is invalid. Date-dependent evaluation is unavailable for all seven until evidence confirms timezone; no browser fallback. SCORE/DISTANCE remain disabled absent valid runtime/location data. The four test fixtures are not runtime inputs or a production capability declaration. Default/fallback REGION semantics and missing-last stable-ID behavior remain W1-owned; no fake distances/GPS or 0 scores.

## W5 source pins and integration gates

- Independently accept/repin **both** latest W1 #489 and this final W2 HEAD/tree. W2 is based on latest main without W1 bytes; testing requires the pinned W1 spec root or an intentional combined checkout. Do not merge stacked W1/W2 assumptions or weaken owner-tree/source gates.
- Preserve existing Canonical/source/audit/preview blobs, especially original P01 SHA1/SHA256 checks and current eight source pins. New W2 index source is a separate immutable provenance layer, not a replacement for #458/#468 history.
- Keep the existing15 W2 unittest methods; add actual18 Task X methods → **33 W2 cases**, zero fail/error/skip. Do not inflate counts with schema gates or reference assets. Add the independent six-schema CLI and `research_index.py validate --git-provenance`; provide declared source Git objects without network calls inside tests.
- Validate complete Canonical ID set, three-language source spans, topic/existence joins, checksum/revision tamper negatives, no publication escalation, admin UNKNOWN, timezone fail-closed and original warnings. Synthetic multi-country/admin rows exist in tests only; they are not real assignments or proof of registry completeness.
- Add W4 desktop/mobile ×3-language browser cases in the W4 implementation task: seven-name selection/search, same-Place two subjects, OR/AND, research-only isolation, unknown admin/timezone, no Directions/forecast/score, retained closures and stale/invalid loading behavior. No browser or full combined CI is claimed by this W2 task.
- Existing W1 integration failure/source-pin enforcement is not waived here. W5 must read actual final-head results, deliberately rotate pins and preserve all prior thresholds. Region/timezone incompleteness stays a product prerequisite and human/source handoff, not a test SKIP or fabricated data.

## Per-Place missing fields and human confirmations

| Place ID | Sourced name labels (not human approval) | Still missing / review |
| --- | --- | --- |
| jp-010 | 大石公園 / Oishi Park / 大石公園 | Country/admin code and scope; verified timezone; name/definition parity. |
| tw-016 | 鳶嘴山 / Yanzui Mountain / 鳶嘴山 | Country/admin code and scope; verified timezone; name/definition parity. |
| tw-026 | 井仔腳瓦盤鹽田 / Jingzaijiao tiled salt pans / 井仔脚瓦盤塩田 | Same missing metadata; original lookout closure/current lawful areas/arrival remain independently unresolved. |
| tw-034 | 崇德 / Chongde / 崇徳 | Same missing metadata; full official Place identity/extent and short-label suitability additionally pending. |
| tw-036 | 七星潭 / Qixingtan / 七星潭 | Country/admin code and scope; verified timezone; name/definition parity. |
| tw-082 | 鯉魚潭 / Liyu Lake / 鯉魚潭 | Country/admin code and scope; verified timezone; name/definition parity. |
| us-071 | Kerry Park / Kerry Park / ケリー・パーク | Country/admin code and scope; verified timezone; proper-name/definition parity. |

All eight Opportunities still need actual human evidence/crosswalk/three-language release review; all geometry, lawful camera boundaries, current access notices and practical arrival points retain their original uncertainties. No approved AUTO/threshold/provider/score was added. No fixed camera coordinate is required to finish this research index; no candidate point becomes navigation.

[Actual commands, counts, initial failure and final results](../tests/logs/task-x/RESULTS.md). Task X ends with its independent W2 Draft PR and waits for W4; further data research/registry acquisition requires a separate authorized task.
