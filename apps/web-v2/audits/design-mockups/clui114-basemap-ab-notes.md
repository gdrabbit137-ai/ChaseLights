# CL-UI-114 — 深色底圖地形改善 A/B 截圖與雲層可讀性評註

Date: 2026-11-17 · branch task/CL-UI-104（worktree D:/tmp/clui104b-wt）· feature-flag 預設關閉，本票不改預設，等 owner 裁示。

## 截圖清單（design-mockups/ 與 D:/tmp/clui114-shots/ 各一份）

三案 ×（台灣全幅、山區放大 zoom 10 合歡山一帶）×（390 / 1280）＝12 張，另有 2 張並列對照：

| 案 | 台灣全幅 1280 | 台灣全幅 390 | 山區 z10 1280 | 山區 z10 390 |
|---|---|---|---|---|
| 現行（亮色 liberty，對照組） | clui114-current-tw-full-1280.png | clui114-current-tw-full-390.png | clui114-current-mountain-z10-1280.png | clui114-current-mountain-z10-390.png |
| 方案 A（fiord 深色＋Terrarium hillshade） | clui114-a-dark-hillshade-tw-full-1280.png | clui114-a-dark-hillshade-tw-full-390.png | clui114-a-dark-hillshade-mountain-z10-1280.png | clui114-a-dark-hillshade-mountain-z10-390.png |
| 方案 B（現行亮色＋CSS 暗化 brightness .55 / saturate .75） | clui114-b-dim-filter-tw-full-1280.png | clui114-b-dim-filter-tw-full-390.png | clui114-b-dim-filter-mountain-z10-1280.png | clui114-b-dim-filter-mountain-z10-390.png |

並列對照：`clui114-compare-tw-full-390.png`（三案 390 全幅並排）、`clui114-compare-mountain-z10-1280.png`（三案 z10 山區並排）。

啟用方式（驗證用 URL flag，預設不開）：`weather-map.html?wgBasemapDark=1`（案 A）、`?wgBasemapDim=1`（案 B）。

## 雲層可讀性評註（低雲／雨色帶對比，實測像素亮度）

| 區域／案 | 雲帶亮度 | 底圖亮度 | 對比 Δ | 判讀 |
|---|---|---|---|---|
| 台灣全幅 390 — 現行 | 185.3 | 219.1（海） | 33.8 | 雲帶偏灰、在亮色海面上「變暗」反而被讀成陰影；低雲邊界模糊 |
| 台灣全幅 390 — A | 102.5 | 112.1（海） | 9.6* | *海面雨帶（淺藍）與深色海面 Δ 小，但**色相分離**明顯：灰白雲 vs 深藍海，人眼判讀以色相為主 → 實際可讀性優於 Δ 數字 |
| 台灣全幅 390 — B | 126.7 | 143.5（海） | 16.8 | 濾鏡連同雲層 canvas 一起暗化（canvas 在地圖容器內），雲也丟失亮度優勢；整體像「夜間版現行」，雲帶辨識度未提升 |
| 山區 z10 1280 — 現行 | 224.2 | 210.5 | 13.7 | 白灰雲霧疊亮綠地形，對比最弱；無地形起伏參考 |
| 山區 z10 1280 — A | 149.6 | 126.1 | 23.5 | 最佳：山脊受光面／背光面清晰，雲帶灰白與深藍地形色相分離，邊界最好認 |
| 山區 z10 1280 — B | 172.4 | 151.9 | 20.5 | 對比數字改善但雲同時被暗化，且地形仍是平面無起伏；偏「照片調暗」感 |

### 結論（供裁示，非決議）

1. **方案 A（dark＋hillshade）對「地形可辨」目標是唯一直接解**：山脊在深色底上經 hillshade（illumination 315°、exaggeration 0.55、半透明白 highlight）清楚可辨；現行與 B 都沒有任何地形起伏資訊。
2. **雲層可讀性**：A 下低雲/雨帶靠色相分離（灰白 vs 深藍）讀得最清楚；B 因濾鏡同時暗化雲層 canvas，優勢打折；現行亮色下雲帶與地形同為高亮度，對比最弱。
3. A 的代價：fiord 樣式地名標籤配色與現行不同（可讀，但視覺語言變了）、hillshade 需下載 AWS Terrarium DEM 圖磚（多一組外部依賴，maxzoom 13 封頂）；B 的代價：雲層一起變暗、無地形資訊、飽和度損失後道路/行政圖形辨識度下降。
4. 縮圖（390）下 A 的 hillshade 仍然可辨，標籤白字可讀。

## 實作位置

- `assets/weather-map.js`：CL-UI-114 區塊（flag 解析、fiord 樣式選擇、Terrarium raster-dem＋hillshade 圖層、容器 CSS 濾鏡），load/styledata 均冪等套用；flag 關閉時 no-op。
- 測試：`apps/web-v2/tests/cl-ui-114-basemap-ab-flag.test.mjs`（預設不變／A 參數／B 濾鏡／套用時機／stamp bclwg47）。
- 截圖 harness：`apps/web-v2/tests/cl-ui-114-screenshots.mjs`、線上驗證 probe：`apps/web-v2/tests/cl-ui-114-probe.mjs`。
