# W3 NWS 403 investigation — 2026-10-18 UTC

Owner: W3. Target #513 exact HEAD/base
`92804a5c86d14e7855bb92b52d6623bf7fa5c91a`.
Latest main reviewed: `8cadcbed0c62ac128cd537c2a9b256b69662e611`.
Read AGENTS, both R4.2 specifications, V2 index, NWS/solar, readiness,
governance, access and free-composition contracts; inspected #501/#511/#514.
Original runtime, evaluator and adapters are unchanged. This adds a one-shot
diagnostic utility and negative tests, not a replacement forecast runtime.

## Verified now

- One curl GET to official `/points/47.6,-122.33`, 2026-10-18
  **18:49:39–18:49:44 UTC**: curl exit 0, CONNECT **200**, target HTTP **200**,
  `application/geo+json`, 3909 body bytes. Selected response headers, request
  headers and SHA256 are in `transport.json`. The first response-header block
  belongs to the CONNECT route; the second is the target HTTP response.
- Then the **unchanged #513 runtime** made one /points request and one request
  to its returned `/gridpoints/SEW/125,68`. Exit 0; completion
  **2026-10-18T18:50:05Z**. Its normal transport enforces TLS, official URLs,
  no redirects and HTTP 200. Both original bodies are archived losslessly in
  `runtime-live.json` and independently decoded/rehashed in `verification.json`:

| Document | Original bytes | SHA256 |
| --- | ---: | --- |
| /points/47.6,-122.33 | 3909 | `3192fc89d391ec6bfccbc7cd9f46109f3059fbd3eb08c4f371be785f8ed584f2` |
| /gridpoints/SEW/125,68 | 186213 | `16d5e83956645a7e527d96c2ab0424cc6e13d7455f7ff5eb0da5ab5843d5c71d` |

- Source `updateTime=2026-10-18T06:26:47Z` is refresh time, not model issuance.
  At Seattle local sunset on **October 18** (October 19 01:15:15 UTC), the
  raw fields are skyCover 54%, windSpeed 9.26 km/h and precipitation probability
  0%. That last value is a provider field, not a photography probability.
  Valid intervals, timezone corroboration and expiry are retained in the JSON.
  The explicit 24h policy is for this one-shot research capture only.
- The result is `RAW_SOURCE_ONLY` / `HTTPS_TLS`, while evaluation remains
  `UNKNOWN`, all condition states `UNKNOWN`, photography `NOT_EVALUABLE`,
  recommendation false, no score and no Directions. Real raw weather does not
  establish skyline visibility, city-light overlap or calibrated thresholds.
- **70 core tests and 10 model tests PASS**, 0 FAIL/ERROR/SKIP. Four new test
  methods distinguish failure layers and exercise real runtime control flow
  with simulated 403, 429 and CONNECT failure at either of its two requests.
  Six failure combinations make no score, records, recommendation or retries.
  These mocked failures are regression evidence, not new live provider evidence.

Three HTTP requests total were used: one curl diagnostic plus two in the
unchanged runtime. No retry, burst, redirect following, new proxy, proxy
override, network-setting change, alternate host, TLS bypass or credential
change was used. Existing proxy environment presence was recorded as a boolean;
proxy URLs/authentication and cookie headers are not published.

## Attribution: facts, inference and unknowns

| Candidate cause | Evidence and conclusion |
| --- | --- |
| Earlier environment/proxy denial | #513 reports HTTPS CONNECT 403. Its archived header transcript shows 403, `server: envoy`, text/plain, 16-byte length; the runtime reports URLError and no records. This is consistent with a proxy-layer denial. The old archive lacks curl `http_connect`, full phase trace and policy decision ID; exact old policy cannot be independently reconstructed from those headers alone. |
| Current proxy/network exit restriction | CONNECT 200 and real runtime capture prove the current effective route permits these requests at the recorded time. They do not explain why the earlier route failed or guarantee another runner's route. The environment's advertised host list omits api.weather.gov, but that alone cannot prove its effective enforcement given this successful capture. |
| NWS/API/CDN rejection | No such rejection observed in this run. A target HTTP 403 after successful CONNECT is distinct and still requires body/request-ID/operator evidence to distinguish NWS, CDN and an intermediary. `Server` alone is insufficient. |
| User-Agent / Accept | Both are already present in `_get_json_bytes`: `ChaseLights-V2-M6b/0.1 (source research; https://github.com/gdrabbit137-ai/ChaseLights)` and `application/geo+json, application/json`. Same values succeed here. Missing UA is not demonstrated as this incident's cause. No deliberate missing-UA A/B traffic was sent. |
| Rate limit | Not observed: no 429 or Retry-After in the diagnostic response, no load test or retry loop. A generic 403 does not establish throttling; absence of Retry-After does not exclude it historically. Shared-egress quota history remains unknown. |

Official references read on October 18:
[NWS API documentation](https://www.weather.gov/documentation/services-web-api)
requires an identifying User-Agent and documents unpublished rate limits;
[NWS FAQ](https://github.com/weather-gov/api/blob/master/general-faqs.md)
suggests checking User-Agent for API 403. Neither explains this historical
managed-proxy decision. No invented quota or email contact was added.

The supported inference is an earlier environment-specific transport restriction,
not an established Runtime defect. Its exact policy, duration, old egress and
whether the earlier process had identical effective networking remain unknown.
Successful current transport does not retroactively erase #513's failed capture.

## Reproduce in the intended execution environment

Run once on an operator-approved host/runner with normal authorized outbound
HTTPS to `api.weather.gov:443`, Python with jsonschema, curl and a correct UTC
clock. Keep the existing network policy/route; if blocked, ask that environment's
administrator for official-host access instead of bypassing it. Pin this task
commit and record host/runner identity, exact commit and UTC time alongside the
artifacts. Do not use this as a recurring or mandatory network CI test.

1. From the repository root, create an output directory outside public/catalog
   paths. Run `python packages/core-v2/nws_transport_probe.py > transport.json`.
   Exit 0 certifies only one transport request, not weather/scoring readiness.
   Exit 1 distinguishes CONNECT denial, target HTTP 403/429, incomplete transfer
   or unresolved connection/TLS failure. Inspect response layers and UTC stamps.
   Stop on denial; do not automatically retry or change UA/IP/proxy to evade it.
2. If transport works, create `probe-policy.json` containing
   `{"approved":true,"source":"One-shot research probe only, not production approval","max_age_seconds":86400}`.
   Choose an upcoming Seattle local date/event, then run the **existing** CLI:

   ```bash
   python packages/core-v2/forecast_runtime.py --local-date YYYY-MM-DD --freshness-policy probe-policy.json > runtime-live.json
   ```

   Exit 0 means raw fields only; 1 means UNKNOWN; 2 means invalid input.
   Preserve failures unchanged. Never replace data with a fixture or raise a
   freshness limit to force success. Replays remain TEST_FIXTURE.
3. Independently decode `weather.documents[*].body_base64`, compute SHA256 and
   compare with each stored hash. Verify actual /points→grid mapping, raw grid
   identity, units, timezone, update/retrieval times, exact event coverage and
   `NOT_EVALUABLE`/false recommendation/no score. Preserve both bodies and policy.
4. On an origin-level 403/429, retain safe response headers, problem body hash,
   Date, request/correlation IDs and runner identity for the network/NWS operator.
   Redact cookies and credentials. Respect Retry-After; no burst diagnosis.

This managed-environment capture is complete. Validation on the **intended
production/deployment executor**, long-term availability, redistribution review,
scientific admission and new current-head W5/CI acceptance remain **NOT DONE**.
Prior #514 CI is not this task's CI. #513's old failing pin check is a separate
integration issue and must not be described as a provider failure.

## W5 handoff

Keep a distinct Draft PR stacked on #513; do not alter #513's branch, #514,
source pins, test minima or workflows here. Integrating this task changes the
whole core tree and adds four core test methods (66→70); W5 must accept its
exact tree and separately retain #514's latest-main Canonical fixture repin.
Do not blindly merge a stacked branch or claim #514's 353 tests apply here.
No merge, deployment, public UI/data publication or scientific approval occurs.

`verification.json` records code hashes and local counts; `sha256.json` covers
the evidence files. Runtime executable source is #513's implementation commit
`9821b5234c1fec127c7a19b4c4e5ea7f25c93f85`; no runtime source edit was needed.
