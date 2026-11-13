// CL-UI-25: UX edge cleanup batch.
//
// 1. Language-aware fallback subject strings: a zh-TW canonical subject shown
//    in en/ja keeps its zh-TW content (honest-translation rule, CL-UI-19) but
//    the JOINER SYMBOLS follow the display language — en half-width
//    (・→' · ', ／→' / ', ＋→' + ', 與 between latin words →' & '), ja natural
//    (與 between latin words → と, ・ kept as-is).
// 2. Favicon: the homepage must not 404 on favicon.ico — index.html links
//    ./assets/favicon.ico + ./assets/favicon.svg and both files exist.
// 3. Cache-bust: app.js was edited this ticket, so index.html carries a
//    monotonic stamp bump (?v=clui41).
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, '..', '..', '..');
const appSource = readFileSync(new URL('../../../assets/app.js', import.meta.url), 'utf8');
const indexSource = readFileSync(new URL('../../../index.html', import.meta.url), 'utf8');
const grab = (start, end) => appSource.slice(appSource.indexOf(start), appSource.indexOf(end, appSource.indexOf(start)));

function makeHarness(lang) {
  const factory = new Function([
    grab('const localeText=values=>{', 'const reviewedLocaleName=values=>{'),
    grab('function fallbackConnectors(s){', 'const reviewedLocaleName=values=>{'),
    grab('const reviewedLocaleName=values=>{', 'function opportunityDisplayName'),
    `let currentLang='${lang}';`,
    'return {fallbackConnectors, reviewedLocaleName};',
  ].join('\n'));
  return factory();
}

test('CL-UI-25 A1: en fallback uses half-width connectors, content stays zh-TW', () => {
  const { fallbackConnectors } = makeHarness('en');
  assert.equal(fallbackConnectors('Griffith Observatory terraces・Los Angeles與Hollywood Sign全景'),
    'Griffith Observatory terraces · Los Angeles & Hollywood Sign全景');
  assert.equal(fallbackConnectors('A／B＋C'), 'A / B + C');
  // zh-TW 與 with CJK neighbours is content, not a latin joiner — untouched.
  assert.equal(fallbackConnectors('台北101與信義天際線夜景'), '台北101與信義天際線夜景');
});

test('CL-UI-25 A2: ja fallback keeps ・ and latin names join naturally with と', () => {
  const { fallbackConnectors } = makeHarness('ja');
  assert.equal(fallbackConnectors('Griffith Observatory terraces・Los Angeles與Hollywood Sign全景'),
    'Griffith Observatory terraces・Los AngelesとHollywood Sign全景');
  assert.equal(fallbackConnectors('台北101與信義天際線夜景'), '台北101與信義天際線夜景');
});

test('CL-UI-25 A3: zh-TW display is verbatim (no transform)', () => {
  const { fallbackConnectors } = makeHarness('zh-TW');
  assert.equal(fallbackConnectors('Griffith Observatory terraces・Los Angeles與Hollywood Sign全景'),
    'Griffith Observatory terraces・Los Angeles與Hollywood Sign全景');
});

test('CL-UI-25 A4: reviewedLocaleName routes its zh fallback through the connectors', () => {
  const en = makeHarness('en');
  const values = { 'zh-TW': '洛杉磯與好萊塢Sign夜景', en: '洛杉磯與好萊塢Sign夜景', ja: '洛杉磯與好萊塢Sign夜景' };
  assert.equal(en.reviewedLocaleName(values), '洛杉磯與好萊塢Sign夜景');
  const valuesLatin = { 'zh-TW': 'Los Angeles與Hollywood Sign全景' };
  assert.equal(en.reviewedLocaleName(valuesLatin), 'Los Angeles & Hollywood Sign全景');
});

// ---------------------------------------------------------------------------
// B: favicon + cache-bust pins
// ---------------------------------------------------------------------------
test('CL-UI-25 B1: homepage links a favicon that exists (no favicon.ico 404)', () => {
  assert.match(indexSource, /<link rel="icon"[^>]*href="\.\/assets\/favicon\.ico"/);
  assert.match(indexSource, /<link rel="icon" type="image\/svg\+xml"[^>]*href="\.\/assets\/favicon\.svg"/);
  assert.ok(existsSync(path.join(repoRoot, 'assets', 'favicon.ico')), 'assets/favicon.ico must exist');
  assert.ok(existsSync(path.join(repoRoot, 'assets', 'favicon.svg')), 'assets/favicon.svg must exist');
});

test('CL-UI-25 B2: other html pages reference the shared favicon asset', () => {
  for (const page of ['weather-map.html', 'field-intake.html', 'genre-eval.html',
    'apps/web-v2/evaluations.html', 'apps/web-v2/index.html']) {
    const src = readFileSync(path.join(repoRoot, page), 'utf8');
    assert.match(src, /<link rel="icon" href="\/assets\/favicon\.ico"/, page + ' must link the favicon');
  }
});

test('CL-UI-25 B3: index.html cache-bust stamp bumped for this app.js edit', () => {
  assert.match(indexSource, /assets\/app\.js\?v=clui88/);
  assert.match(indexSource, /assets\/app\.css\?v=clui88/);
});
