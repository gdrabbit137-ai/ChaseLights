# B111 — Qingshui 06:00 Forecast Revision #5 and Current Stability Segment

Date: 2026-09-29 (Asia/Taipei)

## Purpose

B111 retains a fifth immutable forecast revision for the existing Qingshui Cliff
06:00 revision series and adds explicit reporting for the *current* stable
selected-input and recorded-Opportunity segments.

Target:

- place: `tw-034`
- forecast valid UTC: `2026-09-28T22:00:00+00:00`
- forecast valid local: `2026-09-29 06:00 +08:00`

No scoring, normalization, or spatial thresholds are changed.

## Fifth revision

Snapshot:

`FVS-TW-034-20260928-185246`

Captured:

`2026-09-28T18:52:46.332163+00:00`

Lead time to forecast validity:

`11233 s` — about 3 h 7 m 13 s.

Production commit:

`2d435c582e7c7d1826c698e5c9922ee4b340fe72`

Payload SHA256:

`184824f6f8749e46cad7eebf45b3a2188c18c28014602865fda096b7674d71db`

Observation status:

`unreviewed`

## Five-revision series

The retained 06:00 series is now:

1. `FVS-TW-034-20260928-173805`
2. `FVS-TW-034-20260928-181202`
3. `FVS-TW-034-20260928-183014`
4. `FVS-TW-034-20260928-184220`
5. `FVS-TW-034-20260928-185246`

Total capture span:

`4481 s` — about 74 m 41 s.

The fifth capture moved the nearest retained stable point to about 3 h 7 m
before forecast validity.

## Actual revision-comparison result

Revision Comparison CI reports:

- revision count: 5,
- transition count: 4,
- camera raw revision count: 4,
- spatial raw revision count: 4,
- normalized-input revision count: 0,
- metric revision count: 0,
- recorded Opportunity revision count: 0,
- code-commit revision count: 4,
- model-contract revision count: 0,
- `stable_selected_input = true`,
- `stable_recorded_opportunities = true`,
- `stable_model_contract = true`.

All four transitions classify as:

`provider_payload_revision_without_selected_input_change`

This means every retained provider refresh changed both raw camera and spatial
payloads, but none changed the exact 06:00 row consumed by ChaseLights.

## Current selected-input stable segment

B111 adds a current stable-segment summary.

For the real Qingshui series:

- from snapshot: `FVS-TW-034-20260928-173805`,
- to snapshot: `FVS-TW-034-20260928-185246`,
- capture count: 5,
- stable span: `4481 s`,
- latest capture lead time: `11233 s`.

So the exact selected input has been continuously stable across all five
retained captures for at least about 74 m 41 s.

This is stronger than a simple boolean `stable_selected_input = true` because
it identifies both the start of the current stable run and how close that run
has been observed to forecast validity.

## Current recorded-Opportunity stable segment

The recorded Opportunity segment is identical:

- from snapshot: `FVS-TW-034-20260928-173805`,
- to snapshot: `FVS-TW-034-20260928-185246`,
- capture count: 5,
- stable span: `4481 s`,
- latest capture lead time: `11233 s`.

No recorded P01/P02/P03 revision occurred inside the current segment.

## Selected 06:00 values

All five retained revisions continue to agree on:

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

## Recorded Opportunity stability

All five revisions retain:

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

Revision CI also replays all five forecast revisions under one common current
model.

Result:

- transition count: 4,
- Opportunity revision count: 0,
- `stable_opportunities = true`.

Therefore the stable P01/P02/P03 sequence is not caused by comparing results
recorded under different Git commits.

## Interpretation

The live evidence now shows:

```
5 retained forecast captures
4 provider payload transitions
4 camera raw revisions
4 spatial raw revisions
0 selected-input revisions
0 metric revisions
0 Opportunity revisions
```

This gives ChaseLights a useful product-level concept:

> the forecast provider is still refreshing, but this exact photographic
> decision has remained stable for the currently observed interval.

The current stable segment should not be confused with forecast accuracy.

A forecast may be stable and still be wrong.

## Ground-truth boundary

All five snapshots remain:

- forecast evidence,
- `observation.status = unreviewed`,
- not photographs,
- not observed-scene assessments,
- outside `field_validation_registry_r4_2.json`.

Field validation remains the separate mechanism for comparing the forecast
against reality.

## Runtime impact

None.

B111 changes only Snapshot analytics, retained forecast evidence, regression
coverage, and documentation. It does not modify public Opportunity scoring,
weather normalization, spatial mist logic, or UI behavior.
