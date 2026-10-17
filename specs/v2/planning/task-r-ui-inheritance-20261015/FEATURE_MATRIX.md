# 完整 V1→V2 功能對照

基準main `5bfad32f31007450496ce10123318ac3e8e37aad`。本表沿用Task U全部40項ID；V1與main的網站程式bytes相同，故沿用已確認的CODE事實。Draft實作獨立列示，未合併不算main已有。優先級沿用Task U：P0 26、P1 12、P2 2；P0表示正式產品Gate，不代表必須阻塞每個研究PR。此表涵蓋使用者全部14類：搜尋地區(08–12)、題材排序(07/11)、日期時段(05/06)、評分理由(15/16)、天氣天文(13/14/17/18)、詳情幾何(04/20)、地圖導航(19/21)、WeatherGrid(22–25)、RWD(28–30)、三語(26/27)、實拍(31/32)、不確定性／研究標示(01/16/21/33/34)。

## 現況與差距

| 功能ID／名稱 | V1已有／限制 | V2 main已有／缺少 | 後續Draft／最新缺口 | 優先 | 責任 | 執行批次 | 歷史問題 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| U-F01 攝影預報主畫面 | Place-first 首頁、今天去哪拍與卡片列表；預設地區順序，另可按分數。 | 研究單頁＋側欄；沒有指定日期推薦區，仍要求使用者理解匯入研究資料。 | #487／#488 已完成主畫面候選；未合併 | P0 | W4；跨Owner見契約表 | R-W4-01 | H22 H24 |
| U-F02 多景點可用範圍 | 地區資料各有多景點；正式數量依 weather JSON。 | main 有8筆題材／7景點；預設 Catalog 仍只有 tw-026-P01 一筆。 | #490 已有7 Place索引；W4仍單筆 | P0 | W4；跨Owner見契約表 | R-W4-02 | H23 |
| U-F03 卡片資訊層級 | 景點名、行政區、題材、推薦、時間、少量氣象、工具與收藏。 | 側欄 Place 常顯示 ID；題材內容較完整，但研究版本／R1／review資訊佔主要畫面。 | #487已分層；名稱仍待#490接線 | P0 | W4；跨Owner見契約表 | R-W4-01/02 | H22 H24 |
| U-F04 景點與題材詳情 | Place Guide 分所選日可評估題材與其他研究知識，提供條件與說明。 | 有題材描述、必要條件、風險、未知與摺疊幾何，尚非日期詳情。 | #490提供真實canonical joins，W4未接 | P0 | W4；跨Owner見契約表 | R-W4-02 | H22 |
| U-F05 今天／明天／後天與當地日期 | 按景點 IANA 時區計算日曆日期，find daily.date；已非陣列索引。 | 沒有日期選擇。 | #489日期契約已寫；#490 verified timezone=0 | P0 | W4；跨Owner見契約表 | R-W4-04 | H07 |
| U-F06 研究時間、最佳時段與時效分離 | 日最佳分數／時間段、研究 best_time、逐時列及已過時段分開。 | 僅研究時段文字；太陽 WINDOW 程式在 main，UI尚未接入。 | #489日期transport；尚無W4 runtime時間軸 | P0 | W4；跨Owner見契約表 | R-W4-05 | H07 H08 H09 |
| U-F07 題材分類與多選篩選 | 有題材標籤及資料；現行首頁沒有可操作 theme/scene 篩選，僅殘留變數。 | 可瀏覽所選景點題材；沒有跨景點題材篩選。 | #489 taxonomy＋#490八類十個關聯；W4未接 | P1 | W4；跨Owner見契約表 | R-W4-02 | H25 |
| U-F08 台灣縣市／美國州／日本都道府縣 | 22縣市、47都道府縣、50州＋DC模型；多轄區以陣列交集。 | 沒有國家或行政區控制；投影可接受外部 Place metadata，但預設無完整索引。 | #489完整registry要求；#490 regions=0 | P0 | W4；跨Owner見契約表 | R-W4-04 | H03 H04 |
| U-F09 手機地區面板及多選關閉 | <=640底部面板、搜尋、多選、X／完成／背景／Escape／Back、鎖背景捲動。 | 未實作地區面板。 | #489操作規則已訂；W4未做面板 | P0 | W4；跨Owner見契約表 | R-W4-04/08 | H01 H02 |
| U-F10 文字搜尋 | V1搜尋多語景點名稱、地方名、行政區等。 | 搜尋Place名稱／ID／country/admin1；預設名稱常是ID。 | #487有clear-search；#490名稱可接 | P1 | W4；跨Owner見契約表 | R-W4-02 | H21 |
| U-F11 地區、評分與距離排序 | 明確的地區／分數雙向／距離雙向排序；拒絕定位回地區排序。 | 沒有排序或定位操作。 | #489定義capabilities；score/distance尚不可用 | P1 | W4；跨Owner見契約表 | R-W4-03 | H05 |
| U-F12 我的最愛與偏好保存 | 各國收藏toggle、移除持久化、語言／溫度／日期等本機偏好。 | 只保存語系；無收藏。 | #489版本化local preferences；無W4實作 | P1 | W4；跨Owner見契約表 | R-W4-03 | H26 |
| U-F13 天氣數值與單位 | 溫度C/F、風、能見度、低中高雲等卡片／逐時資訊。 | 沒有日期氣象數值；NWS adapter有raw欄位，不能當攝影判斷。 | main已有NWS RAW_ONLY adapter，UI未接 | P0 | W3；跨Owner見契約表 | R-W4-05/06 | H19 |
| U-F14 太陽、月亮、銀河與極光資訊 | 有太陽方位高度、月亮、暗空、Kp等依題材顯示；不等於全部已科學驗證。 | Sun WINDOW實作已整合；其他能力未接UI，不能假設支援。 | main只有Sun WINDOW；月／銀河／極光未接 | P1 | W3；跨Owner見契約表 | R-W4-05/06 | H12 H13 |
| U-F15 判定與評分一致 | #423後以recommendation物件為準，舊正向status不作fallback；#388仍open。 | runtimeEvaluation固定null，沒有正式分數；正確保持fail closed。 | main W3保守判定；尚無正式pilot | P0 | W3；跨Owner見契約表 | R-W4-06 | H08 |
| U-F16 原因與不確定性說明 | 推薦理由、條件與信心摺疊；部分底層status仍有歷史語意。 | 有必要條件及待確認，但偏研究文字，沒有逐條即時結果。 | #487保留unknowns；日期理由待W3 | P0 | W4；跨Owner見契約表 | R-W4-05/06 | H08 H19 |
| U-F17 倒影與近景不套用山景門檻 | V1有water_surface／本地景物／visibility專用分支，B35修正鯉魚潭。 | 只有倒影R1研究紀錄，沒有已批准AUTO評估。 | 需W2逐題材契約；不複製V1常數 | P0 | W2；跨Owner見契約表 | R-W4-06 | H10 H11 |
| U-F18 雲海／晨霧／銀河時間防線 | V1有可見光／天文／空間proxy防線；雲海不只看單點低雲。 | 沒有這些正式runtime；Sun WINDOW不足以替代。 | Sun WINDOW不代表霧／雲海／銀河可預報 | P0 | W3；跨Owner見契約表 | R-W4-06 | H12 H13 |
| U-F19 地圖與安全導航 | verified到達點才Directions；provisional地圖／待查；有多路線狀態。 | navigationAction有限guard；當前P01沒有可導航目標。 | main guard缺dynamic closure linkage，#487未補 | P0 | W4；跨Owner見契約表 | R-W4-07 | H16 H29 |
| U-F20 自由取景與精確構圖 | V1有機位／觀測關係但歷史導航混淆；不要求沿用限制。 | W1已定自由取景；W4幾何預設收合，有自由構圖提示。 | main自由構圖規格已在；精確構圖僅選用 | P0 | W1；跨Owner見契約表 | R-W4-02/07 | H16 H27 |
| U-F21 封閉與安全警告 | Legacy有access runtime會影響其結果；本次不得改Legacy。 | W1～W4已完成warning-only修正；P01有醒目獨立access區。 | #487保留警告；#491 A/B/C已在main | P0 | W4；跨Owner見契約表 | R-W4-02/07 | H27 H29 |
| U-F22 WeatherGrid與V2入口 | 首頁有weather-map.html和weather-map-v2.html兩入口。 | ChaseLights V2研究首頁沒有WeatherGrid入口；獨立地圖仍在root。 | 獨立WeatherGrid V2既存；app仍無入口 | P1 | W4；跨Owner見契約表 | R-W4-07 | H14 |
| U-F23 全球覆蓋與地圖移動 | 原WeatherGrid有bundle邊界；獨立WeatherGrid V2已有GFS全球fallback、日界線與viewport載入。 | 獨立WeatherGrid V2在main存在，與apps/web-v2不是同一產品頁。 | 沿用獨立WG程式；當前全球live未驗 | P1 | WeatherGrid；跨Owner見契約表 | R-HWG-01 | H14 |
| U-F24 風向箭頭與雲量辨識 | V1已有zoom密度與34/30px bucket間距、風去向圖例、50%配色hinge。 | 獨立WeatherGrid V2沒有同等風箭頭與完整雲配色；不可視為已繼承。 | V1既有密度／配色；獨立WG未同等繼承 | P1 | WeatherGrid；跨Owner見契約表 | R-HWG-01 | H15 |
| U-F25 模型、時間、解析度與觀測區別 | WeatherGrid可切模型、field/time/inspector；Himawari觀測、CWA RH proxy有分離。 | V2 map有provider/valid/coverage/debug，偏工程用；app首頁無氣象來源。 | 模型來源／解析度規範既有；W4未接 | P0 | WeatherGrid；跨Owner見契約表 | R-HWG-01 | H14 H19 |
| U-F26 介面與動態狀態切換 | V1有三語shell、modal重繪與locale-strict；已修混語不等於內容完整。 | 三語UI/ARIA/鍵盤及本機語系持續；31 Node中有對應回歸。 | #487候選已完整動態三語；未合併 | P0 | W4；跨Owner見契約表 | R-W4-08 | H17 |
| U-F27 研究語意完整等價 | 嚴格稽核仍有2899個canonical文字欄位缺locale map；#379 open。 | canonical三語有值與投影保留，但人工semantic signoff=PENDING。 | #490三語索引；未自簽human；#491允許範圍化AI審查 | P0 | W2；跨Owner見契約表 | R-W2-02 | H18 |
| U-F28 四欄與響應式密度 | CSS在>=1500有四欄，700雙欄／1100三欄；含地區群組grid。 | 研究workspace桌機側欄＋詳情，手機單欄；無推薦四欄。 | #487只home/research layout，不等於推薦四欄 | P1 | W4；跨Owner見契約表 | R-W4-08 | H06 |
| U-F29 收合無攝影機會 | V1 deferred-group原生details預設收合no_viable。 | 無指定日結果分組。 | 多景點推薦列表尚未建 | P1 | W4；跨Owner見契約表 | R-W4-02/06 | H06 H19 |
| U-F30 無障礙與對話框 | V1卡片鍵盤、Escape、modal捲動與sticky filters；並非完整WCAG驗收。 | 有skip、ARIA、焦點維持、三語與touch測試；無新面板。 | #487有鍵盤／焦點／44px；全產品待回歸 | P0 | W4；跨Owner見契約表 | R-W4-08 | H01 H26 |
| U-F31 本機照片／EXIF／觀測紀錄 | V1可選JPEG/HEIC/HEIF、多張、本機EXIF、配對、結果與匯出，照片不傳server。 | apps/web-v2沒有實拍入口或表單；不能直接沿用Legacy資料當V2真值。 | 尚無V2觀測表單 | P1 | W4；跨Owner見契約表 | R-W4-09A | H20 H21 |
| U-F32 照片真正提交與處理結果 | 未實作server照片提交；目前只有structured JSON本機保存。 | 沒有submission backend或真實分析結果。 | 尚無V2接收服務／receipt | P2 | W5；跨Owner見契約表 | R-W4-09B | H20 |
| U-F33 Loading、error、empty與retry | V1有loading/load_error/detail_sync_wait，summary/detail版本競爭有恢復處理。 | 自動fetch前render無資料；404直接return；500/JSON錯誤有catch但無retry。 | #487六類狀態已實作，#488 CI通過 | P0 | W4；跨Owner見契約表 | R-W4-01/05 | H19 H28 |
| U-F34 更新時間、有效時間與來源 | V1更新標籤與source details；不同來源有QC/freshness。 | research generated_at、imported_at、loaded time與commit可見；沒有預報issued/valid。 | #487研究載入時間已分；provider時效待接 | P0 | W4；跨Owner見契約表 | R-W4-05 | H19 |
| U-F35 氣象外連、雷達與返回 | V1卡片有天氣modal、官方國別雷達外連；各modal不同目的。 | 研究UI沒有雷達／天氣入口，只有部分證據安全連結。 | 尚無W4工具導覽契約接線 | P2 | W4；跨Owner見契約表 | R-W4-07 | H24 |
| U-F36 溫度單位與資料快取 | V1 C/F本機偏好、記憶／CacheStorage、版本重試與國家切換中止舊request。 | 語系本機保存；Catalog no-store，無forecast/cache協調。 | #489版本鍵與generation契約；尚無runtime cache | P1 | W4；跨Owner見契約表 | R-W4-03/05 | H28 |
| U-F37 Worker來源與版本整合 | V1歷史修復有superseded PR，不能以closed推斷merged。 | W4 #460已進main；#486 Draft未合併；W3 #479 closed未merged但source經#481整合。 | #488有267 CI；#489/#490需新整合 | P0 | W5；跨Owner見契約表 | R-W5-00 | H30 |
| U-F38 過時說明與規格用詞 | V1修復紀錄存在舊政策，不應原封照搬。 | model.mjs仍寫W3未釋出；CAMERA_AREA政策殘留required access evidence可致誤讀。 | #487修主要術語；main仍有stale註解 | P0 | W1；跨Owner見契約表 | R-W1-00/01 | H30 |
| U-F39 發布與公開回歸 | V1 root Pages目前自動從main發布；Legacy需保持。 | V2子目錄已有Preview；Task R工具未進main，正式預報NOT READY。 | #488候選build已測，不等於public部署 | P0 | W5；跨Owner見契約表 | R-W5-00/10 | H30 |
| U-F40 達到V1實用程度的驗收 | V1提供從搜尋到規劃／導航／天氣的完整流程；並非預報真實性的標準答案。 | 現有研究頁測試完整但只驗研究瀏覽，無全流程產品驗收。 | 研究改善不是正式產品取代V1 | P0 | W5；跨Owner見契約表 | R-W4-10 | H22 H30 |


## 契約、相依及逐項驗收

契約代號見[CONTRACTS_AND_DEPENDENCIES.md](CONTRACTS_AND_DEPENDENCIES.md)。本表全部為未來驗收要求，不冒稱本次已測新功能。具體實作順序／可平行工作見Roadmap，tests只可在tests內使用明示synthetic fixtures。

來源Sxx固定連結見[EVIDENCE.md](EVIDENCE.md)；本表保留Task U逐項source mapping。

| 功能ID | 差距／產品目標 | API／Database／Evaluator相依 | 測試及驗收條件 | 程式證據 |
| --- | --- | --- | --- | --- |
| U-F01 | 建立攝影主畫面；預報區無資料時明示，另以使用者開啟的研究瀏覽保留現有內容。 | C0/C1 | 無真實評估時推薦數為0、不出現分數／最佳時段；研究資料只在明確標示的瀏覽區。  | V1 S02 S03；V2 S14 S15 S16 |
| U-F02 | 分離研究列表與推薦；完整顯示已准公開的7景點8題材且逐筆來源可追溯。 | C0/C1/C2/C3 | 精確比對7個 Place ID／8個 Opportunity ID；tw-026 恰有2筆；每筆來源 hash 比對。 逐筆A/B才進Research；C/HOLD隔離，不為湊8筆放行；候選8是snapshot不是永久上限。 | V1 S05 S09；V2 S18 S23 |
| U-F03 | 景點身分、題材與可用狀態優先；證據簽核細節置進階頁，不隱藏影響判斷的缺資料原因。 | C0/C1/C2 | 每張卡最多一個主要判定；鍵盤／點擊可開詳情；工程術語不在主要卡片及主要 CTA。  | V1 S03；V2 S15 S17 |
| U-F04 | 保留完整研究文字；日期預報與「這裡可以拍什麼」分頁／分區。 | C0/C1/C2 | 同景點多題材可切換；研究敘述不被描述成今日已成立；展開前後文字無遺失。  | V1 S03 S25；V2 S15 S30 |
| U-F05 | 顯示明確 YYYY-MM-DD 與景點時區；相對日期按目的地當地日曆。 | C1/C2/C4 | 凍結UTC時間跨台美日期、DST、daily陣列亂序；明天始終取local date+1，不取第2筆。 timezone UNKNOWN時日期功能明示不可評估；DST 23/25h、日界線、A→B→A晚回覆不能覆蓋。 | V1 S03 S35；V2 S14 S15 |
| U-F06 | 日最佳／目前／相對較佳／研究常見時段／天文時間各自標示。 | C4/C5/C6 | 邊界前1分、開始、結束、結束後1分；過去時間不提示現在出發，WINDOW不標適合拍攝。  | V1 S03 S07；V2 S15 S21 S38 |
| U-F07 | 提供題材多選（同維度OR，與地區／文字AND）；只匹配已研究題材。 | C1/C2/C3 | 倒影＋日出為OR；加花蓮為AND；無結果可清除；翻譯切換不改stable ID。 先按Opportunity篩選再group Place；tw-026另一不匹配題材不外漏。 | V1 S02 S03 S09；V2 S14 S17 |
| U-F08 | 沿用第一級行政單位，跨區景點可多值且只列一次；未收錄地區有明確狀態。 | C1/C2 | TW22/JP47/US51；金門／連江有標籤；Death Valley跨州測試只在有真實紀錄時作資料測試。 registry與實際Place membership都要有來源；0 entries不能聲稱TW22/JP47/US51完成。 | V1 S03 S05 S44；V2 S14 S17 |
| U-F09 | 承襲有界面板、44px點擊區、焦點返回與選取狀態持續。 | C1/C2 | 390/360寬面板<=82dvh；多選後不關閉；X/完成/Escape/Back皆可；背景捲動位置不變。  | V1 S03 S33 S43；V2 S14 S37 |
| U-F10 | 名稱／別名／地區可搜尋；顯示地區去歧義；無結果與無資料分開。 | C1/C2/C3 | 名稱／ID各找到同紀錄；同名不同區可分辨；清除回復；語系切換不丟selection。  | V1 S03；V2 S15 S17 |
| U-F11 | 地區預設；無可信分數時禁用分數排序並解釋；距離只用有來源Place參考點。 | C3/C4/C5；分數／距離能力缺即停用 | null分數永不當0；平手stable ID；定位拒絕仍可操作；只有選距離時請求權限。 NAME/REGION穩定排序；全組缺任何可信可比分數／距離時停用，未知不當0；拒定位回REGION ASC。 | V1 S03 S32；V2 S14 S16 |
| U-F12 | stable ID收藏與V2版本化偏好；保持無定位預設與可重置。 | C3；本機版本化保存 | 收藏重載保留、取消不回復；localStorage不可用仍能瀏覽；跨國偏好互不污染。 localStorage損毀、quota、future-version、跨tab、unknown/withheld ID保留可移除；不存位置。 | V1 S03；V2 S15 |
| U-F13 | 只顯示匹配來源／時間／覆蓋的真實數值；單位與缺值可見。 | C5/C6；原生單位與interval | 0與null不同；stale／錯區／錯單位不顯示正常數值；C/F切換不改原始值。  | V1 S03 S06；V2 S15 S22 S39 |
| U-F14 | 分能力顯示；太陽計算可先做，月亮／銀河／極光等各自要W3已驗模型。 | C4/C6；Sun以外需另開模型契約 | polar day/night顯示無事件；錯IANA/未知位置無時間；Kp不等同當地極光可見機率。 Sun-only不能顯示月相、銀河或極光機率；NO_EVENT與UNKNOWN分開。 | V1 S03 S06；V2 S15 S21 S38 |
| U-F15 | W3唯一判定來源；必要失敗覆蓋quality；無校準分數顯示文字狀態。 | C5；W3擁有判定 | 高quality＋必要條件FAIL仍UNFAVORABLE；缺關鍵值NOT_EVALUABLE；UI不寫通用65/80門檻。 低分不配正向文字；高分不得救failed REQUIRED；不得在UI新設全域分數門檻。 | V1 S03 S06 S08；V2 S16 S20 S45 |
| U-F16 | 依據、判斷與未知分開；理由引用同一EvaluationResult revision與時間。 | C5/C6；理由依revision | 卡片／詳情／時間軸同一結果；UNKNOWN不出現綠色已符合；理由不可與分數衝突。  | V1 S03 S08；V2 S15 S20 |
| U-F17 | 各題材用自己的條件；倒影以光線／水面／風等已核准條件，不複製Legacy常數。 | C0/C5；W2 threshold與適用scope | 風弱但光線不足不推薦；近景不因遠山能見度不足被錯殺；所有測試綁題材contract。  | V1 S06 S08 S35；V2 S20 S23 |
| U-F18 | 先提供已研究題材與缺能力說明；雲海保留空間垂直例外，霧/haze與銀河各自驗證。 | C0/C5/C6；幾何按claim | 晨霧下午例排除、camera-in-cloud不說雲海、月光／雲／季節缺值不推銀河；不抄全域門檻。  | V1 S06 S08 S25；V2 S20 S21 |
| U-F19 | 位置角色分明；到達點與題材機位分開；未驗證／封閉路線不發Directions。 | C7；動態封閉transport尚缺 | 同氣象open/closed分數不變；closed verified目標也要禁Directions；名稱／subject不能代導航。 verified＋closed、stale、unverified、multiple routes均測；不可使用subject或map_query當Directions。 | V1 S03 S05 S26；V2 S16 S17 S28 |
| U-F20 | 一般題材可自選構圖；精確對齊／特定倒影才要幾何；不猜camera點。 | C0/C7；不需強制機位 | 普通區域條件無cameraGPS仍可獨立評估；精確alignment未知只影響該條件；required未知阻止整體FAVORABLE。  | V1 S26 S09；V2 S27 S30 |
| U-F21 | 保留warning-only；顯示範圍、來源、查核時間；不暗示替代區開放。 | C0/C7；warning不改score | 相同氣象封閉前後status/score完全相同；warning可見；禁用對應導航且理由明確。 same weather＋closure改變→相同verdict／score、不同warning／Directions；不得暗示替代區開放。 | V1 S06 S07；V2 S15 S17 S28 |
| U-F22 | 先新增獨立入口；延續locale/date/Place只在對方正式支援參數後接入。 | C8；先相對連結 | 相對URL在子目錄可達；無參數支援時不假裝已套用選取日；返回保持篩選。  | V1 S02 S12 S13；V2 S14 |
| U-F23 | 重用既有全球地圖能力，標示真正資料覆蓋／fallback／限流；不重寫一張台灣地圖。 | C8；全球coverage另owner | TW/JP/CONUS/Alaska/跨日界線pan；200但缺cells仍無資料；有界重試；空白不當0雲。  | V1 S12 S13；V2 S13 S36 |
| U-F24 | 保留分層、色階與非顏色圖例；將被驗證的呈現契約交WeatherGrid owner。 | C8；screen-space／色階 | 桌機箭頭最近距>=34px／手機>=30px（容差以繪圖bucket驗）；40/50/70%可辨；觀測不套預報配色。  | V1 S12 S41 S42；V2 S13 S36 |
| U-F25 | 顯示原生解析度、有效時間、來源與衍生限制；工程debug收合。 | C6/C8；forecast/observation/proxy | 插值不變native resolution；Himawari不得叫未來預報；LCL不叫實測雲底；缺run不寫最新模式。  | V1 S12；V2 S13 S36 S39 |
| U-F26 | 所有新增loading/error/empty/導覽／accessible name同批三語；切換不重置ID。 | C0/C1/C3/C4/C5；同時三語 | 所有狀態3語×2viewport；開著詳情切語不殘留；lang/title/ARIA同步；日期／選取不變。  | V1 S03；V2 S15 S30 |
| U-F27 | 新改資料同批三語；禁止泛題材名取代完整題材；自動完整性＋人工語意審查。 | C0/C1/C2；逐欄語意檢查，A/B/C範圍化 | 逐題材名稱／描述／條件／風險逐欄對照；任一語缺值不得退化為簡寫；保留pending事實。 保留human_signoff=PENDING；AI語意證據可支持R1 A/B，但不能冒稱人簽或GUIDE/live核准。 | V1 S09 S29；V2 S31 S17 |
| U-F28 | 基於可讀卡片的1/2/3/4欄；寬桌機四欄、手機不橫向溢位。 | C1/C5；真實集合或明示test-only | 360/390/768/1440/1536/1920寬；>=1500四欄（內容足4筆）；200%zoom可讀；無overlap。  | V1 S04；V2 S37 |
| U-F29 | 已判不適合可收合；未知／無預報獨立分組不可當無機會。 | C1/C5；無機會不等於無資料 | 全部未知時不能說今日無機會；展開顯示原計數；篩選後計數正確；鍵盤可展開。  | V1 S03 S04；V2 S14 S15 |
| U-F30 | 44px主要操作、焦點可見、Escape/返回、對話框focus trap與還原、非顏色狀態。 | C1–C9；所有控件 | Tab完整流程無陷阱；dialog僅自身可focus；關閉回觸發器；reduced-motion；正常字4.5:1。  | V1 S03 S04；V2 S14 S30 |
| U-F31 | 先做V2本機觀測草稿，保留未知與明確配對；之後才正式提交。 | C1/C2/C9草稿 | 缺GPS／EXIF仍可保存草稿；unmatched合法；手填time標來源；未呼叫POST不得顯示已提交。 沒有EXIF維持未知；unmatched可完成；GPS只是建議，零POST；觀測不改Canonical或模型。 | V1 S10 S11；V2 S14 S19 |
| U-F32 | 先定義授權、容量、格式、保存／刪除與review回執；成功必須有伺服器receipt。 | C9接收服務尚待定義 | upload失敗不顯示成功；重送不重複；撤銷／刪除可驗；模型不能把使用者描述自動當ground truth。 真實receipt、idempotency、權限／用途／刪除與失敗重試完成才稱已提交，不產生假AI判斷。 | V1 S10 S11 S25；V2 S19 |
| U-F33 | 明確狀態機；初載不閃空資料；失敗可重試；舊資料清楚標示不當新預報。 | C1/C4；network狀態與科學狀態獨立 | delayed/404/500/invalidJSON/empty及成功；可識別loading；重試只發1個active request；先前選取不洩漏。  | V1 S03；V2 S15 S46 |
| U-F34 | 研究更新／資料取得／模式發報／預報有效分開；普通畫面只保留決策必要資訊。 | C2/C4/C5/C6；四種時間不混用 | 用四個不同時間測試文案與排序；retrieved不能替代issued；過期不顯示更新完成。  | V1 S03 S12；V2 S15 S18 S39 |
| U-F35 | 有意義的入口保留；無runtime時天氣區給無資料；官方雷達先可作獨立外連。 | C8；外連／返回狀態 | TW/JP/US目的地正確、外連noopener；返回時地區／日期保留；不把雷達觀測叫預報。  | V1 S02 S03；V2 S14 S15 |
| U-F36 | 單位偏好不動原值；版本化cache與last-good只在清楚標舊資料後使用。 | C3/C4/C6；原值與cache key | 舊request晚回不可覆寫新地區；summary/detail revision不符顯同步；離線不顯新鮮綠勾。  | V1 S03；V2 S15 |
| U-F37 | 每批獨立W4 Draft；W5有意識repin，不沿用過時head或降低case gate。 | C10；完整tree與逐筆來源 | owner tree、sources與fixture相同；CI exact head與tested merge parents可證；不得把31+6當完整產品驗收。 保留157基準全部案例＋新增真實discovery；規劃文件亦改W1 tree，必須由W5明確接納。 | V1 S01；V2 S23 S24 |
| U-F38 | W1整併規格文字；W4更新現況說明；以最新access警告規則與未接live現況表達。 | C0/C10；規格優先序 | 全域搜尋不得留下access作氣象gate的V2規則；W3缺值仍fail closed；W4不以註解當能力判定。  | V1 S25；V2 S16 S28 S40 |
| U-F39 | 產品達標與發布批准分開；保留V1入口與資產，不以V2-only artifact覆蓋root。 | C10；build/public/live三Gate | 凍結release SHA/assets hash、main CI、6browser、公網manifest與rollback；merge可能觸發Pages，須預先審視。 候選local/package PASS、current-head CI、public exact artifact驗證分列；本次禁止merge/deploy。 | V1 S02 S01；V2 S24 |
| U-F40 | 依矩陣全部P0與保留P1通過；真人流程抽驗，來源與狀態可信；不建立自動新舊比較。 | C0–C10；完整產品驗收 | 3語×6viewport流程；fake/stale/missing provider負測全過；真人可找到題材、時間、風險與可用導航。 所有P0＋已接受P1三語×裝置流程達標，使用者抽樣；禁止自動V1/V2結果比較。 | V1 S25；V2 S24 S30 |


## 不能照搬的V1行為

- V1目前只有題材標籤／殘留currentTheme，沒有可操作的首頁題材篩選；V2題材多選是補完整功能，不宣稱已繼承存在的控件。
- 不移植V1科學常數、score band或access評分；以V2 approved ConditionContract為準。語系缺漏不能用generic theme替代。
- 不直接import Legacy runtime或weather JSON作V2真值；借鑑interaction和回歸案例，資料依W2/W3契約重新接線。
- 原Task U尚待核准／未開發的描述已由本次Draft狀態欄取代；不把原Roadmap當作目前GitHub現況。
