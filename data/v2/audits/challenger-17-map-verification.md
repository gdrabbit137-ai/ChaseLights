# CHALLENGER-17 — 手機天氣圖修復後驗收巡檢（bclwg43 波後獨立複查）

日期：2026-11-17（台北時間）。方法：線上 https://chaselights.app/weather-map，CDP 手機模擬 390×844 DPR3（touch emulation 5 點）、Network.setCacheDisabled+clearBrowserCache 冷載。Mockup 對照基準：task/DESIGN-3 head fdae38022（data/v2/audits/design-mockups/mockup-weathermap.html）。
上線位元組核對：線上 served `weather-map.css?v=bclwg42`／`weather-map.js?v=bclwg42`（weather-map-regions bclwg30／palette bclwg25／deeplink bclwg19），與 origin/main（6ad71ff3d「Auto-update Himawari-9 WeatherGrid」）釘值一致——前波（bclwg39–42）修復已部署。
URL 行為：開 `/weather-map` 自動帶 `?region=tw`。

環境註記（測試方法學，非網站缺陷）：**tab 處於 document.hidden 時 MapLibre 的 `load` 事件永不觸發**（rAF 不跑），8 秒逾時後必然落入「底圖逾時 · Canvas fallback」；`Page.bringToFront` 後 ~6 秒內 ready。隱藏分頁跑 headless 驗收會把 ready 判成逾時——重跑本報告任何斷言前必須 bringToFront。

---

## 一、修復驗證矩陣（11 項：10 PASS、1 N/A-已由 owner 裁決取代）

| # | 項目 | 結果 | 實證 |
|---|------|------|------|
| 1 | 時間軸收摺細帶 32px | ✅ PASS | `#wm-tl-bar` 181×32px（容器 `#wm-timeline-dock` 42px 含 padding）；點開展開為 146px 日/時格（11/16、11/17 今天、11/18 明天＋02:00–20:00 時格＋綠色可繪帶），點帶/開 sheet 均正確收合 |
| 2 | 列表 bottom sheet | ➖ N/A | 入口已依 owner 裁決（bclwg41「景點列表入口移除」）下線：`#side-toggle` display:none，`#wm-sheet` markup 仍在但無入口。mockup fdae38022 的 66.7% 全寬列表 sheet 規格已被此裁決取代，無從驗證 |
| 3 | 圖層 sheet 互斥 | ✅ PASS | 實測序列：開圖層 sheet→點細帶＝sheet 關、細帶展開；細帶展開→開圖層 sheet＝細帶收合、sheet 開（`wm-timeline-dock` 146px→41px）。sheet 內 ✕（`data-wm-act=layer-sheet-close`）正常關閉。列表 sheet 已無入口，兩 sheet 互斥僅餘程式路徑（`wmOpenSheet`/`wmOpenLayerSheet` 互收） |
| 4 | 頁面不捲動 | ✅ PASS | `html/body overflow:hidden`；scrollY 恆 0；scrollWidth×scrollHeight=390×844；地圖拖曳/縮放全程 scrollY 不變 |
| 5 | 地圖手勢平移 | ✅ PASS | 合成 touch 拖曳地圖：camera 125E/26.0N→111.4E/38.6N（scrollY 維持 0，觸控未漏給頁面）；縮放鈕 44×44 各向 zoom 2.50→3.50；雙指 pinch zoom 2.39→3.39 |
| 6 | 初始相機台灣 | ✅ PASS | 冷載 `__weatherGridCamera` = center 125E/23.657N、zoom 2.389（tw bbox 105–145E/5–40N fitBounds+padding28，畫面可見 5°N–38°N 標籤）；切區日本（fit 134E/35.75N/zoom 3.13）再切回＝相機精準回到同一 TW fit；`↺ 模型範圍` 回位正常 |
| 7 | 無行政虛線（五圖層） | ✅ PASS | style layers `boundary_2`/`boundary_3`/`boundary_disputed` 全部 `visibility:none`（111 層掃描）；切區 JP→TW 來回後仍 none（無樣式重置回歸）；全雲量/低雲/中雲/高雲/降雨率五圖層截圖均無行政界線。地圖上唯一虛線為資料 bbox 外框矩形（模型範圍指示，非行政界） |
| 8 | 無標題塊與資料來源行 | ✅ PASS | `.header-title-line` h=0、「WeatherGrid Preview」不可見；`footer` 0×0；模型/起報資訊收進 `#data-info-open` ⓘ → `#data-info-dialog`（709px，開/關正常）。畫面僅剩地圖＋操作區＋底部 site-nav |
| 9 | 歸屬小字 | ✅ PASS | MapLibre compact attribution 縮為地圖下緣單行 8.32px 小字（y=665，地圖框內），「OpenFreeMap © OpenMapTiles Data from OpenStreetMap」連結可用 |
| 10 | 降雨率可點 | ✅ PASS | 兩路徑皆通：圖層 sheet「🌧️ 降雨率」chip 點擊→切層→場重繪（canvas 不透明像素 218k–411k）；水平捲動控制列 `#layer-select` 同樣可切。chip 標籤同步（降雨率/全雲量/能見度皆更新） |
| 11 | 無外洩徽章 | ✅ PASS | body innerText 掃描無 Camera-Subject-Environment/partial-migration/CL-UI/CL-DATA/bclwg 等 leak 字串。圖層 sheet 的「● Camera — Subject — Environment」為可拍% tier 圖例色標（F14 規格），非外洩 |

補充實測（畫面渲染健康度）：MapLibre ready 後資料場確實繪在 overlay canvas（低雲 70k–220k、全雲量 274k、能見度 294k 不透明像素，maxAlpha 184–251）；**等值線縮放閘門在 MapLibre 路徑正常**——region fit（zoom 2.50、cellPx 1.12px）時 `__weatherGridContourGate.allowed=false`，無碎點密布（Canvas fallback 期間閘門依設計放行 always-draw，屬已知 fallback 行為）。景點釘點（219 圓標）與左下圖例（0%–100% 首尾標籤）正常。

---

## 二、新問題分級清單（4×P2、2×P3、1×未定案）

- **P2-1｜圖層 sheet 開啟時，「地圖已收成預覽 · 點此返回」pill 點擊無效**（新缺陷，CL-UI-103 同構遺漏）。`#wm-map-dim` 的 hint 綁死 `data-wm-act="sheet-close"`（列表 sheet 專用）；共用 click handler 命中 `sheet-close` 後呼叫 `wmCloseSheet()`，因 `wmSheetOpen=false` 早退 return——圖層 sheet 的關閉路徑永遠走不到。mockup fdae38022 規格「預覽條 pill 點擊即關 sheet 回復地圖全幅」在圖層 sheet 上破功；✕ 鈕正常。修法建議：handler 判「目前開啟的那個 sheet」時，`sheet-close` 分支應收掉任一開啟中的 sheet（互斥下僅一個開啟），或 hint 動態切換 `data-wm-act`。重現：390×844 開圖層 sheet→點置中 pill→無反應（截圖 s6 佐證序列）。
- **P2-2｜橫向（844×390）落入桌面版配置，APP 式版面整個失效**。寬度斷點 768px 使橫向手機吃 ≥769 桌面塊：標題塊「🗺️ WeatherGrid Preview」重現（y103）、頁面可捲動（scrollHeight 1894 vs 390）、時間軸 dock 落在 y1153（螢幕外，需捲動才可達）、site-nav 跳到頂部（y18）。字面上符合「桌面 ≥769 零改動」規範，但橫向手機體驗與「手機＝APP 式固定版面」精神衝突——規範盲區，建議 owner 裁決是否補 `max-height` 條件（如 `@media (max-width:768px), (max-height:500px)`）。
- **P2-3｜底圖逾時門檻 8s＋unpkg CDN 依賴，慢網環境整頁退化**。MapLibre 自 unpkg 動態 import（800KB 級）＋tiles.openfreemap.org，逾時 8s 後 tear down 成 Canvas fallback：無平移/無縮放手勢（fallback 無 camera）、資料層不繪（僅誠實 QC 警示）。本輪冷載多次觸發（網路快的主機也僅勉強趕上）。建議：maplibre 自家托管（免第三方 CDN 單點）、門檻提高或改為「逾時不 tear down，ready 後無縫接管」。另：fallback QC 徽章「底圖逾時，資料層未顯示」誠實標示正確。
- **P2-4｜切圖層瞬間「目前圖層」inspector 自動浮出數秒後收合（layout flash），且 QC 徽章與畫布矛盾**。切到降雨率等圖層時 `#layer-panel`（目前圖層/詳細/畫面資料範圍/`#qc-summary`）短暫插入操作區下方（T+0.6s 量得 h2 y660、警示 y753），~6s 後自行收合；期間 `#qc-summary` 顯示「資料品質 · 資料層未顯示」，但同刻 canvas 已繪出該層場（降雨率 218k 不透明像素）——徽章在 field draw 完成後未重刷，違反 CL-WG-18「QC 徽章不得與可見 canvas 矛盾」精神。建議：inspector 不隨切層自動展開（維持 bclwg39「預設收合」），或 QC 重刷掛到 render 完成事件。
- **P3-5｜觸控目標多處 <44px**：播放鈕 `#time-play` 38×38、圖層 sheet pill `#layer-sheet-btn` 73×36、`↺ 模型範圍` 71×27、圖例 `legend-toggle` 118×25、ⓘ 資料 58×31、`#time-slider` 本體僅 16px 高（點選精度差；所屬列 44px 緩解但不完整）。CL-UI-102 F4 只升級了 chips/zoom/詳細/mini ✕，這批漏網。
- **P3-6｜sheet 互動後 `.wm-ops` 殘留 `wm-dock-open`**：開過圖層 sheet 再關閉後，ops 類名不復位（殘留至下次重載），操作區維持 132px（乾淨態 90px）——多佔 42px 地圖空間，視覺無明顯破版故僅 P3。
- **未定案-7｜圖層 sheet grab 下拉 >80px 收起**：程式路徑存在（weather-map.js 6199–6219，同款 >80px 閾值），但合成觸控在模擬環境反覆卡死 CDP daemon，無法取得實測結論，需真機複測。

---

## 三、與 mockup（task/DESIGN-3 fdae38022）對照偏差

| mockup 規格 | 線上實況 | 判定 |
|---|---|---|
| 時間軸 32px 細帶（目前所選＋展開箭頭，點開向上浮出、選定即收） | 32px 細帶＋146px 展開格，行為一致 | ✅ 一致 |
| sheet 開＝地圖壓暗 rgba(4,6,12,.55) 縮成上緣預覽條（≥120px）＋置中「地圖已收成預覽 · 點此返回」pill | dim rgba(4,6,12,.55)、預覽條 346px、pill 文案逐字一致 | ✅ 一致（比例不同：圖層 sheet 高 33%，mockup 66.7% 為列表 sheet 規格；圖層 sheet 為 CL-UI-103 後續規格） |
| pill 點擊即關 sheet | **圖層 sheet 開啟時點擊無效** | ❌ 偏差（新問題 P2-1） |
| 細帶排 sheet 下方流內、各佔各列零互疊 | 實測 sheet 底 684＝細帶頂 684，零互疊 | ✅ 一致 |
| 列表全寬 bottom sheet 66.7%＋搜尋＋依可拍% 排序＋grab 下拉收起 | 入口已移除（owner bclwg41 裁決取代規格） | ➖ 規格被取代 |
| grab 下拉 >80px / ✕ / Esc | ✕ 正常；grab 未定案（見 未定案-7）；Esc 未測（行動鍵盤場景） | ⚠️ 部分未驗 |
| 1280 桌面零改動 | 未在本輪範圍（本輪僅 390×844＋844×390） | ➖ 未驗 |

---

## 結論

前波 bclwg39–42 修復全數上線生效（served bclwg42），11 項驗收 10 過、1 項已被 owner 裁決取代；未發現修復引入的破版級回歸。新發現 1 個明確功能缺陷（P2-1 預覽條返回 pill 對圖層 sheet 無效）、2 個規範盲區/健壯性問題（P2-2 橫向、P2-3 底圖 8s 逾時門檻）、1 個 QC 一致性問題（P2-4）、2 個觸控/狀態細節（P3）。建議 owner 先收 P2-1（一行 handler 修正）與 P2-3（CDN 托管策略）。

證檔：截圖留存於本機 D:/tmp/ch17b-shots/（冷載、sheet 開、細帶展開、五圖層、橫向、乾淨冷載共 12 張），未入 repo。
