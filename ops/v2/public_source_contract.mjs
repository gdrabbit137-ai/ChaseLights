// Immutable public byte verification; research metadata is never deployment proof.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
export const runtimeFiles=['index.html','styles.css','app.mjs','model.mjs','catalog-loader.mjs','catalog-state.mjs','v21-adapter.mjs','browse-index.mjs','browse-index.v2.json','catalog.v2.json','bundle-digests.mjs'];
export function validateManifest(manifest){
  assert.equal(manifest.status,'PASS');
  assert.equal(manifest.mode,'RESEARCH_ONLY');
  assert.equal(manifest.deployment_allowed,false);
  assert.equal(manifest.live_forecast_eligible,false);
  assert.match(manifest.source_commit_sha,/^[a-f0-9]{40}$/);
  assert.match(manifest.source_index_commit_sha,/^[a-f0-9]{40}$/);
  assert.deepEqual(Object.keys(manifest.files).sort(),runtimeFiles.map(f=>'apps/web-v2/'+f).sort());
  for(const hash of Object.values(manifest.files))assert.match(hash,/^[a-f0-9]{64}$/);
  return manifest;
}
export function verifyPublicAsset(manifest,path,body){
  assert.equal(createHash('sha256').update(body).digest('hex'),manifest.files['apps/web-v2/'+path],path+' public bytes differ from immutable manifest');
}
export function verifyPublicIndex(manifest,catalog,bundle){
  assert.equal(catalog.source_index_commit_sha,manifest.source_index_commit_sha);
  assert.equal(bundle.source_commit_sha,manifest.source_index_commit_sha);
  assert.equal(catalog.source_index_revision,bundle.manifest.index_revision);
  assert.equal(bundle.manifest.mode,'RESEARCH_ONLY');
  assert.equal(catalog.research_only,true);
  assert.equal(catalog.selected_date_recommendation_eligible,false);
  assert.equal(catalog.forecast_available,false);
  assert.deepEqual(catalog.evaluations,[]);
}
