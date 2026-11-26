// CL-I18N-12C: homepage cards + forecast modal — 393px overflow, translation
// leaks and touch targets (audit items V4, V5, V6, V7, V9, V10).
//
// These are source-contract tests: they pin the invariants that made the audit
// defects possible, not a screenshot. The live evidence for the same rules is
// in the ticket (before/after measurements at 393×852).
//
//  (1) the modal legend is a real list: separators exist as DOM spans and the
//      container actually carries the `.timeline-legend` class (it used to be
//      created with an id only, so the flex/gap rule never matched and the five
//      items rendered as one oversized glued sentence);
//  (2) en/ja never print Chinese: the "Best for selected date" subject name
//      falls back to the localised genre instead of the zh-TW opportunity name,
//      and the two Chinese provenance layer labels have en/ja copies;
//  (3) the ja place name for 助航站 is not a railway station (駅);
//  (4) tap targets are ≥44×44 CSS px on phones (fav ★, hourly ⋯, day tabs,
//      close ×, tier chips, subject chips) while the desktop rules are intact;
//  (5) an EMPTY quota chip occupies no layout space.
//
// Run: node --test apps/web-v2/tests/cl-i18n-12-cards.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const appSource = readFileSync(join(WEB, 'assets', 'app.js'), 'utf8');
const cssSource = readFileSync(join(WEB, 'assets', 'app.css'), 'utf8');
const navCss = readFileSync(join(WEB, 'assets', 'site-nav.css'), 'utf8');

const CJK = /[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]/;

// The phone block added by this ticket — every assertion below reads only that
// block, so a desktop rule can never satisfy a phone contract by accident.
function mediaBlock(source, opener) {
  const start = source.indexOf(opener);
  assert.ok(start >= 0, `missing media block ${opener}`);
  let depth = 0;
  for (let i = source.indexOf('{', start); i < source.length; i++) {
    if (source[i] === '{') depth++;
    else if (source[i] === '}') {
      depth--;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error(`unterminated media block ${opener}`);
}
const phoneStart = cssSource.indexOf('CL-I18N-12C — homepage cards');
assert.ok(phoneStart >= 0, 'the CL-I18N-12C section exists in app.css');
const phoneCss = mediaBlock(cssSource.slice(phoneStart), '@media (max-width:640px)');

// --- (1) legend -----------------------------------------------------------
test('CL-I18N-12C (1a): the legend container carries the .timeline-legend class the stylesheet keys on', () => {
  assert.match(appSource, /legend\.className\s*=\s*'timeline-legend'/, 'the legend div is created with an id only — CSS never matched it');
  assert.match(appSource, /legend\.setAttribute\('role',\s*'note'\)/);
});

test('CL-I18N-12C (1b): the legend items are joined by real separator spans, not by flex gap alone', () => {
  const block = appSource.slice(appSource.indexOf("legend.className='timeline-legend'"),
    appSource.indexOf('const isAurora=activeTheme'));
  assert.match(block, /class="legend-sep" aria-hidden="true"/, 'a separator element sits between items');
  assert.equal((block.match(/'legend-ok'/g) || []).length, 1, 'the chip item is listed once');
  assert.match(block, /\[ 'legend-bad', d\(\)\.v2_hour_general_ok \]|\[\s*'legend-bad',d\(\)\.v2_hour_general_ok\s*\]/, '○ 可拍 is its own item');
  assert.match(block, /v2_tier_not_recommended/, '✗ 不宜 is its own item');
  assert.match(block, /state_outside/, '🕒 off-window is its own item');
  // and the separator is styled (never a 0-width glyph)
  assert.match(cssSource, /\.timeline-legend \.legend-sep\{[^}]*color:/, 'the separator has an explicit colour');
});

test('CL-I18N-12C (1c): the zh-TW chip item does not repeat the two verdict items next to it', () => {
  const zh = appSource.slice(appSource.indexOf("'zh-TW': {"), appSource.indexOf("'en': {"));
  const m = zh.match(/clui94_legend_fit:'([^']*)'/);
  assert.ok(m, 'clui94_legend_fit present in zh-TW');
  assert.ok(!/○ 可拍|✕ 不宜|✗ 不宜/.test(m[1]),
    `the chip item describes the chip only, the verdicts follow as their own items: ${m[1]}`);
});

// --- (2) no Chinese in en/ja ---------------------------------------------
test('CL-I18N-12C (2a): every modal string this ticket touched exists in all three dictionaries', () => {
  const keys = ['best_theme', 'legend_title', 'clui94_legend_fit', 'clui94_legend_no', 'state_outside',
    'eval2_hours', 'close_weather', 'prov_title'];
  for (const key of keys) {
    const occurrences = (appSource.match(new RegExp(`\\b${key}:'`, 'g')) || []).length;
    assert.ok(occurrences >= 3, `${key} must exist in zh-TW/en/ja (found ${occurrences})`);
  }
});

test('CL-I18N-12C (2b): the "Best for selected date" name never renders CJK in en/ja', () => {
  assert.match(appSource, /function localeSafeSubjectName\(name,theme\)/, 'the locale-safe subject resolver exists');
  const fn = appSource.slice(appSource.indexOf('function localeSafeSubjectName'),
    appSource.indexOf('const tempUnitLabel'));
  assert.match(fn, /currentLang==='zh-TW'\)return name/, 'zh-TW keeps the reviewed name');
  assert.match(fn, /CJK_NAME_RE\.test\(name\)/, 'en/ja reject a CJK-only name');
  assert.match(fn, /themeLabel\(/, 'the fallback is the localised subject genre');
  assert.match(appSource, /const selSubject=localeSafeSubjectName\(/, 'the modal headline goes through it');
});

test('CL-I18N-12C (2c): the two Chinese provenance layer labels have en/ja copies', () => {
  const block = appSource.slice(appSource.indexOf('const PROV_LAYER_LABELS'),
    appSource.indexOf('async function loadProvLayers'));
  assert.match(block, /'CAMS 空氣霧霾（CAMS GLOBAL）':\{en:'[^']*',ja:'[^']*'\}/, 'CAMS haze label translated');
  assert.match(block, /'Himawari-9 雲圖':\{en:'[^']*',ja:'[^']*'\}/, 'Himawari label translated');
  // en copy must be CJK-free; ja copy must be a real translation (kanji are
  // native to ja, so the guard is "not the zh-TW string" rather than "no Han").
  for (const m of block.matchAll(/en:'([^']*)'/g)) assert.ok(!CJK.test(m[1]), `en copy is CJK-free: ${m[1]}`);
  const pairs = [...block.matchAll(/'([^']*)':\{en:'([^']*)',ja:'([^']*)'\}/g)];
  assert.equal(pairs.length, 2, 'both Chinese labels carry an en+ja pair');
  for (const [, zh, en, ja] of pairs) {
    assert.notEqual(ja, zh, `ja is translated, not the zh-TW string (${zh})`);
    assert.ok(/^(CAMS|Himawari)/.test(en) && /^(CAMS|Himawari)/.test(ja), 'the vendor name survives both copies');
  }
  assert.match(appSource, /provLayerLabel\(label\)/, 'the render path uses the locale label');
});

// --- (3) ja place name ----------------------------------------------------
test('CL-I18N-12C (3): 助航站 is an aviation navaid in ja, never a railway station (駅)', () => {
  const start = appSource.indexOf('const NAME_LOCALE_FIX');
  const block = appSource.slice(start, appSource.indexOf('const categoryLabel', start));
  const map = block.match(/'大屯山助航駅':\s*'([^']*)'/);
  assert.ok(map, 'the committed ja string is corrected');
  assert.ok(!/駅/.test(map[1]), `the rendered ja name is not a train station: ${map[1]}`);
  assert.ok(!/站/.test(map[1]), `the rendered ja name is not the zh-TW word either: ${map[1]}`);
});

// --- (4) touch targets ----------------------------------------------------
const touchRules = [
  ['fav button (★)', /\.fav-btn\{[^}]*width:44px;height:44px/],
  ['hourly ⋯ toggle', /\.clui87-more\{[^}]*min-width:44px;min-height:44px/],
  ['modal day tabs', /\.modal-day-btn\{min-height:44px\}/],
  ['modal close ×', /\.modal \.close-btn\{[^}]*width:44px;height:44px/],
  ['tier chips', /\.tier-tab\{min-height:44px\}/],
  ['subject chips', /\.subject-chip\{min-height:44px;min-width:44px/],
  ['reminder bell', /\.cl-rem-btn,\.cl-rem-btn\.cl-rem-compact\{min-height:44px;min-width:44px/],
  ['hourly 詳細氣象', /details\.tm-details > summary\{min-height:44px/]
];
test('CL-I18N-12C (4a): every interactive control on the phone surfaces is ≥44×44 CSS px', () => {
  for (const [name, re] of touchRules) assert.match(phoneCss, re, `${name} keeps a 44px hit box at ≤640px`);
});

test('CL-I18N-12C (4b): the phone hit boxes live in the ≤640px block — desktop keeps its own metrics', () => {
  const desktop = cssSource.slice(0, phoneStart);
  assert.match(desktop, /\.fav-btn \{\s*position:static;\s*width:30px;/, 'base ★ stays 30px');
  assert.match(desktop, /\.fav-btn \{\s*width: 28px;\s*height: 28px;/, 'the ≥901px ★ stays 28px');
  assert.ok(!/\.tier-tab\{min-height:44px\}/.test(desktop), 'tier chips are not stretched on desktop');
  assert.match(desktop, /\.tier-tab-bar \{[\s\S]*?overflow-x: auto/, 'desktop keeps the single scrolling strip');
  assert.match(phoneCss, /\.tier-tab-bar\{flex-wrap:wrap;overflow-x:visible/, 'phones wrap instead of hiding chips off-screen');
});

// --- (5) empty quota chip -------------------------------------------------
test('CL-I18N-12C (5): an empty quota chip takes no layout space', () => {
  assert.match(cssSource, /\.cl-cp-quota-chip\[hidden\]\{display:none\}/,
    'a hidden chip must not be laid out at 20×26 next to 新增私人景點');
  // the rule has to beat the owner stylesheet's display:inline-flex (0,1,0)
  assert.ok(/\.cl-cp-quota-chip\[hidden\]/.test(cssSource), 'selector specificity 0,2,0 wins without !important');
  assert.ok(!/\.cl-cp-quota-chip\[hidden\]\{[^}]*!important/.test(cssSource), 'no !important needed');
});

// --- (6) mobile nav (V8) --------------------------------------------------
test('CL-I18N-12C (6): the shared nav bar shrinks its labels and may scroll instead of clipping', () => {
  const navPhone = mediaBlock(navCss, '@media (max-width: 640px)');
  assert.match(navPhone, /\.site-nav-links \{[\s\S]*?overflow-x: auto/, 'the strip can scroll');
  assert.match(navPhone, /\.site-nav-item,\s*\n\s*\.site-nav-more-btn \{[\s\S]*?flex: 0 0 auto/, 'items keep their content width');
  assert.match(navPhone, /font-size: 13px/, 'px sizing: the root font-size differs per page');
  assert.match(navPhone, /min-width: 44px/, 'nav items keep a 44px hit box');
  assert.match(navPhone, /white-space: nowrap/, 'one-line labels');
  assert.ok(!/justify-content: flex-end/.test(navPhone), 'flex-end pins overflow out of reach when the strip scrolls');
});
