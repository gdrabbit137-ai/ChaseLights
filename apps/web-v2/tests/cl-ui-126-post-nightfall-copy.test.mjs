// CL-UI-126 (owner phone report): after nightfall a spot whose day had peaked
// at ✓推薦 printed 「本日無符合題材 · 下一個符合時段：明天 05:00」 — the two
// halves contradicted each other (the day DID qualify, its hours are simply
// over). When today's own evaluation row exists, today has no remaining
// qualifying hour, and the next window falls on a LATER local date, the card
// line now reads 「今日可拍時段已結束 · 下一波推薦：明天 05:00」 (zh-TW; en/ja
// mirrored through i18n keys — never hardcoded Chinese in the logic).
//
// Run: node --test apps/web-v2/tests/cl-ui-126-post-nightfall-copy.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const appSource = readFileSync(join(WEB, 'assets', 'app.js'), 'utf8');

const grab = (start, end) => {
  const a = appSource.indexOf(start);
  assert.ok(a !== -1, `slice start not found: ${start}`);
  const b = appSource.indexOf(end, a);
  assert.ok(b !== -1, `slice end not found: ${end}`);
  return appSource.slice(a, b);
};

const COPY = {
  eval2_unk: '資料不足',
  v2_none_today: '本日無符合題材',
  v2_none_tomorrow: '明日無符合題材',
  v2_none_after: '後日無符合題材',
  v2_none_far: '當日無符合題材',
  v2_next_window: '下一個符合時段：',
  v2_day_over: '今日可拍時段已結束',
  v2_day_next: '下一波推薦：{t}',
  nw_rel_0: '今天', nw_rel_1: '明天', nw_rel_2: '後天', nw_rel_3: '大後天',
  eval2_d0: '今天', eval2_d1: '明天', eval2_d2: '後天'
};

const factory = new Function([
  'let currentDayFilter="today";',
  'let dayOffsetOverride=null;',
  "const DAY_OFFSETS={today:0,tomorrow:1,after_tomorrow:2,day3:3,day4:4,day5:5,day6:6};",
  "const isFarDay=k=>typeof DAY_OFFSETS[k]==='number'&&DAY_OFFSETS[k]>=3;",
  "const currentLang='zh-TW';",
  'const esc=s=>String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;");',
  `const d=()=>(${JSON.stringify(COPY)});`,
  grab('function selectedDayOffset', 'function localDateString'),
  grab('function localDateString', 'function selectedDateForSpot'),
  grab('function shortDateStamp', 'function nextWindowWeekday'),
  grab('function nextWindowWeekday', 'function nextWindowStamp'),
  grab('function nextWindowStamp', 'function evalDayLabels'),
  grab('const v2NoneSubjectKey', '// CL-UI-126 (owner phone report)'),
  grab('function v2NoWindowLine', '// Place names are the one intentional'),
  'return {v2NoWindowLine,localDateString,setDay:k=>{currentDayFilter=k;}};'
].join('\n'));

const { v2NoWindowLine, localDateString, setDay } = factory();
const TZ = 'Asia/Taipei';
const T0 = localDateString(TZ, 0);
const T1 = localDateString(TZ, 1);
const T_1 = localDateString(TZ, -1);

const spot = { spot_id: 'tw-001', timezone: TZ };
const best = (over = {}) => ({
  hours: 0,
  state: 'GUIDANCE_SATISFIED',
  day: { local_date: T0, state: 'GUIDANCE_SATISFIED', good_hours: ['07:00', '08:00'] },
  nextLocal: `${T1} 05:00`,
  ...over
});

test('CL-UI-126 (1): post-nightfall — today peaked, no slot left → 「今日可拍時段已結束 · 下一波推薦：明天 …」', () => {
  setDay('today');
  const html = v2NoWindowLine(spot, best());
  assert.match(html, /今日可拍時段已結束/, `new copy expected, got: ${html}`);
  assert.match(html, /下一波推薦：明天 /, `next wave names tomorrow, got: ${html}`);
  assert.ok(html.includes('05:00'), 'the next window time is kept');
  assert.ok(!html.includes('本日無符合題材'),
    'the self-contradictory 「本日無符合題材」 line is gone for an evaluated today');
});

test('CL-UI-126 (2): a next window still later TODAY keeps the ordinary none line', () => {
  setDay('today');
  const html = v2NoWindowLine(spot, best({ nextLocal: `${T0} 21:00` }));
  assert.match(html, /本日無符合題材/, `today is not over yet: ${html}`);
  assert.ok(!html.includes('今日可拍時段已結束'));
});

test('CL-UI-126 (3): no evaluation for today → 資料不足 stays (never 「已結束」)', () => {
  setDay('today');
  const html = v2NoWindowLine(spot, best({ state: 'NOT_EVALUABLE', day: { local_date: T0, state: 'NOT_EVALUABLE' } }));
  assert.match(html, /資料不足/, `insufficient-data line expected: ${html}`);
  assert.ok(!html.includes('今日可拍時段已結束'));
});

test('CL-UI-126 (4): a future day tab (tomorrow selected) keeps its own none line', () => {
  setDay('tomorrow');
  const html = v2NoWindowLine(spot, best({ day: { local_date: T1, state: 'GUIDANCE_SATISFIED' }, nextLocal: `${localDateString(TZ, 2)} 06:00` }));
  assert.match(html, /明日無符合題材/, `tomorrow's tab keeps its wording: ${html}`);
  assert.ok(!html.includes('今日可拍時段已結束'));
  setDay('today');
});

test('CL-UI-126 (5): a yesterday row can never be mistaken for today', () => {
  setDay('today');
  const html = v2NoWindowLine(spot, best({ day: { local_date: T_1, state: 'GUIDANCE_SATISFIED' } }));
  assert.ok(!html.includes('今日可拍時段已結束'), 'the today-row check is by local_date');
});

test('CL-UI-126 (6): both card surfaces render through the one helper', () => {
  assert.equal((appSource.match(/v2NoWindowLine\(spot,v2Best\)/g) || []).length, 2,
    'the summary line and the no-window line share the helper');
  assert.ok(!/📅 \$\{esc\(v2Best\.state==='NOT_EVALUABLE'/.test(appSource),
    'no surface still inlines the old none line');
});

test('CL-UI-126 (7): the new copy is i18n in all three locales (no Chinese in logic)', () => {
  assert.ok(appSource.includes("v2_day_over:'今日可拍時段已結束'"), 'zh-TW v2_day_over');
  assert.ok(appSource.includes("v2_day_over:\"Today's shooting window is over\""), 'en v2_day_over');
  assert.ok(appSource.includes("v2_day_over:'本日の撮影可能時間は終了しました'"), 'ja v2_day_over');
  assert.equal((appSource.match(/v2_day_next:/g) || []).length, 3,
    'v2_day_next exists in all three dictionaries');
  assert.equal((appSource.match(/v2_day_next:'[^']*\{t\}'/g) || []).length, 3,
    'every v2_day_next keeps the {t} slot');
  const helper = grab('function v2NoWindowLine', '// Place names are the one intentional');
  assert.ok(!/[\u4e00-\u9fff]/.test(helper.split('\n').filter((l) => !/^\s*\/\//.test(l)).join('\n')),
    'the helper body carries no hardcoded Chinese (comment lines excluded)');
});
