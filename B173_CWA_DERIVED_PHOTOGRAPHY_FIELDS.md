# B173 — CWA WRF Derived Photography Diagnostics for WeatherGrid V2

Date: 2026-10-07  
Status: experimental V2 contract

## Goal

Use raw fields already present in the CWA WRF 3 km public GRIB feed to create
photography-oriented diagnostic maps in WeatherGrid V2 without pretending that
CWA publishes native low/mid/high cloud fraction.

This batch is V2-only for presentation and validation. It does not change
Photography Opportunity scoring.

## Raw inputs

The model consumes:

- 2 m temperature
- 2 m relative humidity
- 10 m wind speed derived from U/V
- pressure-level relative humidity at 1000/925/850/700/500/400/300 hPa

The pressure-level RH fields are retained in the compact CWA browser bundle so
the derived result can be audited against its inputs.

## Derived products

### Low-layer cloud presence potential

Input band: 925 and 850 hPa RH.

The maximum RH in the band is mapped linearly:

- RH <= 70% -> 0
- RH >= 95% -> 100
- values between are linearly scaled

Name: `rh_cloud_potential_low_percent`.

### Middle-layer cloud presence potential

Input band: 700 and 500 hPa RH. Uses the same transparent RH transfer.

Name: `rh_cloud_potential_mid_percent`.

### High-layer cloud presence potential

Input band: 400 and 300 hPa RH. Uses the same transparent RH transfer.

Name: `rh_cloud_potential_high_percent`.

### LCL height estimate

Dew point is estimated from 2 m temperature and RH with the Magnus relation.
LCL height is then approximated as:

`125 m/K * (T - Td)`

and clipped to 0–6000 m AGL.

Name: `lcl_height_m_agl`.

This is a thermodynamic LCL estimate, not observed cloud base and not a native
CWA cloud-base field.

### Near-surface fog potential

The first experimental fog diagnostic combines:

- 40% surface saturation term from 2 m RH
- 30% low-LCL term
- 20% low-layer RH cloud potential
- 10% calm-wind term

Name: `fog_potential_percent`.

It is a diagnostic index, not visibility and not a calibrated probability.

## Naming guardrail

The derived RH products MUST NOT be exported as:

- `cloud_cover`
- `cloud_cover_low`
- `cloud_cover_mid`
- `cloud_cover_high`

Those names remain reserved for provider-native cloud-cover/fraction products.

Every derived field carries:

- `product_type=derived_proxy`
- `calibration_status=experimental_unvalidated`
- `native_cloud_fraction=false`
- explicit `derived_from` metadata

## WeatherGrid V2

CWA is a published-tile-only V2 provider. There is no external browser point-API
fallback for these proprietary derived names.

Initial V2 layers:

- CWA low/mid/high RH cloud potential
- CWA LCL cloud-base estimate
- CWA fog potential
- CWA pressure-level RH inspection layers

Auto selects CWA only for CWA-specific fields while the viewport is in Taiwan.
Existing GFS global cloud behavior remains unchanged.

## Validation policy

The first purpose of these maps is comparison against field photography,
Himawari cloud observations, visibility observations and later replay datasets.
Thresholds must remain visibly experimental until sufficient validation exists.

Map diagnostics do not become Photography Opportunity scoring inputs merely by
being displayed in WeatherGrid V2.
