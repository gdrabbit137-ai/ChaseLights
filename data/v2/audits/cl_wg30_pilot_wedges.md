# CL-WG-30 批次 1（資料修正）— 試點 10 景點處置紀錄

依 `data/v2/audits/camera_subject_wedges_design.md`（task/CL-WG-29）§3 委託書。registry B121.17 → B121.18（+7 entries）。

## 已補建（有證據）

| 景點／題材 | 幾何 | 證據層級 |
|---|---|---|
| tw-002-P01 象山藍調 | SUB 294.9–314.9°/0.5–1.2 km ＋ ENV 同弧 0–15 km | observation-relation static_derived（az 304.9/911 m，全庫最精確） |
| tw-003-P01 淡水夕照 | SUB／ENV 月別化 sectors_monthly（12 月弧心 246.6–295.9°±27.5°，Jan–Dec 順序） | 與 condition_contract light_direction 同源；取代 spot-level az 285 |
| tw-001-P02 大屯山雲海 | ENV 0–360°/0–8 km 下環 | 雲海家族先例（同 tw-004-P03） |
| tw-027-P01 月世界惡地 | SUB 0–360°/0–1 km 近環（omni_semantics=panoramic_terrain_ring） | 攝影常識層級，Grade-A pending |
| tw-072-P01 南雅奇岩 | SUB 0–360°/0–0.3 km 近環 ＋ ENV 60–120°/0–15 km | 攝影常識層級，Grade-A pending |
| tw-076-P01 龍磐日出 | SUB 50–130°/0–10 km ＋ ENV 同弧 0–20 km | 攝影常識層級，Grade-A pending |
| tw-076-P02 龍磐銀河 | ENV 0–360°/0–20 km（omni_semantics=celestial_envelope），無主體扇 | 天體家族規則（§4.2） |

## Pending（無證據，誠實不建扇 — CL-WG-29 §4.1）

- tw-001-P01（sunset）、tw-001-P03（city_night）：主體方位為攝影常識層級，Grade-A 證據前僅顯示機位。
- tw-002-P02／P03：觀測關係 azimuth=null。
- tw-003-P02／P03：情人橋近景題材無獨立方位證據。
- tw-004-P01／P04：102 公路主體弧 az=null。
- tw-019-P01/P02/P03/P05/P06：主峰群峰／日出／夕照主體扇 az=null（P04 雲海既有 entry 不變）。
- tw-027-P02／P03、tw-072-P02：無方位資料。
- us-015（金山／金門大橋）：**design 委託書標錯地點**——us-015 是舊金山金門大橋（非台灣金山燭台嶼），且 catalog viewpoints 無座標，無法 derive 任何扇形 → 全 pending。

## 驗證

- `audit_weathergrid_coverage.py`：50/50 entries complete，0 errors。
- `test_weathergrid_coverage.py`：9 tests OK（釘值 43→50）。
- `test_weathergrid_coverage_browser.py`：6 tests OK。
- `test_weathergrid_refresh_workflow.py`：2 failures 為 pristine origin/main 既有（workflow 釘值漂移：forecast_hours 與 JMA coupled 斷言），與本票無關。
- browser bundle 重生：weathergrid/weathergrid_coverage_browser.json（34 spots／50 opportunities）＋ weathergrid_coverage_us_browser.json（registry_version 同步 B121.18）。

## 扇形幾何語義備註

- `sectors_monthly`：type=sector 幾何的新欄位，12 筆 {arc_center_deg, arc_half_width_deg}，1=一月（與 evaluate_batch sectors[month-1] 一致）。編譯端以 12 個月弧的聯集規劃 bbox；渲染端依當月（Asia/Taipei）選弧心畫單月扇。
- `omni_semantics`：全向幾何的語義標記，允許值 `panoramic_terrain_ring`（主體＝機位四周地形）／`celestial_envelope`（天體大氣環）；批次 2 的編譯器防呆以此＋legacy_theme 家族判准。

## 批次 4（試點驗收實況，2026-11-06）

- 編譯 bundle（B121.18，weathergrid/weathergrid_coverage_browser.json）：34 spots／50 opportunities。
- 已建 13 個 pilot 題材逐筆驗證：complete=true、errors=[]，SUB/ENV 數量與委託書一致
  （tw-036-P01/P03/P04 SUB 1；P02/ENV-only 天體；tw-002-P01 SUB 294.9–314.9/0.5–1.2 + ENV 15 km；
  tw-003-P01 月別化 SUB/ENV；tw-027-P01 近環 1 km；tw-072-P01 近環 0.3 km＋晨曦 60–120/15 km；
  tw-076-P01 50–130/0–10＋ENV 20 km；tw-076-P02 天體 envelope）。
- 月別化渲染實測（11 月，Asia/Taipei）：tw-003-P01 當月弧 221.9°–276.9°（弧心 249.4°±27.5°，十一月）。
- 誠實 pending（無 entry、僅機位）13 個題材全部確認未建扇：tw-001-P01/P03、tw-002-P02/P03、
  tw-003-P02/P03、tw-004-P01/P04、tw-019-P01（P02/P03/P05/P06 同前未動）、tw-027-P02/P03、
  tw-072-P02、us-015-P01（P02 同）。
- 測試：python test_weathergrid_coverage 13 OK（含 tw-002/tw-003/001/027/072/076 幾何釘值＋
  renderable 展開測試）；node --test（--test-isolation=none，hermes node-26）464/464 PASS、0 fail。
- postmerge exact 釘值依實測重錨：w4-node 459→464、exact 總數 900→905（ops/v2/postmerge_verify.py）。
- pristine origin/main 已知既有失敗：test_weathergrid_refresh_workflow 2 項釘值漂移（與本票無關，
  未動該 workflow）。
