# B147 WeatherGrid Production Freshness Gate

Date: 2026-09-30

## Goal

Ensure the B145 deployed-page smoke validates the exact WeatherGrid revision
that triggered the workflow, not a still-cached or still-current older GitHub
Pages deployment.

## Problem found from B146

B146 merged a value-aware WeatherGrid opacity change. Its B145 production smoke
completed successfully while the corresponding GitHub Pages deployment was
still finishing.

The screenshot artifact was byte-identical to the prior B145 screenshot. That
showed the previous production wait was too weak: it only looked for B144
basemap markers that were already present in the old deployment.

A green smoke therefore proved that *a compatible page* was live, but not that
*the new revision* was live.

## Freshness contract

Before Selenium starts, the workflow computes SHA-256 digests for the checked
out main-branch versions of:

```text
weather-map.html
assets/weather-map.js
assets/weather-map.css
```

The public versions are downloaded repeatedly with a cache-busting query and
`Cache-Control: no-cache`.

The production browser smoke starts only when all three public digests exactly
match the local repository bytes.

## Retry policy

The workflow retries up to 24 times with a 15-second delay, giving GitHub Pages
roughly six minutes to converge.

Each attempt prints expected and live hashes so a deployment-lag failure can be
distinguished from a browser/runtime failure.

## Result semantics

After B147:

- freshness gate failure = GitHub Pages/CDN did not expose the current revision;
- Selenium failure = the current revision deployed, but the browser contract failed;
- success = the exact current WeatherGrid presentation revision is live and passed.

## Scope

B147 changes deployment validation only.

It does not change:

- GFS data;
- WeatherGrid rendering;
- scoring;
- coverage geometry;
- MapLibre/OpenFreeMap behavior.
