# Issue 528 — W5 safe generated-data publication

## Current disposition

Independent proposal from main `6c3f0e46728b9b774a1d6edf657c979f2823827e`.
**Not activated.** `policy.json` retains `mode=legacy-main`, `pages_enabled=false`.
Existing refresh cadence, data URLs, provider validation, stale-file removal,
WeatherGrid native/derived grouping, V1 and Pages source are retained during review.
No model call, API activation, secret change, auto-merge, main bypass or deployment.
Main was observed `protected=false`, active rulesets `[]`; this PR does not make it protected.
#527 `f35c34c4a36e8d3c3e610e0d196912c6ae7756cf` remains a separate disabled Draft.

## Why the data branch

Approved code stays on PR-protected main. `weather-data` is a data-only orphan
history: complete allowlisted JSON inventory, SHA256 hashes, source code SHA,
producer/run receipts and previous data SHA. No workflow, JavaScript, HTML,
Python, W2 canonical data or executable/symlink payload is admitted.
Main-owned code runs all fetchers and validators. No data-branch code executes.

The 10 main writers now use a single main-owned publication helper. In the
review default, it preserves their legacy main commit route and messages; in
activated data mode it never pushes main, including on failure. Prepare loads
verified current data before dependent generation (CWA/native index/calibration).
Full inventories preserve deletions, including files no longer present on main;
assembly cannot resurrect stale bundles from frozen main. Publisher-scoped
compare-and-swap rejects concurrent same-file changes, preserves unrelated
provider updates and retries non-fast-forward pushes at most five times.
JMA/CWA's existing shared-index concurrency group remains unchanged. Nothing
merges weather values or changes models to resolve a race.

Reviewed data PRs were rejected for this feed: a manual approval every ten
minutes would delay observations and create CI/PR noise. An App main bypass
would undermine the executor boundary. A separate static site copy with changed
fetch URLs would add avoidable V1/WeatherGrid regressions.

## Exhaustive writer inventory

`python ops/v2/data_publish/inventory.py` checks all checked-in workflow files,
including the names omitted from the original issue's initial inventory.

| Workflow | Scope | Existing cadence |
|---|---|---|
| update_weather.yml | 3 regional summaries, detail shards, retired-weather deletions | every 3 h |
| update_weathergrid.yml | GFS, ICON, CWA browser/QC, coverage | four GFS windows/day |
| update_jma_msm_weathergrid.yml | JMA browser/QC | every 3 h |
| update_himawari9_weathergrid.yml | Himawari browser/QC or removal | every 10 min |
| weathergrid_v2_cwa_publish.yml | CWA current tiles + shared V2 index | upstream workflow completion/manual |
| weathergrid_v2_jma_publish.yml | JMA current tiles + shared V2 index | upstream completion, 3 h/manual |
| b169_viirs_live_ingest.yml | VIIRS browser/QC | manual |
| b166_cams_aod_weathergrid.yml | CAMS browser/QC | twice daily |
| cwa_low_cloud_calibration.yml | history/latest calibration JSON | twice daily |
| b117_gfs_multilayer_poc.yml | optional browser preview outputs | explicit manual publish flag |
| field_snapshot_capture_request.yml | fixtures/registry on snapshot-capture/** | branch push; **not a main writer** |

`test-chaselights-app.yml` only does a GET with an existing App credential; it is
not a data writer and is neither invoked nor modified. Workflow permission
`contents:write` is NOT proof of a write. New unreviewed direct/alternate writers
make inventory validation fail. Reviewers must still inspect scripts called by
new workflows; a static inventory is not a sandbox for arbitrary code.

## Pages and CI

Existing production is dynamic main-root Jekyll, recently successful run
[39354040794](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/39354040794).
`weather-data-pages.yml` is disabled by main-owned policy. Once separately
activated, it assembles the committed main site plus a verified complete data
snapshot, builds with the official Jekyll action, uploads a Pages artifact and
deploys via the existing github-pages environment. CNAME, root routes,
weather-map.html and apps/web-v2/ are retained. An explicit post-Jekyll finalizer copies the verified CNAME (the
official action excludes it by default) and checks all data hashes before upload.
It reads latest refs at execution
time to coalesce queued refreshes. `workflow_run` checks trusted main and same
repository and runs after failed producers too, because their stale-file
removal may be an intentional publication. No untrusted artifact is consumed.

This explicit chain avoids reliance on GITHUB_TOKEN push fan-out, which GitHub
documents as not triggering a Pages build. The observed dynamic Pages behavior
is recorded separately; do not assume it will continue for a new data branch.
References: [Pages source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site),
[custom Pages workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

No full W1–W4 integration suite runs per data update. One bounded Git push plus
one Jekyll build/deploy is added to an activated refresh. GitHub queues and Pages
latency are variable; no ten-minute delivery SLA is claimed. Queueing coalesces
intermediate versions while keeping the newest complete snapshot. Himawari
retains its 10-minute schedule and existing 90-minute validity check. Existing
runtime time/quality semantics are untouched. Run CI on code PRs and JSON/hash
checks on data updates. Initial real managed inventory: **327 JSON / 269,276,160
bytes**, so Git transport/build cost is material; measure the shadow build and
keep short-lived Actions artifacts. Repository history growth merits later
retention/compaction work, never force rewriting an active publication ref.

CI includes read-only 22 publisher regressions, 28 compatibility cases and
full-size offline assembly + Jekyll build, plus a separate push-only
GITHUB_TOKEN smoke restricted to `data-publish-smoke/528-<numeric run identity>`.
The latter seeds fixture-only JSON, really pushes an update, rejects code and
stale same-file writes, restores a prior snapshot as a new descendant and deletes
its own test ref. A Git bundle and receipts preserve all test commits. It makes
zero weather/model requests and does not touch main/weather-data/Pages. The
write token is repository scoped, **not** actually ref-scoped; helper boundaries
are defense in depth, not substitutes for GitHub main protection.

Four root workflow-contract tests are minimally updated to follow the delegated
publisher; no Legacy runtime/test expectations about weather values change.
The accepted-source immutable-merge rehearsal correction from #527 is reused
(original blobs `1ea0c2ae5fc49a97c37559d3df1414fd551a0aaa` and
`ad7ab327cdff238282f744959daa08320b592789`), with an additional exact four-file
W5 workflow-test ownership list and negative regression for arbitrary root tests. This avoids the known
post-#525 accepted-owner-source rehearsal error in a standalone main-based PR;
none of #527's executor/policy/workflow files are imported or activated.

## Owner-controlled cutover — separate from this Draft

1. Review exact-head CI and full-size build. Merge this migration only by the
   normal approved-PR path. Keep executor policies disabled. Do not impose
   PR-only main before data/Pages compatibility is verified.
2. With legacy updates still running, owner-dispatch maintenance `bootstrap` on
   main. It creates only the dedicated data branch and refuses existing history.
   This bootstrap is a shadow seed, not live data delivery. Record source/data
   SHA and verify publisher/Pages environment permissions. Do not change secrets.
3. Prepare a separate owner-reviewed activation PR changing the two policy
   fields together to `mode=data-branch`, `pages_enabled=true`. Re-seed/synchronize
   from the last legacy main immediately before cutover, or run all producers
   immediately afterward and verify their actual new data commits; an old shadow
   seed must not be accepted as a current forecast. Use a brief coordinated
   maintenance window: stop new data writers, drain already-running legacy-mode
   jobs, take the final seed, then merge activation and change Pages source to
   GitHub Actions. Do not leave both legacy and custom Pages publishers active.
   Verify a successful complete deployment and fetch V1/V2/map/JSON public URLs.
4. Exercise all ten migrated workflows on main. Verify real workflow_run chaining,
   permission checks, freshness, provider validation, shared V2 index and browser
   smoke. Only after successful publication and no legacy jobs remain, owner
   applies main PR/source/build protection. Codex App is never on the main bypass
   list; neither a new PAT nor all-Apps bypass is an acceptable fix. Protect the
   data ref against deletion and restrict updates to the vetted Actions publisher
   where the account/plan supports that enforcement. Do not assume a ruleset
   supports a particular actor before verifying it in GitHub.
5. Read main.protected, branch protection and effective rulesets/bypass actors
   again. Use an always-triggered required PR/source/build check; do not require
   path-filtered W5 checks on unrelated PRs. For a single maintainer, an approved
   PR requirement needs another eligible human reviewer or a deliberately
   documented feasible review policy. Do not configure an impossible self-review
   requirement or exempt the coding App. The connected App cannot administer
   rules/Pages settings; this remains an owner step.
6. Test an ordinary code PR and another complete scheduled refresh after main
   protection. Record actual rejection of unauthorized code writes only then.
   Until these external facts exist, #528 remains open and #527's
   MAIN_BRANCH_PROTECTION_UNVERIFIED guard stays fail closed.

## Recovery

Before activation this proposal leaves the existing main/Pages path in place.
In data mode, hash/JSON/scope/conflict/push failures leave the last complete data
ref and last deployed site in place; no silent fallback to main data occurs.
Failed provider refreshes retain the original explicit stale-bundle deletion.

Owner-dispatch maintenance `rollback` with a recorded **full ancestor data SHA**.
It validates the old data-only tree, restores the complete snapshot with a **new
fast-forward commit**, preserves original provider/issue/valid times and source
receipts, and records `rollback_of_data_sha`. It never rewinds main or overwrites
code. The maintenance completion triggers the gated Pages rebuild. Review the
snapshot's age first: rollback does not refresh provider data or authorize stale
forecasts; rerun failed producers promptly. Keep the old valid deployment if
assembly/deploy fails. If changing back to legacy mode is necessary, separately
review the policy/Pages-source reversal and synchronize current data to main by
a reviewed data PR; do not disable main protection or force-push a historical
whole repository. A rollback racing a producer gets a normal non-fast-forward
rejection and must be retried after inspecting the current data SHA.

## Reproduce

```sh
python -m unittest discover -s ops/v2/data_publish/tests -v
python ops/v2/data_publish/inventory.py
python -m unittest -v test_update_weather_workflow test_weathergrid_refresh_workflow test_jma_msm_refresh_workflow test_himawari9_refresh_workflow test_viirs_production_publish_workflow test_weathergrid_v2_publish
```

Main AGENTS.md, R4.2 research/navigation, WeatherGrid coverage, V2 README,
Governance, Worker Contracts and Codex runbook reviewed. W1–W4 source trees,
canonical data, provider algorithms, root UI/assets and current weather payloads
are unchanged by this proposal. No new user-visible semantic copy needs locale
translation. Hosting/protection and activated production refreshes remain
UNVERIFIED; isolated smoke is not production acceptance.
