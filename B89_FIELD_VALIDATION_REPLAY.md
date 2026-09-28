# B89 — Field Validation Replay Fixture

Date: 2026-09-28 (Asia/Taipei)

## Goal

B86 introduced a structured field-validation registry, but the first Qixingtan case still stored only:

- observed-scene metadata,
- aggregate production diagnostics,
- expected Opportunity states / scores.

That was enough to validate the registry structure, but not enough to machine-replay the runtime decision.

B89 adds an optional replay-fixture layer.

## Important provenance boundary

The first replay fixture is **not** the original raw historical Open-Meteo response.

It is explicitly:

`fixture_type = synthetic_minimum_reproduction`

and:

`historical_raw_input = false`

The values are chosen to reproduce the already-verified aggregate B85 diagnostics for:

`FV-TW-036-20260928-1300-01`

This lets CI reproduce the intended model behavior without falsely claiming that reconstructed inputs are historical observations.

## Files

- `field_validation_registry_r4_2.json`
  - now links the Qixingtan field case to its replay fixture.
- `field_validation.py`
  - validates replay fixture schema, provenance type, numeric inputs, expected outputs, and registry linkage.
- `test_fixtures/field_validation/FV-TW-036-20260928-1300-01.json`
  - synthetic minimum reproduction of the validated 13:00 Qixingtan runtime boundary.
- `test_opportunity_adapter.py`
  - rebuilds the spatial request response from the fixture,
  - runs P03 / P04 spatial modules,
  - runs Opportunity scoring,
  - compares the result with the field-validation case.
- Adapter CI watches fixture JSON changes.

## Qixingtan replay contract

The replay fixture reproduces these validation characteristics:

- camera visibility: 27 km,
- camera low cloud: 2%,
- camera LCL planning proxy: 699 m AGL,
- four elevated northward proxy samples,
- three LCL/terrain intersections across two bearings,
- minimum elevated visibility: 5.6 km,
- minimum elevated/camera visibility ratio: about 0.21,
- maximum elevated low cloud: 24%,
- three still-readable elevated samples across two bearings.

Expected results:

### `tw-036-P03`
- runtime reason: `orographic_cloud_proxy_candidate`
- score: 78
- confidence: low
- direct cloud signal: false
- low-confidence orographic proxy: true

### `tw-036-P04`
- runtime reason: `directional_mountain_view_readable`
- score: 86
- confidence: medium

## Why this matters

The field-validation registry can now serve two different purposes without mixing evidence classes:

1. **Observed scene record**
   - what was seen in the real photograph / field observation.
2. **Machine replay fixture**
   - the minimum model inputs used to ensure the runtime keeps interpreting that class of scene as intended.

The replay fixture does not admit a new subject and does not replace Place-specific evidence.

## Future fixture types

Supported provenance types are intentionally explicit:

- `synthetic_minimum_reproduction`
  - reconstructed regression input,
  - must set `historical_raw_input = false`.
- `captured_raw_model_inputs`
  - reserved for future cases where the original model inputs are actually retained,
  - must set `historical_raw_input = true`.

Never relabel a synthetic reconstruction as captured raw input.

## Next useful extension

When future field cases are collected, prefer retaining the minimum non-identifying model inputs needed for replay at validation time. This avoids reconstructing them later and makes false-positive / false-negative threshold changes easier to review.
