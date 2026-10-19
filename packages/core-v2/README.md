# Worker 3 V2 deterministic evaluator

This directory is owned by Worker 3. The implementation consumes the Worker 1 draft V2.1 Condition Contract without altering the canonical schema or legacy runtime.

Draft research records and missing/unsupported data must never produce live FAVORABLE recommendations. REQUIRED, BLOCKER and QUALITY are independent of AUTO, GUIDANCE and VERIFY. See evaluator.py and tests.

Access/closure notices are **non-scoring advisories**. The evaluator defensively quarantines legacy `ACCESS_SAFETY` conditions and exposes `access_advisories` separately. A restricted viewpoint must not change the photography/weather verdict; verified Directions remain a separate navigation concern. Only test-only values are accepted by this evaluator.

## Open-Meteo hourly RAW_ONLY pilot

`adapters/open_meteo_hourly.py` implements only Open-Meteo Forecast API ×
Qixingtan `tw-036` × 72 hourly rows × ten W1 fields. It never calls the evaluator,
scores a photograph or supplies Directions. All artifacts remain RAW_ONLY /
UNVALIDATED / NOT_EVALUABLE, with source/model freshness UNKNOWN. The W2
sample `(24.031426, 121.62717)` is a representative weather sample, not a camera
or navigation point. Canonical and the public Place index are unchanged.

This independent W3 branch starts at main
`39c6d9fa4828acabf9976d505778f527f39c775e`. It reads W1/W2 #521's exact
`74f21b365d366b0d1d12efbc23cf6cce484b6b5e` schema/binding Git objects and
checks their SHA256. Fetch that dependency in a full clone before testing:

```sh
git fetch origin refs/heads/codex/w1-w2-hourly-pilot-gate-20261019
git cat-file -e 74f21b365d366b0d1d12efbc23cf6cce484b6b5e
python -m unittest discover -s packages/core-v2/tests -p 'test_*.py' -v
python -m unittest discover -s packages/models-v2/tests -p 'test_*.py' -v
```

The fixed Git objects are deliberate external draft dependencies, not an
assumption that #521 merged. No W1/W2 files or their old schemas are copied or
edited. W3 #520 `a649ace57cda5ca02edc1481660ef2f567eb86f1` is the prior
research input; #517 NWS is not a dependency. Missing/changed inputs fail with
an explicit pin error. Tests need `jsonschema` and Linux system IANA tzdb;
the actual zone file and colocated tzdb version are loaded without UTC fallback.

Eight fields are instantaneous at T. Precipitation and its probability apply
to `(T−1h,T]`, attributed to the Place-local date of T even across midnight.
`select_local_date` selects existing rows only; it does not interpolate or
prorate. A response has to start in the actual request/retrieval UTC hour and
contain a strictly contiguous hourly axis. A short horizon or missing/invalid
cells stays PARTIAL; missing never means zero. Wrong units are not converted.
More than six hours of retrieval age yields STALE; this is not model age.
Offline replay recomputes that age at the new check time. Consumers must not
reuse a saved availability label without rechecking age.

Returned grid coordinates/elevation remain separate from the request point.
The adapter checks finite geographic bounds and conservatively rejects a grid
more than **0.5° in either axis** from this one pilot's sample. This additional
engineering admission guard detects gross request/response misbinding; it is
not provider resolution, a validated coastal representation, distance accuracy
or a scientific photographic threshold. W1/W5 should review this guard; if a
future legitimate provider grid falls outside it, stop for review rather than
silently extending it. Native model IDs, resolution and update/issue times
remain null; `generationtime_ms` and HTTP Date do not supply those facts.

The manual tool is separate from unit discovery. It requires explicit live
opt-in, a shared-quota review note, a local ledger and a new archive directory:

```sh
python packages/core-v2/tools/open_meteo_hourly_pilot.py capture --live --quota-note 'Record the actual local/shared quota review and unknowns here' --ledger /tmp/open-meteo-pilot-ledger.jsonl --output /tmp/open-meteo-pilot-capture
python packages/core-v2/tools/open_meteo_hourly_pilot.py replay --capture-dir /tmp/open-meteo-pilot-capture --output /tmp/open-meteo-pilot-replay.json
```

Do not run the capture command as a test or schedule it. The free endpoint is
admitted only for the noncommercial research scope documented in #521; stop
before commercial use. Keep the same ledger across manual captures. It locks
and reserves one attempt, enforces at least three hours between captures and
at most eight in a rolling day. It cannot measure other applications' shared
IP quotas; record that uncertainty rather than claiming entitlement/capacity.
There is one HTTP attempt, no retry/fallback, including 429 (Retry-After is
retained). TLS verification and inherited proxy/CA trust remain enabled;
redirects are forbidden. A 20-second wall deadline and 3 MiB identity-encoded
body limit apply. Unexpected compression is rejected, not decompressed without
a bound. HTTP/HTML/network failures retain diagnostics without a new artifact.

`response-body.bin` preserves the received bytes before decoding, including
error bodies when available. The receipt records completion time, SHA256,
status, request, grid through the artifact and normalization time. A truncated
oversized body is explicitly incomplete and never accepted as source JSON.
`artifact.json` exists only after validation. Replay checks byte/hash/request
identity and the same schema; it performs zero network attempts and never
claims a second capture. TEST_FIXTURE archives retain TEST_FIXTURE. Archive
consistency is not a signed provider attestation; W5 must review capture logs.

W5 must separately accept the final W3 tree and register the added tests,
alongside #521 W1/W2 pins, before full integration/release. This task does not
edit those Source Pins or authorize W4 publication. Human binding/translation
review, coastal representativeness and every photography/scientific gate remain
pending. Capture/replay results are recorded under `tests/evidence/` when run;
synthetic fixtures are explicitly separate and never provider acceptance.
