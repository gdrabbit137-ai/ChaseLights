# W5 Photography Topics First integration

Scope: independently import W4 #518 into reviewed main 67a154b163c3e9a868d07eccc35f46d37580be38. No merge/deployment authorized by this report. #517 stays a separate Draft at 52074b0590a521a1cc0aaa6666a1fa618606ca40; none of its W3/W5 runtime changes are imported or overwritten. This candidate is the main-based photography-subject increment only.

## Immutable source and gate

W4 #518 HEAD ec067573e7c21a52e40021e87661c7489172e629; all 21 changed files are owner-scoped. Final W4 tree d3af0d46635ec0d49e796a94e9f5671682ba1f6a / 108 tracked files. Prior W4 ca4e59cf5978347f1422fb1fd2d485c188b58edd, tree 70eb22ad22f3cad08aafab9ac71032ee8278139b / 92 files. The final owner tree is imported exactly, including original evidence and six screenshots. All 12 runtime/test SHA256 entries in source-provenance.json independently match current files. Original W4 logs record Node 56 + Chromium 88 = 144 PASS, 0 FAIL/SKIP. Those owner logs are prior evidence, not this candidate's full CI.

W5 deliberately updates commit, branch, PR, subtree, file count and previous-source metadata. Previously active historical Beta/R2 transition declarations are preserved under historical_owner_transitions; current rehearsal uses the existing strict W4 transition verifier. It verifies owner-only changes, ancestry, source/base/tree pins and real Git merge-tree without moving refs. W1, W2 and W3 pins/trees remain main's accepted versions. No gate bypass or lowered count. Node grows 49→56; source Chromium 82→88 and explicitly includes photography-topics-browser.mjs. Six new W5 public-source regression tests grow the total 329→348. Candidate package browser retains six device/locale cases and additionally traverses all eight topics. New public topic checks execute only against a published candidate manifest, never against the old Beta.

Read latest AGENTS.md, Research and Navigation R4.2, specs/v2 index, governance, ownership, topics/filter surface contract, free composition, access separation, V1-parity/two-pass progression and Cloud runbook. Existing current-head tests and release approval requirements remain binding.

## Three distinct verification scopes

1. Existing public Beta R2: ten immutable SHA256 entries reconstructed from actual merged R2 release a4c90f913483eba9dfefef2932a3b62fde7c0517. Its source_index_commit_sha is cf29288ce47e2cccb2fb2e1453ad193200996a95, not the stale first-Beta c10976eb... expected by the old smoke. Each public runtime file must match the R2 manifest. Catalog/index commit and revision are independently checked, with unchanged Research-only and canonical P01 checks. Public success in a PR proves only the existing R2 site, never deployment of #518.
2. Candidate package: build_static verifies exact merged owner trees and committed runtime bytes, writes its ten-file manifest and ships no Legacy assets. Chromium tests all three languages and both viewport classes against that package, including all eight subjects.
3. Postmerge public candidate: the push workflow builds an exact-current-commit manifest, requires every public runtime hash and six public browser scenarios including new topic content. Until that passes after an approved merge plus Pages publication, new features are NOT publicly verified. The shared unchanged index.html hash alone is insufficient; app/model/style/adapter hashes are all required.

## Bounded manual content review

W5 coding-agent manual semantic inspection covered name, description, targets, REQUIRED/QUALITY notes, GUIDANCE/VERIFY labels and independent access warnings for all eight actual canonical records in zh-TW/en/ja. This is not an invented human W1/W2 signoff: source human_semantic_signoff and human_geo remain PENDING. No additional field research or whole-site evidence review was performed.

| ID | Content and condition finding | Disposition for explicit Research-only browsing |
| --- | --- | --- |
| jp-010-P01 | Fuji visibility REQUIRED/GUIDANCE; lavender/kochia condition QUALITY/VERIFY. Seasonal plants are not guaranteed by date. English says summer; zh/ja specify early summer: minor precision difference, no fixed flowering date or current-bloom assurance. | Accept; wording precision is optional W2 follow-up |
| tw-016-P01 | Exposed ridge/distant mountains; discernibility required, clarity improves layering; no numeric visibility cutoff or verified exact camera point. Legal/safe-trail phrasing is conditional with separate warnings, not an assertion of current opening. | Accept |
| tw-026-P01 | Salt-pan sunset light required; colorful clouds optional. Permitted-area boundary uncertainty and original-lookout repair closure retained in all locales, outside weather conditions. | Accept |
| tw-026-P02 | Colorful clouds around sunset require actual verification, not a generic cloud fraction/date. Salt-pan lines improve composition; no current afterglow forecast. English afterglow is read with its explicit around-sunset wording. | Accept |
| tw-034-P02 | Cliff/Pacific discernibility required; low clouds/haze may reduce clarity; no quantitative guarantee. First-platform-only/other-trail restrictions remain independent warnings. | Accept |
| tw-036-P01 | Dawn over Pacific, no exact solar alignment; horizon cloud/visibility qualitative only; no cloud-percentage threshold. | Accept |
| tw-082-P01 | Actual visible reflection required; calm water/wind may improve it, no wind-speed promise; permitted shore framing remains conditional. | Accept |
| us-071-P01 | Skyline/Space Needle discernibility required; Rainier explicitly optional; dusk/city lights quality only, no asserted light-on minute. | Accept |

No material semantic conflict found requiring isolation. All eight remain research, not an approved GUIDE surface or selected-date recommendation. The three-language new UI explicitly says research awaiting review; REQUIRED/QUALITY describe roles, GUIDANCE/VERIFY describe modes, neither means a met condition. Imported AUTO/forged PASS cannot activate results. No new scores, Directions, thresholds or live model. Closure warnings cannot alter photography weather suitability.

## Local evidence and release disposition

Local W4 Node: 56 PASS. W5 Python infrastructure: 40 PASS. New W5 source-contract: 6 PASS. Static packaging, configuration validation, exact W4 source/tree checks and real immutable merge rehearsal PASS. Initial full local gate failed due missing jsonschema and local Chromium/default Playwright path; it is preserved as an environment failure, not a passing full-suite claim. Hosted Actions must establish final candidate acceptance and raw logs must be inspected. Exact final HEAD, tested merge parents, run URLs and final counts are reported in the Draft PR after execution.

Recommended increment after current-head CI and explicit project-owner acceptance: release only existing seven Places/eight Research-only topic descriptions, target lists and special-condition guidance. Do not wait for NWS/#517 or automatic forecast models. Merge the consolidated W5 candidate once, not #518 again; do not combine #517. Recheck latest main/HEAD, required reviews and hosting protections before merge. Existing Pages publishes main automatically: a merge is a deployment-affecting action. Obtain necessary approval first.

Rollback: record the healthy R2 W4 source/tree above; restore only apps/web-v2 from that immutable release in a reviewed recovery change, deliberately repin W4 and rerun the same complete gates. Preserve Legacy root/link, unrelated current weather and WeatherGrid, main's W1/W2/W3, and separate #517 work. Verify all ten restored hashes and six public locale/device scenarios. No automatic merge/deploy or protection changes are introduced.
