# Design gaps — round 16（九州批次，CL-DATA-68）

來源：data/v2/audits/challenger/round16-kyushu.md（2026-11-12）。本檔只記錄「現行條件系統無法表達、且禁止偽造條件」的設計缺口；不修、不造假資料。

## 1. jp-085 青島（鬼之洗衣板）— 潮汐條件缺失

- 景點id：jp-085-P01（geological_landform「鬼之洗衣板波紋岩」）
- 缺口：波紋岩可拍性高度依賴干潮（滿潮時岩盤大半沒入海中，干潮前後 1–2 小時為最佳窗口，宮崎市官方資料），條件鏈完全沒有潮汐語義；評估窗把整個白日標為良好時段，大潮滿潮日會給出看不到岩盤全貌的建議。
- 建議方案：新增 OCEAN domain 潮汐指標（如 `tide_state` / `tide_height_m`），由潮汐預報源（JMA 潮汐表／Open-Meteo Marine API 未含潮位，需獨立源）輸出逐小時潮位，條件「干潮窗 ±2h」；無源前可比照 river_flow_state 的誠實 UNKNOWN 模式先佔位。
- 需要 owner／新資料源：owner 核准潮汐資料源與閾值（哪個潮汐站、干潮窗寬度）；新資料源：JMA 潮汐觀測/預報或等效 API（青島最近檢潮所：宮崎港）。

## 2. jp-058／jp-059／jp-076 — 火山警戒レベル條件缺失

- 景點id：jp-058-P01（櫻島・湯之平展望所，現レベル 3 持續中）、jp-059-P01（阿蘇・草千里，現レベル 2）、jp-076-P01（大観峰，不在管制圈——僅需揭示性資訊）
- 缺口：火山活動／降灰／噴煙量／噴火警戒レベル不在任何條件域；爆發日展望可被噴煙完全遮蔽（aod_550nm 為日尺度均值，不反映瞬時爆發），レベル升級時入山規制也使「可達性」失真。jp-058 本窗成立質疑（中）；jp-059 設計層缺口（低）；jp-076 不在管制圈、僅受益於揭示資訊（低）。
- 建議方案：JMA 已有火山口別 `volcanic_activity` 指標佔位先例（jp-092–095／tw-121–124／us-159–163，USGS HVO feed pending、fail-closed）。JMA 側對應：噴火警戒レベル（506 櫻島／505 阿蘇）＋爆發/噴煙量實況。 levelem 3+ 時作為 REQUIRED FAIL（或 BLOCKER），レベル 2 以下不否決；降灰量另議。
- 需要 owner／新資料源：owner 核准 JMA 火山情報抓取（tenki.jp/JMA VOL report 無結構化 API，需爬取或人工更新節奏）；對照表：景點→火山口→レベル閾值。

## 3. jp-091 屋久島白谷雲水峽 — 颱風後步道封閉狀態

- 景點id：jp-091-P01（waterfall「苔谷溪流水霧」）
- 缺口：颱風 24 號後部分步道（弥生杉路線②–⑤–④、飛流橋・飛流歩道、入口～⑫）封閉（2026-10-16 公告、10/18 再開園後仍有區段通行止め）；卡片無步道/園區狀態條件，只有泛用 river_flow_state=UNKNOWN。本窗卡片無 good_hours、實害低，屬條件覆蓋缺口。
- 建議方案：SUBJECT_STATE domain 的 `trail_status`（open / partial_closure / closed）條件，由園區官方公告人工維護（no live source 時 propagate unknown 誠實標示）；closure 屬事件型資訊，適合放 access/safety notes + 條件佔位，不偽造自動化。
- 需要 owner／新資料源：owner 核准人工維護流程與更新責任人（屋久島環境省/ y-rekumori.com 公告頁作為源）；無結構化 feed，短期只能人工。

---
共通背景：本批已修復項（jp-090 季節窗、jp-034-P01/P03 營業窗、jp-057 纜車窗、jp-034-P02 事件語義）見 task/CL-DATA-68；venue_open_window 的日別規則（土日祝車輛禁入）屬同一設計缺口家族（日別/星期別條件）。
