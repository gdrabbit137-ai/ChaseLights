# 事實查證掃描 batch 6/6 — ak 景點複查（us-041/044/052/057/063/065）＋ hi 空狀態確認

日期：2026-11-06（台北標準時間）｜稽核角色：chaselights_fact_checker（唯讀）
範圍：`data/v2/opportunities/us-041-P01、us-044-P01、us-052-P01/P02、us-057-P01、us-063-P01、us-065-P01`
共 6 個 place、7 個 opportunity 檔；另確認 hi（夏威夷）區域空狀態。
方法：與 batch 1 相同——阿拉斯加/極地權威源逐筆核對 place 名稱、座標與題材地理合理性：
NPS（Denali）、BLM（Dalton Highway）、USGS GNIS、Alaska.org / Alaska DNR、維基百科。
座標容差：地標點 ≤0.5km 視為通過；0.3–2km 列 DRIFT（建議獨立驗證後再改，非阻斷）。
輸出合約：OK 清單一行；每筆 MISMATCH/DRIFT 三行（id＋名稱 | 矛盾與引用值 | 建議修正）。

## MISMATCH（確認）

無。

## DRIFT（疑似座標漂移，建議獨立驗證後再改；非阻斷）

1. `us-065-P01` Glen Alps Overlook・Anchorage／Cook Inlet／Alaska Range 日落
   - repo (61.10489, -149.68461)；Alaska.org 官方 trailhead/parking 為 (61.107222, -149.71472)，
     repo 點偏東約 1.7km（落在往 Flattop 方向山坡內），且 us-065 題材是「觀景台看 Cook Inlet 日落」，
     觀景台（Anchorage Overlook Trail viewing deck）緊鄰停車場北側，不在 repo 點位置。
   - 建議：校正至 (61.107222, -149.71472) 後以 --only-place-id 重生成該點評估。
   - 來源：alaska.org/detail/glen-alps-overlook（Coordinates 欄）＋ dnr.alaska.gov（Chugach State Park）。

## MINOR（註記，不修正）

2. `us-052-P02` Homer Spit・港灣船隻／海濱店舖街景：座標 (59.62, -151.45472) 是沙嘴
   沙尖端（Wikipedia/GNIS 兩源逐位一致），但「港灣船隻/店舖街景」主體（Homer Boat Harbor）
   實際在沙嘴中段約 (59.602, -151.417)，偏東北約 2.3km。與 P01 共用一點是現行慣例，
   屬同 place 多題材共用點語義；若日後拆點，P02 宜錨定港區實際位置。
   - 來源：Wikipedia Homer Spit、USGS GNIS 1413142、NOAA/MXAK Homer Spit 港站。

## OK（名稱、座標與題材對照權威源一致，6 place 中 5 個全數通過）

3. `us-041-P01` Mountain Vista・Denali／Alaska Range：NPS 確認 Mountain Vista 位
   Denali Park Road mile 13（nps.gov/dena/planyourvisit/mountain-vista.htm）；repo
   (63.73209, -148.90273) 與 mile 13 rest stop 一致；高緯 63.7°N 已補 light_window（CL-DATA-12）。
4. `us-044-P01` Point Woronzof：Waymarking/維基確認 Point Woronzof 岬角實測約
   (61.2035, -150.0158)；repo (61.2042, -150.01871) 偏差 ~0.2km，落在岬角展望處。注意
   「Point Woronzof Park」本身在其南約 1 英里（維基），repo 用的是岬角本點——名稱與點位正確。
5. `us-052-P01` Homer Spit・Kachemak Bay 全景：(59.62, -151.45472) 與 Wikipedia/GNIS
   Homer Spit 官方座標逐位一致。
6. `us-057-P01` Arctic Circle Wayside：BLM 官方頁 Geographic Coordinates
   66.555833, -150.810833（milepost 115 Dalton Hwy）；repo (66.55601, -150.8107) 偏差 ~20m。通過。
7. `us-063-P01` Talkeetna Riverfront Park：Alaska.org 官方 Coordinates 欄
   62.322846, -150.121177 與 repo 逐位一致；Susitna/Chulitna/Talkeetna 匯流口遠眺 Denali 語義正確。

## hi（夏威夷）空狀態確認

- `data/v2/opportunities/hi-*` 無任何檔案；catalog.v2.json 無 place_id=hi-* 紀錄。
- WeatherGrid：`assets/weather-map-regions.js` 定義 hi 區域 bbox（160.3–154.8°W /
  18.8–22.4°N，owner 裁決的獨立框）但 places 表 `hi: null`（註解明言 vacuously empty =
  honest empty state，未有真實景點前不偽造資料）——符合 regions.py 的 main-land-only
  裁決（us 主陸框排除 AK/HI）。
- 結論：hi 空狀態為「誠實空狀態」現行設計，非缺漏；本批次無需修正。

## AK bbox 覆蓋檢查（bonus）

六筆座標全部落在 ak 框（west -155.79193, east -134.40617, south 57.82759, north 68.133）
內，且皆在 us 主陸框（west -124.638）之外——分框路由正確（owner 裁決：US=mainland only）。

## 系統性觀察（回報 manager，非本批修正項）

- 全部 7 檔 altitude_m 皆 null、camera_context verification_status=provisional、
  evidence_claims audit_status=UNKNOWN（R0 skeleton），與 batch 2 tw 批次同型資料缺口。
- 座標 derivation_method 一律 imported_from_v1_viewpoint_reference——本批 5/7 檔已對上
  權威源，建議將已驗證者升級 provenance（附本報告為 evidence_ref）。
