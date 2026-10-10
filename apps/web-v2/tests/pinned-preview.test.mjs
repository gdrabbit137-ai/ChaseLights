import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {importV21Catalog} from '../catalog-loader.mjs';
import {navigationAction, runtimeEvaluation} from '../model.mjs';
import {manifest, readPinned, readOriginals, W2_SHA} from './pinned-worker2.mjs';

const preview = readPinned('tw-026-P01.research-only.v21.json');
const catalog = JSON.parse(readFileSync(new URL('../catalog.v2.json', import.meta.url), 'utf8'));

test('default catalog is the byte-verified W2 preview with only explicit provenance additions', () => {
  const additions = ['source_commit_sha','source_path','source_blob_sha','source_preview_path','source_preview_blob_sha'];
  assert.deepEqual(Object.fromEntries(Object.entries(catalog).filter(([key]) => !additions.includes(key))), preview);
  assert.equal(catalog.source_commit_sha, W2_SHA);
  for (const [path, blob] of [['source_path','source_blob_sha'],['source_preview_path','source_preview_blob_sha']]) {
    const entry = manifest.files.find(file => file.source_path === catalog[path]);
    assert.ok(entry, catalog[path]);
    assert.equal(catalog[blob], entry.blob_sha);
  }
  assert.deepEqual(preview.opportunities, [readPinned('tw-026-P01.json')]);
});

test('all real canonical records retain provisional non-AUTO conditions and unknown geometry', () => {
  for (const original of readOriginals()) {
    assert.equal(original.readiness.research_level, 'R1');
    assert.equal(original.lifecycle_status, 'evidence_review');
    for (const condition of original.condition_contract.conditions) {
      assert.notEqual(condition.evaluation_mode, 'AUTO');
      assert.equal(condition.validation_status, 'provisional');
      assert.equal(condition.threshold, null);
      assert.equal(condition.model_binding, null);
      assert.equal(condition.unknown_policy, 'propagate_unknown');
    }
    for (const relation of original.observation_relations) {
      assert.equal(relation.geometry_mode, 'unknown');
      assert.equal(relation.distance_m, null);
      assert.equal(relation.azimuth_deg, null);
      assert.equal(relation.elevation_deg, null);
    }
    assert.ok(original.navigation_targets.every(nav => navigationAction(nav) === null));
  }
});

test('real preview never becomes a live evaluation even with adversarial runtime additions', () => {
  assert.equal(preview.research_only, true);
  assert.equal(preview.forecast_available, false);
  assert.equal(preview.selected_date_recommendation_eligible, false);
  assert.deepEqual(preview.evaluations, []);
  // Deliberately forged metadata is test-only; it is never copied to research sources.
  const forged = {opportunity_id:'tw-026-P01',kind:'runtime',contract_status:'ready',
    source:'test-only-forgery',generated_at:preview.generated_at,verdict:'FAVORABLE',score:100};
  const imported = importV21Catalog({...preview,evaluations:[forged],forecast_available:true});
  assert.deepEqual(imported.evaluations, []);
  assert.equal(runtimeEvaluation(forged), null);
  assert.equal(navigationAction(imported.opportunities[0].navigation_target), null);
  assert.ok(imported.evidence.every(row => row.source === null && !row.url && row.source_status === 'unresolved_reference'));
});
