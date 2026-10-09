# ChaseLights V2 — Integration Status

Snapshot: 2026-10-09 14:59 Asia/Taipei. Owner: Worker 5.
Latest verified main: `684cf7510eec43206fca01252dbd0df82ec0298b`.

| Milestone | State | Verified evidence | Missing acceptance |
| --- | --- | --- | --- |
| M1 | IN_PROGRESS | PR #428 head `1788b0b68e8cdab4064737baad52bd96d04750fa`; schema and validator exist | Real negative reference test, schema CI, review, merge |
| M2 | BLOCKED | W2 branch has 3 canonical records, crosswalks and tests | Schema gate, source review and semantic parity |
| M3 | BLOCKED | W3 branch differs only by README | Executable evaluator, tests and real inputs |
| M4 | BLOCKED | W4 branch has site, loader and real-data test source | Test with original W2 data, W3 runtime, public browser proof |
| M5 | IN_PROGRESS | W5 integration gate and browser-smoke source exist | GitHub CI, real V2 Pages, public smoke and later legacy link |

Workers W1–W5 enabled and staggered at :15/:25/:35/:45/:55 Asia/Taipei.
Main Pages run 37894865917 succeeded for Legacy, not V2.
PR #428 and #429 remain Draft with no check-runs at their inspected head commits.
The canonical V2 path is not in main. Public URL could not be verified: DNS resolution unavailable in execution environment.
Workflow upload and integration-gate update were rejected by connector safety checks during this run.
No legacy index/runtime/scoring changes, no old-vs-new automated comparison, and no V2 release claim.
