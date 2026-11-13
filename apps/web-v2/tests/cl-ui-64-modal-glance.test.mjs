// CL-UI-64: place-modal declutter (three-tier architecture, owner-approved).
// Tier 1 — top "today at a glance" quick view (subject-cards lookup: suitable
// -> short subject chips + window; not-met -> one dominant short reason word).
// Tier 2 — the 8-day assessment becomes a compact strip: one row of day+badge
// cells, click/hover reveals a SHORT reason word (never the long sentence).
// Tier 3 — 拍攝條件/成立條件 collapses into an accordion (default closed,
// summary shows 條件 ×N); the long narrative lives only behind it. Plus an
// hourly-forecast exit link at the modal bottom (weather-map deep link with
// place_id as spot). Source assertions + extracted pure helpers, per the
// established V1-shell test pattern.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, '..', '..', '..');
const appSource = readFileSync(join(ROOT, 'assets', 'app.js'), 'utf8');
const appCss = readFileSync(join(ROOT, 'assets', 'app.css'), 'utf8');
const indexSource = readFileSync(join(ROOT, 'index.html'), 'utf8');
const artifact = JSON.parse(readFileSync(
  join(ROOT, 'data', 'v2', 'evaluations', 'subject-cards-20261112T202312Z.json'), 'utf8'));

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, 'source slice not found: ' + start);
  return appSource.slice(i, appSource.indexOf(end, i));
};

test('CL-UI-64 (1): modal opens with a quick-view section fed by the gated bundle fetch', () => {
  // Section markup in openPlaceModal, before the selected-date section.
  assert.match(appSource, /<section class="place-quick-view"[^>]*>/);
  assert.match(appSource, /id="place-quick-view-body"/);
  // Filled inside decorateV2Eval's single gated fetch (subject cards load
  // alongside the evaluation bundle; a bundle failure degrades honestly).
  assert.match(appSource, /quickHost\.innerHTML=bundle\?v2QuickViewHtml\(spot,qPlace\):`<span class="quick-none">\$\{esc\(d\(\)\.eval2_load_fail\)\}<\/span>`/);
  // The gate no longer requires eval nodes — a spot with no evaluated subject
  // still gets its quick view.
  assert.match(appSource, /if\(!quickHost&&!nodes\.length\)return;/);
});

test('CL-UI-64 (2): quick-view helpers render short chips / short word only', () => {
  const helperCode = grab('function v2DominantFailMetric', 'function ensureV2Detail');
  const prelude = `
    const V2_EVAL_METRICS={'zh-TW':{precipitation:'降水',visibility:'能見度',cloud_cover_low:'低雲'},en:{precipitation:'Precipitation',visibility:'Visibility',cloud_cover_low:'Low cloud'},ja:{precipitation:'降水',visibility:'視程',cloud_cover_low:'下層雲'}};
    const V2_FAIL_PRIORITY=['precipitation','visibility','cloud_cover_low'];
    let currentLang='zh-TW';
    let v2SubjectCards=${JSON.stringify(artifact.places)};
    const v2SubjectCardRow=(id,date)=>(v2SubjectCards[id]&&v2SubjectCards[id][date])||null;
    const v2SubjectCardShorts=(row,lang)=>((row&&row.suitable)||[]).map(s=>s.subject_short&&(s.subject_short[lang]||s.subject_short['zh-TW'])).filter(Boolean);
    const v2SubjectCardShortReason=(row,lang)=>row&&row.dominant_reason?(row.dominant_reason[lang]||row.dominant_reason['zh-TW']||''):'';
    const localDateString=()=>dayDate;
    let dayDate='2026-11-13';
    const selectedDayOffset=()=>0;
    const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    const d=()=>({v2_quick_none:'尚無速覽資料',eval2_hours:'符合時數',eval2_ok:'符合',eval2_bad:'未符',eval2_unk:'資料不足'});
    const listSep=()=>'、';
    const formatHourSegments=list=>(list||[]).join('、');
    const compactHourSegmentsText=text=>String(text||'').split('、').map(seg=>seg.includes('–')?seg.replace(/:00/g,''):seg).join('、');
    const v2EffectiveHours=(day)=>((day&&day.good_hours)||[]);
    const v2BestForSpot=null;
  `;
  const fns = new Function(prelude + helperCode +
    ';return {v2QuickViewHtml,v2DayStripHtml,v2ShortReasonWord,v2DominantFailMetric};')();
  const spot = {spot_id: 'jp-005', timezone: 'Asia/Tokyo'};

  // Clear day: short subject chips + window, no long sentences.
  const clearHtml = fns.v2QuickViewHtml(spot, null);
  assert.ok(clearHtml.includes('quick-chip'), 'clear day renders chips');
  assert.ok(clearHtml.includes('quick-window'), 'clear day renders window');
  assert.ok(!clearHtml.includes('quick-miss'));

  // Failed day: one short dominant reason word, no sentence punctuation
  // (jp-001 2026-11-13 is a failed row that carries dominant_reason).
  const missHelpers = new Function(prelude + helperCode + ';return {v2QuickViewHtml};')();
  const missHtml = missHelpers.v2QuickViewHtml({spot_id: 'jp-001', timezone: 'Asia/Tokyo'}, null);
  assert.ok(missHtml.includes('quick-miss'), 'failed day renders the short miss word');
  assert.ok(!/[。！？，]/.test(missHtml.replace(/<[^>]*>/g, '').replace('✗', '')),
    'quick view never carries a long sentence: ' + missHtml);
  // A failed row WITHOUT a dominant_reason degrades to the honest none-line —
  // never an invented cause. (CL-INT-154: the committed artifact no longer has
  // such a row, so inject a synthetic one instead of pinning live data.)
  const fnsFailed = new Function(prelude.replace("let dayDate='2026-11-13';", "let dayDate='2026-11-15';") + `
    v2SubjectCards = Object.assign({}, v2SubjectCards, { 'jp-005': Object.assign({}, v2SubjectCards['jp-005'] || {}, { '2026-11-15': { status: 'failed', suitable: [] } }) });
  ` + helperCode + ';return {v2QuickViewHtml};')();
  const failedHtml = fnsFailed.v2QuickViewHtml(spot, null);
  assert.ok(failedHtml.includes('quick-none'), 'a failed row with no dominant_reason degrades honestly');

  // No row at all: honest none-line (never invented copy).
  const noneHtml = fns.v2QuickViewHtml({spot_id: 'xx-999', timezone: 'UTC'}, null);
  assert.ok(noneHtml.includes('quick-none'));
});

test('CL-UI-68 (3): 8-day strip — info written INSIDE the cell (two lines), no hover/title carrier', () => {
  const helperCode = grab('function v2DominantFailMetric', 'function ensureV2Detail');
  const prelude = `
    const V2_EVAL_METRICS={'zh-TW':{precipitation:'降水',visibility:'能見度',cloud_cover_low:'低雲'},en:{},ja:{}};
    const V2_FAIL_PRIORITY=['precipitation','visibility','cloud_cover_low'];
    let currentLang='zh-TW';
    let v2SubjectCards={};
    const v2SubjectCardRow=()=>null;
    const v2SubjectCardShortReason=()=>'';
    const v2SubjectCardShorts=()=>[];
    const localDateString=()=>'2026-11-13';
    const selectedDayOffset=()=>0;
    const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    const d=()=>({eval2_hours:'符合時數',eval2_ok:'符合',eval2_bad:'未符',eval2_unk:'資料不足'});
    const listSep=()=>'、';
    const formatHourSegments=list=>(list||[]).join('、');
    const compactHourSegmentsText=text=>String(text||'').split('、').map(seg=>seg.includes('–')?seg.replace(/:00/g,''):seg).join('、');
    const v2EffectiveHours=(day)=>((day&&day.good_hours)||[]);
    const v2BestForSpot=null;
  `;
  const fns = new Function(prelude + helperCode +
    ';return {v2QuickViewHtml,v2DayStripHtml,v2ShortReasonWord,v2DominantFailMetric};')();
  const days = [
    {local_date: '2026-11-13', state: 'GUIDANCE_SATISFIED', good_hours: ['17:00'], conditions: []},
    {local_date: '2026-11-14', state: 'UNFAVORABLE', good_hours: [], conditions: [
      {metric: 'precipitation', day_verdict: 'FAIL'}]},
    {local_date: '2026-11-15', state: 'NOT_EVALUABLE', good_hours: [], conditions: []},
  ];
  const html = fns.v2DayStripHtml(days, ['今天', '明天', '後天'], 'Asia/Taipei', {spot_id: 'jp-003'}, 'cloud_sea', 'jp-003-P01');
  const cells = html.match(/<button[\s\S]*?<\/button>/g) || [];
  assert.equal(cells.length, 3, 'one cell per day row');
  assert.ok(html.includes('v2-ok') && html.includes('v2-bad') && html.includes('v2-unk'));
  assert.ok(html.includes('data-reason="降水"'), 'short reason word on the failed cell');
  // CL-UI-68: the text lives INSIDE the cell — CL-UI-75 compact copy:
  // met = ✓n qualifying-hours badge + abbreviated window, unmet = ✗short
  // reason, unknown = the honest label. No hover/title carrier, no
  // click-to-reveal note, no 🎯 badge (CL-UI-75 owner ruling).
  assert.ok(html.includes('<span class="v2-strip-hours">✓1</span>'),
    'met cell: qualifying-hour badge, not a sentence');
  assert.ok(html.includes('<span class="v2-strip-text">17:00</span>'),
    'met cell: lone whole-hour stamp keeps its full form');
  assert.ok(html.includes('<span class="v2-strip-text">✗降水</span>'),
    'unmet cell text: ✗short reason');
  assert.ok(html.includes('<span class="v2-strip-text">資料不足</span>'),
    'unknown cell text: the honest label');
  assert.ok(!html.includes('title='), 'no title attribute — hover is not the information carrier');
  assert.ok(!html.includes('v2-strip-note') && !html.includes('v2-strip-bar'),
    'click-to-reveal note and bare color bar retired');
  assert.ok(!html.includes('🎯') && !html.includes('v2-strip-next'),
    'CL-UI-75: the 🎯 next-window badge is retired at every breakpoint');
  // decorateV2Eval no longer wires a click -> note reveal.
  assert.ok(!appSource.includes("el.querySelectorAll('.v2-strip-cell').forEach(cell=>cell.addEventListener('click'"));
  // The modal no longer renders the 8 long day rows.
  assert.ok(!appSource.includes('v2DayHtml(day,labels[i]||day.local_date'));
});

test('CL-UI-64 (4): 拍攝條件/成立條件 collapses into an accordion (default closed, 條件 ×N)', () => {
  assert.match(appSource, /<details class="v2-cond-details"><summary class="v2-cond-summary">\$\{esc\(d\(\)\.v2_cond_count\)\.replace\('\{n\}',String\(v2CondCount\)\)\}/);
  // Default collapsed: the markup never opens the details.
  assert.ok(!/<details class="v2-cond-details"[^>]*open/.test(appSource));
  assert.match(appSource, /const v2CondCount=v2c\?\(\(v2c\.conditions\|\|\[\]\)\.length\):0;/);
  // The long metric narrative (v2-why) stays inside the accordion.
  const block = grab('const v2CondHtml=v2c?', 'return `<div class="opportunity-card');
  assert.ok(appSource.includes('v2-why'), 'why-lines remain in the collapsed layer');
  assert.ok(block.includes('</details>'));
});

test('CL-UI-64 (5): bottom hourly-forecast control stays on-page (CL-UI-79 owner ruling)', () => {
  // CL-UI-79: the control is a BUTTON, not an anchor — it must never
  // navigate away to weather-map.html. It opens the same-page weather
  // forecast modal for this place (or smooth-scrolls to a future in-modal
  // hourly table).
  assert.doesNotMatch(appSource, /<a class="place-hourly-link"/);
  assert.doesNotMatch(appSource, /place-hourly-link"[^>]*href=/);
  assert.match(appSource, /<button type="button" class="place-hourly-link" id="place-hourly-btn" data-spot-id="\$\{esc\(spot\.spot_id\|\|''\)\}">/);
  assert.match(appSource, /\$\{esc\(d\(\)\.v2_hourly_link\)\}/);
  const handler = grab("if(hourlyBtn)hourlyBtn.addEventListener('click'", "decorateV2Eval(spot)");
  assert.ok(handler.includes('openWeatherModal(latest'), 'fallback opens the same-page forecast modal');
  assert.ok(handler.includes("scrollIntoView({behavior:'smooth'"), 'in-modal table preference: smooth scroll');
  const modalBlock = grab('function openPlaceModal(spot,summaryMetric){', 'function syncModalScrollLock()');
  assert.ok(!modalBlock.includes('weather-map.html'), 'no navigation to weather-map from the place modal');
});

test('CL-UI-64 (6): i18n keys exist in all three dictionaries', () => {
  for (const key of ['v2_quick_title', 'v2_quick_none', 'v2_cond_count', 'v2_hourly_link']) {
    const count = appSource.split(key + ':').length - 1;
    assert.equal(count, 3, key + ' must exist in zh-TW/en/ja');
  }
  assert.match(appSource, /v2_quick_title:'今日速覽'/);
  assert.match(appSource, /v2_quick_title:'Today at a glance'/);
  assert.match(appSource, /v2_quick_title:'今日サマリー'/);
  assert.match(appSource, /v2_hourly_link:'查看逐小時預報 →'/);
});

test('CL-UI-64 (7): shell styles + 390px mobile rules + cache-bust stamp bumped', () => {
  for (const cls of ['.place-quick-view', '.quick-chip', '.quick-miss', '.v2-day-strip',
    '.v2-strip-cell', '.v2-strip-text', '.v2-strip-hours', '.v2-cond-details',
    '.v2-cond-details[open]', '.place-hourly-link']) {
    assert.ok(appCss.includes(cls), 'css missing ' + cls);
  }
  // CL-UI-75: the strip is ONE horizontal row of fixed-width cells that
  // scrolls horizontally at 390px — no wrap tier, no vertical one-char
  // reflow; the 🎯 badge CSS is retired with the badge.
  assert.ok(appCss.includes('@media (max-width:390px)'), '390px tier present');
  assert.ok(!appCss.includes('.v2-strip-bar') && !appCss.includes('.v2-strip-note'),
    'bare bar / note CSS retired');
  assert.ok(!appCss.includes('.v2-strip-next') && !appCss.includes('🎯'),
    'CL-UI-75: next-window badge CSS retired');
  assert.match(appCss, /\.v2-day-strip\{[^}]*flex-wrap:nowrap/);
  assert.match(appCss, /\.v2-day-strip\{[^}]*overflow-x:auto/);
  assert.match(appCss, /\.v2-strip-cell\{[^}]*width:46px[^}]*box-sizing:border-box/);
  assert.match(appCss, /\.v2-strip-text\{[^}]*white-space:nowrap[^}]*text-overflow:ellipsis/);
  assert.match(indexSource, /assets\/app\.js\?v=clui88/);
  assert.match(indexSource, /assets\/app\.css\?v=clui88/);
});
