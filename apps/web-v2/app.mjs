import {LOCALES,placeId,opportunityId,linkedPlaceId,localized,safeUrl,navigationAction,geometryType,relationValue,runtimeEvaluation,associated} from "./model.mjs";
import {createCatalogState} from "./catalog-state.mjs";
import {browse,validateBrowseIndex} from "./browse-index.mjs";

const copy = {
"zh-TW":{subtitle:"攝影機會研究介面",language:"語言",eyebrow:"獨立 V2 測試入口",headline:"從景點與題材，規劃你的拍攝",intro:"探索已匯入的攝影景點與題材、構圖關係和證據。這不是即時天氣預報。",mode:"研究／展示模式",noData:"尚未提供 V2 正式資料。未顯示任何虛構景點或預報。",hasData:"已載入 V2 研究資料；尚未連接即時判斷。",source:"資料來源",updated:"資料產製時間",loaded:"本機載入時間",none:"未提供",unknown:"未知／未提供",importHeading:"匯入 V2 研究資料",importHelp:"選取 Worker 1／2 的 V2 JSON；不會上傳至伺服器。亦可由同目錄 catalog.v2.json 自動載入。",upload:"選取 JSON",places:"景點",search:"搜尋景點或 ID",empty:"等待 V2 資料",emptyHelp:"匯入包含 places 與 opportunities 的 V2 JSON 後，才會顯示實際研究紀錄。",choose:"選擇左側景點",opportunities:"攝影題材",noneOpp:"此景點沒有已提供的 V2 題材資料。",camera:"Camera Zone · 拍攝位置",subject:"Photo Target · 被攝主體",access:"Navigation / Access · 到達參考",relation:"Camera ↔ Subject · 觀測關係",distance:"距離",azimuth:"方位角",elevation:"仰俯角",time:"季節／時段／天文幾何",timeMissing:"尚未提供可驗證的時段、太陽／月亮／銀河幾何",runtime:"目前沒有可驗證的 V2 即時評估，不提供拍攝適合度或分數。",runtimeReady:"V2 執行結果",advanced:"研究條件、未知項與證據",required:"必要條件",blocker:"直接失敗條件",quality:"品質加分條件",unknowns:"待確認",evidence:"證據來源",notTranslated:"此欄尚未提供此語言的等價敘述",directions:"導航至已驗證到達點",map:"查看暫定座標（非導航）",navPending:"尚無已驗證的到達點；不產生導航路線",footer:"ChaseLights V2 獨立測試介面。研究紀錄不等於指定日期的預報。",invalid:"無法載入 V2 JSON：",count:"個",noMatches:"沒有符合的景點",dataLabel:"V2 研究 JSON",status:"研究狀態",pageTitle:"ChaseLights V2 — 攝影機會研究",skipToContent:"跳至主要內容",languageAria:"語言選擇",provenanceAria:"資料來源與時效",placesAria:"景點清單",opportunitiesAria:"攝影題材與研究資料"},
en:{subtitle:"Photography opportunity research",language:"Language",eyebrow:"Independent V2 test entry",headline:"Explore places and what to photograph",intro:"Explore imported places, compositions, observation relationships and evidence. This is not a live weather forecast.",mode:"Research / preview mode",noData:"No official V2 dataset is available. No fabricated places or forecasts are shown.",hasData:"V2 research data loaded; live evaluation is not connected.",source:"Data source",updated:"Data generated",loaded:"Loaded locally",none:"Not provided",unknown:"Unknown / not provided",importHeading:"Import V2 research data",importHelp:"Select a Worker 1/2 V2 JSON file; it stays in your browser. An optional catalog.v2.json in this directory is loaded automatically.",upload:"Choose JSON",places:"Places",search:"Search places or IDs",empty:"Waiting for V2 data",emptyHelp:"Import V2 JSON with places and opportunities to display actual research records.",choose:"Select a place on the left",opportunities:"Photography opportunities",noneOpp:"No V2 opportunities were provided for this place.",camera:"Camera Zone · shooting area",subject:"Photo Target · subject",access:"Navigation / Access · arrival reference",relation:"Camera ↔ Subject · observation relation",distance:"Distance",azimuth:"Azimuth",elevation:"Elevation angle",time:"Season / time / celestial geometry",timeMissing:"No verified time, sun, moon or Milky Way geometry supplied",runtime:"No verifiable V2 runtime evaluation; no shooting verdict or score is displayed.",runtimeReady:"V2 runtime result",advanced:"Research conditions, unknowns and evidence",required:"Required",blocker:"Blockers",quality:"Quality factors",unknowns:"Unknowns",evidence:"Evidence sources",notTranslated:"Equivalent text for this language has not been supplied",directions:"Directions to verified arrival point",map:"View provisional coordinate (not directions)",navPending:"No verified arrival point; directions are unavailable",footer:"Independent ChaseLights V2 test interface. Research is not a date-specific forecast.",invalid:"Unable to load V2 JSON: ",count:"",noMatches:"No matching places",dataLabel:"V2 research JSON",status:"Research status",pageTitle:"ChaseLights V2 — Photography research",skipToContent:"Skip to main content",languageAria:"Language selection",provenanceAria:"Data provenance and freshness",placesAria:"Places list",opportunitiesAria:"Photography opportunities and research"},
ja:{subtitle:"撮影機会の調査ビュー",language:"言語",eyebrow:"独立した V2 テスト入口",headline:"撮影地と題材から、撮影を考える",intro:"読み込んだ撮影地、構図、観測関係、根拠を確認できます。リアルタイム天気予報ではありません。",mode:"調査／プレビュー",noData:"正式な V2 データは未提供です。架空の撮影地や予報は表示しません。",hasData:"V2 調査データを読み込みました。リアルタイム判定は未接続です。",source:"データ出典",updated:"データ生成日時",loaded:"ローカル読込日時",none:"未提供",unknown:"不明／未提供",importHeading:"V2 調査データを読み込む",importHelp:"Worker 1／2 の V2 JSON を選択してください。サーバーには送信されません。同じフォルダの catalog.v2.json も自動読込できます。",upload:"JSON を選択",places:"撮影地",search:"撮影地または ID を検索",empty:"V2 データ待機中",emptyHelp:"places と opportunities を含む V2 JSON を読み込むと実際の調査記録を表示します。",choose:"左側から撮影地を選択",opportunities:"撮影機会",noneOpp:"この撮影地の V2 撮影機会は未提供です。",camera:"Camera Zone · 撮影位置",subject:"Photo Target · 被写体",access:"Navigation / Access · 到達地点",relation:"Camera ↔ Subject · 観測関係",distance:"距離",azimuth:"方位角",elevation:"仰俯角",time:"季節／時間帯／天体配置",timeMissing:"検証済みの時間帯・太陽・月・天の川の幾何情報は未提供です",runtime:"検証可能な V2 実行結果はありません。撮影可否や点数は表示しません。",runtimeReady:"V2 実行結果",advanced:"調査条件・不明点・根拠",required:"必須条件",blocker:"阻害条件",quality:"品質向上条件",unknowns:"未確認事項",evidence:"根拠資料",notTranslated:"この言語の同等の説明は未提供です",directions:"確認済み到達地点へナビ",map:"暫定座標を地図表示（ナビではありません）",navPending:"確認済み到達地点がないためナビは利用できません",footer:"ChaseLights V2 独立テスト画面。調査記録は日付指定の予報ではありません。",invalid:"V2 JSON を読み込めません：",count:"件",noMatches:"一致する撮影地はありません",dataLabel:"V2 調査 JSON",status:"調査状態",pageTitle:"ChaseLights V2 — 撮影機会の調査",skipToContent:"メインコンテンツへ移動",languageAria:"言語の選択",provenanceAria:"資料の出典と更新時刻",placesAria:"撮影地一覧",opportunitiesAria:"撮影機会と調査資料"}
};
const homeCopy = {
"zh-TW":{subtitle:"攝影預報與拍攝題材",eyebrow:"拍攝前，先了解可能性",headline:"攝影預報",intro:"查看拍攝預報，或探索景點與拍攝題材。",pageTitle:"ChaseLights V2 — 攝影預報",dateStatus:"日期尚未選擇；指定日期預報尚未接線。",forecastStatus:"目前尚無可用的攝影預報",forecastHelp:"你仍可查看現有研究資料，了解拍攝題材與需要留意的條件。",browseResearch:"查看景點與拍攝題材",closeResearch:"關閉研究瀏覽",researchHeading:"景點與拍攝題材",researchScope:"研究資料，非指定日期預報。",toolsHeading:"資料工具",sourceHeading:"資料來源與進階資訊",provenanceAria:"資料來源與進階資訊",loading:"正在載入景點資料…",unavailable:"景點資料尚未提供，請稍後重試。",loadError:"暫時無法載入資料，請重試。",invalidData:"資料結構或語系不完整，無法使用這份資料。請重試或選取其他檔案。",emptyData:"目前尚無可瀏覽的景點資料。",readyData:"景點研究資料已載入。",retry:"重試載入",reload:"重新載入景點資料",clearSearch:"清除搜尋",placeNameMissing:"景點名稱尚未提供",placeIdentity:"景點識別碼",advanced:"資料來源與進階資訊",importHeading:"匯入研究資料",importHelp:"選取 V2 研究 JSON；資料留在此瀏覽器，不會上傳。匯入資料不會啟用攝影預報。",framingHint:"請先確認現場通行與安全，再於確認開放的範圍自行取景；研究範圍不是指定機位。"},
en:{subtitle:"Photography forecasts and subjects",eyebrow:"Explore possibilities before your shoot",headline:"Photography forecast",intro:"Check photography forecasts or explore places and subjects to photograph.",pageTitle:"ChaseLights V2 — Photography forecast",dateStatus:"No date selected; date-specific forecasts are not connected yet.",forecastStatus:"No photography forecast is available yet.",forecastHelp:"You can still browse existing research to understand subjects and the conditions to consider.",browseResearch:"Explore places and photography subjects",closeResearch:"Close research browser",researchHeading:"Places and photography subjects",researchScope:"Research information, not a date-specific forecast.",toolsHeading:"Data tools",sourceHeading:"Data sources and advanced information",provenanceAria:"Data sources and advanced information",loading:"Loading place information…",unavailable:"Place information is not available yet. Please retry later.",loadError:"Information could not be loaded. Please try again.",invalidData:"Invalid structure or incomplete localization. This information cannot be used. Retry or choose another file.",emptyData:"There is no place information to browse yet.",readyData:"Place research information loaded.",retry:"Retry loading",reload:"Reload place information",clearSearch:"Clear search",placeNameMissing:"Place name not provided",placeIdentity:"Place identifier",advanced:"Data sources and advanced information",importHeading:"Import research information",importHelp:"Choose a V2 research JSON file. It stays in this browser and is not uploaded. Importing does not enable photography forecasts.",framingHint:"Check local access and safety first, then choose your composition within confirmed open areas. A researched area is not a prescribed tripod position."},
ja:{subtitle:"撮影予報と撮影の題材",eyebrow:"撮影の前に、可能性を確認",headline:"撮影予報",intro:"撮影予報を確認したり、撮影地と題材を調べたりできます。",pageTitle:"ChaseLights V2 — 撮影予報",dateStatus:"日付は未選択です。指定日の予報はまだ接続されていません。",forecastStatus:"撮影条件の予報はまだ利用できません。",forecastHelp:"既存の調査情報から、撮影の題材と確認すべき条件を調べられます。",browseResearch:"撮影地と撮影の題材を見る",closeResearch:"調査情報を閉じる",researchHeading:"撮影地と撮影の題材",researchScope:"調査情報であり、指定日の予報ではありません。",toolsHeading:"データツール",sourceHeading:"データの出典と詳細情報",provenanceAria:"データの出典と詳細情報",loading:"撮影地の情報を読み込んでいます…",unavailable:"撮影地の情報はまだ提供されていません。後でもう一度お試しください。",loadError:"情報を読み込めませんでした。もう一度お試しください。",invalidData:"構造または翻訳が不完全なため、この情報は使用できません。再試行するか、別のファイルを選択してください。",emptyData:"閲覧できる撮影地の情報はまだありません。",readyData:"撮影地の調査情報を読み込みました。",retry:"読み込みを再試行",reload:"撮影地の情報を再読み込み",clearSearch:"検索をクリア",placeNameMissing:"撮影地の名称は未提供です",placeIdentity:"撮影地の識別子",advanced:"データの出典と詳細情報",importHeading:"調査情報を読み込む",importHelp:"V2 調査 JSON を選択してください。情報はこのブラウザー内に留まり、アップロードされません。読み込んでも撮影予報は有効になりません。",framingHint:"まず現地の通行条件と安全を確認し、開放が確認できた範囲で構図を選んでください。調査上の範囲は指定の三脚位置ではありません。"}
};
for (const locale of LOCALES) Object.assign(copy[locale], homeCopy[locale]);
const browseCopy={
"zh-TW":{openFilters:"搜尋與題材篩選",closeFilters:"關閉篩選",topicHeading:"攝影題材（多選，符合任一項）",clearFilters:"清除全部篩選",resultCount:"符合景點",researchOnly:"僅供研究 · 尚無攝影預報",unknownMetadata:"行政區與當地時區尚未核實",indexInvalid:"研究索引無法驗證；請勿將資料視為攝影預報。",unclassified:"題材分類尚未提供",indexCommit:"研究索引 commit SHA",canonicalPin:"Canonical 來源 commit／Git Blob",sortStatus:"依景點名稱排序；行政區、分數與距離排序尚無可信資料"},
en:{openFilters:"Search and topic filters",closeFilters:"Close filters",topicHeading:"Photography topics (match any selected)",clearFilters:"Clear all filters",resultCount:"Matching places",researchOnly:"Research only · No photography forecast",unknownMetadata:"Region and local time zone are unverified",indexInvalid:"Research index could not be verified; no photography forecast is available.",unclassified:"Topic classification unavailable",indexCommit:"Research index commit SHA",canonicalPin:"Canonical source commit / Git blob",sortStatus:"Sorted by place name; verified region, score and distance sorting unavailable"},
ja:{openFilters:"検索と題材フィルター",closeFilters:"フィルターを閉じる",topicHeading:"撮影題材（複数選択、いずれかに一致）",clearFilters:"すべての条件を解除",resultCount:"一致する撮影地",researchOnly:"調査資料のみ · 撮影予報は未提供",unknownMetadata:"行政区分と現地の時間帯は未確認",indexInvalid:"調査索引を検証できません。撮影予報として利用できません。",unclassified:"題材の分類は未提供",indexCommit:"調査索引の commit SHA",canonicalPin:"Canonical 出典 commit／Git Blob",sortStatus:"撮影地名順。確認済みの行政区分・点数・距離による並べ替えは未提供"}
};
for(const locale of LOCALES)Object.assign(copy[locale],browseCopy[locale]);
const researchCopy={
"zh-TW":{sourceCommit:"來源 commit SHA（資料聲明）",catalog:"研究來源",imported:"研究匯入時間（不是預報有效時間）",readiness:"研究成熟度",revision:"來源版本",review:"審核狀態",schema:"資料格式版本不相容",invalid:"資料結構或語系不完整",noData:"沒有可匯入的 V2.1 題材",accessNotes:"拍攝區域與安全資訊",missingEvidence:"來源索引尚未提供公開連結",framingHint:"攝影師可在開放且安全的範圍自行選擇構圖；研究中的拍攝範圍不是指定機位。",conditionsMain:"需要留意的環境與天文條件（非即時判定）",risksMain:"已知限制與風險",unknownMain:"尚待核實",evidenceMain:"研究證據索引",evidenceItems:"筆",seeDetails:"請展開查核來源",technicalGeometry:"拍攝範圍、被攝主體及觀測幾何（研究參考）",riskNotProvided:"尚無可核實的安全資訊，請現場查核"},
en:{sourceCommit:"Source commit SHA (declared by data)",catalog:"Research source",imported:"Research imported (not forecast valid time)",readiness:"Research readiness",revision:"Source revision",review:"Review status",schema:"Unsupported schema version",invalid:"Invalid structure or incomplete localization",noData:"No V2.1 opportunities to import",accessNotes:"Camera access and safety",missingEvidence:"Evidence index has no public URL",framingHint:"Choose your own composition within open, safe areas; a researched camera area is not a prescribed tripod position.",conditionsMain:"Weather and astronomy requirements (not a live assessment)",risksMain:"Known restrictions and risks",unknownMain:"Still unverified",evidenceMain:"Research evidence references",evidenceItems:"entries",seeDetails:"Expand to inspect sources",technicalGeometry:"Camera area, subject and observation geometry (research reference)",riskNotProvided:"Verified safety information is unavailable; check local access"},
ja:{sourceCommit:"出典 commit SHA（データの申告）",catalog:"調査資料の出典",imported:"調査取込日時（予報有効時刻ではありません）",readiness:"調査の進捗",revision:"出典リビジョン",review:"審査状況",schema:"非対応のスキーマバージョン",invalid:"構造または翻訳が不完全",noData:"読み込める V2.1 撮影機会がありません",accessNotes:"撮影区域・安全情報",missingEvidence:"証拠索引に公開URLがありません",framingHint:"開放され安全な範囲で構図は撮影者が選べます。調査上の撮影範囲は指定された三脚位置ではありません。",conditionsMain:"気象・天文上の条件（現在の判定ではありません）",risksMain:"既知の制限と危険",unknownMain:"未確認事項",evidenceMain:"調査根拠の参照",evidenceItems:"件",seeDetails:"展開して出典を確認",technicalGeometry:"撮影範囲・被写体・観測幾何（調査上の参考）",riskNotProvided:"確認済みの安全情報はありません。現地の立入条件を確認してください"}
};
if (LOCALES.some(l => Object.keys(copy[l]).sort().join("|") !== Object.keys(copy["zh-TW"]).sort().join("|") || Object.keys(researchCopy[l]).sort().join("|") !== Object.keys(researchCopy["zh-TW"]).sort().join("|"))) throw new Error("Incomplete locale UI dictionary");
const $ = id => document.getElementById(id);
const node = (tag, className, text) => {const e=document.createElement(tag);if(className)e.className=className;if(text!==undefined)e.textContent=String(text);return e;};
const state={locale:"zh-TW",catalog:null,selected:null,source:null,loaded:null,status:"loading"};
let researchIndex=null,indexInvalid=false;
const selectedTopics=new Set();
async function sha256(raw){const bytes=new TextEncoder().encode(raw);return [...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('');}
const catalogState=createCatalogState({onChange:data=>{Object.assign(state,data);if(data.status==='ready'&&!data.verifiedBundle)selectedTopics.clear();render();},
  verifyDefault:async raw=>(await sha256(raw))==='f31392087b043e975abcd95a7da45a9bfebf5f513364d7de126c7e75dafe51e8'});
try {const saved=localStorage.getItem("chaselights-v2-locale");if(LOCALES.includes(saved))state.locale=saved;}catch{}
$("language").value=state.locale;
$("language").addEventListener("change",e=>{state.locale=e.target.value;try{localStorage.setItem("chaselights-v2-locale",state.locale);}catch{}render();});
$("search").addEventListener("input",()=>{renderPlaces();renderDetail();});
$("clear-search").addEventListener("click",()=>{$("search").value="";renderPlaces();renderDetail();$("search").focus();});
$("clear-filters").addEventListener("click",()=>{$("search").value="";selectedTopics.clear();render();});
function filterPanel(open){$("filter-panel").hidden=!open;$("open-filters").setAttribute("aria-expanded",String(open));if(open)$("search").focus();else $("open-filters").focus();}
$("open-filters").addEventListener("click",()=>filterPanel(true));
$("close-filters").addEventListener("click",()=>filterPanel(false));
const mobile=matchMedia('(max-width:700px)');
function updateFilterPanel(){if(!mobile.matches){$("filter-panel").hidden=false;$("open-filters").setAttribute("aria-expanded","true");}else if(!$("open-filters").matches(':focus')){$("filter-panel").hidden=true;$("open-filters").setAttribute("aria-expanded","false");}}
mobile.addEventListener('change',updateFilterPanel);updateFilterPanel();
function openResearch(){
  $("research-browser").hidden=false;
  $("browse-research").setAttribute("aria-expanded","true");
  $("research-heading").focus();
}
$("browse-research").addEventListener("click",openResearch);
$("close-research").addEventListener("click",()=>{
  $("research-browser").hidden=true;
  $("browse-research").setAttribute("aria-expanded","false");
  $("browse-research").focus();
});
$("retry").addEventListener("click",()=>{void catalogState.load();});
$("file").addEventListener("change",e=>{
  const file=e.target.files?.[0];if(!file)return;
  // Expose the genuine import state/result, including failed local reads.
  $("research-browser").hidden=false;
  $("browse-research").setAttribute("aria-expanded","true");
  void catalogState.importFile(file);
  e.target.value=""; // Allow retrying the same file after failure.
});
function t(k){return copy[state.locale][k];}
function operationalText(){return t({loading:"loading",unavailable:"unavailable",error:"loadError",invalid:"invalidData",empty:"emptyData",ready:"readyData"}[state.status]);}
function placeName(p){
  const supplied=localized(p,"name",state.locale,true)||localized(p,"canonical_name",state.locale,true);
  return supplied && supplied!==placeId(p) ? supplied : t("placeNameMissing");
}
function name(r){return localized(r,"name",state.locale,true)||localized(r,"canonical_name",state.locale,true)||localized(r,"title",state.locale,true)||t("notTranslated");}
function label(r,k){return localized(r,k,state.locale,false)||t("notTranslated");}
function showDate(raw){if(!raw)return t("none");const d=new Date(raw);return Number.isNaN(d.getTime())?t("unknown"):new Intl.DateTimeFormat(state.locale,{dateStyle:"medium",timeStyle:"short"}).format(d);}
function render(){
  const restoreResearchFocus=!state.catalog && ($("detail").contains(document.activeElement)||$("places-list").contains(document.activeElement));
  document.documentElement.lang=state.locale==="zh-TW"?"zh-Hant":state.locale;
  document.title=t("pageTitle");
  $("skip-link").textContent=t("skipToContent");
  for(const [id,key] of Object.entries({"language":"languageAria","source-strip":"provenanceAria","sidebar":"placesAria","detail":"opportunitiesAria"}))$(id).setAttribute("aria-label",t(key));
  for(const [id,key] of Object.entries({"subtitle":"subtitle","language-label":"language","eyebrow":"eyebrow","headline":"headline","intro":"intro","source-label":"source","updated-label":"updated","loaded-label":"loaded","import-heading":"importHeading","import-help":"importHelp","upload-label":"upload","places-heading":"places","search-label":"search","footer-copy":"footer"}))$(id).textContent=t(key);
  $("search").placeholder=t("search");
  for(const [id,key] of Object.entries({"date-status":"dateStatus","forecast-status":"forecastStatus","forecast-help":"forecastHelp","browse-research":"browseResearch","close-research":"closeResearch","research-heading":"researchHeading","research-scope":"researchScope","tools-heading":"toolsHeading","source-heading":"sourceHeading","clear-search":"clearSearch"}))$(id).textContent=t(key);
  for(const [id,key] of Object.entries({"open-filters":"openFilters","close-filters":"closeFilters","topic-heading":"topicHeading","clear-filters":"clearFilters","sort-status":"sortStatus"}))$(id).textContent=t(key);
  $("data-status").textContent=operationalText();
  $("data-state").setAttribute("data-status",state.status);
  $("retry").textContent=t(state.status==="ready"?"reload":"retry");
  $("retry").disabled=state.status==="loading";
  $("search").disabled=!state.catalog;
  $("detail").setAttribute("aria-busy",String(state.status==="loading"));
  $("source-value").textContent=state.source||t("none");
  $("source-commit-label").textContent=state.catalog?.metadata.source_index_commit_sha?t("indexCommit"):researchCopy[state.locale].sourceCommit;
  $("source-commit-value").textContent=state.catalog?.metadata.source_index_commit_sha||state.catalog?.metadata.source_commit_sha||t("unknown");
  $("updated-value").textContent=showDate(state.catalog?.generated_at);
  $("loaded-value").textContent=showDate(state.loaded);
  renderTopics();
  renderPlaces();renderDetail();
  if(restoreResearchFocus && !$("research-browser").hidden)$("research-heading").focus();
}
function activeIndex(){
  if(!researchIndex || !state.catalog || !state.verifiedBundle)return null;
  try{return validateBrowseIndex(researchIndex,state.catalog);}catch{return null;}
}
function renderTopics(){
  const target=$("topic-options");target.replaceChildren();
  const index=activeIndex();
  $("topic-filters").hidden=!index;
  if(!index)return;
  for(const topic of index.topic_index.topics){
    const label=node("label","topic-option");const input=node("input");input.type="checkbox";input.value=topic.topic_id;input.checked=selectedTopics.has(topic.topic_id);
    input.addEventListener("change",()=>{if(input.checked)selectedTopics.add(topic.topic_id);else selectedTopics.delete(topic.topic_id);renderPlaces();renderDetail();});
    label.append(input,node("span","",topic.name_i18n[state.locale]));target.append(label);
  }
}
function matchingRows(){
  if(!state.catalog)return [];
  const index=activeIndex();
  if(index)return browse(index,state.catalog,{search:$("search").value,topicIds:[...selectedTopics],locale:state.locale});
  if(state.catalog.metadata.source_index_commit_sha && state.verifiedBundle)return [];
  const q=$("search").value.trim().normalize('NFKC').toLocaleLowerCase();
  if(selectedTopics.size)return [];
  return state.catalog.places.filter(p=>[placeName(p),placeId(p),...LOCALES.map(l=>localized(p,"name",l,true))]
    .filter(Boolean).some(v=>String(v).normalize('NFKC').toLocaleLowerCase().includes(q)))
    .map(p=>({place:p,opportunities:state.catalog.opportunities.filter(o=>linkedPlaceId(o)===placeId(p))}));
}
function renderPlaces(){
  const focusedId=document.activeElement?.getAttribute?.("data-place-id");
  const list=$("places-list");list.replaceChildren();$("clear-search").hidden=true;
  const matches=matchingRows();$("place-count").textContent=t("resultCount")+": "+matches.length;
  if(state.verifiedBundle && state.catalog?.metadata.source_index_commit_sha && !activeIndex())indexInvalid=true;
  if(!state.catalog)return;
  if(!matches.length){list.append(node("p","muted",indexInvalid?t("indexInvalid"):t("noMatches")));$("clear-search").hidden=!$("search").value && !selectedTopics.size;return;}
  for(const {place:p,opportunities} of matches){const id=placeId(p);const b=node("button","place-button");b.type="button";b.setAttribute("data-place-id",id);b.setAttribute("aria-current",String(state.selected===id));b.append(node("strong","",placeName(p)),node("small","",id+" · "+t("opportunities")+": "+opportunities.length+" · "+t("researchOnly")));b.addEventListener("click",()=>{catalogState.select(id);});list.append(b);if(id===focusedId)b.focus();}
}
function empty(title,description){const box=node("div","empty");box.append(node("div","glyph","◉"),node("h2","",title),node("p","muted",description));return box;}
function infoBox(title,value){const dl=node("dl","context");dl.append(node("dt","",title),node("dd","",value||t("unknown")));return dl;}
function appendLink(parent,url,text){const safe=safeUrl(url);if(!safe)return;const a=node("a","",text);a.href=safe;a.target="_blank";a.rel="noopener noreferrer";parent.append(a);}
function relationText(r){
  if(!r)return t("unknown");
  const parts=[[t("distance"),relationValue(r.distance,r.distance_unit)],[t("azimuth"),relationValue(r.azimuth,r.azimuth_unit)],[t("elevation"),relationValue(r.elevation_angle,r.elevation_angle_unit)]];
  return parts.map(([k,v])=>k+": "+(v||t("unknown"))).join(" · ");
}
function renderDetail(){
  const target=$("detail");
  const openIds=[...target.querySelectorAll("details[open]")].map(d=>d.getAttribute("data-opportunity-id"));
  const focused=document.activeElement;
  const focusId=target.contains(focused) ? focused?.parentElement?.getAttribute("data-opportunity-id") : null;
  target.replaceChildren();if(!state.catalog)return;
  const c=state.catalog;const match=matchingRows().find(x=>placeId(x.place)===state.selected);
  if(!match){target.append(empty(t("noMatches"),""));return;}
  const p=match.place;
  target.append(node("h2","",placeName(p)));
  target.append(node("p","meta",t("unknownMetadata")));
  const opps=match.opportunities;
  target.append(node("p","meta",t("opportunities")+": "+opps.length));
  if(!opps.length){target.append(empty(t("noneOpp"),""));return;}
  for(const opp of opps)renderOpportunity(target,opp,c,p);
  for(const details of target.querySelectorAll("details")){
    const id=details.getAttribute("data-opportunity-id");
    details.open=openIds.includes(id);
    if(id===focusId)details.querySelector("summary").focus();
  }
}
function renderOpportunity(target,opp,c,place){
  const oid=opportunityId(opp);
  const card=node("article","opportunity");
  const top=node("div","opportunity-head");top.append(node("h3","",name(opp)),node("span","pill",t("researchOnly")));card.append(top);
  const topics=activeIndex()?.topic_index.opportunity_topics.find(x=>x.opportunity_id===oid)?.topic_ids||[];
  if(topics.length)card.append(node("p","meta",topics.map(id=>activeIndex().topic_index.topics.find(x=>x.topic_id===id)?.name_i18n[state.locale]).join(" · ")));
  else card.append(node("p","meta",t("unclassified")));
  const rc=researchCopy[state.locale],prov=opp.provenance||{};
  const description=localized(opp,"description",state.locale);
  if(description)card.append(node("p","opportunity-description",description));
  card.append(node("p","framing-note",t("framingHint")));
  const zones=c.camera_zones.filter(z=>(opp.camera_zone_ids||[]).includes(z.camera_zone_id)||z.opportunity_id===oid);
  const subjects=c.subject_geometries.filter(x=>(opp.subject_geometry_ids||[]).includes(x.subject_geometry_id)||x.opportunity_id===oid);
  const relations=c.view_relations.filter(r=>r.opportunity_id===oid);
  const allConditions=c.conditions.filter(x=>x.opportunity_id===oid && x.domain!=="ACCESS_SAFETY");
  const accessAdvisories=(c.access_advisories||[]).filter(x=>x.opportunity_id===oid);
  const unknowns=c.unknowns.filter(x=>x.opportunity_id===oid);
  const refs=new Set([...(opp.evidence_refs||[]),...allConditions.flatMap(x=>x.evidence_refs||[])]);
  const ev=c.evidence.filter(x=>refs.has(x.evidence_id)||x.opportunity_id===oid);

  // Decision-first layout: research conditions are not current weather observations.
  const decision=node("section","decision-core");
  decision.append(node("p","meta",t("time")+": "+(localized(opp,"sky_geometry_summary",state.locale)||localized(opp,"season_time_summary",state.locale)||t("timeMissing"))));
  decision.append(node("h4","",rc.conditionsMain));
  // Site access/closure is advisory-only; never render it as a required
  // photographic condition, blocker or a reason to change the weather verdict.
  for(const [role,title] of [["REQUIRED","required"],["QUALITY","quality"]]){
    const items=allConditions.filter(x=>x.role===role);
    if(!items.length)continue;
    decision.append(node("h5","",t(title)));
    const ul=node("ul");
    for(const condition of items)ul.append(node("li","",localized(condition,"human_description",state.locale)||label(condition,"description")));
    decision.append(ul);
  }
  // True photographic blockers remain separate from independently sourced
  // area/road/viewpoint closure and lawful-entry warnings.
  const photoBlockers=allConditions.filter(x=>x.role==="BLOCKER");
  card.append(decision);
  if(photoBlockers.length){
    const risk=node("section","decision-risks");
    risk.append(node("h4","",t("blocker")));
    const ul=node("ul");
    for(const item of photoBlockers)ul.append(node("li","",localized(item,"human_description",state.locale)||label(item,"description")));
    risk.append(ul);card.append(risk);
  }
  const access=node("section","access-advisories");
  access.setAttribute("role","note");
  access.append(node("h4","",rc.accessNotes));
  const accessItems=[
    ...accessAdvisories.map(x=>localized(x,"human_description",state.locale)||label(x,"description")),
    ...zones.flatMap(x=>[localized(x,"access_notes",state.locale),localized(x,"safety_notes",state.locale)]).filter(Boolean)
  ];
  if(accessItems.length){
    const ul=node("ul");for(const item of [...new Set(accessItems)])ul.append(node("li","",item));access.append(ul);
  }else access.append(node("p","muted",rc.riskNotProvided));
  card.append(access);
  if(unknowns.length){const unknown=node("section","decision-unknowns");unknown.append(node("h4","",rc.unknownMain));const ul=node("ul");for(const x of unknowns)ul.append(node("li","",localized(x,"text",state.locale)||t("notTranslated")));unknown.append(ul);card.append(unknown);}


  // Arrival navigation is distinct from camera context and the photographed subject.
  const nav=place.navigation_target||opp.navigation_target||null;
  const action=navigationAction(nav);
  if(action&&action.kind==="directions"){const a=node("a","nav-action",t("directions"));a.href=action.url;a.target="_blank";a.rel="noopener noreferrer";card.append(a);}
  else card.append(node("p","nav-disabled",t("navPending")));
  const evalRow=c.evaluations.find(e=>e.opportunity_id===oid);
  const runtime=runtimeEvaluation(evalRow);
  card.append(node("p",runtime?"meta":"notice",runtime?(t("runtimeReady")+": "+(localized(runtime,"verdict",state.locale)||t("unknown"))):t("runtime")));

  // Geometric/camera research stays available, but never implies a mandatory viewpoint.
  const details=node("details","technical");details.setAttribute("data-opportunity-id",oid);details.append(node("summary","",t("advanced")));
  details.append(node("p","meta",t("placeIdentity")+": "+placeId(place)),node("p","meta",oid));
  details.append(node("p","meta",rc.catalog+": "+(prov.source_catalog||t("unknown"))+" · "+rc.revision+": "+(prov.source_revision||t("unknown"))));
  const pin=c.metadata.source_pins?.[oid];
  if(pin)details.append(node("p","meta",t("canonicalPin")+": "+pin.source_commit_sha+" / "+pin.source_blob_sha));
  details.append(node("p","meta",rc.imported+": "+showDate(prov.imported_at)+" · "+rc.readiness+": "+(opp.readiness?.research_level||t("unknown"))+" · "+rc.review+": "+(prov.review_status||t("unknown"))));

  const group=node("div","");
  group.append(node("h4","",rc.technicalGeometry));
  const grid=node("div","context-grid");
  grid.append(infoBox(t("camera"),zones.map(z=>name(z)+(z.geometry_status==="unknown"?" ["+t("unknown")+"]":"")).join(" · ")||t("unknown")));
  grid.append(infoBox(t("subject"),subjects.map(x=>name(x)+(geometryType(x)?" ["+geometryType(x)+"]":"")).join(" · ")||t("unknown")));
  grid.append(infoBox(t("access"),localized(nav,"label",state.locale,true)||nav?.status||t("unknown")));
  group.append(grid);
  group.append(node("p","relation",t("relation")+": "+(relations.length?relations.map(relationText).join(" | "):t("unknown"))));
  if(accessAdvisories.length){
    group.append(node("h4","",rc.accessNotes));
    const ul=node("ul");
    for(const warning of accessAdvisories)ul.append(node("li","",localized(warning,"human_description",state.locale)||t("notTranslated")));
    group.append(ul);
  }
  if(zones.length){group.append(node("h4","",rc.accessNotes));const ul=node("ul");for(const z of zones)ul.append(node("li","",name(z)+": "+(localized(z,"access_notes",state.locale)||t("notTranslated"))+" · "+(localized(z,"safety_notes",state.locale)||t("notTranslated"))));group.append(ul);}
  for(const [role,title] of [["REQUIRED","required"],["BLOCKER","blocker"],["QUALITY","quality"]]){
    const items=allConditions.filter(x=>x.role===role);
    if(!items.length)continue;
    group.append(node("h4","",t(title)));
    const ul=node("ul");
    for(const condition of items)ul.append(node("li","",localized(condition,"human_description",state.locale)||label(condition,"description")));
    group.append(ul);
  }
  if(unknowns.length){group.append(node("h4","",t("unknowns")));const ul=node("ul");for(const x of unknowns)ul.append(node("li","",localized(x,"text",state.locale)||t("notTranslated")));group.append(ul);}
  if(ev.length){group.append(node("h4","",t("evidence")));const ul=node("ul");for(const item of ev){const li=node("li","",item.evidence_id+" · "+(item.source||item.title||t("unknown"))+" ");appendLink(li,item.url,item.url);if(!item.url)li.append(node("span","muted"," · "+rc.missingEvidence));ul.append(li);}group.append(ul);}
  details.append(group);card.append(details);target.append(card);
}
render();
void catalogState.load();
// The bundled W2 index has a fixed byte digest. A missing or changed index
// cannot silently classify research as a recommendation.
void (async()=>{try{
  const response=await fetch('./browse-index.v2.json',{cache:'no-store'});if(!response.ok)throw new Error('index HTTP');
  const raw=await response.text();const digest=await sha256(raw);
  if(digest!=='bda316d5cfcf4cc945dc15202d1570d5e45503e88ef9bb43d4c5824ba7e55dac')throw new Error('index digest');
  researchIndex=JSON.parse(raw);indexInvalid=false;render();
}catch{researchIndex=null;indexInvalid=true;render();}})();
