# ChaseLights R4.2 B85 Production / Maintenance Handoff

Date: 2026-09-28 (Asia/Taipei)

## Start here

This file supersedes `B80_PRODUCTION_HANDOFF.md` as the current production / maintenance checkpoint after the Qingshui-mist and Qixingtan northward-view calibration work in B81–B85.

Before changing production:

1. inspect GitHub `main` and all open pull requests,
2. read this file,
3. read `B85_QIXINGTAN_OROGRAPHIC_PROXY.md`, `B84_QIXINGTAN_NORTHWARD_VIEWS.md`, and `B83_QIXINGTAN_DIRECTIONAL_CLOUD.md` before changing Qixingtan logic,
4. read `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md` and `RESEARCH_EVIDENCE_SPEC_R4_2.md` for evidence rules,
5. preserve Place -> Photography Opportunity -> Condition Variant -> Camera Zone/Viewpoint,
6. use `runtime_catalog_v004_r4_2.json` as the canonical production Opportunity catalog,
7. use `runtime_catalog_manifest_r4_2.json` as the expected-state validation snapshot,
8. keep unresolved current-state dependencies fail-closed.

`B80_PRODUCTION_HANDOFF.md` remains the detailed checkpoint for the B79 aurora-runtime release. B85 focuses on the subsequent Taiwan field-validation fixes.

## Verified production checkpoint

Repository: `gdrabbit137-ai/ChaseLights`

Public site: <https://chaselights.app/>

B85 release:
- PR #145 — MERGED
- code merge commit: `c9c4704557e81f7d5222dd3a0b10293a00b1bbcb`
- generated weather commit: `2a4e9d27842655000fe40810b04ce338b77302a8`
- post-merge Adapter — PASS
- post-merge Evidence Audit — PASS
- production Update Weather — PASS
- Pages deployment on code merge — PASS
- Pages deployment on final generated-weather commit — PASS

B85 PR validation before merge:
- Opportunity Adapter — PASS
- Evidence Audit — PASS
- Taiwan Candidate Weather — PASS
- Japan Candidate Weather — PASS
- US Candidate Weather — PASS
- Browser Smoke — PASS

Duplicate PR #143 was closed after #145 merged because #145 is the stricter implementation: low-confidence classification plus score cap 78.

Open PRs still requiring separate review:
- #140 — Qingshui morning-mist status copy
- #141 — Qingshui mist cliff-readability guard

Do not assume #140/#141 are superseded by B85; they concern `tw-034-P03`, not Qixingtan.

## Canonical catalog checkpoint

| Region | Curated Places | Opportunities | Variants | Viewpoint relations |
|---|---:|---:|---:|---:|
| Taiwan | 83 | 220 | 230 | 225 |
| Japan | 35 | 53 | 58 | 54 |
| United States | 70 | 111 | 111 | 111 |
| **Total** | **188** | **384** | **399** | **390** |

Current runtime-policy totals:
- `module_pending`: 122
- `preview_module_available`: 122
- `minimum_sufficient_available`: 134
- `prototype_pending_certification`: 2
- `hold`: 2
- `data_insufficient`: 2
- minimum-sufficient visibility profiles: 89

Recent Taiwan Opportunity additions after B80:
- B81: `tw-034-P03` 清水斷崖晨霧／雲霧山海
- B83: `tw-036-P03` 七星潭北望清水山／清水斷崖＋貼山雲帶
- B84: `tw-036-P04` 七星潭北望清水斷崖／清水山山海遠眺

## B81–B82 — Qingshui Cliff morning mist

B81 admits the morning-mist / misty-seascape subject only after Grade-A Place-specific evidence.

B82 adds optional north-facing multi-point spatial context:
- broad sector around 330° / 0° / 30°
- environmental proxy only
- not an exact cliff/fog intersection
- camera whiteout remains a veto
- if multi-point data is unavailable, the model falls back to the conservative B81 single-point candidate rather than inventing certainty

Open follow-up PRs #140/#141 should be evaluated separately before any merge.

## B83 — Qixingtan terrain-attached cloud-band subject

`tw-036-P03` is a separate researched subject, not a relaxed sunrise rule.

Evidence establishes that from Qixingtan the northward Qingshui Cliff / Qingshui Mountain view and mountain cloud/mist are real Place-specific photographic subjects.

Runtime:
- camera anchor: representative Qixingtan coast Camera Zone
- northward proxy bearings: 350° / 5° / 20°
- proxy distances: 8 / 15 / 22 km
- target samples must be materially elevated
- direct cloud-band detection prefers coherent target low-cloud / humidity / visibility contrast
- exact cloud/ridge overlap is never claimed

## B84 — separate clear mountain view from cloud-band view

`tw-036-P04` was added because a clear/readable northward mountain-seascape and a terrain-attached cloud band are different photographic outcomes.

P04 asks whether multiple elevated northward proxy samples remain readable across multiple bearings. It can succeed even when P03 cloud-band evidence is not resolved.

This prevents a good daytime Qixingtan mountain-seascape from being scored as a failed sunrise simply because the cloud-band sub-condition cannot be proven.

## B85 — low-confidence orographic cloud proxy

The 2026-09-28 13:00 field photo showed:
- clear/readable Qixingtan coast and sea,
- northward mountain layers,
- a visible terrain-attached / mountain-waist cloud band,
- partial ridge visibility rather than whiteout.

B84 production diagnostics for that hour showed:
- camera visibility: ~27 km
- camera low cloud: ~2%
- LCL planning proxy: ~699 m AGL / ~713 m ASL
- elevated northward target max elevation: ~1670 m
- terrain/LCL intersections: 3 elevated samples across 2 bearings
- minimum elevated visibility: ~5.6 km
- minimum elevated/camera visibility ratio: ~0.21
- maximum elevated low-cloud field: ~24%
- P04 mountain-seascape visibility remained readable

The direct P03 cloud thresholds still missed the real cloud band because the coarse grid did not resolve it. B85 therefore adds a fallback only when all of the following are true:

1. coast/camera grid is clear enough,
2. LCL planning proxy intersects at least 2 elevated targets,
3. intersections span at least 2 bearings,
4. minimum elevated visibility <= 8 km,
5. minimum elevated visibility <= 30% of camera visibility,
6. elevated low cloud >= 15% somewhere in the sector,
7. at least 2 elevated targets across 2 bearings remain readable.

The fallback is intentionally:
- `reason = orographic_cloud_proxy_candidate`
- confidence = `low`
- score capped at **78**
- never described as observed cloud
- never allowed to claim exact cloud/ridge overlap

Direct multi-point cloud evidence remains the higher-confidence path.

## Verified 2026-09-28 13:00 replay after B85

Final production output after the B85 weather refresh:

### Overall Qixingtan winner
- score: **86**
- Opportunity: `tw-036-P04`
- subject: 七星潭北望清水斷崖／清水山山海遠眺
- state: `directional_mountain_visibility_match`
- confidence: medium
- status: 北方山海視野條件良好；實際山稜遮雲仍需現場確認

### Terrain-attached cloud-band sibling
- score: **78**
- Opportunity: `tw-036-P03`
- state: `orographic_cloud_proxy_candidate`
- confidence: low
- status: 地形雲低信心候選；格點未直接解析雲帶，需現場確認
- camera visibility: ~27 km
- min elevated visibility: ~5.6 km
- elevated/camera visibility ratio: ~21%
- max elevated low cloud: ~24%
- terrain/LCL intersections: 3 samples / 2 bearings

This is the intended interpretation of the field photo:
- the broad northward mountain-seascape is strongly photographable,
- the attached cloud band is plausible and worth alerting,
- the cloud-band-specific score remains lower-confidence because the weather grid did not directly resolve the observed local cloud shape.

Before B83–B85, the same hour was effectively represented by the sunrise Opportunity and could score near the teens due to the time gate. That coverage error is now fixed without weakening the sunrise gate.

## Evidence boundary

Keep these distinctions explicit:

- Place-specific evidence establishes **what subjects exist**.
- Runtime weather estimates **when a researched subject may work**.
- A low LCL proxy is not an observed cloud base.
- Terrain intersection with an LCL proxy is not proof of a cloud band.
- Grid visibility / low cloud cannot guarantee every ridge segment is visible.
- A photographed cloud band is valuable ground truth for model validation, but one positive case is not enough to broadly loosen thresholds.
- Local fog at the photographer remains different from cloud on the distant mountain.
- P03 and P04 must remain separate Opportunities.

## Primary next-work queue

### 1. Build a reusable field-validation registry

The Qixingtan case should become the first structured regression record rather than remaining only in prose.

Recommended schema fields:
- case ID / Place / local timestamp
- camera direction
- observed subjects
- observed negative conditions such as no local whiteout
- captured forecast inputs / diagnostics
- expected Opportunity states
- confidence and known uncertainty
- source type: user field observation / official research / runtime snapshot

Do not store a user photo publicly by default. The structured observation can be sufficient unless explicit image publication is requested.

### 2. Review open Qingshui PRs #140 and #141

They address separate user-facing and readability issues for `tw-034-P03`.

Review them against current main rather than blindly merging stale branches.

### 3. Expand field validation before retuning B85

Collect both:
- positive P03 examples: visible terrain-attached cloud bands,
- negative P03 examples: clear mountain but no attached cloud band.

Prioritize false-positive control. If B85 proxy fires repeatedly on clear mountains without a cloud band, tighten the visibility-ratio / low-cloud / LCL-intersection contract before raising any scores.

### 4. Continue the B80 runtime-provider queue

After the Taiwan field-validation work:
- dynamic access providers,
- event-state providers,
- managed-lighting state,
- specialized environmental states,
- staged compatibility cleanup,
- detail-shard payload audit,
- favorites legacy retirement after observation window.

## Release gates

For Qixingtan spatial-weather changes:
- researched subject evidence must remain Grade A / admitted
- P03 and P04 remain separate
- direct cloud-band match stays distinct from low-confidence proxy match
- camera whiteout / meaningful precipitation remain blockers
- proxy fallback stays explicitly uncertain
- no 80+ score from the low-confidence B85 fallback without a future evidence-backed policy change
- Adapter PASS
- Evidence Audit PASS
- Taiwan Candidate Weather PASS
- Browser Smoke PASS
- production weather refresh PASS
- final generated-weather Pages deployment PASS

For all other runtime/provider changes, retain the release gates listed in B80.
