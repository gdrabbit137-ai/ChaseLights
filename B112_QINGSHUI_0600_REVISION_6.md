# B112 — Qingshui 06:00 Forecast Revision #6

Date: 2026-09-29 (Asia/Taipei)

## Purpose

B112 retains a sixth immutable forecast revision for the existing Qingshui Cliff
06:00 revision series and extends the current forecast-stability observation
closer to forecast validity.

Target:

- place: `tw-034`
- forecast valid UTC: `2026-09-28T22:00:00+00:00`
- forecast valid local: `2026-09-29 06:00 +08:00`

No scoring, normalization, spatial, or public UI behavior is changed.

## Sixth revision

Snapshot:

`FVS-TW-034-20260928-191509`

Captured:

`2026-09-28T19:15:09.002992+00:00`

Lead time to forecast validity:

`9890 s` — about 2 h 44 m 50 s.

Production commit:

`ac6726360cef60fe9e77219af5ece92cfd670c7b`

Payload SHA256:

`3cc2fb4c1312c2ea1bb65210d4890a6a589522f5fb0929c77b47435ebd295a4a`

Observation status:

`unreviewed`

## Six-revision series

The retained 06:00 series is now:

1. `FVS-TW-034-20260928-173805`
2. `FVS-TW-034-20260928-181202`
3. `FVS-TW-034-20260928-183014`
4. `FVS-TW-034-20260928-184220`
5. `FVS-TW-034-20260928-185246`
6. `FVS-TW-034-20260928-191509`

Total capture span:

`5823 s` — about 97 m 3 s.

The nearest retained stable observation is now about 2 h 44 m 50 s before the
06:00 forecast-valid time.

## Actual revision-comparison result

Revision Comparison CI reports:

- revision count: 6,
- transition count: 5,
- camera raw revision count: 5,
- spatial raw revision count: 5,
- normalized-input revision count: 0,
- metric revision count: 0,
- recorded Opportunity revision count: 0,
- code-commit revision count: 5,
- model-contract revision count: 0,
- `stable_selected_input = true`,
- `stable_recorded_opportunities = true`,
- `stable_model_contract = true`.

All five transitions classify as:

`provider_payload_revision_without_selected_input_change`

## Current selected-input stable segment

- from: `FVS-TW-034-20260928-173805`
- to: `FVS-TW-034-20260928-191509`
- capture count: 6,
- span: `5823 s`,
- latest capture lead time: `9890 s`.

The selected 06:00 row has therefore remained continuously stable across all
six retained captures for at least about 97 minutes.

## Current recorded-Opportunity stable segment

The recorded Opportunity segment is identical:

- from: `FVS-TW-034-20260928-173805`
- to: `FVS-TW-034-20260928-191509`
- capture count: 6,
- span: `5823 s`,
- latest capture lead time: `9890 s`.

No recorded P01/P02/P03 revision occurred in that interval.

## Opportunity state

All six revisions continue to retain:

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
- mist targets: 0,
- directional-mist targets: 0,
- clear targets: 0,
- `broad_clear_target_sector = false`,
- `directional_mist_negative_evidence = false`.

## Common-model replay

All six revisions were also replayed through one common current model.

Result:

- transition count: 5,
- Opportunity revision count: 0,
- `stable_opportunities = true`.

This confirms that the stable Opportunity sequence is not caused by comparing
snapshots recorded under different Git commits.

## Interpretation

The live evidence now shows:

```
6 retained forecast captures
5 provider-payload transitions
5 camera raw revisions
5 spatial raw revisions
0 selected-input revisions
0 metric revisions
0 Opportunity revisions
```

The provider response has changed on every retained refresh, but the exact 06:00
row consumed by ChaseLights has not changed once over the observed 97-minute
window.

This remains a forecast-stability statement, not an accuracy statement.

## Ground-truth boundary

All six snapshots remain:

- forecast evidence,
- `observation.status = unreviewed`,
- not photographs,
- not observed-scene assessments,
- outside `field_validation_registry_r4_2.json`.

Field validation remains the separate mechanism for comparing the forecast with
the real scene.

## Runtime impact

None.

B112 changes only retained Snapshot evidence, regression coverage, and
documentation.
