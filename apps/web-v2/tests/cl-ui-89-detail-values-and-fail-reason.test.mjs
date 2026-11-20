// CL-UI-89: forecast-modal detail defects (owner QA on 旭岳 jp-002 @390px).
// Contract:
//  (1) 詳細氣象 strip values NEVER truncate: the expandable metrics strip is
//      content-sized flex cells that wrap — the old 4-col grid with
//      overflow:hidden + text-overflow:ellipsis clipped 能見度 「≥ …」 /
//      風速 「1.65…」 / 凝結高度 「6…」. Full value stays in the DOM.
//  (2) ⚠️ 未符 mainline carries a SHORT plain-language reason — the plain
//      mapping layer gains mid/high cloud short words (trilingual): a fully
//      blocked layer >70% → 低雲滿/中雲滿/高雲滿 (priority low→mid→high).
//  (3) Contradiction case: 中雲 100% must NOT read bare 「晴」 next to a
//      ⚠️ 未符 verdict — the sky word itself becomes 中雲滿 and the mainline
//      reads 「⚠️ 未符・中雲滿」. Fail-closed: no fully blocked layer → no
//      invented reason (mainline stays bare ⚠️ 未符).
// Run: node --test --test-isolation=none apps/web-v2/tests/cl-ui-89-detail-values-and-fail-reason.test.mjs
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
// source with a stubbed dictionary (per-language, trilingual contract).
function mappingModule(dict) {
  const block = grab('function clui82VisWord', 'function tempChipHtml');
  const prelude = `const VIS_CAP_KM=24.1;const d=()=>(${JSON.stringify(dict)});`;
  return new Function(`${prelude}\n${block}\nreturn {sky:clui82SkyWord,plain:clui82PlainWeather,reason:clui82CloudFullReason,bad:clui82BadReasonLabel};`)();
}

const ZH = {
  clui82_sky_clear:'晴', clui82_sky_partly:'多雲', clui82_sky_overcast:'陰',
  clui82_clow_full:'低雲滿', clui82_cmid_full:'中雲滿', clui82_chigh_full:'高雲滿',
  clui82_vis_excellent:'能見度極佳', clui82_vis_good:'能見度良好', clui82_vis_fair:'能見度普通', clui82_vis_poor:'能見度差',
  clui82_wind_calm:'無風', clui82_wind_light:'微風', clui82_wind_strong:'風強',
  th_clow:'低雲', state_bad:'⚠️ 未符',
};
const EN = {
  clui82_sky_clear:'Clear', clui82_sky_partly:'Partly cloudy', clui82_sky_overcast:'Overcast',
  clui82_clow_full:'Low cloud thick', clui82_cmid_full:'Mid cloud thick', clui82_chigh_full:'High cloud thick',
  clui82_vis_excellent:'Visibility excellent', clui82_vis_good:'Visibility good', clui82_vis_fair:'Visibility fair', clui82_vis_poor:'Visibility poor',
  clui82_wind_calm:'Calm', clui82_wind_light:'Light breeze', clui82_wind_strong:'Strong wind',
  th_clow:'Low', state_bad:'⚠️ Not met',
};
const JA = {
  clui82_sky_clear:'晴れ', clui82_sky_partly:'雲多め', clui82_sky_overcast:'曇り',
  clui82_clow_full:'下層雲多め', clui82_cmid_full:'中層雲多め', clui82_chigh_full:'上層雲多め',
  clui82_vis_excellent:'視程とても良い', clui82_vis_good:'視程良い', clui82_vis_fair:'視程普通', clui82_vis_poor:'視程悪い',
  clui82_wind_calm:'無風', clui82_wind_light:'弱風', clui82_wind_strong:'強風',
  th_clow:'下層雲', state_bad:'⚠️ 未達成',
};

test('CL-UI-89 (1): trilingual token pack — cloud-full short words exist in all three dicts', () => {
  for (const k of ['clui82_clow_full', 'clui82_cmid_full', 'clui82_chigh_full']) {
    assert.equal(appSource.split(`${k}:'`).length - 1, 3, `${k} in all three dicts`);
  }
  // and they never carry internal/provisional wording
  for (const lang of [ZH, EN, JA]) {
    for (const k of ['clui82_clow_full', 'clui82_cmid_full', 'clui82_chigh_full']) {
      assert.ok(!/TODO|TBD|draft|placeholder|WIP/i.test(lang[k]));
    }
  }
});

test('CL-UI-89 (2): sky mapping — mid/high cloud >70% gets its own word, low-cloud 陰 unchanged', () => {
  const m = mappingModule(ZH);
  assert.equal(m.sky({c_low:5, c_mid:100, c_high:0}), '中雲滿');
  assert.equal(m.sky({c_low:0, c_mid:0, c_high:80}), '高雲滿');
  assert.equal(m.sky({c_low:80, c_mid:100, c_high:0}), '陰', 'low cloud still wins (blocks the sun itself)');
  assert.equal(m.sky({c_low:29, c_mid:40, c_high:10}), '晴', 'partly-covered mid layer keeps 晴');
  assert.equal(m.sky({c_low:0, c_mid:70, c_high:0}), '晴', 'threshold is >70 strictly');
  assert.equal(m.sky({c_low:0, c_mid:0, c_high:0}), '晴');
  assert.equal(m.sky({c_low:null, c_mid:0, c_high:0}), null);
  const en = mappingModule(EN);
  assert.equal(en.sky({c_low:5, c_mid:100, c_high:0}), 'Mid cloud thick');
  const ja = mappingModule(JA);
  assert.equal(ja.sky({c_low:5, c_mid:100, c_high:0}), '中層雲多め');
});

test('CL-UI-89 (3): contradiction case — 中雲100% aux line must not read bare 「晴」 (trilingual)', () => {
  // owner QA case: 低雲 5%・中雲 100%・能見度極佳 used to read 「晴・低雲 5%・能見度極佳」
  // next to a ⚠️ 未符 verdict — self-contradictory.
  const zh = mappingModule(ZH).plain({c_low:5, c_mid:100, c_high:0, visibility:24.1, wind:2});
  assert.equal(zh, '中雲滿・低雲 5%・能見度極佳');
  assert.ok(!zh.startsWith(ZH.clui82_sky_clear), 'no bare 「晴」 head');
  const en = mappingModule(EN).plain({c_low:5, c_mid:100, c_high:0, visibility:24.1, wind:2});
  assert.equal(en, 'Mid cloud thick・Low 5%・Visibility excellent');
  assert.ok(!en.startsWith(EN.clui82_sky_clear));
  const ja = mappingModule(JA).plain({c_low:5, c_mid:100, c_high:0, visibility:24.1, wind:2});
  assert.equal(ja, '中層雲多め・下層雲 5%・視程とても良い');
  assert.ok(!ja.startsWith(JA.clui82_sky_clear));
});

test('CL-UI-89 (4): ⚠️ 未符 short reason — clui82CloudFullReason priority low→mid→high, fail-closed', () => {
  const m = mappingModule(ZH);
  assert.equal(m.reason({c_low:84, c_mid:100, c_high:0}), '低雲滿');
  assert.equal(m.reason({c_low:5, c_mid:100, c_high:0}), '中雲滿');
  assert.equal(m.reason({c_low:0, c_mid:0, c_high:75}), '高雲滿');
  assert.equal(m.reason({c_low:5, c_mid:40, c_high:10}), '', 'no fully blocked layer → no invented reason');
  assert.equal(m.reason({c_low:null, c_mid:null, c_high:null}), '', 'missing data → no invented reason');
  assert.equal(m.reason(null), '');
});

test('CL-UI-89 (5): 未符 mainline = ⚠️ 未符・短原因 (clui82BadReasonLabel, trilingual)', () => {
  const zh = mappingModule(ZH);
  assert.equal(zh.bad(ZH.state_bad, {c_low:5, c_mid:100, c_high:0, visibility:24.1, wind:2}), '⚠️ 未符・中雲滿');
  assert.equal(zh.bad(ZH.state_bad, {c_low:5, c_mid:40, c_high:10}), ZH.state_bad, 'no blocked layer → bare ⚠️ 未符');
  assert.equal(zh.bad(ZH.state_bad, null), ZH.state_bad, 'no weather payload → bare ⚠️ 未符');
  assert.equal(mappingModule(EN).bad(EN.state_bad, {c_low:0, c_mid:0, c_high:90}), '⚠️ Not met・High cloud thick');
  assert.equal(mappingModule(JA).bad(JA.state_bad, {c_low:84, c_mid:0, c_high:0}), '⚠️ 未達成・下層雲多め');
});

test('CL-UI-89/94 (6): the ✗ short reason rides the subject cell — no painter write path left', () => {
  const deco = grab('function decorateWeatherTimeline', 'function decorateV2Eval');
  // CL-UI-94: the status painter is retired — evaluations-details can no
  // longer append a second verdict (it was the 大屯山 contradiction source).
  assert.match(deco, /CL-UI-94/, 'retirement anchor');
  assert.ok(!deco.includes('clui82BadReasonLabel'), 'no second reason write path');
  // the fail short-reason comes from the subject-cards dict (same source as
  // the ✓ chips) and rides the mobile mainline + desktop subject cell
  const cellBlock = grab('function v2HourSubjectCell', '// CL-UI-26: every 不符 verdict');
  assert.ok(cellBlock.includes('fail_reason_short'), 'fail words from the artifact dictionary');
  assert.ok(cellBlock.includes("class=\"subj-no\">✗"), '✗ short reason in the subject cell');
  const cardBlock = grab("const card=document.createElement('div');card.className=`timeline-mobile-card", 'mobile.appendChild(card);');
  assert.ok(cardBlock.includes('tm-subj-fail'), 'fail word rides the mobile mainline');
  assert.ok(cardBlock.includes('wxByT[card.dataset.v2t]=item'), 'weather stash kept for the plain-line source');
  assert.ok(appSource.includes('decorateWeatherTimeline(spot,activeOpportunityId,wxByT)'), 'call site anchor retained');
});

test('CL-UI-89 (7): 詳細氣象 strip never truncates — content-sized flex cells, no ellipsis', () => {
  const rule = cssSource.match(/details\.tm-details \.timeline-mobile-metrics \{[^}]*\}/);
  assert.ok(rule, 'details metrics rule exists');
  assert.match(rule[0], /display: flex;/);
  assert.match(rule[0], /flex-wrap: wrap;/, 'cells wrap to the next row instead of clipping');
  assert.doesNotMatch(rule[0], /grid-template-columns/, 'no fixed 4-col grid (the truncation source)');
  const cell = cssSource.match(/details\.tm-details \.timeline-mobile-metric \{[^}]*\}/);
  assert.ok(cell, 'details metric cell rule exists');
  assert.doesNotMatch(cell[0], /overflow:\s*hidden/, 'no hidden overflow');
  assert.doesNotMatch(cell[0], /text-overflow/, 'no ellipsis — the full value stays visible in the DOM');
  // raw values still ride the details block (full value in DOM, CL-UI-82 (7))
  const cardBlock = grab("const card=document.createElement('div');card.className=`timeline-mobile-card", 'mobile.appendChild(card);');
  for (const raw of ['th_vis', 'th_wind', 'th_cloud_base']) {
    assert.ok(cardBlock.includes(`<b>\${d().${raw}}</b>`), `raw metric inside details: ${raw}`);
  }
  assert.ok(cardBlock.includes('${visCellHtml(item.visibility)}'), 'vis value in the details block');
});

test('CL-UI-89 (8): cache-bust stamp advanced to clui102', () => {
  assert.equal((indexSource.match(/\?v=clui102/g) || []).length,3, 'app.css + feedback-ui stay at clui102; app.js advanced to clui118 (CL-UI-110)');
});
