// CL-UX-01 Part B: 我的頁「預設提醒規則」面板 + 一鍵鈴鐺流（frontend）
//
// Source-contract test (same genre as cl-ui-103-layer-sheet.test.mjs):
//   · reminders.html carries the defaults section anchor + the time input,
//     ABOVE the rules list, with the seven weekday boxes on BOTH axes.
//   · reminders-page.js talks to /api/v1/notify/defaults with GET + PUT,
//     always sends tz derived from Intl.DateTimeFormat, exposes 0..6 on both
//     weekday axes, both min_tier values, the per-rule override panel
//     (PATCH; 恢復預設 = explicit nulls) and the ?focus= deep link.
//   · reminders-client.js POSTs tz (no schedule fields = inherit the default)
//     and renders the two-action bottom bar, while the toggle-to-remove
//     behaviour stays intact.
//   · every new key exists in all three language dicts of each file.
//
// Plus one behavioural check: the summary builders are extracted and executed
// in a vm so the plain-language line matches the owner example
// 「每週四、五 20:00 · 看未來 3 天 · 只看週六日 · 僅✓推薦」.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import vm from 'node:vm';

const require = createRequire(import.meta.url);
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.join(path.dirname(require.resolve('../../../assets/reminders-page.js')), '..');
const HTML = fs.readFileSync(path.join(ROOT, 'reminders.html'), 'utf8');
const PAGE_JS = fs.readFileSync(path.join(ROOT, 'assets/reminders-page.js'), 'utf8');
const CLIENT_JS = fs.readFileSync(path.join(ROOT, 'assets/reminders-client.js'), 'utf8');

// ---------------------------------------------------------------------------
// 1. Markup: 預設提醒規則 section (anchor + time input + both weekday axes)
// ---------------------------------------------------------------------------
test('CL-UX-01: reminders.html carries the 預設提醒規則 section below the rules list', () => {
  // CL-UX-02 reordered the page: the tracked list now comes first, the
  // defaults panel collapses underneath it.
  assert.ok(HTML.includes('id="rem-def-panel"'), 'defaults section anchor');
  assert.match(HTML, /id="rem-def-title"[^>]*>預設提醒規則</, 'section title');
  const defAt = HTML.indexOf('id="rem-def-panel"');
  const listAt = HTML.indexOf('id="rem-list-panel"');
  assert.ok(defAt > 0 && listAt > 0, 'both panels exist');
  assert.ok(listAt < defAt, 'the rules list renders ABOVE the defaults panel');
});

test('CL-UX-01: the defaults panel exposes time / frequency / lead / target / tier controls', () => {
  assert.match(HTML, /id="rem-def-time"[^>]*type="time"/, 'send-time <input type="time">');
  assert.match(HTML, /id="rem-def-time"[^>]*value="20:00"/, 'default 20:00');
  // frequency: two mutually exclusive modes (每隔 N 天 vs 指定每星期幾)
  const modeRadios = HTML.match(/name="rem-def-mode"[^>]*data-v="(every_n|weekdays)"/g) || [];
  assert.equal(modeRadios.length, 2, 'two frequency modes, mutually exclusive by radio name');
  assert.match(HTML, /id="rem-def-every"[^>]*data-f="every_n"/, '1..7 day-step select');
  assert.match(HTML, /id="rem-def-lead"[^>]*data-f="lead"/, 'look-ahead select');
  // target day axis: 不限星期 vs 只篩選
  const targetRadios = HTML.match(/name="rem-def-target"[^>]*data-v="(any|only)"/g) || [];
  assert.equal(targetRadios.length, 2, '不限星期 / 只篩選');
  // tier: both min_tier values
  assert.match(HTML, /data-f="min_tier" data-v="recommend"/, 'min_tier recommend');
  assert.match(HTML, /data-f="min_tier" data-v="shootable"/, 'min_tier shootable');
  assert.ok(HTML.includes('id="rem-def-summary"'), 'one-line plain-language summary');
  assert.ok(HTML.includes('id="rem-def-save"'), '儲存 button');
});

test('CL-UX-01: reminders.html carries the seven weekday boxes (0..6) on BOTH axes', () => {
  const wd = HTML.match(/data-f="wd" value="[0-6]"/g) || [];
  const twd = HTML.match(/data-f="twd" value="[0-6]"/g) || [];
  assert.equal(wd.length, 7, 'send-frequency axis: seven boxes');
  assert.equal(twd.length, 7, 'target-day axis: seven boxes');
  for (let d = 0; d <= 6; d++) {
    assert.ok(HTML.includes(`data-f="wd" value="${d}"`), `send axis value ${d}`);
    assert.ok(HTML.includes(`data-f="twd" value="${d}"`), `target axis value ${d}`);
  }
  // 0 = Sunday per the backend contract — the first box is 日 and the last 六
  assert.ok(HTML.indexOf('data-f="wd" value="0"') < HTML.indexOf('data-f="wd" value="1"'), '0 comes first (Sunday)');
  assert.ok(HTML.includes('<span class="rem-wd-t">日</span>'), 'weekday labels live in the markup');
});

// ---------------------------------------------------------------------------
// 2. Defaults API: GET + PUT on /api/v1/notify/defaults, tz always derived
// ---------------------------------------------------------------------------
test('CL-UX-01: reminders-page.js reads AND writes /api/v1/notify/defaults', () => {
  assert.ok(PAGE_JS.includes("'/api/v1/notify/defaults'"), 'defaults endpoint constant');
  assert.match(PAGE_JS, /function fetchDefaults\(\)[\s\S]*?fetch\(DEFAULTS_ENDPOINT, \{ headers/, 'GET defaults on load');
  assert.match(PAGE_JS, /function saveDefaults\(\)[\s\S]*?fetch\(DEFAULTS_ENDPOINT, \{\s+method: 'PUT'/, 'PUT defaults');
  assert.ok(!/method: 'PUT'[\s\S]*?\/api\/v1\/notify\/rules/.test(PAGE_JS), 'the PUT never leaks onto the rules route');
});

test('CL-UX-01: every defaults/rule write carries tz from Intl.DateTimeFormat', () => {
  assert.ok(PAGE_JS.includes('Intl.DateTimeFormat().resolvedOptions().timeZone'), 'tz read from the browser');
  assert.match(PAGE_JS, /function browserTz\(\)[\s\S]*?return tz \|\| 'UTC'/, 'browserTz helper');
  const read = PAGE_JS.slice(PAGE_JS.indexOf('function readSchedule(root)'), PAGE_JS.indexOf('function setRadio('));
  assert.ok(read.includes('tz: browserTz()'), 'readSchedule puts tz in every payload (PUT + PATCH)');
  const save = PAGE_JS.slice(PAGE_JS.indexOf('function saveDefaults()'), PAGE_JS.indexOf('function patchRuleSchedule('));
  assert.ok(save.includes("payload.channel = 'push'"), 'channel stays push');
  const reset = PAGE_JS.slice(PAGE_JS.indexOf('function resetRuleSchedule('), PAGE_JS.indexOf('function renderList()'));
  assert.ok(reset.includes('tz: browserTz()'), '恢復預設 still carries tz');
});

// ---------------------------------------------------------------------------
// 3. Per-rule override panel: PATCH, concrete save, null reset, focus deep link
// ---------------------------------------------------------------------------
test('CL-UX-01: each rule card grows a 修改此點規則 panel with save + 恢復預設', () => {
  assert.ok(PAGE_JS.includes("scheduleControlsHtml()"), 'card panel reuses the SAME control group');
  assert.ok(PAGE_JS.includes('data-rem-sched-save'), '儲存此點規則 button');
  assert.ok(PAGE_JS.includes('data-rem-sched-reset'), '恢復預設 button');
  assert.ok(PAGE_JS.includes('data-rem-ovr'), 'inline override panel per card');
  assert.match(PAGE_JS, /function patchRuleSchedule\(id, payload\)[\s\S]*?method: 'PATCH'/, 'PATCH /notify/rules/<id>');
  // concrete save sends the read-back schedule
  const save = PAGE_JS.slice(PAGE_JS.indexOf('function saveRuleSchedule('), PAGE_JS.indexOf('function resetRuleSchedule('));
  assert.ok(save.includes('readSchedule(pnl)'), '儲存此點規則 PATCHes concrete values');
  // 恢復預設 PATCHes explicit nulls (= inherit the user default again)
  const reset = PAGE_JS.slice(PAGE_JS.indexOf('function resetRuleSchedule('), PAGE_JS.indexOf('function renderList()'));
  for (const f of ['schedule_mode', 'schedule_every_n', 'schedule_weekdays', 'send_time', 'lead_days', 'target_weekdays', 'min_tier']) {
    assert.match(reset, new RegExp(`${f}: null`), `恢復預設 clears ${f} with null`);
  }
});

test('CL-UX-01: rule cards show the EFFECTIVE schedule with a （預設） suffix', () => {
  assert.match(PAGE_JS, /function effectiveSchedule\(rule, def\)/, 'effective = rule value else default');
  assert.match(PAGE_JS, /inh\[f\] = !has/, 'inherited fields are tracked per field');
  assert.ok(PAGE_JS.includes("tIn('rem_def_inherited', lg)"), 'suffix comes from the i18n dict');
  assert.ok(PAGE_JS.includes('data-rem-sched-summary'), 'summary line lives on the card');
});

test('CL-UX-01: ?focus=<rule id> scrolls to the card and opens its panel', () => {
  assert.ok(PAGE_JS.includes("URLSearchParams(window.location.search).get('focus')"), 'focus query param read');
  const fn = PAGE_JS.slice(PAGE_JS.indexOf('function applyFocusParam()'), PAGE_JS.indexOf('// 儲存此點規則'));
  assert.ok(fn.includes('scrollIntoView'), 'scrolls the card into view');
  assert.ok(fn.includes("pnl.hidden = false"), 'opens the override panel');
  assert.ok(PAGE_JS.includes('applyFocusParam();'), 'called after the list renders');
});

// ---------------------------------------------------------------------------
// 4. Bell flow: POST carries tz, bar carries the two actions, toggle intact
// ---------------------------------------------------------------------------
test('CL-UX-01: reminders-client.js POSTs tz and no schedule fields (inherit default)', () => {
  const create = CLIENT_JS.slice(CLIENT_JS.indexOf('function createRule('), CLIENT_JS.indexOf('function deleteRule('))
    .replace(/^\s*\/\/.*$/gm, '');
  assert.equal((create.match(/tz: browserTz\(\)/g) || []).length, 2, 'both POST shapes (subject + custom) carry tz');
  assert.ok(create.includes("channel: 'push'"), 'channel stays push');
  assert.ok(create.includes('minAdvanceHours: 24'), 'minAdvanceHours stays 24');
  for (const f of ['schedule_mode', 'schedule_weekdays', 'send_time', 'lead_days', 'target_weekdays', 'min_tier']) {
    assert.ok(!create.includes(f), `bell POST carries no ${f} (server inherits the default)`);
  }
  assert.ok(CLIENT_JS.includes('Intl.DateTimeFormat().resolvedOptions().timeZone'), 'tz from the browser');
});

test('CL-UX-01: the post-add bar shows 已套用預設提醒規則 with the two actions', () => {
  assert.match(CLIENT_JS, /function showRuleBar\(ruleId\)/, 'bar builder');
  const bar = CLIENT_JS.slice(CLIENT_JS.indexOf('function showRuleBar('), CLIENT_JS.indexOf('// ---- state ----'));
  assert.ok(bar.includes("t('rem_bar_applied')"), 'bar headline');
  assert.ok(bar.includes("t('rem_edit_rule')"), 'action 1: 修改此點規則');
  assert.ok(bar.includes("t('rem_bar_ok')"), 'action 2: 知道了');
  assert.ok(bar.includes("'./reminders.html' + (ruleId ? '?focus=' + encodeURIComponent(String(ruleId)) : '')"), 'deep link to the new rule');
  assert.ok(bar.includes('rem-bar-ok'), 'dismiss control');
  assert.ok(CLIENT_JS.includes("closest('.rem-bar-ok')"), '知道了 hides the bar');
  // shown only on a successful ADD, and the removal path keeps working
  assert.ok(CLIENT_JS.includes('showRuleBar(created ? created.id : null)'), 'bar appears after a successful add');
  assert.ok(CLIENT_JS.includes('hideRuleBar()'), 'removing the rule hides the bar');
  assert.ok(CLIENT_JS.includes('deleteRule(rule.id)'), 'toggle-to-remove behaviour untouched');
});

// ---------------------------------------------------------------------------
// 5. i18n: every new key exists in zh-TW / en / ja of each file
// ---------------------------------------------------------------------------
function dictOf(src, lang) {
  const start = src.indexOf(`'${lang}': {`);
  assert.ok(start >= 0, `dictionary ${lang} not found`);
  const end = src.indexOf('\n    }', start);
  assert.ok(end > start, `dictionary ${lang} not terminated`);
  return src.slice(start, end);
}

const NEW_PAGE_KEYS = ['rem_def_title', 'rem_def_intro', 'rem_def_freq', 'rem_def_mode_every',
  'rem_def_mode_weekdays', 'rem_def_days', 'rem_def_send_time', 'rem_def_lead', 'rem_def_target',
  'rem_def_target_any', 'rem_def_target_only', 'rem_def_tier', 'rem_def_tier_recommend',
  'rem_def_tier_shootable', 'rem_def_save', 'rem_def_saved', 'rem_def_err', 'rem_def_loading',
  'rem_def_inherited', 'rem_def_every_n', 'rem_def_weekly', 'rem_def_lookahead', 'rem_def_target_days',
  'rem_def_no_days', 'rem_edit_rule', 'rem_def_save_rule', 'rem_def_reset', 'rem_def_rule_saved',
  'rem_def_rule_reset'];
const NEW_CLIENT_KEYS = ['rem_bar_applied', 'rem_edit_rule', 'rem_bar_ok'];

test('CL-UX-01: every new reminders-page key exists in zh-TW, en and ja', () => {
  for (const lang of ['zh-TW', 'en', 'ja']) {
    const dict = dictOf(PAGE_JS, lang);
    for (const key of NEW_PAGE_KEYS) {
      assert.ok(new RegExp(`\\b${key}:`).test(dict), `${lang} is missing ${key}`);
    }
  }
});

test('CL-UX-01: every new reminders-client key exists in zh-TW, en and ja', () => {
  for (const lang of ['zh-TW', 'en', 'ja']) {
    const dict = dictOf(CLIENT_JS, lang);
    for (const key of NEW_CLIENT_KEYS) {
      assert.ok(new RegExp(`\\b${key}:`).test(dict), `${lang} is missing ${key}`);
    }
  }
});

test('CL-UX-01: the spec wording is present verbatim in zh-TW', () => {
  const zh = dictOf(PAGE_JS, 'zh-TW');
  assert.ok(zh.includes('預設提醒規則'), 'section title');
  assert.ok(zh.includes('發送頻率') && zh.includes('發送時間') && zh.includes('預報展望天數'), 'control labels');
  assert.ok(zh.includes('每隔') && zh.includes('發送頻率'), 'frequency label');
  assert.ok(zh.includes('不限星期') && zh.includes('只篩選'), 'target modes');
  assert.ok(zh.includes('僅✓推薦') && zh.includes('包含○可拍'), 'tier labels');
  assert.ok(zh.includes('修改此點規則') && zh.includes('儲存此點規則') && zh.includes('恢復預設'), 'override panel actions');
  for (const s of ['每隔 N 天', '指定每星期幾']) assert.ok(zh.includes(s), `mode label ${s}`);
  const zhClient = dictOf(CLIENT_JS, 'zh-TW');
  assert.ok(zhClient.includes('已套用預設提醒規則') && zhClient.includes('知道了'), 'bar copy');
  assert.ok(zhClient.includes('修改此點規則'), 'bar edit action');
});

// ---------------------------------------------------------------------------
// 6. Behaviour: summary builders executed in a vm (extracted from the source)
// ---------------------------------------------------------------------------
function fnSrc(src, name) {
  const start = src.indexOf(`function ${name}(`);
  assert.ok(start >= 0, `function ${name} not found`);
  const open = src.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) return src.slice(start, i + 1); }
  }
  throw new Error(`unbalanced function ${name}`);
}

function blockSrc(src, startMarker, endMarker) {
  const start = src.indexOf(startMarker);
  assert.ok(start >= 0, `block ${startMarker} not found`);
  const end = src.indexOf(endMarker, start);
  assert.ok(end > start, `block ${startMarker} not terminated`);
  return src.slice(start, end + endMarker.length);
}

function buildScheduleScope() {
  const parts = [
    blockSrc(PAGE_JS, 'var CC_HM_RE = ', ';\n'),
    blockSrc(PAGE_JS, 'var I18N = {', '\n  };'),
    blockSrc(PAGE_JS, 'var SCHEDULE_FIELDS = ', '];'),
    blockSrc(PAGE_JS, 'var WD_NAMES = {', '};'),
    blockSrc(PAGE_JS, 'var WD_DISPLAY_ORDER = ', ';'),
    "function tIn(key, lg) { var p = I18N[lg] || I18N['zh-TW']; return p[key] || I18N['zh-TW'][key] || ''; }",
    "var state = { lang: 'zh-TW', defaults: null };"
  ];
  for (const fn of ['browserTz', 'modeOf', 'csvDays', 'dayNames', 'clampInt', 'blankDefaults',
    'mergeDefaults', 'scheduleParts', 'scheduleSummary', 'effectiveSchedule']) {
    parts.push(fnSrc(PAGE_JS, fn));
  }
  parts.push('globalThis.out = { scheduleSummary: scheduleSummary, effectiveSchedule: effectiveSchedule, mergeDefaults: mergeDefaults, csvDays: csvDays };');
  const ctx = vm.createContext({});
  vm.runInContext(parts.join('\n\n'), ctx);
  return ctx.out;
}

test('CL-UX-01: the summary line matches the owner example wording', () => {
  const S = buildScheduleScope();
  const sch = {
    schedule_mode: 'weekdays', schedule_weekdays: '4,5', send_time: '20:00',
    lead_days: 3, target_weekdays: '6,0', min_tier: 'recommend'
  };
  assert.equal(S.scheduleSummary(sch, 'zh-TW', {}), '每週四、五 20:00 · 看未來 3 天 · 只看週六日 · 僅✓推薦');
  // every-N mode + shootable tier
  assert.equal(
    S.scheduleSummary({ schedule_mode: 'every_n', schedule_every_n: 2, send_time: '07:30', lead_days: 5, target_weekdays: '', min_tier: 'shootable' }, 'zh-TW', {}),
    '每 2 天 07:30 · 看未來 5 天 · 包含○可拍'
  );
  // English / Japanese follow the same shape
  assert.ok(S.scheduleSummary(sch, 'en', {}).startsWith('Every Thu, Fri 20:00'), 'en weekly wording');
  assert.ok(S.scheduleSummary(sch, 'ja', {}).startsWith('毎週木、金 20:00'), 'ja weekly wording');
});

test('CL-UX-01: inherited fields are marked （預設）, overridden ones are not', () => {
  const S = buildScheduleScope();
  const def = S.mergeDefaults({ schedule_mode: 'weekdays', schedule_weekdays: '4,5', send_time: '20:00', lead_days: 3, target_weekdays: '', min_tier: 'recommend' });

  // a rule that overrides nothing carries the suffix once, at the end
  const all = S.effectiveSchedule({ id: 'r1', schedule_mode: null, schedule_every_n: null }, def);
  assert.equal(all.inherited.send_time, true, 'send_time inherited');
  assert.ok(S.scheduleSummary(all.schedule, 'zh-TW', all.inherited).endsWith('（預設）'), 'single trailing 預設');

  // a partial override marks only the inherited fragments
  const part = S.effectiveSchedule({ id: 'r2', schedule_mode: 'every_n', schedule_every_n: 2, send_time: '06:00', target_weekdays: '6,0' }, def);
  assert.equal(part.inherited.send_time, false, 'send_time overridden');
  assert.equal(part.inherited.lead_days, true, 'lead_days inherited');
  const line = S.scheduleSummary(part.schedule, 'zh-TW', part.inherited);
  assert.equal(line, '每 2 天 06:00 · 看未來 3 天（預設） · 只看週六日 · 僅✓推薦（預設）');
  assert.equal(JSON.stringify(S.csvDays('6,0,6,9,x')), '[0,6]', 'CSV input is sanitized to 0..6, sorted, deduped');
});

test('CL-UX-01 (6): the page only WRITES the API-canonical schedule_mode values', () => {
  // The worker rejects anything but 'every_n_days' | 'weekdays' with a 400 —
  // a frontend that writes the short alias 'every_n' silently breaks saving.
  const page = PAGE_JS;
  assert.ok(page.includes("'every_n_days'"), 'canonical every_n_days spelling is used');
  assert.ok(!/schedule_mode:\s*'every_n'/.test(page), "no bare 'every_n' is ever written to the API");
  assert.ok(!/schedule_mode:\s*'weekly'/.test(page), "no 'weekly' alias is ever written to the API");
  // reads stay tolerant, writes stay canonical
  assert.match(page, /s === 'every_n_days' \|\| s === 'every_n'/);
});
