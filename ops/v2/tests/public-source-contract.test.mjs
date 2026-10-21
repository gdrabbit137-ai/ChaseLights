import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {validateManifest,verifyPublicAsset,verifyPublicIndex} from '../public_source_contract.mjs';
const manifest=JSON.parse(readFileSync(new URL('../public-beta-r2-manifest.json',import.meta.url),'utf8'));
const raw=path=>execFileSync('git',['show',manifest.source_commit_sha+':apps/web-v2/'+path]);
const catalog=JSON.parse(raw('catalog.v2.json')),bundle=JSON.parse(raw('browse-index.v2.json'));
test('current public research manifest pins the separately observed ten published bytes',()=>{
  const current=JSON.parse(readFileSync(new URL('../public-research-20261020-manifest.json',import.meta.url),'utf8'));
  validateManifest(current);
  for(const path of Object.keys(current.files)){
    const name=path.replace('apps/web-v2/','');
    verifyPublicAsset(current,name,execFileSync('git',['show',current.source_commit_sha+':'+path]));
  }
  verifyPublicIndex(current,
    JSON.parse(execFileSync('git',['show',current.source_commit_sha+':apps/web-v2/catalog.v2.json'])),
    JSON.parse(execFileSync('git',['show',current.source_commit_sha+':apps/web-v2/browse-index.v2.json'])));
});
test('R2 manifest pins all ten original Git release bytes, not mutable main',()=>{
  validateManifest(manifest);
  for(const path of Object.keys(manifest.files))verifyPublicAsset(manifest,path.replace('apps/web-v2/',''),raw(path.replace('apps/web-v2/','')));
  verifyPublicIndex(manifest,catalog,bundle);
});
test('changed public asset bytes fail even when metadata still claims R2',()=>{
  assert.throws(()=>verifyPublicAsset(manifest,'app.mjs',Buffer.concat([raw('app.mjs'),Buffer.from('// changed')])));
});
test('old W2 index declaration cannot pass the current R2 manifest',()=>{
  assert.throws(()=>verifyPublicIndex(manifest,{...catalog,source_index_commit_sha:'c10976eb5e88fd32ec0adc58a1317ed70015821d'},bundle));
});
test('missing, extra or invalid manifest hashes fail closed',()=>{
  for(const mutate of [m=>delete m.files['apps/web-v2/model.mjs'],m=>m.files['apps/web-v2/extra.mjs']='0'.repeat(64),m=>m.files['apps/web-v2/model.mjs']='bad']){
    const changed=structuredClone(manifest);mutate(changed);assert.throws(()=>validateManifest(changed));
  }
});
test('index revision/source mismatch fails independently of subject count',()=>{
  assert.throws(()=>verifyPublicIndex(manifest,catalog,{...bundle,source_commit_sha:'0'.repeat(40)}));
  assert.throws(()=>verifyPublicIndex(manifest,{...catalog,source_index_revision:'changed'},bundle));
});
test('live flags or forged evaluation cannot pass the Research-only index contract',()=>{
  for(const delta of [{forecast_available:true},{selected_date_recommendation_eligible:true},{evaluations:[{score:100}]}])
    assert.throws(()=>verifyPublicIndex(manifest,{...catalog,...delta},bundle));
});
