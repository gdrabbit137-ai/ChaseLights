# Governance decision — cancellation of the human re-review gate (owner decision, 2026-10-22)

Status: ACTIVE owner decision. Supersedes the "explicit W2 source re-review admission"
requirement for migration and future spot additions. Recorded by the owner in-session.

## Decision

1. **The separate human re-review cycle for V2 data admission is cancelled.**
   Migration records (and all future new spots) are admitted into
   `data/v2/opportunities/` once they pass the automated gates:

   - `opportunity-v2.1` schema validation (strict);
   - deterministic generation with byte-verified provenance
     (source catalog/weather files pinned, reproducible, idempotent);
   - per-Place V1 parity checklist (`data/v2/migration/parity/`) with
     MISSING_IN_V1 recorded honestly — nothing fabricated;
   - three-locale content carries zh-TW source values verbatim with explicit
     provisional/pending-translation markers — no invented translations;
   - access/closure information stays a verbatim, non-scoring warning
     (ACCESS_ADVISORY advisory-only principle);
   - navigation stays `needs_review`/low confidence — no unverified directions;
   - everything stays R0 / RESEARCH_ONLY, never a live forecast.

2. **Future new spots require no human review either.** The same automated
   gates apply. Adding a spot is a data-entry + regeneration action, not a
   review cycle.

3. **Translation quality and access-notice currency are owner-maintained.**
   The owner keeps trilingual wording and access-notice freshness up to date
   directly; the system must not block publication on them.

## What does NOT change

- No live forecast, FAVORABLE verdict, verified directions, or deployment
  authorization follows from admission. Those gates remain separate.
- Provenance, schema, reproducibility and research-only publication rules
  remain enforced by tests/CI.
- Legacy/V2 isolation and the W1 shared-contract pins remain untouched.

## Implementation note

`data/v2/indexes/research/` (source-lock, curation, generated indexes) is the
recorded admission of the migrated canonical set. `curation.json` and
`research_index.py` projections are extended mechanically for the full set;
unclassified opportunities are recorded as `unclassified_opportunity_ids`
rather than force-fitted to the eight-topic vocabulary.
