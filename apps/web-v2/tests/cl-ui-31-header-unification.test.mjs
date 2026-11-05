// CL-UI-31 — genre-eval / field-intake page-header unification (CL-UI-30 leftover).
// The V1 shell owns ONE brand (site-nav): genre-eval drops the old .site-header
// (brand h1 + duplicate 主頁 link) in favor of a page header + CL-UI-30-style
// control strip; field-intake drops the duplicate ← ChaseLights back-link.
// app.css legacy .site-header / .header-top / .header-right / .weather-map-link
// rules are removed once no page references them.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const read = (p) => readFileSync(join(root, p), 'utf8');

const pages = ['index.html', 'weather-map.html', 'genre-eval.html', 'field-intake.html'];
const appCss = read('assets/app.css');

test('CL-UI-31 (1): no page still carries the old .site-header shell', () => {
  for (const p of pages) {
    assert.doesNotMatch(read(p), /class="site-header"/, `${p} must not use .site-header`);
    assert.doesNotMatch(read(p), /class="header-top"/);
    assert.doesNotMatch(read(p), /class="header-right"/);
  }
  assert.doesNotMatch(appCss, /\.site-header\b/, 'app.css legacy .site-header rules removed');
  assert.doesNotMatch(appCss, /\.header-top\b/);
  assert.doesNotMatch(appCss, /\.header-right\b/);
});

test('CL-UI-31 (2): genre-eval keeps page controls in a CL-UI-30 control strip', () => {
  const html = read('genre-eval.html');
  // Page title h1 stays (page content, not the brand).
  assert.match(html, /<span id="page-title">/);
  const header = html.match(/<header class="genre-eval-header">[\s\S]*?<\/header>/);
  assert.ok(header, 'genre-eval page header present');
  const strip = header[0].match(/<div class="control-strip">[\s\S]*?<\/div>\s*<\/div>/);
  assert.ok(strip, 'control strip inside the page header');
  for (const id of ['region-select', 'lang-select', 'update-time']) {
    assert.ok(header[0].includes(`id="${id}"`), `#${id} kept`);
  }
  // The duplicate brand link is gone.
  assert.doesNotMatch(header[0], /weather-map-link/);
  assert.doesNotMatch(appCss, /\.weather-map-link\b/);
  // genre-eval.js still wires the controls.
  const js = read('assets/genre-eval.js');
  for (const id of ['region-select', 'lang-select', 'update-time', 'page-title']) {
    assert.ok(js.includes(`'${id}'`), `genre-eval.js wires #${id}`);
  }
});

test('CL-UI-31 (3): field-intake drops the duplicate brand back-link', () => {
  const html = read('field-intake.html');
  assert.doesNotMatch(html, /class="back-link"/);
  assert.doesNotMatch(read('assets/field-intake.css'), /\.back-link\b/);
  // Page header keeps title / lead / language control / privacy badge.
  for (const frag of ['data-i18n="title"', 'data-i18n="lead"', 'id="language-select"', 'data-i18n="local_badge"']) {
    assert.ok(html.includes(frag), `field-intake header keeps ${frag}`);
  }
});