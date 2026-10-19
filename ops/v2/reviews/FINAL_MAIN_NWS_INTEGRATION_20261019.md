# W5 final main-based NWS integration review

Owner: W5. Scope: restricted Research-only Runtime integration, no merge or
deployment. Exact final candidate SHA and Actions results belong in the PR
description, so this report does not certify a future revision of its own file.

## Immutable sources and main review

Reviewed main: `304a8a4cc7a1b2f346995f58e9a270cba650cc20`.

| PR | Head | Disposition |
| --- | --- | --- |
| #513 | `92804a5c86d14e7855bb92b52d6623bf7fa5c91a` | Original W3 Runtime; already included by #514/#516 |
| #514 | `05320573184c0e78004034a79fd92272202b725a` | Source-pin/Canonical-test adjustment; already included by #516 |
| #515 | `dec398e27aacaaf91365ead2163e9c2912e22f8f` | Separate optional diagnostic tool/tests/evidence; excluded |
| #516 | `6d342c79cf88daf690af57ec2021c9c7f6043fdc` | Primary integration source, merged into this distinct task branch |

Main has 13 automatic weather/WeatherGrid data commits after #514's reviewed
main `8cadcbed0c62ac128cd537c2a9b256b69662e611`. Comparison of the complete Git
trees confirms no AGENTS, research/navigation R4.2, W1, W2, W3, W4 or workflow
change in that main delta. Main's weather data is retained by the merge; it is
not restored from the older candidate. No conflict resolution is required.

Read AGENTS.md, research/navigation R4.2, V2 index, architecture, governance,
readiness, worker ownership, NWS, solar, date query, access advisory and free
composition/camera-area contracts. All source trees and reviewed contract blobs
are still enforced by the existing postmerge verifier and merge rehearsal.

| Owner | Pinned source commit | Accepted subtree |
| --- | --- | --- |
| W1 | `c1fa5348e7ae2b3b4bc1d254773daca86ed5451e` | `c5563eb2db8f719ea13fa19a64af1a2d7792bce2` (`specs/v2`) |
| W2 | `cf29288ce47e2cccb2fb2e1453ad193200996a95` | `228f92d949e4df87719c9a3ef6c341219f9b0714` (`data/v2`) |
| W3 | `92804a5c86d14e7855bb92b52d6623bf7fa5c91a` | `edc073640812ff74bcf4ef01a2b9aa5e8ed30a08` (core), `530a3fe48f460372b2f5ca7304c9fb75fedd0e6b` (models) |
| W4 | `ca4e59cf5978347f1422fb1fd2d485c188b58edd` | `70eb22ad22f3cad08aafab9ac71032ee8278139b` (`apps/web-v2`) |

W1 additionally requires `6a774a95c3bc24ff06f004236fe8b225c7001c4d`.
W2 original Batch03 Canonical source is
`2177bd8c8b6c18e0a4b284e50b55d0ff12697ddd`; reviewed R2 correction source is
`c41567edcfa9efe95111f3306d6410f1934e7062`, Canonical commit
`b45169e42d3acfe9b287c6e16a9ac887bb8cd650`.

The existing W3 exception remains exactly one Canonical-hash test adjustment:
`tests/test_forecast_runtime.py` original blob
`be81080c165028c89809ff7eba401a9967d39eb0`, accepted blob
`10843b955e32ba13e50dd0dffe31f73973bcd5ca`. Kerry Park Canonical SHA256 remains
`74c2284bbd1a2aa153330accea265e86fca27fcb23420512d112d750ac7779fc`.
No new owner pin or test-count transition is made in this task.

## Why #515 is not a prerequisite

All ten additions were inspected. Three tests cover its new optional curl
probe: CONNECT versus target status, transfer/rate-limit classification and
safe header filtering. Its fourth test strengthens 403/429/CONNECT failure
coverage at either request; the existing 66-test baseline already tests
transport failure without fallback, and the unchanged adapter catches
HTTPError/URLError/OSError/TimeoutError and returns UNKNOWN with no records.
This is useful follow-up coverage, not a missing Runtime fix or a requirement
to use that new probe. Its independent successful capture cannot certify the
GitHub runner or establish the historical denial cause.

Do not merge the #515 stack as an additional prerequisite. If later accepted,
review its diagnostic tool, keep the R2 Canonical hash adjustment and explicitly
rotate W3's tree/count from 66 to 70 (full baseline 353 to 357), retaining every
existing test. This task does not claim those four additions are integrated.

## Original real-provider evidence

Original capture run [39156798749](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/39156798749)
on `ff4742de89004217eb3f8fef1982b252b24d4939` completed at
`2026-10-18T19:01:22Z`. Artifact `12147316890` is unexpired, retained until
2027-01-16; GitHub artifact metadata and independently hashed local ZIP agree:
`97d7ea8ef954785b237139394c9c64694fc56e20a4a73fe05e54720029dfe738`.

| Body | Original bytes | SHA256 |
| --- | --- | --- |
| /points/47.6,-122.33 | 3909 | `3192fc89d391ec6bfccbc7cd9f46109f3059fbd3eb08c4f371be785f8ed584f2` |
| /gridpoints/SEW/125,68 | 178376 | `0d9764a81343ee8044820444d0071ea25a5c57c9bf98dc7c34693d1ce3f1dd33` |

Original run remains FAIL due to the documented W5 microsecond-versus-second
verifier error. Corrected #516 run
[39157060470](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/39157060470)
is PASS at #516's exact head; three precision regressions and offline verification,
zero new HTTP requests. Verification ZIP `12147213309` SHA256:
`1960dca28838a7cb6042e54b7c324de52af98073c6dac400aa12276cc2c30766`.
Neither success nor archive replay is relabeled as a new/fresh live capture.

This candidate makes only two operational changes to #516: record the reviewed
main SHA, and allow its own exact task branch to run offline verification on PR
opening and synchronization. The live job remains limited to the original
#516 branch's opened event. No provider refetch is triggered by this task.
This review file is the third changed path relative to the main+#516 merge.

## Required exact-candidate acceptance

Run unchanged Integration: 353 PASS / zero FAIL, ERROR or SKIP, including W1 67,
W2 33, W3 core 66 + models 10, W4 Node 49 + Chromium 82, W5 40 + built-package
Chromium 6. Run Provider Acceptance separately (three verifier tests plus pinned
archive checks); its intentionally inactive live-capture job is not a skipped
Integration test. Run Release Readiness Tools: immutable-head build and real
base/candidate merge rehearsal with refs_changed=false, deployment_allowed=false,
approval=NOT_GRANTED. Inspect logs and proposed merge tree, not just green labels.

Historical #516 Integration 39157060479 and Release Tools 39157060463 passed;
they are source evidence and cannot substitute for this new candidate's checks.
Local browser tooling absence must be reported separately if still present.

## Merge disposition and limitations

At review, main branch metadata reports protected=false, required checks off;
repository Rulesets with includes_parents=true returns []. The protected-branch
details endpoint returns 403 Resource not accessible by integration, so its full
administration configuration cannot be audited. #516 has no submitted reviews.
The task does not change repository settings, infer approval from green CI,
enable auto-merge or bypass a protection. Hosting/environment approval controls
are not certified. Project-owner acceptance of the exact candidate remains
required. An admin should enforce required checks and PR approval before merge,
or the owner must explicitly accept the absence of hosting-enforced protection.

Once exact-candidate CI/provider/rehearsal passes and current main is rechecked,
the technical disposition can be ACCEPT FOR RESTRICTED RESEARCH-ONLY REVIEW.
Merge only the final consolidated candidate; #513/#514/#516 are included history,
not three additional merges. Keep #515 separate. No merge/deploy occurs here.

Photography remains UNKNOWN / NOT_EVALUABLE; no score, recommendation or
Directions. W2 Place timezone remains UNKNOWN. Raw NWS coverage is a Seattle
regional sample, not verified camera/subject/arrival GPS. NOAA updateTime is not
issuance; model/run/native resolution remain unknown. The capture expires under
the one-shot 24-hour operational policy at 2026-10-19T18:25:37Z, before the
selected sunset at 2026-10-20T01:13:25.716934Z. Fresh data and independent
scientific/threshold/terms/semantic/publication gates are still required for any
photographic recommendation. One successful capture provides no long-term or
production-executor availability guarantee. Beta R2, V1 and WeatherGrid sources
are preserved, with no publication or deployment edits.
