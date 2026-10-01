# B170a Photography Transparency Diagnostic

Date: 2026-10-01

B170a introduces a versioned **diagnostic-only** transparency index for replay. It does not change Photography Opportunity scores.

Inputs:
- horizontal visibility;
- CAMS AOD 550 nm;
- CAMS PM2.5;
- relative humidity;
- temperature/dew-point spread when available.

The formula is deliberately labeled `b170a-heuristic-1` and `uncalibrated`. Visibility is required; at least one additional environment component is required. Missing inputs cause lower confidence rather than fabricated values.

The initial formula uses explicit piecewise planning anchors and weighted components (visibility 50%, aerosol 30%, moisture 20%, renormalized over available components). Aerosol uses the more restrictive of AOD and PM2.5 when both are available; moisture uses the more restrictive of RH and dew-point spread.

Scientific rationale is limited to directionality: aerosol loading and humidity both affect extinction/visibility, and high humidity can enhance aerosol scattering. The numeric anchors are **not** claimed as a published physical retrieval model and must be calibrated with ChaseLights replay/field data before any scoring use.

References:
- Deng et al. (2016), Impact of relative humidity on visibility degradation during a haze event, Science of the Total Environment.
- Liu et al. (2024), Visibility-derived aerosol optical depth over global land from 1959 to 2021, Earth System Science Data.
- Taiwan visibility/fog/haze literature already tracked in the ChaseLights research process.

Next gate: replay the index against clear/fog/haze/mixed field snapshots, then decide whether B170b should remain informational or influence specific long-range photography Opportunities.
