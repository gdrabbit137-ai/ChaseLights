// CL-DATA-11: cloud-sea light window + sunset-named window fixes (contract level).
//
// Owner ruling 2026-11-05: 雲海晚上除非有月光否則看不到 — every cloud_sea
// contract that had no light window now carries a REQUIRED `light_window`
// condition (threshold_source=computed; moon branch reuses the existing
// moon_illumination_fraction semantics with illumination >= 0.5). Parity gate
// exempt for these semantic corrections; revision note lives in notes_i18n.
// Also pinned: the 南雅奇岩「夕照雲霞」misplacement (geological_landform x
// spec:day → golden_hour x spec:golden, window REQUIRED) and the three
// sunset-named subjects that lacked any time window.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '..', '..', '..');
const oppDir = path.join(repo, 'data', 'v2', 'opportunities');

const CLOUD_SEA_OPS = [
  'tw-001-P02', 'tw-004-P03', 'tw-008-P03', 'tw-014-P02', 'tw-019-P04',
  'tw-020-P02', 'tw-021-P02', 'tw-022-P02', 'tw-023-P02', 'tw-032-P02',
  'tw-040-P04', 'tw-043-P03', 'tw-082-P09', 'tw-086-P01', 'us-020-P02',
];

function loadContract(oid) {
  return JSON.parse(readFileSync(path.join(oppDir, `${oid}.json`), 'utf8'));
}

test('CL-DATA-11: every cloud_sea contract carries exactly one REQUIRED light_window', () => {
  for (const oid of CLOUD_SEA_OPS) {
    const doc = loadContract(oid);
    const contract = doc.condition_contract;
    assert.equal(contract.genre_template, 'cloud_sea', `${oid} genre`);
    const windows = contract.conditions.filter(c => c.metric === 'light_window');
    assert.equal(windows.length, 1, `${oid} carries exactly one light_window`);
    const w = windows[0];
    assert.equal(w.role, 'REQUIRED', `${oid} light_window REQUIRED`);
    assert.equal(w.condition_tier, 'MAIN', `${oid} light_window MAIN tier`);
    assert.equal(w.threshold_source, 'computed', `${oid} threshold_source`);
    assert.equal(w.domain, 'ASTRONOMY', `${oid} domain`);
    assert.ok((w.notes_i18n?.['zh-TW'] || '').includes('CL-DATA-11'),
      `${oid} revision note cites CL-DATA-11`);
    assert.ok(doc.revision >= 2, `${oid} revision bumped`);
    // every rationale carries the three languages
    for (const lang of ['zh-TW', 'en', 'ja']) {
      assert.ok(w.rationale_i18n?.[lang], `${oid} light_window rationale ${lang}`);
      assert.ok(w.notes_i18n?.[lang], `${oid} light_window note ${lang}`);
    }
  }
});

test('CL-DATA-11: cloud_sea template declares the light window for future instantiations', () => {
  const t = JSON.parse(readFileSync(
    path.join(repo, 'data', 'v2', 'templates', 'cloud_sea.json'), 'utf8'));
  const w = t.conditions.filter(c => c.metric === 'light_window');
  assert.equal(w.length, 1, 'template carries exactly one light_window');
  assert.equal(w[0].role, 'REQUIRED');
  assert.equal(w[0].threshold_source, 'computed');
});

test('CL-DATA-11: 南雅奇岩夕照雲霞 moved to golden_hour with a REQUIRED window', () => {
  const doc = loadContract('tw-072-P02');
  const contract = doc.condition_contract;
  assert.equal(contract.genre_template, 'golden_hour', 'corrected template');
  assert.equal(contract.template_version, 'golden_hour-v0.1');
  const gw = contract.conditions.filter(c => c.metric === 'golden_hour_window');
  assert.equal(gw.length, 1);
  assert.equal(gw[0].role, 'REQUIRED', 'golden window is now REQUIRED (10:00 can no longer pass)');
  assert.equal(gw[0].condition_tier, 'MAIN');
  assert.ok((gw[0].notes_i18n?.['zh-TW'] || '').includes('CL-DATA-11'));
  assert.ok(doc.revision >= 2);
  // the geological subject semantics stay declared
  assert.ok(contract.conditions.some(c => c.metric === 'landform_present'));
});

test('CL-DATA-11: sunset-named subjects with no window now carry REQUIRED sunset_window', () => {
  for (const oid of ['jp-003-P01', 'us-013-P02', 'us-023-P01']) {
    const doc = loadContract(oid);
    const sw = doc.condition_contract.conditions.filter(c => c.metric === 'sunset_window');
    assert.equal(sw.length, 1, `${oid} carries exactly one sunset_window`);
    assert.equal(sw[0].role, 'REQUIRED', `${oid} sunset_window REQUIRED`);
    assert.equal(sw[0].condition_tier, 'MAIN');
    assert.ok((sw[0].notes_i18n?.['zh-TW'] || '').includes('CL-DATA-11'));
    assert.ok(doc.revision >= 2, `${oid} revision bumped`);
  }
});

test('CL-DATA-11: metric vocabulary registers light_window', () => {
  const v = JSON.parse(readFileSync(
    path.join(repo, 'data', 'v2', 'templates', 'metric-vocabulary.json'), 'utf8'));
  assert.ok(v.metrics.light_window, 'light_window registered');
  assert.ok(JSON.stringify(v.changelog).includes('light_window'));
});
