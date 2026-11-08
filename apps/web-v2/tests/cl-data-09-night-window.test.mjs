// CL-DATA-09: TIME_SPECIALIZATION misplacement — contract-level night windows.
//
// Owner ruling 2026-11-05: the four misplated records must carry their night
// window at the CONTRACT level (TIME_SPECIALIZATION_PROPOSAL.md §3–§4), so a
// daytime hour can never qualify even before the evaluator's weather gates:
// - tw-027-P02 (月世界夜間投光地景): REQUIRED city_night_window (civil darkness
//   <= -6 deg), same-source definition as CL-UI-25;
// - tw-035-P05 / tw-036-P02 / tw-038-P02 (galaxy subjects): REQUIRED
//   astronomical_darkness + the full moon cluster (night_sky convention).
// CL-DATA-12 re-anchor (2026-11-06, batch e): the owner's civil-twilight
// ruling for 月世界 takes priority — the astronomical_darkness + moon triple
// is removed and city_night_window becomes the sole night window. The pin
// below is re-measured to that state (revision 3); it is NOT a deletion of
// the gate — the semantics live on in the window condition.
// The source-lock canonical record for tw-027-P02 is re-pinned with a revision
// note (parity gate exempt for this semantic correction).
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '..', '..', '..');

const PINNED = {
  'tw-027-P02': {
    windowMetric: 'city_night_window',
    moonCluster: false,
    revision: 4, // CL-INT-112: revision bumped by CL-DATA-36 batch2 access-verification (e-d36 evidence refs)
  },
  'tw-035-P05': { windowMetric: 'astronomical_darkness', moonCluster: true },
  'tw-036-P02': { windowMetric: 'astronomical_darkness', moonCluster: true },
  'tw-038-P02': { windowMetric: 'astronomical_darkness', moonCluster: true },
};
const MOON_CLUSTER = new Set([
  'moon_illumination_fraction', 'moon_altitude',
  'moon_target_separation_deg', 'moon_illuminance_proxy',
]);

function loadContract(oid) {
  const doc = JSON.parse(readFileSync(
    path.join(repo, 'data/v2/opportunities', `${oid}.json`), 'utf8'));
  return doc;
}

test('CL-DATA-09: pinned contracts declare the contract-level night window', () => {
  for (const [oid, pin] of Object.entries(PINNED)) {
    const doc = loadContract(oid);
    const contract = doc.condition_contract;
    assert.equal(contract.genre_template, 'night_sky', `${oid} genre`);
    const window = contract.conditions.filter(c => c.metric === pin.windowMetric);
    assert.ok(window.length === 1, `${oid} carries exactly one ${pin.windowMetric}`);
    const w = window[0];
    assert.equal(w.role, 'REQUIRED');
    assert.equal(w.condition_tier, 'MAIN');
    assert.equal(w.threshold_source, 'computed');
    assert.equal(w.threshold, null, `${oid} ${pin.windowMetric} is window membership (operator none, no numeric threshold)`);
    assert.ok(w.rationale_i18n['zh-TW'] && w.rationale_i18n.en && w.rationale_i18n.ja,
      `${oid} window carries a trilingual rationale`);
    if (pin.revision !== undefined) {
      assert.equal(doc.revision, pin.revision, `${oid} revision bumped for the ruling`);
    }
  }
});

test('CL-DATA-09: galaxy records carry the moon cluster (night_sky convention)', () => {
  for (const [oid, pin] of Object.entries(PINNED)) {
    if (!pin.moonCluster) continue;
    const doc = loadContract(oid);
    const metrics = new Set(doc.condition_contract.conditions.map(c => c.metric));
    for (const metric of ['astronomical_darkness', ...MOON_CLUSTER]) {
      assert.ok(metrics.has(metric), `${oid} carries ${metric}`);
    }
  }
});

test('CL-DATA-09: tw-027-P02 provenance records the owner ruling in source-lock', () => {
  const lock = JSON.parse(readFileSync(
    path.join(repo, 'data/v2/indexes/research/source-lock.json'), 'utf8'));
  const rec = lock.canonical_records.find(r => r.opportunity_id === 'tw-027-P02');
  assert.ok(rec, 'tw-027-P02 is a pinned canonical record');
  assert.equal(rec.commit_sha, '21198c9cc91e00cdd3df8daea76aac46bf9fb45b'); // CL-INT-112: record re-pinned by CL-DATA-36 batch2 (ruling bytes carried forward)
  assert.ok(/CL-DATA-09/.test(lock.repin_note_cl_data_09_20261105),
    'repin revision note records the ruling');
});
