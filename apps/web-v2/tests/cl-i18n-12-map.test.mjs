// CL-I18N-12B: weather-map.html localization + 393px mobile control layout.
//
// The map carries two string tables inside assets/weather-map.js:
//   WM_STATIC  — keyed dictionary for markup (data-i18n / -aria / -title / -ph)
//   WM_I18N    — zh-TW literal → en/ja lookup used by wmT() at render time
// This test proves both tables are trilingual, that no Chinese leaks into the
// en/ja side, and that the ≤768px control layout keeps every control inside the
// viewport behind an existing toggle (no horizontal scrolling, map not covered).
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const root = new URL('../../../', import.meta.url);
const js = readFileSync(new URL('assets/weather-map.js', root), 'utf8');
const css = readFileSync(new URL('assets/weather-map.css', root), 'utf8');
const html = readFileSync(new URL('weather-map.html', root), 'utf8');

const CJK = /[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]/g;
// Han forms Japanese never writes (it uses 撮 / 図 / 拠 / 気 / 顕 instead).
// Catches zh literals pasted into the ja table, e.g. the 攝 in 「攝影」 instead
// of 撮影. Deliberately excludes 説/数/湿/温 — those ARE Japanese shinjitai.
const ZH_ONLY = /[攝摄訊讯顯显圖图據据氣气]/g;
// Values that are language-neutral (model names, units, numerals) and are
// legitimately identical in zh-TW and ja.
const SAME_BY_NATURE = /^[A-Za-z0-9 .°%×/·:–—-]+$/;

function blockAfter(source, marker) {
  const markerAt = source.indexOf(marker);
  assert.ok(markerAt >= 0, `missing marker: ${marker}`);
  let depth = 0, quote = null, started = false;
  for (let i = source.indexOf('{', markerAt); i < source.length; i += 1) {
    const ch = source[i];
    if (quote) {
      if (ch === '\\') { i += 1; continue; }
      if (ch === quote) quote = null;
      continue;
    }
    if (ch === "'" || ch === '"' || ch === '`') { quote = ch; continue; }
    if (ch === '{') { depth += 1; started = true; continue; }
    if (ch === '}') {
      depth -= 1;
      if (started && depth === 0) return source.slice(source.indexOf('{', markerAt), i + 1);
    }
  }
  throw new Error(`unbalanced block after ${marker}`);
}

const STATIC = vm.runInNewContext(`(${blockAfter(js, 'const WM_STATIC=')})`);
const I18N = vm.runInNewContext(`(${blockAfter(js, 'const WM_I18N=')})`);

const cjkOf = (text) => String(text).match(CJK) || [];

test('WM_STATIC carries the same keys in zh-TW / en / ja', () => {
  const zh = Object.keys(STATIC['zh-TW']).sort();
  for (const lang of ['en', 'ja']) {
    assert.ok(STATIC[lang], `missing WM_STATIC.${lang}`);
    assert.deepEqual(Object.keys(STATIC[lang]).sort(), zh, `WM_STATIC.${lang} key set drifted`);
  }
  assert.ok(zh.length >= 80, `expected a real dictionary, got ${zh.length} keys`);
});

test('WM_I18N carries the same keys in en / ja', () => {
  assert.deepEqual(Object.keys(I18N.en).sort(), Object.keys(I18N.ja).sort());
  assert.ok(Object.keys(I18N.en).length > 150, 'expected the zh→en/ja literal table');
});

test('no Chinese characters in any en string', () => {
  const offenders = [];
  for (const [key, value] of Object.entries(STATIC.en)) {
    if (cjkOf(value).length) offenders.push(`WM_STATIC.en.${key}: ${value}`);
  }
  for (const [key, value] of Object.entries(I18N.en)) {
    if (cjkOf(value).length) offenders.push(`WM_I18N.en[${key}]: ${value}`);
  }
  assert.deepEqual(offenders, []);
});

test('no Chinese-only orthography in ja (攝影→撮影, 圖→図, 數→数 …)', () => {
  const offenders = [];
  const scan = (where, key, value) => {
    const hits = String(value).match(ZH_ONLY);
    if (hits) offenders.push(`${where}.${key}: ${hits.join('')} in "${value}"`);
    if (/攝/.test(String(value))) offenders.push(`${where}.${key}: 攝 must be 撮撮`);
  };
  for (const [key, value] of Object.entries(STATIC.ja)) scan('WM_STATIC.ja', key, value);
  for (const [key, value] of Object.entries(I18N.ja)) scan('WM_I18N.ja', key, value);
  assert.deepEqual(offenders, []);
});

test('the strings this ticket fixed are really translated in ja (no pasted zh)', () => {
  // Many kanji words are identical in Japanese (自動, 詳細, 北 0° …), so "ja must
  // differ from zh" would be wrong in general. These are the keys that were
  // Chinese-only or half-Chinese in the audit; each must now be genuine Japanese.
  const pinned = {
    wm_layer_caption: '撮影レイヤー',
    wm_nav_aria: 'サイト内ナビゲーション',
    wm_ctl_aria: '撮影レイヤーのクイック切替',
    wm_side_aria: 'スポット一覧',
    wm_region_aria: '地域の切替',
    wm_opacity_aria: 'レイヤー表示強度',
    wm_time_aria: 'データ時刻の操作',
    wm_grab_title: '下にドラッグして閉じる',
  };
  for (const [key, expected] of Object.entries(pinned)) {
    assert.equal(STATIC.ja[key], expected, `WM_STATIC.ja.${key}`);
    assert.notEqual(STATIC.ja[key], STATIC['zh-TW'][key], `WM_STATIC.ja.${key} is still the zh-TW string`);
  }
  assert.equal(I18N.ja['☁️ 低雲'], '☁️ 下層雲');
  assert.equal(I18N.ja['資料正常'], 'データ正常');
  assert.equal(I18N.ja['未建立方位資料，僅顯示機位（不以全向環冒充主體扇）。'].length > 10, true, 'ja modal warning must be translated');
});

test('every wmT() literal has an en and a ja translation', () => {
  const literals = new Set();
  for (const m of js.matchAll(/wmT\(\s*'((?:[^'\\]|\\.)*)'/g)) literals.add(m[1].replace(/\\'/g, "'"));
  assert.ok(literals.size > 100, `expected the call sites, found ${literals.size}`);
  const missing = [];
  for (const key of literals) {
    if (!Object.prototype.hasOwnProperty.call(I18N.en, key)) missing.push(`en: ${key}`);
    if (!Object.prototype.hasOwnProperty.call(I18N.ja, key)) missing.push(`ja: ${key}`);
  }
  assert.deepEqual(missing, []);
});

test('layer names that reach the DOM through a label table are translated', () => {
  // photographyLayerLabel()/layerConfig feed the dropdown, the chips and the
  // collapsed pill through wmT(<label>), so those literals need entries too.
  const labelsBlock = /function photographyLayerLabel[\s\S]*?const labels=\{([\s\S]*?)\};/.exec(js);
  assert.ok(labelsBlock, 'photographyLayerLabel labels table not found');
  const labels = [...labelsBlock[1].matchAll(/'((?:[^'\\]|\\.)*)'/g)].map((m) => m[1]);
  const layerConfig = [...js.matchAll(/layerConfig\['[a-z0-9_]+'\]=\{label:'([^']*)'/g)].map((m) => m[1]);
  const missing = [];
  for (const label of new Set([...labels, ...layerConfig])) {
    if (!Object.prototype.hasOwnProperty.call(I18N.en, label)) missing.push(`en: ${label}`);
    if (!Object.prototype.hasOwnProperty.call(I18N.ja, label)) missing.push(`ja: ${label}`);
  }
  assert.deepEqual(missing, []);
  // The audit's headline defects, pinned by name.
  assert.equal(I18N.en['☁️ 低雲'], '☁️ Low cloud');
  assert.equal(I18N.ja['☁️ 低雲'], '☁️ 下層雲');
});

test('the QC status footer and spot-list headings go through wmT', () => {
  assert.match(js, /wmT\('資料正常'\)/, 'footer 「✓ 資料正常」 must be localized');
  assert.ok(!/innerHTML\s*=\s*'[^']*[\u4E00-\u9FFF]/u.test(js), 'an innerHTML literal still contains zh-TW text');
  for (const key of ['wm_side_title', 'wm_sheet_search', 'wm_sheet_sort', 'wm_sheet_n']) {
    assert.ok(STATIC.en[key] && STATIC.ja[key], `${key} must exist in en and ja`);
  }
});

test('aria-labels are resolved for elements that carry only data-i18n-aria', () => {
  // #reset-view / #locate-spot / the sheet close buttons have no data-i18n on
  // the element itself; the applier must query [data-i18n-aria] separately.
  assert.match(js, /querySelectorAll\('\[data-i18n-aria\]'\)/, 'data-i18n-aria needs its own pass');
  assert.match(js, /querySelectorAll\('\[data-i18n-title\]'\)/);
  assert.match(js, /querySelectorAll\('\[data-i18n-ph\]'\)/);
  for (const key of ['wm_reset_aria', 'wm_locate_aria', 'wm_ctl_aria', 'wm_side_aria', 'wm_region_aria', 'wm_opacity_aria', 'wm_time_aria']) {
    assert.ok(STATIC.en[key] && STATIC.ja[key], `${key} must exist in en and ja`);
    assert.ok(html.includes(`data-i18n-aria="${key}"`) || html.includes(`data-i18n="${key}"`), `${key} is not wired into weather-map.html`);
  }
});

// ── V3: 393px layout ──────────────────────────────────────────────────────
function mediaBlock(source, header) {
  const at = source.indexOf(header);
  assert.ok(at >= 0, `missing media query: ${header}`);
  let depth = 0;
  for (let i = source.indexOf('{', at); i < source.length; i += 1) {
    if (source[i] === '{') depth += 1;
    else if (source[i] === '}') {
      depth -= 1;
      if (depth === 0) return source.slice(at, i + 1);
    }
  }
  throw new Error(`unbalanced media query: ${header}`);
}

const mobileCss = mediaBlock(css, '@media (max-width:768px),(max-height:768px)');

test('mobile control bar wraps inside the viewport instead of overflowing', () => {
  // anchor on the tray rule — `.map-panel.sheet-open .control-bar{display:none}`
  // appears earlier in the same block.
  const rule = /\.wm-ops \.control-bar\{order:3;([^}]*)\}/.exec(mobileCss);
  assert.ok(rule, '.wm-ops .control-bar rule missing from the ≤768 block');
  const body = rule[1];
  assert.match(body, /display:grid/, 'control bar must wrap as a grid at 393px');
  assert.match(body, /grid-template-columns:repeat\(2,minmax\(0,1fr\)\)/);
  assert.match(body, /width:100%/);
  assert.doesNotMatch(body, /overflow-x:auto/, 'a horizontally scrolling control strip is unreachable at 393px');
  // every control is pinned to a row, so none can be auto-placed off-screen.
  // Model + region share the last row (both selects are self-describing).
  for (const cls of ['layer-control', 'spot-control', 'opacity-control', 'opportunity-control']) {
    assert.match(mobileCss, new RegExp(`\\.wm-ops \\.control-bar>\\.${cls}\\{grid-column:1/-1;grid-row:\\d\\}`), `${cls} has no fixed row`);
  }
  assert.match(mobileCss, /\.wm-ops \.control-bar>\.model-control\{grid-column:2;grid-row:4\}/, 'model select row unpinned');
  const region = /\.wm-ops \.control-bar>\.region-select\{([^}]*)\}/.exec(mobileCss);
  assert.ok(region, 'region select has no mobile rule');
  assert.match(region[1], /grid-row:4;grid-column:1/, 'region must sit beside the model select on the last row');
  assert.match(region[1], /width:100%/, 'region select fills its column');
});

test('the spot-list toggle exists and is reachable on mobile', () => {
  const rule = /\.map-wrap #side-toggle\{([^}]*)\}/.exec(mobileCss);
  assert.ok(rule, '#side-toggle must be shown in the ≤768 block');
  assert.match(rule[1], /display:inline-flex/);
  assert.doesNotMatch(rule[1], /display:none/);
  assert.match(rule[1], /left:var\(--cl-sp-3\)/, 'toggle must sit inside the left edge');
  assert.match(rule[1], /right:auto/);
  const attr = (id) => {
    const tag = new RegExp(`<button id="${id}"[^>]*>`).exec(html);
    assert.ok(tag, `#${id} missing from weather-map.html`);
    return tag[0];
  };
  for (const [id, target] of [['side-toggle', 'wm-sheet'], ['layer-sheet-btn', 'wm-layer-sheet']]) {
    const tag = attr(id);
    assert.ok(tag.includes(`aria-controls="${target}"`), `#${id} must announce the sheet it opens`);
    assert.ok(tag.includes('aria-expanded="false"'), `#${id} must start collapsed`);
  }
  assert.ok(html.includes('id="wm-sheet-list"'), 'the spot sheet list must exist');
  assert.ok(html.includes('id="wm-ls-chips"'), 'the layer sheet chips must exist');
});

test('the mobile control tray cannot swallow the whole map', () => {
  const ops = /\.wm-ops\{([^}]*)\}/.exec(mobileCss);
  assert.ok(ops, '.wm-ops rule missing');
  assert.match(ops[1], /max-height:47dvh/, 'the ops tray must be capped so the map stays visible');
  assert.match(ops[1], /overflow-y:auto/);
});
