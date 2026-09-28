# B96 — 合歡山空間雲況高度基準與 LCL 文案修正

## 背景

B94 已修正合歡山主峰雲海題材「專屬條件成立但仍沿用單點 cloud_sea 低分」的語意矛盾。

後續檢查 2026-09-29 重新產生的 `tw-019` weather shard 時，又發現兩個精度／文案問題：

1. 空間雲況模組診斷中的 camera elevation 使用 Open-Meteo 格點 DEM 約 3349 m，而 ChaseLights 已有合歡山主峰的已知拍攝高度 3417 m。
2. generic cloud-sea factor 仍將 `(T-Td)×125` 露點差估算稱為「估算雲底」，雖然 B94 已在 UI 標題改成 LCL。

## B96 修正

### 1. 空間模組優先使用 Place / viewpoint 已知高度

`build_spatial_request_plan()` 現在依序使用：

- Opportunity viewpoint 的 `elevation_m`（若存在）；
- Place-level `elevation`（包含 `ELEVATION_OVERRIDES`）；
- 最後才由 evaluator 回退到氣象格點 DEM。

對合歡山主峰，`tw-019-P04` 的 camera reference elevation 因此固定為 3417 m，即使 Open-Meteo camera grid 回傳約 3349 m。

這可避免垂直高差被低估約 68 m，尤其在 `min_vertical_drop_m=250` 的空間雲況門檻附近更重要。

### 2. LCL 文案一致化

以下 factor 改名：

- 中文：`估算凝結高度（LCL）低於機位約 ...`、`估算凝結高度（LCL）接近機位，入霧風險`
- 英文：`Estimated LCL ...`
- 日文：`推定LCL ...`

欄位名稱 `cloud_base_agl` 暫時保留作 schema/backward compatibility；產品文案不再將它宣稱為實際雲底。

## 2026-09-29 最新重新計算結果

B94 weather refresh 後，合歡山主峰 06:00：

- 能見度約 64.0 km
- 低雲約 2%
- P03「360°高山群峰全景」= 93
- P04「主峰下方雲海與露出群峰」= 36
- P04 spatial result = `lower_cloud_not_detected`
- 周邊 8 個較低地形樣本中，符合低雲／霧證據者 = 0

因此最新資料已不再出現「雲海關鍵條件符合但分數 48」的矛盾；目前預報更支持清晰群峰，而不是雲海。

## 回歸測試

新增／強化：

- `tw-019-P04` spatial plan 的 camera reference elevation 必須為 3417 m。
- 即使 synthetic Open-Meteo camera DEM 為 3349 m，runtime 診斷仍必須使用 3417 m。
- 中英文 LCL factor 文案不可退回「實際雲底」語意。


## Batch 編號更正

此修正最初在 PR #171 / merge commit `98d34c5` 中標成 B95；但 main 在該分支建立後已先合併另一組正式 B95（Opportunity card clarity 與 production handoff）。為避免兩個不同工作共用同一 batch ID，本文件與後續交接以 **B96** 為正式編號；既有 Git 歷史訊息不重寫。
