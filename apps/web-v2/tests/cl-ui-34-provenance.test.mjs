// CL-UI-34: user-visible data provenance panel in the weather modal.
// (1) i18n keys exist in all three dictionaries; no internal enum names leak.
// (2) provStaticRows renders honest rows: hourly model + issued time,
//     elevation/coordinate sources with confidence, threshold nature in user
//     language (provisional stays provisional, no raw "provisional" jargon),
//     and the spot-local time-zone convention via GMT±n.
// (3) provStampText derives cycle/observation stamps from WeatherGrid QC data.
// (4) index.html carries the collapsed <details> panel inside the modal,
//     stamps bumped to clui44 in the SAME commit; app.js/app.css carry the
//     render path and styles.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const htmlSource=readFileSync(new URL('../../../index.html',import.meta.url),'utf8');
const cssSource=readFileSync(new URL('../../../assets/app.css',import.meta.url),'utf8');
const grab=(start,end)=>{const i=appSource.indexOf(start);return appSource.slice(i,appSource.indexOf(end,i));};

const provCode=grab('const PROV_LAYER_FILES','    function renderModalProvenance(');
const makeFns=(lang,dict)=>new Function(`let currentLang=${JSON.stringify(lang)};
const d=()=>(${JSON.stringify(dict)});
const esc=v=>String(v??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const tzAbbrLabel=a=>{const s=String(a||'');if(s==='CST')return'GMT+8';if(s==='JST')return'GMT+9';return s;};
${provCode}
return {provRegionOf,provGmtStamp,provConfLabel,provStampText,provStaticRows,provLayerRow,PROV_LAYER_FILES};`)();

// Extract the real dictionaries for the served page (top-level i18n dict).
const dictMatch=lang=>{const i=appSource.indexOf(`'${lang}': {`);const j=appSource.indexOf("      },",i);
  const body=appSource.slice(i,j);const kv={};
  for(const m of body.matchAll(/([A-Za-z0-9_]+):'((?:[^'\\]|\\.)*)'/g))kv[m[1]]=m[2].replace(/\\'/g,"'");
  return kv;};

const SPOT={spot_id:'tw-086',elevation:null,api_elevation:261,timezone:'Asia/Taipei',timezone_abbr:'CST',utc_offset_seconds:28800,coordinate_source:'owner-provided Google Maps link',coordinate_confidence:'medium'};
const V2PLACE={provider_run:{issued_at:'2026-11-06T07:19:38Z',grid:{elevation_m:60.0}}};

test('CL-UI-34 (1): prov_* i18n keys exist in all three dictionaries',()=>{
  for(const lang of ['zh-TW','en','ja']){
    const dict=dictMatch(lang);
    for(const k of ['prov_title','prov_hourly_label','prov_hourly_value','prov_issued_label','prov_layers_label','prov_cycle_label','prov_obs_label','prov_layers_loading','prov_layers_missing','prov_elev_label','prov_elev_camera','prov_elev_api','prov_elev_grid','prov_coord_label','prov_confidence_label','prov_conf_high','prov_conf_medium','prov_conf_low','prov_coord_unknown','prov_threshold_label','prov_threshold_fallback','prov_tz_label','prov_tz_note']){
      assert.ok(dict[k],`${lang} missing ${k}`);
      assert.ok(!/^\s*$/.test(dict[k]),`${lang} ${k} empty`);
    }
    // Honest-rule guard: the source panel describes provisional thresholds in
    // user language; raw internal enum names must not be shipped as copy.
    for(const k of Object.keys(dict).filter(k=>k.startsWith('prov_'))){
      assert.doesNotMatch(dict[k],/\bPROVISIONAL_THRESHOLDS\b|\bDISPLAY_APPROXIMATION\b|\bcamera_context_provisional\b/);
    }
    // Trilingual parity: same key set across languages.
    const zh=dictMatch('zh-TW'),en=dictMatch('en'),ja=dictMatch('ja');
    for(const d2 of [en,ja])for(const k of Object.keys(zh).filter(k=>k.startsWith('prov_')))assert.ok(k in d2,`key ${k} missing`);
  }
});

test('CL-UI-34 (2): provStaticRows renders hourly model, issued time, elevation, coordinate confidence',()=>{
  const zh=makeFns('zh-TW',dictMatch('zh-TW'));
  const html=zh.provStaticRows(SPOT,V2PLACE,'門檻為暫定值（ limitations ）');
  assert.match(html,/Open-Meteo · GFS Seamless/);
  assert.match(html,/2026-11-06 07:19 GMT\+0/);
  assert.match(html,/預報格點海拔（Open-Meteo） 261 m/);
  assert.match(html,/預報格點海拔（評估用） 60 m/);
  assert.match(html,/owner-provided Google Maps link/);
  assert.match(html,/信心 中/);
  assert.match(html,/GMT\+8（Asia\/Taipei）/);
  assert.match(html,/門檻為暫定值（ limitations ）/);
  // Camera-recorded elevation wins over api elevation when both exist.
  const both=zh.provStaticRows({...SPOT,elevation:300},V2PLACE,'');
  assert.match(both,/機位海拔（景點資料） 300 m/);
  assert.doesNotMatch(both,/261 m/);
  // Missing coordinate source falls back to an honest sentence, not a bare dash.
  const none=zh.provStaticRows({...SPOT,coordinate_source:null,coordinate_confidence:null,elevation:null,api_elevation:null},null,'');
  assert.match(none,/座標來源資料暫缺/);
  assert.doesNotMatch(none,/>—</);
});

test('CL-UI-34 (3): provStampText derives cycle/observation stamps from QC payloads',()=>{
  const zh=makeFns('zh-TW',dictMatch('zh-TW'));
  const gfs=zh.provStampText({cycle:{cycle_time_utc:'2026-11-05T18:00:00+00:00'}});
  assert.equal(gfs,'起報 2026-11-05 18:00 GMT+0');
  const hima=zh.provStampText({source_products:{cloud_mask:{path:'noaa-himawari9/AHI-L2-FLDK-Clouds/2026/11/06/0710/AHI-CMSK_v1r1_h09_s202611060710210_e202611060719404_c202611060724028.nc'}}});
  assert.equal(hima,'觀測 2026-11-06 07:10 GMT+0');
  assert.equal(zh.provStampText(undefined),'讀取中…');
  assert.equal(zh.provStampText(null),'暫無此圖層資料');
});

test('CL-UI-34 (4): region layer map is honest per region and esc-safe',()=>{
  const fns=makeFns('zh-TW',dictMatch('zh-TW'));
  assert.equal(fns.PROV_LAYER_FILES.tw.length,6);
  assert.equal(fns.PROV_LAYER_FILES.jp.length,3);
  assert.equal(fns.PROV_LAYER_FILES.us.length,2);
  assert.equal(fns.provRegionOf(SPOT),'tw');
  assert.equal(fns.provRegionOf({spot_id:'ak-001'}),'ak');
  assert.equal(fns.provRegionOf({spot_id:'xx-001'}),null);
  const row=fns.provLayerRow('gfs_tw_weather_qc.json','GFS（NOAA/NCEP）',null);
  assert.match(row,/data-prov-file="gfs_tw_weather_qc\.json"/);
  assert.match(row,/暫無此圖層資料/);
  // Injection safety: coordinate_source is escaped into the HTML.
  const evil=makeFns('zh-TW',dictMatch('zh-TW')).provStaticRows({...SPOT,coordinate_source:'<script>x</script>'},null,'');
  assert.doesNotMatch(evil,/<script>/);
  assert.match(evil,/&lt;script&gt;/);
});

test('CL-UI-34 (5): index.html carries the collapsed panel, cards untouched, stamps bumped in the same commit',()=>{
  assert.match(htmlSource,/<details class="modal-provenance" id="modal-provenance" data-prov-open="false">/);
  assert.match(htmlSource,/<summary data-i18n="prov_title">/);
  // Panel lives inside the weather modal body only (deep layer, after the
  // hourly timeline) — the homepage card markup must not gain prov markup.
  const modalStart=htmlSource.indexOf('id="modal-overlay"');
  const panelAt=htmlSource.indexOf('id="modal-provenance"');
  const modalEnd=htmlSource.indexOf('</div>\n  </div>',modalStart);
  assert.ok(modalStart>0&&panelAt>modalStart&&panelAt<modalEnd);
  assert.doesNotMatch(htmlSource.slice(0,modalStart),/modal-provenance/);
  assert.ok(!htmlSource.includes('?v=clui39'),'stamp must be bumped');
  assert.equal((htmlSource.match(/\?v=clui41/g)||[]).length,2,'site-nav stamps at clui41');
  assert.equal((htmlSource.match(/\?v=clui45/g)||[]).length,1,'app.js stamp bumped to clui45');
  // Render path and styles exist in app.js / app.css.
  assert.match(appSource,/function renderModalProvenance\(/);
  assert.match(appSource,/renderModalProvenance\(summarySpot\);/);
  assert.match(appSource,/#modal-provenance \.prov-layer\[data-prov-file/);
  assert.match(appSource,/\.addEventListener\('toggle'/);
  assert.match(cssSource,/\.modal-provenance\{/);
  assert.match(cssSource,/@media \(max-width:640px\)\{\s*\.modal-provenance summary/);
});
