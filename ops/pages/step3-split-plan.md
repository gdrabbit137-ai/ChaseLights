# Step ③ — A+B dual-track split (inventory + order)

Decided: **A** = self-hosted Windows runner in the private repo for the
compute-heavy scoring/re-evaluation jobs; **B** = a separate **public** data
repository for the high-frequency weather producers. Both write into the same R2
bucket, on **disjoint key prefixes**, so `data.chaselights.app` keeps one base
URL and one CORS policy.

## Why the split is about minutes, not tidiness

30-day measurement (2026-10-26 → 11-25, `runs` API, wall-clock):

- total 10,942 runner-minutes; `schedule` 7,099, `push` 3,178, `workflow_run` 439
- top consumers: B167 CAMS 3,290, V2 Evaluations 1,672, Live WeatherGrid Preview
  1,571, V2 Integration 1,437

A private repo gets 2,000 free minutes; public repos are unlimited. Moving the
scheduled producers to a public repo is what makes the private repo affordable
without paying per-minute.

## Classification (from `.github/workflows/*.yml`, paths + commits inspected)

### B — move to the Public Data Repo, write `weathergrid/**` only

| workflow | trigger | why |
| --- | --- | --- |
| `update_weathergrid.yml` | schedule/push | core GFS/ICON browser bundles |
| `update_himawari9_weathergrid.yml` | schedule/push | satellite cloud tiles |
| `update_jma_msm_weathergrid.yml` | schedule/push | JMA MSM JP tiles |
| `weathergrid_v2_jma_publish.yml` | schedule + workflow_run | v2 JMA tile publisher |
| `weathergrid_v2_cwa_publish.yml` | workflow_run | v2 CWA derived tiles |
| `cwa_low_cloud_calibration.yml` | schedule | CWA calibration history |
| `b166_cams_aod_weathergrid.yml` | schedule | CAMS AOD/PM2.5 (biggest single cost) |
| `b169_viirs_nightlights.yml` | push/dispatch | VIIRS night-light grid |
| `weathergrid_v2_experiment.yml` | push/workflow_run | tile experiments (PR-only parts stay) |

These are pure fetch → transform → commit jobs. They need no private code beyond
the fetch/transform scripts, which move with them.

### A — stay in the Private repo, run on the self-hosted Windows runner

| workflow | trigger | why |
| --- | --- | --- |
| `update_evaluations.yml` | schedule | scoring engine + `weather_details/**` shards (~80 min/run) |
| `update_weather.yml` | schedule | region weather JSON + details fan-out |
| `b169_kv_sync.yml` | schedule | KV/site payload sync |
| `v2-integration.yml` | push/PR | 1,116-case suite; the expensive part is CPU, perfect for a local box |
| `v2_public_preview_smoke.yml`, `v2_schema_contract.yml`, `v2-release-readiness.yml` | push/PR | contracts over the private tree |
| `r2-sync.yml` | push | mirrors whatever the private tree produced |
| `i18n-sync.yml`, `v2-pin-sync.yml` | push | repo hygiene, tiny |

Self-hosting `v2-integration` is the other half of the cost story: 1,437
min/month on hosted runners becomes ~0.

### Keep as-is (PR-only, no schedule, no data commits)

`android-build`, `b113/b117/b155/b156` POCs, `b120`, `b145`, `b149`, `b30_*`,
`b32_*`, `b36`, `b61`, `field_*`, `test_*`, `weather_refresh_contract`,
`weathergrid_v2_jma_benchmark`, `b170a`, `b171`.

## R2 prefix isolation

| writer | allowed prefix | command |
| --- | --- | --- |
| Public Data Repo | `weathergrid/**` | `python ops/pages/r2_sync.py --apply --only weathergrid` |
| Private repo | `weather_details/**` | `python ops/pages/r2_sync.py --apply --only weather_details` |

`r2_sync.py` now **fails closed**: a path outside the `--only` scope aborts with
`refusing N path(s) outside --only scope` instead of being skipped silently, so a
mis-wired repo cannot half-write the other tree.

Both repos hold the same S3 credential today. If you want credential-level
isolation later, split into two buckets (`chaselights-grid`,
`chaselights-details`) and add a small Worker (or two custom domains) to keep a
single `data.chaselights.app` base URL. Policy-level isolation via `--only` is
enough while both repos are yours.

## Order matters — do NOT `git rm` first

`r2_sync.py` uploads **tracked files**, so deleting `weathergrid/` from the
private repo before the public data repo exists would leave the bucket with no
source to sync from. Also `cl-wg-12` reads
`weathergrid/gfs_tw_weather_browser.json` and `build_dist.sh --full` expects both
trees.

Recommended sequence:

1. **Create the Public Data Repo** and seed it with `weathergrid/` (history can
   start fresh; the bucket is the source of truth for consumers).
2. Move the nine producers above into it, each ending with
   `r2_sync.py --apply --only weathergrid`.
3. Point the private repo's `r2-sync.yml` at `--only weather_details`.
4. **Then** `git rm -r weathergrid` + `.gitignore`, and convert the tests that
   read the local tree (`cl-wg-12`, `cl-wg-16` fixtures, `build_dist --full`) to
   either fetch from R2 in CI or use committed fixtures.
5. Same again for `weather_details/` once the self-hosted runner is the writer —
   that tree is 948 MB and the biggest remaining git weight.

Step 4 is the "Git 瘦身" ticket; it is blocked on step 1–2, not on this document.
