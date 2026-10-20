# W3 — V1 forecast inheritance audit / bounded V2 pilot

Date: 2026-10-19 (Asia/Taipei)  
Owner: W3 (`packages/core-v2/`, `packages/models-v2/`)  
Base main: `67e8a14e9ccbfd0eef7ca96c09b4c872a3d519d2`  
Disposition: **research-only scoping and handoff; no live forecast release or model change**.

## Objective and scope

Continue the user's approved “reuse successful V1 weather functions before inventing a new V2 forecasting system” direction. Inventory the existing V1 weather pipeline and identify the smallest scientifically defensible steps toward weather **information** in V2, independently from Opportunity scoring.

This audit only adds this W3-owned review document. It does **not** import Legacy modules, modify `fetch_data.py`/`opportunity_runtime.py`, change any W1/W2/W4/W5-owned path, repin sources, alter schemas, create weather API calls, claim live provider operation, run production forecasting, introduce new AUTO conditions, or merge/deploy. V1 remains in production and V2 stays Research-only.

The baseline V2 public version is the merged #519 “What can you photograph here?” guide (7 Places, 8 Opportunities). W5 #517 contains a separate **US-only**, Seattle regional NWS research runtime and was an open Draft when inspected; do not copy, merge, or depend on its unpublished NWS runtime in this task. Check its current status before implementing anything.

## Evidence verified from the exact main tree

| Source file | Existing, verified behavior | What may be reused |
| --- | --- | --- |
| `fetch_data.py` (`_build_open_meteo_url`, lines ~1674–1691) | Legacy queries Open-Meteo `/v1/forecast` for 24 h history and 72 h forecast, including temperature, dew point, RH, low/mid/high cloud cover, wind, visibility, precipitation, precipitation probability, DNI, sunrise and sunset. Uses `timezone=auto` and epoch time. | **Field inventory and behavior reference**. V2 must independently implement/normalize a source with W1-approved terms, issue/valid/retrieval times and location provenance. Not a drop-in import. |
| `fetch_data.py` (`fetch_weather_for_spot`, lines ~1821–2172) | Legacy builds time-indexed weather rows, theme and Opportunity results, including weather/astronomy, spatial and marine extras. `hv(name,i,default=0)` supplies zero for some missing values while separate `*_available` flags exist for selected fields. The timezone may fall back to UTC or a provider offset if parsing fails. | Retain useful weather **fields** and clearly separated user semantics, **not** zero-on-missing behavior or unverified zone fallback. Missing field = null/UNKNOWN; no implied 0% cloud or 0 mm rain. |
| `analyze_weather.py` (`_window_for_metric`, lines ~32–58; `main`, ~442) | Legacy computes selected-date best windows using Opportunity/theme scores; derived window threshold uses `max(55, best_score-4)`. | UX reference for best-time presentation only. **Do not transfer** thresholds, scores, ranking or selected-date favorable claims without independent W1/W2/W3 review and real inputs. |
| `.github/workflows/update_weather.yml` | Legacy runs `analyze_weather.py` for Taiwan, Japan and US every 3 hours, publishes summary/detail JSON. | Reference for batch/cache operations. Existing Legacy JSON is **not** a V2 live source nor a guaranteed provider-issued dataset; do not import it into V2. |
| `opportunity_runtime.py` | Legacy contains subject-specific diagnostics: water-surface low wind, mountain visibility, solar directional sector, DNI, cloud/sky glow, terrain/cloud sampling, astronomy, marine/tide and aurora. | Reuse *idea and test cases* per rule; never import the module or reuse its per-subject thresholds as already certified V2 AUTO. |
| `spatial_weather.py` | Legacy spatial cloud-sea proxy samples camera area plus surrounding lower-terrain samples rather than inferring a sea of clouds from one RH value. | Reference for difficult phenomenon research only, not first pilot. Distinguish environmental proxy from verified subject/visible composition. |
| `field_snapshot.py`, `B106_FORECAST_REVISION_COMPARISON.md`, `B89_FIELD_VALIDATION_REPLAY.md` | Legacy supports immutable forecast-revision comparison and replay; some regression fixtures are expressly synthetic, not archived original observations. | Adopt provenance/replay discipline; never relabel synthetic fixtures as real source/photographs. |
| `packages/models-v2/solar_window.py` | Existing V2 deterministic solar WINDOW computes regional ideal-horizon crossing; it is not a photographic favorable verdict. | Reuse the **already existing** V2 model when selected Place location and zone requirements are met. Do not rewrite it. |
| `packages/core-v2/evaluator.py`, `packages/core-v2/adapters/nws_gridpoint.py` | Existing V2 evaluator is test-only, requires explicit provenance, fail-closes on missing/unsafe conditions; NOAA/NWS adapter returns RAW_ONLY/NOT_EVALUABLE, no live score. | Preserve these boundaries; extend only through approved contracts and source-specific adapters. |
| `specs/v2/DATE_QUERY_CONTRACT_V0_1.md`, `specs/v2/ARCHITECTURE_SPEC.md` | Selected Place local date, approved timezone, provider validity/source fields, independent V1/V2 boundaries and no unreviewed scores are required. | W1 owns any missing additive source/result/transport schema; W2 owns Place-specific timezone/coordinate evidence. |
| `B175_CWA_LOW_CLOUD_CALIBRATION.md`, `B170A_PHOTOGRAPHY_TRANSPARENCY.md` | Low-cloud RH proxy's first calibration had poor clear-sky specificity; photo transparency diagnostics remain uncalibrated. | These are explicitly **not** ready to become V2 favorable rules. |

All file and line references above are from inspected source on the listed base main. Line numbers are review aids, not immutable API identifiers.

## Inheritance matrix: implement in small independent phases

| Priority | V1 capability | V2 proposed bounded deliverable | Feasibility / admission |
| --- | --- | --- | --- |
| P0-A | Raw 72-hour hourly meteorology | **One source-backed, one-location Research-only hourly weather diagnostic** with low/mid/high cloud, wind, precipitation/PoP and visibility, per-field null/UNKNOWN and valid times. It carries original provider, unit, retrieval and update provenance and explicit coverage. **No photography score**. | **High engineering feasibility**, conditional on W1 provider/terms admission, W2 verified/clearly labeled representative sample and time-zone rules, plus real provider capture. Source selection not preapproved. |
| P0-B | Sunrise / sunset dates | Use existing V2 `solar_window.py` to supply *regional approximate* event WINDOW when evidence allows. Avoid claiming visible sun over local ridge. | **High technical feasibility**; site-specific verified IANA zone and location are gates for dated Place output. |
| P1-A | Reflection low-wind diagnostic | Show source-backed wind/precipitation as separate conditions; only later propose V1-like low-wind threshold for a particular lake and classify `PASS/FAIL/UNKNOWN` after documented evidence. | **Moderate**; wind-speed units easy, photography threshold/water-surface representativeness still unapproved. A `PASS` means only “low wind condition met”, not a guaranteed reflection. |
| P1-B | Mountain visibility | Show genuine weather visibility measurements when available; later propose per-subject minimum-distance/readability conditions. | **Moderate**; one-point forecast visibility ≠ clear mountain ridge or unobstructed specific view. |
| P2 | Low clouds, valley fog, cloud sea, sunset sky glow | Retain V1 source-backed shooting guidance and stage field observations; calibrate proxies independently before deterministic AUTO. | **Research-heavy**, cannot block first weather table or guide publication. |
| Deferred | Global 0–100 score, cross-provider composite and all subjects | No combined score, FAVORABLE, probability or ranking in initial migration. | Requires W1 decision contract, calibrated V1/V2 rule evidence, W3 evaluation, W4 result-store transport and W5 release review; not part of first increment. |

## Critical implementation traps — prevent accidental V1 regressions

1. **No direct Legacy dependency.** V2 code may refer to V1 in documentation/tests for compatibility learning, but must never import `fetch_data`, `opportunity_runtime`, `analyze_weather` or Legacy produced `*_weather.json` as a runtime input.
2. **No “missing means clear”.** Legacy `hv(..., default=0)` behavior is documented but must not be adopted by V2. Missing clouds, wind, precipitation, visibility, stale data, invalid units or unsupported forecast valid time must be explicitly unavailable/UNKNOWN.
3. **Weather-only vs photography.** Raw clouds and winds do not establish sunset color, fog, cloud sea, camera horizon, lake reflection, skyline visibility or suitable photography conditions.
4. **No provider/clock laundering.** The provider's source update time, model-issued time, retrieval time, native interval valid time and selected local-day date are different facts. `timezone=auto` in a response does not independently verify the W2 Place timezone.
5. **Provider scope/terms.** The V1 Open-Meteo client does not itself establish V2 redistribution, API commercial entitlement, rate capacity, quality guarantees or source-licensing approval. W1/W5 must review provider usage and alternatives, including existing WeatherGrid sources (JMA/CWA) only when coverage, provenance and units are individually verified. Himawari-9 cloud observation is not future cloud forecast; CWA RH-derived “low-cloud potential” is not native low-cloud cover.
6. **Source geometry.** A weather sampling coordinate can be representative; it must be labeled accordingly. Do not turn it into Camera GPS, photo Subject, lawful arrival point or Directions.
7. **Access advisory.** Closure and lawful-access guidance remains non-scoring and can warn independently of weather conditions. Preserve zh-TW/en/ja equivalence.
8. **V1 existing score caveat.** V1 Issue #509 and Draft PR #510 document misleading “suitable” wording at middling scores. Preserve useful diagnostic logic as research candidates, not the verdict/score string.

## Precise first engineering work order (following this audit)

**Owner W1 — one small specification/admission review (no overhaul).** Decide the first permitted V2 weather source for a single candidate region, review provider API and redistribution terms, record required original-field/unit/interval/issue/freshness/coverage representation, and clarify an *informational, not scored* weather-result envelope. Reuse existing strict source schema where compatible; only additive changes if actually needed. Do not make the full EvaluationResult a prerequisite to raw weather *display*.

**Owner W2 — one Place evidence check.** Choose a currently published V2 Place/Opportunity with defensible weather sampling context, separately documented Place timezone and sampled coordinate role. Existing source data must be checked before naming or hardcoding a pilot site. If no site meets the gate, keep the pilot as location-labeled Research-only raw diagnostic and defer Place/date binding; do not invent GPS/time zone.

**Owner W3 — one isolated adapter test pilot, after W1/W2 inputs.** Build a source-independent normalizer plus a single approved-provider transport path using fixtures and one opt-in genuine response. Verify mandatory fields, exact valid times, native unit conversions, UTC/local distinctions, source hash/freshness and fail-closed negative cases. Output a versioned informational `RAW_ONLY` hourly result; no `AUTO` result, score or favorable claim. Prefer reusing a source adapter only if actual provider and region are compatible; #517 NWS is Seattle research, **not** a Taiwan weather data fallback. Keep changes in W3 paths and open a distinct Draft PR.

**Owner W4/W5 — separate later handoff.** After the adapter's review, provide a minimal trilingual hourly-weather table in an independent W4 PR (explicit provider/update/valid time, missing-data text, and “raw weather ≠ suitable photograph”). W5 handles pins, immutable artifact, exact-head CI, candidate browser build and manual Research-only deployment approval. The first pilot must not depend on W2 completing all Places or W3 finishing all photographic models.

## Measurable gate for the first releaseable increment

- [ ] One W1-approved provider/region/terms and explicit hourly field mapping.
- [ ] One W2 evidenced location context and date/zone semantics, or visibly location-unbound diagnostic with no Place-date claim.
- [ ] One authenticated real-provider sample plus replayable original bytes; fixture-only testing never treated as live.
- [ ] Source provider/run or honest unknown, retrieval time, provider update time, validity, raw hash, native units/resolution, coverage/freshness and missing-value reasons.
- [ ] Negative tests: missing cloud/wind/rain, stale source, wrong location/timezone, invalid unit or native interval, unsupported region, partial forecast response.
- [ ] W4 read-only display explicitly informational with zh-TW/en/ja semantic parity, no score, no Directions, no hidden date fallback.
- [ ] W5 exact-head Integration, Release Readiness, merge rehearsal, post-merge public manifest/Pages and mobile/desktop smoke after approval.

Do not hold the Research-only “What can you photograph here?” feature while these gates are implemented. #519 remains independent and already published; #517's Research-only NWS merge still requires a separate decision.

## Validation and handoff status

- **This review:** inspected existing code, current main SHA, W1 V2 contract documents and open W3/W5 PRs. No model, API or user-facing code changed.
- **Not performed:** new fixture/real-provider tests, V2 integration CI, public browser tests, real forecast accuracy comparison, deployment, or field calibration.
- **Next bounded action:** W1 provider/admission + W2 single-site evidence; then W3 one-source informational hourly weather diagnostic. No “complete all providers/eight topics” acceptance criteria.
