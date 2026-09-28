# ChaseLights R4.2 B86 Production / Maintenance Handoff

Date: 2026-09-28 (Asia/Taipei)

## Start here

This file supersedes `B80_PRODUCTION_HANDOFF.md` as the current production / maintenance checkpoint after the Qingshui-mist and Qixingtan northward-view work.

Before changing production:

1. inspect GitHub `main` and all open pull requests,
2. read this file,
3. read `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md` and `RESEARCH_EVIDENCE_SPEC_R4_2.md`,
4. read `B83_QIXINGTAN_DIRECTIONAL_CLOUD.md`, `B84_QIXINGTAN_NORTHWARD_VIEWS.md`, and `B85_QIXINGTAN_OROGRAPHIC_PROXY.md`,
5. preserve the Place -> Photography Opportunity -> Condition Variant -> Camera Zone/Viewpoint model,
6. keep `runtime_catalog_v004_r4_2.json` canonical and `runtime_catalog_manifest_r4_2.json` as the expected-state snapshot,
7. keep unresolved provider state fail-closed,
8. do not promote a coarse atmospheric proxy into an observed-scene claim.

## Verified production checkpoint

- Repository: `gdrabbit137-ai/ChaseLights`
- Production branch: `main`
- Public site: <https://chaselights.app/>
- B83 Qixingtan directional cloud merge: `b650e9165c96b6ce8bf40c05ebc7e311f32b9c72`
- B84 Qixingtan northward mountain-view split merge: `bcae1f64a80bd90b2749579b31e0e65b3a14e13f`
- B85 low-confidence orographic-cloud proxy merge: `c9c4704557e81f7d5222dd3a0b10293a00b1bbcb`
- Current generated-weather checkpoint after B85: `2a4e9d278426...`

B85 PR validation:
- Opportunity Adapter — PASS
- Evidence Audit — PASS
- Taiwan Candidate Weather — PASS
- Japan Candidate Weather — PASS
- US Candidate Weather — PASS
- Browser Smoke — PASS

Post-B85 main validation:
- Opportunity Adapter — PASS
- Evidence Audit — PASS
- Pages deployment — PASS
- Production weather refresh — PASS

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

## B81 / B82 — Qingshui Cliff morning-mist runtime

B81 added the verified Qingshui Cliff morning-mist subject as a Place-specific Opportunity with conservative weather gates.

B82 added optional directional spatial context:
- broad north-facing proxy sector,
- compare the camera grid with northward environmental proxy points,
- preserve the camera-whiteout veto,
- keep missing multi-point data as a low-confidence fallback rather than silently declaring success,
- never claim exact mist/cliff overlap.

Two older open PRs remain at this checkpoint:
- PR #140 — clarify Qingshui morning-mist status copy
- PR #141 — guard Qingshui mist score by cliff readability

Review these against current `main` before merging; B81/B82/B83+ changed nearby runtime/UI semantics and stale diffs must not be merged mechanically.

## B83 — Qixingtan terrain-attached cloud Opportunity

Added `tw-036-P03`:

**七星潭北望清水山／清水斷崖＋貼山雲帶**

Place-specific evidence:
- Taiwan Tourism verifies Qixingtan can view Qingshui Cliff.
- Taiwan National Parks describes the northward view from Qixingtan toward the Pacific, Qingshui Cliff, and Qingshui Mountain, and records cloud/mist accumulating around Qingshui Mountain.
- Hualien tourism photography material supports sea/cloud/Central Mountain Range as an actual local photographic subject.

Runtime:
- camera anchor at Qixingtan,
- broad northward sector 350° / 5° / 20°,
- distance bands 8 / 15 / 22 km,
- elevated-target filtering,
- direct cloud-band candidate requires multiple stronger mountain-cloud signals than at the coast,
- exact cloud/ridge overlap is never claimed.

## B84 — separate “mountain visible” from “cloud band”

The 2026-09-28 13:00 field case proved that one binary P03 result was insufficient.

B84 added `tw-036-P04`:

**七星潭北望清水斷崖／清水山山海遠眺**

This keeps two distinct photographic outcomes:

1. P03 — terrain-attached cloud / mountain-cloud band
2. P04 — readable northward mountain-seascape

P04 uses the same broad northward sample geometry but different semantics:
- camera grid must be usable,
- multiple elevated northward samples across multiple bearings must remain readable,
- opaque / fog / very-low-visibility targets are not counted as readable,
- grid data still does not guarantee every ridge segment is cloud-free.

## B85 — low-confidence orographic-cloud proxy

The B84 production diagnostics still showed a P03 false negative at the actual 2026-09-28 13:00 field hour.

Field observation:
- Qixingtan coast / sea remained clear,
- northward mountains had a visible terrain-attached cloud band,
- mountains were not fully white-out.

Production diagnostics for 13:00 before B85:
- camera visibility about 27 km,
- camera low cloud about 2%,
- planning-grade LCL proxy about 699 m AGL / 713 m ASL,
- multiple northward elevated samples above that LCL proxy,
- elevated target max elevation about 1670 m,
- elevated minimum visibility about 5.6 km,
- elevated max low cloud about 24%,
- P04 mountain-seascape remained readable,
- direct P03 low-cloud/moisture threshold did not resolve the actual local cloud band.

B85 therefore added a **fallback only**, not a replacement for the direct cloud-band signal.

The fallback requires all of:
- clear/useable camera grid,
- at least 2 LCL/terrain intersections,
- intersections across at least 2 bearings,
- elevated minimum visibility <= 8 km,
- elevated minimum visibility <= 30% of camera visibility,
- elevated low cloud >= 15%,
- at least 2 still-readable elevated targets across 2 bearings.

Fallback output:
- reason: `orographic_cloud_proxy_candidate`
- confidence: `low`
- score cap: **78**
- explicit UI text that the grid did not directly resolve the cloud band
- no claim of observed cloud, exact cloud/ridge overlap, or guaranteed ridge visibility

## Production re-check of the original 2026-09-28 13:00 field case

After B85 production weather regeneration:

### P03 — terrain-attached cloud
- score: **78**
- state: `orographic_cloud_proxy_candidate`
- confidence: **low**
- camera visibility: 27.0 km
- camera low cloud: 2%
- LCL proxy: 699 m AGL / 713 m ASL
- terrain/LCL intersections: 3 targets / 2 bearings
- elevated min visibility: 5.6 km
- elevated min visibility ratio: 0.21 of camera visibility
- elevated max low cloud: 24%
- direct cloud signal: false
- orographic fallback: true

### P04 — northward mountain-seascape
- score: **86**
- state: `directional_mountain_visibility_match`
- confidence: **medium**

Interpretation:
- the model now correctly distinguishes “the broad northward mountain-seascape is strongly photographable” from “a terrain-attached cloud band is plausible but only weakly resolved by the forecast grid.”
- this matches the field photo substantially better than the old 14-point sunrise-only result.
- the cloud-band score is deliberately lower than the general mountain-seascape score because the cloud band itself is not directly resolved by the forecast grid.

## Important UI behavior after B85

The Place research panel already ranks and displays all researched Opportunities and their day scores, so P03 and P04 can both be inspected.

The main card / weather timeline still follows the active best Opportunity for the selected day/time context. This is intentional for now; do not casually duplicate every secondary Opportunity into the main card.

If future usability tests show users regularly miss a meaningful secondary subject, prefer a compact “other viable subjects” treatment rather than replacing the primary winner logic.

## Current modeling rules reinforced by this case

- Weather-grid accuracy and photographic-subject coverage are separate problems.
- A high coast visibility value does not prove mountain ridges are clear.
- A low point low-cloud percentage does not disprove terrain-attached cloud in nearby mountains.
- Cloud base / LCL estimates are planning proxies, not observations.
- Terrain intersection can support a probabilistic candidate only when paired with spatial weather contrast.
- A researched subject may have multiple mutually compatible photographic outcomes; model them as separate Opportunities when their runtime conditions differ.
- Ground-truth photos are for calibration and regression, not a substitute for Place-specific subject evidence.
- One positive field example is not enough to raise a low-confidence proxy into a high-confidence 80+ recommendation.

## Next-work queue

### 1. Accumulate Qixingtan ground-truth cases

For future field checks, record:
- local time,
- shooting direction,
- whether mountains are fully readable / partly obscured / white-out,
- whether a distinct terrain-attached cloud band exists,
- optional photo,
- production P03/P04 diagnostics at that hour.

Prioritize both positives and negatives. False positives are more important than further score inflation.

### 2. Revisit P03 thresholds only after more labels

Do not tune B85 again from the same 2026-09-28 image.

Useful future questions:
- Does 30% visibility ratio create false positives?
- Is 15% elevated low cloud too permissive?
- Should intersection count use distinct distance bands as well as bearings?
- Does the fallback remain conservative in winter fronts / rain bands?

### 3. Review open Qingshui PR #140 / #141

Rebase/re-evaluate their intent against B81/B82 and current status-copy conventions. Merge only if they still add value without weakening current fail-safe behavior.

### 4. Continue dynamic-access providers

This remains the highest-value general runtime backlog from B80.

### 5. Keep evidence/runtime boundaries explicit

Do not infer a new subject from terrain or weather alone. New subjects still require Place-specific evidence under `RESEARCH_EVIDENCE_SPEC_R4_2.md`.

## Release gates

For future Qixingtan / spatial-weather changes:
- Adapter PASS
- Evidence Audit PASS when catalog/evidence semantics change
- Taiwan Candidate Weather PASS
- Browser Smoke PASS
- production weather refresh PASS after merge
- missing spatial data => no high-confidence cloud-band verdict
- camera whiteout / heavy rain => fail closed
- exact target-zone verification remains false unless separately researched
- low-confidence orographic fallback must remain clearly labeled and capped unless new evidence justifies a policy change
