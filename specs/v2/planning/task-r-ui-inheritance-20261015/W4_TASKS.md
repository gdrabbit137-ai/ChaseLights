# W4 可執行開發任務與跨Owner前置工作

以下是後續任務卡，不是本次實作授權，也不是已建立的GitHub Issues。保留Task U的U-W4-*對照；使用R-W4-*是避免把已完成U-W4-01重做。每張卡一個獨立Draft PR；W4只改apps/web-v2/，不修改Legacy、W2、W3、spec或W5 gate。

## 每批共用執行要求

1. 讀最新main/AGENTS/R4.2/specs/v2與當時W1–W5 HEAD；核對前置成果是否merge/accepted，選正確已存在W4 base，不盲從main重寫，不寫worker原分支。
2. 將輸入的commit/path/blob/revision、allowed paths及產品scope寫進PR。真實資料從accepted W2 source manifest與W3 artifact接入；W5可打包同源靜態資料／提供versioned result服務，不能在產品runtime載入tests fixture或用UI猜真值。
3. 修改與新增文字同批完整zh-TW/en/ja；三語×手機／桌機驗收、keyboard、loading/error/empty、無錯誤Directions／score是每批基本要求，不延到最後才補。
4. 執行當時存在的 `node --test apps/web-v2/tests/*.test.mjs`、`node --test apps/web-v2/tests/browser-smoke.mjs`及source/schema checks。保留既有cases，新增實際state/interaction tests；沒有browser或資料不稱PASS，測試fixture只能在tests。
5. 交W5 exact W4 tree、dependency清單及實際discovery、原始log／限制。source pin mismatch交給W5獨立接受，不能降門檻或把沒有跑的full CI標綠；保持Draft，不merge/deploy。

## 跨Owner前置卡

| ID／Owner | 具體交付 | 完成條件／相依 |
| --- | --- | --- |
| R-W5-00／W5 | 重用#488既有#486/#487整合，接受最新main政策、#489/#490及本規劃，各自更新source pins；#493/#494審查handoff獨立接納 | 新HEAD真實full CI；保留全部157基準與新增測試；不重開相同首頁PR、不自動部署。#488舊267成功不能抵新組合。 |
| R-W1-00／W1 | 調和#489與#491政策；接受#490 sidecar／partial metadata讀取範圍，明確R1 A/B/C、GUIDE與live不同；保留六既有schemas | approved exact契約／review紀錄供W2/W4使用；不能為complete picker放寬metadata來源或假標human approved。 |
| R-W2-01／W2 | 針對既有7 Place補國別、行政所屬、TW22/JP47/US51 registry與三語名稱、Place-scope IANA evidence／extent；不重研主體、不新增景點 | 每值source/checked date/scope；多行政／跨時區解釋；缺資料維持UNKNOWN；更新index revision、provenance、test。不得從ID前綴或device猜值。 |
| R-W2-02／W2獨立review | 接續#493/Task Q實際成果，逐claim source、crosswalk、三語語意及access scope檢查；產A/B/C disposition | 有實際獨立查核才標A/B；C隔離；原human PENDING保留。可與registry補證平行，不能重建已完成Database。 |
| R-W3-01／W3 | 依C4真實local-day resolver與versioned WINDOW/raw artifact接線；另與W2選一個科學pilot，產owned condition/recommendation | DST/日界線/跨日/provider時間覆蓋與provenance負測；WINDOW/raw永遠不自動推薦。不得以NWS Seattle給台日資料。 |
| R-HWG-01／WeatherGrid owner | 重用既有全球loader，補來源時間／native resolution、coverage、風密度／雲配色與三語；定義可支援route參數 | 真實TW/JP/CONUS/Alaska/dateline與pan測試、missing/429不當0%，觀測/proxy分開；獨立PR。 |

## R-W4-01：接續攝影首頁與誠實資料狀態（U-W4-01）

狀態：**已由#487實作，#488測過候選267 cases；未合併。** 這張卡是接受／差異回歸，不是新首頁開發。輸入#487 `f0da51f30252328f82babba7d90dd17f1559c68e`，W4 tree `7ad5210b957e9e184f941a06b714106c528e0b0a`；實作時重核HEAD。

保留無真實指定日結果時的明確空狀態、主動研究入口、進階工程資訊及完整研究文字。由W5修build／public smoke，不讓W4越Owner改gate。驗收仍有43 Node＋75 source-browser案例，delay/404/500/network/invalid/empty/retry與晚回覆；數字是既有候選證據，不是本規劃重新跑。未通過新base回歸不得宣稱已接受。

## R-W4-02：多景點研究探索、真實名稱搜尋與題材多選（優先1）

對應U-W4-03＋U-W4-02C的taxonomy部分；U-F02/04/07/10/20/21/29。前置：接受R-W4-01、C1–C3確切版本、W2逐筆R1研究disposition及W5包裝方式；region/timezone可未知，不阻塞名稱／題材探索。

交付：讀manifest作一致revision，驗每筆canonical來源，按Place group，tw-026兩題材可選；按有來源的名稱／ID搜尋。題材OR、跨維度AND，先篩Opportunity再group，不把同Place另一題材洩漏。研究入口保留非預報標示、全文三語description/conditions、未知欄位與獨立警告；candidate viewpoints不變導航。名稱excerpt不冒稱官方標準名。

驗收：先從最新disposition導出expected集合；若全A/B，精確7 Place/8 Opportunity；任何C/HOLD以明確排除清單驗，不為湊8放行。hash/revision/identity tamper拒絕、部分檔載入失敗不混revision；跨locale搜尋／選取identity不變；兩題材過濾、無結果clear、失敗retry、keyboard＋360/390/1440×3語；0 live score/0 FAVORABLE/0 unverified Directions。既有P01 hash和original provenance保持。完成以獨立Draft交W5；不用預報假資料填卡。

## R-W4-03：收藏、偏好與可用排序（優先2）

對應U-W4-02C餘項；U-F11/12/36。前置：C3＋R-W4-02接受的ID集合。W2補行政／時區與W3 runtime可平行；同app.mjs變更要在02接受後串行。

交付：依 `chaselights.v2.preferences.v1`實作Place/Opportunity收藏；加入／取消／reload、unavailable項目仍可移除。只用可信NAME/REGION，未知membership依C3 missing-last/ID fallback，不偽稱地理順序。SCORE/DISTANCE未滿全部可信條件停用並顯示三語原因；距離只在主動選後要求定位，拒絕回REGION ASC，不存精確位置。

驗收：損毀JSON不startup覆寫、future版本保留read-only、quota/blocked session可用、跨tab最後寫入行為、取消收藏立即更新、unknown/withheld ID不誤配同名、兩種收藏只一Place；stable tie-break、null不當0、filter/date/revision後sort失效明示fallback。**不**補造score或請定位來營造功能完整。

## R-W4-04：行政區多選與目的地日期（優先3）

對應U-W4-02A/02B；U-F05/08/09。前置：R-W2-01真實metadata、C1/C4、W3已測local-day resolver；不能以#490現在0 region/0 zone宣稱已完成。

交付：TW22/JP47/US51及金門連江、未收錄地區狀態、多行政景點去重；手機有界sheet、桌機popover、搜尋/clear/X/Done/Escape/背景/Back、立即多選不關閉、焦點與scroll還原。日期明示per-Place YYYY-MM-DD＋IANA；相對日期由同一frozen UTC now分別換算，不取daily第二筆，不用裝置時區。

驗收：同維度OR跨維度AND；跨界Place只一張、相同地名不串ID；日期陣列亂序／缺日、台美跨日、DST23/25h、跨午夜與no-event、時段前/中/後；A→B→A/retry晚回覆丟棄、cache完整revision key。timezone UNKNOWN時研究仍可用、time-dependent query NOT_EVALUABLE。沒有真實預報可選日期但顯示無結果，不能產生最佳時段或分數。region與date可拆兩個串行獨立PR，兩者都過才關此卡。

## R-W4-05：時間軸、天氣／天文與狀態呈現（U-W4-04A）

U-F06/13/14/16/33/34/36。前置C4/C6與W3真實artifact；C5 UI transport接受後才顯示對應Evaluation。交付WINDOW/raw、forecast/observation/proxy、發報／有效／擷取／計算時間、單位與時間軸，network狀態不取代科學狀態。未來Evaluation元件可tests內fixture驗，public不載fixture。

驗收：raw zero與null、stale/wrong scope/date、NO_EVENT/UNKNOWN、UTC/local offset、native interval不假展成逐時；研究時段與最佳拍攝時段不混，過期不提示現在出發；三語card/detail/timeline相同revision。Sun-only不出現月／銀河／極光可預報主張。

## R-W4-06：真實selected-date攝影pilot（U-W4-04B）

U-F15/17/18及實用預報閉環。前置W1 C5、W2支持主體與approved條件/threshold/AUTO、W3真實matching provider與owned recommendation、versioned result store；不用R1 A/B替代科學核准。

交付一個有明確coverage範圍的真實攝影題材，顯示合理狀態／理由／當地有效時段；QUALITY只有可解釋／可比時顯示。月、銀河、晨霧、雲海等依各自模型能力逐步擴展，不宣稱全部就緒。

驗收：真實provider成功及missing/stale/wrong-date/wrong-region/invalid provenance/threshold null/AUTO未批/未知REQUIRED負測；失敗REQUIRED即使high score不正向、時間成立不代表全部適合；原#388/#423型反例泛化三語；closure前後score/verdict相同但警告和導航獨立。真實資料不足就NOT_EVALUABLE，不把raw或WINDOW改標預報。完成是scoped pilot，非全球全題材正式完成。

## R-W4-07：地圖、導航與WeatherGrid入口（U-W4-05）

U-F19/21–25/35。可先做既有WeatherGrid相對URL入口與返回；deep-link僅使用對方已支持的日期／語系／Place參數。Directions部分等C7正式transport與W2來源，不能自行猜欄位或GPS。

驗收：closed verified、stale/unknown access、needs_review、multiple routes、subject與arrival不同各有反例；不得keyword fallback。警告scope/date/source完整且不改氣象分數；不暗示替代區開放。地圖移動後範圍不足須明示無資料；W4不複製全球loader或把Himawari觀測當forecast。外連返回保留原篩選／日期。

## R-W4-08：RWD、三語與無障礙深化（U-W4-06/07）

U-F26–30，所有前批也必測基本能力。360/390/768/1440/1536/1920、橫直向、200% zoom；>=1500有足夠已准資料時四欄，sticky不蓋內容、焦點無trap、44px與reduced-motion。不能增加虛構live卡只為四欄截圖；layout可在明示tests-only集合測，public仍真實資料。

驗收：keyboard完整探索→日期→詳情→關閉／返回；切語時所有已開面板、狀態與ARIA同步、選取ID不變；逐欄語意對照不以generic theme代全文。保存Chromium device emulation與實體Safari結果的差別；未實測的裝置列UNVERIFIED。

## R-W4-09A／09B：實拍紀錄→真正照片提交（U-W4-08A/08B）

09A前置W1 C9 DTO與W2索引。建立本機選照／EXIF、搜尋配對、unmatched、觀察成立／部分／失敗／不明與原因；缺EXIF保持未知，GPS需使用者確認，不修改Canonical空間真值。驗收零POST、草稿保存／重開／三語／手機與失敗狀態，不稱上傳完成。

09B等W5真實接收服務、用途／同意、保留與刪除、回覆receipt／狀態契約。驗收實際提交、idempotency、進度、斷線／重試、receipt確認、刪除與未review狀態；原圖／GPS權限明確。沒有server／review不產生假receipt或AI判斷。兩卡分開PR；09B為P2，不擋已核准forecast pilot，仍是最終完整實拍能力缺口。

## R-W4-10：完整產品旅程與W5交付（U-W4-09）

U-F37/39/40。對FEATURE_MATRIX逐ID附accepted source、真實test與限制，從搜尋／多選→目的地日期→題材→條件理由／時段→map/warning→實拍完成三語×裝置旅程。P0全部與被接受P1達標，否則明列缺口，不把研究探索驗收當可取代V1。

W5另PR對精確來源做整合／static package／current-head CI與發布readiness；public候選檔hash、hosting approval與實際部署另行授權。本次及後續任務若未給發布授權一律停Draft。由使用者抽樣V1/V2，不建自動結果比較工具。
