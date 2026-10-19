# W3 Open-Meteo hourly RAW_ONLY pilot — execution evidence

Owner: W3, `packages/core-v2/` only. Independent Draft; no merge or deployment.

## Fixed sources

- Base/latest reviewed main: `39c6d9fa4828acabf9976d505778f527f39c775e`.
- Tested final implementation HEAD: `a4bed41483530037b09c258c366c65c94a3018a5`.
- Tested core tree: `2228c6385fb22cbcf6f0837595f01395fd6db0a6`.
- Only real capture HEAD: `9a8d4f58f8bd2ad4d749103db933b3f84118bb03`.
  Subsequent changes only handle deep JSON and escaped unit serialization;
  the CONNECT failure occurred before either path, and no second capture ran.
- W1/W2 #521 HEAD: `74f21b365d366b0d1d12efbc23cf6cce484b6b5e`.
- W3 #520 study HEAD: `a649ace57cda5ca02edc1481660ef2f567eb86f1`.
- W1 schema SHA256: `ce29fee0f08fdd8c71d96a8d33dfb7f68b6235b67e175ac9e1e3775250b06a1a`.
- W2 binding SHA256: `9fb4cc6f89daae3ce851a30f2880847705b4afa6097b7c4c54d19d357b202921`.
- Schema Git blob: `8688cbd5fa090a94087b2a9fdff9fb76948bd232`.
- Binding Git blob: `38c58e742159f05f494dc29c3d96dcb9d75deba5`.

Both PR HEADs matched the user's fixed sources and remained open Drafts.
The #520 changes are research documentation only; latest main already contains
the existing W3 implementation (42 core/10 solar baseline). There was no
overlapping hourly-adapter implementation. #517 is not a dependency.
AGENTS, both R4.2 specs, V2 overview, architecture, governance and local-date
contract were reviewed along with the full #521 gate/binding/schema and #520
study. W1/W2 sources are read from exact Git objects, not copied/modified or
assumed merged. Their SHA256 is checked before use.

`source-provenance.json` records exact tested file digests and the W2 Canonical
commit/path/blob. Evidence-only commits after the implementation change no
adapter/test/tool bytes; W5 must pin the final PR core tree separately.

## Implementation and integrity

One deterministic Open-Meteo request, tw-036, forecast_hours=72, past_hours=0,
ten exact fields, GMT epoch time and explicit units. Coordinate role is not
sent to the API. Original bytes are hashed before JSON decoding. Invalid
transport/identity/time/hash yields no accepted artifact; no old result is
relabelled. Missing/short fields remain per-cell unavailable without suppressing
independent fields. Zero, missing, null, wrong unit and invalid numeric values
are distinct. Short actual horizons remain PARTIAL without padding.

Eight instantaneous fields use T. Precipitation/probability use `(T−1h,T]`,
associated with T's Place-local date, not shifted forward. The actual
Asia/Taipei zone file and its colocated IANA version **2026b** were loaded.
No API offset/browser/country fallback. Six-hour retrieval age is operational
only; model update/issue/run/native resolutions remain null and source
freshness UNKNOWN. HTTP Date and generationtime_ms are not model update times.

Request point and response grid stay separate. Coordinate validation includes
finite geographic bounds and a conservative additional gross-misbinding guard
of 0.5° per axis; this is **not** a scientific weather threshold, native grid
resolution or validated coastal representativeness. W1/W5 review of this
engineering guard remains requested; it must not be silently expanded to
accept an unexpected provider location.

All output remains RAW_ONLY / UNVALIDATED / NOT_EVALUABLE. No scoring, favorable
verdict, recommendation or Directions. Access notices do not change weather.
No V1 imports, W4 changes, W1/W2 edits, Source Pin updates, workflow/schedule,
permanent service, extra provider or numeric imputation.

## Actual tests

Environment: Python 3.12.14, jsonschema 4.26.0, Linux tzdb 2026b.

| Suite | PASS | FAIL | SKIP | Evidence |
| --- | ---: | ---: | ---: | --- |
| Core: unchanged 42 + new 79 | 121 | 0 | 0 | `core-unittest.log` |
| Existing solar regression | 10 | 0 | 0 | `solar-unittest.log` |
| Total offline tests | **131** | **0** | **0** | fixed implementation HEAD above |
| Existing immutable integration gate | 0 | 1 gate | 0 | `integration.log`, `integration-summary.json` |

The new cases include each field absent/null/zero/wrong-unit, missing unit,
invalid boolean/string/nonfinite/range, absent/short/long arrays, complete vs
partial, empty/duplicate/gapped/reordered/nonhourly/old/future axes, previous
hour at Taipei midnight, wrong sample/grid/timezone/binding/hash, byte tampering,
schema/identity/clock/availability consistency, stale boundary, HTTP failures,
TLS/network/timeout/incomplete read/redirect/429/HTML/encoding/oversize,
wall deadline, ledger corruption/budget, opt-in requirement and offline replay.
Positive outputs are checked against #521's exact W1 schema and W2 binding.
Fixture replay retains TEST_FIXTURE and never calls the provider. Synthetic
all-zero input is labelled in the filename, bytes and fixture README; it is
not real weather. `git diff --check` PASS.

Two targeted checks initially failed: the deep-array test expected INVALID_JSON
but this interpreter decoded it and correctly rejected its non-object shape
as INVALID_SOURCE_OBJECT; an unpaired surrogate in a source-unit string caused
UnicodeEncodeError while writing the normalized archive. The first test now
requires rejection under either parser depth behavior and separately forces
a decoder RecursionError to verify fail-closed handling. JSON escaping fixes
the serialization error (original response bytes remain unchanged). Original
failure traces are in `json-depth-prefixed.log` and
`unit-serialization-prefixed.log`; neither remains in the final regression.
The intermediate full core run also failed that same over-specific diagnostic
expectation (120 passed / 1 failed, zero skips); its complete log is
`intermediate-core-parser-expectation.log`. The final 121-case run above passed.

The integration gate exits **1** before suite execution with
`ValueError: Merged w3 subtree differs from tested pin: packages/core-v2`.
No Source Pin is changed here to suppress this actual integration blocker.
No full-project/Release PASS or downstream integration test count is claimed.

Reproduction (fetch #521's fixed Git object first, as in the core README):

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/chaselights-venv/bin/python -m unittest discover -s packages/core-v2/tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 /workspace/chaselights-venv/bin/python -m unittest discover -s packages/models-v2/tests -p 'test_*.py' -v
```

## Only real HTTPS attempt — UNVERIFIED

Explicit command executed once (not a unit test or scheduled request):

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/chaselights-venv/bin/python packages/core-v2/tools/open_meteo_hourly_pilot.py capture --live --quota-note 'Reviewed V1 scheduled workflow and local pilot history: no previous local pilot captures. V1 runs on separate GitHub runners; combined application/IP quota consumption is not observable here. One noncommercial research request only, no retries; stop on 429 and retain Retry-After. No shared quota availability guarantee.' --ledger /workspace/chase-open-meteo-20261019/capture-ledger.jsonl --output /workspace/chase-open-meteo-20261019/real-capture
```

- Request start: **2026-10-19T13:41:23.374081Z**.
- Attempt completion: **2026-10-19T13:41:23.418756Z**.
- Attempts: **1**, automatic retries: **0**, exit **2**.
- Actual failure: **`URLError: Tunnel connection failed: 403 Forbidden`**.
- This is a proxy CONNECT denial, **not a Provider HTTP 403 response**.
- Provider HTTP status, response grid, received body and raw source SHA256:
  **unavailable/null**. No `response-body.bin` or `artifact.json` exists.
- Provider Acceptance: **UNVERIFIED**. No successful real weather capture or
  real-data replay is claimed. Unit fixtures cannot fill this evidence gap.

See `capture/capture.json`, `capture-command.log` and `capture-ledger.jsonl`.
Postfailure environment status reported restricted networking, policy state
unknown and no Open-Meteo host in the effective-host snapshot. This supports
the diagnosis but does not establish enforced policy; the actual CONNECT
failure is the observed evidence. No proxy/TLS bypass, host fallback,
allowlist change or second request was attempted.

The local ledger reserves failures too, at least three hours apart and at most
eight per rolling day. Shared application/IP usage remains unobservable here;
the quota note is not a claim that other usage or long-term capacity is known.
The request remains within #521's noncommercial research-only scope.

## Actual failed-archive replay

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/chaselights-venv/bin/python packages/core-v2/tools/open_meteo_hourly_pilot.py replay --capture-dir /workspace/chase-open-meteo-20261019/real-capture --output /workspace/chase-open-meteo-20261019/failed-capture-replay.json
```

Exit **2**, network attempts **0**, accepted artifact **null**:
`CAPTURE_NOT_ACCEPTED: URLError: Tunnel connection failed: 403 Forbidden`.
This is correct rejection of a failed archive, not successful Provider replay.
See `failed-capture-replay.json` and `replay-command.log`. The same replay
command can point to the committed evidence `capture/` directory without any
network activity; use a fresh output filename.

## W5 handoff and remaining gates

Review the final W3 SHA/tree and register **79 added cases**, keeping original
42 core + 10 solar regressions. Deliberately accept corresponding #521 W1/W2
sources and update W5 pins/test discovery in separate owned work. Current
immutable pins are not adjusted here to force green CI; CI status is reported
in the Draft PR. Unit PASS is not full Integration/Release or live acceptance.

Before Provider Acceptance, an authorized environment must permit this HTTPS
endpoint and independently run one budget-compliant manual capture plus
original-byte/schema/clock/hash offline replay. No evidence exists yet for
actual provider units, returned grid or complete 72-hour coverage in this
environment. Do not retry this task automatically or infer long-term SLA.

Human W1/W2 binding/translation approval, coastal representativeness,
scientific calibration, model-age knowledge, photography thresholds/AUTO,
result transport, W4 read-only display and W5 release authorization remain
separate. Public index timezone UNKNOWN and navigation are unchanged. No
production forecast, merge or deployment is authorized by this deliverable.
