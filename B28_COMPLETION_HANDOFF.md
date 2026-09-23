# ChaseLights R4.2 B28 Completion Handoff

## Status

B28 P0 missing-place curation is complete on branch `r4.2-b28-p0-missing-places`.

Final validated head: `7d36d2f5a3f1b8b718591e0e56e5b5bb4f2d97e6`

GitHub adapter CI: PASS (run 35909453924).

## Catalog delta

Production/B27 baseline:
- 70 active Taiwan Places
- 173 Photography Opportunities
- 181 Condition Variants
- 178 profile-viewpoint relations
- tw-063 retired

B28 final:
- 80 active Taiwan Places
- 191 Photography Opportunities
- 201 Condition Variants
- 196 profile-viewpoint relations
- tw-063 remains retired

B28 addition payload only:
- 10 Places (tw-072 through tw-081)
- 18 Opportunities
- 20 Variants
- 18 profile-viewpoint relations

## Added Places

1. tw-072 南雅奇岩地質步道／奇岩海岸
2. tw-073 老梅綠石槽
3. tw-074 野柳地質公園
4. tw-075 外澳沙灘／龜山朝日
5. tw-076 龍磐公園／草原海岸
6. tw-077 石梯坪海蝕平台／壺穴群
7. tw-078 建功嶼／退潮石板道
8. tw-079 池西柱狀玄武岩／池西岩瀑九孔池
9. tw-080 帆船鼻大草原／海岬
10. tw-081 南竿鐵堡／海防礁岩

## Important runtime constraints preserved

- Area/Camera Zone evidence is used where no unique tripod point is justified.
- Long exposure is a Technique, not a predicted Theme.
- tw-073 Laomei remains module_pending until seasonal_foreground is implemented.
- tw-074 Yehliu does not expose ordinary sunrise because normal opening hours do not support a generic sunrise assumption.
- tw-075 Waiao uses broad dawn geometry; it does not claim exact Sun–Gueishan alignment.
- tw-076 and tw-080 Milky Way/stellar Opportunities do not claim exact foreground/Core alignment.
- tw-077 and tw-079 use relative tide-state logic; no absolute local chart-datum height is claimed.
- tw-078 Jiangong requires authoritative tidal-path access; generic tide percentile cannot substitute.
- tw-081 daytime Iron Fort access remains dynamic-access dependent.
- tw-081-P02 Blue Tears is an explicit access hold under current documented daytime operating hours; night access is not assumed.

## Final QA

- Addition spot IDs: contiguous tw-072…tw-081
- Spot IDs unique: PASS
- Opportunity IDs unique: PASS
- Variant IDs unique: PASS
- Opportunity parent spot IDs consistent: PASS
- Declared addition counts equal actual counts: PASS
- Runtime registry validation: PASS
- Adapter integration tests: PASS
- Branch is currently ahead of main and not behind main.

## PR

Draft PR #4: R4.2 B28 P0 missing-place curation.

Do not merge if the branch becomes behind main due to an automated weather refresh; first merge/rebase the latest production weather snapshot and rerun adapter CI.

## Recommended next phase

After B28 merges into main, start R4.2 B29 Access Provider Seed Batch.

Priority:
1. tw-078 Jiangong official tidal-path schedule/provider
2. tw-081 Iron Fort official attraction-hours/weather-control provider
3. existing B25/B27 dynamic-access profiles with authoritative sources already identified
4. then review tw-052 construction hold and tw-068 facility-hours behavior

Do not mark any dynamic-access profile provider-ready until source identity, freshness, effective window, and closure semantics are tested.
