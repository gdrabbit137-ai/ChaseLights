# ChaseLights 產品藍圖（PRODUCT_BLUEPRINT）

版本：v1.0（2026-11-05）｜授權：owner 已將產品定義（UI／原則／規範／語意）全權交付 AI 端。
本文件是所有 agent（RD／reviewer／PM）的產品依據；reviewer 巡檢以本文件對照審查。
與既有 spec 衝突時：`RESEARCH_EVIDENCE_SPEC_R4_2.md`（證據層）與 `NAVIGATION_SPEC_R4_2.md`（導航層）仍為資料層最高依據，本文件主管「產品呈現與語意」。

---

## 1. 產品定位與目標使用者

### 1.1 定位
ChaseLights 是風景攝影師的「拍攝決策工具」。它回答一個問題：

> 「今天／明天，值不值得出門？幾點到哪個景點？」

不是天氣預報站、不是景點介紹網、不是相簿平台。每一個畫面都必須直接服務「去不去／幾點去」這個決策。

### 1.2 目標使用者
- 風景攝影師（業餘到 semi-pro），事前規劃與當下決斷並用。
- 核心使用情境：睡前的明日規劃、清晨的臨場判斷、半夜確認「今晚還要不要等」。
- 行動裝置是第一現場工具：390px 可讀性是驗收標準。

### 1.3 產品原則（全部 UI/資料呈現共通）
1. **誠實優先**：資料不足就說不足，永不假裝。fallback 必須標示；未知傳播為 unknown，不猜測。
2. **使用者視角**：每個指標附攝影師語意的解釋（這個數字對拍攝代表什麼），不只給數字。
3. **一源一語義**：一個結論只有一個資料源（verdict source），卡片、modal、題材評估頁對同一欄位不得各說各話。卡片是 modal 的摘要，modal 只加深、不得與卡片矛盾。
4. **Fail-closed**：資料缺失、源失敗、無法評估時一律呈現誠實的空狀態或 unknown，絕不靜默用舊資料或相似源頂替。
5. **內部狀態不外洩**：provisional 標題、pipeline 標籤、rule ID、threshold 原始值、證據等級不進一般 UI（見 §3.3）。
6. **資料庫完整 ≠ UI 完整**：顯示的是「攝影師決策所需的投影」（R4.2 §7.2）。

---

## 2. 各表面規範

### 2.1 首頁卡片（repo 根目錄 index.html + assets/app.js）
- **第一眼結論先行**：卡片主列必須是攝影師語意的結論（最佳題材＋時間），表格/數字在後。
- **資訊密度**：一卡 = 景點名、地區標籤、最佳題材＋建議時段、最關鍵的一二個條件訊號（factor row）、必要的天文/暗空資訊。其餘進 modal。
- **去噪（state-row 規則）**：
  - 卡片不重複頁首已呈現的資訊：不做 per-card 時區標籤（頁首時鐘是唯一源）；
  - 主體句不回聲景點名（render 時剝離前綴景點名，最長名優先，僅完整名稱全等比對）；
  - 通用狀態列（「預報狀態：✓符合」）在常態下省略，只在需要解釋的狀態（未符／未評估／資料缺失）顯示，並帶 §4 的口語理由。
- **深夜救援（owner ruling）**：
  - 所選日主網格 0 張可用卡 → 退回明天的建議（同一 verdict 源），每卡加「明天」badge，顯眼橫幅說明今日時段已結束並提供回到今天的方式；絕不把明天的卡偽裝成今天的。
  - 1–4 張（SPARSE_MAIN_THRESHOLD）→ 攤平單列表（按符合時數排序、地理 tiebreak）＋橫幅「今日接近尾聲，以下為剩餘的建議時段」；高於門檻恢復地區分組。
  - 明天也空 → 誠實說「今日與明日目前均無符合時段」，不顯示空格。
  - 四種情境都要測：sparse／normal／today-0-tomorrow-has／both-zero。

### 2.2 Modal
- 位置：卡片與 modal 同源同日期語意；modal 只增加深度（逐時段狀態、條件明細、季節、拍攝位置、成立/加分/不利條件）。
- Modal 摘要列若顯示 generic 不可用訊息而卡片顯示 viable 題材，表示 modal 資料查找漏了 V2 源——必須 fallback 到卡片用的同一源，兩者不得並存矛盾。
- 「下一個符合時段」必須以 render 當下 wall-clock（景點當地時區）重新錨定：過濾已過時段，退回下一個未來日列；過去時段絕不寫「還有 N 小時」，寫「下一個符合時段：明天 05:00」。日期格式用頁首慣例（11/05），不用 ISO。
- 語言切換時，已開啟的 modal 立即以新語言重繪。

### 2.3 題材評估頁（assets/genre-eval.js）
- 用途：單一景點全部已查證題材的「條件是否達標」逐日/逐時段評估（GUIDANCE-only，不評分宣稱）。
- 規範：
  - 只顯示已逐點查證的題材；未查證研究線索不得出現（R4.2 §1）。
  - 每列 = 時段 + 狀態 + 一句攝影師語意的理由（達標也給簡短理由：以什麼關鍵條件成立）。
  - 頁面橫幅固定聲明：「顯示攝影條件是否達標，供拍攝前評估參考。」
  - 與首頁卡片共用同一 evaluation bundle 源；此頁不是第二套評分。

### 2.4 WeatherGrid 五區（weather-map.html）
- **唯一一頁**：repo 根目錄 `weather-map.html`。區卡：tw / jp / us / ak / hi。
  - US 僅本本土；ak、hi 是獨立 frame；hi 目前無收錄景點 → 誠實空狀態。
- **相機收束**：切區與初始載入時以 `fitBounds` 對齊該區 bbox，並以 maxBounds＋bounded minZoom＋適度 maxZoom 鎖定；資料 bbox 以外的鄰國不得佔據主要視野。
  - 相機邏輯在 `assets/weather-map-regions.js` 純函式 + `applyCameraLimits()`；驗收用 static grep＋region 測試，不在 shell 載 bundle 驗。
  - `cameraMinZoom` 必須是「每區固定值」（fitZoom − margin），不得相對於當前 zoom。
  - 切區前先清上區的 `setMaxBounds(null)/setMinZoom(null)/setMaxZoom(null)`，再 fit；resize 用 preserveCamera。
  - `setMaxBounds` 會把視窗整體夾進界內：maxBounds 必須由「fit 後視窗外擴（每邊 ~25% span）」推導，不得貼 raw bbox（否則 fit 相機被再夾、邊緣裁切）。
- **來源可用性（兩層規則）**：全球源（GFS/ICON/CAMS）須完整覆蓋 bbox 才提供（fetch window 是建置期選擇——加寬窗口，不藏源）；區域機關產品（CWA WRF、JMA MSM、Himawari、VIIRS）只要該區有產品即列為可選，只在自身產品域內繪製、域外誠實留白＋QC 註記。無 bundle 的區域顯示誠實空狀態。只用免費源。
- **圖層語意**：下拉選單標籤是乾淨的單一圖層名（zh-TW/en/ja）；「霞光參考」等用途註記放展開的圖層詳情面板。
- **風向圖層**：環向資料用 HSL 色輪（hue＝風角），永不用單調色階；加淡流線箭頭（指向下風＝來向 +180°），<~0.5 m/s 不顯示，390px 密度自適應。所有源的所有 wind_direction 圖層箭頭為必備。
- **縫合政策（Windy 參考）**：一個圖層一幀只渲染一個產品的完整格網（bilinear 到連續場），不做跨模型空間拼接。縫的處理優先序：(1) 加寬全球源窗口讓整個相機範圍單一真源；(2) 提供單源顯示模式；(3) 最後才是值域調和（跨縫 gradient、加寬 feather）——純 alpha feather 永遠蓋不住模式值與解析度不連續。
- **JMA 邊界禁令**：絕不跨越 120.06°E / 22.45°N 空間拼接。
- **渲染依賴外部資料時**：bundle fetch window 必須超出 bbox 至少相機 maxBounds padding——0.5° 邊距的 bundle 會讓 maxBounds 環完全無資料，fill 靜默不畫（模組正確、測試綠也會出空白地圖）。驗證要讀 bundle 的 grid min/max 經緯度對比 cameraBounds，不能只看 JS。
- **預渲染 PNG**：色階邏輯唯一實作在 `assets/weather-map-palette.js`（前端與 `scripts/weathergrid_png_prerender.mjs` 共用——兩套色階數學必漂移，結構性禁令）。前端以 manifest 存在＋版本＋源一致＋frame 有效為閘，任何不符退回 live JSON（`?nopng=1` 為 A/B 旁路）。
- **深連結（CL-WG-19）**：`weather-map.html` 支援 URL 參數驅動初始狀態（卡片頁深連結）：`?region=` 初始區域（覆寫 localStorage 記憶；無參數用上次瀏覽區域，皆無預設 tw）、`&spot=` 景點 ID、`&layer=` 圖層 ID（無 layer 用 region 預設主圖層）、`&focus=lat,lon,zoom` 相機（無 focus 且有 spot 時以景點為中心、依區 bbox 尺度自適應 fit，zoom 約 9–11）、`&subject=` 題材 genre → 相關性映射選圖層（映射表為純函式 `assets/weather-map-deeplink.js`＋測試；無法映射退預設圖層）。任何非法參數 fail-closed 退預設、不報錯；切區寫 localStorage、URL 同步一律 `history.replaceState`（不污染瀏覽歷史）。

### 2.5 地區 bbox 表（常數表，可擴充）
- 每區固定 lat/lon bbox，大小 = 該區天氣播報雲量的範圍，且必須包含該區全部收錄景點（驗證時逐點檢查）。
- bbox 是常數表值，不動態計算；新增區域的 `<source>_<region>` bundle 是資料工作流變更，需 owner 點頭；UI 端只能先顯示誠實空狀態。

---

## 3. 語義決策總帳

### 3.1 時間窗定義（權威值，不得另立口語模板數字）
- **夜景（night_sky／spec:night）**：太陽仰角 ≤ −6°（民用暮光界線，civil darkness）為夜景題材的時間窗必要條件。夜間題材（如銀河）另加天文黑暗叢集（astronomical_darkness＋月照六 metric）。`city_night` 是城市人工光影題材，不受天文黑暗約束（現行語意保留）。
- **日出行窗（sunrise_window）**：日出前後的霞光窗（含日出時刻）。
- **日落窗（sunset_window）**：日落前後至太陽沒入。
- **霞光（golden_hour）**：太陽仰角低角的暖光窗（golden_hour_window）。
- **藍調（blue_hour_city）**：日沒後天空仍亮、城市燈光已起的藍調窗（blue_hour_window）。
- 時間敏感題材（夜/日出/日落/霞光/季節）的判斷契約**必須**帶時間窗條件——缺少時間窗的夜間題材會把白天時段判為「最佳拍攝時段」（11:00–15:00 事故），這是紅線。
- 現行錯置 5 筆（tw-027-P02、tw-035-P05、tw-036-P02、tw-038-P02、tw-082-P06）依 `TIME_SPECIALIZATION_PROPOSAL.md` §3，待 owner 裁定後修正；修復前評估照現行契約呈現。

### 3.2 時區慣例
- 頁面級時鐘與 generated-at 時間戳：**GMT+8 樣式**（如 `GMT+8 14:30`），永不用 raw UTC。單一慣例全站一致。
- 拍攝時段（適合時間、下一個符合時段、天窗）：**景點當地時區**，並標示當地時區。卡片不做 per-card 時區標籤（頁首是唯一源）。

### 3.3 fallback 政策
- **英文名未審**：en/ja 名稱欄若只是 zh-TW 字串複本 → 視為 UNREVIEWED，繼續顯示 zh-TW 名稱（不硬譯），但標點與句構 locale 一致（en 用半形冒號與英文句構；永遠不把 opportunity_id 當名稱；ja 必須是自然日文、零簡體字）。
- **Generated-at 時間戳**一律頁面 GMT+8 慣例。
- **導航**：navigation_target 只有 `verified` 才產生導航 URL；provisional/needs_review 只顯示待確認（不發 URL）；絕不用 map_query 或景點名建構導航（NAVIGATION_SPEC）。
- **資料源降級**：任何降級必須標示（誠實降級標籤）；沒有標示的靜默 fallback 是缺陷。

### 3.4 誠實規則
- **Provisional 不進 UI**：內部 provisional/研究狀態標籤不得出現在一般介面；未決維度若必須露出，明確指出是哪一維（「最佳季節尚無足夠證據」），不用「待氣候驗證」這種混淆存在性與狀態的泛用標籤。
- **not_evaluatable 語義**：機會存在已查證但當日無法有效評估時，不與可操作推薦並列湊數；顯示誠實的「尚無本日評估」＋§4 口語理由。存在性查證不受其他維度未知連坐降級。
- **混合源標示**：任何顯示值標示資料來源；跨源混合（如不同模型的值在同一幀）必須標示或依 §2.4 縫合政策單源化。
- **未實作功能傳播 unknown**：月出月落分離等未實作項目 → 顯示 unknown，不猜。

---

## 4. 不適合（不符）理由規範（新需求 CL-UI-26）

攝影師看到的每個「不符／未符」判定必須帶一句**短口語理由**，不得只給裸狀態。格式：題材名＋「不符合：」＋原因短句（zh-TW/en/ja 三語等義）。

### 4.1 口語理由映射表（逐失敗指標）

| 失敗指標 | zh-TW | 語意 |
|---|---|---|
| precipitation（降水超過門檻） | 下大雨視線不清 | 降水直接遮蔽視線 |
| visibility / 能見度低（大霧） | 大霧看不到 | 低視程，看不到目標 |
| aod_550nm（氣溶膠超標） | 霧霾嚴重看不清 | 大氣混濁，遠景模糊 |
| cloud_cover（雲況不符：需開天但全陰/需低雲但無雲遮景） | 天空雲況不對，缺少需要的雲 | 依題材語意 |
| cloud_cover_low（V2 低雲遮蔽） | 低雲太厚，山頭沒入雲中 | 低雲淹沒山頭，主體不可見 |
| wind_speed（反射/靜水面題材超標） | 風太大，水面不平 | 反射破碎 |
| astronomical_darkness／夜窗失敗 | 現在不是夜間（還沒暗到／已經天亮） | 時間窗外 |
| sunrise/sunset/golden/blue 窗外 | 已過（未到）拍攝時間窗 | 時間窗外 |
| RH925/850・LCL（雲海失敗：LCL 高於視點） | 雲層太高，看不到雲海 | LCL > DEM−200 |
| 雲海：LCL 遠低於視點 | 雲層在腳下太低，山頭沒入雲中 | LCL ≪ 視點 |
| moon_altitude／月照（銀河受月光干擾） | 月光太亮，銀河不明顯 | 月相/月高干擾 |
| water_surface_state = NO_SOURCE | 水面狀態無法評估 | 源缺失 → fail-closed |

「山頭沒入雲中」在 cloud_cover_low 與雲海 LCL 行都出現，但語義不衝突：cloud_cover_low 是低雲自下而上淹沒主體（低雲量失敗指標），LCL 雲海行是視點高於雲層頂而山頭被埋（雲海失敗指標）——同一畫面結果、不同失敗指標，機械映射各自取自其指標。

規則：
1. 一個判定一個主因短句（取第一個失敗的關鍵指標），不堆疊列全部。
2. 理由必須可由評估器的實際失敗指標**機械映射**（查此表），不得人工文案覆寫。
3. 表中沒有的指標 → 用「條件尚未達標」並開 ticket 擴表；不得即興發明理由文案。
4. 資料缺失（源失敗）與條件不符是**不同語意**：缺失走「無法評估」路線（§3.4），不走「不符合」。

---

## 5. CI／測試鐵律

1. **Cache-bust 釘值**：任何改動有 stamp 的資產（`weather-map.js`、`weather-map-regions.js`、`weather-map.css` 等）必須**同一 commit** 內 bump `weather-map.html` 的 `?v=bclwgNN`（per-file、單調遞增），並同步 `test_weathergrid_ui_polish.py` 的釘值。不 bump = 部署後快取客戶端看不到修復；漂移的釘值 = CAMS contract-tests 每次推 push 都紅。
2. **測試釘值同步**：pin-test 樹中釘到舊檔案字串的測試，在同一 ticket 同步（缺少同步紅 CI）。
3. **Schedule 路徑紅燈必查**：schedule 紅但 push 綠 = 兩條程式路徑分歧（unpack 的 heredoc 終結符、只在單一路徑存在的 fixture 等），不是 flaky——同一 workflow 同一 step 跨路徑行為不同必須在該 ticket 內修齊，不得以 pristine-main waiver 永久豁免。
4. 重複紅的 main workflow（連續 push 同一工作流失敗）不是可接受的常態：waiver 只蓋一次 push，下一張 CI 衛生 ticket 修根因。
5. Pages 建置可能落後排程 WeatherGrid workflow 排隊 15+ 分鐘：診斷「部署不見」前先查 GitHub API 的 queued 狀態。

---

## 6. 待決事項與建議

| # | 項目 | 建議 |
|---|---|---|
| 1 | **風向粒子動畫** | ✅ 已實作（CL-DATA-08＋CL-WG-20）：GFS bundle 攜 10m/925/850/700 hPa u/v 向量分量；風向圖層詳情面板提供可開關的粒子流線動畫（單源 u/v 驅動、中性白拖尾、390px 自適應密度、預設關閉、離開圖層即停）。`wind_direction_10m_deg` 隨 u/v 上線重回圖層選單（B169 曾隱藏）。 |
| 2 | **瓦片第二階段** | 預渲染 PNG 已過第一階段；瓦片化（deep-zoom）待 PNG 幀數與載入資料量成長到痛點再開工，避免過早抽象。 |
| 3 | **TIME_SPECIALIZATION 錯置 5 筆** | 見 §3.1；待 owner 逐筆裁定後以語意修正執行（parity gate 豁免＋revision note）。 |
| 4 | **evaluations-details 以 place_id 命名導致兩組座標共用 place_id 互相覆蓋**（2 個 city_night 明細遺失） | 已列 backlog：先修命名方案，再排查「modal 列消失」。 |
| 5 | **22 個 city_night 契約缺時間窗** | 已常態化施工（CL-UI-25 項目 4）：22 份 city_night 契約補 −6° 民用暮光時間窗，與評估層閘門同源。 |
| 6 | **Wind u/v 以外的動畫原語**（如海浪流向） | 與 #1 同一資料層 ticket 類型：先定義 bundle 欄位，再 ticket UI。 |

---

## 7. 導覽與資訊架構（CL-DOC-02）

### 7.1 無 hub 主頁
- 卡片頁（`index.html`）即產品首頁/中樞，不另設 hub 主頁。
- 全站統一常駐導覽列，主項目＝**卡片**（首頁）、**天氣圖**（WeatherGrid）；其餘頁面（題材評估、實拍驗證）收入「更多工具」折疊選單。實用性考量，降級但不移除。

### 7.2 跨頁區域脈絡
- region（tw/jp/us/ak/hi）經 URL `?region=` ＋ localStorage **雙軌攜帶**：看某區卡片切到天氣圖，天氣圖落在同區。
- URL 可分享、重新載入不失脈絡；寫入用 `replaceState`，不污染瀏覽歷史。

### 7.3 深連結契約
- 卡片頁的天氣類按鈕（雷達/天氣預報類）指向 WeatherGrid 深連結，帶 `region/spot/layer/subject/focus`。
- 圖層依景點**當下最佳題材**相關性映射：霧→低雲、霧霾→AOD、夜景→夜間雲圖等；相機涵蓋景點＋拍攝範圍。

### 7.4 連貫性原則
- 任何跨頁切換不得讓使用者重新選一次已選過的東西（區域/日期/語言）。
- 每頁的返回路徑保留原狀態。

### 7.5 導覽列實作規範
- 各頁導覽列使用**同一組 DOM/樣式**；active 態標示當前頁。
- 390px 摺疊為漢堡/底部列（依現有樣式系統擇一）。

---

## 附：本藍圖的更新規則
- 本文件由 manager 維護；語意/規範變更先改此文件，RD 實作對照此版本。
- 變更需在 git 歷史留下理由（commit message 引 ticket ID）；重大口味級選擇仍由 owner 最終裁定。
