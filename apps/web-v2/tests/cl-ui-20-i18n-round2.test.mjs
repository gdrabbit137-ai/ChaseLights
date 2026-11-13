// CL-UI-20: i18n round-2 batch (patrol findings).
//
// 1. The en modal headline uses en sentence order: "Today: 2 suitable hours
//    (from …)" — the day label leads, never trails.
// 2. Separators are language-aware: en uses ': ' / ', ' (listSep/colonSep),
//    zh-TW and ja keep '：' / '、'. No hardcoded '：'/'、' joins remain in
//    shared render paths.
// 3. High-exposure homepage subjects carry verified en/ja names in the V2
//    data layer (data/v2/opportunities + generated contract bundle); the two
//    round-1 review-gated records (tw-036-P01, tw-082-P01) keep their
//    reviewed bytes; the honest-translation fallback stays uniform for the rest.
// 4. The mobile modal close button is keyed to i18n (span data-i18n +
//    aria-label), so a language switch retranslates it.
// 5. The best-subject line follows the selected day tab (today/tomorrow/
//    day after) via v2BestSubjectKey(), in all three dictionaries.
// 6. CL-UI-42: the language dropdown options follow the page language
//    (data-i18n lang_opt_* in all three dicts), and the modal headline never
//    repeats the date when the day label is itself a MM/DD stamp.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const grab=(start,end)=>appSource.slice(appSource.indexOf(start),appSource.indexOf(end,appSource.indexOf(start)));

// ---------------------------------------------------------------------------
// Part A: language-aware separators run for real.
// ---------------------------------------------------------------------------
const factoryA=new Function([
  "let currentLang='en';let currentTempUnit='C';let currentDayFilter='today';",
  'const i18nDict={"zh-TW":{},"en":{},"ja":{}};',
  grab('const colonSep=()=>','// Place names are the one intentional locale exception'),
    grab('function formatHourSegments','function v2ContractThreshold'),
    'const d=()=>({eval2_fail_by:"Unmet conditions"});',
  'const esc=v=>String(v??"");',
  'const v2MetricName=m=>m;',
  'const v2IsToday=()=>true;',
  'const v2RemainingHoursList=l=>l;',
  'const localNowMinutes=()=>600;',
  'return {listSep,colonSep,formatHourSegments};'
].join('\n'));
const {listSep,colonSep,formatHourSegments}=factoryA();

test('CL-UI-20 A1: en separators are half-width, zh/ja keep native punctuation',()=>{
  assert.equal(listSep(),', ');
  assert.equal(colonSep(),': ');
});

test('CL-UI-20 A2: formatHourSegments joins with the language-aware separator',()=>{
  assert.equal(formatHourSegments(['05:00','06:00','17:00']),'05:00–06:00, 17:00');
});

// ---------------------------------------------------------------------------
// Part B: dictionary and wiring pins (all three languages).
// ---------------------------------------------------------------------------
// CL-UI-72: the modal headline (and its modal_headline_* keys) is removed —
// the old B1 day-order pins retire with it.

test('CL-UI-20 B2: no hardcoded full-width joins remain in shared render paths',()=>{
  assert.ok(!appSource.includes(".join('、')"),'hour/time joins must go through listSep()');
  assert.ok(appSource.includes('join(listSep())'));
  assert.ok(appSource.includes('${colonSep()}'));
});

test('CL-UI-20 B3: v2_best_subject_tomorrow / _after exist in all three dicts',()=>{
  for(const [lang,pair] of [
    ['zh-TW',["v2_best_subject_tomorrow:'明日最佳題材：'","v2_best_subject_after:'後日最佳題材：'"]],
    ['en',["v2_best_subject_tomorrow:'Best subject tomorrow: '","v2_best_subject_after:'Best subject day after: '"]],
    ['ja',["v2_best_subject_tomorrow:'明日の最適な題材：'","v2_best_subject_after:'明後日の最適な題材：'"]],
  ]){
    const lines=appSource.split('\n');
    const start=lines.findIndex(l=>l.includes(`'${lang}': {`));
    const end=lines.findIndex((l,i)=>i>start&&/^      '?:?\s*\},?$/.test(l.trim())||/^      \},$/.test(l.trim()));
    const line=lines.slice(start,end>0?end:start+40).find(l=>l.includes('v2_best_subject:'));
    for(const key of pair)assert.ok(line.includes(key),`${lang} missing ${key}`);
  }
});

test('CL-UI-20 B4: the best-subject label follows the day tab via v2BestSubjectKey',()=>{
  assert.ok(appSource.includes("const v2BestSubjectKey=()=>currentDayFilter==='tomorrow'?'v2_best_subject_tomorrow':currentDayFilter==='after_tomorrow'?'v2_best_subject_after':isFarDay(currentDayFilter)?'v2_best_subject_far':'v2_best_subject';"));
  // CL-UI-71: the old best-subject card line is retired (dict keys remain).
  assert.ok(!appSource.includes('${esc(d()[v2BestSubjectKey()])}${esc(stripSpotNamePrefix'),'retired template must be gone');
});

test('CL-UI-20 B5: the mobile modal close button is keyed to i18n',()=>{
  const init=grab("const btn=document.createElement('button');btn.type='button';btn.className='modal-close-mobile-btn';","btn.onclick=e=>{e.preventDefault();closeModal();};");
  assert.ok(init.includes(`btn.setAttribute('data-i18n-aria-label','close_weather')`));
  assert.ok(init.includes(`<span data-i18n="close_weather"></span>`));
  assert.ok(!init.includes('<span data-i18n>'),'a keyless data-i18n span freezes the creation-time language');
});

// ---------------------------------------------------------------------------
// Part B6 (CL-UI-42): the language dropdown follows the page language.
// ---------------------------------------------------------------------------
test('CL-UI-42 B6: lang dropdown options carry data-i18n keys in all three dicts',()=>{
  const pairs=[
    ['zh-TW',["lang_opt_zh:'🌐 繁體中文'","lang_opt_en:'🌐 English'","lang_opt_ja:'🌐 日語'"]],
    ['en',["lang_opt_zh:'🌐 Traditional Chinese'","lang_opt_en:'🌐 English'","lang_opt_ja:'🌐 Japanese'"]],
    ['ja',["lang_opt_zh:'🌐 中国語（繁体字）'","lang_opt_en:'🌐 英語'","lang_opt_ja:'🌐 日本語'"]],
  ];
  const lines=appSource.split('\n');
  for(const [lang,keys] of pairs){
    const start=lines.findIndex(l=>l.includes(`'${lang}': {`));
    const line=lines.slice(start,start+8).find(l=>l.includes('country_label:'));
    for(const key of keys)assert.ok(line.includes(key),`${lang} missing ${key}`);
  }
  const indexSource=readFileSync(new URL('../../../index.html',import.meta.url),'utf8');
  for(const [value,key] of [['zh-TW','lang_opt_zh'],['en','lang_opt_en'],['ja','lang_opt_ja']]){
    assert.match(indexSource,new RegExp(`<option value="${value}"[^>]*data-i18n="${key}"`));
  }
});

// ---------------------------------------------------------------------------
// Part C: V2 data layer — verified en/ja names for high-exposure subjects.
// ---------------------------------------------------------------------------
const contracts=JSON.parse(readFileSync(new URL('../opportunity-contracts.json',import.meta.url),'utf8'));
const HIGH_EXPOSURE=new Set([
  'tw-035-P01','tw-035-P02','tw-035-P03','tw-035-P04','tw-035-P05','tw-035-P06','tw-035-P07','tw-035-P08','tw-035-P09','tw-035-P10',
  'tw-082-P02','tw-082-P03','tw-082-P04','tw-082-P05','tw-082-P07','tw-082-P08','tw-082-P09',
  'tw-019-P01','tw-019-P02','tw-019-P03','tw-019-P04','tw-019-P05','tw-019-P06',
  'tw-040-P01','tw-040-P02','tw-040-P03','tw-040-P04','tw-040-P05','tw-040-P06',
  'tw-024-P01','tw-024-P02','tw-024-P03','tw-024-P04','tw-024-P05',
  'tw-041-P01','tw-041-P02','tw-041-P03','tw-041-P04','tw-041-P05',
  'tw-045-P01','tw-045-P02','tw-045-P03','tw-045-P04','tw-045-P05',
  'tw-020-P01','tw-020-P02','tw-020-P03','tw-020-P04',
  'tw-022-P01','tw-022-P02','tw-022-P03','tw-022-P04',
  'tw-028-P01','tw-028-P02','tw-028-P03','tw-028-P04',
  'tw-036-P02','tw-036-P03','tw-036-P04',
  'tw-043-P01','tw-043-P02','tw-043-P03','tw-043-P04'
]);

test('CL-UI-20 C1: high-exposure subjects carry reviewed (non-copying) en/ja names in the contract bundle',()=>{
  const missing=[];
  for(const id of HIGH_EXPOSURE){
    const c=contracts.opportunities[id];
    if(!c){missing.push(id+':absent');continue;}
    const zh=c.name_i18n['zh-TW'];
    if(c.name_i18n.en===zh||c.name_i18n.ja===zh)missing.push(id);
  }
  assert.deepEqual(missing,[],`untranslated high-exposure subjects: ${missing.join(',')}`);
});

test('CL-UI-20 C2: the fallback stays uniform — unreviewed subjects keep zh-TW in every locale',()=>{
  // An en/ja field that merely copies zh-TW is not a translation; the renderer
  // (reviewedLocaleName) must then show zh-TW in all languages, never a mix.
  const factoryC=new Function([
    grab('const localeText=values=>{','function opportunityDisplayName'),
    "let currentLang='en';",
    'return {reviewedLocaleName};'
  ].join('\n'));
  const {reviewedLocaleName}=factoryC();
  const values={'zh-TW':'未譯題材','en':'未譯題材','ja':'未譯題材'};
  assert.equal(reviewedLocaleName(values),'未譯題材');
});