# ChaseLights V2 — Task R Release Readiness

結論：**NOT READY（正式攝影預報上線）**。已存在且曾部署的 Research-only Preview 不等於正式預報產品。此 PR 為 W5 修復與驗證工具，不授權 merge 或 deployment。

Reviewed main：`f8a1f83bfeda5dc75f7e00c847e7728a0cef79ec`。分支：`codex/w5-task-r-release-readiness-20261014`。Draft PR URL、最終 Head SHA 與 Task R GitHub CI 在發布後由 PR description 與交付版同名報告記錄；本檔不將尚未取得的結果寫成 PASS。

## 真實架構與隔離

- Legacy：`main` repository root，`index.html` / `assets/app.js` 及原有 forecast JSON。`CNAME=chaselights.app`。
- GitHub 動態 `pages build and deployment` 工作流程，非本 repo 中的部署 YAML。即時 [38561249043](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38561249043) completed/success，head=`f8a1f83b…`，branch=`main`。原始 build log 顯示 checkout ref=main，Jekyll source=`.`。因此現有 main push 可能觸發正式 Pages 發布；本次只發布獨立分支。
- V2：同 Hosting 的獨立目錄 `/apps/web-v2/`，URL：https://chaselights.app/apps/web-v2/。入口 `apps/web-v2/index.html`，瀏覽器 ES modules，單頁研究瀏覽器，沒有 SPA history fallback 或 live API/backend。相對 CSS/JS/JSON 均在該目錄。
- 現行 GitHub Pages 是整庫 Jekyll/static build，沒有 V2 npm/Vite build。Task R 加入 `python ops/v2/build_static.py --root . --output work/v2-build`，只產出 `public/apps/web-v2/` 七個真實 runtime files，獨立 `build-manifest.json` 記錄實際 commit 與 SHA256。不包含 Legacy、tests、research audits 或其他 canonical candidates。
- 公開 `catalog.v2.json` 為真實 W2 `tw-026-P01` Research-only projection，只有 1 個機會，`research_only=true` / `forecast_available=false` / `selected_date_recommendation_eligible=false` / `evaluations=[]`。其他七個 canonical records 與 research audits 不因建置而加入公開 Catalog。Repo 既有 Pages 可能公開原始檔，這是產品 eligibility 隔離，不是資料機密性隔離。
- 現有 Legacy 三語連結已存在，Task R 沒有改它。沒有新舊自動比較功能。
- 靜態 build 無新增 secret、API、付費服務。`PLAYWRIGHT_MODULE` / `CHROMIUM_EXECUTABLE` 只是测试 tooling selectors。正式 provider/model/backend 環境設定仍未確立，不能假設不需設定。
- Hosting source 已由真實 Pages job log 證明；Pages settings 與 GitHub Environment protection 沒有可用直接讀取入口。branch protection API 真實 **403 Resource not accessible by integration**，停止該受阻操作，未更換憑證或擴權。`rulesets=[]` 不證明可發布。

## W5 修復

1. 舊 `simulate_merges.py` 硬編碼 #450～#460 的歷史 13 步，遇到已在 main 的 owner pin 必然失敗。改為 `--base-sha` / `--candidate-sha` 的真實 `git merge-tree --write-tree`；檢查完整 SHA、W5 路徑、衝突、owner ancestry/tree、所有非 W5 檔案保留。無 fetch、ref update、merge commit、push 或 deploy。
2. 獨立 static build 驗證 committed bytes、W1～W4 source pins、W2 provenance、Research-only flags、HTML/JS/JSON dependency completeness、輸出目錄與七檔 allowlist；缺資料、髒 runtime、未打包相依或非研究 Catalog 直接 FAIL。
3. 新 `deployment_plan.json` 明確區分現有 Pages auto publish 與本次 `deployment_enabled_by_this_plan=false`，保留待驗 Hosting/environment/approval，不假設 protection 完成。
4. 新 `release_readiness.py` 產出 27 項 JSON / Markdown 驗收清單，逐項指定 owner 和 evidence domain。local、GitHub、public、browser、provider、human review 不互換；缺證據為 UNVERIFIED，必要失敗或阻塞為 NOT READY。GitHub evidence 必須有 head/checkout/merge-parent linkage 與實際 test counts。caller-supplied snapshot 僅 advisory，任何狀態都 `deployment_allowed=false`。
5. 12 個 W5 regression tests 覆蓋缺證據、錯 SHA、CI 全綠但人類 gate 未滿、失敗/SKIP、重複清單、owner/Legacy 越界、真實 Git merge conflict、已整合 pin、dirty build、錯資源、輸出覆寫及 CI bypass。原 **157 個測試全部保留**；新增後總數 **169**，不能降低或忽略。
6. W5 權責由 AGENTS.md 明確允許 `.github/workflows/`。`v2-integration.yml` 維持原有真正 proposed merge checkout，加 12 項及 PyYAML；新 `v2-release-readiness.yml` 僅 PR validation、contents:read、明確 checkout PR head、build/merge-tree/artifact。沒有 deploy action、pages:write、environment、push/schedule trigger 或忽略失敗。

## 原始碼與 PR 相依

即時完整 open PR 清單只有 #420、#482、#483、#484、#485；各 HEAD、merge 狀態與 check runs 保存在 `TASK_R_GITHUB_SNAPSHOT.json`。歷史 closed/merged 狀態同檔，未以舊報告推定。

| PR | 最新狀態與意義 |
|---|---|
| #482 `b429019a…` | Open / non-Draft；真實 NOAA probe 與原 157 CI success。須独立 review；只證明 Seattle raw transport，不能授權攝影分數或 TW/JP coverage。 |
| #483 `543169a5…` | Open / Draft；offline dry-run 與 integration success，尚未進 main。六個檔案不與 Task R 重疊；不重複帶入 inventory/offline gate。release_readiness 是產品驗收清單，不能取代或解除其 policy limitations。 |
| #484 `412908e4…` | Open / Draft；publication validation 文件、CI success。非正式產品必要功能。 |
| #485 `b52495c0…` | Open / Draft；automation research 文件、CI success。原生 timer 未驗收，不是網站上線 prerequisite。 |
| #420 `6fb9ff59…` | Open、mergeable=false；candidate-weather / adapter-test failure，其他 checks success。Legacy navigation 範圍，不是本 V2 pilot 的必要相依；不可為 Task R 合併或修改。 |

已核對 W1～W5 main 成果：#428 schema；#450/#457 W1；#440/#444/#456/#458 W2；#435/#441/#447/#459 W3；#454/#460 W4；#437/#445/#449/#451/#452/#455/#461 W5；#463/#464 已發布 Preview 與連結；#466 evidence follow-up；#468/#469 五筆 Batch04；#473/#477 solar；#478/#481 NWS。#479、#476 本身 **closed/unmerged**，但其固定 source SHA 已由相應 integration 進 main，`verify_main` 另核對實際 ancestry/tree；不可寫成它們 PR 已 merged。#448 等舊 W4 branches 為 closed/unmerged，被 main-based #454 取代。

不存在必须全部合併這五個 open PR 的發布順序。建議 #482 review 先確認真實來源，再走 #467 的 W1 contract → W2 一個 pilot evidence/AUTO approval → W3 runtime → W4 UI → W5 repin/full CI。#483 是獨立治理工具，可分開 review；#484/#485 是文件，#420 是 Legacy 維護。

## Database / Evaluator / Website 驗收

- W2 owner SHA：`509a7c206413a4f8d13350ddb50c2a7ad075ca4a`；P01 canonical content SHA：`2177bd8c8b6c18e0a4b284e50b55d0ff12697ddd`。W3 fixture / W4 fixtures / catalog 均保持 byte/blob/SHA256 同一來源，未假裝「最新 owner commit」必須改變未變動的 P01 bytes。
- CameraContext、PhotographyTarget、ObservationRelation、NavigationTarget 分離；普通自由取景不強制精準 tripod GPS，特定 alignment/geometry claims 才需要。三筆 Batch03及五筆 Batch04仍 R1 / evidence_review；導航待查、無偽造 GPS 或 Directions。
- W3 owner SHA：`8e6f5a1555294ff293a6d7b746b864924f96cfc1`。P01 真實 W2 contracts 未核准 AUTO、threshold/model binding null。deterministic fixtures 是測試；solar 是 WINDOW、NWS 是 RAW_ONLY/UNVALIDATED，兩者都不是 FAVORABLE。UNKNOWN / NOT_EVALUABLE 與 access warning-only tests 全部保留。
- W4 owner SHA：`ec5dc9609596135ba1b2634dfa7d6c07a54fabdc`、tree=`8427cb75fdb433a58d3a4941769a6c06f6f5dc3b`。31 Node cases；6 locale×device Chromium cases。手機為 viewport/touch emulation，不宣稱實體 iPhone/Safari 驗證。
- 已有 no-data/error defensive behavior，但自動 fetch 尚無可識別的獨立 loading 狀態。正式 runtime UI 尚未整合；這是 W4 handoff，不能在 W5 修改 UI。
- 三語 presence/display/keyboard/ARIA 可機器測，human semantic parity 仍 PENDING，不以 key presence 宣稱等價。

## 實際測試與限制

本機固定 reviewed-main baseline：**151 PASS / 6 FAIL / 0 ERROR / 0 SKIP**（157 cases）；六個 browser cases 全部在 before hook 失敗。独立診斷 loopback `listen(127.0.0.1)` 返回 **EPERM**，不是 browser assertion 成功。public HTTP gate 另返回 `URLError … Operation not permitted`；Git fetch 是 proxy:8080 connection failure。保留 logs，不重試繞路或放寬網路。

Task R 初次工具測試：**12 PASS / 0 FAIL / 0 ERROR / 0 SKIP**；static config PASS；七檔独立 build PASS；compile/diff checks PASS。後續 exact candidate 測試、Merge Rehearsal 及新 GitHub CI 必須另外記錄。GitHub 已有 #482～#485 success 並不代替 Task R 自己的 CI，也不代替本機公開網站驗證。

public/Hosting：即時 Pages job success 已確認；本回合本機 live HTTP/Chromium 未成功。GitHub CI local browser 和公開資源 probe 是各自的執行證據；未做 Task R production deployment，所以沒有 Task R post-deploy PASS。

## W1～W4 具體 Handoff

| Owner / 位置 | 重現 / 問題 | 預期與驗收 |
|---|---|---|
| W1 `specs/v2/`、#467 | solar result WINDOW + NWS RAW_ONLY，尚無正式 pilot provider/run/licensing/AUTO production interface；讀兩 spec 與 result flags。 | 審核一個 pilot 的 provider coverage/freshness/time/units/license/threshold/model binding，補正式 contract 與正負 tests；未核准時仍 UNKNOWN，不添加攝影位置 requirement。 |
| W2 `data/v2/reviews/` / `audits/`、#465 | P01/P02/016 lawful-area/evidence 與 human zh-TW/en/ja signoff PENDING；Batch04 human_geo/semantics PENDING。 | 真實 claim-by-claim review 記錄 reviewer/date/source/feedback；一個 pilot 的存在證據與環境條件 threshold 另核准；保留 access warning / needs_review，不猜 GPS、不把 access 變分數 gate。 |
| W3 `packages/core-v2/`、#467 | `tw-026-P01` 所有非 AUTO/provisional/null binding → NOT_EVALUABLE；raw NOAA source update ≠ model run issue，TW/JP無該來源 coverage。 | 真實 time-matched provider、approved AUTO與 valid thresholds 才評估；缺資料/過期/錯區/未校準均 fail closed；同氣象下 open/closed access score相同；不能從 Seattle probe 推定全球可用。 |
| W4 `apps/web-v2/app.mjs:168`、#467 | `fetch('./catalog.v2.json')` pending 時沿用 no-data，沒有 loading 狀態；現有 UI 未接 solar/weather runtime。 | delayed fetch、404、500、invalid JSON、empty catalog、三語×desktop/mobile 各驗收 loading/error/empty；整合 pilot WINDOW 與 raw weather的限制，無未核准 FAVORABLE/Directions，提供新的 owner SHA供 W5 repin。 |

## 安全發布六階段

1. **Build**：固定 release SHA，用新 build tool 產出僅 V2；保存 SHA256 manifest 與上一個健康 V2 source SHA。它目前只能 build Research Preview。
2. **Pre-release Validation**：owner data/spec/tree、169+ strict tests、updated runtime tests、true live provider、trilingual human semantics、六 Browser cases、merge rehearsal、真實 GitHub run/head/checkout SHA、公開健康檢查全部分開驗收。任何必要 failure/unverified 保留阻塞。
3. **Release Approval**：owner明確核准具體 source SHA、產品範圍（Preview vs live forecast）、Hosting source strategy、人工 protection、rollback SHA、時段。403未解決前由 owner 在 GitHub Settings 自行確認，不能要求擴 App 權限來繞過。
4. **Deployment**：**本次不執行**。優先保留現有 Hosting 的独立 `/apps/web-v2/`。因 Pages 現為 main/root自動發布，任何未來 main merge 本身可能就是部署，須先 review 此行為。若要求嚴格人工發布，另一次經 owner 核准的 Hosting migration 必須保留 Legacy 全部資產並用已有 Hosting；不可把 V2-only artifact 替換整個 Legacy Pages artifact。
5. **Post-deployment Verification**：準備 `python ops/v2/integration_gate.py --root . --public` 與 `REQUIRE_PUBLIC_V1_LINK=true node ops/v2/public_browser_smoke.mjs`，檢查 V1連結、V2 HTML/CSS/JS/JSON 200、預期 source/catalog hashes、三語×device與無假 live verdict。本次只準備、未對正式網站執行變更；現有 public smoke 不足以證明新 release bytes，需比對本次 manifest。
6. **Rollback**：另行核准後只恢復 V2目錄到上一個已記錄健康 SHA；禁止 revert整個 main/無關 weather data；Legacy 原樣在線。保留前次 artifact/manifest並重新 public smoke。新 build tool 不刪除舊 artifact。

## 正式發布仍需完成

**必要阻塞**：#465 人類證據/三語評核；#467 reviewed pilot AUTO與真實 provider→runtime→UI；W4 loading/錯誤/無資料驗收；Hosting branch/environment protections及人工發布批准未驗；最新 candidate GitHub CI與當次 public source identity。GitHub CI全綠不能清除上述 gate。

**下一個最小可執行任務**：W2 對一個 `tw-026-P01` pilot 完成存在證據與三語語意的真實 review（#465），並明確將未核准 formation/AUTO thresholds 留待 W1/W3契約；只修改 W2範圍，獨立 PR，不部署。先把一個 pilot 驗收做實，再擴大 runtime。
