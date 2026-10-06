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
- primary objective: maximum balanced accuracy on training valid times;
- secondary objective for equal balanced accuracy: minimum Brier score;
- tertiary tie-break: higher clear-sky specificity.

Balanced accuracy is primary because the calibration goal is specifically to
stop a high low-cloud base rate from rewarding an overcalling model. Brier
remains a required holdout gate, so probability-like calibration cannot be
sacrificed merely to improve the 50% classifier threshold.

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

To avoid losing evidence when the current compact bundle rolls to a new CWA
cycle, the workflow scans Git history for prior **B173-compatible** CWA browser
bundles. It retains distinct model cycles, merges their frames, and de-duplicates
identical valid times by choosing the shortest available forecast lead. This
lets independent valid times accumulate across refreshes without committing a
new calibration result on every run.

The workflow intentionally does not commit a new calibration result every run;
the WeatherGrid raw-data refresh already generates frequent data commits and the
calibration artifact is evidence, not a production input.

## First live calibration result

The first successful time-holdout run used:

- training valid time: 2026-10-06 12:00 UTC;
- holdout valid time: 2026-10-06 18:00 UTC;
- 33,148 holdout labelled cells after ambiguity filtering.

B173 baseline on the holdout:

- Brier: 0.206218
- sensitivity: 0.860805
- specificity: 0.534732
- balanced accuracy: 0.697768

A Brier-first exploratory fit widened the same `max(RH925,RH850)` transfer to
67% -> 0 and 100% -> 100. On holdout it reached Brier 0.188075, sensitivity
0.841190, specificity 0.575253 and balanced accuracy 0.708222. This showed a
real calibration improvement but still failed every promotion-improvement gate.

The candidate selector was subsequently tightened to prioritize **training
balanced accuracy first**, then Brier and specificity, because the main failure
mode being corrected is false low-cloud overcalling. Production B173 remains
unchanged until the multi-slot holdout gate passes.

## Scope guardrails

- B174 only calibrates the CWA **low-layer** diagnostic.
- Himawari cloud-top height is not used to infer middle/high cloud absence.
- Fog calibration remains separate because visibility/near-surface
  observations are required.
- Photography Opportunity scoring is unchanged.
