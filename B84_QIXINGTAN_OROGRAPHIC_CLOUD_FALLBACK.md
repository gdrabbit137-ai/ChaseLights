# B84 — 七星潭貼山雲粗格點漏判修正

## 問題

B83 已新增 `tw-036-P03`「七星潭北望清水山／清水斷崖＋貼山雲帶」，並使用北向多點 spatial weather 判定。

2026-09-28 13:00 實拍驗證卻發現：照片確實有明顯山腰雲帶，海岸／海面能見度很好，但 B83 重算仍得到：

- camera visibility 約 27 km
- camera low cloud 約 2%
- 北向 elevated target 4 點
- directional cloud target 0 點

也就是說，Open-Meteo 粗解析格點沒有直接解析到窄而貼山的地形雲帶。這是 provider/grid-resolution false negative，不應再回頭把單點低雲量硬調高。

## B84 方法

保留 B83 的 direct path 為優先：

1. 海岸 Camera Zone 清楚。
2. 北向高地多點相對海岸出現更強低雲／高濕／能見度下降。
3. 至少一個帶雲高地格點不是白牆。
4. 命中時維持 `directional_mountain_cloud_band_candidate`。

新增一條低信心 fallback：

1. Camera Zone visibility >= 15 km。
2. Camera low cloud <= 20%。
3. Camera RH >= 65%。
4. 無明顯降雨。
5. 由 camera 溫度／露點得到的規劃級 condensation-height/LCL proxy 位於 350–1400 m ASL。
6. 至少兩個北向 elevated DEM proxy 的地形高度進入該 condensation-height 範圍。

成立後只回傳：

`orographic_terrain_intersection_candidate`

而不是宣稱「貼山雲已存在」。

## 分數與 UI

Fallback：

- score cap: **82**
- confidence: **low**
- status: 「北方山地具貼雲潛勢；格點未直接解析雲帶」
- 必須顯示不確定性：沒有直接多點雲帶佐證、實際 ridge/cloud overlap 未驗證。

Direct multi-point path 不受此 cap 影響。

## 為什麼不是過度配合單張照片

這條 fallback 不是用照片本身當作氣象真值，而是修正已查證 Place-specific 題材在粗格點解析不足時的預報路徑。

照片只用來暴露 false negative；Opportunity 的存在仍由官方 Place-specific evidence 支持。

## 安全邊界

- 不把單點 cloud cover 直接當作山區貼雲。
- 不把 LCL proxy 說成實際雲底觀測。
- 不保證清水山／清水斷崖哪一段被雲遮住。
- Camera Zone 白牆、大雨、低能見度仍 veto。
- fallback 永遠低信心且分數封頂。
