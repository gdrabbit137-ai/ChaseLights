# ChaseLights Score V5 — 2026-09-20

## 本版重點

### 1. 載入速度與快取架構
- 首頁改成只讀 `<region>_weather.json` 的精簡 summary，不再一開始下載所有景點 96H 明細。
- 96H 明細拆到 `<region>_weather_details.json`，只有點開景點時才載入。
- 移除 `?t=${Date.now()}` 與 `cache: no-store`。
- 使用 Cache Storage 做 stale-while-revalidate：有快取先立即顯示，再背景更新。
- 同一瀏覽階段另有記憶體快取。
- JSON 改成 compact 輸出，降低傳輸大小。

### 2. 語言切換不再重新抓氣象
- 每個地區只產生一份語言中立的 summary + details。
- 景點名稱保留 `name_i18n`，狀態與因子以 key 傳輸，前端即時翻譯。
- 中文 / English / 日本語切換只重新渲染，不發 weather fetch。

### 3. 修正地區狀態與競態
- 保留 AbortController + sequence guard，防止舊地區資料覆蓋新地區。
- 重新整理會恢復最後選擇的國家、語言、日期、場景、出景題材與各國子區域。
- 切國家時不會先閃現上一個國家的景點。

### 4. 場景 Scene 與出景 Theme 分層
- Scene：山岳、海岸、湖泊、河川溪流、瀑布、森林、濕地、地質奇景、沙漠荒原、草原、田園、冰雪冰川、城市、建築地標。
- Theme：日出、日落、藍調時刻、晨昏彩霞、雲海、晨霧薄霧、鏡面倒影、森林光束、山景通透、銀河星空、長曝水景、冰雪景觀、城市夜景、極光。
- 舊 `tags` 仍保留供相容，但 V5 評分與篩選使用 `scenes` / `themes`。

### 5. 地區動態題材
- 台灣：不顯示極光。
- 日本：不顯示極光。
- 美國：只有選到「阿拉斯加」子區域才顯示極光；美西 / 美中 / 美東 / 全部不顯示。
- 場景與題材按鈕只顯示目前子區域確實有的類型。

### 6. Score V5
- 延續 V4 eligibility gate：先確認題材在該時段是否成立，再評天氣。
- 新增日出、日落、彩霞、藍調、霧景、倒影、光束、長曝與冰雪題材評分。
- 夜間山景、白天城市夜景、缺 Kp 極光、缺天文資料銀河持續設硬上限。
- 卡片顯示 Winning Theme、最佳連續窗口、主要加分 / 扣分因素。

### 7. 既有修正全部保留
- Open-Meteo 風速明確使用 m/s。
- UTC 作為跨國比較基準，顯示時使用景點當地時區。
- NOAA Kp 使用時序資料，不把目前 Kp 複製到全部 96 小時。
- 高山可傳 elevation。
- 天文計算失敗顯示 N/A，不以 0° / 0% 冒充有效資料。
- 固定 `spot_id`，收藏不再因切語言失效。
- 台灣 / 日本 / 美國使用各自雷達來源。

## JSON Schema
`schema_version = 5`

輸出：
- `tw_weather.json`, `tw_weather_details.json`
- `jp_weather.json`, `jp_weather_details.json`
- `us_weather.json`, `us_weather_details.json`

## V5.1 UI hotfix
- 修正場景按鈕點擊後 `active` 藍色 highlight 不更新。
- 修正出景按鈕點擊後 `active` 藍色 highlight 不更新。
- 篩選行為本身不變；現在按鈕視覺狀態會與 `currentScene` / `currentTheme` 同步。

## V5.2 — filter highlight + location audit

- Fixed Scene/Theme highlight state with `aria-pressed`, explicit DOM synchronization and a render fallback.
- Bumped weather cache/schema to 7 so old cached summaries cannot keep stale filter/location data.
- Fixed 不厭亭 to an actual viewpoint/camera coordinate and removed incorrect Coast / Long Exposure classification.
- Removed automatic Long Exposure inheritance from every Coast scene.
- Added/retained explicit POI/viewpoint coordinate overrides across Taiwan, Japan and major US photo locations.
- Navigation now prefers each spot's named `map_query` before raw latitude/longitude.
- Added `LOCATION_AUDIT.md` with confidence coverage and remaining broad-area limitations.

## V5.2.1 — region highlight sync hotfix

- Fixed region/sub-region button highlight becoming stale after clicking another category.
- Region buttons now persist `data-key` / `aria-pressed` state and immediately re-render the sub-navigation after selection.
- Fixes cases such as the Kinmen button remaining blue while Main Island spots are actually being shown.
- No weather JSON regeneration is required for this UI-only hotfix.


## V5.3 — Sky Glow / Temperature / Local-name consistency
- Added a conservative `FIRE_CLOUD_LIKELY` state under the Sky Glow theme. It requires twilight sun altitude, limited low cloud, favorable mid/high cloud, low rain risk, and reasonable wind. This is presented as a probability signal, not a guarantee.
- Renamed the general sky-glow state to clearer wording and added a dedicated fire-cloud indicator/factor in zh-TW/en/ja.
- Added a persistent °C / °F selector in the header. The selected unit updates both cards and the 96H detail modal and is stored in localStorage.
- Added best-window temperature to summary cards.
- Fixed Erliao Sunrise Pavilion (`二寮觀日亭`) local-name metadata so it no longer renders a stray second-line `二寮`.
- In Taiwan + Traditional Chinese mode, redundant Chinese local-name subtitles are suppressed; other language/region combinations can still show useful native names.
- JSON schema bumped to 8 and browser weather cache moved to v8.
