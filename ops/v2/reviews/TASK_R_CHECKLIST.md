# V2 Release Readiness Checklist

Status: **NOT READY**. Deployment allowed: **false**.

Candidate: `15320eac3cfdacc4663b64d46bde4b6a712b2d48`; reviewed main: `f8a1f83bfeda5dc75f7e00c847e7728a0cef79ec`.

Evidence is advisory and requires independent review; this tool never authorizes deployment.

| Check | Owner | Evidence domain | Status | Reason |
|---|---|---|---|---|
| A.owner_integration | W5 | local | PASS | verify_main fixed owner ancestry/tree in local provenance and GitHub postmerge logs |
| A.pending_dependencies | W5 | github_inventory | PASS | Current five open PRs independently inventoried; none is falsely treated as merged; #482/#483 separately reviewed, #420 outside V2 pilot |
| A.merge_rehearsal | W5 | local | PASS | real immutable f8a1 main + 15320eac candidate merge-tree PASS; refs unchanged |
| B.canonical_provenance | W2/W5 | local | PASS | W2 owner 509a7c / P01 content 2177bd; byte/blob/SHA256/fixture/catalog checks PASS |
| B.research_isolation | W2/W5 | local | PASS | seven-file V2 artifact; Research-only flags/no evaluations verified |
| B.camera_subject_free_composition | W1/W2 | review | PASS | Current merged W1 spec and regression preserve distinct spatial roles; no mandatory exact tripod for ordinary claims |
| B.navigation_separation | W2/W4 | local | PASS | All required no-Directions/no-coordinate-substitution regressions preserved and passed |
| B.evidence_uncertainty_review | W2 | review | BLOCKED | #465: claim-by-claim evidence review and Batch04 human geography are pending; uncertainty must be retained |
| B.trilingual_semantic_review | W2/W4 | review | BLOCKED | #465: genuine human zh-TW/en/ja semantic signoff is PENDING |
| C.latest_w2_binding | W3/W5 | local | PASS | W3 real P01 fixture byte-identical to latest unchanged W2 canonical content |
| C.real_weather_provider | W1/W3 | provider | BLOCKED | #482 proves Seattle raw transport only; approved pilot real provider coverage/run/freshness/calibration remain incomplete |
| C.astronomy_source | W1/W3 | local | PASS | M6a model and 14 schema/model tests PASS; WINDOW only, not photography verdict |
| C.approved_auto_thresholds | W1/W2/W3 | review | BLOCKED | #467: canonical pilot AUTO, threshold and model binding are not approved |
| C.unknown_no_false_score | W3 | local | PASS | W3 negative unknown/missing/provisional/research-only tests PASS |
| C.closure_warning_only | W3/W4 | local | PASS | W3 open/closed invariant and W4 independent advisory regressions PASS |
| D.static_build | W4/W5 | local | PASS | Exact GitHub head seven-file static build and manifest PASS |
| D.real_catalog_load | W4 | browser | PASS | GitHub six real-W2 browser locale/device scenarios PASS |
| D.locale_device_browser | W4/W5 | browser | PASS | GitHub six Chromium zh-TW/en/ja desktop/mobile scenarios PASS; local EPERM six FAIL retained separately |
| D.empty_error_loading | W4 | browser | BLOCKED | W4 app.mjs:168 lacks a distinct loading state; delayed-fetch/error/empty browser matrix still needed |
| D.live_ui_contract | W4 | review | BLOCKED | #467: W4 live WINDOW/weather/evaluation path is not integrated |
| D.public_url_assets | W5 | public | PASS | GitHub integration local-isolation real canonical public HTTPS/assets probe PASS; no Task R deployment |
| E.actual_commit_ci | W5 | github | PASS | GitHub Actions head/actual checkout/parents verified |
| E.no_failed_or_skipped_tests | W5 | github | PASS | GitHub actual job log 169 PASS / 0 FAIL / 0 ERROR / 0 SKIP; local 163/6 retained |
| E.fail_closed_missing_input | W5 | local | PASS | W5 12 regressions and CLI missing/SKIP/evidence tests PASS |
| E.hosting_protection | Owner/W5 | review | UNVERIFIED | Branch protection 403; direct Hosting/Environment protection rules cannot be verified with current integration |
| E.approval_stage_defined | Owner/W5 | review | PASS | Six-stage runbook requires explicit owner approval; no approval granted |
| E.health_rollback_plan | W5 | review | PASS | Existing HTTP/browser commands plus build SHA256 manifest and V2-only restore procedure prepared; no deployment executed |
