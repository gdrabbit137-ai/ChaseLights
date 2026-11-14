# CL-UI-87 — mockup-forecast.html 對照報告（Stage 2b）

Spec: `origin/task/DESIGN-3` head `3d455f121` — `data/v2/audits/design-mockups/mockup-forecast.html`（逐字實作，RD 不自行再設計）。
Token: 已上線 `--cl-*` 層（CL-UI-85；新增 `--cl-white` 供色帶最佳時刻白框，mockup 原值 `#fff`）。
範圍：只動預報渲染路徑（預報彈窗逐小時區）＋新 tokens；列表頁（clui91）與詳情彈窗不動。
對照截圖：`apps/web-v2/tests/logs/cl-ui-87/screenshots/`（prod=本分支工作樹 `C:/tmp/clui87b-wt` 靜態伺服＋Playwright，jp-011 東京鐵塔＝mockup 同一資料樣例；mockup=DESIGN-3 原檔；`-top`=捲回頂端的色帶/分組檢視）。
溢出探針：prod-1280 wrap scrollWidth 926 = clientWidth 926（0px 橫捲）；prod-390 桌面表 hidden（cards 192）；mockup-390 shell 390/390。

## 逐區對照

| mockup 區塊 | mockup | 產品頁落地 | 差異 |
|---|---|---|---|
| 日期分組＋摺疊（n1a） | 8 天各一 `<details class="day-group">`，44px 分組列，預設只展開所選日，其餘只留一行摘要（tier chip＋✓/○ 計數＋題材短名） | 逐字：桌面 `#timeline-groups`＋手機 `#timeline-mobile` 各掛同構 day-group（data-date 鍵）；開合規則＝所選日必開＋使用者手開的分組跨重渲染保留（前一次的預設開啟日回退，`clui87LastSelDate`）；摘要列＝相對日詞（今天/明天/後天）或頁首橫幅格式＋MM/DD＋tier chip（✓推薦/○可拍/✗不宜，subject-cards row.tier；無 row 誠實不出 chip）＋✓/○ 計數＋短名 | 實際分組數由資料決定：實測 9 組（hourly 視窗含過去 28h），mockup 示意為 8 組 |
| 24h 迷你色帶（n3b） | 16px 色帶＋00/06/12/18/23 標籤；最佳小時白框 | 逐字：所選日 24 格，格色讀 subject-cards 逐小時 bucket（fit=綠/ok=琥珀/no=灰/na=暗格）；白框＝CL-UI-81 的 v2WmHours（與綠列同一語義），色值走 `--cl-white` token | 無 |
| 時刻欄錨點（n1b / DR1 P2-9） | 40px 列高、時刻欄 mono 64px、符合小時加粗白 | 逐字：`table.hrs td` 40px；`td.hr` mono 64px；加粗用 `tr:has(td.td-subjects.subj-has / .subj-ok-row)` ——錨點與適合題材 chips 同源，永不互相矛盾 | 加粗語義源為 bucket（題材/一般拍攝小時），mockup 為 tr.rec（同一概念） |
| na 時段收摺（n1c） | na 小時收成一行「⏱ 時段外 05:00 · 18:00–23:00」，不佔列 | 逐字：subject-cards `na` bucket 的小時不發 desktop 列，每組一行 `tr.na-row`＝`state_outside`＋`formatHourSegments` 壓縮時段；手機保留 mockup 的最小 na 卡（時刻＋狀態，無口語行/無詳細氣象） | 文案用既有 trilingual `state_outside`（🕒 非建議時段／Off-window／推奨時間帯外），非 mockup 示意的「時段外」二字——mockup 無 i18n 契約 |
| 桌面表格式 | 時刻｜狀態｜適合題材｜口語化氣象｜⋯ 五欄 | 逐字：每組一張 `table.hrs`；口語化氣象欄＝已上線 `clui82PlainWeather`（clui82 級映射，≥24km 原始字串不上卡片層）；⋯ 開合 kv 列（氣溫/風速/濕度/低雲/中雲/高雲/凝結高度/能見度/天文，aurora 加 Kp），能見度走 `visCellHtml`（≥24 km＋tooltip） | 狀態欄仍為 CL-UI-43 的 V2-owned 判定（初始 資料不足、decorate 填入），與 mockup 單源示意不同——見下「狀態單一判斷」 |
| 詳細氣象展開（n2c） | 桌面 ⋯ 展開列；390 `<details>`；展開狀態不因重渲染丟失 | 逐字：桌面 ⋯ toggle `tr.detail`（hidden 屬性＋顯式 `[hidden]{display:none}` 護欄），open 狀態重渲染前捕捉後還原（`kvRestoreOpen`）；手機 `tm-details` 沿用 CL-UI-82 的 tmRestoreOpen | 無 |
| 390 小時卡（n3a） | 3px 左色帶／時刻 64px mono／主狀態＋口語行／收起 ≈68px | CL-UI-82 已落地（`--hour-card-*` tokens：72px/128px/3px/64px），卡移入各日分組內；口語行沿用已上線映射 | 無 |
| 日 tabs 橫捲／會員入口（n3c/n3d） | mockup 頁首區 | 不在本次範圍：彈窗日期切換沿用既有 modal-day-switch（clui81 兩段式已上線）；masthead 為頁面級（clui28/53 已落地） | mockup 頁首語義由 Stage 2a/既有票覆蓋 |

## 已知語義差異（非版面）

1. **狀態單一判斷（mockup n2a）**：mockup 假設每小時單一狀態源；產品頁保持兩個既有裁定源——狀態欄＝現行所選題材的 V2 evaluations-details 判定（CL-UI-43 fail-closed），適合題材/na bucket＝subject-cards 衍生層（CL-UI-73）。二者可並存（例：所選題材未符、但該小時一般拍攝地板通過→○）。合併為單源需資料層裁定，非 Stage 2b 版面工單範圍。
2. **na 行文案**：`🕒 非建議時段`（既有 trilingual 釘死）取代 mockup 示意字「時段外」。
3. **分組數 9≠8**：資料視窗（過去 28h＋未來 163h）跨 9 個本地日；版面按資料逐日成組，無寫死 8。

## 測試

- 全套 `node --test --test-isolation=none`（node-26.7.0）：763 tests → 762 pass / 1 fail / 0 skip；另 1 skip 為既有 browser-gated case。
- 唯一紅：`CL-UI-47 (2) desktop 1280px`（raw-CDP 真實點擊）——單獨重跑 5/5 綠；依 CL-UI-74 歸因協議為本機 CDP 累積負載問題（CL-UI-86 同簽名、base 886d76c64 同紅），非本分支 diff 造成；live-browser 驗證留 reviewer close step。
- 重錨範圍（僅 stamp/結構 pin）：clui92 stamp（36 檔）；cl-ui-78(3)(4)(6b)、cl-ui-73(1)、cl-ui-79(1)、cl-ui-14(U3 順序 pin)、cl-ui-82(8 stamp)、cl-ui-53(max)；新增 `cl-ui-87-forecast-day-groups.test.mjs`（8 案）。
- `python test_opportunity_adapter.py`：PASS（app.js 釘段無 drift）。

## 截圖清單

- `clui87-prod-1280.png` / `clui87-prod-1280-top.png` — 產品頁桌面（-top＝色帶＋分組摘要＋kv 展開）
- `clui87-prod-390.png` / `clui87-prod-390-top.png` — 產品頁 390（分組＋小時卡）
- `clui87-mockup-1280.png` / `clui87-mockup-390.png` — DESIGN-3 mockup 原檔
- `*.json` — 各視角結構探針（band 24 格、分組數、開啟分組、na 行數、列/卡數、溢出）
