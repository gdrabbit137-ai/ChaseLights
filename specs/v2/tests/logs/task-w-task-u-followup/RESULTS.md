# Task U attachment follow-up — actual W1 results

This follows initial Task W commit `3e5a6007c57e704dfec401976f64da74b8321faf` in the same Draft PR #489. The original 65-case result/logs remain historical evidence under `../task-w/`. No full Task U inventory was repeated. See [bounded source reconciliation](../../../TASK_U_REFERENCE_RECONCILIATION.md) for original attachment hashes and actual read scope.

| Actual command | Result |
| --- | --- |
| `python -m unittest discover -s specs/v2/tests -p 'test_*.py' -v` | **67 PASS / 0 FAIL / 0 ERROR / 0 SKIP**, exit0, 3.030s. Original36 + initial Task W29 + follow-up2. Raw output `unittest.log`. |
| `python specs/v2/tests/validate_contract.py` | Existing canonical fixture schema/reference PASS, exit0; raw output `canonical-validation.log`. |
| `python specs/v2/tests/validate_task_w_contracts.py` | All six formats + semantic/provenance/reference gates PASS, exit0; raw output `task-w-validation.log`. |
| `git diff --cached --check` / owner isolation | PASS; all paths under specs/v2; six new schema bytes unchanged since initial Task W; Legacy/other owners and existing canonical/runtime schemas unchanged. Raw output `scope-check.log`. |

Used `/workspace/chaselights-venv/bin/python`, Python3.12.14/jsonschema4.26.0/system IANA2026b, with `PYTHONDONTWRITEBYTECODE=1`. `source-sha256.json` identifies the exact tested W1 source bytes, excluding historical/new logs and bytecode. Final remote SHA is reported in PR metadata rather than self-referenced here.

New tests are W1 acceptance examples for sourced admin-name/code search with stable same-name identities and relative dates from frozen UTC per Place with shuffled provider daily arrays. They are not W4 browser/controller tests or a provider integration. Complete TW22/JP47/US51 registry, storage/permission behavior, UI region fallback and semantic human review remain W2/W4/W5 handoffs.

No schema format change, production implementation, full integration/browser/public/live-provider/merge/deploy validation is claimed. This attachment resolves the original access limitation, but only U-F05–U-F12 were checked; no claim of a full 40-row review or fresh verification of Task U's historical tests.
