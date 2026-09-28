# B104 — Cross-Version Field Snapshot Matrix Replay

Date: 2026-09-29 (Asia/Taipei)

## Purpose

B104 verifies the requirement that one immutable Field Snapshot can be replayed
against more than one ChaseLights code version.

The first permanent baseline remains:

- snapshot: `FVS-TW-034-20260928-163925`
- original production commit: `fadfc65aeb8e9219cec2b60fc0ed91bf9fc98e21`
- archive: `test_fixtures/field_snapshot/FVS-TW-034-20260928-163925.json.gz.b64`

## Provenance issue found

B101 originally checked `GITHUB_SHA` before `git rev-parse HEAD`.

That is unsafe for detached replay worktrees because a GitHub Actions process may
retain the outer workflow SHA while executing code checked out at an older target
commit.

The scoring code itself still came from the correct worktree, but the replay
metadata could incorrectly label the executed version.

B104 fixes this by:

1. preferring the checked-out Git HEAD,
2. using `GITHUB_SHA` only when Git metadata is unavailable,
3. removing `GITHUB_SHA` from the environment passed to a target-version replay
   subprocess.

## Permanent matrix CI

New workflow:

`.github/workflows/test_field_snapshot_matrix.yml`

It uses full Git history and runs:

```bash
python field_snapshot.py matrix \
  test_fixtures/field_snapshot/FVS-TW-034-20260928-163925.json.gz.b64 \
  --commits original current
```

The matrix must prove:

- the archived fixture can be decoded,
- the original commit can execute the same normalized input,
- the original result still matches the recorded B101 baseline exactly,
- the current checkout can execute the same input,
- the replay metadata identifies the actual target Git commit,
- all Qingshui Opportunity IDs remain comparable.

## Future model changes

The CI deliberately does **not** require:

`current_match_recorded = true`

Future scoring changes may intentionally alter P01/P02/P03.

When that happens the workflow remains successful as long as replay itself is
valid; the matrix artifact reports:

- changed Opportunity IDs,
- recorded stable outcome,
- target-version stable outcome.

This turns model evolution into an explicit diff rather than a hidden change.

## Ground-truth boundary

B104 does not change the baseline's status.

`FVS-TW-034-20260928-163925` remains:

- a live forecast snapshot,
- `observation.status = unreviewed`,
- not a field photograph,
- not an `FV-...` field-validation case.

## Runtime/scoring impact

None.

B104 changes only replay provenance and replay CI. No weather threshold,
Opportunity formula, spatial threshold, or UI behavior changes.
