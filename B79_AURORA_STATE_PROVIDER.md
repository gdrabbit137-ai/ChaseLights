# ChaseLights R4.2 B79 — NOAA OVATION Aurora State Runtime

Date: 2026-09-28 (Asia/Taipei)

## Goal

Implement the canonical `aurora_state` dependency without reusing the legacy planetary Kp score as a location-specific aurora guarantee.

B79 connects NOAA Space Weather Prediction Center (SWPC) OVATION short-horizon aurora output to the researched Alaska Camera Zones.

## Authoritative provider

Official NOAA SWPC sources:

- Aurora 30 Minute Forecast:
  https://www.spaceweather.gov/products/aurora-30-minute-forecast
- OVATION latest JSON:
  https://services.swpc.noaa.gov/json/ovation_aurora_latest.json
- Alternate NOAA service host:
  https://services.swpc.woc.noaa.gov/json/ovation_aurora_latest.json

NOAA describes OVATION as a short-term forecast of aurora location and intensity with roughly 30–90 minutes of lead time.

ChaseLights therefore treats one OVATION frame as a short-horizon local signal only. It is not stretched across the multi-day weather forecast.

## Canonical boundary

Planetary Kp remains available as legacy/context weather metadata, but:

- Kp is **not** a canonical `aurora_state` fallback.
- Kp does **not** determine canonical aurora eligibility.
- Kp factors are removed from canonical aurora Opportunity scoring explanations.
- Canonical aurora scores use the local OVATION grid value plus darkness/cloud gates.
- Provider failure remains fail-closed.
- A positive OVATION result is a forecast signal, not a promise that an observer will visually see or successfully photograph aurora.

## Provider mechanics

New module:
- `aurora_state.py`

Provider behavior:
- primary endpoint: `services.swpc.noaa.gov`
- alternate NOAA endpoint: `services.swpc.woc.noaa.gov`
- provider is fetched/indexed once per weather-generation process,
- failure is cached so Alaska Places do not repeatedly hammer a failing provider,
- no provider response causes a Kp fallback,
- nearest surrounding 1-degree OVATION grid cell is used for the Camera Zone,
- local grid sampling is valid only within ±90 minutes of the OVATION Forecast Time.

The provider coordinate is the researched Place / Camera Zone weather coordinate already carried by the canonical spot adapter. It is not a navigation or transport endpoint.

## Aurora eligibility contract

A canonical aurora Opportunity can match only when all of the following are true:

1. a current local OVATION sample is available,
2. the target weather hour is within the short OVATION validity window,
3. astronomical data is available,
4. solar elevation is at or below -12 degrees,
5. low/mid/high cloud data is present,
6. cloud cover does not exceed the conservative sky-blocking thresholds,
7. the local OVATION value meets the minimum activity gate.

B79 uses:
- minimum local OVATION value: 10
- low-cloud block: >=70%
- mid-cloud block: >=80%
- high-cloud block: >=90%

These are product runtime thresholds, not claims that NOAA guarantees photography success.

## Scoring boundary

For canonical aurora Opportunities:

- the old Theme Kp baseline may remain in compatibility payloads,
- it does not influence the canonical Opportunity score,
- an eligible local OVATION result supplies the aurora score hint,
- Kp-related explanation factors are removed,
- the user-facing factor instead identifies the local NOAA OVATION signal,
- provider-missing / condition-miss cases do not gain score from high Kp.

## Opportunities affected

There are 12 canonical Opportunities requiring `aurora_state`.

### Fully runtime-ready after B79: 6

These depend only on `aurora_state` and move from `module_pending` to `preview_module_available`:

- us-042-P01 Fairbanks / Creamer's Field
- us-043-P01 Chena Hot Springs
- us-044-P02 Anchorage / Point Woronzof
- us-058-P02 Nome
- us-065-P02 Anchorage Hillside / Glen Alps
- us-069-P02 Lake Clark / Port Alsworth

### Still module-pending: 6

These gain a ready `aurora_state` component but still require unresolved `dynamic_access`:

- us-041-P02 Denali / Mountain Vista
- us-046-P02 Hatcher Pass
- us-056-P02 Dalton Highway / Atigun Pass
- us-057-P02 Arctic Circle Wayside
- us-066-P02 Bering Land Bridge / Serpentine
- us-068-P02 Noatak River

Good OVATION/weather conditions must not override road, air-taxi, park-road or remote-transport constraints.

## Expected runtime-policy delta

Before B79:
- module_pending: 128
- preview_module_available: 114
- minimum_sufficient_available: 133

After B79:
- module_pending: 122
- preview_module_available: 120
- minimum_sufficient_available: 133

Other policy counts remain unchanged:
- prototype_pending_certification: 2
- hold: 2
- data_insufficient: 2

Canonical catalog content counts remain unchanged:
- 188 Places
- 381 Opportunities
- 396 Condition Variants
- 387 viewpoint relations

## CI / production behavior

B79 adds `aurora_state.py` to:
- Adapter path filters and compile coverage,
- US Candidate Weather,
- Browser Smoke,
- production weather update triggers,
- B67 weather-impact classification as a US weather input.

Provider/parser tests cover:
- OVATION time parsing,
- longitude normalization,
- nearest local grid sampling,
- short-horizon expiration,
- darkness gate,
- cloud blocking,
- local activity threshold,
- explicit no-Kp-fallback behavior,
- Kp-invariant canonical scoring.

## Failure behavior

If NOAA OVATION is missing, stale/outside the short validity window, blocked by an upstream challenge, malformed, or otherwise unavailable:

- weather generation continues,
- `aurora_state` reports unavailable,
- canonical aurora Opportunity remains fail-closed / runtime-data-missing for that hour,
- ChaseLights does not substitute planetary Kp.

This failure mode is intentional.
