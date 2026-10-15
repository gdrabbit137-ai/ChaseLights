import test from 'node:test';
import assert from 'node:assert/strict';
import {createCatalogState} from '../catalog-state.mjs';
import {importV21Catalog} from '../catalog-loader.mjs';
import {readPinned, readOriginals} from './pinned-worker2.mjs';
const preview = readPinned('tw-026-P01.research-only.v21.json');
const response = (body, status=200) => ({status,ok:status>=200 && status<300,text:async()=>typeof body==='string'?body:JSON.stringify(body)});
const deferred = () => {let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve};};
const local = body => ({name:'local-research.json',text:async()=>JSON.stringify(body)});
const assertCleared = state => {for(const key of ['catalog','selected','source','loaded'])assert.equal(state[key],null,key+' must clear');};

test('pending fetch has no stale record and retry clicks share one real request', async()=>{
  const pending=deferred();let calls=0;const changes=[];
  const state=createCatalogState({fetchImpl:()=>{calls++;return pending.promise;},onChange:s=>changes.push(s.status)});
  const first=state.load();assert.equal(state.load(),first);assert.equal(state.load(),first);
  assert.equal(calls,1);assert.equal(state.getState().status,'loading');assertCleared(state.getState());
  pending.resolve(response(preview));await first;
  assert.deepEqual(changes,['loading','ready']);assert.equal(state.getState().catalog.opportunities.length,1);
  assert.deepEqual(state.getState().catalog.evaluations,[]);
});
for(const [http,status] of [[404,'unavailable'],[500,'error']])test(`HTTP ${http} clears previous imported data and a genuine retry recovers`,async()=>{
  let calls=0;const state=createCatalogState({fetchImpl:async()=>response(preview,++calls===1?http:200)});
  await state.importFile(local(preview));await state.load();
  assert.equal(state.getState().status,status);assertCleared(state.getState());
  await state.load();assert.equal(calls,2);assert.equal(state.getState().status,'ready');
});
test('network and interrupted response failures are errors, never raw exceptions or data',async()=>{
  for(const fetchImpl of [async()=>{throw Error('private raw detail');},async()=>({status:200,ok:true,text:async()=>{throw Error('broken body');}})]){
    const state=createCatalogState({fetchImpl});await state.load();assert.equal(state.getState().status,'error');assertCleared(state.getState());
  }
});
for(const [kind,body] of [['malformed JSON','{'],['schema mismatch',{...preview,schema_version:'9'}],['missing locale',(()=>{const x=structuredClone(preview);delete x.opportunities[0].name_i18n.ja;return x;})()]])test(`${kind} invalidates cards, selection and provenance`,async()=>{
  const state=createCatalogState({fetchImpl:async()=>response(body)});await state.importFile(local(preview));await state.load();
  assert.equal(state.getState().status,'invalid');assertCleared(state.getState());
});
test('empty transport is recognized without weakening canonical validation',async()=>{
  for(const body of ['',[],{},null,{schema_version:'2.1.0',opportunities:[]}]){
    const state=createCatalogState({fetchImpl:async()=>response(body)});await state.load();assert.equal(state.getState().status,'empty');assertCleared(state.getState());
  }
  assert.throws(()=>importV21Catalog({schema_version:'2.1.0',opportunities:[]}));
  const state=createCatalogState({fetchImpl:async()=>response({schema_version:'9',opportunities:[]})});
  await state.load();assert.equal(state.getState().status,'invalid');
});
test('late fetch ignoring abort cannot overwrite the newer local import',async()=>{
  const pending=deferred();let signal;
  const state=createCatalogState({fetchImpl:(_url,options)=>{signal=options.signal;return pending.promise;}});
  const first=state.load();await state.importFile(local({opportunities:readOriginals()}));
  assert.equal(signal.aborted,true);assert.equal(state.getState().catalog.opportunities.length,3);
  pending.resolve(response(preview));await first;
  assert.equal(state.getState().catalog.opportunities.length,3);assert.equal(state.getState().source,'local-research.json');
});
test('latest local file wins when file reads resolve out of order',async()=>{
  const pending=deferred();const state=createCatalogState();
  const first=state.importFile({name:'older.json',text:()=>pending.promise});
  await state.importFile({name:'newer.json',text:async()=>JSON.stringify(preview)});
  pending.resolve('{');await first;assert.equal(state.getState().status,'ready');assert.equal(state.getState().source,'newer.json');
});
test('reload preserves an existing stable selection, clears it while pending and replaces a removed selection',async()=>{
  const state=createCatalogState({fetchImpl:async()=>response(preview)});
  await state.importFile(local({opportunities:readOriginals()}));state.select('tw-016');
  const original=state.getState().selected;await state.importFile(local({opportunities:readOriginals()}));assert.equal(state.getState().selected,original);
  const loading=state.load();assert.equal(state.getState().selected,null);await loading;
  assert.equal(state.getState().selected,'tw-026');state.select('invented');assert.equal(state.getState().selected,'tw-026');
});
test('local forged runtime remains research-only and failed reads clear previous truth',async()=>{
  const state=createCatalogState();
  await state.importFile(local({...preview,forecast_available:true,evaluations:[{verdict:'FAVORABLE',score:100}]}));
  assert.deepEqual(state.getState().catalog.evaluations,[]);assert.equal(state.getState().catalog.metadata.research_only,true);
  await state.importFile({name:'unreadable.json',text:async()=>{throw Error('raw file error');}});
  assert.equal(state.getState().status,'invalid');assertCleared(state.getState());
});
test('default bundle verification fails closed, while a local import is explicitly untrusted',async()=>{
  let approved=false;
  const state=createCatalogState({fetchImpl:async()=>response(preview),verifyDefault:async()=>approved});
  await state.load();assert.equal(state.getState().status,'invalid');assertCleared(state.getState());
  await state.importFile(local(preview));assert.equal(state.getState().status,'ready');
  assert.equal(state.getState().verifiedBundle,false);
  approved=true;await state.load();assert.equal(state.getState().status,'ready');
  assert.equal(state.getState().verifiedBundle,true);
});
test('late default verification cannot erase a newer local import',async()=>{
  const pending=deferred();
  const state=createCatalogState({fetchImpl:async()=>response(preview),verifyDefault:()=>pending.promise});
  const first=state.load();
  await new Promise(resolve=>setImmediate(resolve));
  await state.importFile(local({opportunities:readOriginals()}));
  pending.resolve(false);await first;
  assert.equal(state.getState().status,'ready');
  assert.equal(state.getState().catalog.opportunities.length,3);
  assert.equal(state.getState().verifiedBundle,false);
});
