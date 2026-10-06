# B174 — CWA Low-Cloud Calibration Against Himawari-9

Date: 2026-10-07  
Status: calibration framework; production formula unchanged

## Purpose

Calibrate the experimental CWA WRF low-layer RH cloud-presence diagnostic
against time-matched Himawari-9 observations without confusing satellite cloud
top with a vertically resolved low/mid/high cloud analysis.

This specification does **not** authorize an automatic model change. It creates
a repeatable evidence gate for a later CWA low-cloud v2.

## Why calibration is needed

The B173 v1 low-layer diagnostic uses:

- feature: `max(RH925, RH850)`
- 70% RH -> 0 potential
- 95% RH -> 100 potential

An exploratory exact-time comparison at 2026-10-06 18:00 UTC showed that the
v1 diagnostic had high low-cloud sensitivity but poor clear-sky specificity.
In the same comparison, requiring agreement between the two pressure levels
(`min` or `mean` RH) separated the observational labels better than the
single-layer maximum. This is motivation for calibration, not enough evidence
to replace B173.

## Observation label

For each CWA valid time, B174 retrieves the exact 10-minute Himawari slot from
the existing JMA/NOAA NODD archive.

Primary low-cloud ceiling: **3700 m cloud-top height**, matching the approximate
upper bound already documented for the GFS low-cloud layer.

Labels:

- **positive / observed low cloud**: cloud mask = cloudy and cloud-top height
  <= 3700 m;
- **negative / clear**: cloud mask = clear;
- **ambiguous / excluded**: cloudy with cloud top > 3700 m or unavailable
  cloud-top retrieval.

A high cloud top cannot prove that no lower cloud deck exists beneath it.
Therefore high-cloud pixels are never used as negative low-cloud labels.

## Alignment

Himawari cloud mask and cloud-top height are resampled directly to the regular
CWA browser grid with the existing nearest-neighbour + distance-QC path.

The calibration fails if p99 nearest-neighbour distance exceeds the established
5 km Himawari WeatherGrid QC bound.

## Candidate family

B174 deliberately starts with transparent RH-only candidates so improvements
are attributable and debuggable:

1. `max(RH925, RH850)` — B173 baseline feature
2. `min(RH925, RH850)` — both levels must support moisture
3. `mean(RH925, RH850)` — layer-average moisture

For each feature the calibration searches a bounded linear transfer:

- lower RH threshold: 55–90%
- upper RH threshold: max(75%, lower+5%)–100%
- objective: minimum Brier score on training valid times

No opaque fitted model is introduced in this batch.

## Time holdout

The newest observed CWA valid time is never used to fit thresholds. It is kept
as a temporal holdout.

At least two independent valid times are required to produce a calibration
report.

## Promotion gate

A candidate is only **eligible for model review** after at least six independent
CWA/Himawari valid times and all holdout conditions pass:

- Brier score improves by >= 0.02 absolute;
- clear-sky specificity improves by >= 0.15 absolute;
- balanced accuracy improves by >= 0.05 absolute;
- low-cloud sensitivity remains >= 0.50.

Passing the gate still does not change production automatically. A model/spec
change and regression tests are required.

## Continuous evidence

The calibration workflow runs after a successful live WeatherGrid refresh and
can also run manually. It uploads the full JSON report as a retained CI
artifact.

The workflow intentionally does not commit a new calibration result every run;
the WeatherGrid raw-data refresh already generates frequent data commits and the
calibration artifact is evidence, not a production input.

## Scope guardrails

- B174 only calibrates the CWA **low-layer** diagnostic.
- Himawari cloud-top height is not used to infer middle/high cloud absence.
- Fog calibration remains separate because visibility/near-surface
  observations are required.
- Photography Opportunity scoring is unchanged.
