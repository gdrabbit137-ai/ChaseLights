# CL-DATA-78 Phase 1 施工紀錄 — spec-quality-engine.md §2＋§1.2 尾巴

日期：2026-11-20。分支 task/CL-DATA-78（worktree D:/tmp/cld78b-wt，base c18679fbf）。

## 1. ETL 標準 key（§2）落地
- **visibility_km**：V2 管線擷取時已 m→km（open_meteo_batch `_km`）；legacy 路徑
  （get_weather.py 直存 m，fetch_data.py 消費層 /1000）僅供資訊 chips，不承載門檻
  （與 CL-DATA-75 稽核一致，核對無誤、不動）。標準名 `visibility_km` 以
  METRIC_FIELDS 別名提供（→ 原始 cell `visibility`），legacy 契約名不變。
- **tw-086-P02 binding 標註修正**：`model_binding` field `visibility_m` →
  `visibility_km`（純標註，門檻 5 km 不變）。
- **snow_depth_cm**：原始 cell 由 m 直存改為 cm（×100），單位標記、metric-vocabulary
  （snow_depth 條目移除、snow_depth_cm 新增）、snow_cover_state 派生同步。
  雪深數值契約門檻全 repo 為零（稽核確認），rescale 無契約影響；Phase 2 契約門檻
  才以 cm 撰寫。舊 metric `snow_depth` 刻意**不做**別名（避免未來 m 校準門檻誤讀 cm）。
- **wind_speed_10m**：現行請求兩路徑皆已帶 `wind_speed_unit=ms`
  （open_meteo_batch / get_weather），核對無誤、不動。
- **cloud_cover_mid_high** = max(mid, high)：spec 標準名以 METRIC_FIELDS 別名提供
  （→ `cloud_cover_mid_and_high`）。
- **aerosol_optical_depth**：spec 標準名別名（→ `aod_550nm`，CAMS 550nm）。
- **astro 標準 key**：moon_altitude_deg / moon_illumination / galactic_core_altitude_deg
  同值別名（astro_hourly 輸出層），legacy key 為 serving 契約、零漂移；
  另新增 `moon_azimuth_deg`。

別名策略說明：legacy 指標名（visibility / aod_550nm / cloud_cover_mid_and_high /
moon_*）為 38 份以上契約的 serving 名，Phase 1 以評估層別名達成「標準 key 可用」，
契約名大量遷移屬 Phase 2/3（本票不動契約門檻）。

## 2. 月亮-目標夾角（moon_target_separation_deg 視線分支）
- 視線方位取 observation_relations.azimuth_deg（與 light_direction 同一 binding 鏈）；
  分離角＝月方位角與視線方位的方位面循環差（0–180°）。
- fail-closed：view azimuth 已知但月亮方位缺失 → UNKNOWN（MOON_AZIMUTH_UNKNOWN），
  不猜；月亮在地平線下 → PASS（MOON_BELOW_HORIZON_PASS，與月光閘門同語義；
  alternation 錨點本就 stand-down）。
- view azimuth 無法解析的契約（34 份 separation 契約中 30 份）維持舊銀心分離值，
  verdict 零漂移。
- 單元測試 packages/core-v2/tests/test_cl_data_78_standard_keys.py：11 例
  （含台北冬/夏銀心高度、雪梨/台北半球對比、循環差、fail-closed、sentinel 不變）。

## 3. 限定重生成（星空類）＋端到端
- 有可解析視線方位的星空契約：tw-036-P02 / tw-038-P02 / tw-076-P02 / tw-080-P02
  （視線方位 90°東向）。`cl_data_78_eval_regen.py` 依 CL-DATA-75 recipe
  --only-place-id 168h → 暫存 → splice 進 evaluations-latest.json + details。
- 實測：月升時段分離角真值 94°–178°（月亮過天頂走勢），≥45 PASS／<45 FAIL 正確閘門；
  月下時段 999 sentinel + alternation stand-down PASS 不變。
- 回歸檢查：4 份星空契約 pass_hours before→after 皆 0→0（本週月光雙軌未開窗，
  判定語義改變無製造性回歸）；全 bundle place_count 459 / opportunity_count 720 不變，
  僅 10 筆機會點（4 地點全數機會點）更新。

## 4. 驗證
- packages/core-v2 全套 pytest：403 passed / 136 subtests（7 個 ERROR 為缺
  data/v2/evaluations 產物檔的 artifact 耦合測試，在 worktree 環境 pre-existing，
  與本票無關）。
- test_cl_data_74_mounting / test_genre_templates / test_cl_ui_62 / test_cl_data_68
  等資料層閘門同輪通過（除上述 artifact 缺檔 ERROR）。
