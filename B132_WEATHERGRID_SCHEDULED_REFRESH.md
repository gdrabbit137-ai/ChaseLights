# B132 Scheduled Live WeatherGrid Refresh

Date: 2026-09-29

> Canonical batch ID: B132 is reserved for this scheduled WeatherGrid refresh. Subsequent subject-aware coverage handoffs are B133 (Dongyin Lighthouse) and B134 (Duoliang Station).


## Goal

Turn the B119/B117 WeatherGrid live preview from a manually published snapshot into a self-refreshing production preview without coupling it to Photography Opportunity scoring.

B132 does not change scoring, Opportunity eligibility, or the canonical weather JSON refresh.

## Current production state

Before B132:

- the main ChaseLights weather pipeline updates every 3 hours;
- the WeatherGrid GFS pipeline can fetch and render live NOAA/NCEP data;
- B130 and B131 proved Place-scoped live requests for Waiao and Laomei;
- the first regional live WeatherGrid snapshot was published manually on 2026-09-29;
- subsequent WeatherGrid publication still required a manual workflow run.

## Refresh cadence

GFS nominal cycles are:

```text
00Z / 06Z / 12Z / 18Z
```

The scheduled workflow runs at:

```text
05:20Z / 11:20Z / 17:20Z / 23:20Z
```

This is approximately 5 hours 20 minutes after each nominal model cycle.

The existing `candidate_runs()` logic still provides fallback to older cycles when the newest candidate is unavailable.

This cadence is intentionally separate from the canonical ChaseLights three-hour forecast refresh because WeatherGrid is a coarse GFS visualization layer, not the scoring source of truth.

## Published forecast horizon

The default public preview contains:

```text
f000 / f003 / f006 / f009 / f012
```

Manual runs may override the comma-separated forecast-hour list.

## Publication contract

The workflow generates the complete validation output in a temporary Actions workspace, but only these compact browser artifacts are committed to `main`:

```text
weathergrid/gfs_tw_weather_browser.json
weathergrid/gfs_tw_weather_qc.json
weathergrid/weathergrid_coverage_browser.json
```

Raw GRIB2 files and validation PNGs are never added to Git.

The full run output is retained as a GitHub Actions artifact for 7 days for debugging.

## Validation before publication

Every scheduled/manual production run must verify:

1. at least one browser forecast frame exists;
2. the browser bundle contains Places;
3. QC frame count matches the browser frame count;
4. subject-aware coverage bundle is generated from the current `main`;
5. known migrated Places `tw-073` and `tw-075` remain all-topic-complete.

If any assertion fails, publication stops before committing to `main`.

## Concurrency and write safety

The workflow uses:

```text
concurrency.group = chaselights-weathergrid-publish
cancel-in-progress = true
```

Only one WeatherGrid publication is active at a time.

Before pushing, the workflow rebases onto the latest `main` and retries the push up to five times. This protects against the independent three-hour canonical weather updater writing to `main` at the same time.

## CI contract

`test_weathergrid_refresh_workflow.py` statically verifies:

- the intended four-times-daily schedule;
- default f000-f012 horizon;
- regional fetch scope;
- compact-output-only Git publication;
- no GRIB/PNG Git add;
- known coverage completeness guard;
- 7-day artifact retention.

The B117 WeatherGrid CI suite includes this test.

## Operational boundary

WeatherGrid remains:

- NOAA/NCEP GFS 0.25° coarse synoptic data;
- a browser visualization / QC layer;
- separate from Photography Opportunity scoring;
- subject-aware for display/fetch extent only where curated coverage exists.

A successful refresh must not be interpreted as proof that a Photography Opportunity itself is eligible.

## Next work

After several scheduled production cycles are observed:

- audit refresh reliability and artifact size;
- expose live-data age / model-cycle freshness more prominently in the WeatherGrid UI;
- decide whether scoped provider fetches should be used for on-demand Place detail views while the public overview remains regional;
- reconcile the stale field-observation intake and verdict-copy PRs onto current main.
