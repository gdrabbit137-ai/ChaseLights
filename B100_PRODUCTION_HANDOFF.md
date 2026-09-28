# ChaseLights R4.2 B100 Production / Maintenance Handoff

Date: 2026-09-28 (Asia/Taipei)

## Start here

This file supersedes `B98_PRODUCTION_HANDOFF.md` as the current production / maintenance checkpoint.

Before changing production:

1. inspect GitHub `main` and all open pull requests,
2. read this file,
3. read `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md` and `RESEARCH_EVIDENCE_SPEC_R4_2.md`,
4. read B83–B85 before changing Qixingtan P03/P04,
5. read B87–B88 plus B92–B93 before changing Qingshui mist scoring,
6. read B89 before changing field-validation replay semantics,
7. read B94–B96 before changing Hehuan cloud-sea / elevation / LCL behavior,
8. read B97 before changing selected-date Opportunity copy,
9. read `B99_QINGSHUI_FIELD_VALIDATION_INTAKE.md` before adding any Qingshui field-validation case.

## Verified production checkpoint

Repository: `gdrabbit137-ai/ChaseLights`

Public site: <https://chaselights.app/>

Current main:

- main head after B99: `2e7b413e4f47625204b64926679e56e21ac5a944`
- B98 handoff / numbering cleanup: `e6bf155ae8e52407d04014fa75cd87a6f95a8c8d`
- Qingshui negative spatial evidence: `0b84a17a53454580a998278c373349cc79a1fbd2`
- B99 Qingshui field-validation intake profile: `2e7b413e4f47625204b64926679e56e21ac5a944`

Open PR count at checkpoint: 0.

Verified post-B99 release state:

- Opportunity Adapter — PASS on PR #176
- main Opportunity Adapter — PASS
- Pages build — PASS
- Pages deploy — PASS

B99 does not change Opportunity scoring or forecast generation, so region candidate-weather and browser-smoke were not required by the touched-file workflow paths.

## Batch numbering checkpoint

Use these IDs going forward:

- B95 — Opportunity card clarity
- B96 — Hehuan elevation / LCL semantics
- B97 — selected-date score/window labels
- B98 — production handoff and numbering cleanup
- B99 — Qingshui field-validation intake contract
- B100 — this production handoff

The historical Git commit for selected-date labels still contains a B96 label, but documentation has been corrected to B97. Do not rewrite Git history.

## Qingshui Cliff morning-mist runtime contract

Affected Opportunities:

- `tw-034-P03` — 清水斷崖晨霧、雲霧山海
- `tw-034-P02` — 清水斷崖山海遠眺

Preserve:

- P03 morning-only gate before 11:00 local time,
- camera whiteout veto,
- low-visibility fallback only when optional spatial context is missing or inconclusive,
- sub-2.5 km camera visibility capped at 68 / low confidence,
- proxy layout 330° / 0° / 30° × 2.5 / 5.0 km,
- target-sector fog must be materially stronger than camera conditions to count as directional support,
- identical camera/target fog code is not directional evidence by itself,
- broad regional fog is not cliff-sector proof,
- sufficiently complete broad-clear target-sector evidence can veto P03,
- clear/recovered visibility can return the weather winner to P02,
- afternoon rows cannot resurrect the morning-mist subject.

### Broad-clear negative-evidence rule

Current target-sector veto requires:

- at least 4 valid directional targets,
- clear samples spanning at least 2 bearings,
- at least two thirds of valid targets satisfying:
  - visibility >= 8 km,
  - low cloud <= 35%,
  - RH <= 88%,
  - no fog weather code,
- zero mist targets.

When satisfied inside the P03 candidate range, runtime returns:

- `directional_target_sector_lacks_mist_support`
- medium confidence
- `directional_mist_negative_evidence = true`

This is a planning veto from environmental proxy coverage. It is not proof that a narrow real fog ribbon cannot exist outside or between sampled points.

## B99 field-validation registry change

Field-validation registry schema is now:

`field-validation-registry-r4.2-2`

The previous validator hard-coded Qixingtan-specific observed fields. B99 replaces that with data-driven `case_profiles`.

Current profiles:

- `qixingtan_northward_mountain_cloud`
- `qingshui_cliff_mist`

The existing Qixingtan case is explicitly tagged with the Qixingtan profile.

The Qingshui profile defines the required intake fields for a future real observation, including:

- camera whiteout,
- coast/sea readability,
- cliff or mountain-outline readability,
- visible mist/low cloud in the cliff sector,
- visible precipitation,
- camera visibility / low cloud / RH / LCL proxy / weather code,
- north-sector target counts,
- mist / directional-mist counts,
- clear target / bearing counts,
- `broad_clear_target_sector`,
- spatial availability / eligibility state.

## Ground-truth boundary

The registry still contains exactly **one admitted field case**:

- `FV-TW-036-20260928-1300-01` — Qixingtan

There is still **no admitted Qingshui field-validation case**.

The `qingshui_cliff_mist` profile is an intake contract only. It must not be interpreted as:

- proof that morning mist occurred at Qingshui,
- validation of the 2026-09-28 low-visibility regression row,
- proof that the proxy grid locates fog exactly on the cliff,
- field calibration of the current thresholds.

## Qingshui provenance boundary

The reviewed 2026-09-28 ~0.7–0.8 km scenario remains a calibration/regression input, not retained immutable production forecast ground truth.

Do not convert it into a field-validation case unless a real observation with exact capture time and sufficient same-time diagnostics is available.

## Next Qingshui field-validation work

Prefer multiple positive and negative cases before threshold changes.

Useful case classes:

1. visible morning mist around the cliff while cliff/coast remain readable,
2. low camera visibility but broad-clear north-sector evidence and no visible cliff mist,
3. camera whiteout / dense local fog,
4. recovered clear visibility where P02 should beat P03,
5. ambiguous narrow fog ribbon poorly represented by the proxy grid.

For every admitted case, preserve:

- exact offset-aware local capture time,
- camera direction / Camera Zone,
- structured non-identifying scene observations,
- production weather/data commit,
- same-time spatial diagnostics,
- model commit,
- expected Opportunity state/score/confidence,
- explicit limitations,
- replay provenance when available.

User-supplied images remain metadata-only by default and are not committed unless explicit publication authorization is recorded.

## Hehuan / Qixingtan boundaries

Hehuan:

- B94 cloud-sea spatial scoring band remains conservative at 72–79 when dedicated lower-terrain cloud evidence is eligible.
- B96 preserves curated 3417 m camera elevation and LCL wording.
- No real Hehuan photo + exact-time replay case exists yet.

Qixingtan:

- `FV-TW-036-20260928-1300-01` remains the canonical structured field-validation reference.
- Its replay is a synthetic minimum reproduction, not original raw historical provider data.
- Do not generalize one Qixingtan case into Qingshui or Hehuan thresholds.

## Product/runtime rules to preserve

- `Place -> Photography Opportunity -> Condition Variant -> Viewpoint/Camera Zone` remains the product model.
- Dedicated Opportunity runtime evidence takes precedence over generic Theme semantics where subject-specific logic exists.
- Forecast proxies are environmental evidence, not exact visual confirmation.
- Access and photographic-weather quality remain separate.
- Camera, navigation, and environmental proxy coordinates may differ.
- Selected-date daily best score, selected-date best window, hourly score, researched best-time guidance, and confidence remain distinct concepts.
- Generated weather snapshots are refresh snapshots, not a complete immutable history.

## Recommended next work

1. Add the first real Qingshui field-validation case when sufficient field evidence exists.
2. Prefer paired positive/negative Qingshui cases before recalibrating the 2.5 km readability guard or broad-clear veto thresholds.
3. Add a real Hehuan cloud-sea field-validation case before changing the 72–79 band.
4. Continue access-provider work separately from weather calibration.
5. Do not create synthetic field ground truth merely to increase registry coverage.

## Verification commands

```bash
python -m py_compile opportunities.py opportunity_runtime.py runtime_dependencies.py \
  spatial_weather.py marine_state.py tide_state.py aurora_state.py access_state.py \
  shinhotaka_access.py yahiko_access.py johnston_ridge_access.py denali_access.py \
  field_validation.py taxonomy_v004.py regions.py analyze_weather.py fetch_data.py \
  test_opportunity_adapter.py

python test_opportunity_adapter.py
```

Before production releases that change runtime behavior, also run the affected regional candidate-weather workflows and browser smoke.
