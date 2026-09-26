# ChaseLights R4.2 B42 Production / Maintenance Handoff

Date: 2026-09-26 (Asia/Taipei)

## Start here

This file supersedes `B33_PRODUCTION_HANDOFF.md` as the current handoff checkpoint.

Before making changes:
1. inspect GitHub `main` and open pull requests,
2. read this file,
3. read `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md`, `RESEARCH_EVIDENCE_SPEC_R4_2.md`, and the relevant batch research files,
4. preserve the Place -> Photography Opportunity -> Condition Variant -> Viewpoint/Camera Zone model.

## Verified repository state at B42 start

- Repository: `gdrabbit137-ai/ChaseLights`
- Production branch: `main`
- Public site: <https://chaselights.app/>
- Open pull requests when B42 maintenance started: **0**
- Latest production weather commit observed before the B42 branch: `2240699f74a0ea1b727470c7f35bb82b7c5dce11`
- Latest evidence-gate code checkpoint observed on main: B41 commit `9e1fb220195c46a2fc6ac58b501d70a021f8d144`
- B39 completed the final high-risk Opportunity evidence audit.
- B40 closed the initial high-risk review-required backlog.
- B41 introduced the Opportunity evidence admission gate. B42 additionally fixes workflow triggering so new pull-request branches targeting `main` actually run the gate without being added to a historical branch allowlist.

Do not assume these SHAs remain current. Re-check main before release.

## Effective curated catalog checkpoint

The B42 manifest centralizes the expected runtime catalog state in:

`runtime_catalog_manifest_r4_2.json`

Current effective curated catalog:

| Region | Curated Places | Opportunities | Variants | Viewpoint relations |
|---|---:|---:|---:|---:|
| Taiwan | 83 | 217 | 227 | 222 |
| Japan migrated | 26 | 34 | 34 | 34 |
| US migrated | 0 | 0 | 0 | 0 |
| **Total** | **109** | **251** | **261** | **256** |

Important: these are curated Opportunity-catalog counts, not the full production Place-card inventory. Production still carries additional Japan/US Places whose photography research remains pending.

## Post-B33 changes now present on main

B33 is no longer the latest project state.

Notable later work includes:

- B34: 六十石山 enrichment with researched Camera Zones / additional Opportunities.
- B35-era enrichment: 鯉魚潭 and 雲山水夢幻湖 subject expansion plus 大農大富 subject/runtime refinements now represented in the effective catalog.
- Japan migration has reached `jp-026` in the curated Opportunity catalog.
- B39/B40: high-risk Opportunity evidence backlog completed.
- B41: evidence admission gate added so unclassified high-risk Opportunities cannot silently enter production.

At this checkpoint:
- 鯉魚潭 (`tw-082`) has 10 curated Opportunities.
- 雲山水夢幻湖 (`tw-083`) has 5 curated Opportunities.
- 大農大富平地森林園區 (`tw-084`) has 9 curated Opportunities.
- 六十石山 remains a single Place and includes the researched B34 Camera-Zone opportunities.

## B42 maintenance scope

B42 intentionally changes **structure and validation only**, not photography scoring semantics or user-visible UI behavior.

First maintenance batch:
- remove duplicated catalog constants/imports,
- move catalog expected counts/ranges/exact-geometry IDs into one manifest,
- make adapter validation compare actual effective-catalog output with the manifest,
- make adapter tests consume the same manifest instead of duplicating magic numbers,
- mark B33 as historical and point future conversations here,
- replace branch-name-only CI triggering with `pull_request -> main` coverage for adapter, evidence audit, candidate weather, and browser smoke workflows.

No scoring threshold, runtime eligibility rule, event date, access rule, navigation target, UI label, or weather-provider behavior should change in this batch.

## Product contracts that remain authoritative

- Place-specific evidence proves **what can be photographed**.
- Runtime/provider data estimates **when an already-researched subject may work**.
- Terrain, weather, Scene tags, or Theme tags must not create a Photography Opportunity.
- High-risk subjects require explicit Place-specific evidence.
- Place ranking remains Opportunity-first.
- Legacy Theme scoring remains compatibility output only.
- Camera Zone, weather sampling coordinate, and Navigation Target remain separate concepts.
- Only verified Navigation Targets may become exact Directions links.
- Missing optional research fields stay absent; do not generate generic filler.
- Event/wildlife/seasonal presence must not be presented as guaranteed unless the supporting runtime source actually establishes it.

## Technical-debt queue after this batch

Recommended order:

1. **Event calendar extraction** — move year-specific event/date windows out of `opportunity_runtime.py` into a provenance-aware event data file with verification/expiry metadata.
2. **Canonical catalog build** — collapse the growing B15+B28+B32+B33+B34+B35 layering into a generated effective runtime artifact while preserving batch files as research/audit history.
3. **Legacy regional weather-detail retirement** — after verifying shard stability, stop publishing/loading oversized `<region>_weather_details.json` fallback files.
4. **Frontend split** — split the monolithic `index.html` CSS/state/data/card/Place Guide/weather-modal code without changing rendering behavior.
5. **Favorite migration cleanup** — once legacy migration is proven stable, retire the old `chaselights_favs` compatibility state.
6. Continue Japan/US research migration under the existing evidence gate.

## Release gate for B42 maintenance

Before merging:
- `validate_curated_opportunities() == []`
- adapter/integration test passes,
- evidence admission audit passes,
- Taiwan/Japan candidate weather generation does not change catalog semantics,
- browser smoke passes,
- compare branch vs main confirms no generated weather data or scoring-output changes were accidentally committed.

After merge, verify the normal production weather refresh and Pages deployment separately.
