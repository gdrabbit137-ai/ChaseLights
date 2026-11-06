// CL-DATA-12: contract semantic fixes wave 1 (batches A–O).
//
// Full-audit confirmation of MISMATCH contracts. Every fix is a semantic
// correction: the layering parity gate is exempt per record and the
// provenance/audit source + trilingual rationale live in notes_i18n with the
// CL-DATA-12 marker. Pinned scenarios (owner-mandated):
// - 琉璃光 night low-cloud proxy (tw-020-P03 / tw-023-P03);
// - reflection without calm wind must NOT qualify (wind <=2 REQUIRED);
// - 祝山日出雲海 is a cloud sea behind a REQUIRED sunrise window;
// - AK polar-night all-day subjects need the civil light_window (us-056-P01).
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '..', '..', '..');
const oppDir = path.join(repo, 'data', 'v2', 'opportunities');

function loadContract(oid) {
  return JSON.parse(readFileSync(path.join(oppDir, `${oid}.json`), 'utf8'));
}

function conds(oid) {
  return loadContract(oid).condition_contract.conditions;
}

test('CL-DATA-12 A/G: threshold=null cloud_cover_low conditions carry the owner-corrected 30/lte', () => {
  const IDS = [
    'tw-018-P03', 'tw-022-P03', 'tw-032-P01', 'tw-034-P02',
    'jp-003-P01', 'jp-006-P01', 'jp-011-P01', 'jp-027-P01', 'jp-035-P01',
    'us-050-P01', 'us-050-P02', 'us-064-P01', 'us-075-P01', 'us-080-P01',
    'us-083-P01', 'us-083-P02', 'us-091-P01',
  ];
  for (const oid of IDS) {
    const c = conds(oid).find(x => x.metric === 'cloud_cover_low');
    assert.ok(c, `${oid} has cloud_cover_low`);
    assert.equal(c.operator, 'lte', `${oid} operator`);
    assert.equal(c.threshold, 30, `${oid} threshold`);
    assert.equal(c.role, 'REQUIRED', `${oid} REQUIRED`);
    assert.ok((c.notes_i18n?.['zh-TW'] || '').includes('CL-DATA-12'),
      `${oid} revision note cites CL-DATA-12`);
    for (const lang of ['zh-TW', 'en', 'ja']) {
      assert.ok(c.rationale_i18n?.[lang], `${oid} rationale ${lang}`);
      assert.ok(c.notes_i18n?.[lang], `${oid} note ${lang}`);
    }
  }
});

test('CL-DATA-12 B: 琉璃光 night low-cloud proxy replaces the inverted total-cloud cap', () => {
  for (const [oid, lcl] of [['tw-020-P03', 620], ['tw-023-P03', 1170]]) {
    const doc = loadContract(oid);
    const cs = conds(oid);
    assert.equal(doc.condition_contract.genre_template, 'blue_hour_city',
      `${oid} keeps the blue-hour genre/window`);
    assert.ok(!cs.some(c => c.metric === 'cloud_cover_total'),
      `${oid} drops the cloud_cover_total cap`);
    const m = Object.fromEntries(cs.map(c => [c.metric, c]));
    assert.equal(m['relative_humidity_925hpa'].threshold, 85);
    assert.equal(m['relative_humidity_850hpa'].threshold, 55);
    assert.equal(m['lcl_height_m_agl'].threshold, lcl, `${oid} LCL from same-viewpoint cloud_sea sibling`);
    assert.equal(m['cloud_cover_low'].operator, 'gte');
    assert.equal(m['cloud_cover_low'].threshold, 60, `${oid} low cloud >=60 REQUIRED (mid/high uncapped)`);
    assert.ok((m['cloud_cover_low'].notes_i18n?.['zh-TW'] || '').includes('CL-DATA-12'));
  }
});

test('CL-DATA-12 C: reflection subjects require calm wind — no wind metric never qualifies them', () => {
  for (const [oid, th] of [['tw-003-P03', 2], ['tw-011-P02', 2], ['jp-016-P02', 2],
                           ['jp-031-P02', 2], ['tw-045-P03', 3]]) {
    const w = conds(oid).find(c => c.metric === 'wind_speed_10m');
    assert.ok(w, `${oid} carries a wind condition`);
    assert.equal(w.operator, 'lte');
    assert.equal(w.threshold, th, `${oid} wind <=${th}`);
    assert.equal(w.role, 'REQUIRED', `${oid} wind REQUIRED`);
    assert.equal(w.condition_tier, 'MAIN', `${oid} wind MAIN`);
    assert.ok((w.notes_i18n?.['zh-TW'] || '').includes('CL-DATA-12'));
  }
});

test('CL-DATA-12 D: 祝山日出雲海 is cloud_sea behind a REQUIRED sunrise window', () => {
  const doc = loadContract('tw-024-P02');
  assert.equal(doc.condition_contract.genre_template, 'cloud_sea');
  const sr = conds('tw-024-P02').find(c => c.metric === 'sunrise_time_window');
  assert.equal(sr.role, 'REQUIRED');
  assert.equal(sr.condition_tier, 'MAIN');
  const cs = conds('tw-024-P02');
  assert.equal(cs.find(c => c.metric === 'lcl_height_m_agl').threshold, 2251); // CL-DATA-15: Zhushan 2,451 m (owner-verified) - 200
  assert.equal(cs.find(c => c.metric === 'cloud_cover_low').operator, 'gte');
  assert.ok(cs.some(c => c.metric === 'light_window'), 'cloud sea carries light_window');
});

test('CL-DATA-12 F: AK polar-night all-day subjects need the civil light_window', () => {
  const doc = loadContract('us-056-P01');
  const w = conds('us-056-P01').find(c => c.metric === 'light_window');
  assert.ok(w, 'us-056-P01 (68.13N) carries light_window');
  assert.equal(w.role, 'REQUIRED');
  assert.equal(w.condition_tier, 'MAIN');
  assert.equal(w.threshold_source, 'computed');
  assert.ok((w.notes_i18n?.['zh-TW'] || '').includes('CL-DATA-12'));
  assert.ok((w.rationale_i18n?.['en'] || '').includes('-6'));
});

test('CL-DATA-12 us-057-P01 human-review contract is untouched', () => {
  const doc = loadContract('us-057-P01');
  assert.ok(!doc.condition_contract.conditions.some(c => c.metric === 'light_window'),
    'us-057-P01 gains no light_window (owner calibration pending)');
  assert.ok(!readFileSync(path.join(oppDir, 'us-057-P01.json'), 'utf8').includes('CL-DATA-12'));
});

test('CL-DATA-12 H/I/J: window-role semantics pinned', () => {
  // Kerry Park sunset: sunset REQUIRED/MAIN, blue hour demoted to QUALITY/BONUS.
  const kerry = conds('us-071-P02');
  assert.equal(kerry.find(c => c.metric === 'sunset_window').role, 'REQUIRED');
  assert.equal(kerry.find(c => c.metric === 'blue_hour_window').role, 'QUALITY');
  // Brooks Falls / larch season gates.
  for (const oid of ['us-059-P02', 'us-091-P01']) {
    const s = conds(oid).find(c => c.metric === 'seasonal_state');
    assert.equal(s.threshold, 'window_open', `${oid} seasonal_state window_open`);
    assert.equal(s.role, 'REQUIRED');
  }
  // Palouse light-and-shadow: sunset window is MAIN now.
  assert.equal(conds('us-094-P01').find(c => c.metric === 'sunset_window').condition_tier, 'MAIN');
  // All-day panoramas: sunrise demoted to MODIFIER.
  for (const oid of ['tw-036-P04', 'tw-024-P03', 'tw-049-P01']) {
    const w = conds(oid).find(c => c.metric === 'sunrise_time_window');
    assert.equal(w.role, 'QUALITY', `${oid} sunrise window MODIFIER`);
    assert.equal(w.condition_tier, 'MODIFIER');
  }
  // Sunset-named subjects upgraded to REQUIRED/MAIN.
  for (const oid of ['tw-040-P05', 'tw-040-P01']) {
    const metric = oid === 'tw-040-P01' ? 'sunrise_time_window' : 'sunset_window';
    const w = conds(oid).find(c => c.metric === metric);
    assert.equal(w.role, 'REQUIRED', `${oid} ${metric} REQUIRED`);
    assert.equal(w.condition_tier, 'MAIN');
  }
  // Yehliu Queen's Head: civil daylight window REQUIRED, sunrise demoted.
  const yehliu = conds('tw-074-P01');
  assert.equal(yehliu.find(c => c.metric === 'light_window').role, 'REQUIRED');
  assert.equal(yehliu.find(c => c.metric === 'sunrise_time_window').role, 'QUALITY');
});

test('CL-DATA-12 N: tidal subjects are honestly not_evaluatable (fail-closed)', () => {
  for (const oid of ['tw-059-P01', 'tw-060-P01', 'tw-078-P01']) {
    const doc = loadContract(oid);
    const legacy = doc.condition_contract.conditions;
    assert.equal(legacy.length, 1, `${oid} keeps a single legacy placeholder`);
    assert.ok(legacy[0].metric.startsWith('legacy_'), `${oid} no fabricated weather gates`);
    assert.equal(legacy[0].unknown_policy, 'propagate_unknown');
    // The migration-skeleton drift guard pins these un-applied records byte
    // for byte, so the tidal ruling is recorded in the source-lock repin note
    // instead of inside the record.
    assert.ok(!readFileSync(path.join(oppDir, `${oid}.json`), 'utf8').includes('CL-DATA-12'),
      `${oid} bytes untouched (migration archive identity)`);
  }
  const lock = JSON.parse(readFileSync(
    path.join(repo, 'data/v2/indexes/research/source-lock.json'), 'utf8'));
  assert.ok((lock.repin_note_cl_data_12_20261106 || '').includes('tidal module'),
    'source-lock repin note records the tidal not_evaluatable ruling');
});

test('CL-DATA-12 revision/provenance sweep: every touched record cites the ticket', () => {
  const IDS = [
    'tw-020-P03', 'tw-023-P03', 'tw-003-P03', 'tw-011-P02', 'jp-016-P02',
    'jp-031-P02', 'tw-045-P03', 'tw-024-P02', 'tw-035-P06', 'jp-010-P02',
    'tw-005-P01', 'tw-036-P04', 'tw-024-P03', 'tw-040-P05', 'tw-027-P02',
    'tw-040-P01', 'us-041-P01', 'us-045-P01', 'us-046-P01', 'us-047-P01',
    'us-048-P01', 'us-048-P02', 'us-050-P01', 'us-050-P02', 'us-052-P01',
    'us-052-P02', 'us-055-P01', 'us-055-P02', 'us-056-P01', 'us-059-P01',
    'us-059-P02', 'us-060-P01', 'us-060-P02', 'us-061-P01', 'us-061-P02',
    'us-063-P01', 'us-064-P01', 'us-071-P02', 'us-075-P01', 'us-080-P01',
    'us-083-P01', 'us-083-P02', 'us-091-P01', 'us-094-P01', 'us-001-P01',
    'us-006-P01', 'us-007-P02', 'us-012-P01', 'us-012-P02', 'us-014-P01',
    'us-014-P02', 'us-024-P01', 'us-026-P01', 'us-010-P01', 'tw-047-P01',
    'tw-049-P01', 'tw-049-P03', 'tw-052-P01', 'tw-074-P01', 'tw-076-P01',
    'tw-062-P01',
  ];
  for (const oid of IDS) {
    const doc = loadContract(oid);
    const touched = doc.condition_contract.conditions.some(
      c => (c.notes_i18n?.['zh-TW'] || '').includes('CL-DATA-12'));
    assert.ok(touched, `${oid} carries a CL-DATA-12 condition note`);
    assert.ok(doc.revision >= 2, `${oid} revision bumped`);
  }
});
