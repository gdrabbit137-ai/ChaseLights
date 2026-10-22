// Immutable public byte verification; research metadata is never deployment proof.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
// Core runtime files every published release must pin. bundle-digests.mjs is
// the W4 packaging addition: required for post-W4 candidate manifests, absent
// from the immutable historical R2 release evidence — so it is allowed but
// never required. Unknown files still fail closed.
export const requiredRuntimeFiles=['index.html','styles.css','app.mjs','model.mjs','catalog-loader.mjs','catalog-state.mjs','v21-adapter.mjs','browse-index.mjs','browse-index.v2.json','catalog.v2.json'];
export const optionalRuntimeFiles=['bundle-digests.mjs'];
export const runtimeFiles=[...requiredRuntimeFiles,...optionalRuntimeFiles];
export function validateManifest(manifest){
  assert.equal(manifest.status,'PASS');
  assert.equal(manifest.mode,'RESEARCH_ONLY');
  assert.equal(manifest.deployment_allowed,false);
  assert.equal(manifest.live_forecast_eligible,false);
  assert.match(manifest.source_commit_sha,/^[a-f0-9]{40}$/);
  assert.match(manifest.source_index_commit_sha,/^[a-f0-9]{40}$/);
  const keys=Object.keys(manifest.files);
  for(const f of requiredRuntimeFiles)assert.ok(keys.includes('apps/web-v2/'+f),'manifest missing required runtime file: '+f);
  for(const key of keys)assert.ok(runtimeFiles.includes(key.slice('apps/web-v2/'.length)),'manifest declares unknown runtime file: '+key);
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
