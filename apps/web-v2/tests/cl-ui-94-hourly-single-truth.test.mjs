// CL-UI-94 (owner ruling, 實測案例: 大屯山助航站 11:00–15:00 狀態「⚠未符」與
// 雲海 chip 矛盾): the hourly status column is RETIRED. The 適合題材 cell IS
// the single-truth verdict (same source as the chips — subject-cards hours):
// 任一題材符合 → 綠 ✓chip；題材皆不符但一般基準過 → 灰「○ 可拍」；
// 一般也不過 →「✗ 短原因」。歷史 is told by the past-row tint alone (CL-UI-96;
// the （已過） small text was retired). New column anatomy:
// 時間｜適合題材｜口語化氣象 (＋⋯).
// Source assertions + extracted pure helper on the committed artifact, per
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
const cardsFile = (appSource.match(/V2_SUBJECT_CARDS_FILE='([^']+)'/) || [])[1];
assert.ok(cardsFile, 'subject-cards filename pinned in app.js');
const artifact = JSON.parse(readFileSync(
  join(ROOT, 'data', 'v2', 'evaluations', cardsFile), 'utf8'));

// CL-CI-36: derive the exemplars from the CURRENT artifact — one place-day
// with a curated cloud_sea fit hour (the 大屯山 contradiction class), one
// with a general-ok-only hour, one with a weather-fail hour (fog/visibility
// shape). Values are never copied into the test.
let cloudAnchor = null, okAnchor = null, failAnchor = null;
for (const [pid, days] of Object.entries(artifact.places)) {
  for (const [date, row] of Object.entries(days)) {
    const h = row.hours;
    if (!h) continue;
    const fitEntry = Object.entries(h.fit || {}).find(([, gs]) => gs.includes('cloud_sea'));
    if (fitEntry && !cloudAnchor) cloudAnchor = [pid, date, fitEntry[0]];
    const okHour = (h.ok || []).find(hh => !((h.fit || {})[hh]));
    if (okHour && !okAnchor) okAnchor = [pid, date, okHour];
    const failHour = Object.entries(h.no || {}).find(([, m]) => !['light_window','astronomical_darkness'].includes(m));
    if (failHour && !failAnchor) failAnchor = [pid, date, failHour[0], failHour[1]];
    if (cloudAnchor && okAnchor && failAnchor) break;
  }
  if (cloudAnchor && okAnchor && failAnchor) break;
}
assert.ok(cloudAnchor, 'artifact carries a curated cloud_sea fit hour');
assert.ok(okAnchor, 'artifact carries a general-ok-only hour');
assert.ok(failAnchor, 'artifact carries a weather-fail hour');

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, 'source slice not found: ' + start);
  return appSource.slice(i, appSource.indexOf(end, i));
};

const cellCode = grab('function v2HourSubjectCell', '// CL-UI-26: every 不符 verdict');
const makeCell = ({currentLang = 'zh-TW'} = {}) => new Function(
  `${cellCode}\nv2SubjectCards=${JSON.stringify(artifact)};currentLang=${JSON.stringify(currentLang)};` +
  'const d=()=>({eval2_unk:"資料不足",v2_hour_general_ok:"○ 可拍",state_outside:"🕒 非建議時段"});' +
  'const esc=(s)=>String(s);const listSep=()=>" · ";' +
  'const v2SubjectCardRow=(spotId,localDate)=>((v2SubjectCards.places||{})[spotId]||{})[localDate]||null;' +
  'return {v2HourSubjectCell};')();
const cellOf = ([pid, date, hh], lang) => makeCell({currentLang: lang})
  .v2HourSubjectCell({spot_id: pid, local_date: date}, {local_date: date, time: `${date} ${hh}`});

test('CL-UI-94 (1): 雲海 fit hour → green ✓chip (same source as the chip row) — the retired painter can never contradict it', () => {
  const [pid, date, hh] = cloudAnchor;
  const fit = cellOf(cloudAnchor);
  const short = artifact.dictionaries.genre_short_names['cloud_sea']['zh-TW'];
  assert.ok(short, 'cloud_sea short name (雲海) exists');
  assert.equal(fit.cls, 'subj-has');
  assert.ok(fit.html.includes('subj-chip'), 'chip class');
  assert.ok(fit.html.includes(short), `chip shows ${short}: ${fit.html}`);
  // single-truth assertion: the chip and the hourly verdict share the SAME
  // row.tier/hours source (subject-cards) — the old evaluations-details
  // painter has no write path left (src assertion (3) pins the no-op).
  const row = artifact.places[pid][date];
  assert.ok(row.hours.fit[hh].includes('cloud_sea'), 'the row the chip renders from carries the fit');
});

test('CL-UI-94 (2): 一般小時 → 灰「○ 可拍」；霧小時 →「✗ 短原因」', () => {
  const ok = cellOf(okAnchor);
  assert.equal(ok.html, '<span class="subj-ok">○ 可拍</span>', 'general hour = grey pill');
  assert.equal(ok.cls, 'subj-ok-row');
  const [fpid, fdate, fhh, metric] = failAnchor;
  const fail = cellOf(failAnchor);
  const word = (artifact.dictionaries.fail_reason_short[metric] || {})['zh-TW'] || '';
  assert.ok(fail.html.startsWith('<span class="subj-no">✗'), 'fail hour = ✗ short reason');
  assert.ok(fail.html.includes(word), `reason word present: ${fail.html}`);
  assert.equal(fail.cls, 'subj-no-row');
  // tri-lingual parity for both tokens
  for (const lang of ['zh-TW', 'en', 'ja']) {
    const o = cellOf(okAnchor, lang);
    assert.ok(o.html.includes('subj-ok'), `subj-ok rides every language (${lang})`);
    const f = cellOf(failAnchor, lang);
    assert.ok(f.html.includes('subj-no'), `✗ rides every language (${lang})`);
  }
});

test('CL-UI-94 (3): status column retired — three-column anatomy 時間｜適合題材｜口語化氣象 (＋⋯)', () => {
  // header: exactly th_time → th_subjects → th_plain (no th_status, no gap)
  const headIdx = appSource.indexOf('<thead><tr><th>${esc(d().th_time)}</th>');
  assert.ok(headIdx >= 0, 'hourly table header found');
  const head = appSource.slice(headIdx, appSource.indexOf('</thead>', headIdx) + 8);
  assert.equal(head, '<thead><tr><th>${esc(d().th_time)}</th><th>${esc(d().th_subjects)}</th><th>${esc(d().th_plain)}</th><th></th></tr></thead>',
    'exact 4-<th> header (data columns + ⋯)');
  // no status placeholder td anywhere in the row build; kv colspan follows 4
  const rowIdx = appSource.indexOf('rowsHtml.push(`<tr class=');
  const row = appSource.slice(rowIdx, rowIdx + 1600);
  assert.ok(!row.includes('eval2_unk'), 'no 資料不足 placeholder cell');
  assert.ok(row.includes('<td colspan="4">'), 'kv detail row spans the new column count');
  assert.ok(!appSource.includes('na-row"><td colspan="5"'), 'na line spans the new column count');
  // the evaluations-details painter is a no-op (no paint path into the table)
  const deco = grab('function decorateWeatherTimeline', 'function decorateV2Eval');
  assert.match(deco, /return;\s*\n\s*\}/, 'painter retired');
  assert.ok(!deco.includes('cells[1]'), 'no desktop paint write');
  assert.ok(!deco.includes("querySelectorAll('#timeline-mobile [data-v2t]')"), 'no mobile paint write');
  // legend describes the new cell semantics — the retired verdict words
  // (⚠️ 未符 / 資料不足) never reappear above the hourly table
  const legend = grab('legend.innerHTML=', ';');
  assert.ok(legend.includes('clui94_legend_fit') && legend.includes('v2_hour_general_ok'), 'legend = chip/○/✗/🕒 tokens');
  assert.ok(!legend.includes('state_ok') && !legend.includes('state_bad') && !legend.includes('eval2_unk'), 'no retired verdict words in the legend');
  // grey pill + ✗ semantics in CSS (green chip stays green)
  assert.match(cssSource, /\.subj-ok \{[^}]*color:var\(--cl-text-2\)/, '○ 可拍 is grey, not amber');
  assert.match(cssSource, /\.td-subjects\.subj-ok-row \{ background: color-mix\(in srgb, var\(--cl-grey-text\)/, 'general row tint is grey');
  assert.match(cssSource, /\.subj-chip \{[^}]*color:var\(--cl-green-text\)/, '✓chip keeps the green contract');
});

test('CL-UI-96 (4): 歷史 is told by the past-row tint alone — no （已過） small text', () => {
  const rowIdx = appSource.indexOf('rowsHtml.push(`<tr class=');
  const row = appSource.slice(rowIdx, rowIdx + 1600);
  assert.ok(appSource.includes("const rowClass=isBest?'best-row':(isPast?'past-row':'');"), 'past hours keep the past-row class');
  assert.ok(!row.includes('clui94_past') && !row.includes('tag-past'), '（已過） small text removed from the time cell');
  assert.ok(!row.includes('d().tag_past'), '歷史 tag retired from the hourly rows');
  const cardIdx = appSource.indexOf("card.className=`timeline-mobile-card");
  const card = appSource.slice(cardIdx, cardIdx + 3200);
  assert.ok(!card.includes('clui94_past') && !card.includes('tag-past'), 'mobile card time carries no （已過） label either');
  assert.ok(cssSource.includes('.terminal-table tr.past-row { color: var(--cl-grey) !important; background: var(--cl-bg-0); }'), 'desktop past-row stays greyed');
  assert.ok(cssSource.includes('.timeline-mobile-card.past-row { opacity: .58; background: var(--cl-bg-0); }'), 'mobile past cards stay faded');
  assert.ok(!appSource.includes('clui94_past'), 'clui94_past i18n key retired from all three dicts');
});

test('CL-UI-96 (5): cache-bust advanced — index.html serves app.js + app.css at ?v=clui102', () => {
  assert.equal((indexSource.match(/\?v=clui102/g) || []).length,4, 'app.js + app.css both at clui102');
});
