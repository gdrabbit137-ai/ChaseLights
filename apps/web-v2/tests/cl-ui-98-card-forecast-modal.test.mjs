// CL-UI-98 (DESIGN-6b, owner-approved mockup-cards efdd1febc):
//   1) the card body stays untouched; the bottom-left button copy flips
//      「天氣預報」→「題材」 and opens the subject panel;
//   2) clicking the card opens the FORECAST modal (速覽 quick view + 24h
//      mini band + hourly table) — same source/structure as the forecast
//      surface (shared v2BandHtml / v2QuickViewHtml / plain-weather parts);
//   3) the old detail modal's subject content (8-day strip / conditions /
//      viewpoints / guide) moves into the 「題材」 panel (560px, 390 fullscreen).
// Zero duplicated components: the forecast modal mounts the SAME
// mountQuickView pipeline; the band stays v2BandHtml-only.

import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import assert from 'node:assert/strict';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const appSource = readFileSync(join(WEB, 'assets', 'app.js'), 'utf8');
const cssSource = readFileSync(join(WEB, 'assets', 'app.css'), 'utf8');
const indexSource = readFileSync(join(WEB, 'index.html'), 'utf8');

test('CL-UI-98 (1): card body untouched — click opens the FORECAST modal', () => {
  // The card surface click + keyboard activation route to the official card
  // popup bridge (CL-APP-09 patch-6: cpOpenCard wraps openWeatherModal).
  assert.match(appSource, /card\.onclick=e=>\{if\(e\.target\.closest&&e\.target\.closest\('a,button,input,select,summary'\)\)return;cpOpenCard\(spot,metric\);\};/);
  assert.match(appSource, /if\(e\.key==='Enter'\|\|e\.key===' '\)\{e\.preventDefault\(\);cpOpenCard\(spot,metric\);\}/);
  // The forecast modal is the card-click surface: band + hourly table keep
  // their existing hosts; the 速覽 section rides the same shell.
  assert.match(indexSource, /id="modal-quick-view-body"/);
  assert.match(appSource, /mountQuickView\(document\.getElementById\('modal-quick-view-body'\),spot\)/);
});

test('CL-UI-98 (2): bottom-left button 「題材」 opens the subject panel', () => {
  // Trilingual new key (never internal/provisional wording).
  assert.match(appSource, /v2_subject_link:'🎞 題材'/);
  assert.match(appSource, /v2_subject_link:'🎞 Subjects'/);
  assert.match(appSource, /v2_subject_link:'🎞 題材'/);
  // The card footer button renders the new copy and opens the subject panel (CL-APP-09 patch-6 bridge).
  assert.match(appSource, /toolButtonAttrs\(d\(\)\.v2_subject_link\)/);
  assert.match(appSource, /toolButtonInner\(d\(\)\.v2_subject_link\)/);
  assert.match(appSource, /card\.querySelector\('\[data-weather\]'\)\.onclick=e=>\{e\.preventDefault\(\);e\.stopPropagation\(\);cpOpenPlace\(spot,metric\);\};/);
  // The weather modal title still reads the (retained) forecast label.
  assert.match(appSource, /weather_link:'🌦️ 天氣預報'/);
});

test('CL-UI-98 (3): subject panel = 560px / 390 fullscreen; quick view moved out', () => {
  assert.match(cssSource, /\.place-guide-modal \{ max-width: 560px;/);
  assert.doesNotMatch(cssSource, /\.place-guide-modal \{ max-width: 1180px;/);
  // The panel body no longer hosts the quick view; it keeps the subject
  // knowledge sections (selected-date opportunities + guide + hourly link).
  assert.ok(!appSource.includes('place-quick-view-body'));
  assert.match(appSource, /id="place-hourly-btn"/);
  assert.match(appSource, /class="place-guide-section-title"/);
});

test('CL-UI-98 (4): component single-source — one v2BandHtml, one quick-view pipeline', () => {
  // v2BandHtml stays the ONLY band builder.
  assert.match(appSource, /function v2BandHtml\(rows,spot,bestSet\)/);
  assert.equal((appSource.match(/function v2BandHtml\(/g) || []).length, 1);
  // The quick view is mounted by ONE pipeline (mountQuickView) — the old
  // decorateV2Eval inline copy is retired.
  assert.equal((appSource.match(/function mountQuickView\(/g) || []).length, 1);
  assert.ok(!appSource.includes('quickHost'));
  // Cache-bust bumped in the same ticket.
  assert.match(indexSource, /assets\/app\.js\?v=clui119/);
  assert.match(indexSource, /assets\/app\.css\?v=clui119/);
});
