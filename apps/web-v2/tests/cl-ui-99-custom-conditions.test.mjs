// CL-UI-99 — reminders page 自訂條件 mode: third picker layer gains
// 「自訂條件…」, a five-parameter form (lenient defaults + colloquial hints),
// POST payload switches to customConditions (mutually exclusive with
// opportunityId), and custom-mode reminder cards carry a one-line condition
// summary. Covers: 1) markup + stamps; 2) pure helpers (customSummary) with
// boundary inclusion rules; 3) trilingual dict completeness; 4) DOM-driven
// panel behavior (show/hide, defaults, sanitized payload, card summary).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const read = (p) => readFileSync(join(root, p), 'utf8');

const remHtml = read('reminders.html');
const pageJs = read('assets/reminders-page.js');
const workerJs = read('workers/api/src/index.js');
const notifyJs = read('workers/api/src/notify.js');

test('CL-UI-99 (1): custom-conditions form markup, stamps, worker contract wiring', () => {
  // Panel + all five parameter groups (time window = two time inputs).
  assert.match(remHtml, /id="rem-custom-panel" hidden/);
  for (const id of ['rem-cc-low', 'rem-cc-mid', 'rem-cc-high', 'rem-cc-precip',
    'rem-cc-vis', 'rem-cc-wind', 'rem-cc-start', 'rem-cc-end', 'rem-cc-lead']) {
    assert.match(remHtml, new RegExp(`id="${id}"`), id);
  }
  // Inputs carry min/max boundaries mirroring the worker contract.
  assert.match(remHtml, /id="rem-cc-low" type="number" inputmode="decimal" min="0" max="100"/);
  assert.match(remHtml, /id="rem-cc-precip" type="number" inputmode="decimal" min="0" max="200"/);
  assert.match(remHtml, /id="rem-cc-vis" type="number" inputmode="decimal" min="0" max="50"/);
  assert.match(remHtml, /id="rem-cc-wind" type="number" inputmode="decimal" min="0" max="75"/);
  assert.match(remHtml, /id="rem-cc-lead" type="number" inputmode="numeric" min="0" max="4320"/);
  assert.match(remHtml, /id="rem-cc-start" type="time"/);
  assert.match(remHtml, /id="rem-cc-end" type="time"/);
  // Every hint slot is wired for the colloquial explanation.
  assert.equal((remHtml.match(/class="rem-cc-hint" id="rem-cc-hint-/g) || []).length, 8);
  // Stamp bump is scoped to the reminders page script only.
  assert.match(remHtml, /assets\/reminders-page\.js\?v=clui99/);
  assert.doesNotMatch(remHtml, /reminders-page\.js\?v=clui90/);
  // Page CSS stays token-only (no hex outside :root).
  const style = remHtml.slice(remHtml.indexOf('<style>'), remHtml.indexOf('</style>'));
  assert.doesNotMatch(style, /#[0-9a-fA-F]{3,6}\b/, 'no hex colors outside tokens');

  // Page: third layer offers the custom entry; POST payload is mode-exclusive.
  assert.match(pageJs, /CC_CUSTOM_ID = '__custom__'/);
  assert.match(pageJs, /\{ value: CC_CUSTOM_ID, label: t\('rem_custom_opt'\) \}/);
  assert.match(pageJs, /if \(customConditions\) payload\.customConditions = customConditions;/);
  assert.match(pageJs, /else payload\.opportunityId = oppId \|\| undefined;/);
  assert.match(pageJs, /rem_cc_invalid/);
  // The subject change event toggles the panel LIVE (visual-probe regression:
  // selecting 自訂條件… must not require a place re-selection to open the form).
  assert.match(pageJs, /getElementById\('rem-subject'\)\.addEventListener\('change',[\s\S]{0,160}?renderCustomPanel\(\);/);

  // Worker: validation lives next to the engine; POST accepts the payload,
  // rejects the both-modes body, and the GET/cron select carries the column.
  assert.match(workerJs, /const ccRes = validateCustomConditions\(/);
  assert.match(workerJs, /customConditions and opportunityId are mutually exclusive/);
  assert.match(workerJs, /INSERT INTO notify_rules \(id, user_id, place_id, opportunity_id, channel, min_advance_hours, custom_conditions\)/);
  assert.match(workerJs, /custom_conditions, enabled, created_at FROM notify_rules WHERE user_id/);
  assert.match(notifyJs, /FROM notify_rules r WHERE r\.enabled = 1[\s\S]*?custom_conditions/);
  assert.match(notifyJs, /export function validateCustomConditions/);
});

test('CL-UI-99 (2): customSummary pure builder — boundaries, lenient defaults, languages', () => {
  const start = pageJs.indexOf('// ---- CL-UI-99: custom-conditions mode');
  const end = pageJs.indexOf('// ---- next-trigger / unfit-streak derivation');
  assert.ok(start > 0 && end > start, 'custom-conditions helper block found');
  const src = pageJs.slice(start, end);
  const documentStub = { getElementById: () => null };
  const helpers = new Function('document', `"use strict";
    ${src}
    return { customSummary, collectCustomConditions, CC_DEFAULTS, CC_CUSTOM_ID };`)(documentStub);

  // The owner-visible example: 低雲≤20%・能見度≥10km・05:00–07:00
  assert.equal(
    helpers.customSummary({ cloud_low_max: 20, visibility_min_km: 10, window_start: '05:00', window_end: '07:00', precip_max_mmh: 5, wind_max_ms: 20 }, 'zh-TW'),
    '低雲≤20%・能見度≥10km・05:00–07:00');
  // Lenient defaults are suppressed — an all-default rule shows no constraint line.
  assert.equal(
    helpers.customSummary({ ...helpers.CC_DEFAULTS }, 'zh-TW'),
    '');
  // Boundary inclusion: cloud 100 = unconstrained (dropped), vis 0 = dropped,
  // precip 200 = dropped, wind 75 = dropped → nothing constrains, empty summary.
  assert.equal(
    helpers.customSummary({ cloud_low_max: 100, cloud_mid_max: 100, cloud_high_max: 100, precip_max_mmh: 200, visibility_min_km: 0, wind_max_ms: 75 }, 'ja'),
    '');
  // All five groups active, en wording.
  assert.equal(
    helpers.customSummary({ cloud_low_max: 30, cloud_mid_max: 40, cloud_high_max: 50, precip_max_mmh: 2, visibility_min_km: 8, wind_max_ms: 10, window_start: '22:00', window_end: '03:00' }, 'en'),
    'low cloud≤30%・mid cloud≤40%・high cloud≤50%・rain≤2mm/h・vis≥8km・wind≤10m/s・22:00–03:00');
  // Fractional values render trimmed (2.5 → 2.5, not 2.5000000001); tuned
  // precip/wind away from defaults DO appear.
  assert.equal(
    helpers.customSummary({ precip_max_mmh: 2.5, wind_max_ms: 12 }, 'zh-TW'),
    '雨≤2.5mm/h・風≤12m/s');
  // Empty/invalid payload falls back to an empty summary (chip label carries the mode).
  assert.equal(helpers.customSummary(null, 'zh-TW'), '');
  assert.equal(helpers.customSummary({}, 'zh-TW'), '');
});

test('CL-UI-99 (3): trilingual copy in all three dicts, no internal wording', () => {
  const keys = ['rem_custom_opt', 'rem_cc_chip', 'rem_custom_next', 'rem_custom_preview',
    'rem_cc_panel_title', 'rem_cc_low', 'rem_cc_mid', 'rem_cc_high', 'rem_cc_precip',
    'rem_cc_vis', 'rem_cc_wind', 'rem_cc_window', 'rem_cc_lead', 'rem_cc_hint_low',
    'rem_cc_hint_mid', 'rem_cc_hint_high', 'rem_cc_hint_precip', 'rem_cc_hint_vis',
    'rem_cc_hint_wind', 'rem_cc_hint_window', 'rem_cc_hint_lead', 'rem_col_advance_min',
    'rem_cc_invalid'];
  for (const key of keys) {
    const count = (pageJs.match(new RegExp(`\\b${key}:`, 'g')) || []).length;
    assert.equal(count, 3, `${key} exists in all three dictionaries`);
  }
  const copyText = pageJs.slice(pageJs.indexOf('var I18N'), pageJs.indexOf('function lang()'));
  assert.doesNotMatch(copyText, /provisional|draft|internal/i);
});

test('CL-UI-99 (4): panel behavior — custom entry, defaults, sanitized payload, card summary', () => {
  const elements = new Map();
  function el(id) {
    if (!elements.has(id)) elements.set(id, { id, hidden: false, innerHTML: '', textContent: '', value: '',
      dataset: {}, addEventListener() {}, setAttribute() {}, getAttribute: () => null, placeholder: '' });
    return elements.get(id);
  }
  const document = {
    readyState: 'complete',
    getElementById: el,
    querySelector: () => null,
    querySelectorAll: () => [],
    documentElement: {},
    addEventListener() {},
    body: { appendChild() {} },
    createElement: () => ({ style: {}, setAttribute() {}, classList: {} })
  };
  const sandbox = { window: {}, document, localStorage: { getItem: () => 'zh-TW', setItem() {} },
    fetch: () => Promise.resolve({ ok: false, status: 401, json: () => Promise.resolve({}) }),
    Promise, setTimeout, clearTimeout, MutationObserver: undefined };
  sandbox.window = sandbox;
  new Function('window', 'document', 'localStorage', 'fetch', 'Promise', 'setTimeout', 'clearTimeout', 'MutationObserver',
    pageJs)(sandbox.window, document, sandbox.localStorage, sandbox.fetch, Promise, setTimeout, clearTimeout, undefined);
  const pg = sandbox.window.ChaseLightsRemindersPage;
  pg.state.catalog = [{ place_id: 'tw-001', name_i18n: { 'zh-TW': '合歡山' },
    opportunities: [{ opportunity_id: 'tw-001-P01', name_i18n: { 'zh-TW': '雲海' } }] }];
  pg.state.lang = 'zh-TW';
  pg.state.signedIn = true;
  el('rem-place').value = 'tw-001';

  // Third layer carries the 自訂條件… entry alongside subject options.
  pg.renderSubjectOptions();
  assert.match(el('rem-subject').innerHTML, /__custom__/);
  assert.match(el('rem-subject').innerHTML, /自訂條件…/);

  // Selecting it shows the panel; defaults are lenient and prefilled.
  el('rem-subject').value = pg.CC_CUSTOM_ID;
  pg.renderSubjectOptions();
  assert.equal(el('rem-custom-panel').hidden, false);
  assert.equal(el('rem-cc-low').value, 100);
  assert.equal(el('rem-cc-precip').value, 5);
  assert.equal(el('rem-cc-start').value, '00:00');
  assert.equal(el('rem-cc-lead').value, 60);
  assert.match(el('rem-cc-title').textContent, /全部符合才推播/);

  // A subject-mode selection hides the panel again.
  el('rem-subject').value = 'tw-001-P01';
  pg.renderSubjectOptions();
  assert.equal(el('rem-custom-panel').hidden, true);

  // Sanitized payload: defaults pass the worker contract verbatim.
  el('rem-subject').value = pg.CC_CUSTOM_ID;
  pg.renderSubjectOptions();
  const cc = pg.collectCustomConditions();
  assert.equal(cc.cloud_low_max, 100);
  assert.equal(cc.wind_max_ms, 20);
  assert.deepEqual([cc.window_start, cc.window_end], ['00:00', '23:59']);
  // Out-of-range value -> null payload (submit blocked with rem_cc_invalid).
  el('rem-cc-low').value = '101';
  assert.equal(pg.collectCustomConditions(), null);
  el('rem-cc-low').value = '20';
  // Malformed time input -> null.
  el('rem-cc-start').value = '25:99';
  assert.equal(pg.collectCustomConditions(), null);

  // Custom-mode cards render the one-line summary (line3) and minute advance.
  pg.state.rules = [{ id: 'r9', place_id: 'tw-001', opportunity_id: null, channel: 'push',
    min_advance_hours: 24, enabled: 1,
    custom_conditions: { cloud_low_max: 20, visibility_min_km: 10, window_start: '05:00', window_end: '07:00', lead_minutes: 45 } }];
  pg.renderList();
  const html = el('rem-list').innerHTML;
  assert.match(html, /<span class="rem-subject-chip">自訂條件<\/span>/);
  assert.match(html, /class="rem-cc-summary">低雲≤20%・能見度≥10km・05:00–07:00</);
  assert.match(html, /提前 45 分/);
  assert.match(html, /符合自訂條件時推播/);
  // Subject-mode cards keep the CL-UI-90 anatomy (no line3).
  pg.state.rules = [{ id: 'r1', place_id: 'tw-001', opportunity_id: 'tw-001-P01', channel: 'push', min_advance_hours: 24, enabled: 1 }];
  pg.renderList();
  assert.match(el('rem-list').innerHTML, /<span class="rem-subject-chip">雲海<\/span>/);
  assert.doesNotMatch(el('rem-list').innerHTML, /rem-cc-summary/);
  assert.match(el('rem-list').innerHTML, /提前 24 小時/);
});
