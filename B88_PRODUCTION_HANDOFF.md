# ChaseLights R4.2 B88 Production / Maintenance Handoff

Date: 2026-09-28 (Asia/Taipei)

## Start here

This file supersedes `B86_PRODUCTION_HANDOFF.md` as the current production / maintenance checkpoint after the Qixingtan field-validation work (B83–B86) and Qingshui Cliff mist-readability hardening (B87–B88).

Before changing production:

1. inspect GitHub `main` and all open pull requests,
2. read this file,
3. read `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md` and `RESEARCH_EVIDENCE_SPEC_R4_2.md`,
4. read `B86_FIELD_VALIDATION_REGISTRY.md` before adding field observations,
5. read `B83_QIXINGTAN_DIRECTIONAL_CLOUD.md`, `B84_QIXINGTAN_NORTHWARD_VIEWS.md`, and `B85_QIXINGTAN_OROGRAPHIC_PROXY.md` before changing Qixingtan logic,
6. read `B87_QINGSHUI_MIST_READABILITY.md` and `B88_QINGSHUI_MIST_CAP_HARDENING.md` before changing Qingshui mist logic,
7. preserve Place -> Photography Opportunity -> Condition Variant -> Camera Zone/Viewpoint,
8. keep unresolved provider state fail-closed,
9. do not promote planning proxies into observed-scene claims.

## Verified production checkpoint

Repository: `gdrabbit137-ai/ChaseLights`

Public site: <https://chaselights.app/>

Current code release:
- B88 merge commit: `bffe5d7728bf07bd5e5696a9ba3ae2827bef551e`
- final generated-weather commit: `20c35a249fa84420c9b3a745cd9fd956da1f6cab`

B88 pre-merge validation:
- Opportunity Adapter — PASS
- Evidence Audit — PASS
- Taiwan Candidate Weather — PASS
- Japan Candidate Weather — PASS
- US Candidate Weather — PASS
- Browser Smoke — PASS

B88 post-merge validation:
- Opportunity Adapter — PASS
- Evidence Audit — PASS
- production Update Weather — PASS
- Pages deployment on code merge — PASS
- Pages deployment on final generated-weather commit — PASS

Open pull requests at this checkpoint:
- none

## Canonical catalog checkpoint

Catalog counts remain unchanged by B87/B88:

| Region | Curated Places | Opportunities | Variants | Viewpoint relations |
|---|---:|---:|---:|---:|
| Taiwan | 83 | 220 | 230 | 225 |
| Japan | 35 | 53 | 58 | 54 |
| United States | 70 | 111 | 111 | 111 |
| **Total** | **188** | **384** | **399** | **390** |

B87/B88 modify runtime semantics and metadata for an existing Opportunity; they do not add a new Place or Opportunity.

## B83–B85 Qixingtan field-photo correction remains verified

The original 2026-09-28 13:00 north-facing Qixingtan field photo showed:
- coast / sea clear and readable,
- northward mountain layers visible,
- terrain-attached cloud band present,
- ridges partially visible rather than whiteout.

Final production replay after B88 still preserves the intended split:

### `tw-036-P04` — northward mountain-seascape
- score: **86**
- state: `directional_mountain_visibility_match`
- confidence: **medium**
- status: 北方山海視野條件良好；實際山稜遮雲仍需現場確認

### `tw-036-P03` — terrain-attached cloud band
- score: **78**
- state: `orographic_cloud_proxy_candidate`
- confidence: **low**
- status: 地形雲低信心候選；格點未直接解析雲帶，需現場確認

This preserves the key modeling boundary:
- broad mountain-seascape readability can be strong,
- local attached-cloud detail may remain low-confidence when forecast-grid resolution is insufficient.

The structured case is stored as:
- `field_validation_registry_r4_2.json`
- case ID: `FV-TW-036-20260928-1300-01`

The user photograph itself is not committed.

## B86 — field-validation registry

B86 added a separate registry for real-world validation observations.

Important distinction:
- `runtime_evidence_registry_r4_2.json`: what Place-specific photographic subjects are admitted,
- `field_validation_registry_r4_2.json`: how runtime behavior compared with an observed real scene.

Field observations:
- may validate / calibrate runtime behavior,
- may become regression cases,
- do **not** bypass the Place-specific evidence gate,
- should remain metadata-only for user photos unless explicit publication permission exists.

The registry is machine-validated by `field_validation.py` and included in Adapter CI.

## B87 — Qingshui Cliff mist subject-readability guard

Opportunity:
- `tw-034-P03 — 清水斷崖晨霧、雲霧山海`

Problem reproduced before B87:
- camera-grid visibility around 0.6–0.9 km,
- directional mist proxy supported mist,
- old model could still score the Opportunity at 88,
- but the cliff / mountain / coastline could plausibly lose too much structure.

B87 introduced:
- `min_camera_readability_km = 2.5`
- below that threshold, a mist-supported case remains only a low-confidence planning candidate,
- `subject_readability_uncertain = true`
- `score_hint = 68`
- clearer Opportunity-specific status text.

The 2.5 km threshold is a conservative planning guard derived from the current proxy geometry. It is **not** a claimed physical camera-to-cliff distance.

## B88 — hard score ceiling for unreadable Qingshui mist cases

B88 fixes an important scoring loophole.

The minimum-sufficient scoring framework normally does:

`final score = max(generic Theme baseline, dedicated score hint)`

Therefore B87's `score_hint = 68` was not, by itself, guaranteed to prevent a future generic fog/mountain Theme baseline above 68 from lifting the Opportunity back into the 80+ band.

B88 makes the policy explicit:

When:
- `subject_readability_uncertain == true`

then:
- **final Opportunity score <= 68**

This ceiling overrides the generic Theme baseline.

B88 also ensures visibility-only mist candidates below 2.5 km receive the same readability-uncertain flag without falsely upgrading the evidence for actual mist.

## Verified Qingshui production behavior after B88

Final production weather output after B88:

### 2026-10-01 05:00
- camera visibility: ~0.6 km
- low cloud: ~100%
- `tw-034-P03`: **68**
- state: `minimum_sufficient_mist_candidate_uncertain`
- reason: `camera_visibility_too_low_for_cliff_readability`
- `subject_readability_uncertain = true`

### 2026-10-01 06:00
- camera visibility: ~0.9 km
- low cloud: ~88%
- `tw-034-P03`: **68**
- same low-confidence readability-uncertain treatment

### 2026-10-01 07:00
- camera visibility: ~1.5 km
- low cloud: ~70%
- `tw-034-P03`: **68**
- same low-confidence readability-uncertain treatment

At 08:00, visibility rises strongly and the mist Opportunity no longer matches the mist-specific contract; the model correctly does not carry the 68-point candidate forward.

A dedicated regression test additionally uses an intentionally high generic Theme baseline of 85 and verifies the final Opportunity score is still capped at 68.

## Evidence / runtime boundaries reinforced by B87–B88

Keep these explicit:

- Mist being likely is not enough; the intended cliff / mountain / coast composition must remain plausibly readable.
- Directional mist proxy points are environmental proxies, not observed fog and not exact cliff/fog intersections.
- A low visibility value alone must not be described as observed mist.
- Camera whiteout remains a veto.
- The 2.5 km readability threshold is a conservative planning guard, not measured subject distance.
- The 68 limit is a **final score cap**, not merely a score hint.
- A field photo is validation evidence for runtime behavior, not automatic Place-subject admission evidence.
- Qixingtan P03 and P04 remain separate photographic outcomes and must not be collapsed.

## Primary next-work queue

### 1. Accumulate field-validation cases before more threshold tuning

For Qixingtan, prioritize both positive and negative labels:
- visible terrain-attached cloud band,
- clear mountain with no attached cloud band,
- mountain whiteout,
- local camera fog,
- partial ridge visibility.

For Qingshui, useful cases include:
- mist with readable cliff,
- mist with nearly invisible cliff,
- no mist but low visibility,
- directional mist signal without usable subject outline.

Do not retune B85 or the B87/B88 2.5 km guard from the same single case repeatedly.

### 2. Extend field-validation from schema validation toward replay fixtures

The current registry validates structure, references, score expectations, privacy boundaries, and historical snapshot metadata.

A useful future extension is an optional machine-replay fixture containing only the minimum non-identifying raw model inputs needed to reproduce an Opportunity decision. Keep this separate from user image storage.

### 3. Continue dynamic-access providers

After the Taiwan field-validation work, continue the general runtime-provider queue inherited from B80:
- dynamic access providers,
- event-state providers,
- managed-lighting state,
- specialized environmental states.

### 4. Continue payload / compatibility cleanup conservatively

Retain:
- detail-shard payload audit,
- staged compatibility cleanup,
- favorites legacy retirement only after its observation window.

## Release gates

For Qixingtan spatial-weather changes:
- Place-specific subject evidence remains admitted,
- P03 cloud-band and P04 mountain-view remain separate,
- low-confidence orographic fallback remains explicitly uncertain,
- no 80+ score from that fallback without new evidence,
- camera whiteout / meaningful precipitation remain blockers,
- Adapter PASS,
- Evidence Audit PASS when evidence semantics change,
- Taiwan Candidate Weather PASS,
- Browser Smoke PASS,
- production weather refresh PASS,
- final generated-weather Pages deployment PASS.

For Qingshui mist changes:
- subject evidence remains Grade A / Place-specific,
- camera-whiteout veto remains,
- sub-2.5 km readability-uncertain cases remain <= 68 unless future ground truth justifies a reviewed policy change,
- 2.5 km is documented as a planning guard, not physical subject distance,
- directional mist proxy remains non-observational,
- Adapter PASS,
- Evidence Audit PASS,
- Taiwan Candidate Weather PASS,
- Browser Smoke PASS,
- production weather refresh PASS,
- final Pages deployment PASS.
