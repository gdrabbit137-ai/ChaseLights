# B86 — Field Validation Registry

## Purpose

B86 adds a structured, machine-validated registry for real field observations that are useful for calibrating ChaseLights runtime behavior.

The first case is the 2026-09-28 13:00 Qixingtan north-facing photograph that drove B83–B85.

This registry is deliberately separate from the research-evidence registry:

- `runtime_evidence_registry_r4_2.json` answers **what Place-specific subjects are admitted**.
- `field_validation_registry_r4_2.json` answers **how the runtime behaved against an observed real scene**.

A field photo or field note does not bypass `RESEARCH_EVIDENCE_SPEC_R4_2.md`.

## Files

- `field_validation_registry_r4_2.json` — canonical structured field cases plus data-driven case-profile intake contracts
- `field_validation.py` — schema / integrity validator
- `test_opportunity_adapter.py` — catalog-reference, case-profile, and replay regression checks

## Case-profile contract

Schema `field-validation-registry-r4.2-2` separates the generic registry rules from scene-specific observation fields.

Each admitted case declares a `validation_profile`. The profile defines:

- required boolean fields in `observed_scene`,
- required numeric camera diagnostics,
- the scene-specific spatial-sector object name,
- required numeric and boolean spatial diagnostics.

A profile is **not** field evidence by itself. It only defines what must be captured before a case can be admitted as ground truth.

Current profiles:

- `qixingtan_northward_mountain_cloud` — used by the existing Qixingtan case.
- `qingshui_cliff_mist` — intake contract for future Qingshui morning-mist positive/negative cases; no Qingshui case is admitted yet.

## Privacy rule

User-supplied images are not committed by default.

The Qixingtan case stores:
- non-identifying structured observations,
- timestamp and camera direction supplied for the validation task,
- captured ChaseLights forecast diagnostics,
- expected Opportunity behavior,
- verification commits and limitations.

The photo itself is not stored in the repository.

Future public image storage requires explicit publication authorization metadata.

## Case FV-TW-036-20260928-1300-01

Observed scene:
- camera/coast not in whiteout,
- coast and sea readable,
- northward mountain layers readable,
- terrain-attached cloud band visibly present,
- ridge partially visible,
- no uniform overcast / visible precipitation.

Captured production snapshot after B85:
- camera visibility ~27 km,
- low cloud ~2%,
- LCL planning proxy ~699 m AGL,
- northward elevated minimum visibility ~5.6 km,
- elevated/camera visibility ratio ~0.21,
- elevated max low cloud ~24%,
- 3 terrain/LCL intersections across 2 bearings.

Expected model behavior:
- broad scene: `tw-036-P04` mountain-seascape should be a strong viable match,
- specific cloud subject: `tw-036-P03` must not be a hard false negative,
- a grid-unresolved P03 match may remain low confidence and is capped at 78 under B85.

## Validation rules

The validator checks:
- schema version,
- unique case IDs,
- offset-aware local timestamps,
- allowed observation source/publication states,
- required observed-scene booleans,
- numeric captured forecast fields,
- known Place / Opportunity references when supplied by tests,
- score ranges and low-confidence caps,
- verified states belonging to acceptable states,
- valid 40-character commit SHAs,
- captured-weather commit consistency,
- explicit limitations.

## Important boundary

The registry records historical snapshots. It must never make historical forecast values look current.

Threshold tuning should use both positives and negatives. Do not loosen a model from one successful field case alone.

Next useful cases for Qixingtan:
1. clear mountain with **no** attached cloud band,
2. attached cloud band with stronger direct grid signal,
3. mountain whiteout where P03/P04 should both reject,
4. local camera fog with distant scene unavailable,
5. mixed ridge visibility where P04 remains usable but P03 confidence varies.


## Qingshui intake requirements

A future `tw-034` case using `qingshui_cliff_mist` must include, at minimum:

- exact offset-aware local capture time and camera direction,
- structured visual observations for camera whiteout, coast/sea readability, cliff or mountain-outline readability, visible mist/low cloud in the cliff sector, and visible precipitation,
- captured camera visibility, low cloud, RH, LCL proxy, and weather code,
- captured north-sector spatial diagnostics including valid target count, mist target counts, clear target/bearing counts, and the `broad_clear_target_sector` flag,
- explicit expected behavior for the relevant Qingshui Opportunities,
- model/weather commit provenance and limitations.

Positive and negative cases should be collected before changing the current 2.5 km readability guard or broad-clear negative-evidence thresholds.
