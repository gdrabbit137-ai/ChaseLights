// CL-UI-126 (owner report): leftover engineering text in the create-subject form
// — the 「（未調任何參數）」 subtitle (and its repeat at the footer) — plus the
// cloud dropdown's 「不在乎」 label, which the fog/rain dropdowns already spell
// 「不限」. Cloud only: fog/rain wording is left exactly as it was.
//
// Run: node --test apps/web-v2/tests/cl-ui-126-engineering-text.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const read = (p) => readFileSync(join(WEB, p), 'utf8');
const CARD = read('assets/subject-sets.js');
const LIB = read('assets/subject-sets-library.js');
const CP = read('assets/custom-places.js');

const slice = (src, start, end) => {
  const a = src.indexOf(start);
  assert.ok(a !== -1, `slice start not found: ${start}`);
  const b = src.indexOf(end, a);
  assert.ok(b !== -1, `slice end not found: ${end}`);
  return src.slice(a, b);
};

test('CL-UI-126 (1): no 「未調任何參數」 placeholder survives in either create form', () => {
  for (const [name, src] of [['subject-sets.js', CARD], ['subject-sets-library.js', LIB]]) {
    const code = src.split('\n').filter((l) => !/^\s*\/\//.test(l)).join('\n');
    assert.ok(!/未調任何參數/.test(code), `${name}: the engineering placeholder is gone (comments excepted)`);
    assert.ok(!/cc_prev_none/.test(code), `${name}: nothing falls back to it anymore`);
  }
});

test('CL-UI-126 (2): the form subtitle only renders when there IS a summary', () => {
  const cardForm = slice(CARD, 'function editorModal(mode)', "wireClose();");
  assert.match(cardForm, /var headSub = ccSummary\(cc, lang\);/, 'summary computed once');
  assert.match(cardForm, /\(headSub \? '<div class="sub">' \+ esc\(headSub\) \+ '<\/div>' : ''\)/,
    'the subtitle is conditional — no empty 「（）」 shell');
  const libForm = slice(LIB, 'function openEditor(placeId, set)', "var ov = document.getElementById('sslib-overlay');");
  assert.match(libForm, /var headSub = summaryOf\(cc, lg\);/);
  assert.match(libForm, /\(headSub \? '<div class="sub">' \+ esc\(headSub\) \+ '<\/div>' : ''\)/);
});

test('CL-UI-126 (3): the footer preview stays hidden until a parameter is set', () => {
  const cardForm = slice(CARD, 'function editorModal(mode)', "function refreshWarn()");
  assert.match(cardForm, /class="cl-cp-cc-preview"' \+ \(headSub \? '' : ' hidden'\)/,
    'card form: preview row starts hidden');
  assert.match(cardForm, /row\.hidden = !s;/, 'card form: it appears/disappears with the summary');
  const libForm = slice(LIB, 'function openEditor(placeId, set)', "'cloud', 'fog', 'rain'");
  assert.match(libForm, /class="sslib-preview"' \+ \(headSub \? '' : ' hidden'\)/,
    'library form: preview row starts hidden');
  assert.match(libForm, /row\.hidden = !s;/);
});

test('CL-UI-126 (4): the empty custom-subject list says so, instead of the old placeholder', () => {
  assert.match(CARD, /empty_note: '尚無自訂題材'/, 'zh-TW empty note');
  assert.match(CARD, /empty_note: 'No custom subjects yet'/, 'en empty note');
  assert.match(CARD, /empty_note: '自作題材はまだありません'/, 'ja empty note');
  assert.match(CARD, /class="cl-ss-empty">' \+ esc\(t\(\)\.empty_note\)/, 'the list renders it');
});

test('CL-UI-126 (5): the cloud option reads 不限 in all three assets; fog/rain are untouched', () => {
  const cloud = (src) => slice(src, 'cloud: {', 'fog: {');
  const fog = (src) => slice(src, 'fog: {', 'rain: {');
  const rain = (src) => slice(src, 'rain: {', '};');
  for (const [name, src] of [['subject-sets.js', CARD], ['subject-sets-library.js', LIB], ['custom-places.js', CP]]) {
    assert.match(cloud(src), /不限/, `${name}: cloud says 不限`);
    assert.ok(!/不在乎/.test(cloud(src)), `${name}: cloud no longer says 不在乎`);
  }
  for (const [name, src] of [['subject-sets.js', CARD], ['subject-sets-library.js', LIB]]) {
    assert.match(fog(src), /\['any', '不限', null\]/, `${name}: fog wording unchanged`);
    assert.match(rain(src), /\['any', '不限', null\]/, `${name}: rain wording unchanged`);
  }
  assert.match(fog(CP), /\['any', '不在乎', '不限'\]/, 'custom-places fog wording unchanged');
  assert.match(rain(CP), /\['any', '不在乎', '不限'\]/, 'custom-places rain wording unchanged');
});
