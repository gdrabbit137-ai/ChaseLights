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
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '..', '..', '..');

const PINNED = {
  'tw-027-P02': {
    windowMetric: 'city_night_window',
    moonCluster: false,
    revision: 5, // CL-DATA-75: revision bumped again by the owner-spec §1.2 moon any_of wave (4 → 5)
  },
  'tw-035-P05': { windowMetric: 'astronomical_darkness', moonCluster: true },
  'tw-036-P02': { windowMetric: 'astronomical_darkness', moonCluster: true },
  'tw-038-P02': { windowMetric: 'astronomical_darkness', moonCluster: true },
};
// CL-DATA-75 (owner spec §1.2, 2026-11-20): the milky-way moon gate is the
// any_of dual-track — moon_altitude < 0 OR (illumination <= 0.25 AND
// separation >= 45). The old moon_illuminance_proxy gate is REPLACED by the
// spec's raw illumination gate (moon-down hours auto-pass via the evaluator's
// moon-below-horizon override), so the cluster metric set changes accordingly.
const MOON_CLUSTER = new Set([
  'moon_illumination_fraction', 'moon_altitude',
  'moon_target_separation_deg',
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
  // CL-DATA-80: dynamic byte-pin — the pinned commit must still serve the
  // exact pinned bytes (provenance guarantee; a hardcoded commit_sha rots on
  // every mechanical repin wave like this ticket's 734-contract re-pin).
  const served = execFileSync('git', ['show', `${rec.commit_sha}:data/v2/opportunities/tw-027-P02.json`],
    {cwd: repo, maxBuffer: 1 << 24}).toString();
  assert.ok(/CL-DATA-09/.test(served),
    'tw-027-P02 pinned bytes still carry the owner ruling (CL-DATA-09)');
  assert.ok(/CL-DATA-09/.test(lock.repin_note_cl_data_09_20261105),
    'repin revision note records the ruling');
});
