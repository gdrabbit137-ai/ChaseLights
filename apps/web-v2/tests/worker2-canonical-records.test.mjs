import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { importV21Catalog } from '../catalog-loader.mjs';
import { localized, navigationAction } from '../model.mjs';
import { readOriginals } from './pinned-worker2.mjs';

// Byte-exact Worker 2 records pinned in fixtures/worker2/manifest.json.
// An explicit WORKER2_DATA_DIR override must still match the pinned source blobs.
const directory = process.env.WORKER2_DATA_DIR
  ? resolve(process.env.WORKER2_DATA_DIR)
  : fileURLToPath(new URL('./fixtures/worker2/', import.meta.url));
const ids = ['tw-016-P01', 'tw-026-P01', 'tw-026-P02'];
const paths = ids.map(id => resolve(directory, id + '.json'));
const missing = paths.filter(path => !existsSync(path));

test('original Worker 2 canonical records preserve research-only semantics', () => {
  assert.deepEqual(missing, [], 'WORKER2_DATA_DIR must contain all three original files');
  const originals = readOriginals(directory);
  assert.deepEqual(originals.map(x => x.opportunity_id), ids);
  assert.ok(originals.every(x => x.schema_version === '2.1.0'));
  const catalog = importV21Catalog({schema_version:'2.1.0', opportunities:originals});
  assert.equal(catalog.opportunities.length, 3);
  assert.equal(catalog.places.length, 2);
  assert.equal(catalog.camera_zones.length, 3);
  assert.equal(catalog.subject_geometries.length, 3);
  assert.equal(catalog.view_relations.length, 3);
  // tw-016-P01 manager contract 4 conditions (2dc05b3cc) + tw-026-P01/P02
  // sunset-template contracts rebuilt under the 2026-11-02 owner ruling (5 each)
  assert.equal(catalog.conditions.length, 14);
  assert.equal(catalog.access_advisories.length, 0);
  assert.ok(catalog.conditions.every(c => c.domain !== "ACCESS_SAFETY"));
  assert.equal(catalog.evidence.length, 21);
  assert.equal(catalog.unknowns.length, 4);
  assert.deepEqual(catalog.evaluations, []);
  assert.equal(catalog.generated_at, null);
  for (const o of catalog.opportunities) {
    assert.equal(o.lifecycle_status, 'evidence_review');
    assert.equal(o.readiness?.research_level, 'R1');
    assert.ok(o.provenance?.source_catalog && o.provenance?.imported_at);
    assert.equal(navigationAction(o.navigation_target), null);
    for (const locale of ['zh-TW','en','ja']) {
      assert.ok(localized(o,'name',locale), o.opportunity_id + ' missing ' + locale);
    }
  }
  for (const relation of catalog.view_relations) {
    assert.equal(relation.distance, null);
    assert.equal(relation.elevation_angle, null);
    // CL-DATA-13: azimuth is either null (honest unknown) or a legacy V1
    // view_azimuth backfill — never a fabricated angle. The backfill is
    // flagged on the source record's derivation_method.
    assert.ok(relation.azimuth === null || typeof relation.azimuth === 'number',
      `azimuth must be null or a legacy-backfilled number: ${relation.view_relation_id}`);
  }
  assert.ok(catalog.evidence.every(e => Array.isArray(e.evidence_refs)));
  assert.ok(catalog.evidence.every(e => e.source == null && e.source_status === 'unresolved_reference'),
    'Unresolved claim metadata must never be presented as verified sources');
});
