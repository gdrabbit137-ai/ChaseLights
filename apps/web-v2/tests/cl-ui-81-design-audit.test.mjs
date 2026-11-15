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

test('CL-UI-81 (1) P1-2: tier selection is dual-encoded — 600 weight + 1.5px border on bg-3; per-tier semantic color (green recommend / amber shootable / red not-recommended); never the link blue', () => {
  // CL-UI-86 (mockup-cards P2-1): the selected pill follows the mockup's
  // segmented-control scheme — bg-3 elevation + per-tier semantic color;
  // the 推薦 tier keeps the GREEN contract (green=recommended).
  const sel = block('.tier-tab.active {', '.tier-tab[data-tier="recommend"].active');
  assert.match(sel, /background:\s*var\(--cl-bg-3\);/);
  assert.match(sel, /font-weight:\s*600;/);
  assert.match(sel, /border:\s*1\.5px solid var\(--cl-border-strong\);/);
  const rec = block('.tier-tab[data-tier="recommend"].active', '.tier-tab[data-tier="shootable"].active');
  assert.match(rec, /var\(--cl-green-border\)/);
  assert.match(rec, /var\(--cl-green-text\)/);
  const shoot = block('.tier-tab[data-tier="shootable"].active', '.tier-tab[data-tier="not_recommended"].active');
  assert.match(shoot, /var\(--cl-amber-border\)/);
  const no = block('.tier-tab[data-tier="not_recommended"].active', '.tier-tab-count');
  assert.match(no, /var\(--cl-red-border\)/);
  // The blue accent must not survive on the semantic selection.
  assert.doesNotMatch(block('.tier-tab {', '.tier-tab-count'), /var\(--cl-blue\)/);
});

test('CL-UI-81 (2) P1-2: forecast-table best row + badge go green (row highlight, mobile card, sticky cell, tag-best)', () => {
  assert.match(cssSource, /\.terminal-table tr\.best-row \{ background: var\(--cl-green-bg\); border-left: 2px solid var\(--cl-green\);/);
  const tagBest = block('.tag-best {', 'font-size:.66rem');
  assert.match(tagBest, /border:1px solid var\(--cl-green-border\);/);
  assert.match(tagBest, /background:color-mix\(in srgb, var\(--cl-green\) 22%, var\(--cl-bg-0\)\);/);
  assert.match(tagBest, /color:var\(--cl-green-text\);/);
  const mobile = block('.timeline-mobile-card.best-row {', '}');
  assert.match(mobile, /var\(--cl-green-bg\)/);  // == rgba(34,197,94,.10) (CL-UI-85 landing)
  assert.match(mobile, /var\(--cl-green\)/);  // == #22C55E
  assert.match(cssSource, /\.terminal-table tr\.best-row td:first-child\{background:color-mix\(in srgb, var\(--cl-green\) 16%, var\(--cl-bg-0\)\)\}/);
});

test('CL-UI-81 (3) P2-1: pill geometry (tabs 32px / 0 12px / 999px; chips 24px --cl-chip-h / 0 8px / r-xs); unselected text #A8B3C2', () => {
  // CL-UI-86 (mockup-cards): chips use the mockup's 24px --cl-chip-h geometry;
  // tabs keep the 32px pill system height.
  const tab = block('.tier-tab {', '.tier-tab:hover');
  assert.match(tab, /height:\s*32px;/);
  assert.match(tab, /padding:\s*0 12px;/);
  assert.match(tab, /border-radius:\s*999px;/);
  assert.match(tab, /color:\s*var\(--cl-text-2\);/);
  const strip = block('.subject-chip-strip {', '.subject-chip-strip::-webkit-scrollbar');
  assert.match(strip, /gap:\s*8px;/);
  const chip = block('.subject-chip {', '.subject-chip:hover');
  assert.match(chip, /height:\s*var\(--cl-chip-h\);/);
  assert.match(chip, /padding:\s*0 8px;/);
  assert.match(chip, /border-radius:\s*var\(--cl-r-xs\);/);
  assert.match(chip, /color:\s*var\(--cl-text-2\);/);
  // Selected state is distinguishable beyond color: border 1.5px + weight 600.
  assert.match(block('.tier-tab.active {', '.tier-tab[data-tier="recommend"].active'), /font-weight:\s*600;/);
  const chipSel = block('.subject-chip.active {', '\n');
  assert.match(chipSel, /border: 1\.5px solid var\(--cl-border-strong\);/);
  assert.match(chipSel, /font-weight: 600;/);
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
  assert.match(sub, /color:\s*var\(--cl-text-3\);/);
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

test('CL-UI-81 (6) cache-bust: index.html serves app.js + app.css at ?v=clui102', () => {
  assert.match(indexSource, /assets\/app\.js\?v=clui102/);
  assert.match(indexSource, /assets\/app\.css\?v=clui102/);
});
