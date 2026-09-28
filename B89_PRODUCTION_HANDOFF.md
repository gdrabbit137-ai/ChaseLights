# ChaseLights R4.2 B89 Production / Maintenance Handoff

Date: 2026-09-28 (Asia/Taipei)

## Start here

This file supersedes `B88_PRODUCTION_HANDOFF.md` as the current production / maintenance checkpoint.

Before changing production:

1. inspect GitHub `main` and all open pull requests,
2. read this file,
3. read `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md` and `RESEARCH_EVIDENCE_SPEC_R4_2.md`,
4. read `B86_FIELD_VALIDATION_REGISTRY.md` and `B89_FIELD_VALIDATION_REPLAY.md` before adding or changing field-validation cases,
5. read the B83–B85 Qixingtan documents before changing `tw-036-P03/P04`,
6. read the B87–B88 Qingshui documents before changing `tw-034-P03`,
7. keep evidence admission, field observation, replay fixture, and runtime forecast semantics separate.

## Verified production checkpoint

Repository: `gdrabbit137-ai/ChaseLights`

Public site: <https://chaselights.app/>

Latest code checkpoint:
- B89 merge commit: `3e1a379eff9439051ff02d2dcbedad33343004ce`

Runtime/weather checkpoint remains:
- B88 runtime merge: `bffe5d7728bf07bd5e5696a9ba3ae2827bef551e`
- B88 generated weather: `20c35a249fa84420c9b3a745cd9fd956da1f6cab`

B89 changes only validation metadata, fixtures, tests, and documentation. It does not change weather scoring or runtime output, so no production weather regeneration was required.

B89 validation:
- PR Adapter CI — PASS
- post-merge Adapter CI — PASS
- Pages deployment — PASS

Open pull requests at this checkpoint:
- none

## What B89 adds

B86 created a structured field-validation registry. B89 adds a replay layer so an observed field case can also have a machine regression fixture.

Canonical field case:
- `FV-TW-036-20260928-1300-01`
- Place: `tw-036` 七星潭月牙灣
- observed local time: 2026-09-28 13:00 +08:00
- camera direction: north

Replay fixture:
- `test_fixtures/field_validation/FV-TW-036-20260928-1300-01.json`
- schema: `field-validation-replay-r4.2-1`
- type: `synthetic_minimum_reproduction`
- `historical_raw_input = false`

This provenance distinction is mandatory.

The fixture is a synthetic minimum reproduction derived from the already-verified aggregate production diagnostics. It is **not** the original raw historical Open-Meteo response and must never be presented as one.

## Machine replay result

Adapter CI now rebuilds the Qixingtan spatial-weather inputs from the fixture and runs the normal spatial modules plus Opportunity scoring.

Expected / verified behavior:

### `tw-036-P03` — terrain-attached cloud band
- runtime reason: `orographic_cloud_proxy_candidate`
- score: **78**
- confidence: **low**
- direct grid cloud signal: false
- orographic fallback: true
- terrain/LCL intersections: 3 targets across 2 bearings
- minimum elevated visibility: 5.6 km
- elevated/camera visibility ratio: 0.21
- maximum elevated low cloud: 24%
- 3 readable elevated targets across 2 bearings

### `tw-036-P04` — northward mountain-seascape
- runtime reason: `directional_mountain_view_readable`
- score: **86**
- confidence: **medium**
- 3 readable elevated targets across 2 bearings

The replay therefore locks the same interpretation that was validated against the real field photo:
- broad northward mountain-seascape is strongly usable,
- attached-cloud detail remains a lower-confidence candidate because the grid did not directly resolve the observed cloud band.

## Field-validation evidence classes

Keep four concepts separate:

1. **Place-specific research evidence**
   - determines whether a photographic subject may be admitted at a Place.
2. **Field observation**
   - records what was actually seen in a real scene.
3. **Replay fixture**
   - provides machine inputs for regression testing.
4. **Forecast/runtime output**
   - estimates whether an admitted subject is likely under a future or historical forecast state.

A replay fixture cannot admit a new subject.

A synthetic replay fixture cannot be described as original raw weather data.

A user photograph is not committed by default.

## Replay fixture validation

`field_validation.py` now validates:
- replay schema version,
- replay provenance type,
- `historical_raw_input` consistency,
- project-relative fixture paths,
- required camera / target numeric inputs,
- duplicate bearing/distance target points,
- theme-metric / expected-Opportunity ID agreement,
- expected score / state / confidence,
- consistency between fixture expected output and the field-validation registry.

Adapter CI also watches:
- `field_validation.py`
- `field_validation_registry_r4_2.json`
- `test_fixtures/field_validation/*.json`

## Current Qixingtan production behavior remains unchanged

The final B88 production weather output still gives the original 2026-09-28 13:00 validation hour:

- P04 mountain-seascape: **86**, medium confidence
- P03 terrain-attached cloud: **78**, low-confidence orographic proxy

Do not retune B85 again from this same single positive case.

## Current Qingshui protection remains unchanged

B87/B88 remain the production rule for `tw-034-P03`:

- camera visibility below 2.5 km => subject readability uncertain,
- low-confidence candidate may remain,
- final Opportunity score is capped at **68**,
- generic Theme baseline cannot lift it back into 80+,
- 2.5 km remains a planning guard, not a claimed cliff distance.

## Next-work queue

### 1. Collect additional real field-validation cases

Highest-value cases are now new labels, not more tuning from the existing Qixingtan photo.

Qixingtan:
- clear mountain with no attached cloud,
- attached cloud with stronger direct-grid signal,
- mountain whiteout,
- local camera fog,
- mixed partial-ridge visibility.

Qingshui:
- mist with clearly readable cliff,
- mist with mostly hidden cliff,
- low visibility without mist,
- directional mist signal with poor subject readability.

### 2. Preserve raw model inputs for future field cases when practical

For new validations, prefer retaining the minimum non-identifying model inputs required for replay at validation time.

Then use:
- `captured_raw_model_inputs`
- `historical_raw_input = true`

Do not retroactively relabel reconstructed fixtures as captured raw data.

### 3. Continue dynamic-access providers

Resume the B80 runtime-provider backlog after the Taiwan field-validation work:
- dynamic access providers,
- event-state providers,
- managed-lighting state,
- specialized environmental states.

### 4. Continue compatibility / payload cleanup conservatively

Retain:
- detail-shard payload audit,
- staged compatibility cleanup,
- favorites legacy retirement only after its observation window.

## Release gates

For field-validation changes:
- no subject admission from a field case alone,
- user images remain uncommitted unless publication is explicitly authorized,
- synthetic fixtures remain clearly marked synthetic,
- registry / fixture references validate,
- Adapter CI PASS.

For Qixingtan / Qingshui runtime changes, retain all release gates in `B88_PRODUCTION_HANDOFF.md`.
