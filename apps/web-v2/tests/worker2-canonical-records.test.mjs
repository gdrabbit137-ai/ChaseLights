import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { importV21Catalog } from '../catalog-loader.mjs';
import { localized, navigationAction } from '../model.mjs';

// Original Worker 2 records only: no copied or synthesized evidence fixtures.
// WORKER2_DATA_DIR points to data/v2/opportunities in an independent W2 worktree.
const directory = process.env.WORKER2_DATA_DIR
  ? resolve(process.env.WORKER2_DATA_DIR)
  : fileURLToPath(new URL('../../../data/v2/opportunities/', import.meta.url));
const ids = ['tw-016-P01', 'tw-026-P01', 'tw-026-P02'];
const paths = ids.map(id => resolve(directory, id + '.json'));
const missing = paths.filter(path => !existsSync(path));

if (missing.length && !process.env.WORKER2_DATA_DIR) {
  test('BLOCKED: original Worker 2 records not checked out', {
    skip: 'W2 data not merged; set WORKER2_DATA_DIR to the original W2 worktree data/v2/opportunities'
  }, () => {});
} else {
  test('original Worker 2 canonical records preserve research-only semantics', () => {
    assert.deepEqual(missing, [], 'WORKER2_DATA_DIR must contain all three original files');
    const originals = paths.map(path => JSON.parse(readFileSync(path, 'utf8')));
    assert.deepEqual(originals.map(x => x.opportunity_id), ids);
    assert.ok(originals.every(x => x.schema_version === '2.1.0'));
    const catalog = importV21Catalog({schema_version:'2.1.0', opportunities:originals});
    assert.equal(catalog.opportunities.length, 3);
    assert.equal(catalog.places.length, 2);
    assert.equal(catalog.camera_zones.length, 3);
    assert.equal(catalog.subject_geometries.length, 3);
    assert.equal(catalog.view_relations.length, 3);
    assert.equal(catalog.conditions.length, 12);
    assert.equal(catalog.evidence.length, 21);
    assert.equal(catalog.unknowns.length, 6);
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
      assert.equal(relation.azimuth, null);
      assert.equal(relation.elevation_angle, null);
    }
    assert.ok(catalog.evidence.every(e => Array.isArray(e.evidence_refs)));
    assert.ok(catalog.evidence.every(e => e.source == null && e.source_status === 'unresolved_reference'),
      'Unresolved claim metadata must never be presented as verified sources');
  });
}
