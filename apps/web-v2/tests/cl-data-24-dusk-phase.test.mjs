// CL-DATA-24: dusk-named subjects (暮色/夕照) must carry phase:dusk on their
// window condition so the symmetric blue/golden hour elevation windows stop
// matching the dawn side of the day (the 05:00-06:00 false "good hours").
// The evaluator-side gate is covered by packages/core-v2/tests/
// test_cl_data_24_phase.py; this suite pins the 12 owner contracts.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const oppDir = path.join(here, '..', '..', '..', 'data', 'v2', 'opportunities');

// Owner ticket list: every contract whose name names the dusk side of the day.
const DUSK_NAMED = [
  'tw-001-P03', 'tw-002-P01', 'tw-003-P02', 'tw-005-P01', 'tw-005-P02',
  'tw-007-P01', 'tw-017-P03', 'us-071-P01', 'tw-035-P09', 'tw-072-P02',
  'us-007-P02', 'tw-027-P03',
];

function loadContract(oid) {
  return JSON.parse(readFileSync(path.join(oppDir, `${oid}.json`), 'utf8'));
}

test('CL-DATA-24: every dusk-named contract pins phase:dusk on its window condition', () => {
  for (const oid of DUSK_NAMED) {
    const doc = loadContract(oid);
    const name = doc.name_i18n['zh-TW'];
    assert.ok(name.includes('暮色') || name.includes('夕照'),
      `${oid} subject name names the dusk side: ${name}`);
    const windows = doc.condition_contract.conditions.filter(
      c => c.metric === 'blue_hour_window' || c.metric === 'golden_hour_window');
    assert.ok(windows.length === 1, `${oid} has exactly one symmetric window condition`);
    assert.equal(windows[0].phase, 'dusk', `${oid} window condition pins phase:dusk`);
  }
});

test('CL-DATA-24: phase lives ONLY on the dusk-named window conditions', () => {
  // No other condition in any contract may carry a phase key (the constraint
  // exists for this defect class; unrelated conditions stay untouched).
  const ALL = [...DUSK_NAMED, 'tw-024-P02', 'us-071-P02'];
  for (const oid of ALL) {
    const doc = loadContract(oid);
    for (const c of doc.condition_contract.conditions) {
      const isWindow = c.metric === 'blue_hour_window' || c.metric === 'golden_hour_window';
      if (isWindow) {
        if (DUSK_NAMED.includes(oid)) {
          assert.equal(c.phase, 'dusk');
        } else {
          assert.ok(!('phase' in c), `${oid} ${c.id} unpinned window stays unconstrained`);
        }
      } else {
        assert.ok(!('phase' in c), `${oid} ${c.id} non-window condition carries no phase`);
      }
    }
  }
});

test('CL-DATA-24: tw-027-P03 夕照 window promoted REQUIRED/MAIN (subject = the light itself)', () => {
  const c = loadContract('tw-027-P03').condition_contract.conditions
    .find(x => x.metric === 'golden_hour_window');
  assert.equal(c.role, 'REQUIRED');
  assert.equal(c.condition_tier, 'MAIN');
  assert.equal(c.phase, 'dusk');
  assert.ok((c.notes_i18n?.['zh-TW'] || '').includes('CL-DATA-24'));
  assert.ok((c.notes_i18n?.en || '').includes('CL-DATA-24'));
  assert.ok((c.notes_i18n?.ja || '').includes('CL-DATA-24'));
});
