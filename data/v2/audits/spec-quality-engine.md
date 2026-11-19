# ChaseLights 攝影題材規則重構與 QUALITY 計分引擎規格書

> **接收聲明（CL-DATA-75 Phase 0）**
> - 供給者：owner（Richard），經 Telegram 於 **2026-11-20 02:18（台北時間 UTC+8）** 傳入 manager 會話。
> - 收取方式：manager 會話全文接收後原樣落 repo；本檔為 **逐字轉存**（未增刪改 owner 原文，僅加本聲明與檔頭）。
> - 地位：**Phase 1–3（ETL 標準化→QUALITY 引擎→S_rank/全量重生成）之唯一施工規格**。Phase 0（本票 CL-DATA-75）僅施工 §1 四項邏輯修正並完成 §2 單位稽核（稽核不動），其餘章節尚未實施。
> - 落 repo 日期：2026-11-20。

---

## 1. 既有規則 4 項高優先級邏輯修正
1. 山景展望 (`mountain_vista`)**：移除 `cloud_cover_mid [30, 60]%` 的「必須」限制（避免晴空萬里被誤殺），改列為 `QUALITY` 加分項；補上 `visibility_km >= 15` 與 `cloud_cover_low <= 30` 為 `required`。（註：`jp-015-P02` 皇居廣場全景應改歸類為 `golden_hour` 或城市地景）。
2. **星空 (`astrophotography`)**：解決月仰角與月相條件互斥問題，月光 `required` 改為 `any_of` 雙軌邏輯：`moon_altitude_deg < 0` **OR (moon_illumination <= 0.25 AND moon_target_separation_deg >= 45)`；移除 `galactic_core_altitude_deg >= 20 的硬門檻（避免封殺冬季星空），改列為 QUALITY 加分項。
3. **金色時刻 (golden_hour) 與冰雪 (snow_ice)**：
   - golden_hour 必須將 golden_hour_window 設為 `required`（原本誤設為 QUALITY 導致正午觸發），並補上 `cloud_cover_low <= 40`。
   - `snow_ice` 必須補上 snow_depth_cm > 0`（或 `snowfall_cm_h > 0`）與排除降雨，風速上限由 `15.0 m/s 收緊至 `<= 7.0 m/s`。
4. **複合主體與空值參照修正**：
   - `jp-010-P01`（大石公園季節植栽與富士山）補上 `cloud_cover_low <= 30` 與 `visibility_km >= 15`；補齊花季區間。
   - `jp-010-P02`（逆さ富士）移除 `季節窗(必須)=window_open`（全年可拍，避免對照空值欄位報錯）。

---

## 2. Open-Meteo ETL 標準指標與單位換算
進入規則引擎前，ETL 層必須將原始欄位統一換算為以下標準 Key 與單位：
- `wind_speed_10m` (m/s)：請求 Open-Meteo 時帶入 `&wind_speed_unit=ms`。
- `precipitation` (mm/h)：小時降水量。
- cloud_cover / cloud_cover_low / cloud_cover_mid (%, 0–100)；`cloud_cover_mid_high` = `max(cloud_cover_mid, cloud_cover_high)`。
- `visibility_km` (km)：Open-Meteo 原始單位為 `m`，需執行 `visibility / 1000.0`。
- `snow_depth_cm` (cm)：Open-Meteo 原始單位為 `m`，需執行 `snow_depth * 100.0`。
- `aerosol_optical_depth` (1, 無因次)：Open-Meteo Air Quality API `550nm`。
- 天文計算指標（Astral / Ephem）：`moon_altitude_deg` (deg), moon_illumination (0–1), moon_target_separation_deg (deg), galactic_core_altitude_deg (deg)。

---

## 3. 規則 JSON Schema（核心結構範例）
支援 required`（頂層 `AND`，支援巢狀 `any_of / `all_of`）與 `quality`（連續梯形區間）：

{
  "opportunity_id": "jp-010-P02",
  "place_id": "jp-010",
  "tag": "water_reflection",
  "windows": {
    "time_of_day": ["civil_daylight"],
    "seasonal": null
  },
  "conditions": {
    "required": [
      { "metric": "precipitation", "op": "lt", "value": 0.2 },
      { "metric": "wind_speed_10m", "op": "lte", "value": 1.8 },
      { "metric": "cloud_cover_low", "op": "lte", "value": 30 },
      { "metric": "visibility_km", "op": "gte", "value": 15 },
      { "metric": "aerosol_optical_depth", "op": "lte", "value": 0.6 }
    ],
    "quality": [
      { "metric": "wind_speed_10m", "weight": 3.0, "ideal": [0.0, 0.8], "acceptable": [0.0, 2.0] },
      { "metric": "golden_hour_match", "weight": 2.0, "ideal": [1, 1], "acceptable": [0, 1], "bonus_window": "golden_hour" },
      { "metric": "cloud_cover", "weight": 1.5, "ideal": [20, 50], "acceptable": [0, 75] }
    ]
  }
}

---

## 4. `QUALITY` 梯形隸屬函數與綜合排序公式

1. **Gatekeeper**：$G(t) = \mathbb{I}(\text{time\_of\_day} \land \text{seasonal} \land \text{required})$。若 $G(t) = 0$，直接回傳 eligible = false 且 $S_{\text{quality}}(t) = 0$。
2. **單項梯形隸屬函數 $q_i(x) \in [0, 1]$**（四元組 [a, b, c, d]`，其中 [b, c] 為 `ideal`，[a, d]` 為 `acceptable`）：
   - $x \le a$ 或 $x \ge d \implies 0$
   - $a < x < b \implies (x - a) / (b - a)$
   - $b \le x \le c \implies 1$
   - $c < x < d \implies (d - x) / (d - c)$
   - **星空月光覆寫**：當 `moon_altitude_deg < 0` 時，強制令 $q_{\text{moon}} = 1.0$。
3. **加權品質分 $S_{\text{quality}}(t) \in [0, 100]$**：
   $$S_{\text{quality}}(t) = 100 \times \frac{\sum_{i=1}^{n} w_i \cdot q_i(x_i(t))}{\sum_{i=1}^{n} w_i}$$
   （若 $G(t) = 1$ 且無 quality 規則，預設基準分 `75.0`）。
4. **分級與景點綜合排序分**：
   - `recommend`：$S_{\text{quality}} \ge 75$；`good`：$45 \le S_{\text{quality}} < 75$；`marginal`：$S_{\text{quality}} < 45$。
   - 綜合排序分：$S_{\text{rank}}(t) = \text{AGLI}^{0.35} \cdot S_{\text{quality}}(t)^{0.65}$。

---

## 5. 10 大攝影題材 `QUALITY` 權重與梯形四元組 [a, b, c, d]
| 題材 (tag) | metric (unit) | weight | [a, b, c, d] |
| :--- | :--- | :---: | :--- |
| water_reflection | wind_speed_10m (m/s) / golden_hour_match / cloud_cover (%) | 3.0 / 2.0 / 1.5 | [0, 0, 0.8, 2.0] / [0, 1, 1, 1] / [0, 20, 50, 75] |
| mountain_vista | cloud_cover_mid (%) / visibility_km (km) / golden_hour_match / aerosol_optical_depth | 2.0 / 2.0 / 1.5 / 1.0 | [0, 20, 50, 75] / [15, 30, inf, inf] / [0, 1, 1, 1] / [0, 0, 0.15, 0.5] |
| sunrise / sunset | cloud_cover_mid_high (%) / cloud_cover_low (%) / aerosol_optical_depth | 3.0 / 2.5 / 1.0 | [5, 25, 65, 85] / [0, 0, 10, 35] / [0, 0.05, 0.25, 0.6] |
| golden_hour | cloud_cover_low (%) / cloud_cover_mid_high (%) / aerosol_optical_depth | 2.5 / 1.5 / 1.5 | [0, 0, 15, 40] / [0, 15, 45, 70] / [0, 0, 0.2, 0.5] |
| city_night | blue_hour_match / visibility_km (km) / aerosol_optical_depth / wind_speed_10m (m/s, 水岸) | 2.5 / 2.0 / 1.5 / 2.0 | [0, 1, 1, 1] / [10, 25, inf, inf] / [0, 0, 0.15, 0.5] / [0, 0, 1.0, 2.5] |
| astrophotography | cloud_cover (%) / moon_illumination / galactic_core_altitude_deg / aerosol_optical_depth | 3.0 / 2.5 / 1.5 / 1.5 | [0, 0, 5, 20] / [0, 0, 0.05, 0.35] / [0, 25, inf, inf] / [0, 0, 0.1, 0.3] |
| seasonal_foliage | cloud_cover (%) / wind_speed_10m (m/s) / golden_hour_match | 2.0 / 2.0 / 1.5 | [10, 40, 75, 95] / [0, 0, 1.5, 5.0] / [0, 1, 1, 1] |
| snow_ice | snow_depth_cm (cm) / wind_speed_10m (m/s) / golden_hour_match | 3.0 / 2.0 / 1.5 | [2, 15, inf, inf] / [0, 0, 2.5, 7.0] / [0, 1, 1, 1] |
| overcast_soft_light | cloud_cover (%) / wind_speed_10m (m/s) / precipitation (mm/h) | 3.0 / 2.0 / 1.5 | [70, 85, 100, 100] / [0, 0, 1.5, 4.5] / [0, 0, 0.1, 0.5] |
| scenic_lookout | visibility_km (km) / aerosol_optical_depth / cloud_cover_low (%) | 3.0 / 2.0 / 1.5 | [15, 35, inf, inf] / [0, 0, 0.12, 0.4] / [0, 0, 10, 30] |
