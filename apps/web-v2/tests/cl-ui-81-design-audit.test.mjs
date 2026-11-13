// CL-UI-81 contract (design-review-1 P1-2 / P1-4 / P2-1):
// P1-2 — the 「推薦／最佳」 semantic is GREEN everywhere (green=recommended
//        contract); blue is reserved for links and NON-semantic selection.
//        Selected count pill: bg #123B2A / text #4ADE80 / border #166534.
//        Forecast-table best row: bg rgba(34,197,94,0.10) + 2px #22C55E left
//        border; best badge #123B2A / #4ADE80.
// P1-4 — the homepage date pill never folds mid-word: two-segment trigger
//        (line 1 = 📅 day · count at 14px, line 2 = region at 12px #8B98A9),
//        min-width 176px, nowrap, 48px height (ja is the longest locale).
// P2-1 — pills are distinguishable beyond color: selected border 1.5px +
//        font-weight 600; unselected text #A8B3C2 (≥4.5:1); geometry
//        32px / padding 0 12px / gap 8px / radius 999px.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const appSource = readFileSync(new URL('../../../assets/app.js', import.meta.url), 'utf8');
const cssSource = readFileSync(new URL('../../../assets/app.css', import.meta.url), 'utf8');
const indexSource = readFileSync(new URL('../../../index.html', import.meta.url), 'utf8');

const grab = (start, end) => {
  const i = appSource.indexOf(start);
  assert.ok(i >= 0, `source slice start not found: ${start}`);
  const j = appSource.indexOf(end, i + start.length);
  assert.ok(j > i, `source slice end not found after start: ${end}`);
  return appSource.slice(i, j);
};
const block = (start, end) => {
  const i = cssSource.indexOf(start);
  assert.ok(i >= 0, `css slice start not found: ${start}`);
  const j = cssSource.indexOf(end, i + start.length);
  assert.ok(j > i, `css slice end not found after start: ${end}`);
  return cssSource.slice(i, j);
};

test('CL-UI-81 (1) P1-2: selected tier pill is the green recommended contract (#123B2A/#4ADE80/#166534)', () => {
  const sel = block('.tier-tab.active {', '.tier-tab-count');
  assert.match(sel, /background:\s*#123B2A;/);
  assert.match(sel, /color:\s*#4ADE80;/);
  assert.match(sel, /border:\s*1\.5px solid #166534;/);
  // The blue accent must not survive on the semantic selection.
  assert.doesNotMatch(sel, /#38bdf8/);
});

test('CL-UI-81 (2) P1-2: forecast-table best row + badge go green (row highlight, mobile card, sticky cell, tag-best)', () => {
  assert.match(cssSource, /\.terminal-table tr\.best-row \{ background: rgba\(34, 197, 94, 0\.10\); border-left: 2px solid #22C55E;/);
  const tagBest = block('.tag-best {', 'font-size:.66rem');
  assert.match(tagBest, /border:1px solid #166534;/);
  assert.match(tagBest, /background:#123B2A;/);
  assert.match(tagBest, /color:#4ADE80;/);
  const mobile = block('.timeline-mobile-card.best-row {', '}');
  assert.match(mobile, /rgba\(34, 197, 94, 0\.10\)/);
  assert.match(mobile, /#22C55E/);
  assert.match(cssSource, /\.terminal-table tr\.best-row td:first-child\{background:#12291d\}/);
});

test('CL-UI-81 (3) P2-1: pill geometry 32px / 0 12px / gap 8px / radius 999px; unselected text #A8B3C2', () => {
  const tab = block('.tier-tab {', '.tier-tab:hover');
  assert.match(tab, /height:\s*32px;/);
  assert.match(tab, /padding:\s*0 12px;/);
  assert.match(tab, /border-radius:\s*999px;/);
  assert.match(tab, /color:\s*#A8B3C2;/);
  const strip = block('.subject-chip-strip {', '.subject-chip-strip::-webkit-scrollbar');
  assert.match(strip, /gap:\s*8px;/);
  const chip = block('.subject-chip {', '.subject-chip:hover');
  assert.match(chip, /height:\s*32px;/);
  assert.match(chip, /padding:\s*0 12px;/);
  assert.match(chip, /border-radius:\s*999px;/);
  assert.match(chip, /color:\s*#A8B3C2;/);
  // Selected state is distinguishable beyond color: border 1.5px + weight 600.
  assert.match(block('.tier-tab.active {', '.tier-tab-count'), /font-weight:\s*600;/);
  assert.match(block('.subject-chip.active {', '\n'), /border: 1\.5px solid #38bdf8; font-weight: 600;/);
});

test('CL-UI-81 (4) P1-4: date pill is a two-segment trigger — 176px min-width, 48px, nowrap, 12px gray region line', () => {
  const trigger = block('.day-picker-trigger {', '.day-picker-trigger:hover');
  assert.match(trigger, /min-width:\s*176px;/);
  assert.match(trigger, /min-height:\s*48px;/);
  const main = block('.day-picker-main {', '}');
  assert.match(main, /font-size:\s*\.875rem;/);
  assert.match(main, /white-space:\s*nowrap;/);
  const sub = block('.day-picker-sub {', '}');
  assert.match(sub, /font-size:\s*\.75rem;/);
  assert.match(sub, /color:\s*#8B98A9;/);
  assert.match(sub, /white-space:\s*nowrap;/);
});

test('CL-UI-81 (5) P1-4: syncDayButtons renders both segments and reuses honest i18n (works in all three locales)', () => {
  const sync = grab('function syncDayButtons', 'function openDayPicker');
  assert.match(sync, /day-picker-main/);
  assert.match(sync, /day-picker-sub/);
  assert.match(sync, /day_summary_(viable|none)/, 'line 1 keeps the honest day count');
  assert.match(sync, /admin_area_(selected|all)/, 'line 2 carries the region summary');
  // No new i18n keys needed → trilingual parity is inherited from existing keys.
  assert.doesNotMatch(sync, /CLUI81_PLACEHOLDER/);
});

test('CL-UI-81 (6) cache-bust: index.html serves app.js + app.css at ?v=clui84', () => {
  assert.match(indexSource, /assets\/app\.js\?v=clui84/);
  assert.match(indexSource, /assets\/app\.css\?v=clui84/);
});
