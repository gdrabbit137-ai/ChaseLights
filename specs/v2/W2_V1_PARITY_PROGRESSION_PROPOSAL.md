# W1 proposal — V1 information parity as W2 migration progression gate

Status: Draft proposal for owner review; applies to **R1 Research-only migration only**, not live forecast or verified navigation.

## Decision
For an existing Legacy V1 Place, W2 may mark the V2 migration batch ready for downstream Research-only integration once it has faithfully transferred all **available, relevant V1 user-visible information** (name, place identity, location with original precision/provenance, photography topics, description, season/time and documented conditions) into the V2 canonical structure, without fabricating missing fields. Keep complete semantically equivalent zh-TW/en/ja presentation. Preserve original V1 provenance as *legacy-derived*, never mislabel it as newly verified primary evidence.

This is a **progression criterion**, not a declaration that V1 content has been scientifically verified or that every V1 claim qualifies for R1. If subject existence lacks support required by R4.2, provenance is fabricated, translations materially diverge, or a safety claim falsely assures lawful access, record the specific affected claim as HOLD/R0; continue other independently valid places and claims. Do not let an optional unresolved item block the whole batch.

## W2 implementation
1. Compare migrated V2 fields against the actual V1 record and record a per-Place parity checklist with source path/revision, missing fields and explicit uncertainties.
2. Preserve available V1 photography information; do not require new fixed Camera GPS, Subject Zone polygon, EXIF, exact arrival point, or additional primary-source research merely to continue migration.
3. Carry known closure/access information as an independent warning, never a photography score blocker. Keep unverified navigation disabled.
4. Once parity and schema/semantic checks pass, hand the research-only record to W3/W4/W5 and **advance to the next batch**. Track optional evidence/field review in a separate follow-up queue; reopen only for material factual errors, changed official access notices or targeted promotion-to-live work.
5. Existing Jingzaijao tw-026-P01/P02 should be assessed under this same parity checklist; do not repeatedly restart generic W2 research because W3/W5 use their immutable test fixtures.

## W3/W4/W5 boundaries
- W3 can implement/test evaluators using verified canonical fixtures and keep missing real inputs UNKNOWN/NOT_EVALUABLE. No fabricated AUTO threshold, source coverage, score or FAVORABLE.
- W4 can display qualifying migrated records as clearly labeled Research-only, with full three-language content and separate access warnings, no unverified Directions.
- W5 should test parity, provenance, schema, locale semantics, warnings and immutable source pins for Research-only release. **Do not require completion of optional site-specific geometry or all human research follow-ups to advance unrelated batches.** Keep current-head CI and independent release approvals.
- Formal live forecast, precise navigation and unsupported claims retain their existing stricter approval/evidence gates.

## Next owner tasks
- W2: implement per-record V1 parity evidence/checklist in data/v2 and continue the next five distinct Places.
- W1: reconcile any contradictory R1 review language in applicable specs before promotion.
- W5: update integration tests only after reviewing W2's exact source tree; never bypass source pinning or reduce test coverage.

This document does not authorize merge, deployment, live scoring, or blanket legal/safety signoff.
