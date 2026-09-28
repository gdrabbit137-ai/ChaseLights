# ChaseLights R4.2 B94 Production / Maintenance Handoff

Date: 2026-09-28 (Asia/Taipei)

## Start here

This file supersedes `B91_PRODUCTION_HANDOFF.md` as the current production / maintenance checkpoint.

Before changing production:

1. inspect GitHub `main` and all open pull requests,
2. read this file,
3. read `B29_RESEARCH_GUIDE_SCORING_HANDOFF.md` and `RESEARCH_EVIDENCE_SPEC_R4_2.md`,
4. read B83–B85 before changing Qixingtan P03/P04,
5. read B87–B88 plus B92–B93 before changing Qingshui mist,
6. read B89 before changing field-validation replay semantics,
7. read B90–B91 before changing Johnston Ridge / Denali access,
8. read `B94_HEHUAN_CLOUD_SEA_COMMENTARY.md` before changing elevated cloud-sea scoring,
9. keep photographic weather, subject existence, access, transport, safety, and field confirmation as separate contracts.

## Verified production checkpoint

Repository: `gdrabbit137-ai/ChaseLights`

Public site: <https://chaselights.app/>

Recent production merges:

- B92 Qingshui verification: `99ccd6e0614b4d21d0703515005d1f8002ac5006`
- B93 Qingshui directional contrast hardening: `9a4df1a7f781a76c2bdf1e4bf6f97f854534d623`
- B94 Hehuan cloud-sea scoring / commentary: `680919f0e955f6af93c5c36c6db46d420a5be026`
- post-B94 generated weather: `68b0200c602133f28c1f0836f21e2f739afa55fb`

B94 PR: [#165](https://github.com/gdrabbit137-ai/ChaseLights/pull/165) — merged after all PR checks passed.

B94 release validation:

- Opportunity Adapter — PASS
- Taiwan Candidate Weather — PASS
- Japan Candidate Weather — PASS
- US Candidate Weather — PASS
- Browser Smoke — PASS
- main Opportunity Adapter — PASS
- production weather refresh — PASS
- code-merge Pages deployment — PASS
- generated-weather Pages deployment — PASS

## B92–B93 — Qingshui Cliff morning mist

Affected Opportunity:

- `tw-034-P03` — 清水斷崖晨霧、雲霧山海

Current effective behavior includes B81+B82+B87+B88+B92+B93.

Preserve these rules:

- morning-only gate remains before 11:00 local time,
- low visibility without whiteout may create a low-confidence candidate,
- sub-2.5 km camera visibility remains capped at 68,
- camera whiteout remains a veto,
- broad north-sector proxy bearings are `330° / 0° / 30°`,
- each bearing samples `2.5 km / 5.0 km`,
- directional fog/mist must be materially stronger than the camera; a fog code at one target is not enough when the camera has the same fog state,
- no directional contrast must not silently promote a weak visibility-only candidate,
- the proxy remains environmental context, not proof of exact cliff/fog overlap.

B92 also records that the 2026-09-28 0.7–0.8 km Qingshui row is a calibration / regression scenario, not a retained production forecast snapshot.

No Qingshui field-validation replay exists yet.

## B94 — Hehuan Main Peak cloud-sea scoring

Affected Opportunity:

- `tw-019-P04` — 合歡主峰下方雲海與露出群峰

### Problem fixed

The dedicated `spatial_weather_vertical_cloud` module could correctly detect:

- a clear summit camera,
- cloudier / foggier lower terrain,

while the generic single-camera `cloud_sea` Theme baseline still returned a low score. This produced contradictory UI such as “key conditions match” beside a score around 48.

### Current rule

When the lower-terrain spatial contract is available and eligible:

- condition state => `spatial_cloud_sea_candidate`
- status => `OPPORTUNITY_SPATIAL_CLOUD_SEA_CANDIDATE`
- score floor => 72
- score ceiling => 79
- confidence => medium
- include a positive factor summarizing lower-terrain cloud/fog evidence
- include an explicit uncertainty factor that the radial grid is only an environmental proxy

The 72–79 band is deliberate. Do not promote this proxy to 80+ until field validation supports stronger confidence.

The normal visible-light time gate still takes precedence. Before the cloud-sea visible-light window, B94 must not apply the 72-point floor.

### Verified 2026-09-29 production output

Post-B94 generated data show:

At 06:00 local time:

- visibility: ~64.0 km
- low cloud at camera: 2%
- RH: 58%
- wind: 0.25 m/s
- P03 360° mountain panorama: 93, high confidence
- P04 cloud sea: 36
- P04 runtime reason: `lower_cloud_not_detected`
- lower-terrain cloud evidence: 0 / 8
- therefore the cloud-sea Opportunity correctly does **not** claim that its dedicated conditions match at 06:00.

For the daily P04 best window:

- best time: 18:00 local
- score: 72
- condition: `spatial_cloud_sea_candidate`
- confidence: medium
- lower-terrain support: 3 / 8 samples
- maximum supporting vertical drop: about 712 m
- UI uncertainty explicitly says the ring-grid proxy does not guarantee exact cloud placement or a continuous cloud sea.

This resolves the contradiction visible in the pre-B94 screenshot.

## LCL / condensation-height UI semantics

`cloud_base_agl` is currently derived from:

```
max(60, (temperature_2m - dew_point_2m) * 125)
```

This is a dew-point-spread LCL / condensation-height proxy, not a measured or provider-supplied cloud-base height.

B94 therefore changes UI wording:

- zh-TW: `估算凝結高度` / `凝結高度`
- en: `Est. LCL` / `LCL`
- ja: `推定LCL` / `LCL`

Do not rename this back to “cloud base” unless the data source changes to an actual cloud-base product.

## Remaining B94 evidence limits

- The Hehuan spatial profile still uses an 8-direction ring at about 8 km.
- The ring is not a verified view-sector polygon for the primary cloud-sea composition.
- No Hehuan field photograph + same-time raw multi-point forecast replay fixture has been added yet.
- The 72–79 candidate band is a conservative product calibration, not a physical probability.
- A future improvement should use multiple positive and negative field cases before changing thresholds or confidence.

## Current field-validation checkpoint

Qixingtan remains the only structured field-validation / replay path currently used for this class of debugging:

- canonical case: `FV-TW-036-20260928-1300-01`
- replay is a synthetic minimum reproduction derived from stored diagnostics,
- it is not the original raw historical provider payload,
- P04 remains the stronger clear mountain-seascape result,
- P03 remains a lower-confidence terrain-cloud candidate when the grid does not directly resolve the attached cloud band.

Do not generalize one Qixingtan case into universal thresholds for Hehuan or Qingshui.

## Production rules to preserve

- Place -> Photography Opportunity -> Condition Variant -> Viewpoint/Camera Zone remains the product model.
- Dedicated Opportunity runtime evidence overrides generic Theme semantics where a subject-specific module exists.
- Generic Theme scores may remain compatibility output, but must not contradict a stronger dedicated runtime contract.
- A forecast-derived environmental proxy must not be presented as exact visual confirmation.
- Access must remain separate from photographic-weather quality.
- Camera coordinates, navigation coordinates, and environmental proxy points may differ and must keep separate meanings.
- Visible-light / darkness gates remain subject-specific hard boundaries where defined.
- Generated weather snapshots are not a complete immutable archive of every forecast revision.

## Recommended next work

1. Add a Hehuan field-validation case when a real cloud-sea photograph and exact capture time are available.
2. Store a synthetic replay fixture only if the historical raw provider payload is unavailable; mark provenance explicitly.
3. Compare positive and negative Hehuan cloud-sea cases before retuning the 72–79 band.
4. Consider replacing the generic radial ring with researched directional valley / lower-terrain sectors if field evidence supports a stable viewing geometry.
5. Continue the existing access-provider backlog separately; do not mix access readiness into weather scoring.

## Verification commands

```bash
python -m py_compile opportunities.py opportunity_runtime.py runtime_dependencies.py \
  spatial_weather.py marine_state.py tide_state.py aurora_state.py access_state.py \
  shinhotaka_access.py yahiko_access.py johnston_ridge_access.py denali_access.py \
  taxonomy_v004.py regions.py analyze_weather.py fetch_data.py test_opportunity_adapter.py

python test_opportunity_adapter.py
```

Before any release, also run the region candidate-weather workflows and browser smoke through GitHub Actions.
