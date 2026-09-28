# ChaseLights R4.2 B95 Production / Maintenance Handoff

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
9. read `B95_OPPORTUNITY_CARD_CLARITY.md` before changing Opportunity-card score/time semantics.

## Verified production checkpoint

Repository: `gdrabbit137-ai/ChaseLights`

Public site: <https://chaselights.app/>

Recent mainline commits:

- B92 Qingshui verification: `99ccd6e0614b4d21d0703515005d1f8002ac5006`
- B93 Qingshui directional contrast hardening: `9a4df1a7f781a76c2bdf1e4bf6f97f854534d623`
- B94 Hehuan cloud-sea scoring/commentary: `680919f0e955f6af93c5c36c6db46d420a5be026`
- post-B94 generated weather: `68b0200c602133f28c1f0836f21e2f739afa55fb`
- B95 Opportunity card clarity: `e2f0ebe191009d4ddcb3539069cd2bd6f010a62c`

B94 PR #165 was merged after all PR checks passed.

Verified B94/B95 release checks:

- Opportunity Adapter — PASS
- Taiwan Candidate Weather — PASS
- Japan Candidate Weather — PASS
- US Candidate Weather — PASS
- Browser Smoke — PASS
- B94 production weather refresh — PASS
- B94 generated-weather Pages deployment — PASS
- B95 main Opportunity Adapter — PASS
- B95 Pages deployment — PASS

B95 is UI-only and does not require a new weather-generation commit; it reads the already-generated B94 daily Opportunity windows and confidence fields.

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
- directional mist must be materially stronger than the camera,
- no directional contrast must not silently promote a weak visibility-only candidate,
- the proxy is environmental context, not proof of exact cliff/fog overlap.

B92 records that the 2026-09-28 0.7–0.8 km Qingshui row is a calibration/regression scenario, not a retained production forecast snapshot.

No Qingshui field-validation replay exists yet.

## B94 — Hehuan Main Peak cloud-sea scoring

Affected Opportunity:

- `tw-019-P04` — 合歡主峰下方雲海與露出群峰

### Root cause fixed

The dedicated `spatial_weather_vertical_cloud` module could correctly detect a clear summit and cloudier lower terrain while the generic single-camera `cloud_sea` Theme baseline stayed low. That produced contradictory UI such as “key conditions match” beside a score around 48.

### Current B94 rule

When the lower-terrain spatial contract is available and eligible:

- condition state => `spatial_cloud_sea_candidate`
- status => `OPPORTUNITY_SPATIAL_CLOUD_SEA_CANDIDATE`
- score floor => 72
- score ceiling => 79
- confidence => medium
- add a positive lower-terrain cloud/fog evidence factor
- add an uncertainty factor explaining that the radial grid is only an environmental proxy

The normal visible-light gate still takes precedence. Before the cloud-sea visible-light window, B94 must not apply the 72-point floor.

The 72–79 range is a conservative product band. Do not promote this proxy to 80+ without stronger field validation.

## Verified 2026-09-29 Hehuan output

Post-B94 generated weather at 06:00 local:

- camera visibility: ~64.0 km
- camera low cloud: 2%
- RH: 58%
- wind: 0.25 m/s
- `tw-019-P03` 360° mountain panorama: 93, high confidence
- `tw-019-P04` cloud sea: 36
- P04 runtime reason: `lower_cloud_not_detected`
- P04 lower-terrain cloud evidence: 0 / 8

Therefore the cloud-sea Opportunity correctly does **not** claim that its dedicated conditions match at 06:00.

For the same date, P04's daily best forecast window is:

- 18:00–18:07 local
- score 72
- medium confidence
- condition `spatial_cloud_sea_candidate`
- 3 / 8 lower-terrain samples support cloud/fog
- maximum supporting vertical drop about 712 m
- uncertainty explicitly says the ring-grid proxy does not guarantee exact cloud placement or a continuous cloud sea

This is the key distinction that B95 now exposes directly in the Opportunity card.

## B95 — Opportunity card score/time clarity

The Place detail card previously showed:

- a daily score,
- a researched generic “適合時間”,

but not the actual forecast window that produced the daily score.

That made a score such as P04 = 72 easy to misread as the condition at the currently viewed 06:00 row, even though P04 at 06:00 is only 36.

B95 adds to each scored Opportunity card:

- `今日最佳窗口` from `window_start/window_end/timezone_abbr`,
- `信心` from `score_confidence`.

Keep these concepts separate:

1. `適合時間` = general researched shooting-time guidance,
2. `今日最佳窗口` = the selected date's actual winning forecast window,
3. `當日評分` = the score of that winning forecast window,
4. `信心` = confidence in that Opportunity result.

Do not relabel a daily-best score as a “current” score.

## LCL / condensation-height UI semantics

The field currently named `cloud_base_agl` in generated data is derived from:

```
max(60, (temperature_2m - dew_point_2m) * 125)
```

This is a dew-point-spread LCL / condensation-height proxy, not a measured or provider-supplied cloud base.

B94 changed user-visible labels to:

- zh-TW: `估算凝結高度` / `凝結高度`
- en: `Est. LCL` / `LCL`
- ja: `推定LCL` / `LCL`

Do not rename this back to “cloud base” unless the underlying data source changes.

## Remaining Hehuan evidence limits

- The Hehuan spatial profile still uses an 8-direction ring around the camera.
- The ring is not a verified view-sector polygon for the primary cloud-sea composition.
- No Hehuan field photograph + same-time raw multi-point replay fixture exists yet.
- The 72–79 band is a conservative product calibration, not a physical probability.
- Thresholds should be recalibrated only after multiple positive and negative field cases.

## Current field-validation checkpoint

Qixingtan remains the structured field-validation / replay reference:

- canonical case: `FV-TW-036-20260928-1300-01`
- replay is a synthetic minimum reproduction derived from stored diagnostics,
- it is not the original raw historical provider payload,
- P04 remains the stronger clear mountain-seascape outcome,
- P03 remains lower confidence when the grid only provides an orographic proxy.

Do not generalize one Qixingtan case into universal Hehuan or Qingshui thresholds.

## Product/runtime rules to preserve

- `Place -> Photography Opportunity -> Condition Variant -> Viewpoint/Camera Zone` remains the product model.
- Dedicated Opportunity runtime evidence takes precedence over generic Theme semantics where a subject-specific module exists.
- Generic Theme scoring remains compatibility output and must not contradict dedicated runtime state.
- Forecast-derived environmental proxies must not be presented as exact visual confirmation.
- Access remains separate from photographic-weather quality.
- Camera coordinates, navigation coordinates, and environmental proxy points may differ.
- Visible-light / darkness gates remain hard subject-specific boundaries where defined.
- Daily Opportunity score, current hourly score, researched best-time guidance, and confidence are distinct product concepts.
- Generated weather snapshots are not a complete immutable archive of every forecast revision.

## Recommended next work

1. Add a Hehuan field-validation case when a real cloud-sea photograph and exact capture time are available.
2. If the historical raw provider payload is unavailable, use a synthetic replay fixture but mark provenance explicitly.
3. Compare multiple positive and negative Hehuan cases before changing the 72–79 band.
4. Consider replacing the generic radial ring with researched directional valley/lower-terrain sectors if field evidence supports stable geometry.
5. Continue the access-provider backlog separately; do not mix access readiness into weather scoring.
6. When reviewing UI screenshots, always distinguish the Opportunity daily-best score from the selected hourly row.

## Verification commands

```bash
python -m py_compile opportunities.py opportunity_runtime.py runtime_dependencies.py \
  spatial_weather.py marine_state.py tide_state.py aurora_state.py access_state.py \
  shinhotaka_access.py yahiko_access.py johnston_ridge_access.py denali_access.py \
  taxonomy_v004.py regions.py analyze_weather.py fetch_data.py test_opportunity_adapter.py

python test_opportunity_adapter.py
```

Before any production release, also run the region candidate-weather workflows and browser smoke through GitHub Actions.
