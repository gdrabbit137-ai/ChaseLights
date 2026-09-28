# B105 — Qingshui 06:00 Morning-Window Forecast Baseline

Date: 2026-09-29 (Asia/Taipei)

## Purpose

B105 adds a second permanent Qingshui Cliff Field Snapshot baseline, this time
for a forecast-valid hour inside the morning photography window.

It complements B103:

- B103 baseline: 01:00 local, strong directional-mist runtime signal but outside visible-light timing.
- B105 baseline: 06:00 local, visible-light eligible environment but no directional-mist support and insufficient visibility for the clear-cliff subject.

Neither snapshot is field ground truth.

## Production source

The capture workflow checked out production commit:

`808a585ba2c3f087c6d49a60d6a3d1bcb39ca9e6`

This is the post-B104 main commit.

The capture explicitly requested:

`2026-09-29T06:00:00+08:00`

and selected exactly:

- forecast valid UTC: `2026-09-28T22:00:00+00:00`
- forecast local date: `2026-09-29`
- forecast local time: `06:00`

## Permanent baseline

Snapshot:

`FVS-TW-034-20260928-173805`

Permanent archive:

`test_fixtures/field_snapshot/FVS-TW-034-20260928-173805.json.gz.b64`

Metadata:

`test_fixtures/field_snapshot/FVS-TW-034-20260928-173805.metadata.json`

Integrity:

- captured at: `2026-09-28T17:38:05.029841+00:00`
- forecast valid at: `2026-09-28T22:00:00+00:00`
- model commit: `808a585ba2c3f087c6d49a60d6a3d1bcb39ca9e6`
- payload SHA256: `3f370784e11bf2403c2f960dfbfa2a2b2e318ecda013ac4168c31e7557644d59`
- observation status: `unreviewed`

The snapshot was captured approximately 4 hours 22 minutes before the
forecast-valid time. It therefore preserves one forecast revision for 06:00; it
does not claim to describe what will actually be observed at 06:00.

## Recorded camera conditions

At the selected forecast hour:

- visibility: 3.56 km,
- RH: 66%,
- low cloud: 5%,
- mid cloud: 1%,
- high cloud: 0%,
- precipitation: 0 mm,
- wind: about 1.1 m/s,
- temperature: 22.2 °C,
- dew point: 15.5 °C,
- estimated LCL / condensation height: about 837 m AGL,
- sun elevation: 2.7°,
- sun azimuth: 93.8°.

## Recorded Opportunity behavior

### P01

`tw-034-P01`

- score: 64,
- confidence: low,
- condition state: `partial_runtime_contract`.

Its dedicated runtime module remains pending.

### P02 — clear cliff / mountain-sea view

`tw-034-P02`

- score: 54,
- confidence: medium,
- condition state: `minimum_sufficient_conditions_miss`,
- runtime reason: `visibility_too_low`.

The 3.56 km camera visibility is not sufficient for the clear long-distance
cliff/seascape subject.

### P03 — morning mist / cloud-mountain-sea

`tw-034-P03`

- score: 54,
- confidence: medium,
- condition state: `minimum_sufficient_conditions_miss`,
- runtime eligible: false,
- runtime reason: `low_visibility_without_mist_support`,
- minimum-sufficient score hint: 0,
- runtime confidence hint: low,
- `directional_mist_negative_evidence = false`.

Spatial mist diagnostics:

- spatial data available: true,
- spatial mist eligibility: false,
- spatial reason: `directional_mist_not_distinguished_from_camera`,
- target sample count: 6,
- mist target count: 0,
- directional-mist target count: 0,
- clear target count: 0,
- clear bearing count: 0,
- `broad_clear_target_sector = false`.

This is an important middle state:

- visibility is low enough that P02 clear-cliff quality is weak,
- but there is no directional mist signal supporting P03,
- and the spatial sector is not sufficiently broad-clear to invoke the explicit
  negative-spatial veto.

So P03 fails for **lack of positive mist support**, not because of broad-clear
negative evidence.

## Comparison with B103 01:00 baseline

| Signal | B103 01:00 | B105 06:00 |
| --- | ---: | ---: |
| Camera visibility | 0.5 km | 3.56 km |
| Low cloud | 41% | 5% |
| RH | 82% | 66% |
| Mist targets | 5 / 6 | 0 / 6 |
| Directional-mist targets | 2 | 0 |
| Broad-clear sector | false | false |
| P03 runtime reason | camera visibility too low for readability | low visibility without mist support |
| Final P03 score | 38 | 54 |
| Final P03 confidence | medium | medium |

The two baselines therefore cover two materially different reasons that the
same photographic subject may not be recommended.

## Original replay

Immediately after capture, the snapshot was replayed against its original
production commit.

Result:

- `match = true`,
- `different_opportunity_ids = []`.

## Registry-driven matrix CI

B105 generalizes `.github/workflows/test_field_snapshot_matrix.yml`.

The workflow now reads every entry in:

`field_snapshot_baselines_r4_2.json`

and runs:

`original -> current`

matrix replay for each baseline.

For every registered snapshot:

- original commit must equal the baseline's recorded `model_commit`,
- original replay must exactly reproduce the recorded stable output,
- current replay must run against the actual current HEAD,
- current output may intentionally differ from the recorded output,
- all differences are retained in matrix artifacts.

This makes future baseline growth data-driven rather than requiring CI edits for
each new snapshot.

## Ground-truth boundary

This remains forecast evidence only.

No photograph is attached.
No observed Qingshui scene is asserted.
No B99 `qingshui_cliff_mist` field-observation profile has been completed.

Therefore this snapshot must not be added to
`field_validation_registry_r4_2.json`.

A later 06:00 field observation may be compared with this forecast snapshot, but
that comparison would be a separate Field Validation Case.
