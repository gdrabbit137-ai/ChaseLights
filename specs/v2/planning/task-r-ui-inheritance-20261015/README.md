# ChaseLights V2 — Work Task R：V1 功能繼承與 W4 開發規劃

日期：2026-10-15 UTC（使用者提交日為 Anchorage 2026-10-14）。Owner：W1 規劃文件；非網站實作。狀態：Draft proposal。查核基準 main `5bfad32f31007450496ce10123318ac3e8e37aad`；Task U 程式基準 `8bd2256c01aa12ca663b13bc6960272e1c48c830`。

Task U **已完成**40項功能與30項歷史問題盤點。本次不重建Database、不重做全量歷史研究；已取得原交付六份主檔，以摘要、完整machine matrix、Roadmap與產品／Task01關聯段落核對，逐項沿用U-F01–40/H01–30並更新最新程式、Issue及後續PR差異。XLSX保留為原交付，未重新分析或製作。原ZIP SHA256：`e47c50ff2ee148526ee133e5f45f27327235241058600b0cc5f0fed5a739efcc`。原Task U的測試與本次重跑在EVIDENCE分列，未驗項目不升級為完成。

## 交付導航

| 交付 | 文件 |
| --- | --- |
| 完整40項功能對照、P0/P1/P2、Owner、缺口與逐項驗收 | [FEATURE_MATRIX.md](FEATURE_MATRIX.md) |
| 全部30項歷史問題、V1/main/Draft修復狀態 | [HISTORY.md](HISTORY.md) |
| API／Database／Evaluator契約與W1–W5相依 | [CONTRACTS_AND_DEPENDENCIES.md](CONTRACTS_AND_DEPENDENCIES.md) |
| 可執行W4任務、前置輸入、範圍、測試與停止條件 | [W4_TASKS.md](W4_TASKS.md) |
| 階段Roadmap、平行工作及可測試Gate | [ROADMAP.md](ROADMAP.md) |
| 固定來源、實際CI／本機結果、Task U沿用範圍 | [EVIDENCE.md](EVIDENCE.md) |

## 本次決策

1. V2最終產品必須是完整攝影規劃網站：探索→選日期→理解條件／時段→查看位置／警告→實拍回饋。Research-only探索是第一階段，不是最終驗收。
2. main網站程式與Task U相同；#487主畫面已實作、#488曾267項全綠，兩者仍Draft。先獨立驗收既有成果，不重寫U-W4-01。#489共用契約與#490索引也是Draft，不能假設在main。
3. #490可接7景點／8題材、三語名稱與taxonomy，但regions=0、verified timezone=0。名稱／題材探索可以先做；完整地區／日期功能必須補真實metadata。畫面缺資料不造國別、IANA、即時預報或分數。
4. main已合併#491/#492的R1 A/B/C比例審查政策。R1研究公開不再全面等待人類簽核；逐筆獨立source/crosswalk/三語語意檢查，C隔離。保留既有human PENDING；正式guide／live／法律或地理爭議仍走各自Gate。
5. W4只呈現W2與W3真實版本化契約；W3 WINDOW／NWS RAW_ONLY不等於可推薦。封閉為警告及導航限制，不改攝影條件分數；普通題材預設自由構圖。

## 優先前三個新增W4任務

| 順序 | 任務 | 為何優先／進入條件 |
| --- | --- | --- |
| 1 | R-W4-02 多景點、名稱搜尋與題材探索 | 將已存在7景點／8題材實際接到產品。先接受#487＋#489＋#490來源與sidecar transport，按A/B/C逐筆准入；不等完整行政資料，也不造預報。 |
| 2 | R-W4-03 收藏、偏好與可用排序 | 延續V1高使用價值；可與W2行政／時區補證平行。只啟用可信NAME/REGION，SCORE/DISTANCE保持明確停用。 |
| 3 | R-W4-04 地區多選與目的地日期 | 恢復正式規劃的核心控制；W2先交TW22/JP47/US51＋Place membership＋IANA來源，W3交local-day resolver。控件可先測，資料Gate未滿不稱功能就緒。 |

共同前置R-W5-00是整合已完成PR，不是再開發首頁。W1/W2/W3真實pilot工作自M1起平行啟動，避免完成研究探索後才發現沒有預報契約。

本次只新增此目錄下的規劃文件；無正式網站、Canonical、Evaluator、workflow、排程修改，無合併／部署。與既有W5 #486的「Task R Release Readiness」**不同任務**，不覆寫其檔案或聲稱它已合併。本文不新增Schema，不授權其他Worker立即開發或發布。
