// CL-UI-77: card env-type line is downgraded from chips to plain text.
// Owner problem: env-type chips ([城市][山岳]) looked identical to subject
// chips ([夜景]) so users mistook attributes for clickable subjects. The
// env-type line must now be plain gray text (城市 · 山岳) — no chip frame,
// no background, non-interactive — visibly layered under the subject rows
// (夜景: 時段 🔔), which stay unchanged.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';

const root = fileURLToPath(new URL('../../..', import.meta.url));
const appJs = readFileSync(root + 'assets/app.js', 'utf8');
const appCss = readFileSync(root + 'assets/app.css', 'utf8');
const indexHtml = readFileSync(root + 'index.html', 'utf8');

test('CL-UI-77 (1): card env-type renders plain text, never scene chips', () => {
  // The render path emits one .env-type-text span, no .scene-pill classes.
  assert.match(appJs, /const envTypeText=scenes\.map\(x=>sceneLabel\(x\)\.replace\(/);
  assert.match(appJs, /const scenePills=envTypeText\?`<span class="env-type-text">\$\{esc\(envTypeText\)\}<\/span>`:''/);
  assert.ok(!appJs.includes('class=\\"scene-pill'), 'cards must not emit scene-pill chips anymore');
  assert.ok(!appJs.includes('scene-pill scene-more'), 'the +N chip is retired with the pill row');
});

test('CL-UI-77 (2): env-type text is low-key, frameless, non-interactive', () => {
  assert.match(appCss, /\.env-type-text \{/);
  const block = appCss.match(/\.env-type-text \{[^}]*\}/)[0];
  assert.match(block, /color:#94a3b8/);
  assert.ok(!/border/.test(block), 'no border — not a chip');
  assert.ok(!/background/.test(block), 'no background — not a chip');
  assert.ok(!/cursor/.test(block), 'never presented as interactive');
  assert.match(block, /font-size:\.6[0-9]rem/, 'small gray text, visually below chips');
  // The retired chip rules are gone from the stylesheet.
  assert.ok(!appCss.includes('.scene-pill'), '.scene-pill CSS is fully retired');
  assert.ok(!appCss.includes('.scene-more'), '.scene-more CSS is fully retired');
});

test('CL-UI-77 (3): subject reminder rows keep their interactive anatomy', () => {
  // Subject rows stay: name: window + bell (untouched by this ticket).
  assert.match(appJs, /const clSubjectRowHtml=\(entry,hidden\)=>/);
  assert.match(appJs, /cl-rem-btn cl-rem-compact/);
});

test('CL-UI-77 (4): cache-bust bumped to clui89 on the homepage', () => {
  assert.match(indexHtml, /assets\/app\.js\?v=clui89/);
  assert.match(indexHtml, /assets\/app\.css\?v=clui89/);
});
