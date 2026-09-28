# B106 — Forecast Revision Comparison

Date: 2026-09-29 (Asia/Taipei)

## Purpose

B106 adds a first-class way to compare multiple immutable Field Snapshots that
refer to the **same Place and the same forecast-valid row**, but were captured
at different times.

This answers a different question from B104 matrix replay:

- B104: hold forecast input fixed and change the ChaseLights code version.
- B106: hold forecast-valid time fixed and observe how provider forecast data
  changes across capture revisions.

When code commits differ between captures, B106 can also replay every revision
under one common model commit so forecast revision effects are not confused
with model-version effects.

## CLI

Basic recorded-revision comparison:

```bash
python field_snapshot.py compare-revisions \
  snapshot-revision-1.json.gz.b64 \
  snapshot-revision-2.json.gz.b64
```

Write the report to a file:

```bash
python field_snapshot.py compare-revisions \
  snapshot-revision-1.json.gz.b64 \
  snapshot-revision-2.json.gz.b64 \
  --output revision-report.json
```

Replay all revisions under the same current model:

```bash
python field_snapshot.py compare-revisions \
  snapshot-revision-1.json.gz.b64 \
  snapshot-revision-2.json.gz.b64 \
  --replay-commit current
```

A specific B101-or-later Git commit may be supplied instead of `current`.

## Hard comparison boundary

All compared snapshots must have:

- identical `place_id`,
- identical `forecast_valid_epoch` / `forecast_valid_at`.

Snapshots from different forecast-valid hours are rejected rather than compared
as revisions.

## What B106 compares

For each revision, the report records:

- snapshot ID,
- capture time,
- forecast-valid time,
- lead time to forecast validity,
- full Git commit,
- model-contract versions,
- camera raw provider payload fingerprint,
- spatial raw provider payload fingerprint,
- normalized selected-row fingerprint,
- selected forecast metrics,
- stable Opportunity outcomes.

Selected metrics currently include:

- visibility,
- low / mid / high cloud,
- RH,
- precipitation,
- wind,
- temperature,
- dew point,
- estimated LCL,
- sun elevation.

Opportunity comparison includes the stable fields already used by B104 replay:

- score,
- condition state,
- confidence,
- runtime eligibility,
- temporal eligibility,
- runtime reason,
- directional-mist negative-evidence state,
- spatial mist support / clear-sector diagnostics.

## Revision classifications

B106 deliberately distinguishes multiple kinds of change.

### `forecast_data_revision`

The selected normalized forecast row changed while the model contract remained
the same.

### `mixed_forecast_and_model_contract_revision`

Both normalized forecast input and the declared scoring/runtime contract changed.

### `model_contract_revision_only`

The selected forecast input stayed the same but the declared model contract
changed.

### `provider_payload_revision_without_selected_input_change`

Raw camera and/or spatial provider payload changed, but the selected normalized
forecast row did not.

This is important because an Open-Meteo response can change elsewhere in the
forecast horizon without changing the exact hour being scored.

### `code_commit_revision_without_selected_input_or_model_contract_change`

Git commit changed, but neither the selected normalized row nor the model
contract changed.

This prevents UI/docs/weather-data commits from being mislabeled as scoring
model revisions.

### `no_revision_detected`

No compared layer changed.

## Model-contract identity

B106 does not treat a different Git SHA as proof that the scoring model changed.

The model-contract comparison currently includes:

- adapter version,
- canonical catalog schema version,
- Opportunity runtime version,
- spatial weather version.

Full Git commit is still retained for exact reproducibility.

For stronger isolation, `--replay-commit` evaluates every forecast revision
through the same target checkout.

## Registry-driven revision CI

Workflow:

`.github/workflows/test_field_snapshot_revisions.yml`

The workflow reads `field_snapshot_baselines_r4_2.json`, groups entries by:

`place_id + forecast_valid_at`

and automatically compares every group containing two or more revisions.

No workflow edit is required when a third, fourth, or later revision is added.

Each report is preserved as a CI artifact.

## First real revision group — Qingshui 06:00

Place:

`tw-034`

Forecast valid time:

- UTC: `2026-09-28T22:00:00+00:00`
- local: `2026-09-29 06:00 +08:00`

### Revision 1

Snapshot:

`FVS-TW-034-20260928-173805`

Captured:

`2026-09-28T17:38:05.029841+00:00`

Lead time to forecast validity:

15,714 seconds, about 4 h 21 m 54 s.

Production commit:

`808a585ba2c3f087c6d49a60d6a3d1bcb39ca9e6`

### Revision 2

Snapshot:

`FVS-TW-034-20260928-181202`

Captured:

`2026-09-28T18:12:02.957254+00:00`

Lead time to forecast validity:

13,677 seconds, about 3 h 47 m 57 s.

Production commit:

`560db8c542989bedf9688a3c3d60667751a9df4e`

Capture interval:

2,037 seconds, about 33 m 57 s.

## Actual B106 comparison result

Classification:

`provider_payload_revision_without_selected_input_change`

The raw provider payload fingerprints changed:

- camera raw payload: changed,
- spatial raw payload: changed.

However the selected 06:00 normalized input fingerprint remained exactly the
same:

`1206e6bc124ce989a95b8f052c6d2a96e425b40bf3d75787dbf5507bfc30ebd6`

Therefore `metric_changes = {}`.

The selected 06:00 values remained:

| Metric | Revision 1 | Revision 2 |
| --- | ---: | ---: |
| Visibility | 3.56 km | 3.56 km |
| Low cloud | 5% | 5% |
| Mid cloud | 1% | 1% |
| High cloud | 0% | 0% |
| RH | 66% | 66% |
| Precipitation | 0 mm | 0 mm |
| Wind | 1.1 m/s | 1.1 m/s |
| Temperature | 22.2 °C | 22.2 °C |
| Dew point | 15.5 °C | 15.5 °C |
| Estimated LCL | 837 m AGL | 837 m AGL |
| Sun elevation | 2.7° | 2.7° |

The model-contract versions were also unchanged:

- adapter: `v0.04-r4.2-canonical-r34-denali-mountain-vista-access`,
- catalog: `v0.04-r4.2-canonical-1`,
- runtime: `opportunity-runtime-r17-b88-qingshui-mist-cap`,
- spatial: `spatial-weather-r8-qingshui-negative-evidence`.

The Git commit changed, but that commit difference did not represent a declared
Qingshui scoring-contract change.

## Opportunity result

Recorded Opportunity outcomes were unchanged:

### P01

- 64 / low,
- `partial_runtime_contract`.

### P02

- 54 / medium,
- `minimum_sufficient_conditions_miss`,
- reason `visibility_too_low`.

### P03

- 54 / medium,
- `minimum_sufficient_conditions_miss`,
- reason `low_visibility_without_mist_support`,
- six spatial target samples,
- zero mist targets,
- zero directional-mist targets,
- zero clear targets,
- `broad_clear_target_sector = false`,
- `directional_mist_negative_evidence = false`.

Recorded Opportunity changes:

`{}`

## Common-model replay result

Both forecast revisions were also replayed through the same B106 PR model commit.

Result:

- P01 unchanged,
- P02 unchanged,
- P03 unchanged,
- common-model Opportunity changes: `{}`.

This demonstrates that the raw provider response changed while the exact 06:00
model input and decision remained stable.

## Interpretation

B106 prevents a false conclusion such as:

> "The provider response changed, therefore the 06:00 photography forecast
> changed."

For this real case that statement would be incorrect.

The provider payload was revised, but the selected 06:00 forecast row was not.
ChaseLights correctly produced the same P01/P02/P03 result.

A later capture may produce a true `forecast_data_revision`. When that happens,
B106 will identify the exact changed normalized metrics and the resulting
Opportunity deltas.

## Ground-truth boundary

Both snapshots remain:

- forecast evidence only,
- `observation.status = unreviewed`,
- not photographs,
- not field observations,
- not entries in `field_validation_registry_r4_2.json`.

Forecast revision comparison and field validation are separate evidence layers.

## Runtime impact

None.

B106 adds snapshot analysis tooling and CI only. It does not modify:

- Qingshui thresholds,
- Opportunity scoring formulas,
- spatial mist thresholds,
- weather normalization,
- UI behavior.
