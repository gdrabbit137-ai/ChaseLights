# CHALLENGER-18 — 詳情彈窗詞彙外洩全面獵捕＋「可拍」語義判定

日期：2026-11-17（台北時間）　偵察者：chaselights challenger #18
實測：https://chaselights.app/ 390×1280 與 1280×1280 兩種視窗，皆重現。
基準：origin/main `cf1619f506357d5c426ac6202553379a750c5006`。

## TL;DR

- **詞彙外洩根因（單一根因、多渲染面）**：client 端 metric 標籤字典不完整——`assets/app.js` 的
  `V2_EVAL_METRICS`（≈L2654）與 `apps/web-v2/app.mjs` 的 `EVAL_METRICS`（≈L367）都缺一大批
  metric 鍵，而所有標籤函式都以 `dict[m] || m` 收尾，缺鍵時**把內部 metric 原始名直接渲染到 UI**。
  CHALLENGER-13 修的是失敗句子層（`V2_FAIL_REASONS` / fail_reason_overrides），**沒有**覆蓋
  「metric 短名」這一層——這就是為什麼外洩復發（第二實例）。
- **奧萬大明明天（11/18）✗light_window 為真 bug**：該日 light_window `day_verdict=PARTIAL`、
  `pass_hours=11`（06:00–16:00 全部 PASS），全日不可能「非日照」；真正擋路的是
  `seasonal_state=UNKNOWN`（楓紅季節窗未開，fail-closed）。日層主導詞選取把 PARTIAL 窗類 metric
  當成失敗詞，是挑戰者 13「窄窗搶詞」病的變體。
- **今天 ✗雨 vs ○ 可拍·今日無下一窗：呈現層單一真相違規，非資料層矛盾**。詳下。

## 1. 外洩實測重現（線上，非推測）

奧萬大楓林步道（tw-141）詳情彈窗，zh-TW：

- `.v2-cond[data-metric=light_window]` 內 `<b>light_window</b>`（1 處，條件列題名 raw 名；
  且其「現況 符合（11:00）／全日未達」兩行同框自相矛盾）。
- `.v2-day-strip .v2-strip-text`：`✗light_window` ×4（明天、後天、11/22、11/23）。
- 同彈窗：「今天」格 `✗雨`，同頁「今天題材判定」＝`奧萬大楓紅 ○ 可拍·今日無下一窗`。
- 390 與 1280 視窗皆重現（同一渲染路徑，與視窗無關）。
- 對照：大屯山助航站等 5 個雲海/夜景/季節點彈窗 strip 均正常顯示「✗霾／✗低雲／✗厚雲」等中短詞——
  因為那些 metric 鍵**有**出現在 `V2_EVAL_METRICS`。外洩與否完全由「鍵在不在字典」決定。

## 2. 外洩路徑清單（grep＋原始碼核對）

共用根因：標籤查表 `dict[m] || m` 的 raw 後備。

| # | 檔案／函式 | 渲染面 | 實測證據 |
|---|---|---|---|
| 1 | `assets/app.js` `v2MetricName()`（L2741）→ 條件列（L2214 `<b>${esc(v2MetricName(c.metric))}</b>`） | 詳情彈窗 條件 ×n 展開區的條件題名 | `<b>light_window</b>` |
| 2 | `assets/app.js` `v2ShortReasonWord()`（L3132）→ 8 日 strip 格 | 彈窗/預報頁 8 日格 `✗短原因` | `✗light_window` ×4 |
| 3 | `assets/app.js` 速覽無 row 後備（L3271）`✗ ${...[m]||m}` | 卡片「現在去會怎樣」✗chip | 同型（未於本日命中，路徑在） |
| 4 | `apps/web-v2/app.mjs` `evalMetricLabel()`（L368）`return d?...:m` | V2 research/evaluations 頁條件列 | 靜態核對（同缺鍵集） |

### 缺鍵盤點（V2_EVAL_METRICS 缺、且會出現在判定列的 metric）

`light_window`(382 機會)、`city_night_window`(54)、`cloud_base_height`(13)、`temperature_2m`(13)、
`fog_state`(12)、`morning_window`(12)、`soft_light_window`(12)、`snow_cover_state`(5)、
`alpenglow_window`(5)、`nearshore_surf_state`(4)、`noctiluca_concentration`(4)、`venue_open_window`(3)、
`clear_streak_hours`(2)、`light_direction`(2)、`daylight_window`(1)、`volcanic_activity`(1)、
`legacy_drift_ice/legacy_mountain_view/legacy_tide`(各1)。
（括號＝目前線上 bundle 中攜帶該 metric 的機會數；`light_window`＋`city_night_window` 兩項即覆蓋 436 個機會。）

資料層無辜：`data/v2/copy/fail_reason_short.json` 的 `words` 對**全部 53 個 metric** 都有三語短詞
（light_window＝「非日照時段」）；subject-cards artifact 的 `dominant_reason` 也是三語短詞。
**外洩 100% 發生在 client 標籤層**，把現成翻譯丟掉、退回 raw 鍵。

## 3. 追加實錘案例：奧萬大「明天整天 ✗light_window」判定

資料（線上 `apps/web-v2/evaluations-details/tw-141.json` ＋ bundle day 層，2026-11-18）：

- 契約 `tw-141-P01`（seasonal_plant 楓紅）條件：`seasonal_state` REQUIRED eq window_open（現在
  `window_closed`→每小時 UNKNOWN）、`precipitation<0.2` PASS、`wind<5` PASS、
  `light_window` REQUIRED（operator none）。
- **light_window 綁定＝全日民用光窗**（太陽仰角 > −6°），不是黃金時段窄窗——逐小時
  06:00–16:00 共 11 小時全 PASS，17:00 起夜間 FAIL。
- 日層：light_window `day_verdict=PARTIAL`、`pass_hours=11`；`seasonal_state=UNKNOWN`；日狀態
  UNFAVORABLE（13 夜間時數 + 11 NOT_EVALUABLE）。

三問三答：

1. **綁什麼窗？** 全日民用光（civil light），非黃金時段窄窗。
2. **pass_hours？** 11（>0）卻顯示整天 FAIL——**主導詞 bug**：`v2DominantFailMetric()` 把
   `PARTIAL` 計入 failSet（L3120 附近 `day_verdict==='FAIL'||day_verdict==='PARTIAL'`），而
   `seasonal_state=UNKNOWN` 被排除於 failSet 之外，於是「季節窗未開」這個真實原因完全不可見，
   畫面呈現一個其實通過 11 小時的窗類 metric 當 ✗ 理由——挑戰者 13 窄窗搶詞病的 PARTIAL 變體。
3. **建議（採 owner 指示）**：
   - 窄窗/窗類 metric 的失敗詞應為「光線不對（非黃金時段）」類，而非「非日照時段」；
     「非日照時段」只允許在 `pass_hours=0` 時使用。
   - `pass_hours>0` 的 PARTIAL 窗類格不得渲染 ✗；應渲染「○ 可拍（非黃金光線）」或直接列出
     窗時刻（06–16），並在真實阻塞是 UNKNOWN（如季節未開）時誠實顯示「季節未開／資料未知」
     為主導詞（`seasonal_state` 需進入候選詞表，不可因 UNKNOWN 被排除後讓窗類 PARTIAL 頂替）。

## 4. 「○ 可拍·今日無下一窗」vs「今天 ✗雨」語義判定

- 資料層：subject-cards 11/17（今天）row＝`tier:shootable`、`dominant_reason:null`、
  `general_baseline.ok:true`（CHALLENGER-14/B 後 general 基準只看 vis/precip/RH 的寬鬆天氣底線，
  今天白天未超標）；同一 subject（楓紅）的 bundle 日判因下午 15–17 時降水 FAIL 而成 ✗雨。
- **判定：非資料 bug，是呈現層混合兩個真相層**——strip 格讀 curated subject 的 bundle 日判（✗雨），
  「今天題材判定」chip 讀 subject-cards row 的 general-baseline tier（○ 可拍）。違反 owner
  single-truth 裁定（同畫面兩層並列讀作矛盾）。
- 「今日無下一窗」本身語義正確：時間感知 tier 以剩餘時段計，今天的 suitable 窗已全數過去（或
  剩餘時段無窗），非「剩餘時段＝明天凌晨」之誤。
- **建議**：(a) ds chip 與 strip 讀同一層（建議都讀 subject-cards row，strip 缺 row 時誠實顯示
  資料不足）；或 (b) shootable tier 的 chip 加注題材自身未符原因（「○ 可拍·楓紅未符（雨）」），
  讓「可拍＝天氣底線過、題材本身未符」的階層語義顯性化。

## 5. 修復建議（給 RD，未動碼）

1. **補字典（P0，最小修）**：`V2_EVAL_METRICS`（assets/app.js）與 `EVAL_METRICS`（apps/web-v2/app.mjs）
   補齊上表 19 鍵三語短名（可直接引用 `fail_reason_short.json` words 的三語短詞，或生成時同步）。
   加一條 guard 測試：bundle 出現的每個 metric 必須存在於兩個字典（防再犯）。
2. **消滅 `||m` raw 後備（P0）**：四個路徑改為「缺鍵 → 誠實中性詞（如 資料不足）＋console.warn」，
   永不渲染內部鍵。
3. **日層主導詞（P1）**：PARTIAL 且 pass_hours>0 的窗類 metric 不得作為 ✗ 主導詞；UNKNOWN 的
   REQUIRED 條件（seasonal_state）應能成為主導詞「季節未開」；「非日照時段」限定 pass_hours=0。
4. **單一真相（P1）**：同彈窗內 strip 與 ds chip 收斂到同一層（見 §4）。

## 6. 驗證方式備忘

- 實測：`chaselights.app` 首頁 → tier=all → 奧萬大楓林步道卡片 → 題材按鈕；390 與 1280 皆以
  DOM text 掃 `light_window|seasonal_state|...` 計數。
- 靜態：對照 bundle 全 metric 集 × 兩個 client 字典鍵集；`fail_reason_short.json` words 全覆蓋核對。
