# B175 — CWA low-cloud calibration against Himawari-9

Date: 2026-10-07  
Status: calibration/replay contract

## Purpose

Calibrate the experimental CWA WRF 3 km low-cloud presence proxy introduced in
B173 against time-matched Himawari-9 cloud observations.

This work remains WeatherGrid validation. It does not alter Photography
Opportunity scoring unless a later, separately reviewed change explicitly
promotes a calibrated product.

## Why calibration is needed

The B173 v1 proxy uses:

`max(RH925, RH850)`

with a linear transfer from 70% RH = 0 to 95% RH = 100.

The first exact-time comparison at 2026-10-06 18:00 UTC showed that this proxy
has high low-cloud sensitivity but poor clear-sky specificity. A single humid
pressure level is therefore too permissive.

## Observation labels

Himawari remains an observation source, not model cloud cover.

For low-cloud calibration:

- **positive**: observed cloud mask = cloudy AND retrieved cloud-top height
  <= 3700 m;
- **negative**: observed cloud mask = clear;
- **excluded/ambiguous**: cloudy pixel with cloud-top height > 3700 m or
  missing cloud-top retrieval.

The exclusion is mandatory. A high cloud top cannot prove that a lower cloud
deck is absent beneath it.

## Time matching

Calibration requires an exact CWA valid time / Himawari observation slot match
within one minute. Himawari replay therefore supports explicit 10-minute UTC
slots in addition to the normal latest-observation path.

## Spatial matching

Both sources are already published on regular lon/lat presentation grids.

CWA grid points are matched to the nearest Himawari browser-grid point.
This is calibration sampling only and does not claim higher source resolution.

## Metrics

Each snapshot records:

- Brier score, treating the 0-100 proxy as a bounded diagnostic scale;
- ROC AUC;
- sensitivity at 50;
- specificity at 50;
- balanced accuracy and confusion counts.

## Candidate v2 search

The candidate family tests layer consistency instead of maximum humidity:

- `min(RH925, RH850)`
- `mean(RH925, RH850)`
- mean RH minus 0.25 / 0.50 / 0.75 times the 925-850 hPa RH spread

The spread penalty targets a known v1 failure mode: one pressure level can be
very humid while the other remains substantially drier, yet `max(RH)` still
reports a strong low-cloud potential.

For each feature, the training snapshot(s) grid-search a transparent linear RH
transfer with lower endpoint 60-90% and upper endpoint 82-100%.

The newest snapshot is held out chronologically from fitting.

## Provisional promotion gate

A candidate may be marked eligible only when at least two exact-time snapshots
exist and the holdout snapshot shows all of:

- Brier improvement >= 0.015;
- specificity improvement >= 0.10;
- sensitivity loss <= 0.20;
- AUC does not decrease.

Passing this gate means the **current train/holdout pair** is provisionally
successful. It is not sufficient by itself for production promotion.

A separate longitudinal gate must also pass before the candidate is marked
**eligible for model review**. The calibration history must contain at least
six distinct validation slots. Over the most recent six distinct slots, the
median results must satisfy:

- Brier improvement >= 0.015;
- specificity improvement >= 0.10;
- sensitivity loss <= 0.20;
- AUC change >= 0.

The longitudinal gate only permits model review. It never changes production or
Photography Opportunity scoring automatically.

## First calibration evidence

At the exact 2026-10-06 18:00 UTC CWA/Himawari match, using the conservative
3700 m low-cloud label:

- usable unambiguous collocations: 19,671;
- v1 AUC: about 0.71;
- v1 sensitivity at 50: about 0.87;
- v1 specificity at 50: about 0.31;
- `min(RH925,RH850)` and mean RH both improved single-snapshot AUC to about
  0.75.

This is sufficient to justify the replay/calibration harness, but not sufficient
by itself to replace the production v1 proxy.


## First two-slot replay result

The first live replay used 2026-10-06 12:00 UTC for fitting and 18:00 UTC as a
chronological holdout.

The initial min/mean-only search selected:

- feature: `mean(RH925,RH850)`
- transfer: 61% -> 0, 97% -> 100

Holdout comparison versus B173 v1:

- Brier: 0.2057 -> 0.1816
- ROC AUC: 0.7873 -> 0.8139
- sensitivity at 50: 0.8634 -> 0.8658
- specificity at 50: 0.5280 -> 0.5627

The candidate improved calibration/discrimination and did not lose low-cloud
sensitivity, but specificity improved by only 0.0347. It therefore **failed**
the provisional +0.10 specificity gate and was not promoted.

The next search explicitly penalizes 925/850 hPa RH layer disagreement rather
than weakening the gate.


## Exploratory spread-penalty holdout result

The pre-defined spread-penalty family was evaluated on the same 18:00 UTC
holdout for diagnosis only. It did not participate in the existing promotion
decision unless selected from the training snapshot.

Notable holdout results:

- mean RH minus 0.25 × RH spread:
  - Brier 0.1803
  - AUC 0.8155
  - sensitivity 0.8682
  - specificity 0.5650
- mean RH minus 0.75 × RH spread:
  - Brier 0.1865
  - AUC 0.8061
  - sensitivity 0.8081
  - specificity 0.6179

The stronger spread penalty moves in the desired specificity direction but
still does not establish a production replacement from only one holdout time.

## Continuous evidence collection

After merge, the calibration workflow runs twice daily at 08:30 UTC and
20:30 UTC. These windows are chosen after the existing WeatherGrid refresh and
after a second CWA valid time has become observable.

A push to `main` that changes the calibration implementation/spec also runs
the replay once immediately. Calibration-history output files are not included
in that push filter, so the resulting history commit cannot trigger a loop.

Each non-PR run:

1. selects the newest two completed CWA valid times;
2. fetches exact-slot Himawari cloud observations;
3. performs chronological train/holdout calibration;
4. writes the full current report to
   `weathergrid/calibration/cwa_low_cloud_latest.json`;
5. appends/deduplicates a compact result in
   `weathergrid/calibration/cwa_low_cloud_history.json`.

The history retains up to 120 train/holdout pairs and stores metrics and label
counts only. It does not commit raw Himawari pixels or field-validation images.

Each history update also records `review_readiness`: the count of distinct
validation slots, median improvements over the latest six distinct slots, the
candidate features seen in that window, and the longitudinal gate result. This
prevents one unusually favorable replay pair from being treated as stable model
evidence.
