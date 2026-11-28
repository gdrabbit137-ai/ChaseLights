// CL-UI-93 (mockup-first Stage 3c, last face): genre-eval page layout redo per
// data/v2/audits/design-mockups/mockup-genre-eval.html (DESIGN-3 3d455f121).
// Semantics unchanged (evaluations bundle + details): 地區/景點/日期選擇 →
// 逐題材 8 日格（✓視窗/✗短詞/—點名缺項印在格內）、選中日同步、條件明細表
// v-pass/v-fail/v-unk。Direct-URL page: NOT in the site nav (owner ruling).
// Day-cell words come from the same subject-cards short-word dictionaries
// (referenced by metric id). No artifact-coupled literals (CL-CI-36).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..', '..', '..');
const read = (p) => readFileSync(join(ROOT, p), 'utf8');

const js = read('assets/genre-eval.js');
const html = read('genre-eval.html');

// ---------------------------------------------------------------------------
// A: extracted day-cell semantics run for real (new Function harness).
// ---------------------------------------------------------------------------
const i18nSlice = js.slice(js.indexOf('const I18N = {'), js.indexOf('/* 題材短名'));
const genreSlice = js.slice(js.indexOf('const GENRE_SHORT = {'), js.indexOf('const FAIL_SHORT = {'));
const failSlice = js.slice(js.indexOf('const FAIL_SHORT = {'), js.indexOf('/* 未評估格點名缺項'));
const unkSlice = js.slice(js.indexOf('const UNK_REASON = {'), js.indexOf('const FAIL_PRIORITY'));
const coreSlice = js.slice(js.indexOf('const FAIL_PRIORITY'), js.indexOf('/* 條件明細代表值'));
const repSlice = js.slice(js.indexOf('function representativeCondition'), js.indexOf('function condRows'));

const factory = new Function([
  i18nSlice, genreSlice, failSlice, unkSlice, coreSlice, repSlice,
  'function setLang(l){ if (I18N[l]) lang = l; }',
  'return { dayCellInfo, collapseHours, dominantFailWord, unkReason,',
  '  representativeCondition, fmtValue, fmtValueThreshold, fmtThreshold, verdictClass,',
  '  setLang, lang: () => lang };'
].join('\n'));
const api = factory();

const OPP_OK = { days: [{ state: 'GUIDANCE_SATISFIED', good_hours: ['05:00', '06:00', '08:00'], conditions: [] }] };
const OPP_FAIL = { days: [{ state: 'UNFAVORABLE', good_hours: [], conditions: [
  { metric: 'cloud_cover_mid', day_verdict: 'PASS' },
  { metric: 'precipitation', day_verdict: 'FAIL' },
] }] };
const OPP_PARTIAL = { days: [{ state: 'UNFAVORABLE', good_hours: [], conditions: [
  { metric: 'cloud_cover_low', day_verdict: 'PARTIAL' },
] }] };
const OPP_UNK_SEASON = { days: [{ state: 'NOT_EVALUABLE', good_hours: [], conditions: [
  { metric: 'seasonal_state', day_verdict: 'UNKNOWN' },
] }] };
const OPP_UNK_WATER = { days: [{ state: 'NOT_EVALUABLE', good_hours: [], conditions: [
  { metric: 'water_surface_state', day_verdict: 'UNKNOWN' },
] }] };

test('CL-UI-93 A1: satisfied day prints the collapsed window in-cell (✓ 05:00–07:00)', () => {
  api.setLang('zh-TW');
  const c = api.dayCellInfo(OPP_OK, 0);
  assert.equal(c.cls, 'ok');
  assert.equal(c.text, '✓ 05:00–07:00、08:00–09:00');
});

test('CL-UI-93 A2: collapseHours splits at gaps, single hour spans one block', () => {
  assert.equal(api.collapseHours(['07:00']), '07:00–08:00');
  assert.equal(api.collapseHours(['22:00', '23:00']), '22:00–00:00');
  assert.equal(api.collapseHours([]), '');
  api.setLang('en');
  assert.equal(api.collapseHours(['05:00', '06:00', '08:00']), '05:00–07:00, 08:00–09:00');
  api.setLang('zh-TW');
});

test('CL-UI-93 A3: unfavorable day prints the dominant fail SHORT word (✗ 雨)', () => {
  api.setLang('zh-TW');
  const c = api.dayCellInfo(OPP_FAIL, 0);
  assert.equal(c.cls, 'bad');
  assert.equal(c.text, '✗ 雨'); // precipitation outranks cloud_cover_mid in the priority order
  // PARTIAL is a legitimate photographer-facing cause (same rule as the cards).
  assert.equal(api.dayCellInfo(OPP_PARTIAL, 0).text, '✗ 低雲');
  api.setLang('en');
  assert.equal(api.dayCellInfo(OPP_FAIL, 0).text, '✗ rain');
  api.setLang('zh-TW');
});

test('CL-UI-93 A4: not-evaluable day NAMES the missing input — never a bare —', () => {
  api.setLang('zh-TW');
  assert.equal(api.dayCellInfo(OPP_UNK_SEASON, 0).text, '— 季節曆未涵蓋');
  assert.equal(api.dayCellInfo(OPP_UNK_WATER, 0).text, '— 水況資料未接入');
  api.setLang('en');
  assert.equal(api.unkReason({ conditions: [{ metric: 'seasonal_state', day_verdict: 'UNKNOWN' }] }), 'No seasonal calendar');
  api.setLang('ja');
  assert.equal(api.unkReason({ conditions: [{ metric: 'water_surface_state', day_verdict: 'UNKNOWN' }] }), '水況データ未接続');
  api.setLang('zh-TW');
  // A day cell with no data at all stays honest but labelled.
  assert.equal(api.dayCellInfo({}, 3).cls, 'unk');
  assert.match(api.dayCellInfo({}, 3).text, /^— /);
});

test('CL-UI-93 A5: representative condition picks the first qualifying hour per day state', () => {
  const detDay = { hours: [
    { local: '04:00', status: 'UNFAVORABLE', conditions: [{ metric: 'cloud_cover_total', value: 90, verdict: 'FAIL' }] },
    { local: '10:00', status: 'GUIDANCE_SATISFIED', conditions: [{ metric: 'cloud_cover_total', value: 45, verdict: 'PASS' }] },
  ] };
  const okDay = { state: 'GUIDANCE_SATISFIED', local_date: '2026-11-16' };
  const badDay = { state: 'UNFAVORABLE', local_date: '2026-11-16' };
  assert.equal(api.representativeCondition(detDay, 'cloud_cover_total', okDay).value, 45);
  assert.equal(api.representativeCondition(detDay, 'cloud_cover_total', badDay).value, 90);
  // Honest fallback: no detail hours → null (cond table renders 無資料).
  assert.equal(api.representativeCondition(null, 'visibility', okDay), null);
});

// ---------------------------------------------------------------------------
// B: day-cell contract over the REAL evaluation artifact (every place/day).
// ---------------------------------------------------------------------------
const bundle = JSON.parse(read('apps/web-v2/evaluations-latest.json'));

test('CL-UI-93 B1: every artifact day renders a truthful cell in all three languages', () => {
  let checked = 0;
  for (const p of bundle.places) {
    for (const o of (p.opportunities || [])) {
      (o.days || []).forEach((d, i) => {
        for (const lang of ['zh-TW', 'en', 'ja']) {
          api.setLang(lang);
          const c = api.dayCellInfo(o, i);
          assert.ok(['ok', 'bad', 'unk'].includes(c.cls), `cls for ${p.place_id}/${d.local_date}`);
          if (d.state === 'GUIDANCE_SATISFIED') {
            assert.equal(c.cls, 'ok');
            assert.match(c.text, /^✓ \d{2}:\d{2}–\d{2}:\d{2}/, `window in-cell for ${p.place_id}/${d.local_date}`);
          } else if (d.state === 'NOT_EVALUABLE') {
            assert.equal(c.cls, 'unk');
            // hours-absurdity ruling: the missing input must be NAMED, not a bare —.
            assert.ok(c.text.startsWith('— ') && c.text.slice(2).length > 0,
              `unk cell must name the missing input: ${p.place_id}/${d.local_date}: ${c.text}`);
            if ((d.conditions || []).some((x) => x.day_verdict === 'UNKNOWN')) {
              assert.notEqual(c.text.slice(2), lang === 'en' ? ' — not evaluated' : lang === 'ja' ? '未評価' : '未評估',
                `unk cell must name the missing input, not the generic suffix: ${p.place_id}/${d.local_date}`);
            }
          } else {
            assert.equal(c.cls, 'bad');
            assert.match(c.text, /^✗ /, `fail short word for ${p.place_id}/${d.local_date}`);
            assert.ok(c.text.slice(2).length > 0, `fail word non-empty: ${p.place_id}/${d.local_date}: ${c.text}`);
          }
        }
        checked += 1;
      });
    }
  }
  api.setLang('zh-TW');
  assert.ok(checked > 4000, `artifact days scanned: ${checked}`);
});

// ---------------------------------------------------------------------------
// C: page + script structure pins (mockup skeleton, trilingual pack, stamp).
// ---------------------------------------------------------------------------
test('CL-UI-93 C1: genre-eval.html carries the mockup skeleton (title-row/ctl/date-row/overview)', () => {
  for (const frag of ['id="page-title"', 'id="eval-meta"', 'id="region-select"', 'id="place-select"',
    'id="eval-search"', 'id="lang-select"', 'id="update-time"', 'id="date-row"', 'id="overview"']) {
    assert.ok(html.includes(frag), `genre-eval.html keeps ${frag}`);
  }
  // Shared component base comes from app.css tokens; the page defines no new
  // hex colors (CL-UI-85 rule applied page-locally).
  const style = html.match(/<style>[\s\S]*?<\/style>/)[0];
  assert.doesNotMatch(style.replace(/\/\*[\s\S]*?\*\//g, ''), /#[0-9A-Fa-f]{3,8}\b/, 'no hex outside tokens');
  assert.ok(style.includes('var(--cl-bg-1)') && style.includes('var(--cl-border)'), 'styles compose --cl-* tokens');
});

test('CL-UI-93 C2: the page stays OUT of the site nav (direct URL, owner ruling)', () => {
  const nav = html.match(/<nav class="site-nav"[\s\S]*?<\/nav>/)[0];
  assert.ok(nav, 'site-nav block present');
  assert.doesNotMatch(nav, /genre-eval\.html/);
  assert.doesNotMatch(nav, /data-nav-more/);
});

test('CL-UI-93 C3: cache-bust stamp bumped for the genre-eval.js rewrite', () => {
  assert.match(html, /assets\/genre-eval\.js\?v=clui96/);
  // Shared shells keep their pinned stamps (CL-INT-176: main's app.css stamp
  // already advanced to clui102 via CL-INT-175 — merge keeps the main-side pin).
  assert.match(html, /assets\/app\.css\?v=clui148/);
  assert.match(html, /assets\/member-auth\.js\?v=clui117/);
  assert.match(html, /assets\/favorites-client\.js\?v=clui82/);
});

test('CL-UI-93 C4: the mockup day-cell copy pack is trilingual and label-clean', () => {
  for (const key of ['tab_ok', 'tab_no', 'tab_unk', 'tab_all', 'unk_suffix', 'unk_note',
    'today', 'today_v', 'th_metric', 'cond_loading', 'r_tw', 'r_jp', 'r_us',
    'nav_cards', 'nav_weathermap', 'nav_my', 'nav_more_tools', 'nav_genre_eval', 'nav_field_intake']) {
    const re = new RegExp(`${key}: '[^']*'`, 'g');
    const hits = js.match(re) || [];
    assert.equal(hits.length, 3, `${key} exists in all three dictionaries`);
    assert.ok(!hits.some((h) => /provisional|draft|internal/.test(h)), `${key} carries no internal wording`);
  }
  // CL-UI-19: zero simplified-character residue in the ja pack.
  assert.ok(!js.includes('题材'), 'no simplified 题材 in genre-eval.js');
  assert.ok(js.includes("hours: '撮影に適した時間数'"), 'ja hours label kept (CL-UI-19 pin)');
});

test('CL-UI-93 C5: selected-day sync wiring (date pills ↔ mini days) + cond-table classes', () => {
  for (const frag of ["renderDates()", "renderOverview()", "daySel = +mday.dataset.day",
    "daySel = +b.dataset.day", "dayCellInfo(o, i)", "' cur'", 'g-head', 'g-body', 'cond-table',
    'v-pass', 'v-fail', 'v-unk', 'unk-note', 'mini-days', 'mday', 'date-pill', 'sum-tabs']) {
    assert.ok(js.includes(frag), `genre-eval.js keeps ${frag}`);
  }
});

// ---------------------------------------------------------------------------
// D: no artifact-coupled literals (CL-CI-36) — the scheduled refresh must not
//    be able to redden this suite by changing dates/windows/counts.
// ---------------------------------------------------------------------------
test('CL-UI-93 D1: no literal dates, place counts, or artifact filenames pinned', () => {
  assert.doesNotMatch(js, /2026-\d{2}-\d{2}/, 'no literal local_date');
  assert.doesNotMatch(js, /subject-cards-\d+T\d+Z\.json/, 'no literal subject-cards filename');
  assert.doesNotMatch(js, /place_count|opportunity_count/, 'no literal counts read from the artifact');
});
