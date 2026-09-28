# B99 — Qingshui Field-Validation Intake Contract

Date: 2026-09-28 (Asia/Taipei)

## Purpose

Prepare ChaseLights to admit real Qingshui Cliff field-validation cases without forcing them into the Qixingtan-specific observation schema.

This batch changes validation infrastructure only. It does **not** add Qingshui ground truth and does not change Qingshui scoring thresholds.

## Problem found after B98

The original field-validation registry validator was structurally tied to the first Qixingtan case. It required fields such as:

- `northward_mountain_layers_readable`
- `terrain_attached_cloud_band_visible`
- `ridge_partially_visible`
- `northward_elevated_sector`

Those fields are appropriate for Qixingtan P03/P04, but they are not the right observation contract for Qingshui Cliff morning mist.

Adding a Qingshui case under that schema would either fail validation or require misleading Qixingtan-shaped fields.

## B99 change

Registry schema is bumped from:

- `field-validation-registry-r4.2-1`

to:

- `field-validation-registry-r4.2-2`

The registry now contains data-driven `case_profiles`.

Each case declares a `validation_profile`, and the validator reads the required scene fields from that profile.

### Existing Qixingtan profile

`qixingtan_northward_mountain_cloud`

The existing case `FV-TW-036-20260928-1300-01` is preserved and tagged with this profile. Its observation and forecast semantics do not change.

### New Qingshui intake profile

`qingshui_cliff_mist`

Required observed booleans:

- `camera_whiteout`
- `coast_and_sea_readable`
- `cliff_or_mountain_outline_readable`
- `mist_or_low_cloud_visible_in_cliff_sector`
- `precipitation_visible`

Required captured camera diagnostics:

- `visibility_km`
- `low_cloud_pct`
- `rh_pct`
- `lcl_agl_proxy_m`
- `weather_code`

Required spatial object:

- `northward_mist_sector`

Required numeric spatial diagnostics:

- `target_sample_count`
- `mist_target_count`
- `directional_mist_target_count`
- `clear_target_count`
- `clear_bearing_count`

Required boolean spatial diagnostics:

- `available`
- `eligible`
- `broad_clear_target_sector`

These fields match the current Qingshui directional-mist / negative-spatial-evidence runtime diagnostics closely enough to preserve provenance without claiming exact fog/cliff overlap.

## Ground-truth boundary

B99 intentionally leaves the registry at **one admitted case**: the existing Qixingtan observation.

The presence of `qingshui_cliff_mist` means only that ChaseLights now knows how to validate a future Qingshui case. It does not mean:

- Qingshui mist was observed,
- the 2026-09-28 low-visibility regression row was field truth,
- the proxy grid proves fog was on the cliff,
- the current thresholds are field calibrated.

## Recommended Qingshui case set

Before changing the current thresholds, collect multiple cases spanning at least:

1. visible morning mist around the cliff while cliff/coast remain readable,
2. low camera visibility but broad-clear north-sector evidence and no visible cliff mist,
3. dense camera fog / whiteout where the composition is unreadable,
4. clear recovered visibility where P02 should beat P03,
5. if available, an ambiguous narrow fog ribbon not well represented by the proxy grid.

Prefer paired positive and negative observations over tuning from one successful image.

## Runtime impact

None expected. B99 changes field-validation schema/integrity checks and regression coverage only. Qingshui scoring logic remains the PR #174 contract recorded in B98.
