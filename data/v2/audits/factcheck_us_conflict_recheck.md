# CL-DATA-22 — us-025–048 四筆 CONFLICT web 複驗（修正第二波）

日期：2026-11-06（台北標準時間）｜執行者：chaselights_rd
範圍：us-031 / us-032 / us-033 / us-041 每筆對權威源（NPS/USGS/維基/官方目的地指南）重新複驗後裁定。
結果：**4/4 維持原值不修正**——三筆 CONFLICT 經權威源覆核後不成立，一筆（us-032）標的檔已
於 2026-10-31 依 owner 指示自 catalog 移除，無修正面。海拔四筆皆不影響 LCL（本批無
cloud_sea／LCL 條件，opportunity altitude_m 均 null 誠實未知）。

## 逐筆裁定

1. `us-031` Sprague Lake・Continental Divide（CONFLICT：repo 海拔 2648m vs「Bear Lake 約 2890m」）
   - **維持 2648 m，不修正。** 維基百科 Sprague Lake (Colorado) 條目明載 Surface elevation
     2,648 m (8,688 ft)，座標 40°19′12″N 105°36′17″W（40.3200, −105.6047），與 repo
     (40.320586, −105.604813) 一致（<60 m）。CONFLICT 比對對象是**另一座湖**（Bear Lake
     約 2,890 m 位於 Sprague Lake 上方道路終點，為不同地物）；us-031 名稱與座標均錨定
     Sprague Lake（NPS Sprague Lake Scenic View/Photo Spot）。
   - 來源：en.wikipedia.org/wiki/Sprague_Lake_(Colorado)；mapcarta.com/23510212；
     nps.gov/places/sprague-lake.htm。複驗日 2026-11-06。
   - LCL 影響：無（無 LCL/cloud_sea 條件）。

2. `us-032` New Orleans French Quarter（CONFLICT：repo elev 9m vs 0.3–0.9m，語義需確認）
   - **無修正面。** source-lock.json 刪除紀錄：us-032-P01 已於 commit cdc290df9426
     （2026-10-31）依 owner 指示移除（evidence-D 證據不足），opportunities/ 無此檔，
     evaluations bundle 不含此 place——不存在任何顯示/評估面可被此值影響。
   - 語義覆核（供後續任何重引入引入參考）：攝影測點語義（測點海拔）下，French Quarter
     地面海拔為 1 ft（0.3 m）〔維基 Geography 段 infobox〕，Katrina 關聯文句引 5 ft
     （1.5 m）高地值——正確值域 0.3–1.5 m；repo parity 檔中 9.0 m 為 legacy 匯入值
     （legacy-derived），不採。如日後重引入，應以 0.3–1.5 m（測點語義）入檔並附本報告。
   - 來源：en.wikipedia.org/wiki/French_Quarter。複驗日 2026-11-06。

3. `us-033` Denver Skyline（CONFLICT：座標偏 3.5km，建議改 Civic Center 39.7394,−104.9889）
   - **維持 City Park 點位，不採納 Civic Center 建議。** 複驗顯示「丹佛天際線」權威拍攝
     位即 City Park——VISIT DENVER 官方攝影指南指定 City Park 為 skyline＋Front Range
     山景全景點；Westword（5 Places to Get a Great View of Denver's Skyline）與
     photographylife.com（Denver Skyline photo spot, GPS 39.747463, −104.943573）均指向
     Denver Museum of Nature & Science 西側台階、俯瞰 Ferril Lake 對準 downtown+山景。
     建議的 Civic Center 座標是 Civic Center Park（面向州議會大廈/市政建築群，為另一
     地物；en.wikipedia.org/wiki/Denver_Civic_Center），非本題材權威觀景位。
   - repo 點 (39.7461222, −104.9490116) 落在 City Park／Ferril Lake 錨點，距 DMNS 台階
     實拍位約 0.5 km、同一氣象網格，座標來源（Visit Denver City Park subject +
     USGS/GeoNames Ferril Lake anchor）與題材語義一致。無 3.5 km 錯置成立。
   - 來源：visitdenver.com 攝影指南條目；westword.com/news/5-places-to-get-a-great-view-
     of-denvers-skyline-20957340；photographylife.com/photo-spots/denver-skyline。
     複驗日 2026-11-06。
   - --only-place-id 重生成：不適用（無值變更）。

4. `us-041` Mountain Vista・Denali（CONFLICT：座標偏 1km、elev 差 26m，建議 63.733,−148.918/537m「Murie 中心」）
   - **維持原值，不修正。** NPS Mountain Vista 頁（nps.gov/places/dena-mountain-vista.htm）
     僅定位「Mile 13, Denali Park Road」，未發布座標；既有查證批次
     `factcheck_ak.md`（2026-11-06）已以 NPS mile-13 rest stop 核對 repo
     (63.73209, −148.90273) 為通過。複驗中收集的社群座標互相發散 >17 km
     （nationalparkphotographer 63.7365,−148.908；OSM/nationalparksatlas 與 parkwolf 標在
     63.715,−149.255 即 mile-15 公路終點/Savage River 一帶），無一具 NPS/USGS 權威位階
     可據以改座標。建議點 (63.733, −148.918) 所指「Murie 中心」無法對上任何權威地物
     （Murie Science & Learning Center 位於公園入口區），建議源不成立。
   - 海拔：repo 511 m（legacy-derived 記錄）vs 建議 537 m——無權威高程源可裁定；評估
     管線實際海拔取 Open-Meteo 於查詢點的 grid elevation，座標不變即不變。
   - 來源：nps.gov/places/dena-mountain-vista.htm；data/v2/audits/factcheck_ak.md §OK#3。
     複驗日 2026-11-06。

## 釘值同步 / 測試實況

- 本波零資料檔變更 → source-lock / bundle digests / task-x fixtures / research-index
  釘值無須重錨；`--only-place-id` 重生成不適用（無座標/海拔變更，評估束不動）。
- node --test --test-isolation=none apps/web-v2/tests/*.test.mjs：**483 pass / 0 fail**
  （exit 0，node v26.7.0）。
- python -m unittest data.v2.tests.test_migration_skeletons data.v2.tests.test_task_x_research_index：
  **27 tests OK**（exit 0）。
- 排程 CI：無需（無生成物變更）。
