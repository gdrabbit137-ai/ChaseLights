# W2 Batch04 — R1 proportionate review handoff

Status: **triage pending independent evidence and semantic review**. This record does **not** certify A/AUTO-PASS or B/WARN-PASS.

Policy: `specs/v2/W2_PROPORTIONATE_REVIEW_PROPOSAL.md` on main, incorporated by W5 PR #492. Evidence grades A/B/C in R4.2 are independent from the review disposition A/B/C.

## Existing canonical claims (no source promotion)

| Opportunity | Existing evidence source IDs | Review disposition | Outstanding work |
| --- | --- | --- | --- |
| tw-082-P01 | b04-tw082-a, b04-tw082-b | PENDING | Independently verify exact reflection claim scope, three-language semantics and access warning |
| tw-036-P01 | b04-tw036-a, b04-tw036-b | PENDING | Confirm sunrise claim scope and shoreline access warnings; no invented bearing |
| tw-034-P02 | b04-tw034-a, b04-tw034-b | PENDING | Check official trail closure/advisory separately from scenery evidence; no Directions |
| jp-010-P01 | b04-jp010-a, b04-jp010-b | PENDING | Distinguish seasonal lavender from current bloom; validate three languages |
| us-071-P01 | b04-us071-a | PENDING | Check skyline claim scope and park-hours advisory; no exact tripod point |

Source ledger: `data/v2/audits/worker2_batch04_evidence.json`. Listed IDs are references to **existing recorded sources**, not independently reverified links.

## Decision procedure for W2

1. Validate canonical schema, source pointer, human-readable crosswalk and complete zh-TW/en/ja semantics for each record.
2. Independently inspect the actual source and its support for each claimed subject; do not infer source validity from a Grade A label alone.
3. Assign **A/AUTO-PASS** only if all required evidence and checks are confirmed; assign **B/WARN-PASS** only for supported core claims with noncritical UNKNOWN; otherwise **C/HOLD** with an item-specific reason.
4. Keep `human_geo` and `human_trilingual_semantics` PENDING until genuine human signoff. Machine review disposition is a separate field and must not be used to forge signoff.
5. Isolate any C/HOLD item. Do not block unrelated R1 records solely for missing optional EXIF, exact camera polygon or seasonal detail.
6. For every A/B item, require current-head CI and W5 source-lock review before merge; Research-only status is not live forecast authorization, navigation approval or deployment.

## W5 handoff

No Batch04 data promotion is requested by this handoff. W5 must preserve source pins, 157-case CI, Research-only safety and explicit release gates. Issues #465 and #474 remain open for scoped material-risk/human signoff work. This triage is a **planning artifact**, not evidence of completed review.
