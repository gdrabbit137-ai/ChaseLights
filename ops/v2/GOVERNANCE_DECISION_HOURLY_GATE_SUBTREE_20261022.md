# Governance decision — hourly gate integrity checks realign to subtree level (owner decision, 2026-10-22)

Status: ACTIVE owner decision. Recorded by the owner in-session; authorization
to implement given 2026-10-22.

## Context

The hourly owner-integration gate (`ops/v2/simulate_merges.py`,
`hourly_owner_integrations`) was designed for the codex owner-branch flow,
where W1+W2 owner changes arrive on main as ONE dedicated commit whose
cumulative diff since the fork point touches only `specs/v2/` and
`data/v2/`. The V1→V2 breadth migration (no-review gate, 2026-10-22)
instead lands owner changes on a feature branch whose commits legitimately
mix owner trees with W4 app (`apps/web-v2/`) and pin bookkeeping
(`ops/v2/`) changes. Under the old check, NO commit of the new flow can
ever satisfy the permitted-paths test, so the gate structurally blocks the
product's actual release path.

## Decision

1. The integrity INTENT of the hourly gate is preserved and restated at the
   level that actually enforces it:
   - the hourly source commit exists, is not the candidate itself, and is
     an ancestor of the candidate;
   - the source's owner subtree equals the pinned `tree_sha` AND the
     candidate's subtree byte-for-byte;
   - the base's owner subtree equals the recorded `previous_trees`.
   These subtree-level equality checks are the real integrity guarantee and
   are RETAINED unchanged.

2. The cumulative-diff "permitted paths" check is REPLACED by the
   subtree-level equality above. It was a proxy for owner isolation under
   the old flow; the byte-level subtree pins now carry that guarantee
   directly, and `owner_integrations`/`owner_trees` checks already enforce
   that the merged tree contains no nonowner drift in the pinned trees.

3. The requirement that W1 and W2 share ONE source commit (the paired
   codex-branch integration) is REMOVED. Each owner's source is validated
   independently: it exists, is a proper ancestor of the candidate, and its
   owner subtree equals both the pinned tree_sha and the candidate's
   subtree. The W1 pin stays at the reviewed PR 521 source; the W2 pin
   records the breadth-migration integration commit. This applies to the
   current breadth-migration integration and to ALL future owner
   integrations, including the W4 transition rows (whose cumulative-diff
   nonowner scan is likewise replaced by the source-tree pin plus the
   merged-tree subtree equality in rehearse()).
4. This decision document lives under `ops/v2/` (W5-owned) rather than
   `data/v2/` so that recording it never touches a data owner tree.

5. What does NOT change:
   - fail-closed behavior: any mismatch still blocks the release gates;
   - W3 package isolation and the hourly pilot's RAW_ONLY/NOT_EVALUABLE
     status;
   - the Legacy/V2 isolation and W1 shared-contract pins.

## Rationale (product goal)

V2 must fully replace Legacy. The release path is: owner changes via PR →
main → automated re-pin → W5 release gate → publication. A gate that can
only express the retired codex-branch flow would either be permanently red
or permanently exempted (exemption debt). Re-leveling the checks keeps the
same integrity guarantee working for the flow the product actually uses.
