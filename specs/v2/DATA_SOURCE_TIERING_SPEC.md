# Data Source Tiering Spec（跨地區資料源分級架構）

狀態：架構定案（2026-10-24 使用者確認），實作未開始。

## 0. 目的與範圍

攝影條件評分系統的資料源，由「按產品名硬編碼」改為「按角色分級＋地區 manifest 宣告」。
本 spec 適用所有現在與未來的地區；台灣是最第一個實例，不是特例。

**排除範圍（特殊題材）**：極光、閃電不進本評分預報系統，未來另立專屬預報系統
（極光＝太陽風/KP 預報，閃電＝雷達/閃電偵測網——與氣象模式完全不同源）。

## 1. 角色五分法

| 角色 | 職責 | 預設 lead time 帶 |
| :--- | :--- | :--- |
| `SHORT_HQ` | 高解析、地形敏感條件（雲海、山谷霧、稜線風、LCL） | 0–12 h |
| `MID` | 逐時銜接、小時級細節 | 12–72 h |
| `LONG` | 長天期規劃（技能下降須標註） | 72 h–16 天 |
| `AEROSOL` | 全時段透明度（AOD），垂直貫穿、與其他角色平行 | 0 h–全程 |
| `OBS` | 觀測實況校正（**不進評分**，僅供對照） | 即時 |

一個資料源可在不同地區擔任不同角色（JMA MSM 在日本＝SHORT_HQ，在台灣＝第二期加值）。

## 2. 地區 manifest（repo 設定檔）

每個地區一份宣告檔（版本化、可 CI 審查、隨 schema 版本升級）：

```yaml
region: tw
sources:
  short_hq:
    - id: cwa_wrf3
      bbox: {leftlon: 117.5, rightlon: 125.5, bottomlat: 20.0, toplat: 27.0}
      lead_hours: {min: 0, max: 12}
      resolution_km: 3
      fields: [temperature_2m_c, relative_humidity_2m_percent, fog_potential_percent,
               lcl_height_m_agl, wind_speed_10m_m_s, wind_speed_850hpa_m_s, ...]
  mid:  [{id: gfs_0p25, ...}, {id: jma_msm, bbox_note: partial}]
  long: [{id: gfs_0p25_extended, lead_hours: {min: 72, max: 384}}]
  aerosol: [{id: cams_global, lead_hours: {min: 0, max: 108},
             fields: [aerosol_optical_depth_550nm]}]
  obs:  [{id: himawari9, role_note: no_scoring}]
```

規則：
- manifest 只宣告「候選」，不做任何拼接設定——架構上不存在拼接參數
- 新增地區＝新增 manifest＋對應 adapter，**核心選源邏輯零修改**（與 i18n 原則同一精神）
- 與既有 specs/v2 的誠實原則一致：invalid/缺值 fail-closed

## 3. 選源演算法（全地區共用，唯一一條）

對每個「景點 × 時刻 × 欄位」：

```
1. 取該地區 manifest 中「提供此欄位」的候選源
2. 過濾：景點座標完整落在候選源 bbox 內（含安全邊距）
3. 過濾：lead time 落在候選源宣告時效內
4. 剩餘候選中選解析度（resolution_km 最小）最高者
5. provenance 必填：source_id、lead_time 段、resolution_km、選擇理由
```

- 平行軌道：`AEROSOL` 獨立選源，不受氣象欄位分段的 lead time 影響
- `OBS` 永不進評分，僅供 UI 對照與人工驗證

## 4. 涵蓋完整性紀律（無拼接原則）

- 源未完整涵蓋景點 → **不進候選**。禁止空間拼接、邊界混合、跨源補格
- 理由：拼接線兩側來自不同確定性模式的差異會產生假梯度（畫出假雲牆、
  評分因所在側而跳級）；破壞跨景點評分可比性；維護成本永久存在
- **誠實降級**取代拼接：候選中解析度最高者出局後，降級用次優源並在
  provenance/UI 標註（「中期解析度」「長天期、參考用」）
- 所有源皆缺某欄位 → 該欄位 `not_evaluatable`，不拿鄰近格點硬補
- 這是既有 fail-closed／誠實缺值原則從時間維度推廣到空間維度
- 每個「景點 × 時刻 × 欄位」必須恰好在**一個**源的責任區內

## 5. 首批地區草案（供逐一確認，未定案）

| 地區 | SHORT_HQ | MID | LONG | AEROSOL | OBS | 備註 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 台灣 | CWA WRF 3 km | GFS（JMA 第二期、限完整涵蓋景點） | GFS/Open-Meteo | CAMS Global | Himawari | JMA 西/南釘 120.06E/22.45N，僅加值 |
| 日本 | JMA MSM 5 km | JMA/GFS | GFS/Open-Meteo | CAMS Global | Himawari | MSM 涵蓋全日本，可直接當 SHORT_HQ |
| 美國本土 | HRRR 3 km | GFS | GFS/Open-Meteo | CAMS Global | GOES | HRRR 每 1 h 更新 |
| 歐洲 | ICON-EU／AROME | GFS | GFS/Open-Meteo | **CAMS Europe 11 km** | Meteosat | AOD 可升級 11 km |
| 高緯（冰島、挪威等） | 當地區域模式 | GFS | GFS/Open-Meteo | CAMS Global | 極光帶觀測另議 | 極光是特殊題材，不在本系統 |

> 上表為草案；各國 opendata 的實際授權、格式、更新時程須逐一查證後才寫入正式 manifest。

## 6. 與既有管線的銜接（實作順序）

1. **第一期（台灣）**：攝影評分從「綁死 GFS 12 h」改為選源演算法
   （0–12 h 用 CWA，12 h+ 用 GFS；GFS 打包時效延長至 168 h；
   AOD 維持現行 CAMS 自管管線）；每段 provenance 落地
2. **Open-Meteo pin models**：消除 best_match 不透明混合（若 LONG 採用 Open-Meteo）
3. **第二期（台灣加值）**：JMA 對「完整涵蓋」的東部景點提供逐時 MID
4. **第三期**：第二地區（建議日本——JMA MSM 既有管線可直接複用）

## 7. 驗收標準（每個地區）

- 選源結果可由 manifest＋演算法完全推導，無硬編碼特例
- 每個評分值可追溯 provenance（source_id × lead time 段 × 解析度）
- 任一源失效：降級或 not_evaluatable，不出現拼接值
- i18n：來源名稱、降級說明文字支援所有正式啟用語言
