# ops/pages — Cloudflare Pages whitelist publisher

The GitHub Pages origin used to publish the **entire repo root**, which made
`/workers/api/src/index.js`, `/AGENTS.md` and `/data/v2/staging/` publicly
downloadable. This directory replaces that with a whitelist: only the files the
static site actually fetches at runtime reach `dist/`.

## Build

```bash
bash ops/pages/build_dist.sh            # default: HTML/assets/locales/indexes (data lives on R2)
bash ops/pages/build_dist.sh --full     # also ship weathergrid/ + weather_details/ (rollback path)
bash ops/pages/build_dist.sh --light    # alias of the default
bash ops/pages/build_dist.sh --dry-run  # print the resolved manifest, copy nothing
bash ops/pages/build_dist.sh --out DIR
```

Exit codes: `0` ok, `2` forbidden engineering path leaked, `3` a file hit the
25 MiB Cloudflare per-file ceiling, `4` the dist exceeded 20,000 files.

The copy source is `git ls-files` — **tracked files only**. The working tree
carries ~2 GB of generated, uncommitted tiles under `weathergrid/` and
`weather_details/`; a directory copy would ship them, so the script resolves the
whitelist against the index instead and copies file by file.

Measured sizes: default (`--light`) = 533 files / 160.4 MiB; `--full` = 2,054 files /
1,339.7 MiB. Since Step ② the heavy trees live in R2 (`data.chaselights.app`), so
the default build no longer ships them.

`_headers` (Cloudflare Pages header config) is copied to the output root.

### What ships

| Entry | Why |
| --- | --- |
| 6 root HTML shells + `404.html` | the pages themselves; `404.html` uses absolute `/assets/` URLs because it is served at any path depth |
| `assets/` | JS/CSS/brand/vendor bundles |
| `locales/` | zh-TW / en / ja copy |
| `data/v2/copy/` | `fail_reason_overrides.json`, `live_cam.json` (fetched by `assets/app.js`) |
| `data/v2/evaluations/subject-cards-[0-9]*.json` | `V2_SUBJECT_CARDS_FILE` — note the build **input** `subject-cards-weather-input.json` is deliberately excluded |
| `apps/web-v2/*.json` (4 indexes) + `evaluations-details/` | catalog / browse index / per-place detail |
| `*_weather.json` (tw/jp/us) | legacy per-region weather |
| `weathergrid/` | map tiles + per-region manifests |
| `weather_details/` | per-spot hourly shards |

`weathergrid/` and `weather_details/` are served from Cloudflare R2 since Step ②;
they stay available under `--full` only as a rollback path.

Watch the size ceiling: `weathergrid/icon_tw_cloud_browser.json` is 24.9 MiB
(26,105,418 B) — inside the 25 MiB limit with ~104 KiB of headroom, so the build
warns above 24 MiB and aborts at 25 MiB.

## Contract test

```bash
python ops/pages/test_build_dist.py
```

Pins the runtime surface, the forbidden-path list, a real `--light` build on
disk, and both Cloudflare ceilings (exit 3 / exit 4). It runs in
`v2-integration.yml` as *Contract — Cloudflare Pages whitelist publish*, before
the numbered suite, so it never perturbs the pinned test totals.

## Cloudflare Pages project settings

- Build command: `bash ops/pages/build_dist.sh`
- Build output directory: `dist`
- Root directory: `/`
- Environment: none required (static copy; no Node/Python deps)
