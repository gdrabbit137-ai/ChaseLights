# Sequential photography spot expansion

Scope: United States, Japan, Taiwan. New research batches: at most five candidates. Finish admission review, required checks, merge, weather generation, deployment and live verification before starting another batch. Read current specifications and main every time. Do not infer completion from this historical checkpoint.

## Active inherited batch: WA-PR323

Checkpoint: 2026-10-02 Asia/Taipei.
PR: https://github.com/gdrabbit137-ai/ChaseLights/pull/323
Branch: feat/us-071-kerry-park
Status: validation repair; not admitted or deployed by this checkpoint.

This pre-existing PR has 26 proposed additions (us-071 through us-096), not seven as its older description suggests. Do not expand this inherited batch. Review its existing candidates in groups of at most five and record decisions before release; future new batches are capped at five total.

Candidate inventory (all Washington):
- us-071 Kerry Park; us-072 Golden Gardens Park; us-073 Alki Beach Park; us-074 Gas Works Park; us-075 Discovery Park.
- us-076 Hamilton Viewpoint Park; us-077 Dr. Jose Rizal Park; us-078 Myrtle Edwards Park; us-079 Snoqualmie Falls; us-080 Deception Pass State Park.
- us-081 Mount Rainier Paradise; us-082 Reflection Lakes; us-083 Sunrise & Sunrise Point; us-084 Tipsoo Lake; us-085 Ruby Beach.
- us-086 Rialto Beach / Hole-in-the-Wall; us-087 Hurricane Ridge; us-088 Hoh Rain Forest; us-089 Palouse Falls; us-090 Diablo Lake.
- us-091 Washington Pass; us-092 Artist Point; us-093 Picture Lake; us-094 Steptoe Butte; us-095 Cape Disappointment.
- us-096 Sun Lakes–Dry Falls.

Existing catalog entries contain the proposed photographic definitions. Their admission remains to be individually reviewed against source scope, evidence registry, navigation and runtime gates. This inventory is not an approval or a new source of evidence. No new candidate search occurred in this run; no candidate was newly accepted or rejected.

## Validation checkpoint

Inspected PR head e0d7ee3847df43adac4f3400175ade6f890fc4df. Browser smoke, Taiwan/Japan candidate weather, adapter, evidence audit and field intake checks succeeded at that head. US candidate workflow run 37002210755 failed before creating any jobs.

Root cause reproduced locally: us-085 through us-096 expected-ID entries were indented outside the YAML run block. Corrected only their indentation in commit 989c43abde3f87a4c1bd34a403a76c966e0aa662. Validation: original YAML parsing fails; corrected YAML parses; extracted Python AST parses; expected IDs remain exactly us-001 through us-096. No validation assertion was removed or relaxed.

Next: inspect CI on the latest branch head, especially B61 US Candidate Weather QA. Fix actual failures before merge. Review candidate provenance and access/navigation gates, then perform required production release checks. A green evidence audit alone does not certify each photographic claim. No production completion has been verified.

## Waiting existing batch: PR328

https://github.com/gdrabbit137-ai/ChaseLights/pull/328 is draft, branch spot-expansion-20261002, last inspected head e64e32dd5d5cbff086c7e124eddda7d5c407e19d.
Allocated there: tw-085 Nanzilin Trail; jp-036 Takachiho Gorge. Unallocated research leads in its description: Sanxiantai, Shirogane Blue Pond, Reflection Lakes, Laomei Green Reef, Shiroyone Senmaida, Sunrise Point.

Do not start or allocate these until WA-PR323 is complete. Reflection Lakes and Sunrise already overlap PR323 proposals (us-082/us-083); reconcile scope and avoid duplicate IDs/Places. Its old claim that only us-071 through us-077 are reserved is stale: PR323 currently reserves through us-096.

## Search coverage and stopping rule

No claim of exhaustive national coverage. Track country, administrative area, topic, sources and source dates when research resumes. Persist accepted/rejected/deferred decisions and reasons. Rotate countries and prioritize coverage gaps. Stop only after recorded coverage and a recheck produce no eligible candidates, no unresolved candidate reviews and no unfinished release; a CI wait or inaccessible source is not exhaustion.
