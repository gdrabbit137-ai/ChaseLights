# Step ② — move the heavy data plane to R2

> **Status (2026-11-25): DONE.** Bucket `chaselights-data`, public domain
> `data.chaselights.app` (CNAME → public.r2.dev, proxied), CORS applied and
> verified; 1,521 objects / 1,179.5 MiB uploaded; the front end reads the data
> plane through `window.CL_DATA_BASE` (`assets/data-base.js`).
>
> Historical note — this section was first blocked on one dashboard action — the account has R2
> disabled, so every `/r2/buckets` call returns
> `10042 Please enable R2 through the Cloudflare Dashboard`.
> Once R2 is enabled, `bash`-free flow is:
>
> ```bash
> python ops/pages/r2_sync.py --dry-run     # 1,521 files / 1,179.5 MiB, cache policy applied
> python ops/pages/r2_sync.py --apply       # needs R2 S3 creds (R2_ACCESS_KEY_ID/R2_SECRET_ACCESS_KEY)
> ```
>
> Bucket name: `chaselights-data`; CORS rules: `ops/pages/r2-cors.json`.

Goal: shrink the Cloudflare Pages deployment from **2,054 files / 1,339.7 MiB**
to **~534 files / ~161 MiB** by moving the two heavy trees to R2, and remove the
25 MiB per-file risk in the same move.

## What moves

| Path | Files | Size (tracked) | Notes |
| --- | --- | --- | --- |
| `weather_details/` | 473 | 948.3 MB | `{region}/{spot}.json`, one shard per spot (tw 219 / us 160 / jp 94) |
| `weathergrid/` | 1,048 | 230.8 MB | browser bundles + QC + `v2/` tiles + `png/` manifests |
| — of which over 18 MiB | 7 | 148.0 MB | `icon_tw` 24.9, `icon_us` 24.5, `gfs_tw_wind_uv` 22.9, `gfs_us_wind_uv` 20.6, `gfs_tw_weather_browser` 18.6, `gfs_us_weather_browser` 18.4, `jma_msm_jp_cloud_browser` 18.0 |

Everything else on the site is small: the remaining dist is HTML (7 files,
incl. the new `404.html`), `assets/` 2.6 MB, `locales/` 1.0 MB,
`data/v2/copy/` 0.9 MB, the four `apps/web-v2/*.json` indexes ≈ 31 MB,
`evaluations-details/` 460 files / 109 MB, and `*_weather.json` ≈ 10 MB.

## Bucket layout

One bucket, keys mirroring today's URLs so the front end only needs a base
prefix change:

```
chaselights-data/
  weather_details/tw/tw-001.json
  weathergrid/gfs_tw_weather_browser.json
  weathergrid/v2/index.json
  weathergrid/png/<region>/manifest.json
```

Public read through a custom domain (`data.chaselights.app`) attached to the
bucket — never through `*.r2.dev` in production (no SLA, no cache rules).

## Cache-Control policy

| Key prefix | Header | Why |
| --- | --- | --- |
| `weather_details/*` | `public, max-age=300, stale-while-revalidate=60` | shards are rewritten by the daily evaluations run |
| `weathergrid/*.json` | `public, max-age=600` | browser bundles refresh every few hours |
| `weathergrid/v2/*`, `weathergrid/png/*` | `public, max-age=31536000, immutable` | versioned by the manifest / file stamp |
| `*/manifest.json` | `public, max-age=60` | must turn over fast when tiles are replaced |

CORS is mandatory — the JSON is fetched cross-origin from `chaselights.app`:

```
Access-Control-Allow-Origin: https://chaselights.app
Access-Control-Allow-Methods: GET, HEAD
```

(R2 bucket CORS policy; the `pages.dev` preview origin and `http://localhost:8899`
should be added while testing, then trimmed.)

## Front-end constants that must change

Introduce one base so local dev keeps working with a single default:

```html
<script>window.CL_DATA_BASE = "https://data.chaselights.app/";</script>
```

(default `""`, i.e. relative `./`, when the tag is absent)

| File | Line today | Becomes |
| --- | --- | --- |
| `assets/app.js` | 2420 `./weather_details/${region}/${spotId}.json` | `${DATA_BASE}weather_details/...` |
| `assets/app.js` | 2568 `fetch('./weathergrid/'+file)` | `${DATA_BASE}weathergrid/...` |
| `assets/weather-map.js` | 2–7 six `LIVE_*` constants | `DATA_BASE + 'weathergrid/...'` |
| `assets/weather-map-v2-tile-loader.js` | 1 `V2_INDEX_URL` | `DATA_BASE + 'weathergrid/v2/index.json'` |

Tests that pin these strings and will need the same edit plus a cache-bust
stamp bump: `apps/web-v2/tests/cl-wg-12-gfs-tw-window.test.mjs` (pins
`./weathergrid/...`), and any `cl-ui-*` test asserting `app.js?v=` /
`weather-map.js?v=`.

## Upload script (`ops/pages/r2_sync.py`, to be written in this step)

- reads the same whitelist idea: only `weathergrid/` + `weather_details/`
- parallel uploads (8 workers), `Content-Type` by extension
  (`application/json`, `image/png`), `Cache-Control` from the table above
- `--dry-run` prints `key -> size, cache-control` without touching R2
- idempotent: compares `Content-Length` + `ETag` before re-uploading
- auth: `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` (R2 S3 token) or
  `wrangler r2 object put` when only a Cloudflare API token is available

## Cut-over order (no downtime)

1. create bucket + upload everything, verify a few keys over
   `data.chaselights.app` (200, correct `content-type`, CORS preflight OK)
2. flip `CL_DATA_BASE` and deploy Pages — old relative paths keep working only
   if the files are still on Pages, so **keep them for one release**
3. after 24 h of green checks, drop `HEAVY_DIRS` from `build_dist.sh`
   (dist ≈ 161 MiB) and delete the copies from the Pages deployment
4. only then consider `--light` as the default build command
