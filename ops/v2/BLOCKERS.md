# ChaseLights V2 — Blockers and next acceptance

Snapshot: 2026-10-09 04:52 Asia/Taipei. Owner: Worker 5.

| Priority | Owner | Blocker and dependency | Direct action | Next objective evidence |
| --- | --- | --- | --- | --- |
| P0 | W1 | PR #428 is draft, 23 main commits behind, no reported check runs; 9 changed files omit CI workflow. All downstream workers depend on canonical schema. | Rebase/reconcile latest main; add schema validator positive/negative fixtures and CI workflow within W1 spec-gate ownership; obtain passing PR checks and spec review. | #428 green checks, mergeable, approved and merged SHA. |
| P1 | W2 | `data/v2/tests/test_worker2_batch03.py` loads nonexistent `worker2_batch03.jsonl`; canonical schema not on main. | Deterministically load all three existing crosswalk JSONL files and test every claim/condition, then validate against W1 schema; keep research-only. | Reproducible passing data tests, human/machine evidence and locale audit. |
| P1 | W3 | No independent V2 runtime commits; W2 records and W1 contract needed. | Build deterministic evaluator in `packages/core-v2/` with conservative unknown propagation and positive/negative/unknown tests; use legitimate real provider input. | Commit/test logs and structured evaluation with source/valid times. |
| P2 | W4 | Existing `apps/web-v2/` preview not on main; empty newer branch. | Continue actual 4-commit branch, adapt to W1/W2/W3 without synthetic forecast; verify zh-TW/en/ja and mobile/desktop. | Preview PR/tests and data boundary checks. |
| P2 | W5 | No merged V2 CI/deploy; Pages success only proves Legacy; public V2 URL unverified. | Prepare independent integration CI and public smoke; do not modify Legacy link until V2 verified. | V2 CI run, public HTTP/browser smoke, Legacy isolation proof. |

If a write or deploy operation is rejected, preserve exact tool/API error; do not bypass a safety or permissions gate. Every worker must re-read current main R4.2 and V2 contracts before merge.
