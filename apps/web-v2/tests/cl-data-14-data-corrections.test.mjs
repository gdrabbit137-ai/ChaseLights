// CL-DATA-14: 委託書稽查數值修正 (CL-PHOTO-02 photo_brief_pilot_20261106 findings).
//
// Pins:
// 1. tw-040-P04 排雲山莊 LCL threshold 3268 (viewpoint altitude 3468 - 200;
//    the old 3752 wrongly used the Yushan main-peak elevation);
// 2. all four LCL cloud-sea opportunities carry camera_contexts.altitude_m
//    (DEM provenance: V1 snapshot api_elevation, DEM-200 owner formula);
// 3. tw-086-P03 AOD binding is cams_global (GFS has no measured AOD field);
// 4. snow / silver-grass subjects carry seasonal_state proxies;
// 5. tw-035-P02 crepuscular-ray cloud layering (low + mid/high, no total cap).
// Provenance + revision notes live in notes_i18n with the CL-DATA-14 marker.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '..', '..', '..');
const oppDir = path.join(repo, 'data', 'v2', 'opportunities');
const layerPath = path.join(repo, 'data', 'v2', 'staging', 'template_layering', 'assignment.json');

function loadContract(oid) {
  return JSON.parse(readFileSync(path.join(oppDir, `${oid}.json`), 'utf8'));
}
function conds(oid) {
  return loadContract(oid).condition_contract.conditions;
}

test('CL-DATA-14: tw-040-P04 LCL threshold is the Paiyun Lodge DEM-200 value (3268)', () => {
  const doc = loadContract('tw-040-P04');
  const c = doc.condition_contract.conditions.find(x => x.metric === 'lcl_height_m_agl');
  assert.ok(c, 'LCL condition present');
  assert.equal(c.threshold, 3268);
  assert.equal(c.threshold_source, 'computed');
  assert.equal(doc.camera_contexts[0].altitude_m, 3468);
  const note = c.notes_i18n?.['zh-TW'] || '';
  assert.ok(note.includes('CL-DATA-14'), 'revision note cites CL-DATA-14');
  assert.ok(note.includes('3,468') && note.includes('DEM'), 'note carries DEM provenance');
  for (const lang of ['zh-TW', 'en', 'ja']) {
    assert.ok(c.rationale_i18n?.[lang], `rationale ${lang}`);
    assert.ok(c.notes_i18n?.[lang], `note ${lang}`);
  }
});

test('CL-DATA-14: the four LCL opportunities carry camera_contexts.altitude_m', () => {
  for (const [oid, alt] of [['tw-001-P02', 1082], ['tw-019-P04', 3417],
                            ['tw-024-P02', 2450], ['tw-040-P04', 3468]]) {
    const doc = loadContract(oid);
    assert.equal(doc.camera_contexts[0].altitude_m, alt, `${oid} altitude_m`);
    const lcl = doc.condition_contract.conditions.find(x => x.metric === 'lcl_height_m_agl');
    assert.ok(lcl, `${oid} LCL condition`);
    assert.equal(lcl.threshold, alt - 200, `${oid} DEM-200 reproducible`);
  }
});

test('CL-DATA-14: tw-086-P03 AOD binds cams_global (GFS has no measured AOD)', () => {
  const c = conds('tw-086-P03').find(x => x.metric === 'aod_550nm');
  assert.ok(c, 'AOD condition present');
  assert.equal(c.model_binding, 'dataset:cams_global|field:aerosol_optical_depth_550nm|role:AEROSOL');
  assert.ok((c.notes_i18n?.['zh-TW'] || '').includes('CL-DATA-14'));
});

test('CL-DATA-14: snow-ridge subjects carry a seasonal_state snow proxy (11-4)', () => {
  for (const oid of ['tw-019-P06', 'tw-040-P03']) {
    const c = conds(oid).find(x => x.metric === 'seasonal_state');
    assert.ok(c, `${oid} seasonal_state present`);
    assert.equal(c.threshold, 'window_open');
    assert.equal(c.role, 'REQUIRED');
    assert.equal(c.condition_tier, 'MAIN');
    assert.equal(c.threshold_source, 'computed');
    assert.ok((c.rationale_i18n['zh-TW'] + c.notes_i18n['zh-TW']).includes('11'),
      `${oid} snow-window note`);
  }
});

test('CL-DATA-14: glacier subject keeps permanent-ice semantics (seasonal BONUS only)', () => {
  const c = conds('us-083-P01').find(x => x.metric === 'seasonal_state');
  assert.ok(c, 'seasonal_state present');
  assert.equal(c.role, 'QUALITY');
  assert.equal(c.condition_tier, 'BONUS');
  assert.equal(loadContract('us-083-P01').revision, 4);
});

test('CL-DATA-14: tw-001-P01 秋芒 carries the 10-11 month seasonal window', () => {
  const doc = loadContract('tw-001-P01');
  const c = doc.condition_contract.conditions.find(x => x.metric === 'seasonal_state');
  assert.ok(c, 'seasonal_state present');
  assert.equal(c.threshold, 'window_open');
  assert.equal(c.role, 'REQUIRED');
  assert.ok(c.rationale_i18n['zh-TW'].includes('10–11'), 'window 10-11 in rationale');
  assert.ok((c.notes_i18n?.['zh-TW'] || '').includes('CL-DATA-14'));
});

test('CL-DATA-14: tw-035-P02 crepuscular-ray cloud layering (no total-cloud cap)', () => {
  const doc = loadContract('tw-035-P02');
  const cs = doc.condition_contract.conditions;
  assert.ok(!cs.some(c => c.metric === 'cloud_cover_total'), 'total-cloud cap dropped');
  const low = cs.find(c => c.metric === 'cloud_cover_low');
  assert.ok(low, 'low-cloud condition present');
  assert.equal(low.operator, 'lte');
  assert.equal(low.threshold, 55);
  const mid = cs.find(c => c.metric === 'cloud_cover_mid_and_high');
  assert.ok(mid, 'mid/high condition present');
  assert.deepEqual(mid.threshold, [20, 70]);
  assert.ok((low.notes_i18n?.['zh-TW'] || '').includes('CL-DATA-14'));
});

test('CL-DATA-14: layering assignment covers the added/changed conditions', () => {
  const a = JSON.parse(readFileSync(layerPath, 'utf8'));
  const want = [
    ['tw-001-P01', 'C-tw-001-P01-06', 'seasonal_state', 'base:seasonal'],
    ['tw-019-P06', 'C-tw-019-P06-05', 'seasonal_state', 'base:seasonal'],
    ['tw-040-P03', 'C-tw-040-P03-05', 'seasonal_state', 'base:seasonal'],
    ['us-083-P01', 'C-us-083-P01-SN1', 'seasonal_state', 'base:seasonal'],
    ['tw-035-P02', 'C-tw-035-P02-05', 'cloud_cover_low', 'base:cloud_state'],
    ['tw-035-P02', 'C-tw-035-P02-06', 'cloud_cover_mid_and_high', 'base:cloud_state'],
  ];
  for (const [oid, cid, metric, layer] of want) {
    const e = (a[oid]?.conditions || []).find(x => x.condition_id === cid);
    assert.ok(e, `${oid}/${cid} in assignment`);
    assert.equal(e.metric, metric);
    assert.equal(e.layer_id, layer);
  }
});
