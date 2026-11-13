// CL-UI-73: hourly 「適合題材」 column in the forecast modal's hourly table.
// Data layer: build_subject_cards.py emits per-place×date hour buckets
// (fit/ok/no/unk). Renderer semantics: curated subject fits the hour → green
// chips; no subject but the hourly general floor passes → yellow 「○ 可拍」;
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
const artifact = JSON.parse(readFileSync(
  join(ROOT, 'data', 'v2', 'evaluations', 'subject-cards-20261112T202312Z.json'), 'utf8'));

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, 'source slice not found: ' + start);
  return appSource.slice(i, appSource.indexOf(end, i));
};

const cellCode = grab('function v2HourSubjectCell', '// CL-UI-26: every 不符 verdict');
const makeCell = ({currentLang = 'zh-TW', dict = artifact} = {}) => new Function(
  `${cellCode}\nv2SubjectCards=${JSON.stringify(dict)};currentLang=${JSON.stringify(currentLang)};` +
  'const d=()=>({eval2_unk:"資料不足",v2_tier_shootable:"○ 可拍"});' +
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
  const row = appSource.slice(rowIdx, rowIdx + 2000);
  assert.ok(row.includes('<td class="td-subjects ${subjCell.cls}">${subjCell.html}</td>'), 'subjects <td>');
  assert.ok(row.indexOf('eval2_unk') < row.indexOf('td-subjects'), 'after the status cell');
  // mobile card carries the same line
  assert.ok(row.includes('timeline-mobile-subjects ${subjCell.cls}'), 'mobile subjects line');
});

test('CL-UI-73 (2): helper semantics on the committed artifact (tw-142 安平漁人碼頭)', () => {
  const cell = makeCell().v2HourSubjectCell;
  const item = (h) => ({local_date: '2026-11-13', time: `2026-11-13 ${h}`});
  const twRow = artifact.places['tw-142']['2026-11-13'];
  assert.ok(twRow.hours, 'tw-142 2026-11-13 carries hour buckets');
  // 17:00 → sunset chip (green)
  const fit = cell({spot_id: 'tw-142', local_date: '2026-11-13'}, item('17:00'));
  const sunsetShort = artifact.dictionaries.genre_short_names.sunset['zh-TW'];
  assert.ok(sunsetShort, 'sunset short name exists');
  assert.ok(fit.html.includes(sunsetShort), `chip shows ${sunsetShort}: ${fit.html}`);
  assert.ok(fit.html.includes('subj-chip'), 'chip class');
  assert.equal(fit.cls, 'subj-has');
  // 12:00 → no subject, general floor ok → yellow ○ 可拍
  const ok = cell({spot_id: 'tw-142', local_date: '2026-11-13'}, item('12:00'));
  assert.equal(ok.html, '<span class="subj-ok">○ 可拍</span>');
  assert.equal(ok.cls, 'subj-ok-row');
  // 02:00 → floor fails (light_window) → gray ✗ 光線不對
  const no = cell({spot_id: 'tw-142', local_date: '2026-11-13'}, item('02:00'));
  assert.ok(no.html.includes('✗') && no.html.includes('光線不對'), `short reason: ${no.html}`);
  assert.equal(no.cls, 'subj-no-row');
  // a date/hour the artifact never covers → honest dash
  const dash = cell({spot_id: 'tw-999', local_date: '2099-01-01'}, {time: '2099-01-01 10:00'});
  assert.equal(dash.cls, 'subj-unknown');
  assert.ok(dash.html.includes('subj-dash'), 'dash class');
});

test('CL-UI-73 (3): fail-closed — unknown fields and missing rows never invent a verdict', () => {
  const tree = JSON.parse(JSON.stringify(artifact));
  tree.places['xx-000'] = {'2026-01-01': {status: 'clear', suitable: [],
    hours: {ok: [], no: {}, fit: {}, unk: ['11:00']}}};
  const cell = makeCell({dict: tree}).v2HourSubjectCell;
  const unknown = cell({spot_id: 'xx-000', local_date: '2026-01-01'}, {local_date: '2026-01-01', time: '2026-01-01 11:00'});
  assert.equal(unknown.cls, 'subj-unknown', 'incomplete fields → no verdict');
  const missing = cell({spot_id: 'xx-000', local_date: '2026-01-01'}, {local_date: '2026-01-01', time: '2026-01-01 23:00'});
  assert.equal(missing.cls, 'subj-unknown', 'hour with no weather row → no verdict');
  // an artifact without the hours key at all (old schema) → no verdict, no crash
  const legacy = JSON.parse(JSON.stringify(artifact));
  delete legacy.places['tw-142']['2026-11-13'].hours;
  const cell2 = makeCell({dict: legacy}).v2HourSubjectCell;
  const old = cell2({spot_id: 'tw-142', local_date: '2026-11-13'}, {local_date: '2026-11-13', time: '2026-11-13 12:00'});
  assert.equal(old.cls, 'subj-unknown');
});

test('CL-UI-73 (4): artifact shape — every row has fit/ok/no/unk buckets, reasons resolve', () => {
  let rows = 0, fitHours = 0;
  for (const place of Object.values(artifact.places)) {
    for (const row of Object.values(place)) {
      const hours = row.hours;
      assert.ok(hours, 'row carries hours');
      assert.deepEqual(Object.keys(hours).sort(), ['fit', 'no', 'ok', 'unk']);
      assert.ok(Array.isArray(hours.ok) && Array.isArray(hours.unk));
      for (const metric of Object.values(hours.no)) {
        assert.ok(artifact.dictionaries.fail_reason_short[metric], `reason word: ${metric}`);
      }
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

test('CL-UI-73 (5): visual rhythm — cell tint classes + the clui76 stamps', () => {
  for (const cls of ['.td-subjects.subj-has', '.td-subjects.subj-ok-row', '.td-subjects.subj-no-row', '.subj-chip', '.timeline-mobile-subjects']) {
    assert.ok(cssSource.includes(cls), `css has ${cls}`);
  }
  assert.match(indexSource, /assets\/app\.js\?v=clui76/);
  assert.match(indexSource, /assets\/app\.css\?v=clui76/);
});
