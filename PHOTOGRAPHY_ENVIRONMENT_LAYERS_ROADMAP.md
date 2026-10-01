# Photography Environment Layers Roadmap

Date: 2026-10-01

## Purpose

Extend WeatherGrid from meteorological fields into photography-specific
environment layers. These layers remain source-aware: they do not pretend to
come from JMA MSM, CWA WRF, ICON or GFS when the underlying provider is
different.

## Planned batches

| Batch | Layer / capability | Primary use |
| --- | --- | --- |
| B166 | AOD 550 nm / haze | atmospheric haze and long-distance clarity |
| B167 | PM2.5 | near-surface particulate burden |
| B168 | fog-vs-haze classification | distinguish photographic fog from polluted/dusty low visibility |
| B169 | VIIRS nighttime lights | static/nightly artificial-light radiance context; do not label as Bortle |
| B170 | photography transparency | derived clarity signal from visibility + AOD + PM2.5 + RH + dew-point spread |

## Architecture rules

1. Provider provenance stays explicit.
2. A presentation grid or interpolation must never be described as native
   resolution.
3. Raw/environment fields land in WeatherGrid before they influence scoring.
4. Derived photography products keep their inputs and formula version so they
   can be replayed.
5. Observation, forecast and mostly-static layers keep distinct time semantics.
6. Licensing and attribution are part of each provider contract.
7. Global support is required; Taiwan may add higher-resolution validation
   sources without changing the global field meaning.

## Fog / haze direction

B168 will not use low visibility alone.

Candidate evidence for fog:
- high relative humidity;
- small temperature/dew-point spread;
- reduced visibility;
- compatible low-cloud / near-surface moisture evidence.

Candidate evidence for haze:
- elevated AOD and/or PM2.5;
- reduced visibility;
- weaker saturation evidence than a fog case.

The exact classifier thresholds are intentionally deferred until B166/B167
fields have live samples and replay fixtures.

## Night-light direction

B169 will call VIIRS/Black Marble radiance **nighttime lights**. Satellite
upward radiance is not the same thing as zenith sky brightness or a Bortle
class. A later skyglow model may combine night lights, terrain and atmospheric
scattering inputs.

## Commercial-readiness guardrail

The current project may use Open-Meteo's free non-commercial endpoint for
prototype/live validation. Before ChaseLights adds subscriptions, advertising,
or another commercial use, provider access must be switched to a commercial
licence or a self-hosted/open-data path without changing the WeatherGrid field
contract.
