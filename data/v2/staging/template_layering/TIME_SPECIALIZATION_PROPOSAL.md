# 題材條件分層化提案：基底 × 時段特化（v0.1 草案，待 owner 裁定）

日期：2026-10-31 ｜ 狀態：PROPOSAL-DRAFT（未經 owner 核准不得實作）
提出背景：owner 指示「日落應屬於白天題材的特化型」——同一景點的條件應分層共用，
時段特化只描述額外條件，不再以 12 個平面模板各寫一份完整契約。

## 0. 治理邊界

- 對外顯示的 12 題材詞彙**不變**（mountain_view / overlook / reflection / cloud_sea /
  sunrise / sunset / golden_hour / blue_hour_city / overcast_soft / city_night /
  night_sky / seasonal_plant；verdict 另含 geological_landform / waterfall）。
- 本提案新增的是**內部組合層 ID**（`base:*`、`spec:*`），不改變 metric-vocabulary、
  不新增 metric、不改任何 threshold 數值。
- 展開後的 per-opportunity contract 與現行 canonical 位元組等價（parity gate），
  評估器 / bundle schema / UI 不需修改。

## 1. 現況證據（250 機會契約掃描）

16 種去重條件組合，其中 sunset×44、mountain_view×54 為完全相同組合的大量複本——
複本正是分層化要消除的維護負擔。

各 metric 出現情況：
- `precipitation`：16/16 組合全數出現（REQUIRED）→ 唯一真正的全體基底
- `aod_550nm`：12/16（缺 sunrise、reflection、overcast_soft、seasonal_plant 部分組合）
- 雲況：`cloud_cover_low` / `_mid` / `_mid_and_high` / `_total`（門檻各模板不同）
- 風象：`wind_speed_10m`（reflection、overcast_soft、seasonal_plant）
- 無即時觀測源類：`water_surface_state`（reflection）、`seasonal_state`（seasonal_plant）、
  `river_flow_state`（waterfall draft）→ 一律 propagate_unknown
- 宣告類：`landform_present`（geological_landform，owner-declared deterministic PASS）
- 大氣剖面（雲海專用）：RH 925/850、LCL、T850−T925、wind 850
- 時段窗：`sunrise_time_window` / `sunset_window` / `blue_hour_window` / `golden_hour_window`
- 夜間叢集：`astronomical_darkness` + `moon_altitude` + `moon_illumination_fraction` +
  `moon_illuminance_proxy` + `moon_target_separation_deg` + `galactic_core_altitude`

## 2. 分層定義

### L0 全域基底（所有機會繼承）
| layer_id | 條件 | 依據 |
|---|---|---|
| `base:precipitation` | precipitation REQUIRED | 16/16 組合 |

### L1 主題基底（景點/主題性條件，由機會宣告）
| layer_id | 條件 | 適用 |
|---|---|---|
| `base:atmospheric_clarity` | aod_550nm REQUIRED | 霧霾敏感題材（現行 12/16） |
| `base:cloud_state` | 雲況條件（低/中/中高/總，門檻沿用各模板現值） | 各模板現值不同，**隨模板帶入、不在層內定值** |
| `base:wind_state` | wind_speed_10m REQUIRED | reflection / overcast_soft / seasonal_plant |
| `base:water_surface` | water_surface_state REQUIRED（NO_SOURCE→UNKNOWN） | reflection |
| `base:seasonal` | seasonal_state REQUIRED（NO_SOURCE→UNKNOWN） | seasonal_plant |
| `base:landform` | landform_present REQUIRED（declared PASS） | geological_landform |
| `base:river_flow` | river_flow_state REQUIRED（NO_SOURCE→UNKNOWN） | waterfall |
| `base:atmospheric_profile` | RH925、RH850、LCL、T850−T925(QUALITY)、wind850(QUALITY) | cloud_sea 專用 |

### L2 時段特化（互斥擇一；特化繼承 L0+L1 全部條件）
| layer_id | 附加條件 | 對應顯示題材 |
|---|---|---|
| `spec:day` | （無附加） | mountain_view、overlook、reflection、cloud_sea、geological_landform、overcast_soft、city_night* |
| `spec:sunrise` | sunrise_time_window REQUIRED + 該模板雲況層 | sunrise |
| `spec:sunset` | sunset_window REQUIRED + 低雲/中高雲/AOD | sunset |
| `spec:golden` | golden_hour_window REQUIRED + 雲況/AOD | golden_hour |
| `spec:blue` | blue_hour_window REQUIRED + 總雲量/AOD | blue_hour_city |
| `spec:night` | astronomical_darkness + moon 叢集（6 metric） | night_sky |

\* `city_night` 現行契約無時間窗（夜景以燈光為主），維持 `spec:day` + 城市能見度層；
`night_sky` 才是 `spec:night`。此區別照現行模板語意保留，不在本提案變更。

### 顯示名稱規則
`display_genre = f(subject_base, time_spec)`，映射表如下（對外 12 詞彙不變）：

| subject_base | spec:day | spec:sunrise | spec:sunset | spec:golden | spec:blue | spec:night |
|---|---|---|---|---|---|---|
| scenic_view（山/展望） | mountain_view | sunrise | sunset | golden_hour | — | night_sky |
| water_body（水面） | reflection | — | sunset | golden_hour | — | night_sky |
| geological | geological_landform | — | — | golden_hour(QUALITY) | — | night_sky |
| vegetation | seasonal_plant | — | — | golden_hour | — | night_sky |
| cityscape | city_night | — | sunset | — | blue_hour_city | — |

（「—」= 該組合現行不存在；不新增。`waterfall` 為 draft，維持現狀待 owner 補 river_flow 觀測源。）

## 3. 錯置清單（現行契約 vs 名稱語意；待 owner 逐筆裁定）

| opportunity_id | 現行模板 | 名稱 | 建議新組合 |
|---|---|---|---|
| tw-027-P02 | geological_landform | 月世界夜間投光地景 | geological × spec:night |
| tw-035-P05 | seasonal_plant | 六十石山丘陵／涼亭銀河星空 | vegetation × spec:night |
| tw-036-P02 | sunset | 七星潭海岸星空／銀河帶 | scenic_view × spec:night |
| tw-038-P02 | geological_landform | 三仙台銀河 | geological × spec:night |
| tw-082-P06 | sunset | 鯉魚潭水岸光影節夜景與裝置藝術 | city_night（人工光影）或 water × spec:night（owner 裁定） |

裁定後效果：這 5 筆會得到天文黑暗+月照條件，白天不再出現「條件符合」。

## 4. 遷移計畫（核准後執行）

1. **撰寫 staging 層定義**：`data/v2/staging/template_layering/layers.json`
   （L0/L1/L2 定義 + 各模板 → 層組合映射）。
2. **機械拆解**：工具把每個機會現行 contract 分解為 (base_layers, time_spec)；
   任何無法映射的 metric → 阻擋並列出（fail-closed，不靜默丟棄）。
3. **parity gate**：展開(組合) == 現行 canonical contract 位元組等價
   （沿用 source-lock sha256/blob_sha 驗證慣例）。位元組不等價 = 遷移失敗，不得准入。
4. **錯置 5 筆**：owner 裁定後以「現行契約 + 附加夜間層」產生新 staged contract
   （這 5 筆展開結果會**改變**——這是語意修正，parity gate 對這 5 筆豁免、
   改以 revision note 記錄變更理由）。
5. **canonical 寫回**：staged → 准入 → source-lock re-pin（治理不變式照舊）。
6. **評估器零改動**：evaluate_batch 繼續吃展開後 contract。

## 5. 明確不做的事

- 不新增顯示題材詞彙（維持 owner 的 12 詞彙 + verdict 詞彙）
- 不改任何 threshold/operator 數值（除第 3 節 5 筆經裁定的語意修正）
- 不在 GUIDANCE 語意之外引入分數（EXIF 校準路線已由 owner否決）
