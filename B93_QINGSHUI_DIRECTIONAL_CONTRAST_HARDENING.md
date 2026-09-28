# B93 — Qingshui Directional Mist Contrast Hardening

Date: 2026-09-28 (Asia/Taipei)

## Why this follow-up exists

B92 verified the effective B81/B82/B87/B88 transition contract, including:

- low-visibility non-whiteout fallback at 68 / low confidence,
- the 330° / 0° / 30° × 2.5 / 5.0 km proxy layout,
- afternoon exclusion,
- clear-visibility recovery back to P02.

During B93 review, one B82 implementation gap remained.

The directional evaluator treated a target `weather_code` 45/48 as directional contrast by itself. That meant camera and target could both report the same fog code and nearly identical visibility / low-cloud / RH values, yet the target could still be counted as “directionally mistier”.

That contradicts the B82/B92 camera-vs-sector contract.

## Corrected contract

A target fog code may supply directional contrast by itself only when the camera grid is **not** also reporting fog.

If both camera and target report fog code 45/48, the target must still be materially different by at least one existing contrast rule:

- target visibility <= 75% of camera visibility, or
- target low-cloud cover >= camera + 25 percentage points, or
- target RH >= camera + 8 percentage points.

If none applies, the spatial module returns:

- `eligible = false`
- `reason = directional_mist_not_distinguished_from_camera`

This does not erase local B81 mist evidence. It only prevents broad regional fog from being mislabeled as stronger fog specifically toward the cliff sector.

## Regression coverage

B93 adds tests that:

1. each 330° / 0° / 30° bearing can independently create directional context when one of its 2.5 km samples is materially mistier than a clear camera;
2. identical fog code and atmospheric state at camera and all six targets does **not** create directional contrast;
3. the existing B92 transition tests remain unchanged and continue to cover the 0.8 km low-confidence fallback and later P02 recovery.

## Evidence boundary

The directional grid remains an environmental proxy only. It does not establish exact fog position, exact cliff intersection, or on-site observation.

The 2026-09-28 0.7–0.8 km Qingshui case remains a regression/calibration scenario rather than registered Qingshui field ground truth. See `B92_QINGSHUI_B81_B82_REGRESSION.md`.
