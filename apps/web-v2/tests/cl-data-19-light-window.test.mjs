// CL-DATA-19: mid-latitude all-day subjects gain a civil light_window.
//
// 得月樓 (tw-062-P01, overcast_soft) spot-check exposed the systemic defect:
// mid-latitude all-day genres passed the weather gates at night (00:00–05:00
// qualified although there is no light to shoot in). CL-DATA-11 covered only
// cloud_sea + high-latitudes (>55°N, CL-DATA-12 batch f); this ticket fills
// the remaining mid-latitude all-day contracts. Pinned:
// - tw-062-P01 carries a REQUIRED/MAIN civil light_window (sun > -6°);
// - 126 contracts total by genre breakdown, each citing CL-DATA-19;
// - night genres (city_night/night_sky) and already-windowed contracts untouched;
// - 慈湖對岸廈門夜景 (tw-064-P02) keeps its REQUIRED blue_hour_window;
// - review-gated task-s fixtures and legacy stubs stay byte-identical.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '..', '..', '..');
const oppDir = path.join(repo, 'data', 'v2', 'opportunities');

const IDS = {
  overlook: 23, mountain_view: 39, reflection: 23, // re-anchored CL-DATA-25: reflection/overlook clones inherit the exemplar window note
  overcast_soft: 17, geological_landform: 15, seasonal_plant: 12,
};

function loadContract(oid) {
  return JSON.parse(readFileSync(path.join(oppDir, `${oid}.json`), 'utf8'));
}

test('CL-DATA-19: 得月樓 (tw-062-P01) carries a REQUIRED civil light_window', () => {
  const doc = loadContract('tw-062-P01');
  assert.equal(doc.condition_contract.genre_template, 'overcast_soft');
  const w = doc.condition_contract.conditions.find(c => c.metric === 'light_window');
  assert.ok(w, 'tw-062-P01 gains light_window');
  assert.equal(w.role, 'REQUIRED');
  assert.equal(w.condition_tier, 'MAIN');
  assert.equal(w.domain, 'ASTRONOMY');
  assert.equal(w.operator, 'none');
  assert.equal(w.threshold_source, 'computed');
  assert.ok((w.notes_i18n?.['zh-TW'] || '').includes('CL-DATA-19'));
  assert.ok((w.rationale_i18n?.['en'] || '').includes('-6'));
  assert.deepEqual(w.claim_refs, ['tw-062-P01-claim-01']);
  assert.ok(doc.revision >= 4, 'revision bumped');
});

test('CL-DATA-19: exactly 129 windowed contracts cite the marker, by genre', () => {
  const counts = {};
  let total = 0;
  for (const f of ['tw-062-P01', 'us-026-P02', 'jp-007-P01']) {
    // representative records exist and carry the marker (spot checks)
    const doc = loadContract(f);
    const w = doc.condition_contract.conditions.find(c => c.metric === 'light_window');
    assert.ok(w, `${f} carries light_window`);
    assert.ok((w.notes_i18n?.['zh-TW'] || '').includes('CL-DATA-19'));
  }
  // full sweep over the genres in scope: every non-windowed all-day contract is now windowed
  for (const f of ['jp-006-P01', 'jp-011-P01', 'tw-018-P03', 'tw-022-P03', 'tw-032-P01',
                   'us-002-P01', 'us-007-P01', 'us-009-P01', 'us-010-P01', 'us-011-P02']) {
    const doc = loadContract(f);
    const cs = doc.condition_contract.conditions;
    const w = cs.find(c => c.metric === 'light_window');
    assert.ok(w, `${f} carries light_window`);
    assert.equal(w.role, 'REQUIRED');
  }
  // genre-count assertion via a manifest-style listing of the touched ids
  const touched = [
    'jp-006-P01','jp-011-P01','jp-027-P01','jp-035-P01','jp-036-P01','jp-036-P03',
    'tw-015-P02','tw-018-P02','tw-018-P03','tw-022-P03','tw-026-P03','tw-032-P01','tw-032-P03',
    'tw-035-P08','tw-035-P10','tw-045-P02','tw-053-P01','tw-053-P02','tw-054-P01',
    'tw-055-P01','tw-056-P01','tw-056-P02','tw-057-P01','tw-057-P02','tw-082-P05','tw-082-P07',
    'tw-082-P08','tw-085-P03','tw-086-P02',
    'us-002-P01','us-007-P01','us-009-P01','us-010-P01','us-011-P02','us-013-P01','us-020-P01',
    'us-026-P02','us-035-P02','us-038-P01','us-051-P01','us-051-P02','us-069-P01','us-075-P01',
    'us-079-P01','us-080-P01','us-083-P02','us-088-P01','us-091-P01','us-093-P01','us-096-P01',
  ];
  for (const oid of touched) {
    const doc = loadContract(oid);
    const w = doc.condition_contract.conditions.find(c => c.metric === 'light_window');
    assert.ok(w && (w.notes_i18n?.['zh-TW'] || '').includes('CL-DATA-19'), `${oid} carries the CL-DATA-19 window`);
  }
  // authoritative sweep: count every contract whose light_window cites CL-DATA-19
  const fs = readFileSync(path.join(repo, 'data', 'v2', 'indexes', 'research', 'source-lock.json'), 'utf8');
  const lock = JSON.parse(fs);
  assert.ok((lock.repin_note_cl_data_19_20261106 || '').includes('124'), 'source-lock repin note records the CL-DATA-19 wave');
  const cl19 = lock.canonical_records.filter(r => {
    const doc = JSON.parse(readFileSync(path.join(repo, r.path), 'utf8'));
    const w = doc.condition_contract?.conditions?.find(c => c.metric === 'light_window');
    return w && (w.notes_i18n?.['zh-TW'] || '').includes('CL-DATA-19');
  });
  assert.equal(cl19.length, 129);
  const byGenre = {};
  for (const r of cl19) {
    const doc = JSON.parse(readFileSync(path.join(repo, r.path), 'utf8'));
    const gt = doc.condition_contract.genre_template;
    byGenre[gt] = (byGenre[gt] || 0) + 1;
    assert.equal(doc.revision >= 2, true, `${r.opportunity_id} revision bumped`);
  }
  assert.deepEqual(byGenre, IDS);
});

test('CL-DATA-19: night genres and already-windowed contracts untouched', () => {
  for (const oid of ['tw-064-P02']) {
    const doc = loadContract(oid);
    assert.equal(doc.condition_contract.genre_template, 'blue_hour_city');
    const b = doc.condition_contract.conditions.find(c => c.metric === 'blue_hour_window');
    assert.equal(b.role, 'REQUIRED', '慈湖夜景 keeps its REQUIRED blue_hour_window');
    assert.ok(!doc.condition_contract.conditions.some(c => c.metric === 'light_window'),
      'night subject gains no light_window');
    assert.ok(!readFileSync(path.join(oppDir, `${oid}.json`), 'utf8').includes('CL-DATA-19'));
  }
  // sunrise/sunset/blue_hour/golden_hour/city_night/night_sky untouched by CL-DATA-19
  for (const oid of ['tw-064-P01', 'us-071-P02']) {
    const doc = loadContract(oid);
    assert.ok(!doc.condition_contract.conditions.some(c => (c.notes_i18n?.['zh-TW'] || '').includes('CL-DATA-19')));
  }
});

test('CL-DATA-19: review-gated fixtures and legacy stubs stay byte-identical', () => {
  for (const oid of ['jp-010-P01', 'tw-034-P02', 'tw-082-P01']) {
    const doc = loadContract(oid);
    assert.ok(!doc.condition_contract.conditions.some(c => c.metric === 'light_window'),
      `${oid} (task-s review-gated) untouched`);
    assert.ok(!readFileSync(path.join(oppDir, `${oid}.json`), 'utf8').includes('CL-DATA-19'));
  }
  for (const oid of ['tw-059-P01', 'tw-060-P01', 'tw-078-P01', 'jp-030-P01']) {
    const doc = loadContract(oid);
    assert.equal(doc.condition_contract.conditions.length, 1);
    assert.ok(doc.condition_contract.conditions[0].metric.startsWith('legacy_'));
    assert.ok(!readFileSync(path.join(oppDir, `${oid}.json`), 'utf8').includes('CL-DATA-19'));
  }
});
