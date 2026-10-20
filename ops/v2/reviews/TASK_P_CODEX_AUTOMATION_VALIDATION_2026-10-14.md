# Task P：Codex 自動化與 W1～W5 協作驗證

驗證日期：2026-10-14（America/Anchorage）。Owner：W5 / integration。
Repository：`gdrabbit137-ai/ChaseLights`。
Reviewed main / branch base：`8a2d9fa14dca4196386c18649c04ead9a851d350`。
Task branch：`codex/v2-task-p-automation-validation-20261014`。
機器執行紀錄：[TASK_P_READ_ONLY_RUN_2026-10-14.json](TASK_P_READ_ONLY_RUN_2026-10-14.json)。

## 結論與證據等級

**目前不能把「ChatGPT Plus + Codex Cloud + GitHub」驗收為 W1～W5 無人值守、每小時自動開發的完整方案。** 已證實手動啟動的內建 Codex 能執行修改、測試及官方 GitHub Draft PR 發布；未證實原生 Cloud 排程能重新綁定本 repository、published environment、分支及工作狀態，再完成開發與 PR。

本文使用三個等級：**實測**＝本次或 #484 已讀回的真實執行證據；**官方文件支持**＝能力有官方說明、未在本帳戶完成該鏈路；**尚未確認**＝沒有成功執行或必要入口。排程 metadata、離線測試及架構提案都不提升為端到端自動開發成功。

| 問題 | 結果與等級 |
| --- | --- |
| Codex 有原生定期工作嗎？ | **官方文件支持**：桌面 Codex/ChatGPT Scheduled 可對本機 project/worktree 定期工作；需要電腦與 app 持續運作。不能推導本帳戶有原生 Codex Cloud 排程。 |
| 每小時或其他週期？ | **實測**：五個現有 ChatGPT Worker 排程為 HOURLY。**官方文件支持**：付費方案有 hourly，桌面 custom schedule 支援 RRULE。Codex Cloud 環境綁定的週期觸發 **尚未確認**。 |
| 排程直接改程式及測試？ | **官方文件支持**：桌面 project/worktree 背景工作可以執行檔案與命令，受 sandbox/policy 限制。**實測**：本次手動 Cloud checkout 執行現有測試。排程觸發此 Cloud executor **尚未確認**。 |
| 排程直接建立 Draft PR？ | **實測**：#484 是官方 ChatGPT GitHub 整合發布的真實 Draft PR。**尚未確認**：它沒有排程 trigger/run ID，不能證明排程可發布，或 Codex 網頁原生 PR 按鈕可用。 |
| 每次要人工確認？ | **官方文件支持**：背景 Scheduled 可以 unattended 執行，但 app approvals、workspace rules、sandbox、quota 或拒絕仍可停止。**尚未確認**：本帳戶 Cloud → GitHub write 是否每次需確認。此次明確授權不解除歷史 Worker 拒絕。 |
| Plus 涵蓋嗎？ | **官方文件支持**：符合 rollout/workspace 條件的 Plus 包含 Codex Cloud，ChatGPT sign-in 用訂閱額度。**尚未確認**：本帳戶方案、剩餘額度及實際五 Worker 長期用量；沒有讀取 billing/usage dashboard。 |
| 額外費用與限制？ | **官方文件支持**：本機／cloud／Work 共享相關額度，有五小時及可能每週限制；credits/升級為另購。API key 是另外計費路徑。**實測**：本次未建立付費 API 資源、購買 credits 或新增憑證。 |

官方來源（本次查閱；頁面 redirect 已跟隨）：

- [Scheduled tasks / Codex 桌面與 web 工作的區別](https://learn.chatgpt.com/docs/automations?surface=app)。
- [Scheduled tasks in ChatGPT：hourly、approval 與 active-task limits](https://help.openai.com/en/articles/10291617-scheduled-tasks-in-chatgpt)。
- [Using Codex with your ChatGPT plan：Cloud 資格、sign-in 及限制](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan)。
- [Pricing：Plus、共享用量與額外 credits](https://learn.chatgpt.com/docs/pricing)。
- [Codex Cloud：published environment、獨立 workspace 與手動啟動](https://learn.chatgpt.com/docs/cloud)。

## 最新儲存庫、Task M～O 與排程

已讀取 latest-main AGENTS.md、R4.2 Research/Navigation、V2 README、architecture、governance、worker contracts、Codex Cloud runbook、Free Composition、Access Advisory、solar/NWS 契約及 W5 release/pin files。與 #484 基底比較，這些適用規格及 ops/workflow 內容沒有漂移；期間 main 的 WeatherGrid 資料更新不是新 V2 開發。main 上 W1～W4 source pins 可通過現有 provenance 驗證。

| 已有交付 | 本次確認 |
| --- | --- |
| [#483](https://github.com/gdrabbit137-ai/ChaseLights/pull/483) | OPEN / Draft / unmerged；head `543169a5e4c6df50a08fcc07c96a700bf49e7b15`。六個檔案是 proposal runbook、offline gate、read-only inventory、兩組測試及 dry-run workflow。它們不在本次 main。 |
| #483 真實 CI | [V2 Integration 38461152735](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38461152735) 與 [Release Gate Dry Run 38461152589](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38461152589) 均 completed/success，對應上述 head。這證明 PR CI，不能證明已安裝排程 executor、auto-merge 或部署。 |
| [#484](https://github.com/gdrabbit137-ai/ChaseLights/pull/484) | OPEN / Draft / unmerged；head `412908e4ee8f9bfb6f739e76b9a43edc3780d903`，官方 GitHub 發布已實測。 |
| #484 真實 CI | [38558862380](https://github.com/gdrabbit137-ai/ChaseLights/actions/runs/38558862380) completed/success；實際 job log 為 157 PASS / 0 FAIL / 0 ERROR / 0 SKIP，checkout/test SHA 為合成 merge `e7e317ed19ca97b5182d1756fa6bfb81cc086eed`，不是 main 已合併。 |
| Task M | W5 排程保存其禁止 merge/deploy、不得重試受拒 GitHub inventory 寫入的限制。可核查遠端成果以 #483 為準；未重做它的程式。 |
| Task N、O | 本 checkout、相關 PR/Issue 文字及 Task 分支搜索沒有可將 N/O 分別對應到離線檔案、固定 SHA、部署事件的 manifest。既有聊天的離線成果不在此工作區；**未核實其內容／安裝／運作**。未重建、未宣稱已部署。 |

五個既有排程皆 `is_enabled=true`，RRULE=HOURLY；W1 :15、W2 :25、W3 :35、W4 :45、W5 :55。保留原 Asia/Taipei schedule；未更改時區、prompt、enabled 或 cadence。API 提供 last_run_time，但 next_run_time=null，也沒有每輪結果日誌；不能把 enabled/last_run_time 視為成功。

W1、W4 是明確唯讀；W2 有被拒寫入的限制；W3 保留安全拒絕禁令；W5 是唯讀协调並保留 Task M 阻擋。**#484 的新文件發布成功不解除這些舊任務的拒絕。**

最新官方文件列 Plus 最多五個 active scheduled tasks。若本帳戶適用 Plus 的現行限制，五 Worker 已占滿，不能承諾建立第六個測試；本次未嘗試建立，也未為騰出容量停用任何 Worker。帳戶 entitlements/rollout 實際值仍需 Scheduled/Usage UI 確認。

## 真實最小驗證與停止原因

本次在現有內建 Codex Cloud 做一次 **manual one-shot 唯讀驗證**：透過已連接官方 GitHub 整合讀 repository/main、PR #484 head、check runs、workflow run、jobs、reviews，並保存此紀錄。run/check/review/jobs collections 的項目數少於 100 或 total_count 與返回數一致；沒有把截斷的 first page 當完整庫存。

#484 只有一個 check run 且 success、0 reviews。Commit Status API 為 pending、total_count=0，表示沒有舊式 commit statuses；不能因此否定已讀到的 successful check，也不能因此稱所有 release gate 完成。

未建立 native Cloud schedule，原因：

1. 本回合只有一般 ChatGPT `automations.create/list/update`，其可用 schema 沒有 Codex Cloud environment、repository、branch/worktree 綁定欄位。Sites schedule 是另一產品，不適用。
2. 已安裝 Codex CLI 0.159.2，`codex login status` 顯示 ChatGPT sign-in；`codex cloud --help` 有 exec/status/list/apply/diff，沒有 Scheduled 管理介面。官方也說 CLI 不提供該介面。
3. 一次 `codex cloud list --limit 1 --json` 實際 exit 1：`list_tasks failed: error sending request`。沒有返回 Cloud task ID，傳輸失敗的根因未確定；不能推測為訂閱不含或 token 無效。未換憑證、改 endpoint 或重試。
4. 不能用一般 ChatGPT Scheduled 來滿足使用者指定的「Codex 原生排程」條件。**scheduled-run verification = NOT PERFORMED**，不是 PASS，也不是平台全面不支援的宣告。

另實際執行兩組現有驗證：

- #483 fixed-SHA 四個程式／測試檔案以 `git show` 取出至 work/：16 PASS，空 snapshot 被拒（eligible=false，exit 1）。這是離線重跑，不是部署，也沒有重新執行遭拒寫入。
- reviewed-main checkout 跑 `ops/v2/postmerge_verify.py`：source provenance PASS、157 tests PASS（含六個本機 browser cases）、0 FAIL/ERROR/SKIP；**完整 integration gate 為 FAIL**，因 local-isolation 同時要求公開網站 HTTP，而 proxy 對 chaselights.app 回傳 403 Forbidden。未重試、改 proxy、放寬網路或降低 gate。不能把 157 tests PASS 縮寫為完整 gate PASS。

## W1～W5 協作設計（未啟用的新開發流程）

| Worker | 只可修改 | 典型下一個候選工作／依賴 | 驗證與交接 |
| --- | --- | --- | --- |
| W1 | specs/v2/ | NOAA/模型契約缺口；先確認 main 已有 M6a/M6b，避免重做 | schema、negative fixtures、W2/W3 contract handoff；不自行改資料或 UI |
| W2 | data/v2/ | Batch05 真實題材證據；#465 真人簽核仍缺，既有被拒操作不能重試 | canonical/crosswalk/evidence、三語內容、source hashes、research-only |
| W3 | packages/core-v2/、packages/models-v2/ | #467 的 phenomenon pilot；依賴核准 W1 契約、W2 題材與真實 provider/threshold | evaluator/model/negative tests；RAW_ONLY、WINDOW 不晉升 FAVORABLE |
| W4 | apps/web-v2/ | 研究預覽回歸、未完成語意／資料呈現；必須確認真實 W2 fixture | locale/keyboard/browser、research-only、不提供未驗證 Directions |
| W5 | ops/v2/、.github/workflows/ | PR/CI inventory、source pin、Task P 下一步；本次不接手其他 owner 實作 | owner dependency / merged-tree gate / review；merge 與 deploy 禁用 |

每次工作執行以下協議；這是可實施的設計，不能聲稱已有 coordinator/鎖在運行：

1. **Intake**：fetch 當下 main；記錄全 SHA 與適用 specs blob。讀 issue、全部相關 open/closed PR、owner branch HEAD、進度紀錄，選一個真未完成且未受拒的 acceptance item。
2. **Dedup / claim**：task_key 使用 repository + owner + issue + acceptance revision；先查相同 key 的 branch/PR/run。W5 單一 dispatcher 串行 claim；同 owner/path 只能一個 executor。每小時錯開只能降碰撞機率，不能當鎖。
3. **Base / isolate**：若 owner 實作已在 main，用已核實 main；若必要程式只在 pending owner branch，明確 pin 該 base/dependencies。建 distinct `codex/v2-w<owner>-<issue>-<run>`，不覆寫 worker 正式分支。
4. **Execute**：只改 owner allowlist；不得修改其他 owner pin/fixture、Legacy 或 workflow。跨 owner 需求產生 handoff，各 owner 獨立 PR。W5 review 實際 normalized changed paths、rename 與 symlink，不能只信 prompt。
5. **Validate / draft**：跑適用現有測試；記錄 exact tested HEAD、PASS/FAIL/ERROR/SKIP、source evidence；失敗保存 runnable logs，保持 Draft。官方 connector 發布若生成不同 SHA，先核對完整 tree，並在發布 head 上重驗。
6. **CI**：讀 GitHub 原始 run/check/job/log，核對 event、workflow path、PR number、head SHA、run attempt、tested checkout SHA。PR merge-ref 與 branch head 分列；pending/缺失/skip 不算通過。
7. **W5 acceptance**：核對依賴與以下 Release Gate，不能替真人簽核。任何 gate UNKNOWN/FAIL 保持 Draft，本 Task P 永不 merge/deploy。
8. **Durable progress**：worker 用自己 PR body 保存 key、base/head、tests、deps、blocker、next item；W5 才可維護 ops/v2/ 的 ledger。狀態為 CLAIMED → RUNNING → DRAFT_PR → CI_PENDING → W5_REVIEW / BLOCKED；保留歷史結果而不覆寫。
9. **Resume**：下一輪從遠端紀錄恢復，重新驗證 main/spec/head；先接續既有 PR，不新增 duplicate。quota、缺權限、受拒或不可信輸入即 STOP/BLOCKED，不能自動轉別種憑證或付費 API。

不把上述五個邏輯 owner 等同五個無限制並行 agent；最低成本配置使用一個 coding executor 串行服務，owner 職責仍分開。這不會修改五個現有 schedule。

## W5 Release Gate

| Gate | 必要證據與失敗處理 |
| --- | --- |
| PR 來源／SHA | repository/head owner、branch parent、task/run provenance、真實 diff；local、remote、tested SHA 必須可追溯 |
| Actions | complete jobs/checks/statuses、required workflow identity、exact attempt；合成 merge、PR head、post-merge main 各別記錄；未完成保持 Draft |
| W1～W4 dependencies | exact owner commits/trees、main ancestry、canonical bytes/fixture/manifest；任何修改須 owner review，W5 intentional repin |
| 規格 | 當下 main AGENTS/R4.2/V2 blob，main 移動後確認相關 spec 是否漂移；不能沿用舊 chat 指示 |
| 三語 | machine key/non-regression + 真實 zh-TW/en/ja semantic review；presence tests 不冒充真人簽核 |
| 科學防線 | missing critical input → UNKNOWN/NOT_EVALUABLE；fixture、RAW_ONLY、WINDOW、無核准 threshold/model binding 不產生 favorable/score/probability |
| Research-only | public catalog research_only=true、forecast_available=false、selected_date_recommendation_eligible=false、evaluations=[]；R1 不晉升正式推薦 |
| Access/navigation | closure 是獨立不計分 advisory；geometry/navigation 分離；未核實 lawful arrival point 不生成 Directions |
| 授權／policy | 核對 branch protection、rulesets、CODEOWNERS、required reviewer、deployment gates、人類 evidence approval、明確 action authorization；無法讀取即 UNKNOWN/BLOCKED |

本次 branch protection 讀取 **403 Resource not accessible by integration**，未擴大權限；rulesets collection 回傳 []，不能據此說 branch policy 全部滿足。main 無 CODEOWNERS 檔；這也不是免除 owner review。#465 human evidence / access / translation signoff 尚待真人審查。歷史 safety refusal 未解除。merge_authorized=false、deploy_authorized=false；就算所有 CI success，也沒有本次發布產品的授權。

## 成本最低的下一階段

**立即可用的 Cloud 路徑**：保留五 Worker 唯讀研究／coordination，每次由使用者在已發布 ChaseLights Cloud environment 啟動一個 owner-specific task；該次任務完成 code/test/Draft PR，W5 讀 CI。使用 ChatGPT sign-in 的 included quota，無須買 OpenAI API；仍有每次人工啟動及用量上限。這是半自動，不是已驗收的 hourly autonomous development。

**無額外 API 的定期 coding 替代**：若可使用一直開機的電腦，在 ChatGPT desktop Codex 選本機 ChaseLights project、Scheduled、isolated worktree，設定自訂 cadence。先只測兩次 readonly，下列 prompt 可直接使用；operator 必須先確認 schedule mode/project/worktree 與容量。這是本機方案，不是 Codex Cloud；本回合沒有可控制該桌面的工具，未設定它。

Readonly prompt：

> 只讀取 gdrabbit137-ai/ChaseLights，取得當下 main 完整 SHA；讀 PR #484 的 head、state、draft、merged、所有 checks 與 Actions run/job/log，列出 CI 實際 checkout SHA、PASS/FAIL/ERROR/SKIP 或 UNKNOWN；以執行時間、executor context、repository/head/run URL 產生可檢閱紀錄。不得修改 repository、comment、建立 PR、rerun CI、merge、deploy、購買或更換憑證；任何拒絕停止，沒有真實結果不可稱成功。

建議 pilot `RRULE:FREQ=HOURLY;COUNT=2`，在 Scheduled 可 Pause/Delete。**只是待設定方案，本次未建立。** 五個現有 tasks 不得為 pilot 自行修改；Plus 若容量已滿，需使用者另行明確決定是否調整現有配置。不要將提示文字中的 environment ID 當已存在的原生綁定。

**Cloud 原生下一道驗收**：若 Codex/Work UI 實際提供 repository + published environment + branch 的排程目標，再建立独立兩次 readonly pilot。必須收集 schedule ID、真正 timer trigger、兩個 run/task ID、executor context、讀回 SHA/CI 與輸出；僅 Run now 不證明 timer。確認成功後，另行授權一個低頻單 owner code/test/Draft PR pilot，才能考慮五 owner 協作。未滿足即停在半自動 Cloud 或桌面方案。

不採用 `openai/codex-action@v1` 作為「Plus 免費 Cloud 原生排程」：其[官方範例要求 API key](https://learn.chatgpt.com/docs/github-action)，是另外計費的 API/CI 執行方案。[Codex automation access tokens](https://learn.chatgpt.com/docs/enterprise/access-tokens) 目前面向 Business/Enterprise，不能假設 Plus 可取得。GitHub `@codex` 的[官方 PR delegation](https://learn.chatgpt.com/docs/third-party/github) 可作受支持的事件入口候選，但本次沒有啟用、發送 trigger 或验证 reaction/task ID，也不能拿 review success 當開發 PR 成功。

本次 Task P 的安全邊界：獨立文件／紀錄 Draft PR；不寫 main、不合併、不 auto-merge、不部署、不建立付費 API 資源、不擴 GitHub 權限、不修改既有排程、不重試原受拒操作。完整進度、commit 與 Task P 自身 CI 另由 PR/task report 記錄。
