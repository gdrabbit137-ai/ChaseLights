# ChaseLights R4.2 B56 Production / Maintenance Handoff

Date: 2026-09-27 (Asia/Taipei)

## Start here

This file supersedes `B49_PRODUCTION_HANDOFF.md` as the current production / maintenance checkpoint.

Before making changes:
1. inspect current GitHub `main` and all open pull requests,
2. read this file,
3. read `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md` and `RESEARCH_EVIDENCE_SPEC_R4_2.md`,
4. preserve the Place -> Photography Opportunity -> Condition Variant -> Viewpoint/Camera Zone model,
5. treat `runtime_catalog_v004_r4_2.json` as the canonical production Opportunity catalog,
6. treat `runtime_catalog_manifest_r4_2.json` as the expected-state validation snapshot.

## Verified repository state at B56 start

- Repository: `gdrabbit137-ai/ChaseLights`
- Production branch: `main`
- Public site: <https://chaselights.app/>
- Open pull requests at this checkpoint: **0**
- Latest observed main checkpoint: `6174e6115d9930dad60312aaffbfca687c1846a4`
- Do not assume this SHA remains current; automated weather commits may advance main.

## Canonical catalog checkpoint

Current canonical totals:

| Region | Curated Places | Opportunities | Variants | Viewpoint relations |
|---|---:|---:|---:|---:|
| Taiwan | 83 | 217 | 227 | 222 |
| Japan | 35 | 53 | 58 | 54 |
| US migrated | 0 | 0 | 0 | 0 |
| **Total** | **118** | **270** | **285** | **276** |

Important:
- all 35 Japan production Place cards now have individually researched Opportunities,
- Japan has **0 research-pending production Places**,
- individual Japan Opportunities may still remain `module_pending` when seasonal/event/access/provider data is not sufficient,
- the 70 US production Place cards remain research-pending and are intentionally absent from the curated Opportunity catalog.

## B50 — Japan jp-027 through jp-031

Merged research migration:
- jp-027 神戶六甲山
- jp-028 高野山
- jp-029 伊賀上野城
- jp-030 鳴門海峽漩渦
- jp-031 倉敷美觀地區

Research rationale is recorded in `B50_JP_RESEARCH_BATCH15.md`.

Key modeling boundaries:
- Rokko broad views use visibility-aware scoring and official Tenrandai access hours.
- Koyasan architecture can use local-scene scoring; seasonal foliage stays seasonal-state dependent.
- Iga castle architecture can use local-scene scoring; cherry blossom state is not inferred from month alone.
- Naruto whirlpools are not scored with the ordinary relative sea-level tide model. The relevant physical contract is tidal-current/extremum timing.
- Kurashiki daytime streetscape uses local-scene scoring; managed night lighting remains an explicit state dependency.

The Japan Candidate Weather workflow was also repaired for the B45 shard-only architecture and no longer reads the retired regional detail JSON.

## B51 — Japan jp-032 through jp-035

Merged final Japan migration:
- jp-032 福岡城跡
- jp-033 唐津城
- jp-034 長崎哥拉巴園
- jp-035 福岡塔

Research rationale is recorded in `B51_JP_RESEARCH_BATCH16.md`.

Important safety/access boundaries:
- Fukuoka Castle Tenshudai closure is not used as a Camera Zone/navigation destination while the official restriction is active.
- Karatsu public park access and paid keep-interior access are separate contracts.
- Glover Garden night photography depends on current-year night/event access; ordinary dates are not treated as permanently night-open.
- Fukuoka Tower interior recommendations use the official last-admission cutoff; exterior illumination remains a managed-lighting subject.

## B52 — weather summary/detail race recovery

The production screenshot showing:

`Weather detail version mismatch`

was traced to a static publication/cache race, not a scoring failure.

Summary and per-Place detail shards are committed together, but CDN/browser caches can briefly expose different generations.

Current frontend recovery contract:
1. detail network requests are versioned from the expected summary `updated_at`,
2. summary is re-fetched once when generations disagree,
3. the frontend never downgrades to an older summary,
4. the selected detail is retried once with cache busting,
5. failure after retry shows a localized friendly synchronization message rather than the raw internal mismatch string,
6. the modal re-derives the current summary metric after a summary resync.

Cache safety:
- version/cache-bust query parameters are used for the network request,
- Cache API storage uses the canonical unversioned shard URL,
- this preserves compatibility with existing cached shards and prevents per-version cache-key accumulation.

Browser Smoke deliberately injects a fake old summary generation and verifies automatic recovery.

## B53 — Browser Smoke acceleration

Browser Smoke no longer regenerates Taiwan + Japan weather for every frontend-only PR.

Current contract:
- PR changed files are inspected through the GitHub PR files API,
- UI/workflow-only changes use the already committed summary + per-Place shards,
- weather is regenerated when an output-affecting model/runtime/data file changes,
- manual workflow dispatch still regenerates weather,
- the workflow has read-only `contents` and `pull-requests` permission.

Output-affecting path coverage includes:
- `regions.py`
- `analyze_weather.py`
- `fetch_data.py`
- `opportunities.py`
- canonical catalog + manifest
- `opportunity_runtime.py`
- event calendar
- runtime dependencies
- access modules
- `spatial_weather.py`
- `marine_state.py`
- `tide_state.py`
- `taxonomy_v004.py`

Historical batch catalog fragments are no longer Browser Smoke inputs after the B44 canonical-catalog cutover.

## B54 — favorite migration sentinel

Legacy favorite compatibility remains supported:
- canonical key: `chaselights_favs_v2` (spot IDs),
- legacy migration input: `chaselights_favs` (names).

A versioned per-region migration sentinel now prevents the same unresolved legacy-name set from being rescanned on every weather refresh.

Behavior:
- each region scans unresolved legacy names at most once per migration version,
- unmatched names remain available for other regions,
- when legacy names are fully resolved/removed, the sentinel is cleared,
- removing a v2 favorite still removes matching legacy names so refresh cannot resurrect it.

Do **not** delete legacy compatibility yet without an explicit migration-retirement decision.

## B55 — slim per-Place detail runtime payload

Large per-Place shards were analyzed at field level.

Before B55, the three largest Taiwan shards were approximately:
- tw-082: 2.96 MB repository file size,
- tw-035: 2.75 MB,
- tw-084: 2.63 MB.

The dominant duplicated field was hourly top-level `opportunity_runtime`.

Every `opportunity_runtime[opportunity_id]` was already duplicated inside:

`opportunity_scores[opportunity_id].runtime`

For the three largest shards:
- 2,784 Opportunity/hour pairs checked,
- 0 missing nested runtime copies,
- 0 JSON mismatches.

Projected raw JSON reduction from removing only the duplicate top-level map:
- tw-082: about **26.9%**
- tw-035: about **21.7%**
- tw-084: about **28.3%**

B55 therefore:
- keeps `opportunity_runtime` internally during scoring/debug construction,
- keeps `opportunity_scores[*].runtime` in the published detail,
- removes only the duplicate top-level `opportunity_runtime` from published hourly rows,
- leaves `theme_scores` and legacy `tag_scores` untouched.

Taiwan and Japan Candidate QA now explicitly reject any generated published shard that leaks the duplicate top-level field.

Important deployment note:
- the B55 code is merged,
- existing committed weather shards are not rewritten by the merge itself,
- the reduced payload becomes visible in main/site data after the next successful production weather refresh.

## Current source-of-truth boundaries

- Place-specific evidence proves what can actually be photographed.
- Narrow documented derived-condition exceptions (for example B47 cloud sea) must remain explicit.
- Runtime/provider data estimates when an admitted Opportunity may work.
- Terrain/tags/elevation/weather alone must not invent a Photography Opportunity.
- High-risk subjects remain evidence-gated unless a documented exception applies.
- Place ranking is Opportunity-first.
- Legacy Theme output is compatibility output only.
- Camera Zone, weather sample point and Navigation Target are separate concepts.
- Only verified Navigation Targets may become exact directions.
- Year-specific events belong in the event calendar / current official event state.
- Missing optional research data stays absent; do not generate generic filler.

## Next optimization queue

Recommended order:

1. **Post-B55 production refresh verification**
   - confirm the next auto weather commit is generated from B55,
   - verify large Taiwan shard sizes actually drop,
   - spot-check that weather modals still load from the refreshed shards.

2. **Payload budget / regression reporting**
   - add non-invasive Candidate QA reporting for largest/median shard size,
   - consider a budget threshold only after observing normal variance.

3. **Legacy `tag_scores` review — do not remove silently**
   - `tag_scores` is byte-for-byte equivalent to `theme_scores` in sampled shards,
   - unlike B55 `opportunity_runtime`, it is explicitly marked V4 compatibility output,
   - removal requires an explicit compatibility/schema decision.

4. **US research migration**
   - 70 US production Place cards remain research-pending,
   - migrate in small evidence-backed batches,
   - do not promote legacy tags into Opportunities automatically.

5. **Further detail-payload projection**
   - `opportunity_scores` is now the largest remaining block in complex Places,
   - frontend currently reads only a subset for the timeline, but diagnostic/runtime detail may be valuable,
   - do not prune nested runtime or diagnostic fields without an explicit consumer/schema audit.

## Release gates

For runtime/catalog/data changes:
- Adapter/integration tests pass,
- Evidence Audit passes when evidence/catalog semantics change,
- Taiwan/Japan Candidate Weather pass where relevant,
- Browser Smoke passes,
- generated weather files are not accidentally committed from PR validation.

For frontend-only changes:
- Adapter passes,
- Browser Smoke passes using the B53 fast path,
- visual/state behavior is unchanged unless explicitly intended.

For weather-payload schema changes:
- Candidate QA must validate actual generated shards,
- Browser Smoke must render the weather modal successfully,
- preserve a clear compatibility path for any field intentionally retired.
