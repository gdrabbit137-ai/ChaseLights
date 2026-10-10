# ChaseLights V2 — Integration Status

Snapshot: 2026-10-09 19:57 Asia/Taipei. Owner: Worker 5.
Latest verified main: `aa2b3b18be5944f7f633f2662a6ac70c937752d3` (GitHub branch ref).

| Milestone | State | Verified evidence | Missing acceptance |
| --- | --- | --- | --- |
| M1 | IN_PROGRESS | PR #428 head `a93a9832c11f6ea5cf7a9d81de39384333efb7f6`, Draft; schema v2.1, architecture, validator and reference tests exist | Actual unittest and formal CI, R4.2 latest-main gate, review, merge |
| M2 | BLOCKED | W2 head `d3d8b17a138dcec2f41695bd4820125feaa68f66`, 3 research-only Opportunities and 108 crosswalk rows; independent audit artifact exists | Formal W1 schema gate, per-claim external evidence verification, semantic parity in zh-TW/en/ja, reviewed merge |
| M3 | IN_PROGRESS | W3 head `7dbd6434cdd8f47110c2648f08ff495a76fc1a6c`, executable test-only evaluator and 16 test methods | Executed tests, approved real weather/astronomy source and contract, positive/negative/unknown real trace, CI |
| M4 | BLOCKED | W4 head `f4ceeb36de90d870c01ca594d8ee61fe2f8a9650`, V2 isolated site and canonical import test | Non-SKIP W2 test, W3 real evaluation, accessible three-language UI, mobile/desktop and public smoke |
| M5 | IN_PROGRESS | W5 offline integration candidate and tests (previous local 13/13); PR #429 head `c450227373b2fcbd0bdacf521065be7127044474` | GitHub integration workflow/checks, V2 Pages and browser smoke, only then localized Legacy link |

Automations: W1–W5 enabled, Asia/Taipei hourly :15/:25/:35/:45/:55. Last run UTC W1 11:17:45, W2 11:24:38, W3 11:38:07, W4 11:49:11, W5 prior 11:02:29. No sixth V2 worker. `automations.list` available, `peek` unavailable.

GitHub: PR #428 and #429 both Draft and reported not mergeable; checked commit status lists empty and PR-head workflow runs absent at the inspected heads. Latest Pages run #37926601340 succeeded for main `aa2b3b1` but this is Legacy, not V2. V2 public HTTP/browser smoke unavailable; no V2 readiness claim.

Current blocker: no formal V2 integration workflow/checks. Earlier GitHub workflow/create PR/update requests returned `This tool call was blocked by OpenAI's safety checks.` Do not bypass. W1 schema gate and W3 real-input adapter remain separate critical dependencies.

No Legacy index/scoring/runtime edits, no automatic Legacy/V2 comparison, no release approval.
