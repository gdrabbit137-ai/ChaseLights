# B109 — Qingshui 06:00 Forecast Revision Stability Series

Date: 2026-09-29 (Asia/Taipei)

## Purpose

B109 extends the B106 two-point forecast revision comparison into a
three-capture stability series for the exact same Qingshui Cliff forecast-valid
row.

The target remains:

- place: `tw-034`
- forecast valid UTC: `2026-09-28T22:00:00+00:00`
- forecast valid local: `2026-09-29 06:00 +08:00`

The purpose is to distinguish:

1. provider payload churn,
2. selected-hour forecast revisions,
3. Opportunity-output revisions,
4. code-commit changes,
5. declared model-contract changes.

No field observation is claimed.

## Revision series

### Revision 1

- snapshot: `FVS-TW-034-20260928-173805`
- captured: `2026-09-28T17:38:05.029841+00:00`
- lead time to 06:00: 15,714 s
- production commit: `808a585ba2c3f087c6d49a60d6a3d1bcb39ca9e6`

### Revision 2

- snapshot: `FVS-TW-034-20260928-181202`
- captured: `2026-09-28T18:12:02.957254+00:00`
- production commit: `560db8c542989bedf9688a3c3d60667751a9df4e`

### Revision 3

- snapshot: `FVS-TW-034-20260928-183014`
- captured: `2026-09-28T18:30:14.951207+00:00`
- lead time to 06:00: 12,585 s
- production commit: `2730098cc4796288ace43ab9450d26d9107936e0`
- payload SHA256:
  `5cb55c373293cf92983497ba508cccef05e7948a5bc3e4ee5f643ef3c625454c`

Total capture span:

`3129 s` — about 52 m 9 s.

Transition 1 interval:

`2037 s` — about 33 m 57 s.

Transition 2 interval:

`1091 s` — about 18 m 11 s.

## Stability summary

B109 adds `stability_summary` to `compare-revisions`.

For the real three-capture Qingshui series:

- revision count: 3,
- transition count: 2,
- camera raw revision count: 2,
- spatial raw revision count: 2,
- normalized-input revision count: 0,
- metric revision count: 0,
- recorded Opportunity revision count: 0,
- code-commit revision count: 2,
- model-contract revision count: 0,
- `stable_selected_input = true`,
- `stable_recorded_opportunities = true`,
- `stable_model_contract = true`.

Both transitions classify as:

`provider_payload_revision_without_selected_input_change`

## Selected 06:00 forecast values

All three retained revisions agree on the selected forecast row:

| Metric | Rev 1 | Rev 2 | Rev 3 |
| --- | ---: | ---: | ---: |
| Visibility | 3.56 km | 3.56 km | 3.56 km |
| Low cloud | 5% | 5% | 5% |
| Mid cloud | 1% | 1% | 1% |
| High cloud | 0% | 0% | 0% |
| RH | 66% | 66% | 66% |
| Precipitation | 0 mm | 0 mm | 0 mm |
| Wind | 1.1 m/s | 1.1 m/s | 1.1 m/s |
| Temperature | 22.2 °C | 22.2 °C | 22.2 °C |
| Dew point | 15.5 °C | 15.5 °C | 15.5 °C |
| Est. LCL | 837 m AGL | 837 m AGL | 837 m AGL |
| Sun elevation | 2.7° | 2.7° | 2.7° |

Therefore:

`metric_changes = [{}, {}]`

## Recorded Opportunity stability

All three revisions also agree on the recorded Opportunity result.

### P01

- score: 64,
- confidence: low,
- condition state: `partial_runtime_contract`,
- runtime reason: `module_pending`.

### P02

- score: 54,
- confidence: medium,
- condition state: `minimum_sufficient_conditions_miss`,
- runtime reason: `visibility_too_low`.

### P03

- score: 54,
- confidence: medium,
- condition state: `minimum_sufficient_conditions_miss`,
- runtime reason: `low_visibility_without_mist_support`,
- target samples: 6,
- mist targets: 0,
- directional-mist targets: 0,
- clear targets: 0,
- clear bearings: 0,
- `broad_clear_target_sector = false`,
- `directional_mist_negative_evidence = false`.

Recorded Opportunity changes:

`[[], []]`

## Common-model replay stability

B109 also summarizes common-model replay stability.

All three snapshots were replayed through the same current PR model.

Result:

- transition count: 2,
- Opportunity revision count: 0,
- `stable_opportunities = true`.

This confirms that the stable output is not an artifact of comparing snapshots
recorded under different Git SHAs.

## Why this matters

The three retained provider responses were not byte-identical.

Both camera and spatial provider payloads changed between every capture.

However the exact 06:00 values consumed by ChaseLights did not change.

Therefore it would be incorrect to say:

> every provider refresh represents a meaningful forecast revision.

B109 establishes a stronger distinction:

```
provider refresh
  != selected forecast-row revision
  != Opportunity decision revision
```

For this real series:

```
2 provider payload revisions
0 selected-input revisions
0 metric revisions
0 Opportunity revisions
```

This gives ChaseLights a measurable concept of forecast stability.

## New stability fields

`compare-revisions` now reports:

- `capture_span_seconds`,
- first / last lead time,
- transition count,
- camera raw revision count,
- spatial raw revision count,
- normalized-input revision count,
- metric revision count,
- recorded Opportunity revision count,
- code-commit revision count,
- model-contract revision count,
- selected-input stability,
- recorded-Opportunity stability,
- model-contract stability,
- classification counts.

Common-model replay additionally reports:

- transition count,
- Opportunity revision count,
- stable-Opportunity flag.

## CI

`.github/workflows/test_field_snapshot_revisions.yml` now publishes these
stability summaries for every registry revision group.

The workflow remains registry-driven; no location-specific logic is required for
future Qixingtan, Hehuanshan, or other forecast revision series.

## Ground-truth boundary

All three snapshots remain:

- forecast evidence,
- `observation.status = unreviewed`,
- not photographs,
- not observed-scene assessments,
- outside `field_validation_registry_r4_2.json`.

Forecast stability does not validate forecast accuracy.

A stable wrong forecast is still wrong. Field Validation remains the separate
mechanism for measuring forecast-versus-reality performance.

## Runtime impact

None.

B109 changes only Snapshot analytics, retained forecast evidence, regression
coverage, and CI reporting.

It does not modify:

- Qingshui thresholds,
- Opportunity scoring,
- spatial mist rules,
- weather normalization,
- public UI behavior.
