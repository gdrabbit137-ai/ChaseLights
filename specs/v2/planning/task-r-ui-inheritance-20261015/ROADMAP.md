# 分階段 Roadmap 與驗收 Gate

沿用Task U階段方向，依#487–494實際成果調整順序。沒有承諾未驗證的日期／工時。每階段都要有可審查變更與真實驗收，不以排程存在或PR名稱當完成。

| 階段 | 具體成果／順序 | 先完成的相依 | 可平行工作 | 可測試離開條件 |
| --- | --- | --- | --- | --- |
| M0 接受現有成果 | R-W1-00/R-W5-00；重用#487首頁、#488 build，接受#489契約/#490研究索引與最新#491政策；不重寫 | 重新查HEAD、解政策及owner source-tree整合；C0–C3/C10 | W2 R1獨立review／metadata補證；W1 C5/C7/C9設計 | 每個accepted tree/hash清單、真實discovery、完整current-head CI；失敗source pin有明確owner，不降低157基準；仍Draft。 |
| M1 有用的多景點探索 | R-W4-02 → R-W4-03；真實名稱／題材多選／全文詳情／收藏／可用排序 | M0接受的W4＋W1/W2契約；逐筆A/B/C；C0–C3 | W2 registry/IANA，W3 local-day/真實provider pilot，WeatherGrid獨立改善；不在同app.mjs互撞 | 完整expected研究集合（全准才7/8）、tw-026兩題材、來源tamper負測、三語手機桌機搜尋／題材／收藏／null排序。0 live score/0 unverified Directions。**仍非V1替代品。** |
| M2 日期、行政區與可解釋時間資訊 | R-W4-04 → 05；region/date controls＋真實WINDOW/raw（可先只無資料） | W2 TW22/JP47/US51＋Place membership/IANA與W3 resolver；C4/C6 | W1/W2/W3科學pilot條件與provider、C7導航，09A DTO；三語／RWD持續 | 全registry及未收錄狀態、多選關閉／Back；目的地local日期、DST/日界線/array亂序/晚回覆；WINDOW/raw不給分數；四種時間與資料來源不混用。 |
| M3 真實攝影預報pilot | R-W4-06、C5 result store與可信條件／理由／有效時段；R-W4-07先接工具入口、合法到達另Gate | W1批准契約→W2 subject/條件/AUTO→W3真實matching provider/evaluation→W4；#467相關 | 07受管導航、08RWD深化、HWG，09A本機草稿 | 一個明確coverage/題材的真實閉環；成功＋missing/stale/錯區/錯日/threshold null/未批AUTO負測；必要失敗優先於分數；closure不改score。未覆蓋區明示無資料，不能推全球預報。 |
| M4 V1實用能力完整與回歸 | R-W4-07/08/09A/10；WeatherGrid來源／legend／pan、導航安全、實拍本機觀測；更多已驗模型逐步擴展 | 各相關契約及true source，非所有模型一次完成；完整P0＋已接受P1 | W5真實照片服務與09B可另支線 | FEATURE_MATRIX逐ID連實際tests/log/head；三語×6viewport完整旅程、無overflow／focus遺失／內容縮水。保留不支援功能清單；由使用者抽樣接受，無自動比較。 |
| M5 照片服務與正式發布準備 | 09B server receipt/review/delete；W5 independent release readiness/public candidate verification | C9真實服務、用途同意；C10 source/CI/hosting/owner approval | 已核准forecast穩定性與擴充 | 上傳／重試／receipt／刪除實測；candidate package/public exact hashes；live資料與unknown防線。**發布需要獨立核准，本規劃不部署。** |

## Gate 分層，避免新的人工卡點

研究Gate：逐筆A/B可進Research-only，C/HOLD僅影響該claim/record；沒有選用機位／EXIF不能擋整批，沒有完整registry/timezone也不能擋名稱研究探索。三語關鍵語意缺漏、來源不支持或假合法保證仍HOLD。保留human_signoff=PENDING而不冒簽。

產品Gate：Research-only、正式guide、selected-date recommendation為不同surface；要達到可取代V1，必須完成日期與真實評估旅程，不能只交M1展示頁。GUIDE與live科學／幾何／provider必要條件不得由A/B狀態取代。

整合Gate：每個Owner完整tree精確接受＋真實測試；沒有把#490 index合入的#494 157成功不能替代完整索引整合。規劃文件也改W1 tree，W5需明確接納，不能將docs blanket排除或調整gate範圍來掩蓋來源差異。

發布Gate：本機／source browser／packaged browser／current-head CI／public artifact／live capability分開。#488的267成功未代表新main、public候選或正式預報。每階段只準備Draft，合併與部署依當次授權；本Task R明確禁止。

## 建議排程與責任順序（僅計畫，未改排程）

先讓W5處理已完成成果的main-based整合與W1政策衝突；W4接續真實索引探索。W2同時補行政／時區與R1例外查核；W1/W3同時推版本化日期／runtime pilot；WeatherGrid獨立維護。W4主線02→03→04→05→06，07單純入口可提前，08每批持續，09依DTO與服務；所有同檔改動避免並發覆寫。每個等待項都有Owner與可交付輸入，不以「等待人工審核」泛稱全部停止。
