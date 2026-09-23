# ChaseLights R4.2 B28 Completion Handoff

## Status

B28 P0 missing-place curation is complete on branch `r4.2-b28-p0-missing-places`.

Final validated code head: `13393e032b3e09e0bc67579d4c1be2e4f10c4a38`

GitHub adapter CI: PASS (run 35910563850).

## Catalog delta

Production/B27 baseline:
- 70 active Taiwan Places
- 173 Photography Opportunities
- 181 Condition Variants
- 178 profile-viewpoint relations
- tw-063 retired

B28 final:
- 80 active Taiwan Places
- 189 Photography Opportunities
- 199 Condition Variants
- 194 profile-viewpoint relations
- tw-063 remains retired

B28 addition payload only:
- 10 Places (tw-072 through tw-081)
- 16 Opportunities
- 18 Variants
- 16 profile-viewpoint relations

## Added Places

1. tw-072 南雅奇岩地質步道／奇岩海岸
2. tw-073 老梅綠石槽
3. tw-074 野柳地質公園
4. tw-075 外澳沙灘／龜山朝日
5. tw-076 龍磐公園／草原海岸
6. tw-077 石梯坪海蝕平台／壺穴群
7. tw-078 建功嶼／退潮石板道 — secondary/simple
8. tw-079 池西柱狀玄武岩／池西岩瀑九孔池
9. tw-080 帆船鼻大草原／海岬
10. tw-081 南竿鐵堡／海防礁岩 — secondary/simple

## Secondary/simple policy

User review determined that 建功嶼 and 南竿鐵堡 are not major landscape-photography destinations and should not receive the same runtime/model complexity as core scenic Places.

### tw-078 建功嶼
- Keep one simple Opportunity only: 退潮石板道景觀.
- Keep verified location / Camera Zone and official tidal-access reference.
- Runtime dependency reduced to tide + access.
- Removed dedicated sunset, marine-state and secondary intertidal Outcome modeling.
- Removed tw-078-P02; retired Opportunity/Variant IDs must not be reused.
- No dedicated Access Provider development priority is required unless future product needs justify it.

### tw-081 南竿鐵堡
- Keep one simple daytime Opportunity only: 海防景觀.
- Keep verified location and current official-hours/access note.
- Removed dedicated Blue Tears Opportunity tw-081-P02.
- No Blue Tears forecasting or night-access model should be built specifically for Iron Fort.
- Removed Opportunity/Variant IDs must not be reused.
- No dedicated Access Provider development priority is required unless future product needs justify it.

## Important runtime constraints preserved

- Area/Camera Zone evidence is used where no unique tripod point is justified.
- Long exposure is a Technique, not a predicted Theme.
- tw-073 Laomei remains module_pending until seasonal_foreground is implemented.
- tw-074 Yehliu does not expose ordinary sunrise because normal opening hours do not support a generic sunrise assumption.
- tw-075 Waiao uses broad dawn geometry; it does not claim exact Sun–Gueishan alignment.
- tw-076 and tw-080 Milky Way/stellar Opportunities do not claim exact foreground/Core alignment.
- tw-077 and tw-079 use relative tide-state logic; no absolute local chart-datum height is claimed.
- tw-078 stays simple; official tidal-access information is more important than sophisticated photo-condition scoring.
- tw-081 stays simple; daytime attraction information is sufficient for the current product.

## Forecast hint semantic safety

User review found that blue-hour cards for non-city Places could display phrases such as "城市燈火清晰無霧". The root cause was legacy scoring that treated every `blue_hour` Theme as a city condition.

B28 now enforces:

- `blue_hour` is scene-neutral. It uses only blue-hour / low-cloud / visibility wording.
- Blue-hour clear wording is emitted only when astronomy timing is valid and the relevant visibility / cloud / precipitation / wind inputs are present.
- If required weather fields are unavailable, the hint explicitly reports limited data instead of claiming a clear view.
- Architecture alone does not auto-enable `city_night`; only a `city` Scene does.
- A curated non-city Opportunity may retain legacy `city_night` compatibility when the photographic Outcome genuinely involves night illumination, but the displayed hint becomes generic "夜間景觀" wording rather than "城市燈火".
- Current reviewed non-city compatibility cases are:
  - tw-020 金龍山 — 盆地低雲琉璃光
  - tw-023 頂石棹 — 聚落琉璃光
  - tw-027 田寮月世界 — 夜間投光地景
  - tw-064 金門慈湖 — 對岸廈門夜景
- The phrase "無霧" was removed from city-night clear messaging; forecast visibility is described as "能見度良好" instead of an absolute local-fog claim.
- Automated tests assert that blue-hour output cannot contain "城市", "燈火" or "無霧", and non-city night Outcomes cannot emit city-specific status/indicator keys.

Latest semantic-hint QA: PASS on `82edd7801337c50ee1d06c4aeef462438729ee64` (workflow run 35911902281).

## Final QA

- Addition spot IDs: contiguous tw-072…tw-081
- Spot IDs unique: PASS
- Opportunity IDs unique: PASS
- Variant IDs unique: PASS
- Opportunity parent spot IDs consistent: PASS
- Declared addition counts equal actual counts: PASS
- Runtime registry validation: PASS
- Dependency inventory exact-match validation: PASS
- Adapter integration tests: PASS
- Final simplification CI: PASS
- Branch was not behind main at the last validation checkpoint.

## PR

Draft PR #4: R4.2 B28 P0 missing-place curation.

Do not merge if the branch becomes behind main due to an automated weather refresh; first merge/rebase the latest production weather snapshot and rerun adapter CI.

## Recommended next phase

After B28 merges into main, start R4.2 B29 Access Provider Seed Batch for Places where dynamic access materially changes whether a strong photographic Opportunity can be recommended.

Do not prioritize tw-078 or tw-081 merely because they have access notes. They are secondary/simple Places.

Suggested B29 priority:
1. existing high-value B25/B27 dynamic-access Opportunities with authoritative sources already identified
2. tw-052 reopening / construction-hold verification
3. tw-068 facility-hours behavior only if it remains in the catalog after the planned 朝日溫泉 vs 帆船鼻 review
4. other core scenic Places where access state materially gates a strong photographic Outcome

Do not mark any dynamic-access profile provider-ready until source identity, freshness, effective window, and closure semantics are tested.
