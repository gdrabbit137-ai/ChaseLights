// CL-I18N-12A: the 「我的」(My Library) page was fully Chinese under ?lang=en/ja.
//
// Two separate leaks are pinned here:
//   1. language RESOLUTION — the page read #lang-select first, and the markup
//      ships that control preselected to zh-TW, so ?lang=en and a stored `en`
//      preference were both overridden back to Chinese. The resolver now mirrors
//      assets/app.js: ?lang= → localStorage → navigator → zh-TW, and the select
//      is an OUTPUT (syncLangSelect), never an input.
//   2. hard-coded Chinese left in the markup / code paths — every user-visible
//      string must come from the trilingual dict, so en/ja can never render a
//      Chinese literal.
//
// Run: node --test apps/web-v2/tests/cl-i18n-12-reminders.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const HTML = readFileSync(join(WEB, 'reminders.html'), 'utf8');
const PAGE_JS = readFileSync(join(WEB, 'assets', 'reminders-page.js'), 'utf8');
const CLIENT_JS = readFileSync(join(WEB, 'assets', 'reminders-client.js'), 'utf8');

// Han + CJK punctuation (what must never reach en; ja is checked separately).
const CJK = /[\u3000-\u303f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff00-\uffef]/;
const KANA = /[\u3040-\u309f\u30a0-\u30ff]/;

// ---- tiny source scanner (strings + comments aware) -------------------------
// Walks JS source once and returns the string literals with their offsets, so a
// scan can tell "this CJK lives inside a dictionary entry" from "this CJK is a
// hard-coded literal in code".
function stringLiterals(src) {
  const out = [];
  let i = 0;
  let prev = '';
  while (i < src.length) {
    const ch = src[i];
    if (ch === '/' && src[i + 1] === '/') { i = src.indexOf('\n', i); if (i < 0) break; prev = '\n'; continue; }
    if (ch === '/' && src[i + 1] === '*') { i = src.indexOf('*/', i + 2); if (i < 0) break; i += 2; continue; }
    // A regex literal (esc()'s /[&<>"']/g would otherwise open a bogus string).
    if (ch === '/' && /[(,=:[!&|?{};+\-*%~^<>]/.test(prev || '(')) {
      i++;
      let inClass = false;
      while (i < src.length) {
        const c = src[i];
        if (c === '\\') { i += 2; continue; }
        if (c === '[') inClass = true;
        else if (c === ']') inClass = false;
        else if (c === '/' && !inClass) { i++; break; }
        else if (c === '\n') break;
        i++;
      }
      prev = '/';
      continue;
    }
    if (ch === '\'' || ch === '"' || ch === '`') {
      const quote = ch;
      const start = i;
      i++;
      let value = '';
      while (i < src.length) {
        const c = src[i];
        if (c === '\\') { value += src.slice(i, i + 2); i += 2; continue; }
        if (c === quote) { i++; break; }
        value += c;
        i++;
      }
      out.push({ value, start, end: i });
      prev = quote;
      continue;
    }
    if (!/\s/.test(ch)) prev = ch;
    i++;
  }
  return out;
}
function matchBrace(src, openIdx) {
  let depth = 0;
  let i = openIdx;
  while (i < src.length) {
    const ch = src[i];
    if (ch === '/' && src[i + 1] === '/') { i = src.indexOf('\n', i); if (i < 0) return src.length; continue; }
    if (ch === '/' && src[i + 1] === '*') { i = src.indexOf('*/', i + 2); if (i < 0) return src.length; i += 2; continue; }
    if (ch === '\'' || ch === '"' || ch === '`') {
      const q = ch; i++;
      while (i < src.length && src[i] !== q) i += (src[i] === '\\' ? 2 : 1);
      i++; continue;
    }
    if (ch === '{' || ch === '[') depth++;
    else if (ch === '}' || ch === ']') { depth--; if (depth === 0) return i + 1; }
    i++;
  }
  return src.length;
}
function evalDict(src, name) {
  const at = src.indexOf(`var ${name} = {`);
  assert.ok(at > 0, `${name} dictionary exists`);
  const body = src.slice(at + `var ${name} = `.length, matchBrace(src, src.indexOf('{', at)));
  // eslint-disable-next-line no-new-func
  return new Function(`return (${body});`)();
}
// Ranges that legitimately hold Chinese/Japanese: the zh-TW and ja blocks of
// the I18N dict, plus the zh-TW / ja rows of the small per-language helper maps
// (weekday names, custom-condition words, regions). Everything else is code.
function chineseRanges(src, dictName) {
  const ranges = [];
  const at = src.indexOf(`var ${dictName} = {`);
  const open = src.indexOf('{', at);
  const dictEnd = matchBrace(src, open);
  const zhAt = src.indexOf("'zh-TW': {", open);
  assert.ok(zhAt > 0 && zhAt < dictEnd, `${dictName} has a zh-TW block`);
  ranges.push([zhAt, matchBrace(src, src.indexOf('{', zhAt))]);
  const jaAt = src.indexOf("'ja': {", ranges[0][1]);
  assert.ok(jaAt > 0 && jaAt < dictEnd, `${dictName} has a ja block`);
  ranges.push([jaAt, matchBrace(src, src.indexOf('{', jaAt))]);
  return ranges;
}
// A literal is dictionary copy when it sits inside the dict blocks, or on a
// helper-map line whose own key is zh-TW / ja.
function isDictCopy(src, pos, ranges) {
  if (ranges.some(([a, b]) => pos >= a && pos < b)) return true;
  const lineStart = src.lastIndexOf('\n', pos) + 1;
  const lineEnd = src.indexOf('\n', pos);
  const line = src.slice(lineStart, lineEnd < 0 ? src.length : lineEnd);
  return /'(?:zh-TW|ja)':/.test(line);
}

// ---- 1. trilingual dictionaries --------------------------------------------
test('CL-I18N-12A (1): page + client dictionaries cover every key in zh-TW / en / ja', () => {
  for (const [label, src, name] of [['reminders-page.js', PAGE_JS, 'I18N'], ['reminders-client.js', CLIENT_JS, 'I18N']]) {
    const dict = evalDict(src, name);
    assert.deepEqual(Object.keys(dict).sort(), ['en', 'ja', 'zh-TW'], `${label}: three languages`);
    const zh = Object.keys(dict['zh-TW']).sort();
    assert.ok(zh.length > 10, `${label}: dictionary is populated (${zh.length} keys)`);
    for (const lg of ['en', 'ja']) {
      assert.deepEqual(Object.keys(dict[lg]).sort(), zh, `${label}: ${lg} key set === zh-TW key set`);
      for (const k of zh) {
        assert.equal(typeof dict[lg][k], 'string', `${label}: ${lg}.${k} is a string`);
        assert.ok(dict[lg][k].trim().length > 0, `${label}: ${lg}.${k} is not empty`);
      }
    }
    // English copy must be English — a Chinese string leaking into en is the
    // exact failure this ticket exists to kill.
    for (const k of zh) assert.ok(!CJK.test(dict['en'][k]), `${label}: en.${k} contains no CJK — got ${JSON.stringify(dict['en'][k])}`);
    // Japanese copy must actually be translated (either kana present, or the
    // value carries no Han at all), never a copy of the zh-TW string. The few
    // entries that ARE identical are Sino-Japanese kanji compounds that are
    // correct in both languages (題材, 降水上限, 風速上限).
    const JA_SAME_OK = new Set(['rem_subject_label', 'rem_cc_precip', 'rem_cc_wind']);
    for (const k of zh) {
      if (CJK.test(dict['ja'][k])) {
        assert.ok(KANA.test(dict['ja'][k]) || dict['ja'][k] !== dict['zh-TW'][k] || JA_SAME_OK.has(k),
          `${label}: ja.${k} is translated, not copied — got ${JSON.stringify(dict['ja'][k])}`);
      }
    }
  }
});

test('CL-I18N-12A (2): the keys this ticket added exist in all three languages', () => {
  const dict = evalDict(PAGE_JS, 'I18N');
  const added = ['nav_aria', 'lang_label', 'my_tabs_aria', 'rem_cc_window_start', 'rem_cc_window_end', 'rem_def_every_aria'];
  for (const k of added) {
    for (const lg of ['zh-TW', 'en', 'ja']) {
      assert.ok(dict[lg][k], `${lg}.${k} present`);
    }
  }
  assert.equal(dict['en'].page_title, 'My Library');
  assert.equal(dict['en'].my_rem_tab, 'My reminders');
  assert.equal(dict['en'].my_subj_tab, 'My subjects');
  assert.equal(dict['en'].rem_login_line, 'Sign in with LINE');
});

// ---- 2. no Chinese outside the zh-TW dictionary ----------------------------
test('CL-I18N-12A (3): no CJK string literal survives outside the zh-TW entries', () => {
  for (const [label, src] of [['reminders-page.js', PAGE_JS], ['reminders-client.js', CLIENT_JS]]) {
    const ranges = chineseRanges(src, 'I18N');
    const leaks = stringLiterals(src)
      .filter((lit) => CJK.test(lit.value) && !isDictCopy(src, lit.start, ranges))
      .map((lit) => `${lit.value} @${lit.start}`);
    assert.deepEqual(leaks, [], `${label}: CJK literals outside the zh-TW dict`);
  }
});

// Targeted HTML scan: text nodes + user-visible attributes. A CJK text node is
// allowed only when it is owned by a dictionary key (data-i18n → this page's
// dict; data-sf-i18n / data-ma-i18n → the shell footer / member-auth modules
// this ticket may not touch). <style>, <script>, comments and elements marked
// lang="…" (the language names in the switcher) are out of scope by design.
function htmlCjkLeaks(html) {
  const source = html
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<!--[\s\S]*?-->/g, '');
  const leaks = [];
  const stack = [];
  const tagRe = /<(\/?)([a-zA-Z][\w:-]*)((?:\s+[^<>]*?)?)\/?>/g;
  let cursor = 0;
  let m;
  const checkText = (text) => {
    if (!CJK.test(text)) return;
    // An element carrying lang="…" names a language in its own script (the
    // switcher's 繁體中文 / 日本語 options) — never page copy.
    if (stack.some((el) => el.attrs.includes('lang'))) return;
    const owner = [...stack].reverse().find((el) =>
      el.attrs.some((a) => /^data-(i18n|sf-i18n|ma-i18n)$/.test(a)));
    if (!owner) leaks.push({ kind: 'text', text: text.trim().slice(0, 60) });
  };
  while ((m = tagRe.exec(source))) {
    checkText(source.slice(cursor, m.index));
    cursor = tagRe.lastIndex;
    const [, closing, name, rawAttrs] = m;
    const attrs = [...rawAttrs.matchAll(/([a-zA-Z][\w:-]*)(?:="([^"]*)")?/g)].map((a) => a[1]);
    if (closing) { stack.pop(); continue; }
    if (/^(area|br|col|embed|hr|img|input|link|meta|source|track|wbr)$/i.test(name)) { continue; }
    stack.push({ name, attrs });
    // The shared shell nav is byte-identical across six pages (CL-UI-28 pins the
    // DOM), so its labels belong to a site-wide nav ticket, not this page.
    if (name === 'nav' && /class="[^"]*\bsite-nav\b/.test(rawAttrs)) {
      const closeRe = /<\/nav>/g;
      closeRe.lastIndex = cursor;
      const close = closeRe.exec(source);
      stack.pop();
      cursor = close ? close.index + close[0].length : source.length;
      tagRe.lastIndex = cursor;
      continue;
    }
    // User-visible attributes must be CJK-free (localised ones use data-i18n-aria).
    for (const am of rawAttrs.matchAll(/(aria-label|placeholder|title|alt)="([^"]*)"/g)) {
      if (CJK.test(am[2])) leaks.push({ kind: am[1], text: am[2] });
    }
  }
  checkText(source.slice(cursor));
  return leaks;
}

test('CL-I18N-12A (4): reminders.html carries no hard-coded Chinese outside dict keys', () => {
  assert.deepEqual(htmlCjkLeaks(HTML), [], 'CJK text nodes / attributes without an i18n key');
  // Every data-i18n / data-i18n-aria hook must map to a key the page ships.
  const dict = evalDict(PAGE_JS, 'I18N');
  for (const m of HTML.matchAll(/data-i18n(?:-aria)?="([^"]+)"/g)) {
    assert.ok(dict['en'][m[1]] && dict['ja'][m[1]], `hook ${m[1]} has en + ja copy`);
  }
  // The retired Chinese defaults are gone, not merely hidden.
  for (const gone of ['>我的</span>', '>儲存</button>', 'aria-label="地區"', '>預設提醒規則</h2>']) {
    assert.ok(!HTML.includes(gone), `retired Chinese literal ${gone} is absent`);
  }
});

// ---- 3. resolution precedence ----------------------------------------------
function buildResolver(search, stored, navLangs) {
  const at = PAGE_JS.indexOf('var VALID_LANGS');
  const end = PAGE_JS.indexOf('function lang()');
  assert.ok(at > 0 && end > at, 'resolver block is extractable');
  const block = PAGE_JS.slice(at, end);
  const writes = [];
  const store = {
    getItem: (k) => (k === 'chaselights_lang' ? stored : null),
    setItem: (k, v) => { writes.push([k, v]); if (k === 'chaselights_lang') stored = v; }
  };
  // eslint-disable-next-line no-new-func
  const factory = new Function('window', 'localStorage', 'navigator',
    `${block}; return { resolveLang, queryLang, storedLang, navigatorLang };`);
  const api = factory({ location: { search } }, store, { languages: navLangs, language: navLangs[0] });
  return { api, writes };
}

test('CL-I18N-12A (5): ?lang= wins, then the stored preference, then navigator', () => {
  // Query param beats a conflicting stored preference AND is persisted
  // (assets/app.js does the same, so the choice survives the next navigation).
  let r = buildResolver('?lang=en', 'ja', ['ja-JP']);
  assert.equal(r.api.resolveLang(), 'en', '?lang=en beats stored ja + navigator ja');
  assert.deepEqual(r.writes.at(-1), ['chaselights_lang', 'en'], 'the query choice is persisted');

  r = buildResolver('?lang=ja', 'en', ['en-US']);
  assert.equal(r.api.resolveLang(), 'ja', '?lang=ja beats stored en');

  // No query param: the site's stored preference is honoured (the audit's
  // "language switch forgotten on My Library" case).
  r = buildResolver('', 'en', ['zh-TW']);
  assert.equal(r.api.resolveLang(), 'en', 'stored en is honoured without a query param');

  // No query, no storage: the browser language decides, not the markup default.
  r = buildResolver('', null, ['ja-JP', 'en-US']);
  assert.equal(r.api.resolveLang(), 'ja', 'navigator ja-JP resolves to ja');
  r = buildResolver('', null, ['en-GB']);
  assert.equal(r.api.resolveLang(), 'en', 'navigator en-GB resolves to en');
  r = buildResolver('', null, ['zh-TW']);
  assert.equal(r.api.resolveLang(), 'zh-TW', 'navigator zh-TW resolves to zh-TW');

  // Garbage never wins.
  r = buildResolver('?lang=fr', 'ja', ['en-US']);
  assert.equal(r.api.queryLang(), null, 'unknown ?lang is ignored');
  assert.equal(r.api.resolveLang(), 'ja', 'falls through to the stored preference');
  r = buildResolver('', 'klingon', ['en-US']);
  assert.equal(r.api.resolveLang(), 'en', 'invalid stored value falls through to navigator');
});

test('CL-I18N-12A (6): the select is an output of the resolver, never an input', () => {
  // Root cause pin: lang() must not read #lang-select (the markup default is zh-TW).
  const fn = PAGE_JS.slice(PAGE_JS.indexOf('function lang()'), PAGE_JS.indexOf('function t(key)'));
  assert.ok(!fn.includes('lang-select'), 'lang() does not read the select');
  assert.match(fn, /return resolveLang\(\)/);
  assert.match(PAGE_JS, /function syncLangSelect\(\)[\s\S]{0,200}sel\.value = state\.lang/,
    'renderAll pushes the resolved language INTO the control');
  assert.match(PAGE_JS, /state\.lang = lang\(\);\s*\n\s*syncLangSelect\(\);/, 'boot syncs the control');
  // t() resolves against the page state, and falls back to zh-TW only.
  assert.match(PAGE_JS, /function t\(key\) \{ var p = I18N\[state\.lang\]/);
});

test('CL-I18N-12A (7): every rendered surface reads the dict (no literal copy in render paths)', () => {
  // The audit's four failing surfaces: title, tabs, headings, LINE button.
  assert.match(PAGE_JS, /document\.title = 'ChaseLights — ' \+ t\('page_title'\)/);
  assert.match(PAGE_JS, /getElementById\('page-title'\)\.textContent = t\('page_title'\)/);
  assert.match(PAGE_JS, /querySelectorAll\('\[data-i18n\]'\)/);
  assert.match(PAGE_JS, /querySelectorAll\('\[data-i18n-aria\]'\)/);
  assert.match(PAGE_JS, /t\('rem_login_line'\)/);
  assert.match(PAGE_JS, /setText\('rem-def-title', 'rem_def_title'\)/);
  assert.match(PAGE_JS, /setText\('rem-def-save', 'rem_def_save'\)/);
  assert.match(PAGE_JS, /WD_NAMES\[state\.lang\]/);
  // A language switch re-renders instead of leaving the old copy behind.
  assert.match(PAGE_JS, /getElementById\('lang-select'\)\.addEventListener\('change'[\s\S]{0,1200}renderAll\(\);/, 'a language switch re-renders');
  // The markup's tab labels/title hooks are on this page's dict.
  assert.match(HTML, /data-i18n="my_rem_tab"/);
  assert.match(HTML, /data-i18n="my_subj_tab"/);
  assert.match(HTML, /id="page-title"><\/span>/, 'title text is rendered from the dict');
});

test('CL-I18N-12A (8): cache-bust stamp bumped on the edited script', () => {
  assert.match(HTML, /assets\/reminders-page\.js\?v=clui134/);
  assert.ok(!HTML.includes('reminders-page.js?v=clui129'), 'old stamp is gone');
});
