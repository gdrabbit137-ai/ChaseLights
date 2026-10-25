import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {importV21Catalog} from '../catalog-loader.mjs';
import {navigationAction, runtimeEvaluation} from '../model.mjs';
import {manifest, readPinned, readOriginals, W2_SHA} from './pinned-worker2.mjs';

const preview = readPinned('tw-026-P01.research-only.v21.json');
const catalog = JSON.parse(readFileSync(new URL('../catalog.v2.json', import.meta.url), 'utf8'));

test('default catalog retains the original pinned P01 source and research-only publication', () => {
  const original = catalog.opportunities.find(o => o.opportunity_id === 'tw-026-P01');
  assert.deepEqual(original, readPinned('tw-026-P01.json'));
  assert.equal(catalog.source_pins['tw-026-P01'].source_commit_sha, W2_SHA);
  assert.equal(catalog.source_pins['tw-026-P01'].source_blob_sha,
    manifest.files.find(file => file.source_path === 'data/v2/opportunities/tw-026-P01.json').blob_sha);
  assert.equal(catalog.opportunities.length,416);
  assert.equal(catalog.places.length,214);
  assert.deepEqual(preview.opportunities, [readPinned('tw-026-P01.json')]);
});

test('all real canonical records retain provisional non-AUTO conditions and unknown geometry', () => {
  for (const original of readOriginals()) {
    assert.equal(original.readiness.research_level, 'R1');
    assert.equal(original.lifecycle_status, 'evidence_review');
    for (const condition of original.condition_contract.conditions) {
      assert.notEqual(condition.domain, 'ACCESS_SAFETY');
      assert.notEqual(condition.evaluation_mode, 'AUTO');
      assert.equal(condition.validation_status, 'provisional');
      assert.ok(condition.threshold === null || typeof condition.threshold === 'number' || Array.isArray(condition.threshold));
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


test('latest W2 source preserves lawful-area uncertainty in all three languages', () => {
  const canonical = readPinned('tw-026-P01.json');
  const mirrored = catalog.opportunities.find(o => o.opportunity_id === 'tw-026-P01');
  const phrases = {
    'zh-TW': '可拍攝區域邊界尚未獨立核實',
    en: 'boundaries of permitted shooting areas have not been independently verified',
    ja: '撮影可能区域の境界は独立に確認できていない'
  };
  for (const [locale, phrase] of Object.entries(phrases)) {
    assert.equal(mirrored.description_i18n[locale], canonical.description_i18n[locale]);
    assert.ok(mirrored.description_i18n[locale].includes(phrase), locale + ': camera access uncertainty lost');
    assert.equal(mirrored.camera_contexts[0].access_notes_i18n[locale],
      canonical.camera_contexts[0].access_notes_i18n[locale]);
    assert.equal(mirrored.condition_contract.conditions[0].notes_i18n[locale],
      canonical.condition_contract.conditions[0].notes_i18n[locale]);
  }
  assert.ok(mirrored.navigation_targets.every(target => navigationAction(target) === null));
  assert.equal(catalog.research_only, true);
  assert.equal(catalog.forecast_available, false);
  assert.equal(catalog.selected_date_recommendation_eligible, false);
  assert.deepEqual(catalog.evaluations, []);
});
