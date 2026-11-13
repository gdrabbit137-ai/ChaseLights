# CHALLENGER-14 — 預報表「適合題材」欄語義審查（owner 實測截圖：鰲峰山 tw-197，11/14–15）

- 分支：`task/CHALLENGER-14`（base = origin/main `34c7bf631`）
- 性質：read-only 調查＋報告；不含任何產品碼修改
- 前置閱讀：CHALLENGER-13（`task/CHALLENGER-13` `data/v2/audits/challenger-13-time-window.md`）、CL-UI-73（`2420484ac` hours 層＋`7ad75e85d` 渲染）
- 實碼依據：`data/v2/tools/build_subject_cards.py`（`hourly_general_rows`/`general_hour_state`）、`assets/app.js`（`v2HourSubjectCell` L2386、`decorateWeatherTimeline` L2856、timeline 表 L2207–2226）

## 0. 兩欄的資料來源不同——先釐清架構

| 欄 | 來源 | 語義 |
|---|---|---|
| 狀態 | `apps/web-v2/evaluations-details/<spot>.json`（評估 bundle 逐小時 `hours[].status`，**所選題材**的 curated 判定） | 「這個小時，你選的題材符不符合」 |
| 適合題材 | `data/v2/evaluations/subject-cards-20261112T202312Z.json`（**place 層** derived hours buckets：fit=curated `good_hours` 覆蓋；ok/no/unk=general-v0.1 floor） | 「這個小時，哪些策展題材的窗覆蓋它／一般拍攝天氣是否許可」 |

owner 截圖當下（main 樹 34c7bf631）：details 全部生成於 **2026-11-13T07:12:12Z**（bundle-071212），subject-cards 仍派生自 **bundle-20261112T202312Z**——兩個不同 run 的預報。tw-197 11-14 的窗，1112 run＝`['22:00']`、071212 run＝`['21:00','22:00','23:00']`；11-15 前者＝`18:00–23:00`、後者多出 `00:00–04:00`。owner 看到的「21:00 ✓符合（details）」配「✗ 非日照時段（subject-cards，21:00 不在窗內→落入 no 桶 light_window）」正是兩 run 拼接的結果。

## 1. 矛盾分類與根因（四類，含歸屬）

### 類別 A（owner #1、#2 直接根因）：跨 run 漂移——派生/流水線層
- **現象**：同一小時，狀態欄 ✓ 符合、題材欄 ✗ 短原因（或夜窗 chip 只出現一小時）。
- **根因**：狀態欄（details，071212 run）與題材欄（subject-cards，1112 run）來自不同 bundle。兩 run 預報窗不同→同列拼接必然矛盾。**不是 off-by-one**：同 run 內 `good_hours→hours.fit` 映射逐一比對 1,338 個 place-day，**0 不一致**；CL-UI-73 派生層忠實。
- **歸屬**：派生層（subject-cards 未與 details 同源）＋CI/部署層。CL-UI-70（2c1a524bc）「同 job 重生成 subject-cards」已 merge，但 071212 run 發生在 merge（10:32Z）之前，main 上的現存產物仍是 drift 態；下一次排程 run 應自癒。**但自癒是運氣不是契約**：目前沒有任何驗證斷言「subject-cards.derived_from 與 details.generated_at 同 run」。
- **規模**：SAT place-day 1,307 中 **682 天**兩 run 窗不同；owner 的 11-14/15 兩天 439 個 SAT 天中 **254 漂移**；「狀態✓但題材欄無 chip」小時 **1,057**。tw-197 兩天全部命中（21/22/23 vs [22:00]；00–04 缺）。

### 類別 B（owner #2 殘餘根因，自癒後仍在）：夜間小時的 light_window 語義誤用——派生層＋詞表
- **現象**：夜間小時（不在任何策展窗內）題材欄顯示「✗ 非日照時段」——對夜景/夜窗題材景點是語義顛倒：夜景窗本來就是夜間，太陽高度≤-6 是該題材的**成立條件**，不是失敗原因。
- **根因**：`general_hour_state()`（build_subject_cards.py L224）把 `sun_elevation <= GENERAL_SUN_ELEVATION_MIN(-6)` 記為 `light_window` 違反→`hours.no[hh]='light_window'`→渲染（app.js L2402）經 `fail_reason_short.light_window`＝「非日照時段」。詞沿用 CHALLENGER-13 §5-2 已裁定的中性化方向，但 hours 層**把「非日照」用在了夜窗題材的夜間小時上**——這個短詞只該描述日窗題材在夜間的狀態。
- **歸屬**：派生層（bucket 規則）＋copy 詞表層。注意 `data/v2/tests/test_cl_ui_73_hourly_subject_cards.py::test_night_hour_votes_light_window` 目前把此行為**當正確行為 pin 住**，修正時須同步改 pin。
- **規模**（1112 現行產物）：夜間小時 ✗非日照時段共 **3,352 place-days / 28,962 小時**，460/460 景點全中（tw 1,557、us 1,095、jp 700 天）。同 run 重生成（071212）後「某題材該小時 SAT（狀態✓）但題材欄 ✗非日照時段」仍有 **291 小時**（夜窗題材景點 43）——即自癒後不會消失的部分。
- **附帶資料層自相矛盾**：同一天**同一小時可同時在 `fit` 與 `no` 兩桶**（1112 產物 1,163 小時/351 天；tw 188、jp 55、us 108）——22:00 同時「夜景覆蓋」又「light_window 違反」，目前只靠渲染優先序（fit>ok>no）遮蔽，任何渲染層重排都會翻出矛盾。

### 類別 C（owner #3）：兩欄定義不同源，同列並讀即矛盾——渲染層語義切割
- **現象**：15:00–17:00 狀態「⚠️ 未符」、題材欄「○ 可拍」。
- **根因**（三層疊加）：
  1. **判定源不同**：狀態欄＝所選題材的逐小時 curated 判定（門檻含雲量/風速/潮汐/水面等完整條件）；題材欄＝place 層 general-v0.1 floor，**只檢查 vis/降水/RH/太陽高度四項**。curated 因風速或雲量失敗而 floor 通過是常態。
  2. **UNFAVORABLE 一律譯「未符」**：app.js `v2HourLabel()` L2764 不區分「天氣失敗」與「窗未到（幾何必然）」。逐小時 FAIL 分布中窗類幾何 metric（light_window 36,383、sunset 28,824、sunrise 10,562、golden 8,075）遠大於天氣類——大量「未符」其實是「🕒 非建議時段」的誤用（CHALLENGER-13 P2/P4 的**小時版**；`state_outside` 詞已存在但未接上）。
  3. **「○ 可拍」文案與日層三級「可拍」同名不同義**：日層 tier_shootable＝「策展皆敗但 general 可拍」，小時層 ok 桶＝「floor 通過」；同詞異義放大衝突感。
- **歸屬**：渲染層（欄位敘事＋狀態映射）＋派生層（floor 範圍定義）。**資料本身沒有錯**——同一小時「夜景題材未符、一般拍攝可拍」可以同時為真；錯在兩欄共用「未符/可拍」詞彙卻不標明各自評估對象。
- **規模**（同 run 071212 重生成後仍在）：「任何題材該小時 UNFAVORABLE＋題材欄 ○可拍」**19,576 小時**（夜窗題材景點 4,854）；日層同構「status=failed 且當日有 ok 小時」2,401 天（tw 1,107、us 765、jp 529）。tw-197 11-14 15–17 的具體案例：071212 run 中該三小時能見度 1.56–2.24 km＋降水 3.4–5.2 mm，floor 實際也 fail——owner 看到「○可拍」同樣是 1112 產物的殘影（類別 A）；但 jp-001 等處「天氣好、僅窗未到→未符＋可拍」是同 run 真實存在的語義衝突。

### 類別 D（次要，窗邊界桶策略）：子小時桶不可達＋跨 run 邊界小時忽有忽無
- `hours.fit` 有 **720 個子小時桶**（17:35/05:40 等，681 place-days），逐時表只有 :00 列，**這些桶永遠不可達**；藍調窗邊緣小時是否出現 17:00 桶，隨 run 的取整而異（CHALLENGER-13 P7 已註記 11-14 缺 17:25 桶），造成「窗邊界忽進忽出」的觀感。非 off-by-one bug，屬桶生成策略未統一。

## 2. 修正建議

1. **（類別 A，最高優先）同源契約＋驗證斷言**：CI 在 update_evaluations 同 job 內重生成 subject-cards（CL-UI-70 已做）之外，加一個 fail-fast 斷言：`subject-cards.derived_from.source_bundle_sha256 == evaluations-latest 對應 bundle sha` 且 details.generated_at 同 run，否則 job 失敗。手動重錨流程（如 CL-INT-158）也必須連動重生成 subject-cards。
2. **（類別 B）夜間小時不再以 light_window 進 no 桶**（`general_hour_state`/`hourly_general_rows`）：
   - `sun_elevation<=-6` 的小時：若任一策展題材窗覆蓋→進 fit（現行）；**否則從 no 桶移除 light_window**——該小時若 curated 窗類 metric PASS 而天氣 metric 違反，no 詞應為天氣詞（厚雲/霾/雨，對齊 CHALLENGER-13 §5-1 的 hours 版）；若天氣全過僅窗未覆蓋，進中性桶（渲染為 dash 或「非拍攝時段」，不用失敗式短詞）。
   - **清除 fit∩no 雙值**：小時進入 fit 時同步從 no 桶移除（單一事實源），渲染優先序不再承擔遮蔽矛盾的责任。
   - 同步改 pin：`test_cl_ui_73_hourly_subject_cards.py::test_night_hour_votes_light_window` 與 `cl-ui-73-hourly-subject-column.test.mjs`。
   - 詞表：`fail_reason_short.light_window` 的使用範圍限縮為「日窗題材×夜間小時」；夜窗場景改用天氣詞或中性詞。
3. **（類別 C）欄位語義切割＋狀態映射三分**：
   - 狀態欄加歸屬標示（表頭 `th_status`→「狀態〈夜景〉」或在圖例說明「狀態＝所選題材的逐時判定；適合題材＝全題材窗＋一般拍攝許可」）。
   - `v2HourLabel()` 三分：`GUIDANCE_SATISFIED`→✓符合；UNFAVORABLE 且唯一 FAIL 為窗類幾何→🕒非建議時段（`state_outside`，機制已存在）；UNFAVORABLE 含天氣 FAIL→⚠️未符（可帶小時天氣短詞）。
   - 「○ 可拍」文案區分粒度：小時桶改「○ 一般拍攝」或 title 註明 floor 四指標，避免與日層 tier_shootable 同詞異義。
4. **（類別 D）統一子小時桶策略**：子小時桶（17:35）歸入最近整點列（或兩桶並存時整點列標 ✓）；在窗桶生成處加註解固定策略（P7 收尾）。

## 3. 影響面估計

| 修法 | 觸及 | 測試影響 |
|---|---|---|
| A 同源斷言 | `.github/workflows/update_evaluations.yml`（+~10 行）；無產品碼 | 無 pin 變更 |
| B 夜桶規則 | `build_subject_cards.py`（general_hour_state/hourly_general_rows，~30 行）＋`fail_reason_short.json`（使用範圍註記）；subject-cards 產物需重生成（CI 自帶） | `test_cl_ui_73_hourly_subject_cards.py`（night pin 翻轉）、`cl-ui-73-hourly-subject-column.test.mjs`；不觸 engine/day 層 pins |
| C 欄位語義 | `assets/app.js`（v2HourLabel＋表頭/圖例，~15 行）＋三語 i18n；cache-bust cluiNN | CL-UI-43/73 渲染 pin、i18n 三語 pin、`test_opportunity_adapter.py` 子串 pin |
| D 桶策略 | 窗桶生成（engine 側或派生側）＋註解 | 子小時桶相關測試 |

- 評估引擎（逐小時 curated 判定）**不需改**：同 run 內引擎數據自洽；錯在派生與呈現。
- 日層三級（recommend/shootable/not_recommended）與 hours 桶無衝突（tier=not_recommended 的天數 0 天帶 ok 小時），不需動。
- 全庫矛盾規模量級：A＝682 天漂移（自癒後歸零，需斷言守住）；B＝3,352 天夜間誤詞＋1,163 小時雙值；C＝19,576 小時同列衝突；D＝720 個不可達桶。

— CHALLENGER-14（知識隔離挑戰者；證據＝main 34c7bf631 產物逐位掃描＋bundle-071212 同 run 重生成對照＋app.js/build_subject_cards.py 實碼）
