# Genre Review Registry — 單一入口

所有題材判定、參考照片、採集工具集中在這裡。**之後增加資料只往這裡加，不要分散。**

## 結構

```
genre_review/
  registry.json        ← 唯一主檔（機會 → 題材判定 + photos[] + sources[]）
  photos/              ← Wikimedia Commons 下載照片（含 _meta/*.json 授權資訊）
  sheets/              ← 2x2 拼圖（vision_analyze 用）
  tools/
    harvest_multi.py   ← 批次採集（Commons API 多輪搜尋 + 併發下載 + meta 記錄）
    make_sheets_v2.py  ← 拼圖產生器
  archive/
    p1/                ← 第一階段（mountain_view 批次）原始 findings/harvest_state
    p2/                ← 第二輪（其他題材批次）原始 findings
```

## 之後新增資料的標準流程（唯一入口）

1. **採集**：把新機會加進 `tools/harvest_multi.py` 的 targets（oid/zh/keywords），執行後照片自動落 `photos/<oid>/`，meta（source_page_url + 授權）自動寫 `photos/_meta/`，狀態自動合併進 `photos/_harvest_state.json`。
2. **拼圖**：跑 `tools/make_sheets_v2.py`，新拼圖落 `sheets/`。
3. **判定**：vision_analyze 逐拼圖判定 → 依 registry.json 既有格式寫入（verdict / confidence / evidence / notes / round2 關鍵詞），用 `record_finding()` 合併進 registry.json，不覆蓋既有判定。
4. **round2 補查**：registry.json 的 `round2_pending` 清單；補查後用 record_finding() 更新同一筆。
5. **整合進 canonical**：owner 裁定後，照 binding lint 規則把 verdict 寫入 canonical opportunity 的 genre_template。

## 題材詞彙（固定 12 個，不得自創）

mountain_view / overlook / reflection / cloud_sea / sunrise / sunset / golden_hour /
blue_hour_city / overcast_soft / city_night / night_sky / seasonal_plant
（非攝影題材物件 → D）

## 狀態

- registry.json：408 機會 / 1609 照片（407 個別 + 124 拼圖多照）+ 379 筆判定 findings
- 來源：photo_refs/p1（mountain_view 批次）、photo_refs/p2（其他題材批次）已全量併入並歸檔
- round2 補查 pending：26 筆（多機會共用批次，非目標題材證據不足）
