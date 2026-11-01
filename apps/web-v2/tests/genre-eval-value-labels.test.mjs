// CL-UI-06 CI: the genre-evaluation UI must never render a raw true/false
// condition value. Pipeline publishes 'satisfied'/'unsatisfied' enum strings;
// legacy artifacts may still carry JSON booleans — both must map to localized
// labels in every supported language (zh-TW / en / ja).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import vm from 'node:vm';

const here = path.dirname(fileURLToPath(import.meta.url));
const webRoot = path.resolve(here, '..');
const repoRoot = path.resolve(webRoot, '..', '..');

function loadGenreEval() {
  const src = readFileSync(path.join(repoRoot, 'assets', 'genre-eval.js'), 'utf8');
  const ctx = {
    window: {},
    localStorage: { getItem: () => null, setItem: () => {} },
  };
  vm.createContext(ctx);
  vm.runInContext(src, ctx);
  const api = ctx.window.__genreEval;
  assert.ok(api, 'genre-eval.js must expose window.__genreEval test hooks');
  return api;
}

const CONDITIONS = [
  { metric: 'sunset_window', operator: 'none', threshold: null, value: false, verdict: 'FAIL' },
  { metric: 'sunset_window', operator: 'none', threshold: null, value: true, verdict: 'PASS' },
  { metric: 'sunset_window', operator: 'none', threshold: null, value: 'satisfied', verdict: 'PASS' },
  { metric: 'sunset_window', operator: 'none', threshold: null, value: 'unsatisfied', verdict: 'FAIL' },
  { metric: 'cloud_cover_mid', operator: 'between', threshold: [20, 70], value: 66, verdict: 'PASS' },
  { metric: 'landform_present', operator: 'none', threshold: null, value: 'declared', verdict: 'PASS' },
  { metric: 'water_surface_state', operator: 'none', threshold: null, value: null, verdict: 'UNKNOWN' },
  { metric: 'water_surface_state', operator: 'none', threshold: null, value: undefined, verdict: 'UNKNOWN' },
  { metric: 'moon_altitude', operator: 'gte', threshold: 10, value: 25.5, verdict: 'PASS' },
];

test('fmtValue maps booleans and pipeline enums to localized labels', () => {
  const api = loadGenreEval();
  const expected = {
    'zh-TW': { true: '符合', trueStr: '符合', false: '未符', falseStr: '未符',
               declared: '已宣告', nullish: '無資料', numeric: '25.5' },
    en: { true: 'Meets', trueStr: 'Meets', false: 'Not met', falseStr: 'Not met',
          declared: 'Declared', nullish: 'No data', numeric: '25.5' },
    ja: { true: '達成', trueStr: '達成', false: '未達成', falseStr: '未達成',
          declared: '宣言済み', nullish: 'データなし', numeric: '25.5' },
  };
  for (const [lang, exp] of Object.entries(expected)) {
    api.setLang(lang);
    const c0 = CONDITIONS[0]; // legacy raw false
    const c1 = CONDITIONS[1]; // legacy raw true
    const c2 = CONDITIONS[2]; // enum 'satisfied'
    const c3 = CONDITIONS[3]; // enum 'unsatisfied'
    assert.equal(api.fmtValue(c0), exp.false, `${lang}: raw false`);
    assert.equal(api.fmtValue(c1), exp.true, `${lang}: raw true`);
    assert.equal(api.fmtValue(c2), exp.trueStr, `${lang}: enum satisfied`);
    assert.equal(api.fmtValue(c3), exp.falseStr, `${lang}: enum unsatisfied`);
    assert.equal(api.fmtValue(CONDITIONS[5]), exp.declared, `${lang}: declared`);
    assert.equal(api.fmtValue(CONDITIONS[6]), exp.nullish, `${lang}: null`);
    assert.equal(api.fmtValue(CONDITIONS[7]), exp.nullish, `${lang}: undefined`);
    assert.equal(api.fmtValue(CONDITIONS[8]), exp.numeric, `${lang}: numeric passthrough`);
  }
  api.setLang('zh-TW');
});

test('fmtValueThreshold renders the photographer-friendly localized form (Minor #7)', () => {
  const api = loadGenreEval();
  const c = CONDITIONS[4]; // 66 / 20–70
  api.setLang('zh-TW');
  assert.equal(api.fmtValueThreshold(c), '66（門檻 20–70）');
  api.setLang('en');
  assert.equal(api.fmtValueThreshold(c), '66 (threshold: 20–70)');
  api.setLang('ja');
  assert.equal(api.fmtValueThreshold(c), '66（しきい値 20–70）');
  api.setLang('zh-TW');
  // window metric with no threshold keeps the plain label (no " / —" suffix)
  assert.equal(api.fmtValueThreshold(CONDITIONS[0]), '未符');
});

test('CI: no raw true/false can ever surface from fmtValue/fmtValueThreshold', () => {
  const api = loadGenreEval();
  const battery = [true, false, 'satisfied', 'unsatisfied', 'declared', null,
                   undefined, 0, 66, 25.5, 'x', '', [], {}];
  for (const lang of ['zh-TW', 'en', 'ja']) {
    api.setLang(lang);
    for (const v of battery) {
      const c = { metric: 'sunset_window', operator: 'none', threshold: null, value: v, verdict: 'PASS' };
      const out = String(api.fmtValue(c));
      assert.notEqual(out, 'true', `${lang}: raw "true" leaked for ${String(v)}`);
      assert.notEqual(out, 'false', `${lang}: raw "false" leaked for ${String(v)}`);
      assert.equal(typeof api.fmtValue(c), 'string', `${lang}: non-string output`);
      const th = { metric: 'cloud_cover_mid', operator: 'between', threshold: [20, 70], value: v, verdict: 'PASS' };
      const outTh = String(api.fmtValueThreshold(th));
      assert.ok(!/ (true|false)$/.test(outTh), `${lang}: raw boolean in threshold cell for ${String(v)}`);
    }
  }
  api.setLang('zh-TW');
});

function collectConditions(node, out) {
  if (Array.isArray(node)) {
    for (const item of node) collectConditions(item, out);
  } else if (node && typeof node === 'object') {
    if ('metric' in node && 'value' in node && !('conditions' in node)) out.push(node);
    for (const v of Object.values(node)) collectConditions(v, out);
  }
  return out;
}

test('CI: shipped evaluation artifacts render without raw true/false', () => {
  const api = loadGenreEval();
  const artifacts = [path.join(webRoot, 'evaluations-latest.json')];
  const detailsDir = path.join(webRoot, 'evaluations-details');
  if (existsSync(detailsDir)) {
    for (const f of readdirSync(detailsDir)) {
      if (f.endsWith('.json')) artifacts.push(path.join(detailsDir, f));
    }
  }
  assert.ok(artifacts.length > 1, 'expected evaluations-latest.json plus detail artifacts');
  let checked = 0;
  for (const file of artifacts) {
    let data;
    try {
      data = JSON.parse(readFileSync(file, 'utf8'));
    } catch {
      continue; // unreadable artifact is not a UI-contract failure here
    }
    const conditions = collectConditions(data, []);
    for (const c of conditions) {
      for (const lang of ['zh-TW', 'en', 'ja']) {
        api.setLang(lang);
        const out = String(api.fmtValue(c));
        assert.notEqual(out, 'true', `${path.basename(file)}[${c.metric}]: raw "true" visible`);
        assert.notEqual(out, 'false', `${path.basename(file)}[${c.metric}]: raw "false" visible`);
      }
      checked += 1;
    }
  }
  api.setLang('zh-TW');
  assert.ok(checked > 0, 'no conditions found in artifacts — scan did not run');
});

test('CI: no UI file interpolates c.value directly into HTML', () => {
  const genreEvalSrc = readFileSync(path.join(repoRoot, 'assets', 'genre-eval.js'), 'utf8');
  assert.ok(!/\$\{esc\(c\.value/.test(genreEvalSrc),
            'genre-eval.js must render values through fmtValue, not raw c.value');
  const evalHtml = readFileSync(path.join(webRoot, 'evaluations.html'), 'utf8');
  assert.ok(evalHtml.includes('v==="satisfied"'),
            'evaluations.html fmtValue must map the pipeline enum');
  const appMjs = readFileSync(path.join(webRoot, 'app.mjs'), 'utf8');
  assert.ok(appMjs.includes('v==="satisfied"'),
            'app.mjs evalValue must map the pipeline enum');
});
