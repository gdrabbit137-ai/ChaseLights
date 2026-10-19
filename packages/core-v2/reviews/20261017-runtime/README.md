# W3 runtime verification evidence

Draft PR: https://github.com/gdrabbit137-ai/ChaseLights/pull/513

These logs pin executable code commit `9821b5234c1fec127c7a19b4c4e5ea7f25c93f85`.
This evidence-only follow-up changes no executable code or test inputs.
All local counted groups: **265 PASS / 0 FAIL / 0 ERROR / 0 SKIP**.
Commands and per-group counts are in `verification.json`; `*-head.log` files
contain actual stdout/stderr. The W2 initial dependency-configuration error is
preserved in `data-tests.log`; the corrected run is `data-head.log`.

`live-attempt-head.json` is the actual default-transport runtime attempt on
that exact code HEAD. It has no weather records and returns UNKNOWN /
PROVIDER_TRANSPORT_UNAVAILABLE, never a fake provider success. The proxy's
HTTPS CONNECT 403 is preserved separately (header transcript line endings normalized). The source bytes therefore cannot
be archived or independently verified for this execution.

`w5-gate.log` and `isolation.log` preserve separate failures, excluded from
the local passing-test total: exact W3 source-pin mismatch and unavailable
public HTTP. No browser or deployment success is asserted.

GitHub Integration also failed on the proposed merge for the same source-pin
mismatch, before running its counted groups:
https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/39073494581
Downloadable CI failure artifact:
https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/39073494581/artifacts/12115634562

W5 must independently review/repin, rebaseline 329→353 for this change and run
current-head release verification. See `../../REAL_FORECAST_RUNTIME.md` for
Provider inventory, native data limits and the next pilot admission conditions.
