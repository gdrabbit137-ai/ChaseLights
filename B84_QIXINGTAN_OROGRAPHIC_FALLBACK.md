# B84 — 七星潭貼山雲：地形抬升 fallback

## 問題

B83 已新增 `tw-036-P03`「七星潭北望清水山／清水斷崖＋貼山雲帶」，並使用北向多格點低雲／高濕／能見度差異來判斷。

但把 2026-09-28 13:00 的現場照片回放到 B83 production runtime 後，仍出現明確 false negative：

- 現場：海岸與海面清楚，北方山區有明顯貼山低雲帶，山峰仍部分露出。
- ChaseLights 點位氣象：visibility 約 27 km、低雲約 2%、RH 約 72%、規劃級 cloud-base/LCL proxy 約 699 m AGL（約 713 m ASL）。
- B83：`tw-036-P03` base mountain-view score 約 86，但 northward target grid 沒有直接解析低雲，因此 runtime miss，最終只剩 54 分。

這表示「題材 coverage」已補齊，但 coarse-grid 的山區雲解析度仍會造成 false negative。

## B84 原則

B84 不把單點低雲、濕度或低凝結高度直接當成「山上已有雲」。

Runtime 仍然優先使用 B83 的直接方向性多點雲訊號。

只有當直接格點沒有解析出雲帶時，才允許一個低信心 fallback：

> 海岸拍攝點本身清楚，而海岸氣團的規劃級 LCL／凝結高度落入多個北向山地 proxy 的高程範圍，則標示「地形抬升貼雲潛勢」。

這是 orographic-cloud potential，不是 cloud observation。

## Fallback gate

`tw-036-P03` 目前要求：

- camera visibility >= 15 km
- camera low cloud <= 20%
- camera RH >= 65%
- precipitation < 0.5 mm
- planning-grade condensation-height proxy: 350–1400 m ASL
- 至少 2 個北向高地 proxy 的 DEM 高程進入 condensation-height ±150 m 的交會範圍
- camera 不可白牆

若成立：

- runtime `eligible = true`
- `candidate_source = orographic_lcl_terrain_fallback`
- `confidence_hint = low`
- score cap = 82
- UI 必須明確說明「格點沒有直接解析出雲帶」
- `exact_target_zone_verified = false`
- `cloud_ridge_overlap_verified = false`
- `visibility_guaranteed = false`

## 為何不用更高分

直接 northward cloud-grid match 仍可保留完整 Theme 分數與 medium confidence。

B84 fallback 的物理意義只是：

1. 海岸空氣清楚且仍有足夠水氣；
2. 該氣團若被山地抬升，大約在某高度達到凝結；
3. 北方研究過的山地視線中有多個高地 proxy 進入這個高度帶。

它不能知道：

- 雲是否真的已形成；
- 雲帶是否正好貼在清水山／斷崖；
- 山峰露出比例；
- 雲形是否好看；
- 拍攝者實際視線是否被局部雲遮住。

因此只給低信心並 cap 82。

## 2026-09-28 field backtest target

B84 需要讓下列模式不再被判成 54 分的 hard miss：

- clear coast
- visibility ~27 km
- low cloud near beach ~2%
- RH ~72%
- condensation-height proxy ~713 m ASL
- multiple northward mountain proxy elevations intersect that condensation level
- direct coarse-grid mountain low-cloud signal may still be absent

預期結果：

- status: `OPPORTUNITY_OROGRAPHIC_CLOUD_POTENTIAL`
- score <= 82
- confidence: low
- 不宣稱實際雲帶已被 forecast grid 直接看到

## Safety / evidence boundary

Place-specific 題材存在性仍由 B83 的 Grade-A 官方證據建立。

B84 只改「何時較可能成立」的 runtime 推斷，不新增題材，也不把地形／氣象本身當作題材存在證據。
