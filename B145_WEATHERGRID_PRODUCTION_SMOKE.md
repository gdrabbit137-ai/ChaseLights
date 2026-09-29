# B145 WeatherGrid Production Smoke

Date: 2026-09-30

## Goal

Verify the actually deployed ChaseLights WeatherGrid page after the B144 cartographic-basemap rollout, rather than relying only on local/static browser smoke.

The production check targets:

```text
https://chaselights.app/weather-map.html
```

## Why this batch exists

B144 proved the MapLibre/OpenFreeMap integration against the repository candidate and existing Browser Smoke. GitHub Pages deployment is a separate boundary: CDN publication, external MapLibre module loading, OpenFreeMap style/tile access and browser CORS behavior can still fail after repository CI passes.

B145 therefore makes the deployed page itself part of the validation loop.

## Production assertions

The smoke test requires:

1. `window.__weatherGridPreviewReady === true`;
2. LIVE GFS rather than the demo fixture;
3. `#basemap-status` reaches the ready state;
4. the status identifies MapLibre + OpenFreeMap;
5. a visible MapLibre canvas exists underneath the WeatherGrid canvas;
6. the default weather opacity is 62%;
7. known all-topic-complete Place `tw-073` (老梅綠石槽) can be selected;
8. at least one real Opportunity can be selected;
9. subject-aware coverage reports a live coverage source and viewport status;
10. a production screenshot is retained for seven days.

## Triggering

The workflow has three modes:

- pull request: offline/static contract only;
- push to main for WeatherGrid presentation/smoke files: run the deployed production smoke;
- workflow_dispatch: allow an explicit production recheck.

Before launching Selenium, the workflow retries the public page for up to roughly six minutes so GitHub Pages publication can catch up with the main-branch commit.

## Failure interpretation

A failure after local Browser Smoke passed means the problem is in the deployed delivery path or an external presentation dependency, not necessarily in GFS decoding or Photography Opportunity scoring.

Typical categories are:

- GitHub Pages publication lag/failure;
- MapLibre CDN unavailable;
- OpenFreeMap style/tile unavailable;
- browser CORS/network failure;
- live WeatherGrid bundle not available;
- production-only DOM/runtime regression.

## Scope guardrails

- no scoring changes;
- no GFS fetch changes;
- no coverage geometry changes;
- no requirement that basemap data influence any photography decision;
- screenshot is diagnostic only and is retained as a short-lived Actions artifact.
