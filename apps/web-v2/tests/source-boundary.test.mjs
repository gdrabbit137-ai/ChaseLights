import test from 'node:test';
import assert from 'node:assert/strict';
import {navigationAction, runtimeEvaluation, safeUrl} from '../model.mjs';
test('unverified targets never create directions', () => {
  for (const status of ['needs_review', 'multiple_access_routes']) {
    assert.equal(navigationAction({status, lat:25, lon:121}), null);
  }
});
test('research is never promoted to runtime', () => {
  assert.equal(runtimeEvaluation({kind:'research',contract_status:'ready',source:'import',generated_at:'2026-10-08T00:00:00Z'}), null);
});
test('evidence links reject executable URLs', () => {
  assert.equal(safeUrl('javascript:alert(1)'), null);
});
