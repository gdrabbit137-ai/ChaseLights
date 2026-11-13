# CHALLENGER-13 —「未符·時段不對」語義審查（讀取「未符」類失敗短詞映射）

- 分支：`task/CHALLENGER-13`（base = origin/main `c3a16c4c0`）
- 性質：read-only 調查 + 報告；不含任何產品碼修改
- 日期：2026-11-13；live 產物版本：`evaluations-latest` 生成於 2026-11-13T07:12:12Z；subject-cards = `subject-cards-20261112T202312Z.json`（derived from bundle-20261112T202312Z.json）

## 1. 個案重現（大屯山助航站 tw-001「大屯山俯瞰台北盆地暮色／夜景」tw-001-P03，城市藍調模板）

Owner 截圖：明天方框顯示「✗ 未符 · 時段不對」，後天（11/15）與 11/16、11/17 顯示「符合 · 17:25」。

Live 數據逐小時驗證（tw-001-P03，傍晚時段）：

| 日期 | blue_hour_window 17:00 | 總雲 17:00 | 小時判定 | 日判定 |
|---|---|---|---|---|
| 11-13 | PASS | 68% | 符合（17:00/17:25） | 符合 |
| **11-14（明天）** | **PASS** | **100% FAIL** | 未符 | 未符 |
| 11-15 | PASS | 27% | 符合（17:00/17:25） | 符合 |
| 11-16 | PASS | 18% | 符合 | 符合 |
| 11-17 | PASS | 1% | 符合 | 符合 |

明天（11-14）的藍調窗**有發生且被正確評估**（17:00 PASS），未符是因為該時刻總雲 100%＋降雨；後天起雲量下降所以符合。**明天的窗不是「沒評到」，是「評到了但天氣不行」**（詳 §3）。

但卡片的短詞（derived subject-cards 層）卻給了「時段不對」：

```
tw-001 / 2026-11-14: dominant_metric=blue_hour_window, dominant_reason=時段不對,
dominant_source=curated_votes, tier=shootable
```

## 2. 根因（映射邏輯：`data/v2/copy/fail_reason_short.json` + `data/v2/tools/build_subject_cards.py`）

機制鏈：評估 bundle 每日 day conditions（帶 `day_verdict` + `pass_hours`）→ `build_subject_cards.py` 為每個「當日失敗題材」投一票給其「最核心被違反 metric」→ 全日票數最高者成為 place-day 的 `dominant_reason` 短詞。

核心違反的挑選規則（`_core_violation_metric`）：FAIL 條件優先；**無 FAIL 時走 CL-UI-65 擴充池：任一 PARTIAL，按 `pass_hours` 由少到多排序，最少者勝**。

對 11-14 的三個題材：
- tw-001-P01（夕照）：sunset_window PARTIAL pass_hours=2 → 投「時段不對」
- tw-001-P02（雲海）：cloud_cover_low **FAIL** → 投「低雲」
- tw-001-P03（暮色/夜景）：blue_hour_window PARTIAL pass_hours=1、cloud_cover_total PARTIAL 3、precipitation PARTIAL 17 → 最少 pass_hours 的 blue_hour_window 勝 → 投「時段不對」

票數：時段不對×2 vs 低雲×1 →「時段不對」當選。

**兩個結構性缺陷疊加：**

1. ** Tie-break 系統性偏袒窗類 metric。** 窗類條件（日出/日落/黃金/藍調/夜景/天文黑暗）一天最多只成立 1–3 小時，而天氣類條件（雲/雨/霾）動輒成立 10+ 小時。「PASS 時數最少＝最束縛」的假設對**天氣門檻**成立，對**時段窗**完全不成立：窗永遠是最少 pass_hours 的那個。結果是只要某天「窗有發生＋天氣也失敗」，主導原因幾乎必然被窗類搶走，把真正的天氣失敗說成「時段不對」——語義**顛倒**：時間其實是對的，天氣才是錯的。
2. **窗類短詞對攝影師無信息量。** `fail_reason_short.json` 把 blue_hour_window / city_night_window / sunrise / sunset / golden_hour / daylight_window 全部映射成「時段不對 / wrong time window」。夜景／藍調題材本來就是夜間窗；攝影師白天查詢時「時段不對」是必然狀態的複述，不是天氣失敗，也不是行動指引。

全庫規模（live subject-cards 全 catalog 掃描）：264 個 place-day 的主導原因是窗類 metric，其中 **244 個（92%）該窗實際有發生（pass_hours>0）**——即絕大多數「時段不對」都是被錯標的天氣失敗。短詞分布：厚雲 502、霾 430、低雲 293、**時段不對 235**、非季節 243、雨 199 等。

## 3. 對「未來日期」的裁定：不是快照時刻 bug

檢驗了 owner 的假設（評估基準時刻今天 05:00，明天的夜窗可能「還沒到所以不能評」）：**不成立**。逐小時數據顯示明天 11-14 17:00 的 `blue_hour_window` 判定為 `PASS/satisfied`——引擎對未來日期的夜窗照樣可評；11-14 全天未符是因該窗時刻雲量 100%＋降雨，與後天/11-16/17 的差異純粹是預報天氣不同。三級語義也不需要變：明天的「未符」是真實天氣結論，維持 ✗不宜／○可拍（general baseline 通過）正確。**需要修的是原因短詞，不是評估引擎。**

附帶小觀察：11-14 的逐小時網格缺 17:25 桶（其他符合日有 17:00+17:25 兩個藍調桶、11-14 只有 17:00），`pass_hours=1` 與桶數一致，屬窗邊緣取整行為，不影響結論，建議在窗桶生成處補一個註解確認。

## 4. 語義裁定（對攝影師的正確表達）

候選方案評估：

- (a) 不顯示未符、改中性語義——**不採**：明天確實不宜拍（雲 100%），隱藏真實失敗違反「每個不符判定必須帶原因」的 blueprint 鐵律。
- (c) 保持未符但短詞改「白天」——**不採**：明天 17:25 有窗，「白天」是錯的描述。
- **採 (b) 為主軸＋窗缺時退化為中性語義**：
  - **窗有發生（pass_hours>0）、天氣在窗內失敗** → 未符成立，但主導原因必須是**天氣詞**（厚雲／雨／霾／低雲），並可在卡片帶出「窗口 17:25」導引（subject-cards 的 suitable 列已存 window 小時；failed 列可加 `window_hint`）。這正是三級語義的自然表達：明天 ✗不宜（天氣），但攝影師知道去早了沒用、要等到傍晚且看雲。
  - **窗根本沒發生（pass_hours=0，如極區極晝、季節性天光）** → 未符不是天氣失敗，短詞用中性「非拍攝時段（…17:25 起）」而非失敗式「時段不對」，呈現接近既有 `🕒 非建議時段`（state_outside）語義。
  - 三級影響：窗內天氣失敗 → 維持 not_recommended；窗未發生但 general baseline 過 → shootable（「○ 可拍」已涵蓋）；僅窗缺且無其他機會 → 維持現有 outside/中性路徑。**明天 17:25 若條件會符合，引擎已會給 recommend**（11-15/16/17 即如此），無需改判定層。

## 5. 修正建議（實作層）

1. **`build_subject_cards.py` `_core_violation_metric`**：把窗類 metric（sunrise/sunset/golden/blue/city_night_window、light_window、astronomical_darkness、daylight_window）從 PARTIAL 回退池與「pass_hours 最少者勝」的排序中**排除**，除非其 `pass_hours==0`（窗未發生）且天氣類 metric 全 PASS。窗有發生時，核心違反票只能在天氣/品質類 metric 之間產生。
2. **`fail_reason_short.json`**：窗類詞拆兩類——`pass_hours==0` 用中性詞「非拍攝時段 / outside shooting window」；`pass_hours>0` 不參與主導投票（見 1）。`light_window` 的「光線不對」同樣改為中性「非日照時段」。
3. **卡片導引**：failed 列在窗 metric 有窗時附 `window_hint`（「窗口 17:25」），讓「何時該再來」有答案（選項 b 的呈現）。
4. **跨題材投票隔離**：`seasonal_state`／`landform_present`／`light_direction` 屬單題材資格條件，不應參與 place-day 層的票池（它們對其他題材無意義，且 11-15 出現「recommended chips＝雲海/藍調、day 詞＝非季節」的矛盾組合）。日層主導票限定天氣類 metric；資格類失敗只留在題材展開區的逐題材原因。
5. **一致性**：subject-cards（11-12T20:23 run）與 evaluations-latest（11-13T07:12）來自不同 run，chips／主導詞可能與 modal 逐日列互相矛盾。建議 CI 在每個 bundle 發布的同一 job 內強制重生成 subject-cards（同源原子更新）。

## 6. 系統性問題清單（owner 擴大範圍：逐類檢查「對攝影師無意義的失敗原因」）

| # | 症狀 | 根因 | 建議修法 |
|---|---|---|---|
| P1 (Major) | 夜景/藍調/夕照題材白天查詢顯示「未符·時段不對」，其實窗有發生、天氣才是失敗 | §2 兩缺陷疊加；全庫 244/264 案 | §5-1/2/3（窗類不參與投票；天氣詞＋窗口導引） |
| P2 (Major) | 窗未發生時「時段不對」是失敗語義，攝影師無行動信息 | 詞表將所有窗類統一「時段不對」 | §5-2：中性詞「非拍攝時段」＋下一窗導引（選項 b） |
| P3 (Major) | place-day 主導詞「非季節」（243 天），與同日 recommended chips 並存，矛盾呈現 | 資格類 metric 參與日層投票 | §5-4：資格類不進日層票池 |
| P4 (Minor) | `light_window`＝「光線不對」、`daylight_window`＝「時段不對」——太陽高度不足是確定性事實不是天氣 | 詞表把幾何/天文條件寫成失敗語義 | 併入 §5-2 中性詞處理 |
| P5 (Minor) | NOT_EVALUABLE 呈現 | 現況誠實（不發明原因、fallback general baseline） | 維持，不需改 |
| P6 (Medium) | 卡片短詞層（subject-cards）與 modal 詳細屬不同生成 run，可能互相矛盾 | 生成流水線不同步 | §5-5 同 job 原子重生成 |
| P7 (Info) | 11-14 缺 17:25 藍調桶（其他日有），窗邊緣取整行為 | 窗桶生成規則 | 註解確認＋統一邊緣桶策略 |

## 7. 影響面

- 邏輯：`data/v2/tools/build_subject_cards.py`（`_core_violation_metric`＋票池規則）、`data/v2/copy/fail_reason_short.json`（詞表/規則文字）。
- 顯示：assets/app.js 卡片第二行（`v2SubjectCardShortReason`）＋可選 `window_hint` 呈現；modal 逐日列（長句機制已正確，不動）。
- 測試：CL-UI-62/63/65 資料層測試需補「窗有發生時主導詞必為天氣類」斷言；fail_reason_short 詞表 pin 測試同步。
- 不影響：評估引擎（未來日期夜窗判定已正確）、三級 tier 判定、fail_reason_overrides 長句層。

— CHALLENGER-13（知識隔離挑戰者，由 live 卡片內容＋線上產物＋web 證據裁定）
