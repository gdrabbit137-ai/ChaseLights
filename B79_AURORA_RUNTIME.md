# ChaseLights R4.2 B79 — Location-aware Aurora Runtime Preview

Date: 2026-09-27 (Asia/Taipei)

## Goal

Implement the first canonical `aurora_state` runtime provider without weakening the fail-closed rules introduced by B72.

B79 does **not** use planetary Kp as proof that aurora is photographable at a specific Camera Zone. Kp remains compatibility/context data only.

## Authoritative provider

NOAA / NWS Space Weather Prediction Center (SWPC):

- Product: Aurora - 30 Minute Forecast
  - https://www.spaceweather.gov/products/aurora-30-minute-forecast
- Grid JSON:
  - https://services.swpc.noaa.gov/json/ovation_aurora_latest.json

NOAA describes OVATION as a short-term forecast of aurora location and intensity, normally with a 30–90 minute lead time. The product uses solar-wind / IMF input and can fall back to current Kp forcing when those inputs are unavailable.

The JSON grid exposes:
- Observation Time
- Forecast Time
- Data Format
- one-degree-ish longitude / latitude / Aurora grid values

## Canonical modeling boundary

The new `aurora_state` module is location-aware and Camera-Zone-specific.

For each canonical aurora Opportunity:

1. use the researched Place / weather anchor for the actual Camera Zone,
2. sample the nearest NOAA OVATION grid cell,
3. accept the sample only for the nearest hourly weather row within 45 minutes of NOAA's published `Forecast Time`,
4. reject stale / malformed / missing provider data,
5. require astronomical data,
6. require Sun elevation <= -12 degrees,
7. combine the local OVATION signal with local low/mid/high cloud cover,
8. never report the result as guaranteed visible aurora.

B79 deliberately does **not** extrapolate the single latest OVATION grid across the whole multi-day weather forecast.

## Provider validity

Fail closed when:
- payload is malformed,
- Observation Time / Forecast Time is missing,
- the coordinate grid is missing,
- the provider forecast is stale,
- the target weather hour is outside the short OVATION horizon,
- the local grid cell cannot be sampled,
- astronomy data is missing,
- local cloud data is missing.

The runtime result always publishes:
- `visibility_guaranteed: false`
- provider timestamps
- sampled grid coordinate
- OVATION model value
- local cloud state
- solar elevation
- confidence hint

## Conservative preview thresholds

Initial preview profile:

- minimum local OVATION value: 5
- maximum Sun elevation: -12 degrees
- low cloud <= 50%
- mid cloud <= 65%
- high cloud <= 80%

These are preview gating thresholds, not a scientific claim that a given OVATION value corresponds to an exact human-visible probability.

A higher model value can increase confidence, but the system still avoids promising that aurora will be seen or photographed.

## Canonical Opportunities covered

The explicit `AURORA_STATE_PROFILES` registry contains all current canonical aurora-state Opportunities:

- us-041-P02 Denali / Mountain Vista
- us-042-P01 Fairbanks / Creamer's Field
- us-043-P01 Chena Hot Springs
- us-044-P02 Anchorage / Point Woronzof
- us-046-P02 Hatcher Pass
- us-056-P02 Brooks Range / Atigun Pass
- us-057-P02 Arctic Circle Wayside
- us-058-P02 Nome
- us-065-P02 Chugach / Glen Alps
- us-066-P02 Bering Land Bridge / Serpentine
- us-068-P02 Noatak River
- us-069-P02 Lake Clark / Port Alsworth

New Place/theme tags do not automatically enter this registry.

## Dynamic-access separation

B79 only resolves the `aurora_state` component.

Aurora Opportunities that also require `dynamic_access` remain `module_pending` until their profile-specific authoritative access provider is connected.

Examples:
- Denali Park Road
- Hatcher Pass
- Dalton Highway / Atigun Pass
- Arctic Circle Wayside
- Serpentine remote transport
- Noatak remote transport

Good aurora conditions must never override those access requirements.

## Runtime policy delta

Before B79:
- module_pending: 128
- preview_module_available: 114
- minimum_sufficient_available: 133
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

After B79:
- module_pending: 122
- preview_module_available: 120
- minimum_sufficient_available: 133
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

The six aurora-only profiles become preview-module-ready:
- us-042-P01
- us-043-P01
- us-044-P02
- us-058-P02
- us-065-P02
- us-069-P02

The six aurora + dynamic-access profiles remain module-pending because access is still unresolved.

## Implementation

New:
- `aurora_state.py`

Updated:
- `fetch_data.py`
  - fetch NOAA OVATION once per generator process,
  - cache provider failure,
  - attach only short-horizon local samples to runtime item data.
- `opportunity_runtime.py`
  - register `aurora_state` as implemented,
  - add evaluator and registry validation.
- `runtime_dependencies.py`
  - advance dependency inventory version.
- `runtime_catalog_manifest_r4_2.json`
  - update runtime-policy expected counts.
- `test_opportunity_adapter.py`
  - exact registry coverage,
  - parsing / nearest-cell / freshness / horizon tests,
  - darkness / cloud / weak-signal fail-closed tests,
  - updated Alaska runtime-policy expectations.

## Explicit non-goals

B79 does not:
- remove the legacy Kp fields from generated weather,
- turn Kp into the canonical aurora gate,
- promise visible aurora,
- model terrain horizon obstruction,
- model local artificial light extinction,
- extend OVATION beyond its short provider horizon,
- resolve remote-road / transport access,
- create a multi-day aurora forecast.

Those remain separate future work.
