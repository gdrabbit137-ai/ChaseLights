# hourly 平面 ↔ bundle 時差對齊

**狀態**：backlog（owner 2026-11-27 裁示）
**來源**：物理與氣象邏輯稽核官 2026-11-26 體檢

## 問題（實測）

`weather_details/<region>/<place>.json`（逐時平面，modal 的逐時表就是讀它）與
`evaluations-latest.json`（判定 bundle）不是同一次抓取：

- 體檢當時 hourly 平面時間戳 `2026-11-25T19:04`，比 bundle 舊 **16 小時**
- 對照 459 個景點：**77%** 的能見度格差 > 5 km、**16%** 的低雲量差 > 50 個百分點
- 2,053 個「推薦」小時在 hourly 平面裡找不到對應列（其中 12-03 全天 722 列）

後果：使用者點開逐時明細，看到的可能是半天前的天氣，而卡片是剛算完的判定。

## 提議做法

1. 讓 `update_evaluations` 在同一次執行中**同時**寫出 hourly 平面與判定 bundle，
   兩者共用同一個 `provider_run.run_id`。
2. bundle 增加 `hourly_plane: {generated_at, sha256}`，前端只要發現不一致就在
   逐時表標註「逐時資料落後 N 小時」而不是靜靜顯示舊值。
3. 移除任何「第二次單獨抓 weather_details」的排程，避免兩條時間軸。

## 驗收標準

- 一次刷新後，`bundle.provider_run.run_id` 與 hourly 平面的 `run_id` 相同。
- 全站掃描：能見度格差 > 5 km 的比例 < 1%，低雲差 > 50 pp 的比例 < 1%。
- 逐時表的每一列都能在 bundle 的同日判定中找到對應小時（不再有 2,053 個孤兒推薦）。
- 前端在兩者不一致時一定顯示落後提示（有測試斷言）。

## 風險

- hourly 平面檔案量大（473 檔 / 948 MB），同一次執行寫出會拉長 workflow 時間；
  必要時改用「同 run_id + 只同步當日與次日」的折衷。
