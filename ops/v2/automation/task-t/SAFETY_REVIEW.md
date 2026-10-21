# Task T — #497 safety acceptance and one real pilot

Owner W5. **BLOCKED: disabled, no live OpenAI call, no automatic merge/deploy.**
This follow-up is stacked on #497 `bec25989330f1dec555b29c86e0d65f6b95e43c3`;
it does not update that branch or rebuild its executor. Merge order, if the
user later approves: #497, then this narrow follow-up, then a fresh reviewed
activation policy. Do not enable #497's original scheduled live path alone.
This PR targets #497's task branch to show only Task T changes. After an approved
#497 merge, W5 must retarget/revalidate this follow-up against actual latest main;
do not merge it into or overwrite the original task branch during this task.

## Source review and real evidence

Initial reviewed main `38561c8b862542587ee7756f59075517afe37efe`; refreshed main
`1733a46b152e5760540f59b4d4c192824222ac48`. Non-generated code/spec blobs are
unchanged from Task P's reviewed main. AGENTS, both R4.2 specs, V2 specs/schemas,
Worker ownership and Release Gate match the source bytes already read; current
Worker/Release Gate were reread. Main movement was generated data only.

#497 remains open Draft at its specified SHA, #483 remains open Draft at
`543169a5e4c6df50a08fcc07c96a700bf49e7b15`. #495 W2 Task Q and #496 W1 Task R
remain open Draft at `c41567edcfa9efe95111f3306d6410f1934e7062` and
`ba57ede02bfe004f49ac4b14b570d29bf18b96fa`; neither supplies this wiring.
Recent PRs show no duplicate Task T executor. None is presumed merged.

Fetched #497 original real job logs again:

| Real Actions run | PASS | FAIL | ERROR | SKIP |
| --- | ---: | ---: | ---: | ---: |
| [Executor 38703631711](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38703631711) | 56 | 0 | 0 | 0 |
| [Foundation 38703631715](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38703631715) | 16 | 0 | 0 | 0 |
| [Integration 38703631686](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38703631686) | 157 | 0 | 0 | 0 |

Source head `bec2598…`; actual proposed merge tested was
`d6989bebe5644c826f64e51a59b8b1392ca73bb9`. These **229** cases prove PR
validation, not a live model call. Preflight explicitly returned BLOCKED/NOT_RUN.
The live job was inapplicable on PRs. No original feature is reimplemented.

## Findings and disposition

| ID | Finding | Disposition |
| --- | --- | --- |
| T01 | GitHub GET branches/main reports **protected=false** | **BLOCKED**. No protection is invented or changed. Activation now requires protected=true at the exact approved SHA; owner must establish and inspect main rules/bypass lists. |
| T02 | Original enabled policy could run via schedule, without one explicit live approval | Fixed for this pilot: manual dispatch only, exact task/main bound, owner-authored approval comment, merged activation-policy PR, successful current approval CI, matching approved executor/policy blobs, and approval recheck before publication. |
| T03 | A model-name regex excludes current Sol names; rates/tiers/cache writes were not pinned | Fixed with one explicit current model profile, Standard tier, bounded short-context input, cache-write upper rate, 10% processing margin, expiring price review and enforced run/lifetime reservation caps. |
| T04 | Generic trusted HTTP wrapper could express unnecessary GitHub mutations | Fixed: endpoint/data allowlist before network. Only one W5 JSON/state file, new task ref, non-force ledger ref and Draft PR writes. Main/protected refs, force, comments/self-approval, merge and deployment endpoints are rejected. |
| T05 | Request socket timeout is not a total wall deadline | Fixed with a Linux wall timer around connect/headers/body; 90 seconds max for the model request, plus 12-minute live-job cap. |
| T06 | App install, effective token scope and repository-side Secrets/Variables not visible here | **UNVERIFIED**; do not substitute connector credentials or request Admin/Secrets permission. Exact manual checklist below. |
| T07 | No verified real provider response or automatically published pilot PR | **BLOCKED/NOT_RUN**. Unit approvals/transports remain explicitly mocked. No model cost or token usage is fabricated. |

Existing owner checks, durable claims, refusal stopping, uncertainty retention,
SHA/spec reading, Draft publication and 157-case Release Gate are preserved.
All four actions in the credential-bearing workflow are pinned to the observed
official tag commit SHAs. Token-action pinned `action.yml` was read and confirms
repository restriction, token revocation default, and all four requested
permission inputs. The GitHub workflow token remains read-only.

## GitHub App permission checklist

| Permission/control | Required | Observed status |
| --- | --- | --- |
| Install only on gdrabbit137-ai/ChaseLights | Yes | UNVERIFIED |
| Contents | read/write for new Git objects/task/state refs | Design checked; effective install UNVERIFIED |
| Pull requests | read/write for Draft PR only | Design checked; effective install UNVERIFIED |
| Checks / Commit statuses / Metadata | read | Design checked; effective install UNVERIFIED |
| Administration, Secrets, Workflows-write, Actions-write, organization permissions | None | Must remain absent; actual install UNVERIFIED |
| Main protection with required CI/PR review; no App bypass | Yes | **MISSING protection signal: protected=false**; exact rules/bypass not verified |
| Dedicated task/state branches, no main write or force | Yes | Enforced in code; server rules require owner review |
| Token lifetime/revocation | Short-lived repository token, revoke after job | Pinned token action default checked; not exercised live |

GitHub App permissions are repository-wide, not path-scoped. Runtime mutation
guards enforce the narrower W5 pilot scope; the owner must also verify branch
rules because repository Contents-write alone does not establish main safety.
Do not weaken existing CI, exempt the App from main protections, or auto-approve.

## Secrets/configuration status

| Setting | Execution environment | GitHub repository |
| --- | --- | --- |
| V2_CODEX_APP_ID | MISSING | NOT_CONFIRMED |
| V2_CODEX_APP_PRIVATE_KEY | MISSING | NOT_CONFIRMED |
| OPENAI_API_KEY | MISSING | NOT_CONFIRMED |

No required setting is confirmed present. Runtime observations are current,
connected and enforced, with no configured secret/identity bindings. Connector
Secrets/Variables endpoint reads return **400 unsupported endpoint**, not 403;
this is not evidence of absent repository values or insufficient GitHub App
permissions. No App-authenticated request was attempted, so App authorization
is UNVERIFIED rather than a claimed permission failure. Shell OpenAI egress is
also not in the current allowlist; the authorized future run uses Actions.

## Current model and enforceable API budget

Official sources checked: [Codex models](https://learn.chatgpt.com/docs/models),
[GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
[API pricing](https://developers.openai.com/api/docs/pricing), and
[reasoning cost limits](https://developers.openai.com/api/docs/guides/reasoning).
The recommended profile is **gpt-6.1-sol / high / Standard (`default`)**.
Public documentation confirms Responses and Structured Outputs support; this
account's entitlement is UNVERIFIED without a real authorized credential.
GPT-5.3-Codex is marked deprecated; no silent fallback is configured.

Standard short-context USD per million: input 2.00, cached input 0.10,
cache writes 2.50, output 10.00. Reasoning consumes the output budget. Fast,
Ultrafast and long-context multipliers are excluded by the payload/input guard.

| Enforced control | Single-pilot value |
| --- | --- |
| Billable model requests, across the persistent ledger lifetime | **1** |
| Retry limit | **0**, including 429/5xx |
| Parallel live workflows | **1**, existing concurrency group |
| Input bound | **240000 tokens**, conservative UTF-8 serialized request bytes +8192 framing; checked before API |
| Output including reasoning | **4096 tokens**, max_output_tokens sent to provider |
| API timeout / live job | **90 seconds wall time / 12 minutes** |
| Cost cap | **USD 0.75 per run/day/ledger lifetime**, reserved before API |
| CI assessments | At most **3** manual read-only assessments, no further model calls |
| Price validity | Explicit UTC review/expiry fields; stale/future review blocks |

Worst-case reservation at the maximum accepted bound:
`(240000 × 2.50 + 4096 × 10.00) / 1000000 × 1.10 = USD 0.705056`.
Every input token is charged at the higher cache-write rate for this bound;
the multiplier adds 10% processing margin. No cache discount is assumed.
The actual current spec request must fit; input is never silently truncated.
Reservations survive uncertain calls and are not refunded. The ledger logs
actual token usage when supplied, model/response ID, timing, SHA and a
conservative usage-cost estimate, **not an invoice**. This cap covers reviewed
OpenAI token rates; GitHub runner billing/tax is separate. Changed prices or
unverifiable model/cost conditions require disabled policy and renewed review.

The concrete [single-pilot policy](../single-pilot-policy.json) remains
`enabled=false`; #497's original policy is also unchanged/disabled. A future
activation PR must freshly check prices, dates and model access, pass CI and be
merged only after explicit user approval. A disabled policy is not an approval.

## Precise owner setup and approval steps

Credential-dependent work stops here until the following are actually satisfied:

1. In repository **Settings → Rules → Rulesets**, establish an active main rule:
   PR review and existing required CI, prohibit direct/force updates/deletion,
   and **do not add this App as a bypass actor**. Keep task and ledger branches
   usable without weakening main. Verify branches/main now reports protected=true.
2. In GitHub **Settings → Developer settings → GitHub Apps**, use a dedicated App
   with the table's permissions; install it on **selected repository ChaseLights
   only**. Accept required permission updates and verify the installation.
   Create the PEM private key in GitHub; never send it in chat/PR/logs.
3. In repository **Settings → Secrets and variables → Actions → Variables**, set
   `V2_CODEX_APP_ID` to that App ID. Under **Secrets**, set
   `V2_CODEX_APP_PRIVATE_KEY` to its PEM and `OPENAI_API_KEY` to a restricted
   OpenAI project key. Check account/project model access and billing. Provider
   budget alerts are supplementary, not a substitute for executor limits.
4. W5 reviews/merges only with user authorization: #497, this follow-up, then
   the reviewed activation-policy PR setting the **single** policy enabled.
   Keep one task and the fixed limits. Record the merged activation PR number.
5. Fetch exact latest main SHA and the Git blob SHA of
   `ops/v2/automation/single-pilot-policy.json`. The owner account
   `gdrabbit137-ai` must **manually** add this one-line comment to the merged
   activation PR, replacing the public placeholders (not secret values):

   `APPROVE_SINGLE_W5_PILOT task=w5-provenance-receipt-v1 main=<40-char-main-sha> usd=0.75 model=gpt-6.1-sol policy=<40-char-policy-blob-sha>`

   Copy the comment's numeric ID from its `#issuecomment-…` link. A comment is
   used because an owner may be the PR author and cannot self-approve a GitHub
   review. The executor cannot write comments; no agent creates this approval.
   Edit/delete the comment to revoke it. It must belong to that merged PR,
   authored by the owner, and match the exact task/main/model/budget/policy.
6. Owner opens **Actions → V2 Bounded Codex Executor → Run workflow**, main,
   operation `run_pilot`; supply approved_task_id, approved_main_sha,
   approval_pr and approval_comment_id. Do not run a worker branch or schedule.
   A stale SHA, protection gap, missing secret, revoked approval, expired pricing,
   failed approval CI or executor/policy drift blocks before model spend.
7. Preserve actual run URL, ledger claim/reservation, real response/usage/timing,
   new task branch, **automatically created Draft PR**, GitHub CI and W5 result.
   The low-risk output is the existing W5 JSON **regression test data**, consumed
   by CI and source-bound validation; producing a fixture through a real model
   is different from faking the model transport. Nothing is labeled real E2E
   until the actual provider→Draft PR→CI chain is verified.
8. Use operation `assess_ci` to check that PR (same approval bindings, at most
   three polls); it cannot call the model. If main moves, stop for W5 revalidation.
   Do not reset claims, budgets or task IDs to force another request. A refused,
   timed-out, incomplete or uncertain request remains terminal for this campaign.

Real E2E now: **BLOCKED / NOT_RUN**. Missing environment credentials, unverified
repository App/settings/account access, unprotected main, unmerged Draft source,
disabled policy and absent explicit bound approval are independent blockers.
No real token/cost/response/pilot PR evidence is fabricated. Failure/refusal and
authorization tests are offline fakes, except the local wall-time interrupt.
Existing Release Gate remains unchanged at 157 cases. See the separate
[phased roadmap](ROADMAP.md); no W1–W5 bulk enablement is authorized.
