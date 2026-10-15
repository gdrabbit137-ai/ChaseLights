# Task R 查核來源、測試與限制

固定main `5bfad32f31007450496ce10123318ac3e8e37aad`。GitHub PR/Issue/Actions於2026-10-15 UTC讀回；本文件只證明該snapshot。原始Task U之歷史盤點與本次查核分列，不把舊測試冒稱重跑。clone/review使用既有repo來源；沒有public browser、實體手機、全球當前provider或新功能實作驗收。

## Task U沿用與範圍

實際取得並讀取 `ChaseLights_Task_U_UI_UX_Research_and_Roadmap(1).zip`，533145 bytes；SHA256 `e47c50ff2ee148526ee133e5f45f27327235241058600b0cc5f0fed5a739efcc`。六份主檔為inventory/history/product spec/xlsx matrix/roadmap/task01；XLSX此處不重做、不修改，40功能／30歷史以原交付machine matrix逐項轉成可審查Markdown；本次新結論以程式／GitHub與右欄更新為準。

| 原始成員 | bytes | SHA256 |
| --- | --- | --- |
| README.md | 3410 | d9af843e3b5dc93f1147cfee67f687ca464203d59d2e42f57a874c59f92e49a0 |
| V1_V2_FEATURE_INVENTORY.md | 79787 | ab155a0e8ae24dfda3a28696a62961e8440d99bed1d1c0aca8eecfb627a85e4c |
| V1_HISTORICAL_UX_ISSUES.md | 41843 | b4e3d4540c9e9b1f75c456ece9e808a82d8e862da2f39aa879b3799cca856923 |
| V2_UI_UX_PRODUCT_SPEC.md | 27591 | 13c7b669730a42c893d4beed9fd6635ff849931bed00043ad66e683885e0a009 |
| V2_W4_CODEX_ROADMAP.md | 19473 | dd23db8f525572fdfc062020bafe1cca40315137c0786f54b21628b5699d57a9 |
| V2_W4_TASK_01.md | 20103 | 4df60d7a559566a5f6f5d269529aafe6b87a9fc73d0e6c385e444a81cd0810bf |
| evidence/matrix-data.json | 60224 | 7b12f44a2223b59af8ed6e3aada071dfce8cff650bd23a5053351bf0cd428af2 |


Task U code baseline `8bd2256c01aa12ca663b13bc6960272e1c48c830`，交付最後main `77ecfb8066d2cb737327138fa51b2e21678b9c85`。本次比對其46個固定來源：44個對應路徑bytes仍相同，S23 integration-sources更新、S24原本是#486 Draft且不在main；不可把它當已merge。另比較整個V1 assets/index/regions/fetch/runtime與apps/web-v2、packages、適用spec，差異只有main新增#491政策與W5 source pins；完整UI未漂移。因此沿用Task U已查證的CODE事實，沒有重新研究全部486筆舊GitHub項目。

## 後續PR即時狀態

| PR | 實際HEAD | 狀態 | Actions讀回 |
| --- | --- | --- | --- |
| [#487](https://github.com/gdrabbit137-ai/ChaseLights/pull/487) | f0da51f30252328f82babba7d90dd17f1559c68e | open／Draft=True／merged=False | [V2 Integration failure](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38633947630)；[V2 Public Research Preview Smoke success](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38633947668) |
| [#488](https://github.com/gdrabbit137-ai/ChaseLights/pull/488) | bfd7afa14e6c416518592bf48d3dcbd5677d60d7 | open／Draft=True／merged=False | [V2 Release Readiness Tools success](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38638478711)；[V2 Public Research Preview Smoke success](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38638479163)；[V2 Integration success](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38638478808) |
| [#489](https://github.com/gdrabbit137-ai/ChaseLights/pull/489) | 38b234ba5f4df4a751eaea14dcc79036b45ed180 | open／Draft=True／merged=False | [ChaseLights V2 Schema Contract success](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38654783994)；[V2 Integration failure](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38654784007) |
| [#490](https://github.com/gdrabbit137-ai/ChaseLights/pull/490) | c10976eb5e88fd32ec0adc58a1317ed70015821d | open／Draft=True／merged=False | [V2 Integration failure](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38656336472) |
| [#493](https://github.com/gdrabbit137-ai/ChaseLights/pull/493) | b8570555c5cb1080b9a18059addadab427ba8c52 | open／Draft=True／merged=False | [V2 Integration failure](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38699861755) |
| [#494](https://github.com/gdrabbit137-ai/ChaseLights/pull/494) | 577f4c31b302c4fd603222bef6dce419e36ea3a0 | open／Draft=True／merged=False | [V2 Integration success](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38700042249) |


#491 HEAD `9710d77dae3338123e4d93a47c720c2f4f929a4e`、#492 HEAD `ff944a781741606dc0d34c15374edd1aee057847`已合併（GitHub搜尋＋本機main差異確認）。#493描述內有舊HEAD `03b54a36...`，本次採metadata實際HEAD `b8570555...`，不採舊body當pin。#494成功的synthetic測試tree `2cde1c0ce1aa72aabed7f8e831933a37bdce6d80`；#488成功的synthetic tree `5b4dfd2f5f8cb7b86be3f155f96d0caa459ae2a4`，均與PR head及main分開記錄。

失敗已實際讀job logs，不只是猜測：#487=w4 subtree、#489=w1 subtree、#490/#493=w2 subtree differs from tested pin。這些是Owner來源尚未被W5接受，不能刪掉gate或當產品測試全數失敗。#488 log最後counts=267/267 PASS、0 FAIL/ERROR/SKIP；#494 log=157/157、0 FAIL/ERROR/SKIP。#488 source-browser75＋package-browser6、W4 Node43，並非本次重跑。

| job ID | 原始最後結果摘錄 |
| --- | --- |
| 116092247169 | 2026-10-14T20:42:42.5856150Z {"status": "FAIL", "head": null, "counts": null, "error": "ValueError: Merged w4 subtree differs from tested pin: apps/web-v2"} |
| 116161847978 | 2026-10-14T23:33:46.7266433Z {"status": "FAIL", "head": null, "counts": null, "error": "ValueError: Merged w1 subtree differs from tested pin: specs/v2"} |
| 116166889950 | 2026-10-14T23:49:15.5620862Z {"status": "FAIL", "head": null, "counts": null, "error": "ValueError: Merged w2 subtree differs from tested pin: data/v2"} |
| 116305150736 | 2026-10-15T07:37:04.1692847Z {"status": "FAIL", "head": null, "counts": null, "error": "ValueError: Merged w2 subtree differs from tested pin: data/v2"} |
| 116305755061 | 2026-10-15T07:38:36.2726906Z {"status": "PASS", "head": "2cde1c0ce1aa72aabed7f8e831933a37bdce6d80", "counts": {"tests": 157, "pass": 157, "fail": 0, "error": 0, "skip": 0}, "error": null} |
| 116107637061 | 2026-10-14T21:14:35.1886798Z {"status": "PASS", "head": "5b4dfd2f5f8cb7b86be3f155f96d0caa459ae2a4", "counts": {"tests": 267, "pass": 267, "fail": 0, "error": 0, "skip": 0}, "error": null} |


main `5bfad32f31007450496ce10123318ac3e8e37aad`僅讀到Pages與watchdog success，未找到該exact SHA的V2 Integration run；不能把#494 PR成功叫做此main的157 PASS。

## 本次實際本機重跑（在固定main相同程式bytes）

| 命令／範圍 | 實際結果 | 解讀 |
| --- | --- | --- |
| `node --test apps/web-v2/tests/*.test.mjs` | 31 PASS／0 FAIL／0 SKIP，exit0 | main現有研究UI防線；非#487新UI、browser或live驗收。 |
| `python3 -m unittest discover -s specs/v2/tests -p 'test_*.py' -v` | 36 PASS／0 FAIL／0 ERROR／0 SKIP，exit0 | main既有W1 cases，非#489候選67。 |
| `python3 -m unittest test_place_discovery_sorting_static test_mobile_admin_picker_static test_field_intake_static test_weathergrid_wind_vectors` | 34 PASS／0 FAIL／0 ERROR／0 SKIP，exit0 | V1定向靜態回歸，不代表全部Task U113案例或browser重跑。 |
| 六個既有推薦函式回歸（見下） | 6 PASS／0 FAIL／0 ERROR／0 SKIP | #423決策防線；非#388原日端到端。 |
| strict localization audit（重定向REPORT_PATH到scratch，未修改Legacy） | `ok=false`、2899 historical debt fields、new/modified debt=[]、propagation errors=[] | 確認舊語意欠帳仍存在；不是2899景點，也不是本次引入失敗。 |
| `python3 -m unittest test_navigation_contract` | 3 methods；1 method內3 failed subtests（jp-021/022/025），0 ERROR/SKIP，exit1 | 既有失敗重現，未改資料／GPS／test期望；不能誤報0 FAIL或算成3個失敗methods。 |
| 本次browser／full integration／provider/public | 未執行 | 規劃文件無runtime變更；引用#488/#494實際Actions但不冒稱本次執行。 |

六函式：`test_recommendation_is_condition_driven_not_score_driven`、`test_recommendation_required_condition_failure_overrides_high_score`、`test_recommendation_material_uncertainty_is_candidate`、`test_recommendation_missing_contract_is_unavailable`、`test_dingshizhuo_sunset_requires_visibility_not_only_sunset_geometry`、`test_daily_winner_gate_requires_runtime_recommendation_eligibility`（`test_opportunity_adapter.py`）。

原始Task U的113 methods／1 method三失敗subtests、6推薦、31 Node、2899欠帳、browser環境失敗及#486169歷史CI僅作舊證據。本次選定重跑如上，沒有宣稱重跑其全部測試或重新核對其全部歷史GitHub敘述。

## 本次GitHub歷史追蹤讀回

| 項目 | 狀態 | 判定 |
| --- | --- | --- |
| [#379](https://github.com/gdrabbit137-ai/ChaseLights/issues/379) | open | Governed localization parity: require semantic-equivalent Opportunity content in zh-TW/en/ja |
| [#388](https://github.com/gdrabbit137-ai/ChaseLights/issues/388) | open | runtime: enforce #381 semantic consistency for dedicated Opportunity matches |
| [#423](https://github.com/gdrabbit137-ai/ChaseLights/issues/423) | closed | fix: enforce selected-date recommendation consistency |
| [#465](https://github.com/gdrabbit137-ai/ChaseLights/issues/465) | open | V2 W2 R1 human evidence, lawful-camera-area and zh-TW/en/ja semantic signoff |
| [#467](https://github.com/gdrabbit137-ai/ChaseLights/issues/467) | open | V2 next runtime milestone — verifiable sun-window and real weather-provider contracts (no premature scores) |
| [#471](https://github.com/gdrabbit137-ai/ChaseLights/issues/471) | open | W4 V2 Research Preview: publish all 8 source-pinned R1 opportunities, 7 places |
| [#474](https://github.com/gdrabbit137-ai/ChaseLights/issues/474) | open | W2 Batch04 five R1 Places: real human photo-evidence, access and three-language signoff |


另外實際讀取#489三份contract/handoff、#490 index-status/handoff、#487 HTML diff、#488 runner/source metadata與main model/evaluator/solar/NWS adapter；不是僅憑PR title作結論。完整required spec review包括AGENTS、Research/Navigation R4.2、specs/v2 index、architecture/governance、free composition、camera policy、access advisory、readiness/worker contract、M6a/M6b與最新比例審查。

## 固定程式／規格證據索引

| ID | Task U來源用途 | 本次固定連結 | 本次同一性 |
| --- | --- | --- | --- |
| S01 | 貢獻與路徑所有權 | [AGENTS.md](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/AGENTS.md) | bytes與Task U來源相同 |
| S02 | V1 首頁控制與入口 | [index.html](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/index.html) | bytes與Task U來源相同 |
| S03 | V1 卡片、篩選、日期與推薦呈現 | [assets/app.js](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/assets/app.js) | bytes與Task U來源相同 |
| S04 | V1 響應式版面 | [assets/app.css](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/assets/app.css) | bytes與Task U來源相同 |
| S05 | V1 地區與導航資料 | [regions.py](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/regions.py) | bytes與Task U來源相同 |
| S06 | V1 時間、題材與評分程式 | [fetch_data.py](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/fetch_data.py) | bytes與Task U來源相同 |
| S07 | V1 每日摘要與時間段 | [analyze_weather.py](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/analyze_weather.py) | bytes與Task U來源相同 |
| S08 | V1 條件契約與推薦決策 | [opportunity_runtime.py](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/opportunity_runtime.py) | bytes與Task U來源相同 |
| S09 | V1 研究題材 Catalog | [runtime_catalog_v004_r4_2.json](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/runtime_catalog_v004_r4_2.json) | bytes與Task U來源相同 |
| S10 | V1 實拍表單 | [field-intake.html](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/field-intake.html) | bytes與Task U來源相同 |
| S11 | V1 實拍搜尋、EXIF 與匯出 | [assets/field-intake.js](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/assets/field-intake.js) | bytes與Task U來源相同 |
| S12 | WeatherGrid 地圖與風／雲圖呈現 | [assets/weather-map.js](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/assets/weather-map.js) | bytes與Task U來源相同 |
| S13 | 獨立 WeatherGrid V2 全球資料載入器 | [assets/weather-map-v2.js](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/assets/weather-map-v2.js) | bytes與Task U來源相同 |
| S14 | V2 首頁現況 | [apps/web-v2/index.html](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/apps/web-v2/index.html) | bytes與Task U來源相同 |
| S15 | V2 研究畫面與自動載入 | [apps/web-v2/app.mjs](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/apps/web-v2/app.mjs) | bytes與Task U來源相同 |
| S16 | V2 導航與 runtime fail-closed | [apps/web-v2/model.mjs](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/apps/web-v2/model.mjs) | bytes與Task U來源相同 |
| S17 | V2 唯讀 canonical 投影 | [apps/web-v2/v21-adapter.mjs](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/apps/web-v2/v21-adapter.mjs) | bytes與Task U來源相同 |
| S18 | V2 預設單一研究紀錄 | [apps/web-v2/catalog.v2.json](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/apps/web-v2/catalog.v2.json) | bytes與Task U來源相同 |
| S19 | V2 W1 架構與產品契約 | [specs/v2/ARCHITECTURE_SPEC.md](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/specs/v2/ARCHITECTURE_SPEC.md) | bytes與Task U來源相同 |
| S20 | V2 W3 評估器 | [packages/core-v2/evaluator.py](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/packages/core-v2/evaluator.py) | bytes與Task U來源相同 |
| S21 | V2 太陽時間計算 | [packages/models-v2/solar_window.py](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/packages/models-v2/solar_window.py) | bytes與Task U來源相同 |
| S22 | V2 NOAA NWS raw adapter | [packages/core-v2/adapters/nws_gridpoint.py](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/packages/core-v2/adapters/nws_gridpoint.py) | bytes與Task U來源相同 |
| S23 | W5 各 owner 固定來源 | [ops/v2/integration-sources.json](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/ops/v2/integration-sources.json) | main已更新；本次重新讀取 |
| S24 | Task R Release Readiness（未合併 #486） | [ops/v2/reviews/TASK_R_RELEASE_READINESS.md](https://github.com/gdrabbit137-ai/ChaseLights/blob/0837dd555df9d8f647b9042223d5e766d6fd6afc/ops/v2/reviews/TASK_R_RELEASE_READINESS.md) | 原本就是#486 Draft，main不存在；不可當main |
| S25 | R4.2 研究／呈現／語系／實拍規格 | [RESEARCH_EVIDENCE_SPEC_R4_2.md](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/RESEARCH_EVIDENCE_SPEC_R4_2.md) | bytes與Task U來源相同 |
| S26 | R4.2 導航規格 | [NAVIGATION_SPEC_R4_2.md](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/NAVIGATION_SPEC_R4_2.md) | bytes與Task U來源相同 |
| S27 | V2 自由取景規格 | [specs/v2/FREE_COMPOSITION_SPEC.md](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/specs/v2/FREE_COMPOSITION_SPEC.md) | bytes與Task U來源相同 |
| S28 | V2 封閉警告與分數分離規格 | [specs/v2/ACCESS_ADVISORY_SPEC.md](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/specs/v2/ACCESS_ADVISORY_SPEC.md) | bytes與Task U來源相同 |
| S29 | V1 三語內容嚴格稽核程式 | [audit_localization_semantic_parity.py](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/audit_localization_semantic_parity.py) | bytes與Task U來源相同 |
| S30 | V2 Chromium 六情境既有測試 | [apps/web-v2/tests/browser-smoke.mjs](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/apps/web-v2/tests/browser-smoke.mjs) | bytes與Task U來源相同 |
| S31 | V2 W2 fixture 與人工語意簽核狀態 | [apps/web-v2/tests/fixtures/worker2/manifest.json](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/apps/web-v2/tests/fixtures/worker2/manifest.json) | bytes與Task U來源相同 |
| S32 | V1 地區多選與排序回歸 | [test_place_discovery_sorting_static.py](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/test_place_discovery_sorting_static.py) | bytes與Task U來源相同 |
| S33 | V1 手機地區面板回歸 | [test_mobile_admin_picker_static.py](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/test_mobile_admin_picker_static.py) | bytes與Task U來源相同 |
| S34 | V1 導航回歸 | [test_navigation_contract.py](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/test_navigation_contract.py) | bytes與Task U來源相同 |
| S35 | V1 條件／時間／推薦回歸 | [test_opportunity_adapter.py](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/test_opportunity_adapter.py) | bytes與Task U來源相同 |
| S36 | WeatherGrid V2 頁面與語系現況 | [weather-map-v2.html](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/weather-map-v2.html) | bytes與Task U來源相同 |
| S37 | V2 樣式與手機版現況 | [apps/web-v2/styles.css](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/apps/web-v2/styles.css) | bytes與Task U來源相同 |
| S38 | V2 太陽時間契約 | [specs/v2/ASTRONOMY_WINDOW_SPEC_V0_1.md](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/specs/v2/ASTRONOMY_WINDOW_SPEC_V0_1.md) | bytes與Task U來源相同 |
| S39 | V2 NOAA NWS raw source 契約 | [specs/v2/WEATHER_SOURCE_NWS_SPEC_V0_1.md](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/specs/v2/WEATHER_SOURCE_NWS_SPEC_V0_1.md) | bytes與Task U來源相同 |
| S40 | V2 候選機位規則與殘留 access 用詞 | [specs/v2/CAMERA_AREA_COMPOSITION_POLICY.md](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/specs/v2/CAMERA_AREA_COMPOSITION_POLICY.md) | bytes與Task U來源相同 |
| S41 | V1 雲量配色修復說明 | [B161_WEATHERGRID_CLOUD_READABILITY.md](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/B161_WEATHERGRID_CLOUD_READABILITY.md) | bytes與Task U來源相同 |
| S42 | V1 風向密度契約測試 | [test_weathergrid_wind_vectors.py](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/test_weathergrid_wind_vectors.py) | bytes與Task U來源相同 |
| S43 | V1 手機地區面板規格 | [B143_MOBILE_ADMIN_AREA_PICKER.md](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/B143_MOBILE_ADMIN_AREA_PICKER.md) | bytes與Task U來源相同 |
| S44 | V1 地區第一級行政分類 | [B137_ADMIN_LEVEL1_FILTERS.md](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/B137_ADMIN_LEVEL1_FILTERS.md) | bytes與Task U來源相同 |
| S45 | V2 版本化評估結果結構 | [specs/v2/schema/evaluation-result-v0.1.schema.json](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/specs/v2/schema/evaluation-result-v0.1.schema.json) | bytes與Task U來源相同 |
| S46 | V2 Catalog 防禦性載入 | [apps/web-v2/catalog-loader.mjs](https://github.com/gdrabbit137-ai/ChaseLights/blob/5bfad32f31007450496ce10123318ac3e8e37aad/apps/web-v2/catalog-loader.mjs) | bytes與Task U來源相同 |


## 仍未證實

來源照片現場／EXIF真實性、實際合法通行範圍、未支持行政／IANA assignment、各語言人類簽核、dynamic closure導航鏈、現今全球天氣服務、公開候選新版檔案、Safari／實體裝置均未被本次規劃認證。R1 A/B/C仍需真正獨立source／語意檢查，不能由這份計畫自動標PASS。

本目錄全為規劃文件；W1 source tree會改變，current-head integration若報pin mismatch屬待W5接受項，應如實保留，不以docs為由豁免。最終Draft PR的SHA、doc validation、scope isolation與CI讀回於交付時另補。

## 交付前文件驗證

7份Markdown、本地相對連結、表格欄數、40項功能現況＋40項驗收、30項歷史問題與11組契約完整性檢查PASS。新檔全部在本規劃目錄，不修改其他W1規範／schemas、W2/W3/W4/W5或Legacy。`git diff --check` PASS；文件完整性不是新產品功能測試。本次未新增測試程式或降低既有門檻。Draft提交HEAD與其CI另外記錄在PR，避免在commit內自我宣稱測過未來SHA。
