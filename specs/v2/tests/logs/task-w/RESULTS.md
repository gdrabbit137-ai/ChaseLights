# Task W actual W1 validation

Reviewed base: `dcb1a22f1af6f1d07f0e0e1fa1233c1d0f5d069f`. Validation ran in the isolated real checkout, with four unchanged pinned canonical records read from Git by the provenance CLI. These results apply to the exact specification/schema/test bytes recorded in `source-sha256.json`; that manifest excludes this results/log directory and Python bytecode. Final commit SHA is recorded in the Draft PR to avoid a self-referential commit hash.

Environment: Python 3.12.14, jsonschema 4.26.0, system IANA tzdb 2026b. Synthetic date test metadata is explicitly test-only; it is not a verified Place timezone claim.

| Actual command | Result |
| --- | --- |
| `python -m unittest discover -s specs/v2/tests -p 'test_*.py' -v` | **65 PASS / 0 FAIL / 0 ERROR / 0 SKIP**, exit 0. Original 36 cases retained; 29 Task W cases added. Raw output: `unittest.log`. |
| `python specs/v2/tests/validate_contract.py` | Existing Opportunity fixture schema + references PASS, exit 0. Raw output: `canonical-validation.log`. |
| `python specs/v2/tests/validate_task_w_contracts.py` | Six schema documents + cross-reference/canonical hash/date/topic/preferences/capability checks PASS, exit 0. Exact commit:path canonical bytes read successfully. Raw output: `task-w-validation.log`. |
| `git diff --cached --check` and owner-path check against base | PASS; every changed file is under `specs/v2/`, old canonical/runtime schemas and other-owner/Legacy trees unchanged. Raw output: `scope-check.log`. |

`python` above used `/workspace/chaselights-venv/bin/python` and `PYTHONDONTWRITEBYTECODE=1`. The initial 28-case Task W run and 64-case full run passed; one index/timezone/canonical-binding regression was then added, and the final full 65-case run passed. No test was removed/skipped or threshold lowered. Schema definitions were factored with local `$defs` to avoid duplicating capability/day/artifact structures.

Unit tests intentionally work in shallow PR checkouts: they check current canonical bytes against pinned fixture Git blob hashes. The separate provenance CLI checks the declared commit:path; W5 needs those explicit Git objects available. Neither path authenticates human evidence, geographic/timezone assignment or translation parity. Reference filter truth tables are W1 test oracles, not W4 production behavior.

No W2/W3/W4/W5 implementation, full integration suite, browser, public URL, live provider, forecast or deployment validation was performed by this task. Existing W5 source pins have not adopted this W1 tree; an integration pin mismatch is a cross-owner handoff, never a waived gate. GitHub checks on the final PR must be read separately from these local results.

Human gates and next tasks: see [Task W handoff](../../../TASK_W_HANDOFF.md). Task U original matrix/Roadmap location remains unconfirmed; no 40-feature re-inventory was performed. This task ends after creating its Draft PR; no merge or deploy.
