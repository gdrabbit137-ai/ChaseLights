# Task X actual W2 validation

Reviewed base/main: `500ec3a76b5f77a0752ecdca5cc1b12fa63d223d`. External W1 source: Draft #489 `38b234ba5f4df4a751eaea14dcc79036b45ed180` (not assumed merged). Original Canonical commits are declared per record in `../../../indexes/research/source-lock.json`. Final PR SHA is recorded in the Draft PR rather than self-referenced in this commit.

| Actual command / gate | Result |
| --- | --- |
| `CHASELIGHTS_W1_SPEC_ROOT=<pinned specs/v2> python -m unittest discover -s data/v2/tests -p 'test_*.py' -v` | **33 PASS / 0 FAIL / 0 ERROR / 0 SKIP**, exit0, 2.077s. Existing15 retained; Task X adds18. Raw output `w2-unittest.log`. |
| `python <pinned W1>/tests/validate_task_w_contracts.py <work schema-bundle>` | **Six PASS**: place-index/date-query/topic-index/local-preferences/browse-query/sort-capabilities, exit0. Raw `w1-six-contracts.log`. The bundle copies the two real index files plus four explicit test-only documents; it is not a runtime result artifact. |
| `python data/v2/tools/research_index.py build --w1-root <pinned specs/v2> --git-provenance` | PASS deterministic rebuild, six-schema/semantic/reference checks, actual source commit:path provenance, exit0. Raw `index-provenance.log`. |
| Git diff/owner/source isolation | PASS; only new W2 files, no existing Canonical/audit/crosswalk/review/preview/test changes; no W1/W3/W4/W5/Legacy edits. Raw `scope-check.log`. |

Environment: Python3.12.14, jsonschema4.26.0, system IANA tzdb2026b. Commands used `/workspace/chaselights-venv/bin/python` with `PYTHONDONTWRITEBYTECODE=1`. Source roots are explicit inputs, not assumed main contents. `source-sha256.json` records tested W2 bytes excluding log directories and bytecode. W1 dependency files have independent exact blob/SHA256 pins. There was no data/source/schema/threshold relaxation.

## Preserved initial failure

The first real suite executed33 methods: **32 PASS / 1 FAIL / 0 ERROR / 0 SKIP**, exit1. Raw output is retained as `initial-failure.log`. One newly written regression mistakenly asserted the older historical P01 blob `3459ee…`; actual accepted #458 source `2177bd8…` and reviewed main both resolve to `001a3380231e3d073e900bf2b415aac7dcc5fd79`. The literal test expectation was corrected to that independently checked current source. Canonical and source-lock bytes did not change. The final full suite above passed with the same strict blob guard.

## Meaning and remaining limits

7 Places / 8 Opportunities / 8 taxonomy IDs / 10 topic edges; 21 exact sourced name strings. **0 verified administrative registry entries, 0 verified Place timezones, 0 GUIDE_ELIGIBLE records**. Seven admin/timezone gaps remain UNKNOWN because the restricted existing W2 source set cannot prove them. Complete TW22/JP47/US51 picker readiness is false and not waived. Definition translations are W1-scope derived and require human semantic review.

Six schema gates are not added to unittest counts. Synthetic multi-admin values and the four extra-format fixtures are test-only; they establish representation/failure behavior, not real geography, storage, runtime, provider, forecast or navigation. No W4 browser, full W5 integration, public URL, live source, human signoff, merge or deployment PASS is claimed. W5 must independently accept exact W1/W2 pins and retain all existing gates.

[W4/W5 paths, missing fields and human handoff](../../../reviews/TASK_X_HANDOFF.md) · [Index read contract](../../../indexes/research/README.md).
