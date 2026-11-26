// CL-UI-126 (owner report): the language switcher on the 「我的」 page sat in the
// page header under the title. It now lives in the top navbar — the SAME control
// (#lang-select), ONE instance on the page, so both surfaces can never disagree.
//
// Run: node --test apps/web-v2/tests/cl-ui-126-my-page-lang-nav.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const HTML = readFileSync(join(WEB, 'reminders.html'), 'utf8');
const PAGE_JS = readFileSync(join(WEB, 'assets', 'reminders-page.js'), 'utf8');

const navHtml = HTML.slice(HTML.indexOf('<nav class="site-nav"'), HTML.indexOf('</nav>'));
const headerHtml = HTML.slice(HTML.indexOf('<header class="rem-header">'), HTML.indexOf('</header>'));

test('CL-UI-126 (1): exactly ONE #lang-select on the page', () => {
  assert.equal((HTML.match(/id="lang-select"/g) || []).length, 1,
    'the control exists once (moved, not duplicated)');
});

test('CL-UI-126 (2): the switcher sits inside the top navbar', () => {
  assert.ok(navHtml.includes('id="lang-select"'), 'the select is a navbar child');
  assert.match(navHtml, /<span class="site-nav-lang">[\s\S]*?<select id="lang-select"/,
    'it rides the navbar links row');
  assert.deepEqual([...navHtml.matchAll(/<option value="([^"]+)"/g)].map((m) => m[1]), ['zh-TW', 'en', 'ja'],
    'the same three languages, same order');
});

test('CL-UI-126 (3): the page header no longer carries a second switcher', () => {
  assert.ok(!/id="lang-select"/.test(headerHtml), 'no duplicate in <header class="rem-header">');
  assert.ok(!/class="rem-lang"/.test(HTML), 'the retired header wrapper is gone');
  assert.ok(!/\.rem-lang\b/.test(HTML), 'its dead CSS is gone too');
});

test('CL-UI-126 (4): navbar styling keeps the control usable (mobile included)', () => {
  assert.match(HTML, /\.site-nav-lang\{display:inline-flex/, '.site-nav-lang is a flex slot');
  assert.match(HTML, /\.site-nav-lang \.lang-dropdown\{height:32px/, 'compact height');
  assert.match(HTML, /@media \(max-width: 768px\) \{[\s\S]*?\.site-nav-lang \.lang-dropdown\{max-width:80px/,
    'narrow screens shrink it instead of overflowing the bar');
});

test('CL-UI-126 (5): the page logic still binds the same control (no JS change needed)', () => {
  // CL-I18N-12A: the resolution moved from "read #lang-select" to the site's own
  // precedence (?lang= → stored → navigator), and the select became an OUTPUT of
  // that decision — reading its markup default was what pinned every visit to
  // zh-TW. The control itself is still the one the page listens to and persists.
  assert.match(PAGE_JS, /function resolveLang\(\) \{[\s\S]{0,400}return storedLang\(\) \|\| navigatorLang\(\) \|\| 'zh-TW'/,
    'lang() resolves query param → stored → navigator (app.js precedence)');
  assert.match(PAGE_JS, /function syncLangSelect\(\) \{[\s\S]{0,200}getElementById\('lang-select'\)/,
    'the select is synced FROM the resolved language');
  assert.match(PAGE_JS, /getElementById\('lang-select'\)\.addEventListener\('change'/,
    'the change handler is still wired');
  assert.match(PAGE_JS, /localStorage\.setItem\('chaselights_lang', state\.lang\)/,
    'the choice is still persisted');
});
