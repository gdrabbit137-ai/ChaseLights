# W3 Open-Meteo hourly RAW_ONLY pilot — independent live capture (second one-shot)

Owner: W3, `packages/core-v2/` only. Manual, budget-compliant, single attempt.
No scheduler, no evaluator, no deployment.

A verified one-shot capture already exists in the W5 archive
(`ops/v2/integration-sources.json` `one_shot_evidence`, commit
`93707e108…`, evidence source `93707e108`/execution `7ae28020`, response
4,468 bytes, `source_sha256=e441ea1b…`). This capture independently
reproduces provider acceptance from a different environment and a later
clock; it is supplementary evidence, not the first.

## Environment

- Executed from the owner's Windows workstation, which permits the HTTPS
  endpoint (the 2026-10-19 evidence environment was network-restricted and
  could not reach the provider).
- Capture tooling fixed for that platform before the attempt:
  ledger lock via `msvcrt.locking` fallback (`fcntl` is POSIX-only),
  `os.O_NOFOLLOW` via `getattr` fallback, and the POSIX wall-clock deadline
  (`SIGALRM`/`setitimer`) short-circuits to the documented 20 s socket
  timeout where those primitives are absent. POSIX behavior is unchanged;
  `unittest` suite: 121 tests OK (1 platform-guarded skip).
  The socket `timeout=20`, no-redirect, identity-encoding, host and TLS
  checks in `fetch_one` are unchanged and apply on every platform.
- Base HEAD: `7f2e648c3330489c0b60622d3e793bbabd2be02b` (post-breadth-migration main).

## Capture facts

- One HTTPS attempt; HTTP 200; `application/json`; identity encoding;
  no redirect; body complete: 4,582 bytes.
- Raw body SHA256: `a121471780fae6b5…` (full value in `capture.json`).
- Request URL is the exact contract request for `tw-036` (lat 24.031426,
  lon 121.62717, 72 hourly rows, ten fields, GMT/unixtime).
- Normalized artifact: `data_state=RAW_ONLY`, `availability=COMPLETE`,
  72 hourly rows, 720/720 cells AVAILABLE, no synthetic values.
- Response grid point: latitude 24.007029, longitude 121.59067,
  elevation 14.0 m — recorded as the provider-selected grid, distinct from
  the request point.
- `source_update_time_utc`, `provider_issued_at_utc`, `provider_run_id`,
  `resolved_model_ids`, `native_resolution_m`, `native_time_resolution_seconds`
  are null with reason `NOT_SUPPLIED_BY_FORECAST_RESPONSE`; `model_selection`
  is `provider_default_auto`; `source_freshness=UNKNOWN`.
- Time zone: `Asia/Taipei`, tzdb release observed at execution: `2025c`.
- Budget: one ledger reservation (`capture-ledger.jsonl`); ≥3 h from any
  prior capture; well under the eight-per-day cap; `automatic_retries=0`.

## Replay

`replay.json`: OFFLINE_REPLAY PASS, `availability=COMPLETE`, zero reasons,
zero network attempts. Hash/identity/contract checks passed against the
archived original bytes.

## Provider acceptance status

`CAPTURE_COMPLETE_REPLAY_PENDING` → after this replay: provider units,
returned grid, and complete 72-hour horizon have now been observed again in
a second independent authorized environment, consistent with the archived
one-shot. Acceptance remains scoped to these two captures; no long-term SLA
is inferred and no automatic retry is authorized.

## Still separate (unchanged)

Human W1/W2 translation approval, coastal representativeness, scientific
calibration, photography thresholds/AUTO, W4 read-only display, W5 release
authorization, and any `forecast_available` promotion. This artifact is
RAW_ONLY research weather information, not a photography forecast.
