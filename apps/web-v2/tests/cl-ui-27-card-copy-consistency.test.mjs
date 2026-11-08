// CL-UI-27 — 未符卡文案聚焦與資訊一致性
// 1) none-copy + next window merged into ONE line; 2) 「預報狀態：」 prefix
// removed and synonymous visibility reason deduped; 3) relative-day words on
// the next-window stamp; 4) chip row all-or-nothing; stamp bump clui41.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const ROOT = new URL('../../../', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');
const appSource = readFileSync(ROOT + 'assets/app.js', 'utf8');
const indexSource = readFileSync(ROOT + 'index.html', 'utf8');

function grab(start, end) {
  const a = appSource.indexOf(start);
  const b = appSource.indexOf(end, a);
  assert.ok(a >= 0 && b > a, 'source slice not found: ' + start);
  return appSource.slice(a, b);
}

// Deterministic "today" so the relative-day math is testable: 2026-11-05.
const PRELUDE = `
let currentLang='zh-TW';
const i18nDict={
 'zh-TW':{nw_rel_0:'今天',nw_rel_1:'明天',nw_rel_2:'後天',nw_rel_3:'大後天'},
 'en':{nw_rel_0:'today',nw_rel_1:'tomorrow',nw_rel_2:'in 2 days',nw_rel_3:'in 3 days'},
 'ja':{nw_rel_0:'今日',nw_rel_1:'明日',nw_rel_2:'明後日',nw_rel_3:'3日後'}
};
const d=()=>i18nDict[currentLang];
const localDateString=(tz,off)=>'2026-11-05';
`;
function makeFns(lang) {
  const src = PRELUDE + `currentLang='${lang}';\n`
    + grab('function shortDateStamp', '// CL-UI-27: relative-day')
    + grab('function nextWindowWeekday', '// CL-DATA-06: label chain')
    + 'return {nextWindowStamp,shortDateStamp};';
  return new Function(src)();
}

test('CL-UI-27 (1): none-copy and next window render as ONE merged line', () => {
  const card = grab('function createSpotCard', 'function distanceToSpotKm');
  assert.match(card, /theme-winner v2-none">📅 \$\{esc\(v2Best\.state==='NOT_EVALUABLE'\?d\(\)\.eval2_unk:d\(\)\[v2NoneSubjectKey\(\)\]\)\}\$\{v2Best\.nextLocal\?` · \$\{esc\(d\(\)\.v2_next_window\)\}/);
  // the old separate next-window row no longer exists on the none path
  assert.ok(!card.includes('best-window-row">${esc(d().v2_next_window)}'));
});

test('CL-UI-27 (2a): the card status row drops the 「預報狀態：」 prefix', () => {
  const card = grab('function createSpotCard', 'function distanceToSpotKm');
  assert.match(card, /forecast-status-row card-meta-row">\$\{esc\(v2StateLabel\)\}\$\{esc\(v2FailReasonSuffix\(v2Best,spot\)\)\}/);
  assert.ok(!card.includes('forecast_status'), 'createSpotCard must not render d().forecast_status');
});

test('CL-UI-27 (2b): the visibility fail reason keeps one plain-language clause', () => {
  assert.ok(appSource.includes("visibility:'大霧看不到'"));
  assert.ok(!appSource.includes('大霧看不到，能見度差'), 'synonymous duplicate removed');
});

test('CL-UI-27 (3): relative-day words on the next-window stamp (zh/en/ja)', () => {
  const zh = makeFns('zh-TW');
  assert.equal(zh.nextWindowStamp('2026-11-05 23:00', 'Asia/Taipei'), '今天 11/05 23:00');
  assert.equal(zh.nextWindowStamp('2026-11-06 05:00', 'Asia/Taipei'), '明天 11/06 05:00');
  assert.equal(zh.nextWindowStamp('2026-11-07 23:00', 'Asia/Taipei'), '後天 11/07 23:00');
  assert.equal(zh.nextWindowStamp('2026-11-08 05:00', 'Asia/Taipei'), '大後天 11/08 05:00');
  // day 4+ falls back to the plain MM/DD page-header convention
  assert.equal(zh.nextWindowStamp('2026-11-10 05:00', 'Asia/Taipei'), '11/10 05:00');
  const en = makeFns('en');
  assert.equal(en.nextWindowStamp('2026-11-07 23:00', 'Asia/Taipei'), 'in 2 days · Sat 11/07 23:00');
  assert.equal(en.nextWindowStamp('2026-11-05 23:00', 'Asia/Taipei'), 'today · Thu 11/05 23:00');
  assert.equal(en.nextWindowStamp('2026-11-10 05:00', 'Asia/Taipei'), 'Tue 11/10 05:00');
  const ja = makeFns('ja');
  assert.equal(ja.nextWindowStamp('2026-11-07 23:00', 'Asia/Taipei'), '明後日 11/07 23:00');
  assert.equal(ja.nextWindowStamp('2026-11-08 05:00', 'Asia/Taipei'), '3日後 11/08 05:00');
  // non-date passthrough
  assert.equal(zh.nextWindowStamp('05:00', 'Asia/Taipei'), '05:00');
});

test('CL-UI-27 (3b): all next-window render points go through nextWindowStamp', () => {
  assert.match(appSource, /nextWindowStamp\(v2Best\.nextLocal,spot\.timezone\)/);
  assert.match(appSource, /nextWindowStamp\(summaryData\.nextLocal,tz\)/);
  assert.match(appSource, /nextWindowStamp\(nextLocal,spot\.timezone\)/);
});

test('CL-UI-27 (3c): relative-day words exist in all three dictionaries', () => {
  for (const [lang, rels] of [
    ['zh-TW', ["nw_rel_0:'今天'", "nw_rel_1:'明天'", "nw_rel_2:'後天'", "nw_rel_3:'大後天'"]],
    ['en', ["nw_rel_0:'today'", "nw_rel_1:'tomorrow'", "nw_rel_2:'in 2 days'", "nw_rel_3:'in 3 days'"]],
    ['ja', ["nw_rel_0:'今日'", "nw_rel_1:'明日'", "nw_rel_2:'明後日'", "nw_rel_3:'3日後'"]],
  ]) {
    const line = grab(`'${lang}': {`, `best_window:`);
    for (const r of rels) assert.ok(line.includes(r), lang + ' ' + r);
  }
});

test('CL-UI-27 (4): the metric-chip row is all-or-nothing', () => {
  assert.match(appSource, /return cloudChip&&tempChip\?cloudChip\+tempChip:'';/);
  assert.ok(appSource.includes('chip row is all-or-nothing'));
});

test('CL-UI-27 (5): index.html cache-bust stamp bumped to clui41', () => {
  assert.match(indexSource, /assets\/app\.js\?v=clui51/);
  assert.match(indexSource, /assets\/app\.css\?v=clui53/);
  assert.ok(!indexSource.includes('clui27'));
});