# ChaseLights R4.2 B49 Production / Maintenance Handoff

Date: 2026-09-27 (Asia/Taipei)

## Start here

This file supersedes `B42_PRODUCTION_HANDOFF.md` as the current maintenance checkpoint.

Before making changes:
1. inspect current GitHub `main` and all open pull requests,
2. read this file,
3. read `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md`, `RESEARCH_EVIDENCE_SPEC_R4_2.md`, `NAVIGATION_SPEC_R4_2.md`, and the relevant batch research files,
4. preserve the Place -> Photography Opportunity -> Condition Variant -> Viewpoint / Camera Zone model,
5. do not infer a photographic subject from legacy Scene/Theme tags.

Do not assume commit SHAs or event dates in this handoff remain current. Re-check main before release.

## Production checkpoint carried forward

Canonical curated Opportunity catalog:
- Taiwan: 83 curated Places / 217 Opportunities / 227 Condition Variants / 222 viewpoint relations
- Japan: 26 curated Places / 34 Opportunities / 34 Condition Variants / 34 viewpoint relations
- US: 0 curated Places / 0 Opportunities
- Total: 109 curated Places / 251 Opportunities / 261 Condition Variants / 256 viewpoint relations

The full production Place-card inventory is larger than the curated Opportunity catalog:
- Taiwan active Places: 83
- Japan active Places: 35
- US active Places: 70

Canonical source of truth:
- `runtime_catalog_v004_r4_2.json` — active researched Opportunity definitions
- `runtime_catalog_manifest_r4_2.json` — centralized expected-state validation snapshot
- `runtime_evidence_registry_r4_2.json` — evidence/provenance classification
- `runtime_event_calendar_r4_2.json` — year-specific event/date/time gates

Historical B15/B28/B32/B33/B34/B35 catalog fragments remain research/migration history and are not independent production sources of truth.

## Maintenance completed after B42

### B43 — annual event calendar extraction
PR #82

Year-specific Hualien event/date/time gates were moved out of `opportunity_runtime.py` into `runtime_event_calendar_r4_2.json`.

The data file carries:
- gate kind,
- timezone,
- verified dates/ranges,
- time windows,
- verification timestamp,
- validity/expiry,
- source references.

Scoring thresholds and eligibility semantics were intentionally preserved.

### B44 — canonical runtime catalog cutover
PR #83

Production `opportunities.py` now reads `runtime_catalog_v004_r4_2.json` directly instead of rebuilding the effective catalog at runtime from B15+B28+B32+B33+B34+B35 layers.

`RESEARCH_EVIDENCE_SPEC_R4_2.md` now documents repository ownership/source-of-truth classes.

The B42 manifest remains an independent validation snapshot and must agree with the canonical catalog totals.

### B45 — regional weather-detail retirement
PR #84

Oversized regional 96-hour detail files were retired:
- `tw_weather_details.json`
- `jp_weather_details.json`
- `us_weather_details.json`

At the retirement checkpoint they totaled about 140.5 MB in the current tree.

The only persisted detailed forecast artifacts are now per-Place shards:
- `weather_details/tw/*.json` — 83 shards
- `weather_details/jp/*.json` — 35 shards
- `weather_details/us/*.json` — 70 shards

Transient provider-failure fallback is preserved:
- previous summary row comes from `<region>_weather.json`,
- previous detail row comes from the corresponding per-Place shard,
- publication still fails closed if either fallback is unavailable.

The browser no longer contains a legacy regional-detail fallback.

### B46 — weather modal opens at the current/next hour
PR #85

The 96-hour weather modal still retains historical rows, but initial scroll now targets the first non-history row.

Desktop and mobile layouts both mark a `data-now-anchor`.
Browser Smoke verifies that the modal actually scrolls and that the target row is not a past row.

### B47 — cloud-sea spatial inference hardening
PR #87

Cloud sea is now a narrowly defined forecast-derived environmental condition rather than a generic terrain/Scene-tag inference.

The exception is allowed only when:
- the Opportunity has a configured spatial-weather profile,
- a Camera Zone coordinate exists,
- the profile requires materially lower terrain (production minimum 250 m),
- at least two lower samples must contain coherent low-cloud/fog evidence,
- multiple surrounding samples are present,
- the camera itself remains clear.

Spatial weather now also requests camera temperature and dew point. A planning-grade dew-point-spread / LCL proxy is used as an additional `camera_in_cloud_risk` veto so a photographer standing in cloud/fog is not told that a visible sea of clouds exists.

Important evidence boundary:
- ordinary fog/mist still requires Place-specific photographic evidence,
- explicit evidence-registry outcomes still take precedence,
- the evidence audit records the cloud-sea exception as `derived_condition`, not as photographic evidence,
- the derived condition proves only “cloud layer below a clear camera,” not scenic composition, legal access, safety, or exact target geometry.

### B48 — frontend asset split
PR #89

The former monolithic `index.html` is split without intended behavior changes:
- `index.html` — DOM shell and external asset references
- `assets/app.css` — former inline style block
- `assets/app.js` — former inline application script

Adapter/static checks inspect the combined frontend source where appropriate.
Browser Smoke remains the behavior gate for filters, cards, Place Guide, navigation, weather modal, and shard loading.

## Contracts that remain authoritative

- Place-specific research proves what can be photographed.
- Runtime/provider data estimates when a researched subject may work.
- The only current narrow exception is cloud-sea environmental-state inference under the B47 spatial contract.
- Fog/mist is not part of that exception.
- Place ranking remains Opportunity-first.
- Legacy Theme scoring remains compatibility output only.
- Camera Zone, weather sampling coordinate, and Navigation Target are separate concepts.
- Only verified Navigation Targets may become exact Directions links.
- Missing optional research fields stay absent; do not synthesize filler.
- Event/wildlife/seasonal presence must not be presented as guaranteed unless the supporting runtime source establishes it.
- Expired annual event windows remain inactive until a new official year is curated.

## Favorite migration decision

Do not remove `chaselights_favs` compatibility yet.

Current browser state still migrates legacy name-based favorites to `chaselights_favs_v2` spot IDs. There is no migration-completion telemetry or account-level version marker proving all existing users have completed that conversion.

Safe next step, if this is revisited:
1. add an explicit migration-version strategy and regression coverage,
2. preserve unmatched legacy names across regions,
3. only retire the legacy key after a deliberate compatibility window.

The code is small; immediate removal has little payoff compared with the risk of silently losing old favorites.

## Japan research migration queue

Japan has 35 production Places; canonical research currently reaches `jp-026`.

Pending:
- `jp-027` 神戶六甲山
- `jp-028` 高野山
- `jp-029` 伊賀上野城
- `jp-030` 鳴門海峽漩渦
- `jp-031` 倉敷美觀地區
- `jp-032` 福岡城跡
- `jp-033` 唐津城
- `jp-034` 長崎哥拉巴園
- `jp-035` 福岡塔

Research already started for the first group:
- 六甲山：天覽台官方直接支持白天廣角展望、黃昏與神戶／大阪夜景；Camera Zone 可沿用已 cross-check 的天覽台座標。
- 高野山：官方資料直接支持壇上伽藍、根本大塔、秋季紅葉與蛇腹路季節夜間照明；年度照明日期不可自動跨年複製。
- 伊賀上野城：三重縣官方旅遊／照片資料直接支持白色三層天守、約 30 m 高石垣與春季櫻花。
- 鳴門海峽：官方潮見表明確表示漩渦不是全天存在，並給出大潮／中潮／小潮相對滿乾潮的最佳觀潮時間窗。現有 `tide_state` modes 不足以直接代表 tidal-current extremum，因此不得硬套低潮露出模型。
- 倉敷美觀地區：官方旅遊資料直接支持白壁／柳／倉敷川街景，以及季節固定時段的夜間景觀照明與水面映照。

Before admitting these Opportunities:
- verify a Place/Camera-Zone anchor,
- choose an existing runtime module only when its semantics actually match,
- otherwise keep the formula explicitly pending rather than approximating with an unrelated module,
- add high-risk evidence-registry coverage where required.

## Technical-debt / next-work queue

Recommended order after this checkpoint:

1. Finish Japan `jp-027`–`jp-035` research migration in small reviewed batches.
2. Add an explicit tidal-current/extremum contract before scoring Naruto whirlpool strength from tide data.
3. Browser Smoke CI optimization:
   - add missing model-impact path coverage such as `spatial_weather.py`, `marine_state.py`, `tide_state.py`, `taxonomy_v004.py`,
   - for UI-only PRs, reuse committed summary/shard fixtures instead of regenerating Taiwan+Japan weather,
   - preserve candidate-weather generation for model/data changes.
4. Revisit favorite migration only with a versioned migration plan.
5. Start US Opportunity research in small geographic batches after Japan coverage is complete.
6. Investigate per-Place detail payload size. At the B45 checkpoint Taiwan shards averaged about 1 MB raw JSON, with the largest near 3 MB; optimize only after field-level profiling proves safe removable duplication.

## Release gates

For model/data changes:
- `validate_curated_opportunities() == []`
- Adapter integration test passes
- Evidence Audit passes when evidence-sensitive files are touched
- Candidate Weather QA passes
- Browser Smoke passes
- compare branch vs main confirms generated weather output was not accidentally committed unless the change explicitly targets generated data

For UI-only changes:
- Adapter/static frontend regression passes
- Browser Smoke passes on desktop/mobile-relevant flows
- asset path changes must be covered by workflow path triggers

After merge:
- verify the production source tree contains expected summary/shard assets,
- verify no retired regional detail file is reintroduced,
- verify the public site after the normal weather refresh/deployment cycle.
