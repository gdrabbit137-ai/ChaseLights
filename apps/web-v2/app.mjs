import {LOCALES,placeId,opportunityId,linkedPlaceId,localized,safeUrl,navigationAction,geometryType,relationValue,runtimeEvaluation,associated} from "./model.mjs";
import {importV21Catalog} from "./catalog-loader.mjs";

const copy = {
"zh-TW":{subtitle:"攝影機會研究介面",language:"語言",eyebrow:"獨立 V2 測試入口",headline:"從拍攝位置，看見真正的拍攝主體",intro:"探索已匯入的攝影景點與題材、構圖關係和證據。這不是即時天氣預報。",mode:"研究／展示模式",noData:"尚未提供 V2 正式資料。未顯示任何虛構景點或預報。",hasData:"已載入 V2 研究資料；尚未連接即時判斷。",source:"資料來源",updated:"資料產製時間",loaded:"本機載入時間",none:"未提供",unknown:"未知／未提供",importHeading:"匯入 V2 研究資料",importHelp:"選取 Worker 1／2 的 V2 JSON；不會上傳至伺服器。亦可由同目錄 catalog.v2.json 自動載入。",upload:"選取 JSON",places:"景點",search:"搜尋景點或 ID",empty:"等待 V2 資料",emptyHelp:"匯入包含 places 與 opportunities 的 V2 JSON 後，才會顯示實際研究紀錄。",choose:"選擇左側景點",opportunities:"攝影題材",noneOpp:"此景點沒有已提供的 V2 題材資料。",camera:"Camera Zone · 拍攝位置",subject:"Photo Target · 被攝主體",access:"Navigation / Access · 到達參考",relation:"Camera ↔ Subject · 觀測關係",distance:"距離",azimuth:"方位角",elevation:"仰俯角",time:"季節／時段／天文幾何",timeMissing:"尚未提供可驗證的時段、太陽／月亮／銀河幾何",runtime:"目前沒有可驗證的 V2 即時評估，不提供拍攝適合度或分數。",runtimeReady:"V2 執行結果",advanced:"研究條件、未知項與證據",required:"必要條件",blocker:"直接失敗條件",quality:"品質加分條件",unknowns:"待確認",evidence:"證據來源",notTranslated:"此欄尚未提供此語言的等價敘述",directions:"導航至已驗證到達點",map:"查看暫定座標（非導航）",navPending:"尚無已驗證的到達點；不產生導航路線",footer:"ChaseLights V2 獨立測試介面。研究紀錄不等於指定日期的預報。",invalid:"無法載入 V2 JSON：",count:"個",noMatches:"沒有符合的景點",dataLabel:"V2 研究 JSON",status:"研究狀態",pageTitle:"ChaseLights V2 — 攝影機會研究",skipToContent:"跳至主要內容",languageAria:"語言選擇",provenanceAria:"資料來源與時效",placesAria:"景點清單",opportunitiesAria:"攝影題材與研究資料"},
en:{subtitle:"Photography opportunity research",language:"Language",eyebrow:"Independent V2 test entry",headline:"From camera location to photographic subject",intro:"Explore imported places, compositions, observation relationships and evidence. This is not a live weather forecast.",mode:"Research / preview mode",noData:"No official V2 dataset is available. No fabricated places or forecasts are shown.",hasData:"V2 research data loaded; live evaluation is not connected.",source:"Data source",updated:"Data generated",loaded:"Loaded locally",none:"Not provided",unknown:"Unknown / not provided",importHeading:"Import V2 research data",importHelp:"Select a Worker 1/2 V2 JSON file; it stays in your browser. An optional catalog.v2.json in this directory is loaded automatically.",upload:"Choose JSON",places:"Places",search:"Search places or IDs",empty:"Waiting for V2 data",emptyHelp:"Import V2 JSON with places and opportunities to display actual research records.",choose:"Select a place on the left",opportunities:"Photography opportunities",noneOpp:"No V2 opportunities were provided for this place.",camera:"Camera Zone · shooting area",subject:"Photo Target · subject",access:"Navigation / Access · arrival reference",relation:"Camera ↔ Subject · observation relation",distance:"Distance",azimuth:"Azimuth",elevation:"Elevation angle",time:"Season / time / celestial geometry",timeMissing:"No verified time, sun, moon or Milky Way geometry supplied",runtime:"No verifiable V2 runtime evaluation; no shooting verdict or score is displayed.",runtimeReady:"V2 runtime result",advanced:"Research conditions, unknowns and evidence",required:"Required",blocker:"Blockers",quality:"Quality factors",unknowns:"Unknowns",evidence:"Evidence sources",notTranslated:"Equivalent text for this language has not been supplied",directions:"Directions to verified arrival point",map:"View provisional coordinate (not directions)",navPending:"No verified arrival point; directions are unavailable",footer:"Independent ChaseLights V2 test interface. Research is not a date-specific forecast.",invalid:"Unable to load V2 JSON: ",count:"",noMatches:"No matching places",dataLabel:"V2 research JSON",status:"Research status",pageTitle:"ChaseLights V2 — Photography research",skipToContent:"Skip to main content",languageAria:"Language selection",provenanceAria:"Data provenance and freshness",placesAria:"Places list",opportunitiesAria:"Photography opportunities and research"},
ja:{subtitle:"撮影機会の調査ビュー",language:"言語",eyebrow:"独立した V2 テスト入口",headline:"撮影地点から被写体まで、関係を明確に",intro:"読み込んだ撮影地、構図、観測関係、根拠を確認できます。リアルタイム天気予報ではありません。",mode:"調査／プレビュー",noData:"正式な V2 データは未提供です。架空の撮影地や予報は表示しません。",hasData:"V2 調査データを読み込みました。リアルタイム判定は未接続です。",source:"データ出典",updated:"データ生成日時",loaded:"ローカル読込日時",none:"未提供",unknown:"不明／未提供",importHeading:"V2 調査データを読み込む",importHelp:"Worker 1／2 の V2 JSON を選択してください。サーバーには送信されません。同じフォルダの catalog.v2.json も自動読込できます。",upload:"JSON を選択",places:"撮影地",search:"撮影地または ID を検索",empty:"V2 データ待機中",emptyHelp:"places と opportunities を含む V2 JSON を読み込むと実際の調査記録を表示します。",choose:"左側から撮影地を選択",opportunities:"撮影機会",noneOpp:"この撮影地の V2 撮影機会は未提供です。",camera:"Camera Zone · 撮影位置",subject:"Photo Target · 被写体",access:"Navigation / Access · 到達地点",relation:"Camera ↔ Subject · 観測関係",distance:"距離",azimuth:"方位角",elevation:"仰俯角",time:"季節／時間帯／天体配置",timeMissing:"検証済みの時間帯・太陽・月・天の川の幾何情報は未提供です",runtime:"検証可能な V2 実行結果はありません。撮影可否や点数は表示しません。",runtimeReady:"V2 実行結果",advanced:"調査条件・不明点・根拠",required:"必須条件",blocker:"阻害条件",quality:"品質向上条件",unknowns:"未確認事項",evidence:"根拠資料",notTranslated:"この言語の同等の説明は未提供です",directions:"確認済み到達地点へナビ",map:"暫定座標を地図表示（ナビではありません）",navPending:"確認済み到達地点がないためナビは利用できません",footer:"ChaseLights V2 独立テスト画面。調査記録は日付指定の予報ではありません。",invalid:"V2 JSON を読み込めません：",count:"件",noMatches:"一致する撮影地はありません",dataLabel:"V2 調査 JSON",status:"調査状態",pageTitle:"ChaseLights V2 — 撮影機会の調査",skipToContent:"メインコンテンツへ移動",languageAria:"言語の選択",provenanceAria:"資料の出典と更新時刻",placesAria:"撮影地一覧",opportunitiesAria:"撮影機会と調査資料"}
};
const researchCopy={
"zh-TW":{catalog:"研究來源",imported:"研究匯入時間（不是預報有效時間）",readiness:"研究成熟度",revision:"來源版本",review:"審核狀態",schema:"資料格式版本不相容",invalid:"資料結構或語系不完整",noData:"沒有可匯入的 V2.1 題材",accessNotes:"拍攝區域與安全資訊",missingEvidence:"來源索引尚未提供公開連結"},
en:{catalog:"Research source",imported:"Research imported (not forecast valid time)",readiness:"Research readiness",revision:"Source revision",review:"Review status",schema:"Unsupported schema version",invalid:"Invalid structure or incomplete localization",noData:"No V2.1 opportunities to import",accessNotes:"Camera access and safety",missingEvidence:"Evidence index has no public URL"},
ja:{catalog:"調査資料の出典",imported:"調査取込日時（予報有効時刻ではありません）",readiness:"調査の進捗",revision:"出典リビジョン",review:"審査状況",schema:"非対応のスキーマバージョン",invalid:"構造または翻訳が不完全",noData:"読み込める V2.1 撮影機会がありません",accessNotes:"撮影区域・安全情報",missingEvidence:"証拠索引に公開URLがありません"}
};
if (LOCALES.some(l => Object.keys(copy[l]).sort().join("|") !== Object.keys(copy["zh-TW"]).sort().join("|") || Object.keys(researchCopy[l]).sort().join("|") !== Object.keys(researchCopy["zh-TW"]).sort().join("|"))) throw new Error("Incomplete locale UI dictionary");
const $ = id => document.getElementById(id);
const node = (tag, className, text) => {const e=document.createElement(tag);if(className)e.className=className;if(text!==undefined)e.textContent=String(text);return e;};
const state={locale:"zh-TW",catalog:null,selected:null,source:null,loaded:null,error:null};
try {const saved=localStorage.getItem("chaselights-v2-locale");if(LOCALES.includes(saved))state.locale=saved;}catch{}
$("language").value=state.locale;
$("language").addEventListener("change",e=>{state.locale=e.target.value;try{localStorage.setItem("chaselights-v2-locale",state.locale);}catch{}render();});
$("search").addEventListener("input",renderPlaces);
$("file").addEventListener("change",async e=>{const file=e.target.files?.[0];if(!file)return;try{useCatalog(JSON.parse(await file.text()),file.name);}catch(err){state.catalog=null;state.error=err.code||err.message;render();}});
function t(k){return copy[state.locale][k];}
function errorText(code){const x=researchCopy[state.locale];return code==="SCHEMA_MISMATCH"?x.schema:code==="NO_DATA"?x.noData:code==="INVALID_SCHEMA"?x.invalid:String(code);}
function name(r){return localized(r,"name",state.locale,true)||localized(r,"canonical_name",state.locale,true)||localized(r,"title",state.locale,true)||t("notTranslated");}
function label(r,k){return localized(r,k,state.locale,false)||t("notTranslated");}
function showDate(raw){if(!raw)return t("none");const d=new Date(raw);return Number.isNaN(d.getTime())?t("unknown"):new Intl.DateTimeFormat(state.locale,{dateStyle:"medium",timeStyle:"short"}).format(d);}
function useCatalog(data,source){const normalized=importV21Catalog(data);state.catalog=normalized;state.source=source;state.loaded=new Date().toISOString();state.selected=placeId(normalized.places[0]);state.error=null;render();}
function render(){
  document.documentElement.lang=state.locale==="zh-TW"?"zh-Hant":state.locale;
  document.title=t("pageTitle");
  $("skip-link").textContent=t("skipToContent");
  for(const [id,key] of Object.entries({"language":"languageAria","source-strip":"provenanceAria","sidebar":"placesAria","detail":"opportunitiesAria"}))$(id).setAttribute("aria-label",t(key));
  for(const [id,key] of Object.entries({"subtitle":"subtitle","language-label":"language","eyebrow":"eyebrow","headline":"headline","intro":"intro","mode":"mode","source-label":"source","updated-label":"updated","loaded-label":"loaded","import-heading":"importHeading","import-help":"importHelp","upload-label":"upload","places-heading":"places","search-label":"search","footer-copy":"footer"}))$(id).textContent=t(key);
  $("search").placeholder=t("search");
  $("data-status").textContent=state.error?t("invalid")+errorText(state.error):(state.catalog?t("hasData"):t("noData"));
  $("source-value").textContent=state.source||t("none");
  $("updated-value").textContent=showDate(state.catalog?.generated_at);
  $("loaded-value").textContent=showDate(state.loaded);
  $("place-count").textContent=(state.catalog?.places.length||0)+" "+t("count");
  renderPlaces();renderDetail();
}
function renderPlaces(){
  const list=$("places-list");list.replaceChildren();if(!state.catalog)return;
  const q=$("search").value.trim().toLocaleLowerCase();
  const matches=state.catalog.places.filter(p=>[name(p),placeId(p),p.country,p.admin1].filter(Boolean).some(v=>String(v).toLocaleLowerCase().includes(q)));
  if(!matches.length){list.append(node("p","muted",t("noMatches")));return;}
  for(const p of matches){const id=placeId(p);const b=node("button","place-button");b.type="button";b.setAttribute("aria-current",String(state.selected===id));b.append(node("strong","",name(p)),node("small","",id||t("unknown")));b.addEventListener("click",()=>{state.selected=id;renderPlaces();renderDetail();});list.append(b);}
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
  const target=$("detail");target.replaceChildren();if(!state.catalog){target.append(empty(t("empty"),t("emptyHelp")));return;}
  const c=state.catalog;const p=c.places.find(x=>placeId(x)===state.selected);
  if(!p){target.append(empty(t("choose"),""));return;}
  target.append(node("p","eyebrow",placeId(p)),node("h2","",name(p)));
  const opps=c.opportunities.filter(o=>linkedPlaceId(o)===state.selected);
  target.append(node("p","meta",t("opportunities")+": "+opps.length));
  if(!opps.length){target.append(empty(t("noneOpp"),""));return;}
  for(const opp of opps)renderOpportunity(target,opp,c,p);
}
function renderOpportunity(target,opp,c,place){
  const oid=opportunityId(opp);
  const card=node("article","opportunity");
  const top=node("div","opportunity-head");top.append(node("h3","",name(opp)),node("span","pill",t("mode")));card.append(top,node("p","meta",oid||t("unknown")));
  const rc=researchCopy[state.locale],prov=opp.provenance||{};
  card.append(node("p","meta",rc.catalog+": "+(prov.source_catalog||t("unknown"))+" · "+rc.revision+": "+(prov.source_revision||t("unknown"))));
  card.append(node("p","meta",rc.imported+": "+showDate(prov.imported_at)+" · "+rc.readiness+": "+(opp.readiness?.research_level||t("unknown"))+" · "+rc.review+": "+(prov.review_status||t("unknown"))));
  const zones=c.camera_zones.filter(z=>(opp.camera_zone_ids||[]).includes(z.camera_zone_id)||z.opportunity_id===oid);
  const subjects=c.subject_geometries.filter(s=>(opp.subject_geometry_ids||[]).includes(s.subject_geometry_id)||s.opportunity_id===oid);
  const relations=c.view_relations.filter(r=>r.opportunity_id===oid);
  const grid=node("div","context-grid");
  grid.append(infoBox(t("camera"),zones.map(z=>name(z)+(z.geometry_status==="unknown"?" ["+t("unknown")+"]":"")).join(" · ")||t("unknown")));
  grid.append(infoBox(t("subject"),subjects.map(s=>name(s)+(geometryType(s)?" ["+geometryType(s)+"]":"")).join(" · ")||t("unknown")));
  const nav=place.navigation_target||opp.navigation_target||null;
  grid.append(infoBox(t("access"),localized(nav,"label",state.locale,true)||nav?.status||t("unknown")));
  card.append(grid);
  const action=navigationAction(nav);
  if(action){const a=node("a","nav-action",t(action.kind));a.href=action.url;a.target="_blank";a.rel="noopener noreferrer";card.append(a);}
  else card.append(node("p","nav-disabled",t("navPending")));
  card.append(node("p","relation",t("relation")+": "+(relations.length?relations.map(relationText).join(" | "):t("unknown"))));
  const sky=node("p","meta",t("time")+": "+(localized(opp,"sky_geometry_summary",state.locale)||localized(opp,"season_time_summary",state.locale)||t("timeMissing")));card.append(sky);
  const evalRow=c.evaluations.find(e=>e.opportunity_id===oid);
  const runtime=runtimeEvaluation(evalRow);
  card.append(node("p",runtime?"meta":"notice",runtime?(t("runtimeReady")+": "+(localized(runtime,"verdict",state.locale)||t("unknown"))):t("runtime")));
  const details=node("details","technical");details.append(node("summary","",t("advanced")));
  const group=node("div","");
  if(zones.length){group.append(node("h4","",researchCopy[state.locale].accessNotes));const ul=node("ul");for(const z of zones)ul.append(node("li","",name(z)+": "+(localized(z,"access_notes",state.locale)||t("notTranslated"))+" · "+(localized(z,"safety_notes",state.locale)||t("notTranslated"))));group.append(ul);}
  for(const [role,title] of [["REQUIRED","required"],["BLOCKER","blocker"],["QUALITY","quality"]]){
    const items=c.conditions.filter(x=>x.opportunity_id===oid&&x.role===role);
    if(!items.length)continue;
    group.append(node("h4","",t(title)));
    const ul=node("ul");
    for(const condition of items){const li=node("li","",localized(condition,"human_description",state.locale)||label(condition,"description"));ul.append(li);}
    group.append(ul);
  }
  const unknowns=c.unknowns.filter(x=>x.opportunity_id===oid);
  if(unknowns.length){group.append(node("h4","",t("unknowns")));const ul=node("ul");for(const u of unknowns)ul.append(node("li","",localized(u,"text",state.locale)||t("notTranslated")));group.append(ul);}
  const refs=new Set([...(opp.evidence_refs||[]),...c.conditions.filter(x=>x.opportunity_id===oid).flatMap(x=>x.evidence_refs||[])]);
  const ev=c.evidence.filter(x=>refs.has(x.evidence_id)||x.opportunity_id===oid);
  if(ev.length){group.append(node("h4","",t("evidence")));const ul=node("ul");for(const item of ev){const li=node("li","",item.evidence_id+" · "+(item.source||item.title||t("unknown"))+" ");appendLink(li,item.url,item.url);if(!item.url)li.append(node("span","muted"," · "+researchCopy[state.locale].missingEvidence));ul.append(li);}group.append(ul);}
  details.append(group);card.append(details);target.append(card);
}
render();
(async()=>{try{const response=await fetch("./catalog.v2.json",{cache:"no-store"});if(response.status===404)return;if(!response.ok)throw new Error("HTTP "+response.status);useCatalog(await response.json(),"catalog.v2.json");}catch(err){state.catalog=null;state.error=err.code||err.message;render();}})();
