// CL-UI-38 contract: the homepage mirrors its region/date/lang context into
// the URL with history.replaceState (never pushing a history entry), and the
// URL params win over localStorage on load — ?lang= (CL-UI-35) plus the new
// ?region= and ?date= keys. ?date= uses the day-tab key space (DAY_KEYS:
// today/tomorrow/after_tomorrow/day3..day6); invalid values fail closed to
// the stored preference.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const appSource = readFileSync(new URL('../../../assets/app.js', import.meta.url), 'utf8');
const indexSource = readFileSync(new URL('../../../index.html', import.meta.url), 'utf8');
const cssSource = readFileSync(new URL('../../../assets/app.css', import.meta.url), 'utf8');

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, `source slice start not found: ${start}`);
  const j = appSource.indexOf(end, i + start.length);
  assert.ok(j > i, `source slice end not found after start: ${end}`);
  return appSource.slice(i, j);
};

// Simulate the top-level date resolution (the urlDate → currentDayFilter
// block) with a stubbed URL/localStorage environment.
const resolveDate = (urlSearch, storedDay) => {
  const f = new Function([
    `const VALID_LANGS=['zh-TW','en','ja'];`,
    `const urlLang=null;`,
    `const VALID_DAYS=['today','tomorrow','after_tomorrow','day3','day4','day5','day6'];`,
    `const location={search:${JSON.stringify(urlSearch)}};`,
    `const localStorage={_s:new Map([['chaselights_day',${JSON.stringify(storedDay)}]]),`,
    `  getItem(k){return this._s.has(k)?this._s.get(k):null;},`,
    `  setItem(k,v){this._s.set(k,String(v));}};`,
    grab('const urlDate=new URLSearchParams', '// CL-UI-16:'),
    'return {currentDayFilter, stored: localStorage.getItem("chaselights_day")};'
  ].join('\n'));
  return f();
};

test('CL-UI-38: URL ?date=day3 wins over the stored today and writes it back', () => {
  const r = resolveDate('?date=day3', 'today');
  assert.equal(r.currentDayFilter, 'day3');
  assert.equal(r.stored, 'day3');
});

test('CL-UI-38: URL without date falls back to the stored day filter', () => {
  assert.equal(resolveDate('', 'tomorrow').currentDayFilter, 'tomorrow');
});

test('CL-UI-38: invalid URL date fails closed to the stored day filter', () => {
  assert.equal(resolveDate('?date=yesterday', 'today').currentDayFilter, 'today');
});

test('CL-UI-38: syncContextUrl writes lang/region/date via replaceState only', () => {
  const fn = grab('function syncContextUrl', 'function switchLanguage');
  assert.match(fn, /history\.replaceState/);
  assert.match(fn, /searchParams\.set\('lang'/);
  assert.match(fn, /searchParams\.set\('region'/);
  assert.match(fn, /searchParams\.set\('date'/);
  assert.ok(!fn.includes('pushState'));
});

test('CL-UI-38: switchRegion/switchDay/switchLanguage all mirror the context URL', () => {
  assert.match(grab('function switchDay', 'function syncContextUrl'), /syncContextUrl\(\);/);
  assert.match(grab('function switchRegion', '// CL-UI-28 (blueprint'), /syncContextUrl\(\);/);
  assert.match(grab('function switchLanguage', 'function switchTempUnit'), /syncContextUrl\(\);/);
});

test('CL-UI-38: first load mirrors the resolved context into the URL', () => {
  assert.match(grab('function initializeApp', '// CL-UI-14/U4:'), /syncContextUrl\(\);/);
});

test('CL-UI-38: homepage cache-bust stamp bumped to clui41', () => {
  assert.match(indexSource, /assets\/app\.js\?v=clui76/);
  assert.match(indexSource, /assets\/app\.css\?v=clui75/);
});

test('CL-UI-38: narrow-viewport rule keeps the bottom-bar labels visible', () => {
  const i = cssSource.indexOf('CL-UI-38: at 390px');
  assert.ok(i >= 0, 'CL-UI-38 css block not found');
  const block = cssSource.slice(i, cssSource.indexOf('}', cssSource.indexOf('text-align', i)));
  assert.match(block, /@media \(max-width: 640px\)/);
  assert.match(block, /\.site-nav-item,\s*\n\s*\.site-nav-more-btn/);
  assert.match(block, /white-space:\s*normal/);
});
