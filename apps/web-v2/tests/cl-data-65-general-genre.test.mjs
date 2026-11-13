// CL-DATA-65: the general (fallback) genre must be displayable in the live V1
// shell with a three-language label and a visually distinct chip, plus a
// cache-bust bump (skill rule: any app.js/app.css byte change bumps the stamp).
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const root = new URL('../../../', import.meta.url);
const appSource = readFileSync(new URL('assets/app.js', root), 'utf8');
const cssSource = readFileSync(new URL('assets/app.css', root), 'utf8');
const htmlSource = readFileSync(new URL('index.html', root), 'utf8');
const template = JSON.parse(readFileSync(
  new URL('data/v2/templates/general.json', root), 'utf8'));

test('CL-DATA-65 (a): V2_GENRES carries the three-language general label', () => {
  for (const lang of ["'zh-TW'", 'en', 'ja']) {
    const block = appSource.slice(appSource.indexOf(`'zh-TW': { mountain_view`));
    const dictBlock = block.slice(block.indexOf(lang), block.indexOf(lang) + 600);
    assert.match(dictBlock, /general:'/);
  }
  assert.equal(template.title_i18n['zh-TW'], '一般拍攝');
  assert.equal(template.title_i18n.en, 'General shooting');
  assert.equal(template.title_i18n.ja, '一般撮影');
});

test('CL-DATA-65 (b): the general genre chip is visually distinct from curated genres', () => {
  assert.match(appSource, /v2-genre-chip\$\{v2c\.genre_template==='general'\?' v2-genre-chip-general':''\}/);
  assert.match(cssSource, /\.v2-genre-chip-general\{/);
  // the curated chip keeps its blue fill; the general chip must differ
  const general = cssSource.slice(cssSource.indexOf('.v2-genre-chip-general{'));
  assert.doesNotMatch(general, /background:rgba\(88,166,255/);
});

test('CL-DATA-65 (c): cache-bust stamps bumped for app.js/app.css', () => {
  assert.match(htmlSource, /assets\/app\.css\?v=clui71/);
  assert.match(htmlSource, /assets\/app\.js\?v=clui71/);
});
