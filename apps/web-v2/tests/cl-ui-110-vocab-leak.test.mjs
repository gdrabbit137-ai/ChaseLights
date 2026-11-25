// CL-UI-110 (CHALLENGER-18): vocabulary-leak fix — metric label dictionary
// completion + fail-closed lookup, narrow-window PARTIAL semantics, and the
// layered quick-view wording.
// Contract:
//  (1) EVERY metric that can appear in an evaluation (the full key set of
//      data/v2/copy/fail_reason_short.json words) has a trilingual label in
//      BOTH client dictionaries: assets/app.js V2_EVAL_METRICS and
//      apps/web-v2/app.mjs EVAL_METRICS. A missing key can never leak the raw
//      internal metric name again — lookups fail CLOSED ('?' + console.warn).
//  (2) A window-class metric with day_verdict=PARTIAL and pass_hours>0 must
//      never carry the day's ✗ word (the CHALLENGER-13 narrow-window
//      word-stealing disease in its PARTIAL variant — 奧萬大 11h civil-light
//      window rendered 「整天非日照」). pass_hours=0 keeps 「非日照時段」; an
//      UNKNOWN eligibility condition (seasonal_state) renders the neutral
//      「—季節窗待確認」 and never a ✗ word.
//  (3) The 「今天題材判定」 chip states the GENERAL-baseline layer explicitly
//      (「今日整體」) so it can coexist with a subject-level ✗ strip cell
//      without reading as a contradiction.
// Run: node --test --test-isolation=none apps/web-v2/tests/cl-ui-110-vocab-leak.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const appSource = readFileSync(join(WEB, 'assets', 'app.js'), 'utf8');
const mjsSource = readFileSync(join(WEB, 'apps', 'web-v2', 'app.mjs'), 'utf8');
const grab = (start, end) => {
  const a = appSource.indexOf(start);
  const b = appSource.indexOf(end, a + 1);
  assert.ok(a >= 0 && b > a, `source block ${start}…${end} not found`);
  return appSource.slice(a, b);
};
const words = JSON.parse(readFileSync(join(WEB, 'data', 'v2', 'copy', 'fail_reason_short.json'), 'utf8')).words;
const wordKeys = Object.keys(words);
const extractDict = (src, marker) => {
  const a = src.indexOf(marker);
  const b = src.indexOf('};', a);
  assert.ok(a >= 0 && b > a, 'dict block not found: ' + marker);
  return new Function('return (' + src.slice(a + marker.length, b + 1) + ')')();
};

test('CL-UI-110 (1): every fail_reason_short metric key exists in BOTH client label dictionaries', () => {
  assert.ok(wordKeys.length >= 50, 'fail_reason_short registry parsed');
  const jsDict = extractDict(appSource, 'const V2_EVAL_METRICS = ');
  const mjsDict = extractDict(mjsSource, 'const EVAL_METRICS=');
  for (const lang of ['zh-TW', 'en', 'ja']) {
    assert.ok(jsDict[lang], 'V2_EVAL_METRICS has ' + lang);
    for (const k of wordKeys) {
      assert.ok(jsDict[lang][k], `V2_EVAL_METRICS.${lang} missing ${k}`);
    }
  }
  for (const k of wordKeys) {
    assert.ok(mjsDict[k], `EVAL_METRICS (app.mjs) missing ${k}`);
    assert.ok(mjsDict[k]['zh-TW'] && mjsDict[k].en && mjsDict[k].ja, `EVAL_METRICS.${k} trilingual`);
  }
});

test('CL-UI-110 (2): label lookups fail closed — no raw `||m` fallback anywhere', () => {
  // The four audited leak paths (condition title, strip word, quick-view
  // chip, app.mjs evalMetricLabel) must all route through fail-closed
  // helpers that warn and render '?' instead of the internal metric name.
  assert.match(appSource, /console\.warn\('\[v2\] metric label missing:'/);
  assert.ok(appSource.includes("if(!v){console.warn('[v2] metric label missing:',m);return '?';}"),
    'v2MetricName fail-closed body');
  assert.ok(mjsSource.includes("if(!d){console.warn('[v2] metric label missing:',m);return '?';}"),
    'evalMetricLabel fail-closed body');
  assert.ok(!appSource.includes('[m]||m'), 'no dict[m]||m raw fallback left in app.js');
  assert.ok(!mjsSource.includes('):m};'), 'no :m raw fallback left in evalMetricLabel');
  assert.ok(appSource.includes('return v2MetricName(m);'), 'strip word routes through v2MetricName');
});

test('CL-UI-110 (3): narrow-window PARTIAL semantics in the 8-day strip', () => {
  const helperCode = grab('function formatHourSegments', 'function v2ContractThreshold')
    + grab('function v2MetricName', '// CL-COPY-01: handwritten')
    + grab('const V2_WINDOW_METRICS', 'function v2DayStripHtml')
    + grab('function v2DayStripHtml', '// CL-UI-64: top');
  const prelude = `
    const V2_EVAL_METRICS={'zh-TW':{cloud_cover_low:'低雲',light_window:'非日照時段',precipitation:'雨'},en:{},ja:{}};
    const V2_FAIL_PRIORITY=['precipitation','cloud_cover_low','light_window'];
    let currentLang='zh-TW';
    let v2SubjectCards={};
    const v2SubjectCardRow=()=>null;
    const v2SubjectCardShortReason=()=>('');
    const v2SubjectCardShorts=()=>[];
    const localDateString=()=>'2026-11-13';
    const selectedDayOffset=()=>0;
    const esc=s=>String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    const d=()=>({eval2_hours:'符合時數',eval2_ok:'符合',eval2_bad:'未符',eval2_unk:'資料不足',v2_win_partial_golden:'可拍（非黃金光線）',v2_win_partial:'可拍（非最佳光線）',v2_season_unknown:'季節窗待確認'});
    const listSep=()=>'、';
  `;
  const fns = new Function(prelude + helperCode + ';return {v2DayStripHtml};')();
  const cellsOf = html => html.match(/<button[\s\S]*?<\/button>/g) || [];
  const textOf = c => (c.match(/<span class="v2-strip-text">([^<]*)<\/span>/) || [])[1] || '';
  // 奧萬大明明天 repro: light_window PARTIAL pass_hours=11 + seasonal UNKNOWN.
  const dayAowanda = {local_date: '2026-11-18', state: 'UNFAVORABLE', good_hours: [], conditions: [
    {metric: 'seasonal_state', day_verdict: 'UNKNOWN', pass_hours: 0},
    {metric: 'precipitation', day_verdict: 'PASS', pass_hours: 24},
    {metric: 'wind_speed_10m', day_verdict: 'PASS', pass_hours: 24},
    {metric: 'light_window', day_verdict: 'PARTIAL', pass_hours: 11},
  ]};
  const htmlA = fns.v2DayStripHtml([dayAowanda], ['明天'], 'Asia/Taipei', {spot_id: 'tw-141'}, 'seasonal_plant', 'tw-141-P01');
  const cellA = cellsOf(htmlA)[0] || '';
  assert.ok(!cellA.includes('✗'), 'a passing-11h window never carries ✗');
  assert.ok(!cellA.includes('非日照時段'), '「非日照時段」 never shown while the window passes');
  assert.ok(cellA.includes('—季節窗待確認'), 'the UNKNOWN eligibility blocker shows the neutral word');
  // Pure window partial: window passes part of the day, nothing else fails → ○.
  const dayWin = {local_date: '2026-11-19', state: 'UNFAVORABLE', good_hours: ['06:00', '07:00'], conditions: [
    {metric: 'light_window', day_verdict: 'PARTIAL', pass_hours: 2},
  ]};
  const cellW = cellsOf(fns.v2DayStripHtml([dayWin], ['後天'], 'Asia/Taipei', {spot_id: 'tw-002'}, 'cloud_sea', 'tw-002-P01'))[0] || '';
  assert.ok(cellW.includes('○'), 'partial-window day renders ○');
  // CL-UI-110b (owner): the visible cell text is the window hours ALONE —
  // the same anatomy as the best-window cell. 「可拍（非黃金光線）」 lives
  // ONLY in the tooltip (title/aria), never in the visible hour line.
  assert.equal(textOf(cellW), '○06–07', 'PARTIAL cell shows ○ + the window hours (standard anatomy)');
  assert.ok(cellW.includes('○ 可拍（非黃金光線）'), 'off-peak wording demoted to the tooltip/aria');
  // pass_hours=0 → the whole day is out: ✗非日照時段 stays.
  const dayZero = {local_date: '2026-11-20', state: 'UNFAVORABLE', good_hours: [], conditions: [
    {metric: 'light_window', day_verdict: 'FAIL', pass_hours: 0},
  ]};
  const cellZ = cellsOf(fns.v2DayStripHtml([dayZero], ['11/22'], 'Asia/Taipei', {spot_id: 'tw-002'}, 'cloud_sea', 'tw-002-P01'))[0] || '';
  assert.ok(cellZ.includes('✗非日照時段'), 'pass_hours=0 keeps the honest all-day-out word');
  // A real weather failure still wins over window/UNKNOWN layers.
  const dayRain = {local_date: '2026-11-21', state: 'UNFAVORABLE', good_hours: [], conditions: [
    {metric: 'precipitation', day_verdict: 'FAIL', pass_hours: 8},
    {metric: 'light_window', day_verdict: 'PARTIAL', pass_hours: 11},
    {metric: 'seasonal_state', day_verdict: 'UNKNOWN', pass_hours: 0},
  ]};
  const cellR = cellsOf(fns.v2DayStripHtml([dayRain], ['11/23'], 'Asia/Taipei', {spot_id: 'tw-002'}, 'cloud_sea', 'tw-002-P01'))[0] || '';
  assert.ok(cellR.includes('✗雨'), 'a genuine weather failure keeps ✗');
  assert.ok(!cellR.includes('非日照時段'), 'window PARTIAL does not steal the day word');
});

test('CL-UI-110 (4): layered quick-view wording — chip states the general baseline', () => {
  assert.ok(appSource.includes('${t.v2_tier_shootable}（${t.v2_ds_overall}）'),
    'shootable chip reads 「○ 可拍（今日整體）」');
  for (const [lang, overall] of [['zh-TW', '今日整體'], ['en', 'overall today'], ['ja', '本日全体']]) {
    assert.ok(appSource.includes(`v2_ds_overall:'${overall}'`), `v2_ds_overall in ${lang}`);
  }
  for (const [lang, word] of [['zh-TW', '可拍（非黃金光線）'], ['en', 'Shootable (off-peak light)'], ['ja', '撮影可（ゴールデン時間外）']]) {
    assert.ok(appSource.includes(`v2_win_partial_golden:'${word}'`), `v2_win_partial_golden in ${lang}`);
  }
  for (const [lang, word] of [['zh-TW', '季節窗待確認'], ['en', 'Season window unconfirmed'], ['ja', '季節窓は未確認']]) {
    assert.ok(appSource.includes(`v2_season_unknown:'${word}'`), `v2_season_unknown in ${lang}`);
  }
  // The rowless subject-branch mirrors the strip semantics (never a raw name).
  assert.ok(appSource.includes('v2EligibilityUnknownMetric'), 'eligibility-UNKNOWN helper wired');
  assert.ok(appSource.includes('v2WindowPartialMetric'), 'window-PARTIAL helper wired');
});

test('CL-UI-110 (5): cache-bust stamp advanced for app.js', () => {
  const indexSource = readFileSync(join(WEB, 'index.html'), 'utf8');
  assert.match(indexSource, /assets\/app\.js\?v=clui127/);
});
