// CL-UI-110b (owner): single per-subject-row anatomy across the THREE
// surfaces that show qualifying windows —
//   • the 8-day strip cell (detail strip)
//   • the card's per-subject row (cl-subject-row)
//   • the modal's 題材判定 row (v2-day-sub)
// A PARTIAL window (pass_hours>0) must render the SAME hour-window anatomy
// as the best window: ○ + the qualifying window hours. The
// 「可拍（非黃金光線）」 semantics are DEMOTED — strip keeps them only in the
// tooltip (title/aria); the 題材判定 row may carry the word as a
// supplementary note. The word must never share a visible hour line again.
// pass_hours=0 keeps 「✗ 非日照時段」.
// Run: node --test --test-isolation=none apps/web-v2/tests/cl-ui-110b-subject-row-format.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const appSource = readFileSync(join(WEB, 'assets', 'app.js'), 'utf8');
const indexSource = readFileSync(join(WEB, 'index.html'), 'utf8');
const grab = (start, end) => {
  const a = appSource.indexOf(start);
  const b = appSource.indexOf(end, a + 1);
  assert.ok(a >= 0 && b > a, `source block ${start}…${end} not found`);
  return appSource.slice(a, b);
};
const esc = s => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const stripTextOf = c => (c.match(/<span class="v2-strip-text">([^<]*)<\/span>/) || [])[1] || '';
const stripTitleOf = c => (c.match(/ title="([^"]*)"/) || [])[1] || '';

// Common window fixture: a partial 06:10–06:50 window (owner's defect repro).
const win = ['06:10', '06:50'];
const dayPartial = {local_date: '2026-11-19', state: 'UNFAVORABLE', good_hours: win, conditions: [
  {metric: 'light_window', day_verdict: 'PARTIAL', pass_hours: 2},
]};
const dayBest = {local_date: '2026-11-19', state: 'GUIDANCE_SATISFIED', good_hours: win, conditions: []};

test('CL-UI-110b (1): strip — a PARTIAL window shows the window hours alone, word demoted to the tooltip', () => {
  const helperCode = grab('function formatHourSegments', 'function v2ContractThreshold')
    + grab('const V2_WINDOW_METRICS', 'function v2DayStripHtml')
    + grab('function v2DayStripHtml', '// CL-UI-64: top');
  const prelude = `
    const V2_EVAL_METRICS={'zh-TW':{light_window:'非日照時段'},en:{},ja:{}};
    const V2_FAIL_PRIORITY=['light_window'];
    let currentLang='zh-TW';
    const v2SubjectCardRow=()=>null;
    const v2SubjectCardShortReason=()=>'';
    const localDateString=()=>'2026-11-13';
    const selectedDayOffset=()=>0;
    const esc=${esc.toString()};
    const d=()=>({eval2_hours:'符合時數',eval2_ok:'符合',eval2_bad:'未符',eval2_unk:'資料不足',v2_win_partial_golden:'可拍（非黃金光線）',v2_win_partial:'可拍（非最佳光線）',v2_season_unknown:'季節窗待確認'});
    const listSep=()=>'、';
  `;
  const fns = new Function(prelude + helperCode + ';return {v2DayStripHtml};')();
  const cellsOf = html => html.match(/<button[\s\S]*?<\/button>/g) || [];
  // PARTIAL cell: same anatomy as the best-window cell — hours only.
  const cellP = cellsOf(fns.v2DayStripHtml([dayPartial], ['明天'], 'Asia/Taipei', {spot_id: 'tw-002'}, 'cloud_sea', 'tw-002-P01'))[0] || '';
  const cellB = cellsOf(fns.v2DayStripHtml([dayBest], ['明天'], 'Asia/Taipei', {spot_id: 'tw-002'}, 'cloud_sea', 'tw-002-P01'))[0] || '';
  assert.equal(stripTextOf(cellP), '○06:10–06:50', 'PARTIAL cell visible text = ○ + the window hours (best-window anatomy)');
  assert.equal(stripTextOf(cellB), '06:10–06:50', 'best-window cell visible text = the window hours');
  assert.ok(!cellP.match(/<span class="v2-strip-text">[^<]*非黃金光線/), '「非黃金光線」 never shares the visible hour line');
  assert.ok(stripTitleOf(cellP).includes('○ 可拍（非黃金光線）'), 'off-peak wording demoted to the cell tooltip/aria');
  assert.ok(!stripTitleOf(cellB).includes('非黃金光線'), 'best window keeps its clean tooltip');
});

test('CL-UI-110b (2): card — every per-subject row is 「短名： HH:MM–HH:MM 🔔」, PARTIAL windows included', () => {
  // CL-APP-09 patch-4: the row builder is the SHARED clSubjectRowLine (the
  // private-point popup renders its subject rows through the same function).
  const slice = grab('function clSubjectRowLine', '// CL-UI-91: the tier identity row');
  const prelude = `
    let currentLang='zh-TW';
    const esc=${esc.toString()};
    const colonSep=()=>currentLang==='en'?': ':'：';
    const listSep=()=>'、';
    const spot={spot_id:'tw-002'};
  `;
  const fns = new Function(prelude + grab('function formatHourSegments', 'function compactHourSegmentsText') + slice + ';return {clSubjectRowLine};')();
  // A curated PARTIAL-window subject row and a plain best-subject row share
  // the exact same anatomy: name → colon → formatHourSegments window → bell.
  const row = fns.clSubjectRowLine({name: '夕照', window: win}, 'tw-002', false);
  assert.match(row, /<span class="cl-subject-name">夕照<\/span><span class="cl-subject-colon">：<\/span><span class="cl-subject-window">06:10–06:50<\/span>/,
    'card row anatomy: 短名： HH:MM–HH:MM');
  assert.match(row, /cl-rem-btn/, 'card row keeps the 🔔 slot');
  assert.ok(!row.includes('非黃金光線'), 'the card row never injects the off-peak word');
  // Fallback (CL-UI-71) rows ride the same builder; a preformatted stamp
  // (private-point popup rows) wins over the segment list.
  const fb = fns.clSubjectRowLine({name: '○ 可拍', window: win}, 'tw-002', false);
  assert.match(fb, /<span class="cl-subject-window">06:10–06:50<\/span>/, 'fallback rows use the same window format');
  const stamped = fns.clSubjectRowLine({name: '雲海窗', stamp: '11/16 05:00'}, 'cp1', false);
  assert.match(stamped, /<span class="cl-subject-window">11\/16 05:00<\/span>/, 'stamp rows keep the SAME row anatomy');
});

test('CL-UI-110b (3): modal — 題材判定 carries the off-peak word as SUPPLEMENTARY text, never a separate hour anatomy', () => {
  const helperCode = grab('const V2_WINDOW_METRICS', 'const V2_FAIL_REASONS=')
    + grab('const V2_ELIGIBILITY_METRICS', 'function v2DaySubHtml')
    + grab('function v2DaySubHtml', '\n    function ensureV2Detail');
  const prelude = `
    let currentLang='zh-TW';
    const esc=${esc.toString()};
    const d=()=>({eval2_hours:'符合時數',eval2_ok:'符合',eval2_bad:'未符',eval2_unk:'資料不足',v2_ds_label:'今天題材判定',v2_ds_none:'題材判定僅提供今天',v2_ds_next:'下一窗',v2_ds_nonext:'今日無下一窗',v2_ds_ok_today:'今天 {t} 符合',v2_tier_shootable:'○ 可拍',v2_win_partial_golden:'可拍（非黃金光線）',v2_win_partial:'可拍（非最佳光線）',v2_season_unknown:'季節窗待確認',v2_ds_overall:'今日整體'});
    const localDateString=()=>'2026-11-19';
    const selectedDayOffset=()=>0;
    const v2SubjectCardRow=()=>null;
    const v2DayForOffset=()=>({local_date:'2026-11-19',state:'UNFAVORABLE',good_hours:['06:10','06:50'],conditions:[{metric:'light_window',day_verdict:'PARTIAL',pass_hours:2}]});
    const v2NextWindowLocal=()=>null;
    const nextWindowStamp=()=>'';
    const v2LocalNow=()=>'2026-11-19T10:00';
    const v2EffectiveHours=day=>day.good_hours||[];
    const v2SubjectCardShortReason=()=>'';
    const v2GeneralBaseline=()=>null;
    const v2DominantFailMetric=()=>null;
    const v2MetricName=()=>'';
    const v2Contract=()=>null;
    const reviewedLocaleName=()=>'';
  `;
  const fns = new Function(prelude + helperCode + ';return {v2DaySubHtml};')();
  const html = fns.v2DaySubHtml({spot_id: 'tw-002', timezone: 'Asia/Taipei'}, {opportunity_id: 'tw-002-P01', days: []});
  assert.ok(html.includes('○ 可拍（非黃金光線）'), 'the 題材判定 row keeps the off-peak word as supplementary wording');
  assert.ok(!html.includes('06:10–06:50'), 'the word row does NOT re-exhibit the hours as a second anatomy');
});

test('CL-UI-110b (4): the word is never concatenated with hours in any visible surface (source pin)', () => {
  // Retired concatenation form of the strip branch.
  assert.ok(!appSource.includes('+(goodList?\' \'+goodList:\'\')'), 'strip winPartial no longer appends hours to the word');
  // The strip branch must render hours-first anatomy.
  const stripBlock = grab('function v2DayStripHtml', '// CL-UI-64: top');
  assert.ok(stripBlock.includes("text=goodList||(winPartial==='light_window'?d().v2_win_partial_golden:d().v2_win_partial)"),
    'PARTIAL cell text = window hours (word only as an empty-hours fallback)');
  // Card row anatomy unchanged — single-truth window format via formatHourSegments
  // (now inside the shared clSubjectRowLine builder, CL-APP-09 patch-4).
  assert.ok(appSource.includes("entry&&entry.stamp!=null?esc(entry.stamp):esc(formatHourSegments((entry&&entry.window)||[]))"),
    'card per-subject row keeps the standard window format');
  // pass_hours=0 word is still routed by the reason path (✗ 非日照時段).
  assert.ok(appSource.includes("const words=dicts.fail_reason_short||{};"), 'fail-short word path intact');
});

test('CL-UI-110b (5): cache-bust stamp advanced for app.js', () => {
  assert.match(indexSource, /assets\/app\.js\?v=clui123/);
  assert.equal((indexSource.match(/\?v=clui120/g) || []).length, 2, 'app.js + app.css at clui120 (CL-UI-118b cache-bust)');
});
