# B168R WeatherGrid Fog / Haze Inspector + Replay

Date: 2026-10-01

## Scope

B168R makes the B168 diagnostic visible and replayable without changing Photography Opportunity scores.

WeatherGrid's selected-spot inspector combines nearest-time / nearest-cell environment evidence from:
- GFS: visibility and low cloud
- CWA WRF3: relative humidity when available
- CAMS Global: AOD 550 nm and PM2.5

The inspector reports fog-supported, haze-supported, mixed, unresolved low visibility, aerosol-without-degraded-visibility, or no-signal states. It explicitly says the diagnosis does not yet affect photography scoring.

## Runtime

`fetch_data._build_opportunity_runtime_diagnostics` now attaches the B168 `photography_environment` object to each Opportunity diagnostic. `_score_opportunity` does not consume it in B168R.

## Replay

`test_fixtures/fog_haze_replay_cases.json` covers Qingshui Cliff and Qixingtan scenarios.

The meteorological values mirror existing regression cases. No historical CAMS snapshot was captured for the 2026-09-28 field case, so AOD / PM2.5 values in this B168R replay are sensitivity inputs, not historical observations or ground truth. The replay therefore validates classification behavior and non-scoring isolation; it does not claim what the aerosol state actually was at the photographed moment.

## Next gate

Before B170 transparency scoring:
1. capture time-matched CAMS/environment snapshots for future field cases;
2. replay enough clear, fog, haze and mixed cases;
3. calibrate thresholds without weakening existing subject-readability and whiteout guards.
