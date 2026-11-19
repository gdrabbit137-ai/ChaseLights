# CL-DATA-75 §2 單位稽核 — 現行管線 visibility / snow_depth 實存單位 vs 規格標準

稽核日期：2026-11-20。範圍：repo-root `get_weather.py`（legacy `${region}_weather.json` 管線）、
`fetch_data.py`（legacy 消費層）、`packages/core-v2/adapters/open_meteo_batch.py`（V2 評估管線 ETL）、
`packages/core-v2/adapters/threshold_observations.py` + `evaluate_batch.py`（評估層）、
全部 `data/v2/opportunities/*.json` 契約門檻。**只稽核不動**（Phase 1 才施工）。

## 對照表（現行單位 vs 規格標準單位）

| 規格標準 Key（§2） | 現行 V2 批次 ETL 實存 | 現行 legacy 管線實存 | 契約門檻現況 | 判定 / 需同步換算？ |
| --- | --- | --- | --- | --- |
| `wind_speed_10m` (m/s) | m/s（請求帶 `wind_speed_unit=ms`，open_meteo_batch.py:130） | m/s（get_weather.py:38 同參數） | 全部 `m/s` | ✅ 一致，免換算 |
| `precipitation` (mm/h) | mm（`precipitation_unit=mm`，L131） | mm（Open-Meteo 預設） | 全部 `mm/h`（0.2/0.3 門檻） | ✅ 一致，免換算 |
| cloud_cover / _low / _mid（% 0–100） | %（cloudcover_low/mid/high，L162–164） | % | 全部 `%` | ✅ 一致 |
| `cloud_cover_mid_high` = max(mid, high) | 已存在同名派生欄（L207–209） | 無 | seasonal_plant 家族 1 筆採用 | ✅ 已符合 |
| `visibility_km` (km) | **km**——Open-Meteo 原始 m 已於擷取時 `/1000`（L167，來源註記 L230） | 原始 **m** 直存；消費層才 `/1000`（fetch_data.py:667/917/1047） | 全部宣告 `km`（≥3~≥24 門檻） | ✅ V2 一致，免換算。legacy 直存 m 但契約評估不走 legacy → 免改 |
| `snow_depth_cm` (cm) | **m**（Open-Meteo 原始 m 直存，L174，單位標記 "m"） | 無此欄位 | **無任何數值型 snow_depth 門檻**（雪題材走 CL-DATA-74 派生 `snow_cover_state` OR 枚舉） | ⚠️ 單位不符規格；但零門檻受影響——Phase 1 落 `snow_depth_cm` 時 rescale ×100 或改存 cm 即可，現行無須換算任何門檻 |
| `snowfall_cm_h` (cm/h) | cm/h（Open-Meteo 原生 cm/h，L173） | 無 | 無數值門檻 | ✅ 一致 |
| `aerosol_optical_depth` (1) | 1（Open-Meteo Air Quality API CAMS 550nm，L10/L182） | 無 | 全部無因次（0.3–0.6） | ✅ 一致 |
| 天文指標（moon_altitude / illumination / separation / galactic_core） | astro_hourly 提供（key 為 `moon_altitude`、`moon_illumination_fraction`、`moon_target_separation_deg`、`galactic_core_altitude`，無 `_deg`/無 `_fraction` 後綴） | astro 層另有 `astrophotography_environment.py` | 契約 metric 與 V2 key 同名 | ⚠️ 僅命名差異（Phase 1 ETL 標準 key 時統一，非單位問題）；月下 999 哨兵已 fail-closed |

## 結論（既有契約門檻是否需同步換算）

1. **visibility：不需要。** V2 評估管線在擷取時已 m→km，全契約 213 個 visibility 條件均以 km 校準
   （本次 §1 新增的 ≥15 km 亦直接成立）。規格 §2 的標準化在 V2 路徑上**已達成**；legacy 路徑存 m
   但僅供資訊 chips 且自帶換算，不承載契約門檻。
2. **snow_depth：不需要（現況無數值門檻）。** 全 repo 零筆數值型 snow_depth/snowfall 契約門檻；
   CL-DATA-74 的 `snow_cover_state` 派生枚舉（snowing/snow_covered/none）即是「雪深>0 或 降雪>0」
   的 OR 語義，§1.3 已採用它。Phase 1 落 `snow_depth_cm` 時才做 m→cm rescale（×100），
   並同步把 L174 的單位標記與 metric-vocabulary 詞條一起改。
3. **發現一件標註缺陷（稽核記錄，不動）：** `tw-086-P02` visibility 條件的 `model_binding`
   寫 `field:visibility_m`，與擷取後實存的 km 欄位名不符（門檻值 5 km 不受影響，純標註）。
   Phase 1 ETL 標準化時一併修正。
4. 規格 §2 的 key 命名（`*_deg`、`moon_illumination`）與現行 key（`moon_altitude` 等）在
   Phase 1 以 ETL 標準層統一，非單位問題。

（本稽核由 CL-DATA-75 Phase 0 執行；§2 施工仍待 Phase 1。）
