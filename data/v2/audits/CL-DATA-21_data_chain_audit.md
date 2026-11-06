# CL-DATA-21 資料鏈稽查 — 首頁卡片 ↔ V2 evaluations 同源（藍圖 §1.3）

稽查對象：V1 shell 首頁（repo-root `assets/app.js` + `${region}_weather.json` + V2 bundle）。
稽查日：2026-11-06。基準 commit：`52ed33394`（origin/main 最新）。

## 1. 結論先行

1. **首頁卡片的「判定欄位」在本票基準上已由 V2 evaluations 驅動**（CL-UI-05 已落地）：
   卡片最佳題材/符合時數/最佳拍攝時段/下一個符合時段/主分組/排序全部讀
   `apps/web-v2/evaluations-latest.json`（與 modal 同一 bundle、同一函式族
   `v2BestForSpot` / `v2EffectiveHours` / `v2NextWindowLocal` / `v2SpotDayVerdict` /
   `v2HoursSortValue`）。
2. **審查證據（野柳 11/06 卡片顯示 22:00–23:00「符合」）的根因不是 legacy 卡片管線，
   而是線上 bundle 落後於 CL-DATA-19 契約修正**：
   - `tw-074-P02`（野柳蕈狀岩與燭台石群紋理）原契約只有 `golden_hour_window`（BONUS/QUALITY），
     沒有光線窗 → REQUIRED 條件（地形+降水）通過時夜間 22:00–23:00 仍標記
     `GUIDANCE_SATISFIED`（見 evaluations-details/tw-074.json 11-06 各小時的
     `golden_hour_window: FAIL` 但小時整體 SATISFIED）。
   - CL-DATA-19（commit `e261cc981`, 19:08+0800）已為其補上 `light_window`
     REQUIRED/MAIN（civil，sun > −6°），**晚於** evaluations-latest.json 的
     generated_at（10:44 UTC = 18:44+0800）→ bundle 尚未吃進修正。
   - 本票以全量 `evaluate_batch.py --forecast-hours 168` 重生成 bundle+details，
     野柳卡在 11/06 不再出現 22:00–23:00「符合」（驗證見本檔 §4）。
3. **legacy 仍在使用的部分（分離處理，不動資料層）**見 §2 對照表。

## 2. 資料鏈對照表（欄位 → 舊源 → 新源）

| 卡片欄位 | 稽查前實際資料源 | 稽查後 | 處置 |
|---|---|---|---|
| 本日最佳題材（主題列） | V2 bundle（v2BestForSpot，名稱經契約 `name_i18n`） | 同 | 已同源 |
| 符合時數 | V2（v2EffectiveHours，today 只算剩餘小時） | 同 | 已同源 |
| 最佳拍攝時段 | V2（formatHourSegments(v2Best.hoursList)） | 同 | 已同源 |
| 下一個符合時段 | V2（v2NextWindowLocal，已重錨本地時鐘；live.next_good 只作未來值候選） | 同 | 已同源 |
| 主分組（viable/deferred/無評估） | V2（v2SpotDayVerdict） | 同 | 已同源 |
| 卡片排序 | V2（v2HoursSortValue；sort_rows 的 hours 模式） | 同 | 已同源 |
| 遠日 tab（day3–day6） | V2（v2DayForOffset 以 local_date 解日；tabs 為固定 7 天常數） | 同 | 已同源；V2 bundle 8 天 ≥ 7 tabs |
| **卡片是否存在於列表** | **legacy**：`getMetric()` 要求 legacy `${region}_weather.json` daily 有該日 `day.all` | legacy（標註保留） | legacy 檔由同一排程天氣 workflow 每 6h 更新且涵蓋 7 天；缺點＝V2 有評估但 legacy 缺日時卡片整卡消失（誠實降級，非錯誤判定）。不做重構（風險>效益），在 app.js 註記 |
| 溫度/雲底/加分減分 pills/indicator | legacy `day.all`（metric.temp/cloud_base_agl/factors/indicator_key） | legacy（標註保留） | 純資訊性欄位，不承載判定語義；V2 bundle 不含這些即時天氣數值 |
| 天文數值列（太陽方位/月照/Bortle） | legacy astronomy 欄 | legacy（標註保留） | 同上；夜間判定語義一律由 V2 時間窗控制 |
| 天氣 modal 小時表「最佳」列 | **legacy**：`summaryMetric.window_start/window_end` 標 tag-best | **改 V2** | CL-DATA-21 修正：tag-best 只在 V2 對該 opportunity 該日 GUIDANCE_SATISFIED 的 good_hours 內標記（與卡片同源；V2 缺評估時 fail-closed 不標） |
| 地點 modal 欄位排序（v2Hours） | V2 但用 **index** 錨日 `(days)[offset]`（bundle 過日界後錯位） | **改 V2** | CL-DATA-21 修正：一律 `v2DayForOffset()` 以 local_date 解日（含機會卡 current 列） |

## 3. legacy tw_weather.json 保留範圍（標註）

- 保留：spot 目錄（name/scenes/admin_areas/座標/時區/navigation/access）、
  `daily[].all` 的資訊性欄位（temp/cloud_base/factors/indicator/astronomy 數值）、
  `hourly_forecast`（modal 小時表的數值列）。
- 不再承載：任何「判定/符合/時段」語義 — 這些全數出自 V2 evaluations。
- `access_mode`/`access_note_i18n`、`navigation_target` 屬 legacy 目錄獨有資訊
  （V2 無），依票令分離保留。

## 4. 驗證

- `evaluate_batch.py --forecast-hours 168` 重生成後：`tw-074-P02` 11-06 →
  `UNFAVORABLE`、good_hours `[]`（光線窗 REQUIRED 生效），卡片與 modal 同源。
- `node --test`（web-v2 全套）＋ 新增 `cl-data-21-card-modal-source.test.mjs`
  （modal「最佳」列 V2 同源釘值 + 野柳/得月樓/和平島夜間不符釘值）。
- `python test_opportunity_adapter.py`、python legacy 管線測試基準一致。
