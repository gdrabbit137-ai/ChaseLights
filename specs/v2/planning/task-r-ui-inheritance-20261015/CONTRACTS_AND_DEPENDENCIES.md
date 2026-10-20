# W1–W5 契約、相依與整合順序

本文件為規劃；以下已存在的schemas不重建。新服務介面是待Owner定義的交付要求，並非聲稱已有API端點。

## 必要契約

| ID | 已存在來源／尚缺內容 | Owner→Consumer | 驗收／缺資料行為 |
| --- | --- | --- | --- |
| C0 研究及條件Canonical | main Opportunity v2.1、Crosswalk、Evidence Ledger、FREE_COMPOSITION/ACCESS_ADVISORY及#491政策；逐筆A/B/C審查證據仍待#493/Task Q後續 | W1規範、W2資料→W3/W4/W5 | camera/subject/relation/navigation分開；存在證據必備，選用geometry未知不阻塞普通題材；閉區不改score。C/HOLD不進research feed。 |
| C1 Place/admin index | #489 `PLACE_INDEX_CONTRACT_V0_1.md`及place-index schema；stable IDs、多值membership、三語名稱、publication | W1契約→W2→W4 | #490輸出可供研究，完整TW22/JP47/US51＋實際Place所屬來源尚缺；不解析tw-/jp-/us-猜國別。GUIDE_ELIGIBLE與RESEARCH_ONLY不同。 |
| C2 Manifest/provenance transport | #490 `data/v2/indexes/research/manifest.json`、source-lock、field-provenance、index-status、curation及canonical joins；W1需接受sidecar為一致revision的讀取契約 | W2＋W1確認→W4/W5 | manifest檔hash＋每筆commit/path/blob/revision/ID一致；原P01 #458與Batch04 #468歷史分別保留。partial fetch、tamper、跨revision混用整批可見集合失效，舊卡不冒充新資料。 |
| C3 Browse/topics/preferences/sort | #489 topic-index/local-preferences/browse-query/sort-capabilities四schema；#490 taxonomy 8 IDs、10 associations | W1→W2分類→W4；W3提供可比score能力 | OR within topic/region、AND across；先filter opp再group Place。V2 storage key `chaselights.v2.preferences.v1`；無可信score/distance停用並解釋，不當0。 |
| C4 Date/query | #489 date-query schema、local-day規則；W2 verified IANA=0；W3 resolver/result-store接線尚缺 | W1＋W2→W3→W4 | frozen UTC now→per-Place日曆日；explicit YYYY-MM-DD；DST／日界線／跨午夜；query_id/generation及artifact hash/revision一致。未知zone只阻塞time-dependent結果，不阻塞研究。 |
| C5 Evaluation/recommendation | main `evaluation-result-v0.1.schema.json`及`packages/core-v2/evaluator.py`；production result store/API location、刷新政策、UI projection及pilot核准尚缺 | W1契約／W2 approved conditions→W3唯一判定→W4 | W3提供structured state/actionability/reasons/valid window/provider&contract refs；UI不由score或單一sunset推FAVORABLE。missing/stale/wrong region/threshold null/AUTO未批→UNKNOWN/NOT_EVALUABLE。 |
| C6 天文與氣象輸入 | main solar WINDOW request/result、NWS raw source schema/adapter；其他provider與月／銀河／極光需獨立Owner契約 | W1/W3＋WeatherGrid→W4 | original units/native interval、issue/valid/retrieved/computed各自標示；NWS限真實coverage；WINDOW/RAW_ONLY不給攝影分數。forecast/observation/proxy不可混稱。 |
| C7 Navigation/access | main navigation語意與advisories；缺current route/closure/freshness連動的正式view transport與逐筆到達來源 | W1→W2→W4；W3 score獨立 | Directions僅已驗證實際到達且路線未被警告關閉；unknown/stale不推safe。provisional只可在有真實座標與契約時顯示Map，絕不升Directions；多路線不任選第一筆。 |
| C8 WeatherGrid route/layer | 既有root `weather-map-v2.html`與全球loader；app到工具的locale/place/date返回／deep-link規格未接受 | WeatherGrid owner＋W1→W4入口；W5驗收 | 先提供既有相對URL，未支援參數不偽稱同步。coverage、model/run/valid/native resolution、interpolation、429／缺tile、pan/dateline。 |
| C9 Field observation | R4.2 §14已有觀測語意；V2 DTO、backend、auth/retention/delete尚缺 | W1 DTO→W4本機草稿；W5服務＋W4提交 | 照片GPS只建議、unmatched有效、EXIF缺值不補；server receipt前只能稱本機保存。未review不當ground truth或模型校正，不能假造AI辨識結果。 |
| C10 Integration/release | main owner pins＋157 case；#488有build/release工具及267 CI；本規劃與#489/#490未被其source接受 | W5整合，各Owner交付→Owner發布核准 | 每個接受tree精確鎖定，保留原測試與新增discovery；source/code/schema/browser/package/public/live Gate分開。CI失敗不降門檻；本次無merge/deploy。 |

## 最新main政策如何套用到舊Draft

#491/#492已在main，對R1研究可採獨立AI source／crosswalk／三語語意審查，不需要所有非關鍵欄位一律人簽。#489/#490原handoff的人類簽核敘述早於新規，W1須保留最新main政策並明確區分：

- A/B：只在證據支持的R1研究範圍可准入；未知選用機位、EXIF、非核心季節不阻塞全批。未實做的AI review不能用規劃表自行認證。
- C/HOLD：主體存在未支持、來源不可驗、關鍵語意缺漏、重大矛盾、虛構合法通行等，隔離受影響claim/record，不能因湊數放行。
- human_signoff原為PENDING仍PENDING；R1許可不等於GUIDE_ELIGIBLE/live/法律保證。不要把#489 GUIDE人簽條件誤套到所有RESEARCH_ONLY，也不要擅刪正式guide Gate。
- 封閉資訊只作警告／導航限制；地區封閉不使獨立氣象判定未知或不適合。幾何僅限制真正需要它的claim。

## W5安全組合計畫（本次不執行）

1. 重新讀最新main與全部候選HEAD，不把本文件SHA當永遠最新。既有main接受#491/#492。
2. 保留#488對#486＋#487的已完成成果；#487已是#488祖先時只整合一次，不能雙重cherry-pick。#488的267項成功是其舊base/synthetic tree，需在新組合重新測。
3. 合入被獨立接受的#489共用契約，解specs/v2/README的main-policy衝突，保留#491新增政策；再納入本規劃目錄。W1整個tree重新接受，不能只pin#489而忽略新main。
4. 合入#490索引與#493審查handoff（若已接受）。兩者都改W2 tree，不可接受一個pin而遺失另一個；#494成功只涵蓋#493，**沒有**接受#490 index。
5. 對W4後續獨立PR逐筆accept；保留original P01 blob `001a3380231e3d073e900bf2b415aac7dcc5fd79`與Batch04各自commit，不把最新W2 tree commit冒充每筆original source。
6. 最新actual組合跑full CI、schema、所有Node/browser、build/runtime dependencies、public smoke範圍及Legacy隔離；不移除失敗／SKIP檢查。自動發布與合併均另由授權Gate處理。

目前可預估：#488 267 cases，若完整接受#489新增31與#490新增18且沒有新變動，discovery算術應為316；**這是計畫估算，從未宣稱316實跑通過**。W5必須按實際組合逐suite重新discovery，不用舊157或267當新上限，也不以重複schema gate灌入case數。

## 可平行與必須串行

W2行政registry/IANA補證可與W4名稱／題材／收藏平行。W3 local-day及WINDOW/raw transport、W1 C5/C7/C9界面、WeatherGrid獨立改善也可平行；各Owner路徑隔離，不在同一app.mjs同時開多個W4 branch。W4 R-W4-02→03→04同檔時串行或以先前被接受commit為base，不能盲從main覆寫。

正式推薦必須 W1契約→W2 evidence/conditions/AUTO核准→W3真實provider/result→W4呈現→W5 exact-head Gate；不可用研究完成取代這條鏈。照片提交必須先有W1 DTO＋W5真實服務，W4才能稱提交完成。任何階段缺上游時交付明確disabled/unknown與可執行負測，不造資料。
