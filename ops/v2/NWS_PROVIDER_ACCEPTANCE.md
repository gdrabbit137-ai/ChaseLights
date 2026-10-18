# W5 real NWS acceptance — #467 / #506

This is an explicitly requested, one-shot research acceptance of W3 #513 on
W5 #514 HEAD `05320573184c0e78004034a79fd92272202b725a`. The existing W1–W4
trees, Source Pins, 353-case Integration gate and release rehearsal are unchanged.
Reviewed latest main `2c73eb6a205ee25fb09ddf25eb8d1e40f007f9df`, AGENTS.md,
R4.2 and applicable V2 architecture/governance/NWS/solar/date/access contracts.
Its only delta from #514's base is an automatic Himawari data update.

The same-repository, exact-task-branch workflow runs on GitHub-hosted Ubuntu
with read-only contents/Actions and no secrets, publishing or deployment.
Only `pull_request: opened` performs provider requests. Synchronization runs
offline verification of the pinned original artifact; it never repeats HTTP.
Opening this task PR is the explicit opt-in; a new capture requires an explicit
Actions rerun of the original opened event.
Do not redirect denied traffic, unset proxies or use an intermediary to reach NWS.

`python ops/v2/nws_provider_acceptance.py --output work/nws-acceptance`
performs at most four official requests: an independent /points and mapped
/gridpoints pair, then the unchanged W3 runtime's pair. No retry, redirect,
transport injection, fixed retrieval clock or fixture fallback. Each request is
limited to 12 seconds and 8 MiB. A failure is archived and fails the workflow.
The probe never writes to Legacy, public data, Canonical, source manifests or UI.

The artifact includes original independent HTTP bodies, status, URL, UTC request
times and parsed response-header bytes; W3 original body bytes and runtime JSON;
SHA256 manifest; independent geography/time/schema/field/interval/expiry checks;
and negative archive replays. Header serialization is parsed HTTP metadata,
not wire-level TLS packet capture. W3 bodies have the runtime's completion UTC
clock; their HTTP headers are not exposed by the existing adapter. The two
captures can differ as NOAA refreshes and are never forced to share hashes.
HTTP and runtime failures are separate from the unchanged offline CI tests.

The independent verifier matches raw native validTime intervals and numeric
values, reports null/missing fields and native coverage, corroborates grid/body
identity and regional timezone, hashes the actual R2 Canonical and verifies
UNKNOWN / NOT_EVALUABLE with no score or Directions. Replaying an archived
real capture is always TEST_FIXTURE; replay is not authenticated live transport.
Stale, timezone-mismatched and corrupt archives must fail closed.

PASS establishes only this run's technical raw-provider acceptance. The 24-hour
age policy is an explicit operational research probe, not an approved production
policy or scientific threshold. NOAA updateTime is not model issuance; run ID,
model ID/version, physical cell resolution and model horizon remain unknown.
Provider timestamps and the actual native valid intervals are retained.

W5 may recommend Research-only Runtime merge only after exact-head Integration
(353, including 82 W4 and six built-package browser cases), Release Readiness,
this provider evidence and latest-main source review pass. Project-owner review
remains required. Retain Draft if any condition is unresolved. No deployment is
authorized by this tool. Formal photography scoring additionally needs W2
scientific condition/provider/threshold approval, real coverage and freshness,
W1/W3 scientific admission, required human semantic/terms review, W4 presentation
and an independent release gate. NWS raw sky cover does not establish skyline
visibility or city-light overlap. W2 Place timezone remains UNKNOWN.

Next bounded capability: Seattle regional sunrise/sunset WINDOW. Next Taiwan
research candidate: Jingzaijiao sunset, after a versioned W1 JMA MSM contract,
real native-domain/interval capture and W2 evidence/condition review. Neither
is an approved photography score; CWA RH proxies cannot substitute for clouds.

## Actual capture and verifier correction

Original Actions [39156798749](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/39156798749)
on `ff4742de89004217eb3f8fef1982b252b24d4939` made the four bounded requests,
with independent HTTP 200 responses and default W3 HTTPS_TLS / RAW_SOURCE_ONLY.
Completion: `2026-10-18T19:01:22Z`. Artifact 12147316890 ZIP SHA256:
`97d7ea8ef954785b237139394c9c64694fc56e20a4a73fe05e54720029dfe738`.
The run remains FAIL: the first independent verifier incorrectly required
microsecond equality between the solar event and W3's seconds serialization.
The verifier correction preserves the actual event microseconds, checks the
serialized timestamp equals its exact whole-second representation and checks
both instants belong to the same original half-open native interval. Three
separate verifier regressions reject one-second drift and exclusive-end errors.
The existing W3 runtime/parser and Source Pins remain byte-identical to #514.

The corrected verifier uses the same immutable capture offline. Its PASS, when
confirmed, certifies the original run/time, never a fresh network retrieval.
The original capture/failure is retained alongside the new verification result.
Use `--verify-archive ARCHIVE_DIRECTORY --output NEW_DIRECTORY` to reproduce;
all archive manifest/body hashes and the pinned capture run/head are checked.
Archive records/replays are never reissued as current HTTPS results.

The actual selected event is Seattle sunset `2026-10-19T18:13:25.716934-07:00`,
or `2026-10-20T01:13:25.716934Z`; W3 serializes valid_at as
`2026-10-20T01:13:25Z`. NOAA refresh is `2026-10-18T18:25:37Z`, not issuance;
the explicit age cutoff is `2026-10-19T18:25:37Z`, **before the event**.
This capture is valid technical forecast context at retrieval only. Refresh
is required before using it at the event; no event-time or photographic
recommendation admission is granted. Native skyCover is 93%, windSpeed
5.556 km/h, probabilityOfPrecipitation 0%; these are provider values, not
photographic scores. All three fields have zero null entries in this capture.

Concurrent W3 [#515](https://github.com/gdrabbit137-ai/ChaseLights/pull/515)
has a separate successful managed-route capture and four additional tests.
It is deliberately not integrated here: doing so changes W3 trees/counts and
requires its own reviewed W5 pin transition. Its earlier result cannot certify
this GitHub-hosted runner or explain the historical proxy denial.
