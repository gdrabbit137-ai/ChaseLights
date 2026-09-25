Continue ChaseLights R4.2 B32 from branch `codex/jp026`. Its integration
base is `r4.2-b32-jp025-hagi`.

Read first:
1. `handoff/B32_20260925/00_START_HERE/HANDOFF_README.md`
2. `handoff/B32_20260925/QA_STATUS.md`
3. `NAVIGATION_SPEC_R4_2.md`
4. `B32_JP_RESEARCH_BATCH13.md`
5. `B32_JP_RESEARCH_BATCH14.md`
6. `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md`
7. `LOCATION_AUDIT.md`
8. `regions.py`
9. `opportunity_runtime.py`
10. `test_opportunity_adapter.py`

Current Japan research is 26/35. The jp-026 checkpoint is green:
- Adapter: 36128165281
- Japan Candidate QA: 36128522907
- Browser Smoke: 36128731623
- Taiwan Candidate QA: 36128226766

Next research target: `jp-027 神戶六甲山`.

Research the actual photographic outcome and legal Camera Zone first. Separately
verify the practical arrival target. 六甲山 has materially different transport
and viewpoint possibilities, so do not select a Directions destination until
the specific composition and arrival mode are established.

Preserve these contracts:
- Camera Zone and Navigation Target are separate.
- Never build production navigation from `map_query`.
- No researched Opportunity means no photography score.
- Place-local shooting/access time uses JST.
- Missing fields remain absent.
- Access uncertainty fails closed.
- `jp-014` remains held at score 0 while the official photography restriction
  remains in force.

After the jp-027 implementation, run Adapter, Japan Candidate Weather, Browser
Smoke, and Taiwan Candidate QA if shared runtime or region behavior changes.
