# Task A — W4 真實資料、多語系回歸驗證

本次僅變更 `apps/web-v2/`，在獨立分支接續 #436、#442，沒有合併、部署或修改任何 Worker 分支。研究預覽不代表可用的即時預報。

## 版本與規格

- 分支：`codex/v2-w4-real-data-regression-20261011`。
- PR base（#442 head）：`9fe8816e8e1c4d284cc56ee0435fc62278577fe7`。
- 實際測試的 code commit：`e97eca268ec770b03f14fa46fe6e6da720c29897`。後續提交只保存紀錄與本報告；最終 PR head 見 PR 說明。
- W4 owner branch：`e931981a31d2ade1a94f921edd66f069027ec47c`。
- #436 head：`7cc1ac237f806c737113bc753e1e8d1996b07c43`；#436、#442 均 open / Draft / 未合併。
- 最新 main 規格：`75f3dc64a3eac11145b04612e5ce5e93e750337f`。已閱讀 AGENTS、R4.2 research/navigation、specs/v2 README、Architecture、Governance、Worker Contracts、ADR、migration matrix、Codex runbook 及 canonical schema。遵循 main，不將未合併的選用機位或 runtime 契約當作正式規格。
- W2 source commit：`7f10e9bd2757449d72546155c66714880c6d3ab1`。三筆 canonical 機器資料及 research-only preview 與該 SHA 的 Git blob 逐位元一致，詳見 `source-verification.log`。
- #442 說明中的 `c7c4dfc...` 與實際 catalog 的 `7f10e9bd...` 不一致；此報告以檔案、manifest 與 Git blob 驗證結果為準，未修改 #442 或 W2。

## 本次修改

1. 投影保留資料聲明的完整 source commit SHA，UI 顯示三語系標籤。無 SHA 的匯入顯示未知，不沿用前一資料來源的 SHA。標籤明確為資料聲明，不能據此宣稱任意本機檔案經 GitHub 認證。
2. 將真實 W2 access notes 與 safety notes 一起放入主要限制資訊。CameraContext / Target / ObservationRelation 仍為預設收合的選用細節。
3. 匯入防線擴充到 optional description、camera access/safety、navigation label 與 place name 的三語系完整性；欄位缺少某語系時拒絕匯入，不默默退回中文。
4. 新增真實資料語意投影／缺譯負向 Node 測試；擴充 browser 的來源 SHA、幾何收合、資訊順序、觸控／滑鼠選取測試，沿用已有 skip link／ARIA 修正。

沒有改動 canonical W2 內容、氣象值、GPS、條件門檻、模型或 Legacy。偽造 FAVORABLE 僅存在於既有明確標記的負向測試輸入。

## 實際結果

| 項目 | PASS | FAIL | ERROR | SKIP | 原始紀錄 |
| --- | ---: | ---: | ---: | ---: | --- |
| 完整 Node `*.test.mjs` | 29 | 0 | 0 | 0 | node.log |
| 其他 adapter smoke | 1 | 0 | 0 | 0 | adapter-smoke.log |
| Chromium：desktop/mobile × zh-TW/en/ja | 6 | 0 | 0 | 0 | browser.log |
| 最新 main schema 測試 | 15 | 0 | 0 | 0 | main-schema-tests.log |
| 三筆真實 canonical schema 驗證 | 3 | 0 | 0 | 0 | schema.log |
| 四個 upstream Git blob／bytes 核對 | 4 | 0 | 0 | 0 | source-verification.log |

`node --check`（app、loader、browser test）與 `git diff --check` 通過。Node 修改前基準為 22 PASS，保存於 node-baseline.log。

起初 `/usr/bin/chromium` 不存在，browser runner 原始結果為 0 PASS / 6 FAIL（共用 before hook 的 launch ERROR），保存於 browser-environment-error.log，不能算產品斷言失敗或 PASS。Playwright 官方 Chromium 下載遇到損壞 ZIP，保存於 chromium-install.log。最後使用 npm 取得 `@sparticuz/chromium@153.0.0`，在 scratch 解壓 Chromium，實際完成六個案例。未修改測試以 SKIP 或忽略缺少工具。

Python 起初缺 jsonschema，曾發生環境 ERROR；以 pip 安裝到 scratch 後，使用固定 main SHA 匯出的原始 validator 與 schema 成功重跑。安裝紀錄為 schema-install.log。

## 重跑與環境

詳細版本見 environment.json；本次 Chromium 153.0.8010.0、Node v24.19.0，headless Linux。手機為 390×844 Chromium touch/viewport 模擬，桌機 1440×1000；並非實體手機或 Safari。

```sh
node --test apps/web-v2/tests/*.test.mjs
node --test apps/web-v2/tests/adapter-smoke.mjs
PLAYWRIGHT_MODULE=/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright CHROMIUM_EXECUTABLE=/tmp/chase-w4-browser/extracted/chromium FONTCONFIG_PATH=/tmp/chase-w4-browser/extracted/fonts node --test apps/web-v2/tests/browser-smoke.mjs
```

Browser 測試使用真實固定 W2 資料，自啟 loopback HTTP server，涵蓋自動載入、本機匯入、語系來回切換與保存、可存取名稱、skip link、鍵盤焦點、搜尋／空結果、觸控／滑鼠選取、預設收合與展開、未驗證 GPS 無 Directions、偽造 runtime 無 FAVORABLE、缺譯拒絕、無上傳及無水平溢出。

## W5 驗收與未完成項

可交給 W5 進行整合驗收，不能據此合併或部署。

- 本 PR 堆疊於 #442，再往下為 #436／W4；W5 必須處理依賴順序、並行 Worker 變更與最新 main spec gate。
- 自動測試證明 W2 各語系文字完整保留／切換，不等於人工語意等價或地理研究簽核。W2 manifest 的 human_semantic_signoff 仍 PENDING；既有開放時間、拍攝區域、來源 scope 等問題未被提升為已解決。
- 瀏覽器結果為本機可重現測試；独立 CI、真人螢幕閱讀器、Safari／實體手機與公開網站驗證仍未完成。
- R1 / evidence_review、provisional non-AUTO 條件、null threshold/model binding、未知 geometry 均保持；Research-only 不提供真實 FAVORABLE、可用分數或指定日期預報。
- 未建立 W3 runtime 契約或進行其他 Worker 開發。
