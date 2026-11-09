// CL-UI-52: guest comment feature (homepage footer entry → modal → Apps
// Script bridge action='comment').
//
// Contract tested here (source-level, mirroring sibling cl-ui-XX tests):
//  (1) index.html carries the footer entry + hidden modal, closed by the
//      `hidden` attribute;
//  (2) guest-comment.css scopes the overlay display rules to :not([hidden])
//      with an explicit [hidden] guard (real-hit-testing rule, CL-UI-47
//      lesson) and keeps the entry small/tertiary;
//  (3) guest-comment.js carries ALL copy in three languages (zh-TW/en/ja),
//      enforces maxlengths, a honeypot field, and a no-cors POST with
//      action:'comment';
//  (4) templates/gas_sheet_bridge.js routes on `action` — comments append to
//      the 「訪客留言」 tab and the legacy clear+setValues sync is separate;
//  (5) cache-bust: new assets carry ?v=clui60 in index.html (monotonic,
//      after clui59).
// Run: node --test apps/web-v2/tests/cl-ui-52-guest-comment.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const htmlSource = readFileSync(join(WEB, 'index.html'), 'utf8');
const jsSource = readFileSync(join(WEB, 'assets', 'guest-comment.js'), 'utf8');
const cssSource = readFileSync(join(WEB, 'assets', 'guest-comment.css'), 'utf8');
const bridgeSource = readFileSync(join(WEB, 'templates', 'gas_sheet_bridge.js'), 'utf8');

const I18N_KEYS = [
  'gc_entry', 'gc_title', 'gc_close', 'gc_nickname', 'gc_message',
  'gc_cancel', 'gc_submit', 'gc_sending', 'gc_ok', 'gc_err_empty',
  'gc_err_network', 'gc_err_disabled'
];
const LANGS = ['zh-TW', 'en', 'ja'];

test('CL-UI-52 (1): index.html has a footer-level entry that is NOT inside the card container', () => {
  const entryAt = htmlSource.indexOf('id="guest-comment-entry"');
  const containerAt = htmlSource.indexOf('id="spots-container"');
  assert.ok(entryAt > 0 && containerAt > 0 && entryAt > containerAt,
    'entry must live after the card grid (footer), not inside it');
  assert.match(htmlSource, /<footer class="guest-comment-footer">/);
  assert.match(htmlSource, /class="guest-comment-entry"/);
});

test('CL-UI-52 (1b): modal markup is hidden by default and carries every required field', () => {
  assert.match(htmlSource, /<div class="guest-comment-overlay" id="guest-comment-overlay" hidden>/);
  assert.match(htmlSource, /id="gc-nickname"[^>]*maxlength="20"/);
  assert.match(htmlSource, /id="gc-message"[^>]*maxlength="500"/);
  assert.match(htmlSource, /id="gc-hp"[^>]*class="gc-honeypot"[^>]*tabindex="-1"/);
  assert.match(htmlSource, /id="guest-comment-submit"/);
});

test('CL-UI-52 (2): overlay display rules are state-scoped with an explicit [hidden] guard', () => {
  assert.match(cssSource, /\.guest-comment-overlay:not\(\[hidden\]\)\s*\{\s*display:\s*flex;/);
  assert.match(cssSource, /\.guest-comment-overlay\[hidden\]\s*\{\s*display:\s*none\s*!important;/);
  // Honeypot must be invisible to humans but present in the DOM.
  assert.match(cssSource, /\.gc-honeypot\s*\{[^}]*position:\s*absolute;[^}]*left:\s*-9999px/);
});

test('CL-UI-52 (2b): entry is tertiary — small font, muted color, never a primary CTA', () => {
  const block = cssSource.slice(cssSource.indexOf('.guest-comment-entry {'),
    cssSource.indexOf('.guest-comment-entry:hover'));
  assert.match(block, /font-size:\s*0\.78rem/);
  assert.match(block, /color:\s*#9aa3ad/);
});

test('CL-UI-52 (3): all copy keys exist in all three dictionaries', () => {
  for (const key of I18N_KEYS) {
    const vals = [...jsSource.matchAll(new RegExp(`${key}:\\s*'([^']*)'`, 'g'))].map(m => m[1]);
    assert.equal(vals.length, LANGS.length, `${key} must exist ${LANGS.length} times`);
    vals.forEach(v => assert.ok(v.length >= 2, `${key} carries a meaningful label`));
  }
  // Dictionaries must be keyed exactly once per language.
  for (const lang of LANGS) {
    assert.match(jsSource, new RegExp(`'${lang}':\\s*\\{`), `${lang} dictionary present`);
  }
});

test('CL-UI-52 (3b): submit flow enforces caps, honeypot drop, and a no-cors comment POST', () => {
  assert.match(jsSource, /slice\(0,\s*20\)/, 'nickname hard cap 20');
  assert.match(jsSource, /slice\(0,\s*500\)/, 'message hard cap 500');
  assert.match(jsSource, /if\s*\(hp\.value\)\s*\{\s*closeModal\(\);\s*return;/,
    'honeypot-filled submissions are silently dropped');
  assert.match(jsSource, /mode:\s*'no-cors'/, 'no-cors fetch avoids CORS errors');
  assert.match(jsSource, /action:\s*'comment'/, 'payload carries action=comment');
  assert.match(jsSource, /var GC_ENDPOINT = 'https:\/\/chaselights\.app\/api\/comment';/,
    'endpoint is the owner-deployed same-origin comment API, never a secret');
});

test('CL-UI-52 (4): bridge template routes on action and appends, never clears, the comment tab', () => {
  assert.match(bridgeSource, /if\s*\(payload\.action === 'comment'\)/);
  assert.match(bridgeSource, /sheet\.appendRow\(\[new Date\(\), nickname, message, lang, ua\]\)/);
  assert.match(bridgeSource, /const COMMENT_TAB = '訪客留言';/);
  assert.match(bridgeSource, /const DATA_TABS = \[/);
  assert.match(bridgeSource, /function legacySync_/);
  // Legacy sync clears only its own tab sheets inside the loop, guarded by
  // the secret; the comment path has no clear anywhere.
  const commentFn = bridgeSource.slice(bridgeSource.indexOf('function handleComment_'),
    bridgeSource.indexOf('function legacySync_'));
  assert.doesNotMatch(commentFn, /clearContents/, 'comment path must never clear');
  assert.match(bridgeSource, /p\.secret !== SECRET/, 'legacy sync stays secret-gated');
  assert.match(bridgeSource, /if\s*\(p\.website\)/, 'bridge-side honeypot drop');
});

test('CL-UI-52 (5): cache-bust stamps on the new assets are gc01 in index.html', () => {
  assert.match(htmlSource, /assets\/guest-comment\.css\?v=gc01/);
  assert.match(htmlSource, /assets\/guest-comment\.js\?v=gc01/);
  // monotonic: no stamp may regress below the previous generation
  const stamps = [...htmlSource.matchAll(/\?v=(clui\d+)/g)].map(m => Number(m[1].slice(4)));
  assert.ok(Math.min(...stamps) >= 41, 'all stamps clui41+');
});
