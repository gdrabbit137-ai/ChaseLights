# B93 — Qingshui Directional Mist Relative-Contrast Hardening

Date: 2026-09-28 (Asia/Taipei)

## Why B93 exists

B92 already verified the effective B81/B82/B87/B88 state transitions, including:

- low-visibility non-whiteout -> low-confidence P03 fallback,
- no directional contrast -> no spatial promotion,
- afternoon rejection,
- visibility recovery -> P02 can win again.

A follow-up audit found one narrower B82 implementation bug that the B92 negative case did not exercise.

## Bug

In `_evaluate_directional_mist_sector()`, a target `weather_code in {45, 48}` was itself treated as `directional_contrast`.

That is valid when the camera is not fog-coded. It is not valid when the camera and target are both fog-coded with otherwise equivalent visibility, RH, and low cloud.

Before B93, a uniform non-whiteout fog field could therefore be mislabeled as “north sector materially mistier than the camera” and promote P03 to the directional 88-point state.

## B93 contract

For `tw-034-P03`:

- target fog code 45/48 + camera not fog-coded -> fog code may establish directional contrast;
- camera and target both fog-coded -> fog code alone is not directional contrast;
- when both are fog-coded, at least one relative contrast is still required:
  - target visibility <= camera visibility × 0.75, or
  - target low cloud >= camera low cloud + 25 percentage points, or
  - target RH >= camera RH + 8 percentage points.

Uniform fog can still support the local P03 mist contract. It simply cannot be upgraded by B82 unless the north-sector proxy is materially different from the camera.

## Regression additions

`test_opportunity_adapter.py` now additionally verifies:

1. each 330° / 0° / 30° bearing can independently provide a positive directional signal;
2. equal non-whiteout fog at camera and all six proxy points returns `directional_mist_not_distinguished_from_camera`;
3. that uniform-fog case remains local `coastal_cliff_light_mist_supported` at score hint 82 rather than becoming directional 88;
4. a valid B82 directional signal at 14:00 still returns `outside_morning_mist_window`;
5. the B81 test comment matches the implemented contract: visibility-only may form a low-confidence candidate, while corroboration is required to strengthen it.

## What B93 does not change

- B81 subject admission;
- B87/B88 2.5 km camera-readability guard;
- B88 final score cap of 68 below that guard;
- camera whiteout veto;
- B92 winner-transition regression;
- the proxy interpretation as broad environmental context rather than exact fog/cliff geometry.

## 2026-09-28 data boundary

B92 established that the retained 2026-09-28 production snapshots do not preserve the 0.7–0.8 km low-visibility Qingshui row used during review. That row remains a calibration/regression scenario, not captured historical raw model input.

B93 therefore validates decision semantics, not the exact historical location of mist on 2026-09-28. A Qingshui field-validation case with captured raw multi-point inputs is still needed for true historical replay.
