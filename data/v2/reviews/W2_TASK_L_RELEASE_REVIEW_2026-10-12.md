# W2 Batch03 發布前研究審查（Task L）

審查日：2026-10-12。資料基線：W2 #444 `8725bf13348dfae371ae8358930a25dd424a3361`（承接 #440）；最新 main 查核時為 `fc146b58df237943b283dd197dce4fc78e73ebc3`。參照 main 的 AGENTS.md、R4.2 研究及導航規格、V2 schema/Worker contracts，以及未合併的 W1 #450、W3 #447、W4 #454、W5 #455 和 W5 release gate。#450 的自由構圖政策仍是待審提案；本次沒有把它當成已合併的 main。

這是 AI 的研究審查紀錄，**Human Signoff: PENDING**。以下分類只用於審查：`VERIFIED_BY_EVIDENCE`、`PARTIALLY_SUPPORTED`、`UNKNOWN`、`REQUIRES_HUMAN_REVIEW`、`UNSUPPORTED`；沒有新增 Canonical schema enum。三筆仍是 R1 / `evidence_review`，沒有 Live、FAVORABLE、數值門檻、AUTO binding、經驗證的 Camera polygon 或 Directions。

## 證據與適用範圍

「查核」只代表當日檢視該來源可取得的公開內容，不是現場觀測或攝影許可。無刊載日期時寫「未載」，不以網站頁尾日期代替文章日期。

| ID／來源 | 發布／更新；查核 | 確實支持的主張與地理範圍 | 時效、限制與 Canonical 對應 |
| --- | --- | --- | --- |
| e016a [林業保育署鳶嘴稍來小雪山步道](https://www.forest.gov.tw/0000304)；補充 [官方步道動態頁](https://recreation.forest.gov.tw/Trail/RT?tr_id=060&typ=0) | 頁面發布日未載；2026-10-12 | 鳶嘴山岩稜、峭壁、攀岩步道及山景；`tw-016-P01` 的 existence、Camera 安全及 ACCESS_SAFETY。動態頁顯示整條路線「部分開放」，2026-09-03 至 2027-03-06 封閉的是**稍來小雪山段 8–10K**，不可套用為鳶嘴山段封閉或全線開放。 | 路況會變；無合法立足點 polygon、現場繩索狀態及實際抵達 GPS。`camera_contexts`、`condition_contract`、`navigation_targets`。 |
| e016b [健行筆記照片與紀錄](https://hiking.biji.co/index.php?act=info&q=review&review_id=46263) | 拍攝／發表日未確認；本輪未能獨立確認原圖 EXIF；2026-10-12 檢視既存引用 | 原審查描述岩稜前景與遠山層次，是 `tw-016-P01` 的 B 級照片線索；與官方地點敘述互相參照。 | 作者、機位、時季、拍攝方向及照片位置均未獨立驗證。不能用這張圖證明合法 Camera Area。`targets`、`observation_relations`、existence。 |
| e026a [風景區官方景點頁](https://www.swcoast-nsa.gov.tw/zh-tw/attraction/details/000369) | 更新 2026-09-21；2026-10-12 | 井仔腳格狀瓦盤鹽田、夕陽及晚霞倒映，是 P01/P02 題材存在的現地 A 級文字與圖說。頁面列夏令 09:00–19:30、冬令 09:00–18:30，另有每日 09:00–18:00 區塊，兩者口徑不一；特殊錄攝影需求要求事前洽營運單位。 | 時段須由管理者確認；景點範圍不等於可拍攝區域或導航點。`tw-026-P01` existence、日落條件；P02 的交叉核實。 |
| e026b [原瞭望台整修公告](https://www.swcoast-nsa.gov.tw/zh-tw/news/details/2592) | 發布 2026-09-02、更新 09-03；2026-10-12 | **管制區只有公告指稱的「井仔腳瓦盤鹽田瞭望台」**；自公告日起全面暫停開放，預計至 2026-11-30。另建議步行至永華哨所觀景平台，該平台每日 09:00–18:00 開放。對 P01/P02 的封閉警告與 P02 Camera 排除該瞭望台有直接支持；依最新 V2 產品政策不得作為攝影 BLOCKER。 | 結束日是預計而非自動開放日。只證明替代平台供登高眺望，未獨立證明任何其他公共攝影區邊界、商業拍攝許可、替代平台的特定構圖、通行線或 GPS。`camera_contexts`、ACCESS_SAFETY claims。 |
| e026c [原審查所列風景區新聞](https://www.swcoast-nsa.gov.tw/zh-tw/news/details/1896) | 原紀錄未載；2026-10-12 直接讀取逾時 | 原紀錄稱鹽滷倒影、鹽堆與晚霞，但本輪**未能獨立重讀原文**。目前 P01 的夕霞 QUALITY claim 仍引用它。 | `PARTIALLY_SUPPORTED`，應由人核對該頁主張；不得以讀取失敗的來源推定風速或彩霞機率。`tw-026-P01` QUALITY。 |
| e026d [臺南市政府新聞及附圖](https://www.tainan.gov.tw/News_Content.aspx?n=13370&s=8717068) | 2025-01-15；2026-10-12 | 市府明確記述井仔腳夕陽景點。原審查照片稱鹽池、鹽堆與反射同框；本輪未取得照片 EXIF。 | 文字能佐證景點與夕照，不證明圖中的拍攝點、今日許可或特定幾何；對其照片細節保留人工複核。`targets`、`observation_relations`。 |
| e026e [風景區官方夕鹽段路線](https://www.swcoast-nsa.gov.tw/zh-tw/tour/beimen-route) | 頁面發布日未載；2026-10-12 | 直接記述井仔腳瓦盤鹽田整齊鹽池、滷水倒影、夕照、雲與彩霞，且有攝影愛好者欣賞。為 P02 存在與晚霞／鹽田構圖提供可重讀、現地 A 級證據。 | 場景可拍不等於每次都有彩霞；亦無攝影區界線、拍攝許可、風或雲量門檻、抵達 GPS。`tw-026-P02` existence、target、WEATHER/QUALITY。 |

沒有證據支持「最佳季節」或全年固定最佳時刻；P01/P02 只保留與日落前後相關的定性題材，tw-016 沒有固定時段。科學條件僅作方向性指引：山景需要可辨的遠山，夕照需實際光線，彩霞需實際形成；現有來源不支持公里能見度、風速、雲量、方位或機率數值。

## 逐筆結論

| Opportunity | 題材／Subject | Camera 與現行存取 | Navigation／條件 | 結果 |
| --- | --- | --- | --- | --- |
| `tw-016-P01` | `VERIFIED_BY_EVIDENCE`：官方指明鳶嘴山危崖岩稜及山景；照片層次 `PARTIALLY_SUPPORTED`。 | `PARTIALLY_SUPPORTED`：官方指定步道可作一般研究脈絡，無已驗證安全攝影區 polygon。動態頁只明確封閉稍來小雪山 8–10K；鳶嘴路段當日繩索、路況、許可 `UNKNOWN`。 | `UNKNOWN`：無獨立實用抵達點座標；距離、方向、仰角、定量能見度皆未知。危崖／濕滑為獨立進入及安全警告，不改變天氣攝影適合度；尚無經核准的即時預報，因此不得產生 Live FAVORABLE。 | R1；`REQUIRES_HUMAN_REVIEW` 現場路況、Camera 範圍與三語。 |
| `tw-026-P01` | `VERIFIED_BY_EVIDENCE`：瓦盤鹽田與夕照；不含特定太陽方位或固定鏡面構圖。 | `PARTIALLY_SUPPORTED`：舊瞭望台封閉公告仍刊載，預計至 11-30。替代永華平台 09:00–18:00 的「觀景」功能有官方證據，**特定拍攝位置／其他開放區界線與權限仍 `UNKNOWN`**。平台的關門時間不能用鹽田冬令 18:30 自動延長。 | `UNKNOWN`：無經驗證的抵達點／攝影 polygon／幾何；現場 ACCESS_SAFETY 獨立顯示為警告，夕照／晚霞只能 GUIDANCE；封閉不作為天氣攝影條件的 REQUIRED／BLOCKER。 | R1；現有 P01 Canonical 與 Preview 保持原樣，Preview 不提供路線／即時推薦。 |
| `tw-026-P02` | `VERIFIED_BY_EVIDENCE`：鹽池加夕照／彩霞是地點特定題材；所選日期是否有彩霞 `UNKNOWN`。 | 原短文「開放的鹽田公共區」容易被讀成已知區域。**已修正**三語 Camera 短文：實際開放、許可、邊界尚未獨立核實；無法確認時不可用，舊瞭望台不得進入，替代平台不保證別區開放。Camera geometry 仍 unknown/provisional。 | `UNKNOWN`：Navigation 無座標，晚霞形成仍需 VERIFY；公共區開放狀態僅為安全警告，不改變天氣判定；沒有科學閾值。 | R1；需現場／管理單位確認及正式三語簽核。 |

## 原始與更新資料差異

- P02 `camera_contexts[0].access_notes_i18n`：三語原本僅稱「開放的公共區、不要使用封閉瞭望台」；現在明示**區域與邊界未獨立核實、依當日公告及現場規定，若無法確認則不可使用**。Human-readable 的 Camera 行與 Crosswalk `H-tw-026-P02-camera` 同步，保留研究限制段落。
- P02 Canonical 的 Camera 引用補入直接支持封閉的 e026b；題材、Target、Relation 與晚霞條件以可重讀的官方 e026e 補強／取代本輪讀取失敗的 e026c 引用。Crosswalk 對應引用同步；Evidence Audit 新增 e026e。沒有升級研究成熟度或驗證地理位置。
- P01 Canonical 與 Research-only Preview 的內容未變；P02 不在該單筆 P01 Preview 中。三筆 Human-readable 內容、Canonical 的 zh-TW 欄及 Crosswalk 需由自動驗證逐一對照。P01 Preview 應與 P01 Canonical 完全相同，且 `research_only=true`、`selected_date_recommendation_eligible=false`、`forecast_available=false`、`evaluations=[]`。

## 三語語意核對

逐一比對三筆的 name、description、Camera access/safety、Target、Navigation label、四條 condition notes 與研究狀態的結構／Human review。P02 修正後，繁中、英文、日文均明示未知合法區界、需當日確認、封閉瞭望台不可用；P01 三語均明示舊瞭望台封閉、區界未知及抵達點未驗證；tw-016 三語均保留危崖與合法步道安全限制。研究狀態 R1、`evidence_review` 是 Canonical 的非文案欄位，Research-only 提示由 Preview 的安全旗標與 W4 獨立呈現，這份 W2 審查沒有代替 W4 畫面簽核。**AI 語意檢查通過並不構成人類正式簽核；Human Signoff: PENDING。**

## 人工審查問題與發布決定

1. 管理單位能否提供 P01/P02 一般攝影（以及特殊錄攝影）當日允許的具體區域、營業時間與限制？官網每日 09:00–18:00 與季節時間不一致，請確認適用區域和夕照時段。
2. 舊瞭望台是否仍按 2026-11-30 預定完工？永華哨所平台能否拍攝鹽池與夕照，從哪個合法範圍？目前僅能證明其為 09:00–18:00 替代觀景平台。
3. 是否取得分別驗證的合法實際抵達點、Camera Area、通行動線和地理證據？不得用景點中心、照片或地圖搜尋結果代替。
4. 鳶嘴路段當下是否開放及安全？P01 的 e026c 原文／e026d 照片細節可否人工複核？請真人逐欄核准 zh-TW/en/ja 的攝影條件、限制及 Research-only 警語。

結論：資料可保留在**供審查的研究資料及受控 Research-only 檢視**，但尚未滿足公開 Preview 的存取／三語人工審核 gate。若要公開，先取得上述證據與正式簽核；之前維持沒有 Directions、選定日期推薦、分數或 FAVORABLE 的研究呈現。W3 需檢查來源 SHA／fixture，W4 需檢查 #454 manifest／fixture／catalog 是否引用本次 P02 Canonical，W5 需更新 #455 W2 pin 後重新執行整合 CI 與合併模擬。其餘 Worker 所屬檔案未在本 PR 修改。

## 驗證紀錄

在 #444 精確來源檔案本機具現後執行 `python -m unittest discover -s data/v2/tests -p 'test_*.py' -v`：**發現 8 項；7 PASS / 1 FAIL / 0 ERROR / 0 SKIP**。唯一 FAIL 是 SchemaGate 的環境相依 `ModuleNotFoundError: jsonschema`；嘗試 `pip install --target /tmp/chase-task-l-deps 'jsonschema>=4.23'`，此執行環境未找到可用套件來源。交叉對照、Human-readable、引用完整性、P02 三語存取限制、P01 Preview 與 Canonical 完全一致及 Research-only 安全旗標的 7 項均 PASS；Python compileall、JSON 語法及三份 Canonical 的 Evidence ID 解析另行 PASS。**Schema Validation 未完成，不得宣稱 8/8 或 GitHub Actions 綠燈。**

目前 main 的 `.github/workflows/v2_schema_contract.yml` PR path filter 只包含 `specs/v2/**` 與 workflow 自身，這個 W2 `data/v2/**` 修正預期不觸發它。PR 建立後仍須查實際 run；W5 的既有 113 PASS 屬於舊 W2 HEAD，不適用本次 P02 變更。

## 2026-10-12 存取警告政策更正（接續 W1 #457）

本次僅遷移 ConditionContract 的角色分類，不改寫封閉事實或提升資料證據信心。`tw-016-P01`、`tw-026-P01`、`tw-026-P02` 各移除兩項舊 `ACCESS_SAFETY` REQUIRED/BLOCKER，保留全部已查核 Camera access/safety 三語內容、官方封閉公告、導航 needs_review、原始 EvidenceClaim 與來源連結。Crosswalk 的 condition ordinal 依實際保留的兩條攝影條件重新定位，Human-readable、P01 Preview 同步。封閉、危險步道或未核實位置只能作進入警告，不得影響天氣攝影分數／判定。現場仍不得進入封閉區域，沒有經驗證的抵達點仍不提供 Directions。原研究 R1/Research-only 不變，人類審查仍 PENDING。
