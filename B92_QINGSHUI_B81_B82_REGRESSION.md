# B92 — 清水斷崖 B81/B82 主線回歸與方向差修正

Date: 2026-09-28 (Asia/Taipei)

## 目的

重新驗證 `tw-034-P03 — 清水斷崖晨霧、雲霧山海` 在目前 `main` 的有效行為，並補齊 B81/B82 沒有完整鎖住的回歸條件。

本批次不改變 B81 題材 admission，也不改變 B87/B88 的 2.5 km 構圖可讀性 guard / 68 分 hard cap。

## 必須維持的主線 contract

1. **低能見度、但未達 camera whiteout**
   - visibility-only 可以形成低信心晨霧 planning candidate。
   - 不能把單一低能見度數值敘述成已確認晨霧。
   - 若 camera visibility < 2.5 km，`subject_readability_uncertain = true`，最終 Opportunity score <= 68。

2. **B82 北向 spatial proxy**
   - proxy bearings 固定為 broad north sector：330° / 0° / 30°。
   - 每個 bearing 都必須能獨立提供 directional corroboration。
   - proxy 只代表環境 context，不是精確斷崖位置、精確霧區或實景觀測。
   - directional promotion 必須表示 target sector 相對 camera **materially mistier**。

3. **B92 fog-code contrast 修正**
   - target `weather_code in {45, 48}` 且 camera 未 fog-coded：可作為方向差之一。
   - 若 camera 與 target 都是 fog code，fog code 本身不能再被算作 directional contrast。
   - 此時仍需 target 相對 camera 具有至少一項 material contrast：
     - visibility <= camera visibility × 0.75；或
     - low cloud >= camera low cloud + 25 percentage points；或
     - RH >= camera RH + 8 percentage points。
   - 因此「整個 camera + north sector 都是相同非白牆霧況」可以保留 local mist support，但不得被 B82 升級成 directional 88 分狀態。

4. **時間 gate**
   - `tw-034-P03` 只接受 local time < 11:00。
   - 即使 spatial directional support 成立，下午仍必須回傳 `outside_morning_mist_window`。

5. **清晰海崖重新勝出**
   - visibility 恢復到清晰山海條件時，P03 必須退出 mist candidate。
   - `tw-034-P02 — 清水斷崖山海遠眺` 必須能重新成為同時段／同日的最佳 Opportunity。
   - 目前 production snapshot 亦可見清晰條件下 P02 重新勝出，例如 2026-09-29 06:00：visibility 約 36.1 km、low cloud 0%，P02 93 分。

## 2026-09-28 資料邊界

B81/B87/B88 現有測試中標示 `2026-09-28` 的 0.7–0.8 km、1.5 km、2.8 km 等 Qingshui weather rows 是**合成回歸輸入**，用來重現規格邊界，不是保存下來的原始歷史 Open-Meteo response。

目前 repository 沒有 Qingshui 2026-09-28 的 `captured_raw_model_inputs` / field-validation replay fixture，因此可以證明「目前 runtime 對這類輸入會怎麼判」，但不能反向宣稱已重播當天原始 330°/0°/30° 格點預報。

這與 B89 的七星潭 field case 不同；七星潭已有明確標示 provenance 的 replay fixture。清水斷崖仍需要後續新增真實 field labels：

- mist with clearly readable cliff
- mist with mostly hidden cliff
- low visibility without mist
- directional mist signal with poor subject readability

新 field case 若可行，應保留最小非識別 raw model inputs，標示 `captured_raw_model_inputs` / `historical_raw_input = true`；不得把事後合成 fixture 說成原始歷史資料。

## B92 regression coverage

`test_opportunity_adapter.py` 新增／強化：

- 330°、0°、30° 每個 bearing 的單獨 positive directional case。
- camera / target 同為 fog code 且條件相同的 uniform-fog negative case。
- uniform fog 僅保留 local P03 82 分 support，不得升為 directional 88。
- spatial positive case 在 14:00 仍被 morning gate 否決。
- 29.6 km clear recovery case同時評估 P02/P03，鎖定 P02 重新勝出。
- 原有 visibility-only 0.8 km case 保留為 low-confidence 68 分候選，並修正文案註解，避免誤寫成「低能見度 alone 不可形成候選」。

## 不變的 evidence boundary

- 2.5 km 是 conservative planning guard，不是 camera-to-cliff 實際距離。
- 330° / 0° / 30° 是 broad environmental sector，不是精確攝影方位。
- forecast candidate 不等於 observed mist。
- camera whiteout 仍 fail closed。
