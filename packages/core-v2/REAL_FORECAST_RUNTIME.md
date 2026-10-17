# W3 real forecast runtime diagnostic — #467 / #506

Owner: W3. Base reviewed: `cf38747d9b04958ea0bbdd784d90708553ea1f4e`.
Read main AGENTS.md, R4.2 research/navigation, V2 architecture/governance,
readiness, free composition/access, solar, NWS, and date-query contracts.
W3 owner source `8e6f5a1555294ff293a6d7b746b864924f96cfc1` is already on main.
Pending W3 #501 (`725291e…`) and #511 (`21c9ff9…`) change the original
single-field adapter/tests; this task leaves those files untouched. W2 #493/#495,
W1 #496 and W5 #499/#500/#482 were inspected; no cross-owner data is changed.

## Implemented path

Real W2 `us-071-P01` Canonical bytes → existing regional solar WINDOW → exact
UTC sunrise/sunset instant → one official NWS /points lookup and one raw
/gridpoints request for all fields → existing W1 source records → existing W3
Evaluator's raw-context bridge → per-condition UNKNOWN with explicit sources.

Kerry Park dusk is the first **technical pilot**, because main already has a
W1 NWS source contract, a US regional probe and W2 subject evidence. It is not
scientifically admitted for scoring. `seattle_skyline_visibility` is not measured
by `skyCover`; `dusk_city_lights_overlap` is not proved by an ideal-horizon solar
crossing. No substitute metric, threshold, favorable verdict or probability is
introduced. REQUIRED/BLOCKER/GUIDANCE rules remain in the existing evaluator.

The artifact is `RESEARCH_RUNTIME_DIAGNOSTIC`, **not** W1 EvaluationResult,
public DateQuery READY, a new shared schema, or a public forecast. It always has
`research_only=true`, `photography_verdict=NOT_EVALUABLE`,
`recommendation_eligible=false`, and no score or Directions. Even caller-supplied
approved Canonical flags cannot turn raw data into a condition PASS.

## Provenance and time

- Exact Canonical bytes SHA256, revision, stable condition/claim IDs, canonical
  contract content hash and solar result hash are recorded. Current pilot
  Canonical SHA256: `7546ab2c1cad9a1e3c0b5d7a7e8604eda7743cc8f24618510df9ea204ce75e8d`.
- Both original HTTP bodies are stored losslessly as base64 with URL and SHA256;
  raw-grid hashes can therefore be independently recomputed, unlike the older
  #482 artifact. NWS records reference the matching raw body and mapping.
- Forecast, missing observation and deterministic astronomy are distinct. No
  satellite observation, fog probability, or cloud-color outcome is inferred.
- Source `updateTime` remains refresh time, **never model issuance**. Model ID,
  version, run, issuance, physical cell resolution and model forecast horizon are
  unknown/null. Approximate documented NWS grid size is not a per-cell survey.
- One real UTC completion clock supplies all fields. Live callers cannot inject
  an opener or `retrieved_at`. Host-pinned HTTPS, no redirects, bounded responses,
  timeout, duplicate JSON rejection, source-body grid identity and coordinate
  mapping are checked. Grid data must corroborate /points; URL text alone fails.
- Caller supplies an explicit approved/source/max_age_seconds operational age
  policy (bounded by the existing parser at 48h); there is no production default
  or scientific approval implied by a dictionary flag. Every replay rechecks
  `as_of - updateTime`, retrieval order, and exact half-open `[start,end)` coverage.
  `expires_at_utc` is the operational age cutoff (inclusive at the cutoff, stale
  immediately after), not model issuance or a promise of photographic validity.
  Past events cannot be served as a current forecast. No hourly rounding or
  interpolation fills a missing interval; unknown fields stay null individually.
- Date and event conversion use the existing IANA/zoneinfo model, including DST
  and UTC dates differing from local dates. The sample is the existing Seattle
  research sample (47.6, −122.33), **not Kerry Park camera/subject/arrival GPS**.
  `America/Los_Angeles` is the existing Seattle numerical benchmark assumption;
  NWS /points `properties.timeZone` must corroborate it before weather is accepted.
  The W2 Place index still has UNKNOWN timezone: this diagnostic does not promote
  it or authorize a public Place date query. Altitude, viewpoint horizon and
  spatial uncertainty are unknown; skyline/terrain claims remain unevaluable.
- Replays verify hashes but always produce `TEST_FIXTURE`. An archive, even with
  official-looking URLs, does not authenticate who originally retrieved it.
  Tests mocking default HTTPS control flow are not live-source evidence.
- Access notices are copied separately in zh-TW/en/ja, do not affect solar,
  weather, evaluation or score, and never enable navigation. New diagnostic
  caveats have all three locales; formal human semantic review remains pending.

## Provider inventory (repository inspection, not a new live-source certification)

| Interface on reviewed main | Actual data and limits | W3 disposition |
| --- | --- | --- |
| WeatherGrid `weathergrid/v2/index.json`, cache/tile modules | Generated multi-provider browser cache; tile pixel/remap size is not native resolution. Providers, frames, field semantics and original provenance require individual review. | Do not use a map layer or stale cached value as a photographic observation. No WeatherGrid publishing changes. |
| CWA `cwa_wrf3_poc.py`, `cwa_weathergrid_derived.py` | Unsigned `s3://cwaopendata` MIC/Model `M-A0064-xxx` GRIB2; legacy CWA HTTPS file endpoint. WRF 3km regional model; actual public series 0–84h every 6h, despite model capability 126h/hourly. Browser remap is 0.03°. RH-derived low/mid/high cloud/fog proxies are unvalidated derived fields, not native cloud-cover/fog probability. | No approved V2 W1 record/binding here. Preserve native coverage, altitude and proxy flags; review CWA terms/attribution before redistribution. No Taiwan sunset pass from RH. |
| JMA `jma_msm_aws_om.py`, `jma_msm_cloud_poc.py` | Open-Meteo unsigned AWS OM transport, `https://openmeteo.s3.amazonaws.com/data_spatial/jma_msm/latest.json`; model is JMA MSM. Native 0.05° lat × 0.0625° lon (~5km), domain 120–150E, 22.4–47.6N; hourly fields, 3h cycles, 39h standard / 78h at 00/12Z per repository. Cloud-layer definitions are model specific. Taiwan subset does not cover the entire island chain. | Strong next regional candidate; need W1 versioned source contract, exact original-byte provenance and both model/transport license review. Do not call AWS transport the weather model or assume global coverage. |
| GFS `gfs_raw_poc.py`, `gfs_multilayer_poc.py` | NOAA/NCEP NOMADS `filter_gfs_0p25.pl`; global regular 0.25° (~27.8km), run/lead metadata; current resolver samples 3h through 384h. | Existing non-V2 ingestion is not an approved V2 condition source. Need field/unit/run/freshness/license binding; no imports from Legacy runtime. |
| ICON `icon_global_cloud_poc.py`, `weathergrid_model_resolver.py` | DWD `https://opendata.dwd.de/weather/nwp/icon/grib`; native icosahedral ~13km, cycles 00/06/12/18Z; 180h at 00/12 and 120h at 06/18, hourly through 78h then 3h in resolver. Remapping does not improve meteorological resolution. | Review DWD attribution/redistribution, native field definitions and W1 source contract. Never silently merge model disagreements or label interpolated cells as finer native forecasts. |
| NWS `adapters/nws_gridpoint.py`, new `nws_snapshot.py` | Official NOAA/NWS raw grid forecasts (not direct GFS). Original /points mapping and /gridpoints bytes, original units and merged validTime intervals. US only; no Taiwan/Japan fallback. Model issuance/run not supplied. | Selected first diagnostic adapter. Official API docs: https://www.weather.gov/documentation/services-web-api ; data semantics: https://github.com/weather-gov/api/blob/master/gridpoints.md ; terms reference https://www.weather.gov/disclaimer . Public redistribution/attribution review remains required; no new license certification. |
| Himawari-9 existing WeatherGrid product | Satellite observation, separate from forecast; image/cloud products do not establish future outcome. | No relabeling as NWS forecast or calibrated photo probability. |

## Run and verify

Python requires `jsonschema`; all other new runtime dependencies are stdlib.
Create an operator-reviewed policy JSON with `approved`, `source` and
`max_age_seconds`. A one-shot 24h research policy like #482 is only a probe,
not a production freshness approval. Then run from the repository root:

```bash
python packages/core-v2/forecast_runtime.py --local-date YYYY-MM-DD \
  --freshness-policy work/w3-runtime/probe-policy.json > work/w3-runtime/live.json
python ops/v2/run_unittest.py packages/core-v2/tests 'test_*.py' work/w3-runtime/core-results.json
python ops/v2/run_unittest.py packages/models-v2/tests 'test_*.py' work/w3-runtime/model-results.json
```

CLI status 0 means raw fields available (still NOT_EVALUABLE); 1 means source
UNKNOWN; 2 means invalid arguments/input. No fixtures are available on the CLI.
Persist the JSON artifact outside Canonical/public publication directories.
Replay via `adapters.nws_snapshot.replay_nws_snapshot()` with an explicit
`as_of`, requested instant and policy. Replays can never certify live transport.

This execution's real runtime attempt returned `PROVIDER_TRANSPORT_UNAVAILABLE`
(URLError), no records or archived weather bodies. An independent curl attempt
confirmed HTTPS CONNECT denied with HTTP 403 by the environment proxy;
`api.weather.gov` is absent from its restricted host list. **No successful live
NOAA retrieval is claimed.** This is a configured network-policy blocker, not
an auto-review rejection. Enable official NOAA host access in the managed
environment, then rerun the one-shot command and independently hash both bodies.
No fixture fallback, production merge or deployment is appropriate.

## W5 acceptance and next topic

Local checks: W3 **66 PASS** (42 existing + 24 new), models **10 PASS**, W1
**67 PASS**, W2 **33 PASS**, W5 tooling **40 PASS**, Node **49 PASS**; no skips.
W2 initially errored without `CHASELIGHTS_W1_SPEC_ROOT`; configuring it to the
real checked-out `specs/v2` passed the pinned dependencies, without edits.
All 8 real Canonical records and Task W fixtures validate. Public HTTP isolation
smoke is environment-blocked; browser/public/real-source success is not claimed.

W5 must review this exact head, deliberately rotate W3 source pins, retain every
existing test and increase its 42-case W3 count to 66 and total 329 to **353**
for this change alone. If #501/#511 are also integrated their distinct tests
raise the count separately. Existing strict CI will reject the unrotated W3
tree; do not weaken it or change W5 files in this task. Re-run actual current-head
CI and all required release/browser/public checks before any separate release.

Next technically openable capability: regional **sunrise/sunset WINDOW**, after
verified sample/timezone provenance and W5 acceptance, with real horizon/visible
Sun/photographic conditions explicitly unknown. Taiwan candidate: Jingzaijiao
sunset `tw-026-P01`, using a reviewed representative sample and JMA MSM **only
inside its actual domain and native event-time coverage**. First deliver a W1
source contract and live capture; CWA 6h RH proxies cannot replace native hourly
cloud evidence. Neither pilot is ready for a formal photography score. Kerry
Park additionally needs real skyline visibility and light-overlap evidence;
Jingzaijiao needs opportunity-specific scientifically reviewed conditions and
threshold/model binding. W2 owns these approvals; camera/access uncertainty is
an independent warning, not a reason to invent GPS or block general research.
