# B110 — Qingshui 06:00 Forecast Revision #4

Date: 2026-09-29 (Asia/Taipei)

## Purpose

B110 retains a fourth immutable forecast revision for the existing Qingshui Cliff
06:00 revision series and verifies whether the selected forecast row begins to
change as capture time moves closer to forecast validity.

Target:

- place: `tw-034`
- forecast valid UTC: `2026-09-28T22:00:00+00:00`
- forecast valid local: `2026-09-29 06:00 +08:00`

No scoring thresholds are changed.

## Fourth revision

Snapshot:

`FVS-TW-034-20260928-184220`

Captured:

`2026-09-28T18:42:20.773974+00:00`

Lead time to forecast validity:

`11859 s` — about 3 h 17 m 39 s.

Production commit:

`48733937b271a8da11198da7084a0a33f56c4da5`

Payload SHA256:

`9dca4f83e8c73a93593605c2b0aead3b6d342365a6367060a730f3d8fac04801`

Observation status:

`unreviewed`

## Four-revision series

The retained 06:00 series is now:

1. `FVS-TW-034-20260928-173805`
2. `FVS-TW-034-20260928-181202`
3. `FVS-TW-034-20260928-183014`
4. `FVS-TW-034-20260928-184220`

Total capture span:

`3855 s` — about 64 m 16 s.

Capture intervals:

- revision 1 → 2: about 33 m 57 s,
- revision 2 → 3: about 18 m 12 s,
- revision 3 → 4: about 12 m 6 s.

## Selected 06:00 input

The normalized selected-row SHA256 remains:

`1206e6bc124ce989a95b8f052c6d2a96e425b40bf3d75787dbf5507bfc30ebd6`

All four revisions retain:

| Metric | Value |
| --- | ---: |
| Visibility | 3.56 km |
| Low cloud | 5% |
| Mid cloud | 1% |
| High cloud | 0% |
| RH | 66% |
| Precipitation | 0 mm |
| Wind | 1.1 m/s |
| Temperature | 22.2 °C |
| Dew point | 15.5 °C |
| Estimated LCL | 837 m AGL |
| Sun elevation | 2.7° |
| Sun azimuth | 93.8° |

Therefore the fourth capture still does **not** represent a selected-hour
forecast-data revision.

## Recorded Opportunity result

All four revisions retain:

### P01

- score: 64,
- confidence: low,
- state: `partial_runtime_contract`.

### P02

- score: 54,
- confidence: medium,
- state: `minimum_sufficient_conditions_miss`,
- runtime reason: `visibility_too_low`.

### P03

- score: 54,
- confidence: medium,
- state: `minimum_sufficient_conditions_miss`,
- runtime reason: `low_visibility_without_mist_support`,
- target samples: 6,
- mist targets: 0,
- directional-mist targets: 0,
- clear targets: 0,
- clear bearings: 0,
- `broad_clear_target_sector = false`,
- `directional_mist_negative_evidence = false`.

## Actual four-point stability result

Revision Comparison CI reports:

- revision count: 4,
- transition count: 3,
- camera raw revision count: 3,
- spatial raw revision count: 3,
- normalized-input revision count: 0,
- metric revision count: 0,
- recorded Opportunity revision count: 0,
- code-commit revision count: 3,
- model-contract revision count: 0,
- `stable_selected_input = true`,
- `stable_recorded_opportunities = true`,
- `stable_model_contract = true`.

All three transitions classify as:

`provider_payload_revision_without_selected_input_change`

Common-model replay reports:

- transition count: 3,
- Opportunity revision count: 0,
- `stable_opportunities = true`.

## Interpretation

Across more than one hour of retained captures, the provider responses changed
every time, but the exact 06:00 input consumed by ChaseLights did not.

For this real series:

```
3 raw camera payload revisions
3 raw spatial payload revisions
0 selected-input revisions
0 metric revisions
0 Opportunity revisions
```

This further confirms that provider-response churn must not be treated as
forecast-decision churn.

## Ground-truth boundary

B110 is still forecast evidence only.

A stable forecast is not necessarily an accurate forecast.

No photograph, observed-scene assessment, or B99 field observation is attached,
so this revision remains outside `field_validation_registry_r4_2.json`.

## Runtime impact

None.

B110 changes only retained Snapshot evidence, registry data, regression coverage,
and documentation. It does not modify scoring, normalization, spatial mist
logic, or the public UI.
