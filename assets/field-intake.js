(function(){
"use strict";
const CATALOG_URL="./runtime_catalog_v004_r4_2.json";
const DRAFT_SCHEMA="field-observation-draft-r4.2-1";
const EXIF_PARSER="exifr@7.1.3";
const REVIEW_KM=5;
const LANGS=["zh-TW","en","ja"];
const L={
"zh-TW":{
back:"← ChaseLights",title:"📷 實拍驗證",lead:"選擇實拍照片，確認拍攝地點與實際看到的景象。照片只會在你的裝置上讀取，不會上傳。",language_label:"語言",local_badge:"照片留在本機",
step_photo:"1. 選擇照片",photo_help:"支援 JPEG / HEIC / HEIF。系統會嘗試讀取拍攝時間、GPS 與相機資訊，缺少的資料會清楚標示。",choose_photos:"選擇一張或多張實拍照片",photo_local:"原始照片不會傳到 ChaseLights",preparing:"正在準備照片資訊解析與景點資料…",
step_data:"2. 資料使用設定",consent_model:"在下載紀錄中標記：我同意這筆觀測可供後續模型驗證。這不會自動上傳資料。",consent_gps:"在下載紀錄中保留照片的精確 GPS；預設不保留。",data_boundary_short:"目前流程只會在瀏覽器中整理資料並下載到你的裝置，不會建立伺服器紀錄。",
step_review:"3. 確認實拍內容",review_help:"逐張確認照片資訊、拍攝景點、想驗證的題材，以及現場是否真的成立。GPS 只會提供候選建議，不會自動確認景點。",download_all:"下載全部驗證紀錄",no_photos:"尚未選擇照片。",
what_happens:"下載後會發生什麼？",boundary_photo:"原始照片仍留在你的裝置，不會上傳。",boundary_record:"你會下載一份結構化驗證紀錄；這份紀錄仍需後續人工確認或提交。",boundary_truth:"景點配對與你填寫的觀測結果，都不會自動改變 ChaseLights 的評分、導航位置或研究資料。",
ready:"已就緒：可搜尋 {n} 個景點。照片只在本機解析。",ready_no_exif:"景點資料已載入，但 EXIF 解析器無法載入；系統不會改用上傳式解析。",catalog_error:"景點資料載入失敗：{e}",parsing:"正在本機解析 {n} 張照片…",done:"完成。本機已讀取可用的照片資訊；照片仍未上傳。",partial:"完成，但有 {n} 張照片無法完整讀取 EXIF。缺少資料會維持未知；照片仍未上傳。",
download_one:"下載這張驗證紀錄",capture:"拍攝時間",gps:"GPS（只在本機顯示）",camera:"相機",lens:"鏡頭 / 焦距",found:"已讀取",missing:"未讀取到",no_tz:"EXIF 沒有時區",parse_problem:"這張照片的 EXIF 無法完整讀取；缺少欄位會保持未知。",
capture_help:"如果拍攝時間缺少或需要修正，可由你手動補充。",capture_manual:"補充／修正拍攝時間（選填）",
place:"拍攝景點",place_help:"搜尋景點名稱、ID 或地區。GPS 候選只是建議，只有你明確選擇後才會完成配對。",search:"搜尋景點名稱、ID 或地區…",search_hint:"輸入至少 1 個字元開始搜尋。",close_results:"關閉搜尋結果",no_match:"找不到符合的景點；可換關鍵字或保留「尚未配對」。",unmatched:"尚未配對",unmatched_meta:"可繼續下載紀錄，之後再人工確認。",clear:"取消配對",
gps_suggestion:"GPS 建議候選",confirm:"確認為這個景點",near:"照片 GPS 距離候選拍攝位置約 {d}。仍需由你確認。",far:"照片 GPS 距離最近候選約 {d}，距離較遠。不會自動配對。",gps_none:"照片有 GPS，但目前沒有可用的研究景點候選。",gps_missing:"照片沒有可讀取的 GPS；請搜尋景點，或保留尚未配對。",
selected_suggestion:"你已明確確認 GPS 建議景點。",selected_manual:"你已手動選擇景點。",selected_override:"你選擇了不同於 GPS 建議的景點。",
subject:"要驗證的題材／機會",subject_help:"如果這次本來就是要驗證某個已研究題材，可在這裡選擇；不確定時可以留空。",subject_empty:"不確定／未指定",
outcome:"現場結果",outcome_empty:"尚未填寫",held:"有成立／有看到",partial_outcome:"部分成立",failed:"沒有成立",uncertain:"無法確定",
reason:"主要未成立原因（選填）",reason_ph:"例如：低雲遮住山頭、風太大無法形成倒影…",note:"補充備註（選填）",note_ph:"可記錄現場狀況、構圖位置或其他之後回看會有幫助的資訊。",export_note:"下載的紀錄仍需後續人工確認；不會因為下載就自動改變模型或研究結論。",limit:"顯示前 {n} 個符合結果；可輸入更多字縮小範圍。"
},
"en":{
back:"← ChaseLights",title:"📷 Field validation",lead:"Choose field photos, confirm where they were taken, and record what you actually saw. Photos are read only on your device and are not uploaded.",language_label:"Language",local_badge:"Photos stay on device",
step_photo:"1. Choose photos",photo_help:"JPEG / HEIC / HEIF are supported. ChaseLights will try to read capture time, GPS, and camera details and clearly mark anything missing.",choose_photos:"Choose one or more field photos",photo_local:"Original photos are not sent to ChaseLights",preparing:"Preparing photo metadata and place data…",
step_data:"2. Data-use settings",consent_model:"Mark in the downloaded record that I consent to this observation being used for later model validation. Nothing is uploaded automatically.",consent_gps:"Keep the photo's precise GPS in the downloaded record; it is omitted by default.",data_boundary_short:"This flow only organizes data in your browser and downloads it to your device. It does not create a server record.",
step_review:"3. Confirm what you observed",review_help:"For each photo, confirm metadata, shooting place, intended subject, and whether it actually held. GPS only suggests candidates; it never confirms a place automatically.",download_all:"Download all validation records",no_photos:"No photos selected yet.",
what_happens:"What happens after download?",boundary_photo:"The original photo stays on your device and is not uploaded.",boundary_record:"You download a structured validation record that still needs later human review or submission.",boundary_truth:"Place matching and your observation do not automatically change ChaseLights scoring, navigation locations, or research data.",
ready:"Ready: {n} places can be searched. Photos are parsed locally only.",ready_no_exif:"Place data loaded, but the EXIF parser is unavailable. ChaseLights will not fall back to an upload-based parser.",catalog_error:"Place data failed to load: {e}",parsing:"Reading {n} photo(s) locally…",done:"Done. Available photo metadata was read locally; photos were not uploaded.",partial:"Done, but EXIF could not be fully read from {n} photo(s). Missing fields remain unknown; photos were not uploaded.",
download_one:"Download this validation record",capture:"Capture time",gps:"GPS (shown locally only)",camera:"Camera",lens:"Lens / focal length",found:"Found",missing:"Not found",no_tz:"EXIF has no timezone",parse_problem:"EXIF could not be fully read from this photo. Missing fields remain unknown.",
capture_help:"If capture time is missing or needs correction, you can explicitly add a value.",capture_manual:"Add / correct capture time (optional)",
place:"Shooting place",place_help:"Search by place name, ID, or area. A GPS candidate is only a suggestion; the place is associated only after you explicitly choose it.",search:"Search place name, ID, or area…",search_hint:"Type at least 1 character to search.",close_results:"Close search results",no_match:"No matching place. Try another term or leave the observation unmatched.",unmatched:"Unmatched",unmatched_meta:"You can still download the record and confirm the place later.",clear:"Clear match",
gps_suggestion:"GPS suggested candidate",confirm:"Confirm this place",near:"The photo GPS is about {d} from this candidate shooting area. You still need to confirm it.",far:"The nearest candidate is about {d} from the photo GPS, which is relatively far. It will not be matched automatically.",gps_none:"The photo has GPS, but no researched place candidate is available.",gps_missing:"No readable GPS was found. Search for a place or leave it unmatched.",
selected_suggestion:"You explicitly confirmed the GPS-suggested place.",selected_manual:"You selected the place manually.",selected_override:"You selected a different place from the GPS suggestion.",
subject:"Subject / opportunity to validate",subject_help:"If this trip was intended to validate a researched photography opportunity, select it here. Leave it blank if unsure.",subject_empty:"Unsure / not specified",
outcome:"What happened in the field?",outcome_empty:"Not filled in",held:"Held / observed",partial_outcome:"Partly held",failed:"Did not hold",uncertain:"Cannot determine",
reason:"Main reason it did not hold (optional)",reason_ph:"For example: low cloud covered the ridge, wind was too strong for reflections…",note:"Additional note (optional)",note_ph:"Record field conditions, composition position, or anything useful for later review.",export_note:"The downloaded record still needs later human review. Downloading it does not automatically change the model or research conclusions.",limit:"Showing the first {n} matches. Type more to narrow the results."
},
"ja":{
back:"← ChaseLights",title:"📷 実写検証",lead:"実際に撮影した写真を選び、撮影場所と現地で見えた状況を確認します。写真は端末内でのみ読み取り、アップロードしません。",language_label:"言語",local_badge:"写真は端末内のみ",
step_photo:"1. 写真を選ぶ",photo_help:"JPEG / HEIC / HEIF に対応。撮影時刻、GPS、カメラ情報を読み取り、取得できない項目は明確に表示します。",choose_photos:"実写写真を1枚以上選ぶ",photo_local:"元の写真は ChaseLights に送信されません",preparing:"写真情報とスポットデータを準備中…",
step_data:"2. データ利用設定",consent_model:"ダウンロード記録に、この観測を今後のモデル検証に利用してよいことを記録します。データは自動送信されません。",consent_gps:"写真の正確な GPS をダウンロード記録に残します。初期状態では保存しません。",data_boundary_short:"現在の流れはブラウザ内で情報を整理し端末へダウンロードするだけで、サーバー記録は作成しません。",
step_review:"3. 実際の状況を確認",review_help:"写真ごとに情報、撮影場所、検証したかったテーマ、現地で成立したかを確認します。GPS は候補を提案するだけで、場所を自動確定しません。",download_all:"すべての検証記録をダウンロード",no_photos:"まだ写真が選択されていません。",
what_happens:"ダウンロード後はどうなる？",boundary_photo:"元の写真は端末内に残り、アップロードされません。",boundary_record:"構造化された検証記録を端末へダウンロードし、後で人が確認・提出できます。",boundary_truth:"スポットの関連付けや入力した観測結果だけで、ChaseLights の評価・ナビ位置・研究データが自動変更されることはありません。",
ready:"準備完了：{n} 件のスポットを検索できます。写真は端末内でのみ解析します。",ready_no_exif:"スポットデータは読み込みましたが EXIF 解析器を利用できません。アップロード型の解析へ切り替えることはありません。",catalog_error:"スポットデータの読み込みに失敗しました：{e}",parsing:"{n} 枚の写真を端末内で解析中…",done:"完了しました。取得できる写真情報を端末内で読み取りました。写真はアップロードされていません。",partial:"完了しましたが、{n} 枚で EXIF を完全に読み取れませんでした。欠落項目は不明のままです。",
download_one:"この検証記録をダウンロード",capture:"撮影時刻",gps:"GPS（端末内表示のみ）",camera:"カメラ",lens:"レンズ / 焦点距離",found:"取得済み",missing:"取得できません",no_tz:"EXIF にタイムゾーンなし",parse_problem:"この写真の EXIF を完全に読み取れませんでした。欠落項目は不明のままです。",
capture_help:"撮影時刻が欠落している、または修正が必要な場合だけ手動で補足できます。",capture_manual:"撮影時刻を補足／修正（任意）",
place:"撮影スポット",place_help:"スポット名、ID、地域で検索できます。GPS 候補は提案にすぎず、明示的に選択した場合だけ関連付けられます。",search:"スポット名、ID、地域を検索…",search_hint:"1文字以上入力すると検索します。",close_results:"検索結果を閉じる",no_match:"一致するスポットがありません。別の語句で検索するか、未関連付けのままにできます。",unmatched:"未関連付け",unmatched_meta:"このまま記録をダウンロードし、後で場所を確認できます。",clear:"関連付けを解除",
gps_suggestion:"GPS の候補",confirm:"このスポットを確認",near:"写真 GPS から候補の撮影位置まで約 {d} です。関連付けにはあなたの確認が必要です。",far:"写真 GPS から最寄り候補まで約 {d} と離れています。自動関連付けはしません。",gps_none:"写真に GPS はありますが、利用できる調査済みスポット候補がありません。",gps_missing:"写真から GPS を読み取れません。スポットを検索するか、未関連付けのままにしてください。",
selected_suggestion:"GPS 候補を明示的に確認しました。",selected_manual:"スポットを手動で選択しました。",selected_override:"GPS 候補とは別のスポットを選択しました。",
subject:"検証したいテーマ／撮影機会",subject_help:"今回の撮影が調査済みの撮影機会を検証する目的なら選択してください。不明なら空欄のままで構いません。",subject_empty:"不明／未指定",
outcome:"現地でどうだった？",outcome_empty:"未入力",held:"成立した／見えた",partial_outcome:"一部成立",failed:"成立しなかった",uncertain:"判断できない",
reason:"成立しなかった主な理由（任意）",reason_ph:"例：低い雲で稜線が隠れた、風が強く水面反射が出なかった…",note:"補足メモ（任意）",note_ph:"現地状況、構図位置、後で確認するときに役立つ情報を記録できます。",export_note:"ダウンロードした記録は後で人が確認する必要があります。ダウンロードだけでモデルや研究結論が自動変更されることはありません。",limit:"一致した先頭 {n} 件を表示中。さらに入力すると絞り込めます。"
}};
const state={places:[],rows:[],catalogLoaded:false,lang:LANGS.includes(localStorage.getItem("chaselights_lang"))?localStorage.getItem("chaselights_lang"):"zh-TW"};
const $=function(id){return document.getElementById(id);};
const photoInput=$("photo-input"),results=$("results"),parserStatus=$("parser-status"),downloadAll=$("download-all"),consentModel=$("consent-model"),consentGps=$("consent-gps"),languageSelect=$("language-select");
function t(k,v){let s=(L[state.lang]&&L[state.lang][k])||L["zh-TW"][k]||k;Object.entries(v||{}).forEach(function(x){s=s.replaceAll("{"+x[0]+"}",String(x[1]));});return s;}
function setLanguage(lang){if(!LANGS.includes(lang))return;state.lang=lang;localStorage.setItem("chaselights_lang",lang);document.documentElement.lang=lang;languageSelect.value=lang;document.querySelectorAll("[data-i18n]").forEach(function(n){n.textContent=t(n.dataset.i18n);});languageSelect.setAttribute("aria-label",t("language_label"));if(state.rows.length)renderRows();else if(state.catalogLoaded)readyStatus();}
function num(v){v=Number(v);return Number.isFinite(v)?v:null;}
function texts(v){if(Array.isArray(v))return v.flatMap(texts);if(v&&typeof v==="object")return Object.values(v).flatMap(texts);return v?[String(v)]:[];}
function opNames(o){return [o.name_zh,o.name_en,o.name_ja,o.name_local].concat(texts(o.name_i18n)).filter(Boolean);} function opName(o){const localized=o.name_i18n&&o.name_i18n[state.lang];if(localized)return localized;if(state.lang==="en"&&o.name_en)return o.name_en;if(state.lang==="ja"&&o.name_ja)return o.name_ja;return o.name_zh||o.name_en||o.name_ja||o.name_local||o.opportunity_id;}
function buildPlaceIndex(catalog){
 const raw=Array.isArray(catalog&&catalog.spots)?catalog.spots:Object.values((catalog&&catalog.spots)||{});
 return raw.filter(function(s){return s&&s.spot_id&&s.active_in_catalog!==false&&Array.isArray(s.opportunities)&&s.opportunities.length;}).map(function(s){
  const seen=new Set(),viewpoints=[];
  (s.opportunities||[]).forEach(function(o){(o.viewpoints||[]).forEach(function(v){const lat=num(v.lat),lon=num(v.lon);if(lat===null||lon===null)return;const k=lat.toFixed(7)+","+lon.toFixed(7);if(seen.has(k))return;seen.add(k);viewpoints.push({viewpoint_id:v.viewpoint_id||null,name:v.name||null,lat:lat,lon:lon});});});
  const names=texts(s.name_i18n).concat([s.canonical_name,s.name_local,s.map_query]).filter(Boolean);
  return {spot_id:s.spot_id,canonical_name:s.canonical_name||names[0]||s.spot_id,name_i18n:s.name_i18n||{},name_local:s.name_local||null,aliases:texts(s.aliases).concat(texts(s.alias_i18n)),admin_areas:texts(s.admin_areas),category:s.category||"",names:names,viewpoints:viewpoints,opportunities:s.opportunities||[]};
 }).sort(function(a,b){return a.spot_id.localeCompare(b.spot_id);});
}
function placeName(p){return (p.name_i18n&&p.name_i18n[state.lang])||p.canonical_name||p.name_local||p.spot_id;}
function placeArea(p){return p.admin_areas.join(" · ")||p.category||"";}
function placeById(id){return state.places.find(function(p){return p.spot_id===id;})||null;}
function searchPlaceCandidates(q){
 q=String(q||"").trim().toLocaleLowerCase();if(!q)return[];
 return state.places.filter(function(p){const h=[p.spot_id,p.canonical_name,p.name_local,p.category].concat(p.names,p.aliases,p.admin_areas).filter(Boolean).join(" ").toLocaleLowerCase();return h.includes(q);}).slice(0,12);
}
function haversineKm(a,b,c,d){const r=function(x){return x*Math.PI/180;},p1=r(a),p2=r(c),dp=r(c-a),dl=r(d-b),x=Math.sin(dp/2)**2+Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)**2;return 6371.0088*2*Math.atan2(Math.sqrt(x),Math.sqrt(1-x));}
function nearestPlace(lat,lon,places){let best=null;(places||[]).forEach(function(p){p.viewpoints.forEach(function(v){const d=haversineKm(lat,lon,v.lat,v.lon);if(!best||d<best.distance_km)best={spot_id:p.spot_id,canonical_name:p.canonical_name,viewpoint_id:v.viewpoint_id,viewpoint_name:v.name,distance_km:d};});});return best;}
function pad(v){return String(v).padStart(2,"0");}
function normDate(v){if(!v)return null;if(v instanceof Date&&!Number.isNaN(v.getTime()))return v.getFullYear()+"-"+pad(v.getMonth()+1)+"-"+pad(v.getDate())+"T"+pad(v.getHours())+":"+pad(v.getMinutes())+":"+pad(v.getSeconds());const s=String(v).trim(),m=s.match(/^(\d{4}):(\d{2}):(\d{2})[ T](\d{2}):(\d{2}):(\d{2})/);return m?m[1]+"-"+m[2]+"-"+m[3]+"T"+m[4]+":"+m[5]+":"+m[6]:(s||null);}
function captureTime(m){const c=[["DateTimeOriginal",m.DateTimeOriginal],["CreateDate",m.CreateDate],["ModifyDate",m.ModifyDate]].find(function(x){return x[1];});const local=c?normDate(c[1]):null,off=m.OffsetTimeOriginal||m.OffsetTimeDigitized||m.OffsetTime||null;return{captured_at:local&&off?local+String(off):null,local_clock:local,utc_offset:off?String(off):null,source_tag:c?c[0]:null,timezone_status:off?"offset_from_exif":(local?"local_clock_without_offset":"missing")};}
function location(m){const lat=num(m.latitude),lon=num(m.longitude);return lat===null||lon===null?null:{latitude:lat,longitude:lon,altitude_m:num(m.GPSAltitude),direction_deg:num(m.GPSImgDirection),direction_ref:m.GPSImgDirectionRef||null,source:"embedded_exif"};}
function camera(m){return{make:m.Make||null,model:m.Model||null,lens_model:m.LensModel||null,focal_length_mm:num(m.FocalLength),f_number:num(m.FNumber),exposure_time_s:num(m.ExposureTime),iso:num(m.ISO||m.ISOSpeedRatings)};}
function bytes(n){return n<1024?n+" B":n<1048576?(n/1024).toFixed(1)+" KB":(n/1048576).toFixed(1)+" MB";}
function distance(d){return d==null?"—":d<1?Math.round(d*1000)+" m":d.toFixed(d<10?2:1)+" km";}
function associationMethod(row){if(!row.selected_spot_id)return"unmatched";if(row.selection_source==="gps_suggestion_confirmation")return"user_confirmed_gps_suggestion";if(row.selection_source==="manual_override")return"user_override";return"manual_search_selection";}
function buildObservationDraft(row,opt){
 const p=placeById(row.selected_spot_id),auto=row.auto_match,includeGps=!!(opt&&opt.includeGps);
 const loc={available_in_source:!!row.location,source:row.location?"embedded_exif":null,retention:row.location?(includeGps?"included_by_explicit_user_choice":"withheld_from_export"):"not_available"};
 if(row.location&&includeGps)Object.assign(loc,row.location);
 return{schema_version:DRAFT_SCHEMA,status:"unreviewed",created_at:new Date().toISOString(),source:{type:"user_field_observation",medium:"photograph",image_bytes_uploaded:false,publication:"metadata_only_image_not_uploaded",parser:EXIF_PARSER,processing:"browser_local"},file:{name:row.file.name,type:row.file.type||null,size_bytes:row.file.size,last_modified_ms:row.file.lastModified},capture:{time:row.capture_time,user_supplied_local_time:row.user_capture_time||null,camera:row.camera},location:loc,place_match:{spot_id:p?p.spot_id:null,canonical_name:p?p.canonical_name:null,method:associationMethod(row),confirmed_by_user:!!p,gps_suggestion:auto?{spot_id:auto.spot_id,canonical_name:auto.canonical_name,distance_km:Number(auto.distance_km.toFixed(4)),viewpoint_id:auto.viewpoint_id,basis:"nearest_researched_camera_zone",review_distance_km:REVIEW_KM}:null,review_required:true},observation:{opportunity_id:row.selected_opportunity_id||null,outcome:row.outcome||null,failure_reason:row.failure_reason.trim()||null,note:row.note.trim()||null},consent:{model_validation:!!(opt&&opt.modelValidation),precise_location_storage:includeGps,public_photo:false},ground_truth_boundary:"Unreviewed user observation only; no automatic scoring, research, navigation, or field-validation admission."};
}
function downloadJson(name,payload){const blob=new Blob([JSON.stringify(payload,null,2)+"\n"],{type:"application/json"}),url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(function(){URL.revokeObjectURL(url);},1000);}
function el(tag,cls,text){const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;}
function meta(grid,label,value,found){const item=el("div","meta-item "+(found?"found":"missing"));item.append(el("span","meta-label",label),el("span","meta-value",value||"—"),el("span","meta-state",found?t("found"):t("missing")));grid.appendChild(item);}
function selectedPlaceBox(row){
 const box=el("div","selected-place"+(row.selected_spot_id?"":" unmatched")),copy=el("div","selected-place-copy"),p=placeById(row.selected_spot_id);
 copy.append(el("div","selected-place-title",p?placeName(p):t("unmatched")),el("div","selected-place-meta",p?(p.spot_id+(placeArea(p)?" · "+placeArea(p):"")):t("unmatched_meta")));box.appendChild(copy);
 if(p){const b=el("button","clear-btn",t("clear"));b.type="button";b.addEventListener("click",function(){row.selected_spot_id=null;row.selected_opportunity_id=null;row.selection_source=null;renderRows();});box.appendChild(b);}
 return box;
}
function placeMatcher(row){
 const root=el("div","place-matcher");root.appendChild(selectedPlaceBox(row));
 if(row.auto_match){
  const p=placeById(row.auto_match.spot_id);
  if(p){const far=row.auto_match.distance_km>REVIEW_KM,s=el("div","gps-suggestion"+(far?" warn":""));s.append(el("div","gps-suggestion-title",t("gps_suggestion")+" · "+placeName(p)),el("div","gps-suggestion-meta",t(far?"far":"near",{d:distance(row.auto_match.distance_km)})));const actions=el("div","gps-suggestion-actions"),b=el("button","suggestion-btn",t("confirm"));b.type="button";b.addEventListener("click",function(){row.selected_spot_id=p.spot_id;row.selected_opportunity_id=null;row.selection_source="gps_suggestion_confirmation";renderRows();});actions.appendChild(b);s.appendChild(actions);root.appendChild(s);}
 }else root.appendChild(el("div","association-note",row.location?t("gps_none"):t("gps_missing")));
 const wrap=el("div","place-search-wrap"),input=el("input","place-search-input"),list=el("div","place-results");input.type="search";input.placeholder=t("search");input.setAttribute("role","combobox");input.setAttribute("aria-autocomplete","list");input.setAttribute("aria-expanded","false");list.id="place-results-"+row.id;input.setAttribute("aria-controls",list.id);list.setAttribute("role","listbox");list.hidden=true;let active=-1;
 function close(manual){list.hidden=true;input.setAttribute("aria-expanded","false");active=-1;if(manual)input.dataset.manualClosed="1";}
 function choose(p){row.selected_spot_id=p.spot_id;row.selected_opportunity_id=null;row.selection_source=(row.auto_match&&p.spot_id!==row.auto_match.spot_id)?"manual_override":"manual_search_selection";renderRows();}
 function show(){
  const found=searchPlaceCandidates(input.value);list.innerHTML="";active=-1;
  if(!input.value.trim()){close();return;}
  if(!found.length)list.appendChild(el("div","matcher-empty",t("no_match")));
  found.forEach(function(p){const b=el("button","place-option");b.type="button";b.setAttribute("role","option");b.dataset.spotId=p.spot_id;b.append(el("span","place-option-name",placeName(p)),el("span","place-option-meta",p.spot_id+(placeArea(p)?" · "+placeArea(p):"")));b.addEventListener("click",function(e){e.preventDefault();choose(p);});list.appendChild(b);});
  if(found.length===12)list.appendChild(el("div","matcher-empty",t("limit",{n:12})));const closeButton=el("button","place-option",t("close_results"));closeButton.type="button";closeButton.dataset.action="close-results";closeButton.addEventListener("click",function(e){e.preventDefault();close(true);input.focus();});list.appendChild(closeButton);list.hidden=false;input.setAttribute("aria-expanded","true");
 }
 function move(delta){const options=Array.from(list.querySelectorAll(".place-option[data-spot-id]"));if(!options.length)return;active=Math.max(0,Math.min(options.length-1,active+delta));options.forEach(function(x,i){x.classList.toggle("active",i===active);});options[active].scrollIntoView({block:"nearest"});}
 input.addEventListener("input",function(){delete input.dataset.manualClosed;show();});input.addEventListener("focus",function(){if(input.dataset.manualClosed){delete input.dataset.manualClosed;return;}if(input.value.trim())show();});input.addEventListener("keydown",function(e){if(e.key==="Escape"){close(true);return;}if(e.key==="ArrowDown"||e.key==="ArrowUp"){e.preventDefault();if(list.hidden)show();move(e.key==="ArrowDown"?1:-1);}else if(e.key==="Enter"&&!list.hidden&&active>=0){e.preventDefault();const b=list.querySelectorAll(".place-option[data-spot-id]")[active];if(b){const p=placeById(b.dataset.spotId);if(p)choose(p);}}});input.addEventListener("blur",function(){setTimeout(close,120);});
 wrap.append(input,list);root.append(wrap,el("div","place-search-status",t("search_hint")));
 if(row.selected_spot_id){const key=row.selection_source==="gps_suggestion_confirmation"?"selected_suggestion":(row.selection_source==="manual_override"?"selected_override":"selected_manual");root.appendChild(el("div","association-note",t(key)));}
 return root;
}
function option(select,value,text){const o=document.createElement("option");o.value=value;o.textContent=text;select.appendChild(o);}
function observationFields(row){
 const block=el("section","review-block"),p=placeById(row.selected_spot_id);block.append(el("div","review-block-title",t("subject")),el("p","review-block-help",t("subject_help")));
 const grid=el("div","observation-fields"),subjectLabel=el("label","field-label"),subject=el("select","field-control");subjectLabel.append(el("span","",t("subject")));option(subject,"",t("subject_empty"));if(p)(p.opportunities||[]).forEach(function(o){option(subject,o.opportunity_id,opName(o));});subject.value=row.selected_opportunity_id||"";subject.addEventListener("change",function(){row.selected_opportunity_id=subject.value||null;});subjectLabel.appendChild(subject);
 const outcomeLabel=el("label","field-label"),outcome=el("select","field-control");outcomeLabel.append(el("span","",t("outcome")));[["",t("outcome_empty")],["held",t("held")],["partial",t("partial_outcome")],["failed",t("failed")],["uncertain",t("uncertain")]].forEach(function(x){option(outcome,x[0],x[1]);});outcome.value=row.outcome;outcome.addEventListener("change",function(){row.outcome=outcome.value;});outcomeLabel.appendChild(outcome);
 const reasonLabel=el("label","field-label wide"),reason=el("input","field-control");reason.type="text";reason.placeholder=t("reason_ph");reason.value=row.failure_reason;reason.addEventListener("input",function(){row.failure_reason=reason.value;});reasonLabel.append(el("span","",t("reason")),reason);
 const noteLabel=el("label","field-label wide"),note=el("textarea","field-textarea");note.placeholder=t("note_ph");note.value=row.note;note.addEventListener("input",function(){row.note=note.value;});noteLabel.append(el("span","",t("note")),note);grid.append(subjectLabel,outcomeLabel,reasonLabel,noteLabel);block.appendChild(grid);return block;
}
function renderRows(){
 results.innerHTML="";if(!state.rows.length){results.appendChild(el("div","empty-state",t("no_photos")));downloadAll.disabled=true;return;}downloadAll.disabled=false;
 state.rows.forEach(function(row){
  const card=el("article","observation-card"),head=el("div","observation-head"),fw=el("div");fw.append(el("div","file-name",row.file.name),el("div","small",bytes(row.file.size)+(row.file.type?" · "+row.file.type:"")));head.appendChild(fw);card.appendChild(head);
  const grid=el("div","meta-grid"),cap=row.capture_time.captured_at||(row.capture_time.local_clock?(row.capture_time.local_clock+" · "+t("no_tz")):""),gps=row.location?(row.location.latitude.toFixed(6)+", "+row.location.longitude.toFixed(6)):"",cam=[row.camera.make,row.camera.model].filter(Boolean).join(" "),lens=row.camera.lens_model||(row.camera.focal_length_mm?row.camera.focal_length_mm+" mm":"");
  meta(grid,t("capture"),cap,!!cap);meta(grid,t("gps"),gps,!!gps);meta(grid,t("camera"),cam,!!cam);meta(grid,t("lens"),lens,!!lens);card.appendChild(grid);if(row.parse_error)card.appendChild(el("div","parse-note",t("parse_problem")));
  const review=el("div","review-grid"),captureBlock=el("section","review-block");captureBlock.append(el("div","review-block-title",t("capture")),el("p","review-block-help",t("capture_help")));const cl=el("label","field-label"),ci=el("input","field-control");ci.type="datetime-local";ci.value=row.user_capture_time||"";ci.addEventListener("input",function(){row.user_capture_time=ci.value;});cl.append(el("span","",t("capture_manual")),ci);captureBlock.appendChild(cl);
  const placeBlock=el("section","review-block");placeBlock.append(el("div","review-block-title",t("place")),el("p","review-block-help",t("place_help")),placeMatcher(row));review.append(captureBlock,placeBlock,observationFields(row),el("div","association-note",t("export_note")));card.appendChild(review);
  const dr=el("div","download-row"),b=el("button","download-btn",t("download_one"));b.type="button";b.addEventListener("click",function(){downloadJson("observation-"+row.id+".json",buildObservationDraft(row,{includeGps:consentGps.checked,modelValidation:consentModel.checked}));});dr.appendChild(b);card.appendChild(dr);results.appendChild(card);
 });
}
async function parsePhoto(file,index){
 const id=Date.now().toString(36)+"-"+index.toString(36);let m={},error=null;if(!window.exifr||typeof window.exifr.parse!=="function")error="EXIF parser unavailable";else try{m=await window.exifr.parse(file,true)||{};}catch(e){error=String(e&&e.message?e.message:e);}
 const loc=location(m),auto=loc?nearestPlace(loc.latitude,loc.longitude,state.places):null;
 return{id:id,file:{name:file.name,type:file.type||"",size:file.size,lastModified:file.lastModified},capture_time:captureTime(m),user_capture_time:"",camera:camera(m),location:loc,auto_match:auto,selected_spot_id:null,selection_source:null,selected_opportunity_id:null,outcome:"",failure_reason:"",note:"",parse_error:error};
}
async function handleFiles(files){const list=Array.from(files||[]);if(!list.length)return;parserStatus.className="status";parserStatus.textContent=t("parsing",{n:list.length});const rows=[];for(let i=0;i<list.length;i++)rows.push(await parsePhoto(list[i],i));state.rows=rows;const failures=rows.filter(function(r){return r.parse_error;}).length;parserStatus.className=failures?"status warn":"status ready";parserStatus.textContent=failures?t("partial",{n:failures}):t("done");renderRows();}
function readyStatus(){if(!state.catalogLoaded)return;if(!window.exifr){parserStatus.className="status warn";parserStatus.textContent=t("ready_no_exif");}else{parserStatus.className="status ready";parserStatus.textContent=t("ready",{n:state.places.length});}}
async function loadCatalog(){try{const response=await fetch(CATALOG_URL,{cache:"no-cache"});if(!response.ok)throw new Error("HTTP "+response.status);state.places=buildPlaceIndex(await response.json());state.catalogLoaded=true;readyStatus();}catch(e){parserStatus.className="status warn";parserStatus.textContent=t("catalog_error",{e:String(e&&e.message?e.message:e)});}}
photoInput.addEventListener("change",function(){handleFiles(photoInput.files);});
languageSelect.addEventListener("change",function(){setLanguage(languageSelect.value);});
downloadAll.addEventListener("click",function(){const o={includeGps:consentGps.checked,modelValidation:consentModel.checked};downloadJson("chaselights-field-observations.json",{schema_version:DRAFT_SCHEMA,exported_at:new Date().toISOString(),observations:state.rows.map(function(r){return buildObservationDraft(r,o);})});});
window.ChaseLightsFieldIntake={haversineKm:haversineKm,buildPlaceIndex:buildPlaceIndex,nearestPlace:nearestPlace,searchPlaceCandidates:searchPlaceCandidates,buildObservationDraft:buildObservationDraft,associationMethod:associationMethod,getStateSummary:function(){return{catalogLoaded:state.catalogLoaded,placeCount:state.places.length,rowCount:state.rows.length,lang:state.lang,rows:state.rows.map(function(r){return{id:r.id,selected_spot_id:r.selected_spot_id,gps_suggestion_spot_id:r.auto_match?r.auto_match.spot_id:null,association_method:associationMethod(r)};})};}};
setLanguage(state.lang);loadCatalog();
})();