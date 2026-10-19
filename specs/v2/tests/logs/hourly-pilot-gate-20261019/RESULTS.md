# W1/W2 hourly pilot gate validation — 2026-10-19

Reviewed main: 67e8a14e9ccbfd0eef7ca96c09b4c872a3d519d2; W3 audit reference #520 a649ace57cda5ca02edc1481660ef2f567eb86f1. Only specs/v2 and data/v2 changes. No source pin, V1, W3 runtime, W4 website, production data or weather models changed. No live Open-Meteo response, accuracy, current forecast, integration/browser acceptance or deployment claimed.

Actual local results: W1 **79 PASS / 0 FAIL / 0 ERROR / 0 SKIP** (67 existing +12 new); W2 **38 PASS / 0 FAIL / 0 ERROR / 0 SKIP** (33 existing +5 new); eight actual Canonical records PASS; six shared-contract fixture validators PASS; git diff --check PASS. Included raw unittest/validation logs, not synthetic test-run summaries. Validation counts are distinct from a full W5 release gate.

Commands from the checkout, with jsonschema 4.26.0 and PyYAML 6.0.3 installed in scratch tooling:

```
PYTHONPATH=<scratch-tooling> PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s specs/v2/tests -p 'test_*.py' -v
CHASELIGHTS_W1_SPEC_ROOT=<checkout>/specs/v2 PYTHONPATH=<scratch-tooling> PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s data/v2/tests -p 'test_*.py' -v
PYTHONPATH=<scratch-tooling> PYTHONDONTWRITEBYTECODE=1 python specs/v2/tests/validate_contract.py data/v2/opportunities/*.json
PYTHONPATH=<scratch-tooling> PYTHONDONTWRITEBYTECODE=1 python specs/v2/tests/validate_task_w_contracts.py
```

An initial W2 invocation omitted its existing mandatory CHASELIGHTS_W1_SPEC_ROOT and reported 19 passing tests +1 environment setup error; after supplying the actual pinned W1 directory, the complete 38 passed. No test was skipped or gate relaxed. The runtime tzdb at this local check is 2025b from /usr/share/zoneinfo/tzdata.zi; the synthetic fixture's 2024a label is test-only, never a runtime version claim.

The new synthetic fixture is explicitly TEST_FIXTURE and uses no real weather. W1 tests are executable schema/semantic examples, not the W3 adapter or transport. W2 checks pin the existing canonical blob, explicit representative-sample role, individual timezone evidence, noncommercial scope, trilingual limitations and unchanged public-index UNKNOWN zone/navigation/geometry.

Expected W5 disposition: new W1/W2 owner trees require deliberate independent source-pin/tree/count/baseline acceptance. This Draft must not update W5 pins merely to pass CI. Integration may stop before running suites due the changed owner trees, as #520 did for W3; report that actual failure separately from passing local W1/W2 validation. Final PR HEAD and actual Actions outcomes are recorded in the PR description, without self-referential HEAD edits to these logs.
