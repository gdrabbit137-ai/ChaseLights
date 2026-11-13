// CL-UI-73: hourly 「適合題材」 column in the forecast modal's hourly table.
// Data layer: build_subject_cards.py emits per-place×date hour buckets
// (fit/ok/no/unk/na). Renderer semantics: curated subject fits the hour →
// green chips; no subject but the hourly general floor passes → yellow
// 「○ 一般拍攝」 (CHALLENGER-14/C: not the day-tier 「○ 可拍」); a night hour
// with clean weather no curated window covers → neutral 「🕒 非建議時段」;
// floor fails → gray 「✗ <short reason>」; missing artifact/hour/fields → an
// honest dash (fail-closed). Source assertions + extracted pure helper, per
// the established V1-shell test pattern.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, '..', '..', '..');
const appSource = readFileSync(join(ROOT, 'assets', 'app.js'), 'utf8');
const cssSource = readFileSync(join(ROOT, 'assets', 'app.css'), 'utf8');
const indexSource = readFileSync(join(ROOT, 'index.html'), 'utf8');
// CL-CI-36: the artifact is read through the SAME stable pointer app.js uses
// (V2_SUBJECT_CARDS_FILE) — never a filename copied into the test.
const cardsFile = (appSource.match(/V2_SUBJECT_CARDS_FILE='([^']+)'/) || [])[1];
assert.ok(cardsFile, 'subject-cards filename pinned in app.js');
const artifact = JSON.parse(readFileSync(
  join(ROOT, 'data', 'v2', 'evaluations', cardsFile), 'utf8'));

// CL-CI-36: the scheduled refresh slides the 8-day window every run, so the
// helper-semantics exemplar is DERIVED from the current artifact: one
// place-day whose hour buckets cover all three render branches (a curated
// fit hour, a general-ok hour, and a neutral na hour). tw-142 安平漁人碼頭
// was the original pinned case.
let anchor = null;
outer:
for (const [pid, days] of Object.entries(artifact.places)) {
  for (const [date, row] of Object.entries(days)) {
    const h = row.hours;
    if (!h) continue;
    const fitHour = Object.keys(h.fit || {})[0];
    const okHour = (h.ok || []).find(hh => !((h.fit || {})[hh]));
    const naHour = (h.na || [])[0];
    if (fitHour && okHour && naHour) { anchor = [pid, date]; break outer; }
  }
}
assert.ok(anchor, 'artifact carries a row with fit/ok/na hour buckets');

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, 'source slice not found: ' + start);
  return appSource.slice(i, appSource.indexOf(end, i));
};

const cellCode = grab('function v2HourSubjectCell', '// CL-UI-26: every 不符 verdict');
const makeCell = ({currentLang = 'zh-TW', dict = artifact} = {}) => new Function(
  `${cellCode}\nv2SubjectCards=${JSON.stringify(dict)};currentLang=${JSON.stringify(currentLang)};` +
  'const d=()=>({eval2_unk:"資料不足",v2_hour_general_ok:"○ 一般拍攝",state_outside:"🕒 非建議時段"});' +
  'const esc=(s)=>String(s);const listSep=()=>" · ";;' +
  'const v2SubjectCardRow=(spotId,localDate)=>((v2SubjectCards.places||{})[spotId]||{})[localDate]||null;' +
  'return {v2HourSubjectCell};')();

test('CL-UI-73 (1): tri-lingual column header + the column rides after the status column', () => {
  for (const lang of ['zh-TW', 'en', 'ja']) {
    assert.match(appSource, new RegExp(`th_subjects:'[^']+'`), `th_subjects exists (${lang})`);
  }
  assert.ok(appSource.includes("th_subjects:'適合題材'"), 'zh-TW header');
  assert.ok(appSource.includes("th_subjects:'Subjects'"), 'en header');
  assert.ok(appSource.includes("th_subjects:'適合テーマ'"), 'ja header');
  // header: 狀態 then 適合題材, before the metric columns
  const headIdx = appSource.indexOf('thead.innerHTML=`<tr>');
  const head = appSource.slice(headIdx, headIdx + 600);
  assert.ok(head.includes('<th class="key-metric">${d().th_subjects}</th>'), 'subjects <th>');
  assert.ok(head.indexOf('th_status') < head.indexOf('th_subjects'), 'after 狀態');
  // row cell: the subjects <td> sits between the status <td> and the Kp <td>,
  // so the status column keeps its cells[1] index (CL-UI-43 painters rely on it)
  const rowIdx = appSource.indexOf('(spot.hourly_forecast||[]).forEach(item=>{');
  // CL-UI-78: the loop body grew (date-group banner before the row build), so
  // the window widened — the pinned substrings themselves are unchanged.
  const row = appSource.slice(rowIdx, rowIdx + 3200);
  assert.ok(row.includes('<td class="td-subjects ${subjCell.cls}">${subjCell.html}</td>'), 'subjects <td>');
  assert.ok(row.indexOf('eval2_unk') < row.indexOf('td-subjects'), 'after the status cell');
  // CL-UI-82: the mobile card carries the subject on the mainline (能拍：題材名)
  assert.ok(row.includes('tm-mainline-subj'), 'mobile mainline subject line');
});

test('CL-UI-73 (2): helper semantics on the committed artifact (derived anchor)', () => {
  const cell = makeCell().v2HourSubjectCell;
  const [anchorId, anchorDate] = anchor;
  const item = (h) => ({local_date: anchorDate, time: `${anchorDate} ${h}`});
  const twRow = artifact.places[anchorId][anchorDate];
  assert.ok(twRow.hours, `${anchorId} ${anchorDate} carries hour buckets`);
  // a curated fit hour → green chip with the genre short name
  const fitHour = Object.keys(twRow.hours.fit)[0];
  const fitGenre = twRow.hours.fit[fitHour][0];
  const fit = cell({spot_id: anchorId, local_date: anchorDate}, item(fitHour));
  const fitShort = artifact.dictionaries.genre_short_names[fitGenre]['zh-TW'];
  assert.ok(fitShort, `${fitGenre} short name exists`);
  assert.ok(fit.html.includes(fitShort), `chip shows ${fitShort}: ${fit.html}`);
  assert.ok(fit.html.includes('subj-chip'), 'chip class');
  assert.equal(fit.cls, 'subj-has');
  // a general-ok hour (no curated subject) → yellow ○ 一般拍攝
  // (CHALLENGER-14/C: the HOUR floor pass is not the day tier ○ 可拍)
  const okHour = (twRow.hours.ok || []).find(hh => !((twRow.hours.fit || {})[hh]));
  const ok = cell({spot_id: anchorId, local_date: anchorDate}, item(okHour));
  assert.equal(ok.html, '<span class="subj-ok">○ 一般拍攝</span>');
  assert.equal(ok.cls, 'subj-ok-row');
  // a neutral na hour → 🕒 非建議時段
  // (CHALLENGER-14/B: never a failure word, never ○)
  const naHour = twRow.hours.na[0];
  const na = cell({spot_id: anchorId, local_date: anchorDate}, item(naHour));
  assert.ok(na.html.includes('🕒') && na.html.includes('非建議時段'), `neutral: ${na.html}`);
  assert.ok(!na.html.includes('✗'), 'no failure word on a neutral night hour');
  assert.equal(na.cls, 'subj-na-row');
  // a date/hour the artifact never covers → honest dash
  const dash = cell({spot_id: 'tw-999', local_date: '2099-01-01'}, {time: '2099-01-01 10:00'});
  assert.equal(dash.cls, 'subj-unknown');
  assert.ok(dash.html.includes('subj-dash'), 'dash class');
});

test('CL-UI-73 (3): fail-closed — unknown fields and missing rows never invent a verdict', () => {
  const tree = JSON.parse(JSON.stringify(artifact));
  tree.places['xx-000'] = {'2026-01-01': {status: 'clear', suitable: [],
    hours: {ok: [], no: {}, fit: {}, unk: ['11:00'], na: []}}};
  const cell = makeCell({dict: tree}).v2HourSubjectCell;
  const unknown = cell({spot_id: 'xx-000', local_date: '2026-01-01'}, {local_date: '2026-01-01', time: '2026-01-01 11:00'});
  assert.equal(unknown.cls, 'subj-unknown', 'incomplete fields → no verdict');
  const missing = cell({spot_id: 'xx-000', local_date: '2026-01-01'}, {local_date: '2026-01-01', time: '2026-01-01 23:00'});
  assert.equal(missing.cls, 'subj-unknown', 'hour with no weather row → no verdict');
  // an artifact without the hours key at all (old schema) → no verdict, no crash
  // (CL-CI-36: the stripped row is the derived anchor, not a pinned place/day)
  const [anchorId, anchorDate] = anchor;
  const legacy = JSON.parse(JSON.stringify(artifact));
  delete legacy.places[anchorId][anchorDate].hours;
  const cell2 = makeCell({dict: legacy}).v2HourSubjectCell;
  const old = cell2({spot_id: anchorId, local_date: anchorDate}, {local_date: anchorDate, time: `${anchorDate} 12:00`});
  assert.equal(old.cls, 'subj-unknown');
});

test('CL-UI-73 (4): artifact shape — every row has fit/ok/no/unk/na buckets, reasons resolve', () => {
  let rows = 0, fitHours = 0;
  for (const place of Object.values(artifact.places)) {
    for (const row of Object.values(place)) {
      const hours = row.hours;
      assert.ok(hours, 'row carries hours');
      assert.deepEqual(Object.keys(hours).sort(), ['fit', 'na', 'no', 'ok', 'unk']);
      assert.ok(Array.isArray(hours.ok) && Array.isArray(hours.unk) && Array.isArray(hours.na));
      for (const metric of Object.values(hours.no)) {
        assert.ok(artifact.dictionaries.fail_reason_short[metric], `reason word: ${metric}`);
        // CHALLENGER-14/B: light_window never names an HOUR failure
        assert.notEqual(metric, 'light_window');
      }
      // CHALLENGER-14/B: one hour, one bucket — no fit∩no / fit∩na overlap
      assert.ok(!Object.keys(hours.fit).some(hh => hh in hours.no), 'fit∩no empty');
      assert.ok(!Object.keys(hours.fit).some(hh => hours.na.includes(hh)), 'fit∩na empty');
      for (const genres of Object.values(hours.fit)) {
        for (const g of genres) {
          assert.ok(artifact.dictionaries.genre_short_names[g], `genre short: ${g}`);
        }
        fitHours++;
      }
      rows++;
    }
  }
  assert.ok(rows > 3000, `row count ${rows}`);
  assert.ok(fitHours > 1000, `fitting-hour count ${fitHours}`);
});

test('CL-UI-73 (5): visual rhythm — cell tint classes + the clui89 stamps', () => {
  for (const cls of ['.td-subjects.subj-has', '.td-subjects.subj-ok-row', '.td-subjects.subj-na-row', '.td-subjects.subj-no-row', '.subj-chip', '.subj-na', '.timeline-mobile-subjects']) {
    assert.ok(cssSource.includes(cls), `css has ${cls}`);
  }
  assert.match(indexSource, /assets\/app\.js\?v=clui89/);
  assert.match(indexSource, /assets\/app\.css\?v=clui89/);
});
