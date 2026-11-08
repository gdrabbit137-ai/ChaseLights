// CL-UI-35 contract: the URL ?lang= param takes precedence over the stored
// localStorage language (and the resolved value is written back so the stored
// preference stays in sync), and switchLanguage keeps the URL's lang param in
// step via history.replaceState — so a link like index.html?lang=zh-TW can no
// longer render Japanese just because the visitor's storage says ja.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const appSource = readFileSync(new URL('../../../assets/app.js', import.meta.url), 'utf8');
const indexSource = readFileSync(new URL('../../../index.html', import.meta.url), 'utf8');

// grab() — same source-slice helper convention as the other cl-ui tests.
const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, `source slice start not found: ${start}`);
  const j = appSource.indexOf(end, i + start.length);
  assert.ok(j > i, `source slice end not found after start: ${end}`);
  return appSource.slice(i, j);
};

// Simulate the top-level currentLang resolution (CL-UI-35 block) with a stubbed
// URL/localStorage environment: prelude sets location/localStorage, then the
// grabbed slice declares urlLang/currentLang.
const resolveInit = (urlSearch, storedLang) => {
  const f = new Function([
    `const VALID_LANGS=['zh-TW','en','ja'];`,
    `const location={search:${JSON.stringify(urlSearch)}};`,
    `const localStorage={_s:new Map([['chaselights_lang',${JSON.stringify(storedLang)}]]),`,
    `  getItem(k){return this._s.has(k)?this._s.get(k):null;},`,
    `  setItem(k,v){this._s.set(k,String(v));}};`,
    grab('const urlLang=new URLSearchParams', 'let currentDayFilter='),
    'return {currentLang, stored: localStorage.getItem("chaselights_lang")};'
  ].join('\n'));
  return f();
};

test('CL-UI-35: URL ?lang=zh-TW wins over a stored ja and writes it back', () => {
  const r = resolveInit('?lang=zh-TW', 'ja');
  assert.equal(r.currentLang, 'zh-TW');
  assert.equal(r.stored, 'zh-TW');
});

test('CL-UI-35: URL without lang falls back to the stored language', () => {
  assert.equal(resolveInit('', 'ja').currentLang, 'ja');
});

test('CL-UI-35: invalid URL lang fails closed to the stored language', () => {
  assert.equal(resolveInit('?lang=xx', 'ja').currentLang, 'ja');
});

test('CL-UI-35: switchLanguage syncs the URL lang param via replaceState', () => {
  const slice = grab('function switchLanguage', 'function switchTempUnit');
  // CL-UI-38 moved the URL context write into the shared syncContextUrl helper.
  assert.match(slice, /syncContextUrl\(\)/);
});

test('CL-UI-35: homepage cache-bust stamp bumped to clui41', () => {
  assert.match(indexSource, /assets\/app\.js\?v=clui51/);
  assert.match(indexSource, /assets\/app\.css\?v=clui53/);
});
