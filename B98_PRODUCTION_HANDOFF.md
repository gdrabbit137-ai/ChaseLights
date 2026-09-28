# ChaseLights R4.2 B98 Production / Maintenance Handoff

Date: 2026-09-28 (Asia/Taipei)

## Start here

This file supersedes `B95_PRODUCTION_HANDOFF.md` as the current production / maintenance checkpoint.

Before changing production:

1. inspect GitHub `main` and all open pull requests,
2. read this file,
3. read `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md` and `RESEARCH_EVIDENCE_SPEC_R4_2.md`,
4. read B83–B85 before changing Qixingtan P03/P04,
5. read B87–B88 plus B92–B93 before changing Qingshui mist,
6. read B89 before changing field-validation replay semantics,
7. read B90–B91 before changing Johnston Ridge / Denali access,
8. read B94 before changing Hehuan cloud-sea scoring,
9. read B95 before changing Opportunity-card score/time semantics,
10. read B96 before changing Hehuan elevation/LCL semantics,
11. read B97 before changing selected-date score/window copy.

## Verified production checkpoint

Repository: `gdrabbit137-ai/ChaseLights`

Public site: <https://chaselights.app/>

Current production main before this maintenance PR:

- main head: `fbf32892a99ec65053f995833009c749f823d8d1`
- latest functional Qingshui merge: `0b84a17a53454580a998278c373349cc79a1fbd2`
- latest generated weather update: `fbf32892a99ec65053f995833009c749f823d8d1`
- open PR count at checkpoint: 0

Recent functional mainline work:

- B92 Qingshui B81/B82 regression verification: `99ccd6e0614b4d21d0703515005d1f8002ac5006`
- B93 Qingshui directional contrast hardening: `9a4df1a7f781a76c2bdf1e4bf6f97f854534d623`
- B94 Hehuan cloud-sea commentary/scoring alignment: `680919f0e955f6af93c5c36c6db46d420a5be026`
- B95 Opportunity card clarity: `e2f0ebe191009d4ddcb3539069cd2bd6f010a62c`
- B96 Hehuan elevation/LCL wording: `98d34c509864c034a90c9953d28bb14ebcfa86e8`
- B97 selected-date labels: historical implementation commit `bef1b4e837deea2a49c99317722f73eae55bed2f` (originally mislabeled B96 in Git history; documentation corrected to B97)
- Qingshui negative spatial evidence / PR #174: `0b84a17a53454580a998278c373349cc79a1fbd2`

## Release verification around PR #174

PR #174 — "Port Qingshui negative spatial evidence onto current main" — was merged after these checks passed on its head commit:

- Opportunity adapter test — PASS
- Evidence audit — PASS
- Taiwan candidate-weather — PASS
- Japan candidate-weather — PASS
- US candidate-weather — PASS
- Browser smoke — PASS

After merge:

- main Opportunity Adapter — PASS
- main Evidence Audit — PASS
- scheduled weather refresh — PASS
- Pages deployment — PASS

## Qingshui Cliff morning mist — current effective contract

Affected Opportunity:

- `tw-034-P03` — 清水斷崖晨霧、雲霧山海
- `tw-034-P02` — 清水斷崖山海遠眺

Current behavior includes the effective B81 + B82 + B87 + B88 + B92 + B93 logic plus PR #174 negative spatial evidence.

Preserve these rules:

- P03 is morning-only; local time >= 11:00 is rejected.
- camera whiteout is a veto.
- low camera visibility without whiteout may be retained only as a conservative low-confidence candidate when spatial context is missing or inconclusive.
- camera visibility below 2.5 km remains capped at 68 with low confidence.
- north-sector proxy layout remains exactly 330° / 0° / 30° × 2.5 / 5.0 km.
- target-sector mist must be materially stronger than camera conditions to count as directional support.
- camera and target sharing the same fog code is not directional evidence by itself.
- broad regional fog without directional contrast must not be mislabeled as cliff-sector directional mist.
- a fully sampled, broadly clear target sector can be explicit negative evidence.

### Broad-clear negative spatial evidence

For `tw-034-P03`, the target sector is treated as explicit negative evidence when:

- at least 4 directional targets are valid,
- clear targets span at least 2 distinct bearings,
- at least two thirds of valid directional targets satisfy all of:
  - visibility >= 8 km,
  - low cloud <= 35%,
  - RH <= 88%,
  - no fog weather code,
- mist target count is zero.

When that condition is met within the P03 mist-candidate visibility range, P03 is ineligible with:

- reason: `directional_target_sector_lacks_mist_support`
- confidence: medium
- diagnostic: `directional_mist_negative_evidence = true`

Missing, insufficient, or inconclusive spatial data must not be treated as negative evidence; that path may still preserve the B81-style 68 / low-confidence fallback.

This negative-evidence rule is a planning veto, not proof that no narrow real fog ribbon exists outside the sampled proxy grid.

### P02/P03 transition

The regression contract preserves:

- low-visibility morning + inconclusive optional spatial context → P03 may remain 68 / low confidence,
- broad-clear target-sector evidence → P03 rejected,
- clear camera / recovered visibility around 20–30 km → P03 rejected and P02 may become the best weather Opportunity again,
- afternoon rows cannot resurrect P03.

## 2026-09-28 Qingshui provenance boundary

The reviewed 0.7–0.8 km Qingshui morning scenario remains a calibration/regression input derived from the 2026-09-28 review.

It is not a retained immutable production forecast snapshot and is not field ground truth.

Do not describe the regression fixture as if Open-Meteo permanently archived that exact historical row.

## Qingshui field-validation gap

There is still no `tw-034` field-validation registry case and no Qingshui replay fixture backed by an observed photo + exact capture time + same-time diagnostics.

Therefore current Qingshui thresholds are protected regression/product guards, not field-calibrated physical truth.

Do not loosen or tighten these thresholds from a single forecast review:

- 2.5 km camera readability guard,
- 8 km clear-target visibility,
- 35% low-cloud clear threshold,
- 88% RH clear threshold,
- minimum 4 valid targets,
- minimum 2 clear bearings,
- two-thirds clear coverage.

Next Qingshui calibration should collect both positive and negative real cases.

## Current field-validation checkpoint

Qixingtan remains the structured field-validation reference:

- canonical case: `FV-TW-036-20260928-1300-01`
- replay is a synthetic minimum reproduction derived from stored diagnostics,
- the original raw historical provider payload is not preserved,
- P04 remains the stronger clear mountain-seascape outcome,
- P03 remains lower confidence when the grid only provides an orographic proxy.

Do not generalize one Qixingtan case into Hehuan or Qingshui thresholds.

Hehuan still lacks a real photo + exact-time multi-point replay case.

## B96 — Hehuan elevation / LCL semantics

B96 is the canonical batch for:

- using curated Place / viewpoint elevation before provider-grid DEM in spatial cloud geometry,
- preserving 3417 m as the Hehuan Main Peak camera reference elevation,
- describing the dew-point-spread estimate as LCL / condensation height, not measured cloud base.

The legacy field name `cloud_base_agl` remains for compatibility.

## B97 — selected-date labels

The selected-date UI fix is now formally B97.

Keep these concepts distinct:

1. researched generic shooting-time guidance,
2. selected-date best forecast window,
3. selected-date best Opportunity score,
4. hourly 96H score at the currently viewed row,
5. score confidence.

Do not relabel a daily-best score as a current-hour score.

## Product/runtime rules to preserve

- `Place -> Photography Opportunity -> Condition Variant -> Viewpoint/Camera Zone` remains the product model.
- Dedicated Opportunity runtime evidence takes precedence over generic Theme semantics where subject-specific logic exists.
- Generic Theme scoring must not contradict a dedicated runtime state.
- Forecast-derived environmental proxies must not be presented as exact visual confirmation.
- Access remains separate from photographic-weather quality.
- Camera coordinates, navigation coordinates, and environmental proxy points may differ.
- Visible-light / darkness gates remain hard subject-specific boundaries where defined.
- Selected-date daily score, current hourly score, researched best-time guidance, and confidence are distinct concepts.
- Generated weather snapshots are refresh snapshots, not a complete immutable archive of every forecast revision.

## Recommended next work

1. Add the first Qingshui field-validation case when an observed image, exact capture time/direction, and same-time forecast diagnostics are available.
2. Prefer paired positive/negative Qingshui cases before changing the current spatial-veto thresholds.
3. Add a Hehuan cloud-sea field-validation case before recalibrating the 72–79 spatial cloud-sea band.
4. Continue access-provider work separately from weather-quality calibration.
5. Preserve batch numbering from this checkpoint onward: B96 = Hehuan elevation/LCL, B97 = selected-date labels, B98 = this production handoff.

## Verification commands

```bash
python -m py_compile opportunities.py opportunity_runtime.py runtime_dependencies.py \
  spatial_weather.py marine_state.py tide_state.py aurora_state.py access_state.py \
  shinhotaka_access.py yahiko_access.py johnston_ridge_access.py denali_access.py \
  taxonomy_v004.py regions.py analyze_weather.py fetch_data.py test_opportunity_adapter.py

python test_opportunity_adapter.py
```

Before any production release that changes runtime behavior, also run all regional candidate-weather workflows and browser smoke through GitHub Actions.
