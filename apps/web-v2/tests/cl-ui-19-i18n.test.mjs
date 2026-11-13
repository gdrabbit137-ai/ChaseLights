// CL-UI-19: i18n closing batch (reviewer patrol Majors).
//
// 1. Subject names follow the honest-translation rule: an "en" field that
//    merely copies the zh-TW string is not a reviewed translation, so the
//    zh-TW name stays (never the raw opportunity id, never fabricated copy).
// 2. The "best subject" punctuation is per-language (en uses ": " + en sentence
//    order); the ja copy is natural Japanese with zero simplified characters.
// 3. The modal summary falls back to the spot's V2 best opportunity when the
//    legacy daily metric carries no opportunity_id (the en "No shooting
//    summary" gap), and re-rendering an open modal retranslates its header.
// 4. genre-eval displays the evaluation timestamp in the GMT+8 convention.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const appSource=readFileSync(new URL('../../../assets/app.js',import.meta.url),'utf8');
const genreSource=readFileSync(new URL('../../../assets/genre-eval.js',import.meta.url),'utf8');
const grab=(start,end)=>appSource.slice(appSource.indexOf(start),appSource.indexOf(end,appSource.indexOf(start)));

// ---------------------------------------------------------------------------
// Part A: reviewedLocaleName runs for real.
// ---------------------------------------------------------------------------
const factoryA=new Function([
  grab('const localeText=values=>{','const reviewedLocaleName=values=>{'),
  grab('const reviewedLocaleName=values=>{','function opportunityDisplayName'),
  'let currentLang=\'en\';',
  'return {localeText,reviewedLocaleName};'
].join('\n'));
const {reviewedLocaleName}=factoryA();

test('CL-UI-19 A1: an en field copying zh-TW is NOT a translation — zh-TW name stays',()=>{
  const values={'zh-TW':'大稻埕淡水河夕照','en':'大稻埕淡水河夕照','ja':'大稻埕淡水河夕照'};
  assert.equal(reviewedLocaleName(values),'大稻埕淡水河夕照');
});

test('CL-UI-19 A2: a genuinely authored English name is used in en mode',()=>{
  const values={'zh-TW':'南子吝・山海360°晨景與海面日出','en':'Nanzilin sunrise over the sea','ja':'南子吝の海面日出'};
  // en is the current lang in this harness (localeText reads 'en').
  assert.equal(reviewedLocaleName(values),'Nanzilin sunrise over the sea');
});

test('CL-UI-19 A3: a missing localized name falls back to the zh-TW name, never an id',()=>{
  assert.equal(reviewedLocaleName({'zh-TW':'霧中淡水大橋'}),'霧中淡水大橋');
  assert.equal(reviewedLocaleName(null),'');
});

// ---------------------------------------------------------------------------
// Part B: source pins — dictionaries and wiring.
// ---------------------------------------------------------------------------
const jaLine=appSource.split('\n').find(l=>l.includes("v2_best_subject:'本日の最適な題材：'"));

test('CL-UI-19 B1: v2_best_subject carries per-language punctuation, template adds none',()=>{
  assert.ok(appSource.includes("v2_best_subject:'本日最佳題材：'"));
  assert.ok(appSource.includes("v2_best_subject:'Best subject today: '"));
  assert.ok(!appSource.includes('}：${esc(stripSpotNamePrefix(v2Best.name,spot))}'),'the template must not hardcode a full-width colon');
  // CL-UI-71: the old best-subject card line is retired; the dict keys stay
  // for any future data surface, but the render expression is gone.
  assert.ok(!appSource.includes('${esc(d()[v2BestSubjectKey()])}${esc(stripSpotNamePrefix'),'retired template must be gone');
});

test('CL-UI-19 B2: ja copy is natural Japanese with zero simplified 题',()=>{
  assert.ok(jaLine.includes("eval2_hours:'撮影に適した時間数'"));
  assert.ok(jaLine.includes("v2_next_window:'次の撮影に適した時間帯：'"));
  assert.ok(jaLine.includes("v2_none_today:'本日に適したテーマなし'"));
  assert.ok(appSource.includes("genre_eval_link:'🌗 題材評価'"));
  assert.ok(appSource.includes("genre_eval_title:'撮影題材の条件評価を開く'"));
  assert.ok(appSource.includes("sort_hours:'撮影に適した時間数が多い順'"));
  assert.ok(appSource.includes("result_count_hours_desc:'撮影に適した時間数の多い順 · {n} スポット'"));
  // zero simplified-character residue in the ja dict line and genre-eval
  assert.ok(!appSource.split('\n').some(l=>l.includes('题材')));
  assert.ok(!genreSource.includes('题材'));
  assert.ok(genreSource.includes("hours: '撮影に適した時間数'"));
  assert.ok(genreSource.includes("if (lang === 'ja') return '題材';"));
});

test('CL-UI-19 B3: the name fallback chain never ends on the raw opportunity id first',()=>{
  // CL-UI-25: the raw zh-TW fallback arms now run through fallbackConnectors
  // so en/ja display keeps zh-TW content with locale-consistent joiners.
  assert.ok(appSource.includes("(currentLang!=='zh-TW'?fallbackConnectors(o.name_i18n?.['zh-TW']||''):o.name_i18n?.['zh-TW'])||o.opportunity_id;"));
  assert.ok(appSource.includes("return fallbackConnectors(op?.name_i18n?.['zh-TW'])||op?.name_zh||legacyName||themeLabel(op?.legacy_theme||theme||'mountain_view');"));
});

test('CL-UI-19 B4: modal summary falls back to the V2 best opportunity',()=>{
  assert.ok(appSource.includes('let activeOpportunityId=summaryMetric?.opportunity_id||null;'));
  assert.ok(appSource.includes('if(!activeOpportunityId){const v2place=v2PlaceForSpot(summarySpot);const v2best=v2place?v2BestForSpot(v2place,summarySpot?.timezone):null;if(v2best&&v2best.oppId)activeOpportunityId=v2best.oppId;}'));
});

test('CL-UI-19 B5: re-rendering an open modal retranslates the modal header',()=>{
  // The header line lives inside renderWeatherModal (it previously only ran in
  // the async openWeatherModal), so a language switch re-renders it.
  const fn=grab('function renderWeatherModal(spot,summaryMetric){','function closeModal()');
  assert.ok(fn.includes("document.getElementById('modal-spot-name').innerText=`🌦️ ${spotName(spot)} — ${d().weather_link.replace(/^🌦️\\s*/, '')}`;"));
  const sw=grab('function switchLanguage(k){','function switchTempUnit');
  assert.ok(sw.includes("renderWeatherModal(activeModalSpot,activeModalSummary)"));
});

test('CL-UI-19 B6: genre-eval renders the generated_at stamp in GMT+8',()=>{
  assert.ok(genreSource.includes("new Date(generated.getTime() + 8 * 3600 * 1000).toISOString().slice(0, 19).replace('T', ' ') + ' GMT+8'"));
  assert.ok(!genreSource.includes(".replace('Z', ' UTC')}`"));
});

// ---------------------------------------------------------------------------
// Part C: GMT+8 conversion maths (the +8 offset is the ticket's own rule).
// ---------------------------------------------------------------------------
test('CL-UI-19 C1: 06:56:33 UTC renders as 14:56:33 GMT+8, data untouched',()=>{
  const generated=new Date('2026-11-04T06:56:33Z');
  const shifted=new Date(generated.getTime()+8*3600*1000);
  assert.equal(shifted.toISOString().slice(0,19).replace('T',' '),'2026-11-04 14:56:33');
});