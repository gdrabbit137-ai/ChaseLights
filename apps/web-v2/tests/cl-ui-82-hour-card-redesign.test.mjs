// CL-UI-82: mobile hour-card redesign (design-review-2, head c9fe19505).
// Contract (audit token table — RD has no design latitude):
//  (1) Plain-language mapping layer, trilingual: visibility ≥24 → 極佳 /
//      12–24 → 良好 / 6–12 → 普通 / <6 → 差; total cloud ≤10% → 晴, low cloud
//      30–70% → 多雲, >70% → 陰; wind >6 → 風強 / 1.5–6 → 微風 / <1.5 → 無風.
//      The raw cap text 「≥ 24 km（資料上限）」 NEVER appears on the card face.
//  (2) Dedupe: the 「一般拍攝」 chip is hidden by default on the mobile card and
//      revealed ONLY on a ✅ hour; ⚠️ 未符 / 🕒 非建議時段 hours never carry it.
//      The decorate pass also drives the 3px status band classes (tm-st-*).
//  (3) Raw values (vis/temp/wind/rh/LCL/low+mid+high cloud/astro) live only
//      inside the 「詳細氣象」 native <details>; its open state is captured
//      before a re-render wipes the DOM and restored after (tmRestoreOpen).
//  (4) Height tokens: --hour-card-h 72px / --hour-card-h-expand 128px;
//      fixed 64px time column; 3px band width token.
// Run: node --test --test-isolation=none apps/web-v2/tests/cl-ui-82-hour-card-redesign.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {dirname, join} from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const WEB = join(HERE, '..', '..', '..');
const appSource = readFileSync(join(WEB, 'assets', 'app.js'), 'utf8');
const cssSource = readFileSync(join(WEB, 'assets', 'app.css'), 'utf8');
const indexSource = readFileSync(join(WEB, 'index.html'), 'utf8');
const grab = (start, end) => {
  const a = appSource.indexOf(start);
  const b = appSource.indexOf(end, a + 1);
  assert.ok(a >= 0 && b > a, `source block ${start}…${end} not found`);
  return appSource.slice(a, b);
};

// Extracted plain-language mapping functions run against the REAL app.js
// source with a stubbed dictionary (per-language, so the trilingual contract
// is exercised for real).
function mappingModule(dict) {
  const block = grab('function clui82VisWord', 'function tempChipHtml');
  const prelude = `const VIS_CAP_KM=24.1;const d=()=>(${JSON.stringify(dict)});`;
  return new Function(`${prelude}\n${block}\nreturn {vis:clui82VisWord,sky:clui82SkyWord,wind:clui82WindWord,plain:clui82PlainWeather};`)();
}

const ZH = {
  clui82_vis_excellent:'能見度極佳', clui82_vis_good:'能見度良好', clui82_vis_fair:'能見度普通', clui82_vis_poor:'能見度差',
  clui82_sky_clear:'晴', clui82_sky_partly:'多雲', clui82_sky_overcast:'陰',
  clui82_wind_calm:'無風', clui82_wind_light:'微風', clui82_wind_strong:'風強',
  th_clow:'低雲',
};

test('CL-UI-82 (1): visibility mapping — 極佳/良好/普通/差 + cap never leaks', () => {
  const m = mappingModule(ZH);
  assert.equal(m.vis(24.1), '能見度極佳');
  assert.equal(m.vis(30), '能見度極佳');
  assert.equal(m.vis(12), '能見度良好');
  assert.equal(m.vis(6), '能見度普通');
  assert.equal(m.vis(5.9), '能見度差');
  assert.equal(m.vis(null), null);
  assert.equal(m.vis('abc'), null);
});

test('CL-UI-82 (2): cloud/sky mapping — 晴/多雲/陰 thresholds from the audit table', () => {
  const m = mappingModule(ZH);
  assert.equal(m.sky({c_low:5, c_mid:0, c_high:5}), '晴');
  assert.equal(m.sky({c_low:0, c_mid:20, c_high:5}), '晴');
  assert.equal(m.sky({c_low:43, c_mid:10, c_high:10}), '多雲');
  assert.equal(m.sky({c_low:71, c_mid:0, c_high:0}), '陰');
  assert.equal(m.sky({c_low:29, c_mid:40, c_high:10}), '晴');
  assert.equal(m.sky({c_low:null, c_mid:0, c_high:0}), null);
});

test('CL-UI-82 (3): wind mapping — 無風/微風/風強', () => {
  const m = mappingModule(ZH);
  assert.equal(m.wind(0), '無風');
  assert.equal(m.wind(1.4), '無風');
  assert.equal(m.wind(1.5), '微風');
  assert.equal(m.wind(6), '微風');
  assert.equal(m.wind(6.1), '風強');
  assert.equal(m.wind(undefined), null);
});

test('CL-UI-82 (4): plain weather line composes one 口語化 line — no raw cap text', () => {
  const m = mappingModule(ZH);
  assert.equal(m.plain({c_low:5, c_mid:0, c_high:0, visibility:24.1, wind:2}),
    '晴・低雲 5%・能見度極佳');
  assert.equal(m.plain({c_low:0, c_mid:10, c_high:10, visibility:24.1, wind:2}),
    '晴・能見度極佳');
  assert.equal(m.plain({c_low:43, c_mid:0, c_high:0, visibility:20, wind:2}),
    '多雲・低雲 43%・能見度良好');
  assert.equal(m.plain({c_low:100, c_mid:0, c_high:0, visibility:5, wind:8}),
    '陰・低雲 100%・能見度差・風強');
  assert.ok(!m.plain({c_low:0, c_mid:0, c_high:0, visibility:24.1, wind:1}).includes('24'));
  assert.equal(m.plain({c_low:null, c_mid:null, c_high:null, visibility:null, wind:null}), '');
});

test('CL-UI-82 (5): trilingual token pack — every clui82_* key in all three dicts', () => {
  const KEYS = ['clui82_sky_clear','clui82_sky_partly','clui82_sky_overcast',
    'clui82_vis_excellent','clui82_vis_good','clui82_vis_fair','clui82_vis_poor',
    'clui82_wind_calm','clui82_wind_light','clui82_wind_strong','clui82_details'];
  for (const k of KEYS) assert.equal(appSource.split(`${k}:'`).length - 1, 3, `${k} in all three dicts`);
  const en = mappingModule({
    clui82_vis_excellent:'Visibility excellent', clui82_vis_good:'Visibility good', clui82_vis_fair:'Visibility fair', clui82_vis_poor:'Visibility poor',
    clui82_sky_clear:'Clear', clui82_sky_partly:'Partly cloudy', clui82_sky_overcast:'Overcast',
    clui82_wind_calm:'Calm', clui82_wind_light:'Light breeze', clui82_wind_strong:'Strong wind', th_clow:'Low',
  });
  assert.equal(en.vis(24.1), 'Visibility excellent');
  assert.equal(en.sky({c_low:43, c_mid:0, c_high:0}), 'Partly cloudy');
});

test('CL-UI-82 (6): dedupe — 一般拍攝 hidden by default, decorate reveals only on ✅', () => {
  const deco = grab('function decorateWeatherTimeline', 'function decorateV2Eval');
  assert.ok(deco.includes("card.querySelectorAll('.tm-subj-general')"), 'decorate targets the general chips');
  assert.ok(/state_ok\)\{card\.classList\.add\('tm-st-ok'\);general\.forEach\(x=>x\.hidden=false\)/.test(deco), '✅ reveals the chip');
  assert.ok(/state_outside\)\{card\.classList\.add\('tm-st-outside'\);general\.forEach\(x=>x\.hidden=true\)/.test(deco), '🕒 hides the chip');
  assert.ok(/state_bad\)\{card\.classList\.add\('tm-st-bad'\);general\.forEach\(x=>x\.hidden=true\)/.test(deco), '⚠️ hides the chip');
  assert.ok(deco.includes("card.classList.remove('tm-st-ok','tm-st-bad','tm-st-outside')"), 'band classes reset before repaint');
  const cardBlock = grab("const card=document.createElement('div');card.className=`timeline-mobile-card", 'mobile.appendChild(card);');
  assert.ok(cardBlock.includes('tm-subj-general" hidden'), 'render emits the chip hidden');
  assert.ok(cardBlock.includes('tm-subj-fail'), 'fail word rides the mainline');
});

test('CL-UI-82 (7): detailed-weather <details> — raw values inside, open state preserved', () => {
  const cardBlock = grab("const card=document.createElement('div');card.className=`timeline-mobile-card", 'mobile.appendChild(card);');
  for (const raw of ['th_vis', 'th_temp', 'th_wind', 'th_rh', 'th_cloud_base', 'th_clow', 'th_cmid', 'th_chigh']) {
    assert.ok(cardBlock.includes(`<b>\${d().${raw}}</b>`), `raw metric inside details: ${raw}`);
  }
  assert.ok(cardBlock.includes('details class="tm-details"'), 'native details element');
  assert.ok(cardBlock.includes('tmDetailsOpen'), 'open attribute restored');
  assert.ok(appSource.includes('const tmRestoreOpen='), 'open-state capture exists');
  const capture = grab('const tmRestoreOpen=', 'let nowAnchorAssigned');
  assert.ok(capture.includes("details.tm-details[open]"), 'capture reads currently-open details');
  assert.ok(capture.indexOf('mobile.innerHTML') === -1 || capture.indexOf('mobile.querySelectorAll') < capture.indexOf('mobile.innerHTML'),
    'capture runs BEFORE the DOM wipe');
});

test('CL-UI-82 (8): height/scan tokens + raw cap kept OUT of the card face', () => {
  assert.match(cssSource, /--hour-card-h: 72px;/);
  assert.match(cssSource, /--hour-card-h-expand: 128px;/);
  assert.match(cssSource, /--hour-card-band-w: 3px;/);
  assert.match(cssSource, /--hour-card-time-w: 64px;/);
  assert.match(cssSource, /--hour-card-status-fs: 14px;/);
  assert.match(cssSource, /--hour-card-sub-fs: 12px;/);
  // the cap string is allowed ONLY inside the details tooltip (tip_vis), and
  // the card-face plain line can never contain it
  const cardBlock = grab("const card=document.createElement('div');card.className=`timeline-mobile-card", 'mobile.appendChild(card);');
  assert.ok(cardBlock.includes('clui82PlainWeather(item)'), 'card face uses the plain-language layer');
  assert.ok(!/class="timeline-mobile-quick/.test(cardBlock), 'old quick raw row retired');
  assert.ok(cardBlock.includes('${visCellHtml(item.visibility)}'), 'details vis uses the short cap cell (tooltip, never the full cap text)');
  assert.ok(!cardBlock.includes('visibilityText(item.visibility)'), 'full cap string never rendered on the card');
  // cache-bust advanced
  assert.equal((indexSource.match(/\?v=clui87/g) || []).length, 2, 'app.js + app.css at clui87');
});
