# ChaseLights V2 — M6a Solar Window Contract v0.1

**Owner:** W1 `specs/v2/`. **Status:** implementation proposal for [Issue #467](https://github.com/gdrabbit137-ai/ChaseLights/issues/467), **NOT a released model**. Respects `RESEARCH_EVIDENCE_SPEC_R4_2`, `NAVIGATION_SPEC_R4_2`, `ACCESS_ADVISORY_SPEC`, `FREE_COMPOSITION_SPEC` and independent V1/V2 release gates.

## 1. Core distinction

- The deterministic sun-event algorithm answers **when an astronomical altitude crossing may occur** for a documented geographic observation sample.
- It does **not** establish **what is photographed**, a lawful Camera Area, sunrise over the actual photographed horizon, cloud obstruction, a Place-specific composition, a weather score, or a calibrated probability.
- `WINDOW` is a deterministic technical capability, not `FAVORABLE`. A returned sunrise/sunset never satisfies an unreviewed Opportunity `ConditionContract.REQUIRED` and does not promote R1 to R2/R3.
- A broad representative Place location may be used for illustrative **regional solar times only**, with visible coordinate provenance/uncertainty. It MUST NOT be called a surveyed tripod GPS or used for Directions. If the origin is unknown/missing, return `UNKNOWN_LOCATION` and no invented timestamp.
- No exact camera or Subject GPS is required for normal free composition. Only actual horizon alignment, shadow, subject direction and other geometry-specific claims need verified observer/horizon/camera relations.
- Access warnings remain **independent of sunrise computation/photographic suitability**; a closed location can have a computable sunrise time, but never verified Directions to a closed/unreviewed arrival target.

## 2. Formal interface

Separate Draft 2020-12 contracts:
- `schema/solar-window-request-v0.1.schema.json` — validated input only.
- `schema/solar-window-result-v0.1.schema.json` — results and explicit uncertainty, no prediction/score.
- Both require `schema_version="0.1.0"`; every request and result must record `request_id`, a strict `local_date` and valid IANA `time_zone` (the JSON Schema checks nonempty syntax; implementation MUST check using the IANA/zoneinfo database and reject invalid dates or timezone names).
- `observer` has separate `coordinate_role` (`verified_camera_reference`, `representative_place_sample`, `unknown`), coordinates, `coordinate_source` (nonblank citation if coordinates given), `uncertainty_m` (nullable if not measured) and `altitude_m` (nullable). Null/unverified observer must yield `UNKNOWN_LOCATION`; representative samples may yield a **regional sample** with that limitation shown.
- `model` identifies algorithm/version and astronomical conventions; W3 MUST NOT silently substitute a method that has different sunrise refraction/horizon assumptions. A default geometric sea-level horizon does NOT account for actual mountains/buildings.
- `sun_altitude_crossing_deg` for apparent sunrise/sunset MAY be fixed to `-0.833` as a widely used *approximation* at an unobstructed ideal horizon; W3 must explain that atmospheric refraction, observer altitude, topography and real weather can shift the visible event. Do not silently claim ±1 minute geophysical accuracy.
- `computed_at_utc` is **when computation ran**, not a weather-model issue time. Event `time_utc` and `time_local` are absolute instants paired with UTC offset and IANA timezone conversion, not a provider `issued_at` or forecast `valid_at`.
- Result `capability="WINDOW"`, `recommendation_eligible=false` and `photography_verdict="NOT_EVALUABLE"` are frozen in v0.1. Future full-source W3 evaluations live in separate EvaluationResult artifacts after reviewed AUTO gates.

## 3. Model result statuses

Each of `sunrise` and `sunset` returns:
- `CALCULATED`: an event instant based on declared assumptions; `time_utc` and `time_local` are non-null.
- `NO_EVENT`: the relevant altitude crossing does not occur within the specified **local civil date**; time fields null, `reason` is `POLAR_DAY`, `POLAR_NIGHT` or `OTHER_HIGH_LATITUDE`. W3 MUST distinguish such days from calculation failures. A single sunrise/sunset missing does **not** justify a made-up timestamp.
- `UNKNOWN`: missing/invalid observer, unverified timezone, model breakdown or geographic/accuracy limitation; no event time. Unknown `reason` must be explicit.
- For `CALCULATED`, W3 must prove `time_local` falls within the requested `local_date`, and verify consistency with `time_utc` and the named IANA zone (DST-safe). A UTC civil date may differ from the local date. Never clip/swap crossing times to force the output.
- `polar_state` is an independent diagnosis: `NORMAL`, `POLAR_DAY`, `POLAR_NIGHT` or `UNKNOWN`. Any polar-classification disagreement or multiple atypical crossings must propagate `UNKNOWN` rather than making sunrise events up.

## 4. Correctness, evidence and boundaries

W3 implementation requires reproducible benchmark references (NOAA/USNO-style algorithms or authoritative almanac comparisons, with documented licensing and input parameters). These are **acceptance targets, not claims of tests already run**:
1. Taiwan / Japan / Seattle event times compared to authoritative dated reference values; tolerances are measured empirically and published, not selected to hide a drift.
2. Alaska autumn, equinox and solstice; northern and southern polar day/night, and events crossing the international date line.
3. IANA daylight saving change days in `America/Los_Angeles` and `America/Anchorage`, including days with non-24-hour length, and `Asia/Taipei` / `Asia/Tokyo` no-DST baseline.
4. Deliberately missing coordinates, invented `source`, `local_date` invalid, IANA zone typo, coordinate range errors, and mismatched UTC/local event instants must all fail closed.
5. Ordinary free composition without camera GPS can show `regional sample solar times` with `representative_place_sample`, BUT must not label such a result a confirmed horizon alignment.
6. A site/access closure SHALL NOT change the solar event or photography score, yet shall independently restrict navigation/entry advisories.
7. No dynamic color clouds, fog, Milky Way or moon events are inferred from this Sun-only v0.1 output.

## 5. Deployment and model ownership

- W1: publishes/reviews these immutable input/output schemas and localized user-facing explanation requirements.
- W3: writes `packages/models-v2/` algorithm and independent numeric tests; produces `WINDOW` only, not photography `FAVORABLE`.
- W2: supplies place-specific research evidence and candidate descriptive conditions; does not fabricate thresholds from the deterministic solar event alone.
- W4: optional research-only diagnostic view, clearly marked regional estimate vs verified camera point; preserve zh-TW/en/ja and safety warning.
- W5: intentional immutable W1/W3 source-pin rotation and strict test-count rebaseline; old full research-only and public V1/V2 smoke must still pass. Do not merge this proposal to main or enable model-related claims until cross-worker verification is ready.

**Example safe behavior:** A user selects `2026-10-13` at a researched lake. If only the lake's representative location is known, compute a regional approximate sunrise `WINDOW` with `representative_place_sample`, show a note that local obstruction/visibility are not checked, and leave all actual subject-alignment and sky-weather conditions `UNKNOWN`; do **not** issue a shooting recommendation or Directions.
