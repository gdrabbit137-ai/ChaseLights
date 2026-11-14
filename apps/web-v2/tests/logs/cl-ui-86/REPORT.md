# CL-UI-86 — mockup-cards.html 對照報告（Stage 2a）

Spec: `origin/task/DESIGN-3` head `3d455f121` — `data/v2/audits/design-mockups/mockup-cards.html`（逐字實作）。
對照截圖：`apps/web-v2/tests/logs/cl-ui-86/screenshots/`（prod=本分支工作樹 `C:/tmp/clui86b-wt` 靜態伺服＋Playwright 真實視窗模擬；mockup=DESIGN-3 原檔）。
水平溢出探針：prod-1280 = 0px、prod-390 = 0px（mockup-390 130px 為 mockup 自身的示範容器寬度切換鈕未啟用所致，非產品頁）。

## 逐區對照

| 區塊 | mockup | 產品頁落地 | 差異 |
|---|---|---|---|
| 日期 pill 兩段式 | `.date-pill` 176/48，l1「📅 今天 · 11/16」、l2「台灣 · 日本 · 美國」 | `.day-picker-trigger` 兩段（CL-UI-81 已落地），border/radius/hover 改依 mockup（`--cl-border`/`--cl-r-sm`/hover border-strong，hover 藍色退役） | l2 內容為現行區域摘要（誠實計數），非 mockup 的三地區清單——產品頁按地區過濾 |
| tier 分段控制雙編碼 | 選中＝600 字重＋1.5px 語義色框＋bg-3；綠=推薦/黃=可拍/紅=不宜/中性=全部；計數 mono 第二灰層 | 完全一致：`.tier-tab.active`＋`[data-tier=…]` 三語義色、`.tier-tab-count` mono text-3（選中隨語義色）；🌐 記號加在全部 tab（live＋cache 兩條渲染路徑） | 無（CL-UI-81 的全綠選中態依 mockup 改為 per-tier） |
| 題材 chips | 24px `--chip-h`、r-xs、bg-1、單行橫捲＋scroll-snap＋右緣 24px fade mask、選中中性 bg-3 | 完全一致（`.subject-chip`/`.subject-chip-strip`），藍色選中態依 mockup 退役 | 無 |
| 卡片頭 | 名稱 14/600 ellipsis＋tier 徽章＋★（fav=amber） | 名稱 14/600 ellipsis＋`.tier tier-rec/shoot/no/defer` 徽章（共享 tier adapter 狀態；NOT_EVALUABLE=灰「資料不足」）＋裸 ★ | 無 |
| 地區/屬性灰字 | `.region` 灰字 | `.category-tag`（行政區，去框改純灰字）＋`.env-type-text`（屬性，CL-UI-77 保留）＋雙語 `.spot-local-name` | 產品頁多保留雙語次行（既有功能，不砍） |
| 逐題材行 | `.subj-row`：綠點＋短名 600＋mono 時段＋🔔 行尾 | `.cl-subject-row`＋`::before` 綠點（CSS 注入，CL-UI-69 pin 的渲染表達式不動）、時段改 mono text-2（藍僅連結）、外框 retirement | 生產頁保留「短名： 」冒號分隔（CL-UI-69 釘死之解剖），mockup 無冒號 |
| pills | `.pill` 22px bg-2 r-xs fs-12 | `.metric-chip` 重塑為同規格 | 生產頁 pills 為真實欄位（海拔/太陽角度/雲底/溫度/距離），mockup 為示意值 |
| 三鈕 | `.acts` border-top 實線＋30px 三等寬鈕 | `.card-footer-tools` margin-top:auto＋實線＋`.tool-link` 30px flex:1、hover bg-3/border-strong/text-1 | 觸寬（≤640）維持 CL-UI-17R 44px 圖示鈕（無障礙既有裁決，mockup 為桌面示意） |
| 460 卡效能 | `content-visibility:auto;contain-intrinsic-size:auto 190px`＋離屏跳過排版 | 逐字照抄至 `.card` | mockup 的「首屏 15 張＋IntersectionObserver 虛擬載入」未抄——生產頁為全量渲染＋content-visibility（15 張上限是 mockup demo 的固定示意，抄入會破壞既有清單行為斷言與 CL-UI-84 測試契約） |
| grid | 1280 shell、3 欄、24px gap；≤768 單欄 8px | `.container`/`.deferred-grid` 同步；700/1100/1500/1700 欄階梯退役；B103 單欄 override 退役 | 無 |
| 標題列 | P3-1：16/600 與右側 13px 灰字同 baseline | `.discovery-title` 16/600＋`.rank-summary` 13px text-3，flex baseline | 無 |

## 測試
- 全套 `node --test --test-isolation=none`（node-26.7.0）：762 tests → 761 pass / 1 fail / 1 skip。
- 唯一紅：`CL-UI-47 (2) desktop 1280px`（raw-CDP 真實點擊）。歸因：於 base `886d76c64` detached worktree 單獨重跑同樣紅（行動版 390 兩邊皆綠）——依 CL-UI-74 歸因協議，本機 CDP 點擊環境問題，非本分支 diff 造成；live-browser 驗證留 reviewer close step。
- 重錨範圍（僅 stamp/結構 pin）：clui91 stamp（37 檔）、cl-ui-81(1)(3)、cl-ui-66(16)、cl-ui-78(6)、cl-ui-46(2)、cl-ui-53(max=91)；新增 `cl-ui-86-list-layout.test.mjs`（9 案）。
- `python test_opportunity_adapter.py`：PASS。

## 截圖清單
- `clui86-prod-1280.png` / `clui86-prod-390.png` — 產品頁（本分支）
- `clui86-mockup-1280.png` / `clui86-mockup-390.png` — DESIGN-3 mockup 原檔
