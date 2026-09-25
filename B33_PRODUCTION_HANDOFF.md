# ChaseLights R4.2 B33 Production Handoff

Date: 2026-09-25 (Asia/Taipei)

## Start here in a new conversation

Ask the new conversation to read this file first, then inspect current GitHub `main` and open pull requests before making changes.

Suggested prompt:

> 請先閱讀 `B33_PRODUCTION_HANDOFF.md`、`B29_RESEARCH_GUIDE_SCORING_HANDOFF.md` 與相關 batch 規格，確認 GitHub `main` 和 open PR 是否有更新，再依交接狀態分批繼續 ChaseLights 工作。

Do not assume commit SHAs or workflow state remain current after this handoff date. Verify them through GitHub before editing.

## Authoritative production state

- Repository: `gdrabbit137-ai/ChaseLights`
- Production branch: `main`
- Public site: <https://chaselights.app/>
- B33 release PR: [#12](https://github.com/gdrabbit137-ai/ChaseLights/pull/12) — MERGED
- B33 production merge commit: `8497fc1d60045528aac2df1c33a6676175f8b0f7`
- Post-release production weather commit: `649082242518d8c19eaf0529aa2a609815dd607a`
- Weather schema remains 9; Opportunity fields remain additive.
- `tw-063` remains retired.

Production validation checkpoints:

| Check | Result | GitHub Actions run |
|---|---|---|
| Opportunity adapter/integration | PASS | `36144452730` |
| Taiwan candidate weather, 83 Places | PASS | `36144452760` |
| Browser smoke | PASS | `36144453293` |
| Production weather refresh | PASS | `36145196232` |
| Pages deployment after B33 merge | PASS | `36145196447` |
| Pages deployment after refreshed weather | PASS | `36146123256` |

Live browser verification after final deployment confirmed:

- `https://chaselights.app/` redirects and loads successfully.
- Taiwan renders 83 active Place cards.
- `鯉魚潭`, `雲山水夢幻湖`, and `大農大富平地森林園區` are all searchable and visible.
- Current production update label at verification time was `09/25 22:06 [GMT+8]`.

## B33 inserted work — COMPLETE

B33 added three researched Hualien Places:

| Place ID | Place | Curated photographic outcome | Runtime policy |
|---|---|---|---|
| `tw-082` | 鯉魚潭 | 潭北公共湖岸的湖光、山景與平靜倒影 | `preview_module_available` via water-surface + visibility modules |
| `tw-083` | 雲山水夢幻湖 | 夢幻湖、落羽松與平靜倒影 | `preview_module_available` via water-surface + visibility modules |
| `tw-084` | 大農大富平地森林園區 | 平地森林廊道與林間光影 | `minimum_sufficient_available` via the manually curated visibility contract |

B33 catalog delta:

- Taiwan active Places: 80 -> 83
- Taiwan Opportunities: 189 -> 192
- Taiwan Condition Variants: 199 -> 202
- Taiwan profile-viewpoint relations: 194 -> 197
- Composite active Places: 104 -> 107
- Composite Opportunities: 220 -> 223
- Composite Condition Variants: 230 -> 233
- Composite profile-viewpoint relations: 225 -> 228

New IDs are fixed and must not be reused:

- Places: `tw-082`, `tw-083`, `tw-084`
- Opportunities: `tw-082-P01`, `tw-083-P01`, `tw-084-P01`
- Viewpoints: `tw-082-VP01`, `tw-083-VP01`, `tw-084-VP01`
- Variants: `VAR-202`, `VAR-203`, `VAR-204`

## B33 evidence and modeling constraints

Detailed source decisions are in `B33_HUALIEN_RESEARCH.md`. Preserve these rules:

### tw-082 鯉魚潭

- The representative Camera Zone is the public north-shore waterfront around `23.93493,121.50803`.
- Navigation uses the exact coordinate instead of a broad place-name search.
- Do not treat visitor-center hours as a hard closure for the whole public lake shore.
- The forecast may evaluate calm-water/reflection potential, but it must not guarantee a perfect reflection.

### tw-083 雲山水夢幻湖

- This is a private landscaped park.
- Current researched access window is `08:30–17:00`; current on-site rules take priority.
- Representative Dream Lake coordinate is `23.827018,121.51548` with `medium_high` confidence.
- The coordinate is not a verified vehicle entrance and must not be described as one.
- Photography must remain within legal visitor areas; accommodation/private zones are not public access.

### tw-084 大農大富平地森林園區

- Navigation target is the official visitor-center/entrance coordinate `23.6151728,121.4146215`.
- Representative photography/weather area is `23.6143836,121.4159714`.
- Recommendations use the official `08:00–17:00` service window.
- The park is described separately from the visitor-center closure schedule.
- Fireflies are date-specific, announcement/booking-dependent events. Do not create a regular firefly Opportunity or infer firefly visibility from weather.
- Wet leaves and moss may make paths slippery; this is an access/safety note, not a photography score booster.

## Files added or changed by B33

Primary data and research:

- `runtime_catalog_v004_r4_2_b33_hualien_additions.json`
- `B33_HUALIEN_RESEARCH.md`
- `regions.py`
- `opportunities.py`
- `opportunity_runtime.py`

Tests and deployment contracts:

- `test_opportunity_adapter.py`
- `.github/workflows/test_opportunity_adapter.yml`
- `.github/workflows/b30_candidate_weather.yml`
- `.github/workflows/b30_browser_smoke.yml`
- `.github/workflows/update_weather.yml`

Production-generated data after the release includes 83 Taiwan summary/detail entries and 83 per-Place Taiwan shards under `weather_details/tw/`.

## Product and runtime contracts to preserve

The governing product model remains:

`Place -> Photography Opportunity -> Condition Variant -> Viewpoint/Camera Zone`

Key rules inherited from earlier handoffs:

- Homepage discovery remains Place-first: Region/subregion -> Day -> ranked Places -> optional name search.
- Do not restore Scene/Theme as intersecting homepage filters.
- Place ranking is Opportunity-first; legacy Theme scoring is compatibility output only.
- A high score requires a dedicated runtime condition match or an explicitly curated minimum-sufficient contract.
- Never infer a minimum-sufficient contract automatically from Scene/Theme labels.
- Area/Camera Zone evidence must not be presented as a surveyed tripod point.
- Navigation coordinates, weather sampling coordinates, and Camera Zones may be different and must retain their separate meanings.
- Shooting times use the Place's local timezone. The header's Last Updated value uses the viewer/browser timezone.
- Visible claims must be supported by official research plus actual model/provider data. Do not claim fog-free conditions, exact alignments, reflections, fireflies, seasonal color, peaks, or safe access without corresponding evidence and runtime support.
- Weather details continue to load from per-Place shards; the large regional detail file remains a temporary fallback until separately retired.

## Open work and branch caution

At this handoff there are two open PRs:

### PR #11 — active Japan research chain

- PR: [#11](https://github.com/gdrabbit137-ai/ChaseLights/pull/11)
- Title: `Research jp-026 Izumo Taisha with separate camera and arrival states`
- Head: `codex/jp026`
- Base: `r4.2-b32-jp025-hagi`
- It does **not** target production `main` directly.
- Its documented target state is 26/35 researched Japan Places; production `main` still reflects the earlier Japan checkpoint.
- Before releasing this Japan chain, re-check the entire jp-025/jp-026 integration history against current `main`, including B33 catalog totals and workflow count assertions.
- Do not merge PR #11 into the integration branch and then assume production is updated; a separate current-main release PR and full CI/deployment cycle are required.

### PR #1 — stale historical release PR

- PR #1 predates the current production state and is non-mergeable.
- Do not use it as a source of truth or merge it into `main`.

## Recommended next batch

Resume the Japan research migration as a controlled integration/release batch:

1. Inspect the latest `main`, PR #11, and its `r4.2-b32-jp025-hagi` base.
2. Confirm exactly which Japan Places are already represented in each branch; do not rely only on batch document labels.
3. Integrate/rebase the Japan chain onto current production without dropping B33 Hualien data or current weather commits.
4. Recalculate all composite/Taiwan/Japan catalog counts and update exact assertions once, from actual catalog output.
5. Run adapter, Taiwan candidate weather, Japan candidate weather, and browser smoke on one final head.
6. Release to `main` only after navigation, access, timezone, score-eligibility, and research-pending counts match the intended Japan checkpoint.
7. Monitor production weather refresh and the second Pages deployment, then verify the live site in a browser.

Continue Japan work in small batches. Do not enable legacy Scene/Theme scores for unresearched Japan Places.

## Useful verification commands

```bash
python -m py_compile opportunities.py opportunity_runtime.py runtime_dependencies.py \
  spatial_weather.py marine_state.py tide_state.py access_state.py \
  shinhotaka_access.py yahiko_access.py taxonomy_v004.py regions.py \
  analyze_weather.py fetch_data.py test_opportunity_adapter.py

python test_opportunity_adapter.py
```

Before any production release, also run the candidate weather and browser workflows through GitHub Actions. Local adapter success alone is not enough because weather generation and live card rendering exercise network data and deployment behavior.

