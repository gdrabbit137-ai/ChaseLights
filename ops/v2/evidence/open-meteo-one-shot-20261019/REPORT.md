# Open-Meteo × 七星潭 one-shot provider acceptance

**Disposition: VERIFIED_ONE_SHOT (technical provider capture and offline replay only).**
No photography scoring, recommendation, navigation, W4 hourly display, merge, or deployment is authorized by this result. Forecast data in this directory are a dated research snapshot, not current weather for site users.

## Provenance and environment

- Owner: W5 evidence, stacked Draft PR #524 on #523 (`2cb08673e987ca4d930b2227de1d7447de563132`). The one-shot workflow execution used commit `7ae2802047e2f6b445dbe00731749e0ccd13df64`. W1/W2 #521 was `74f21b365d366b0d1d12efbc23cf6cce484b6b5e`; W3 #522 was `c8bafcf88da996f0c3a4b4deed488bf5e5f855f8`. Reviewed main was `586192ae7c6a729432d86f67d737a83a1cb2f50c`.
- [Actual GitHub Actions run 39283623067](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/39283623067) on GitHub-hosted `ubuntu-24.04`, Azure `canadaeast`, Python 3.12.15; job `capture` PASS. The [original nine-file artifact 12202959410](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/39283623067/artifacts/12202959410) has ZIP SHA256 `bc81b9423c7e7d96c9cdfc9a0c000bfb5e74707c1f0c1b39230cadd259701081` and 30-day retention through 2026-11-18. This directory preserves the original raw response and losslessly compressed receipt, normalized result, and replay beyond that retention.
- The first workflow commit `2630c82968e7843517801f9bbd234d938524c21a` produced [run 39283369672](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/39283369672), which failed workflow validation before job creation; **zero HTTP attempts**. The corrected workflow ran once. GitHub reported degraded Actions/Pages/Webhooks processing during its queue delay; this was not an Open-Meteo error.
- Execution is personal/public **noncommercial research** using the free API. Source: [Open-Meteo](https://open-meteo.com/); raw API data licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The adapter normalized timestamps, availability, and previous-hour intervals without interpolation or photography scoring. Shared V1/application/IP use cannot be observed completely; the job made one bounded request with no retry and reserved it in the ledger. No security proxy, TLS validation, or provider endpoint was bypassed or weakened.

## Network and identity

| Field | Observed value |
| --- | --- |
| Previous failed V2 attempt | 2026-10-19T13:41:23.374081Z, local proxy CONNECT 403, no provider response |
| This request start | 2026-10-19T16:43:00.171395Z; **3 h 1 m 36.797 s** after previous reservation |
| HTTPS completion | 2026-10-19T16:43:00.776727Z |
| HTTP | 200; `application/json; charset=utf-8`; Date `Mon, 19 Oct 2026 16:43:00 GMT`; identity body complete, no redirect |
| Endpoint and request | `https://api.open-meteo.com/v1/forecast`; latitude 24.031426, longitude 121.62717, `forecast_hours=72`, `past_hours=0`, `timezone=GMT`, `timeformat=unixtime`, `cell_selection=land`, exactly the ten fields in the pinned W1/W2 contract. Exact URL in the original receipt. |
| Returned grid | latitude 24.007029, longitude 121.59067, elevation 14.0 m; **distinct from requested Place sample**; coastal representativeness UNVALIDATED |
| Original HTTP body | 4,468 bytes, [response-body.bin](response-body.bin), SHA256 `e441ea1bad2d42cfd89169bb030d7aec518d798c56aafe61e037f8a0e9406b1f` |
| Attempts | one real HTTPS attempt, zero automatic retries; both capture and offline replay exit 0 |

## Replay and data integrity

- Original `capture.json` and `artifact.json` are losslessly archived as `capture-capture.json.gz` and `capture-artifact.json.gz` (uncompressed SHA256 `a98c7c975bd18b2440be40c7f3bdb7f703dc297697522c863e6deed512b77bf2` and `5da077c5d63b8450dab413dff62ef03ec0056df22f5c0d4449e38f634d29ceb0`). The original zero-network `replay.json.gz` decompresses to SHA256 `b60deea0369f62a05e33bfdd839131d6192d01720c9838ce2633bd4ce8972584`.
- GitHub-run replay: network attempts **0**, `COMPLETE`; all source-derived normalized fields matched capture (the later `checked_at_utc` naturally differs). Independently downloaded the artifact, verified its ZIP and raw SHA256, and replayed the committed raw archive locally with the existing W3 tool: **PASS**, network attempts **0**, 72 rows × 10 AVAILABLE cells, no missing cells. The separate local machine has tzdb `2025b` versus the GitHub capture/replay's installed tzdb `2026c`; source rows/units/grid are identical. `Asia/Taipei` maps the first row `2026-10-19T16:00:00Z` to `2026-10-20 00:00+08:00` and the last `2026-10-22T15:00:00Z` to `2026-10-22 23:00+08:00`, with contiguous one-hour steps. Exactly 24 rows select for local date 2026-10-20.
- Actual source units: temperature/dew point `°C`, RH/three cloud layers/PoP `%`, 10 m wind `m/s`, visibility `m`, precipitation `mm`, and axis `unixtime`. Every cell is present and has the original source unit. Actual zeros remain AVAILABLE, including 64 precipitation zeros, 24 PoP zeros, 19 high-cloud zeros, 17 mid-cloud zeros, one low-cloud zero and one wind-speed zero. Missing/null cells: **0** in this response; the existing negative tests retain their separate missing-versus-zero checks. No 72-hour padding occurred.
- Eight fields are instantaneous at T. Precipitation and PoP represent `(T−1h,T]`; independent replay checked every row's preceding-hour endpoints and matched every normalized numeric value to the original JSON. The adapter and W1 schema enforce `RAW_ONLY`, `UNVALIDATED`, `NOT_EVALUABLE`, `recommendation_eligible=false`. Model issue/run, model IDs, native resolution and actual model freshness remain **UNKNOWN/null**. HTTP Date and retrieval time are not model update time.

To replay with this directory and the exact W1/W2 Git objects available in the repository checkout:

```sh
mkdir -p /tmp/chase-open-meteo-replay/capture
gzip -dc ops/v2/evidence/open-meteo-one-shot-20261019/capture-capture.json.gz > /tmp/chase-open-meteo-replay/capture/capture.json
cp ops/v2/evidence/open-meteo-one-shot-20261019/response-body.bin /tmp/chase-open-meteo-replay/capture/response-body.bin
python packages/core-v2/tools/open_meteo_hourly_pilot.py replay --capture-dir /tmp/chase-open-meteo-replay/capture --output /tmp/chase-open-meteo-replay/replay.json
```

The original #523 proposed merge passed **444 tests** on [Integration 39271513313](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/39271513313). This evidence branch adds only the one-shot workflow and archival evidence; it does not claim a new 444-test run. Provider Acceptance here is a single technical capture, not a guarantee of future uptime or coastal accuracy. W1/W2 human Binding/semantic review, W4 trilingual read-only presentation, current-data transport and W5 main-based release checks/authorization remain separate gates. Keep both PRs Draft; do not merge or deploy as a consequence of this capture.
