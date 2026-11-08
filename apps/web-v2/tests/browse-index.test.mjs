import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {importV21Catalog} from '../catalog-loader.mjs';
import {browse,validateBrowseIndex} from '../browse-index.mjs';
import {readPinned} from './pinned-worker2.mjs';

const rawIndex=readFileSync(new URL('../browse-index.v2.json',import.meta.url));
const rawCatalog=readFileSync(new URL('../catalog.v2.json',import.meta.url));
const index=JSON.parse(rawIndex),source=JSON.parse(rawCatalog),catalog=importV21Catalog(source);
const sha256=bytes=>createHash('sha256').update(bytes).digest('hex');
const blob=bytes=>createHash('sha1').update(`blob ${bytes.length}\0`).update(bytes).digest('hex');
test('W2 index and 434 canonical sources remain source pinned (CL-DATA-32 jp-051..jp-064 + CL-DATA-34 jp legacy supplement contracts)',()=>{
  assert.equal(sha256(rawIndex),'f8b7ce9899e0e915dd3eeb95396ec189ae3bd792ffb52fc771f66ffdc2155995'); // CL-INT-103: re-measured on union tree after tw-034-P02 repin
  assert.equal(sha256(rawCatalog),'92d74341fd433bb395eeab886ba6f5fbdbc43538d1b5283e4e719a392d963627'); // CL-INT-103: re-measured on union tree after tw-034-P02 repin
  assert.equal(validateBrowseIndex(index,catalog),index);
  assert.equal(source.opportunities.length,434);assert.equal(source.places.length,239);
  const pinnedOriginal=['tw-016-P01','tw-026-P01','tw-026-P02'];
  const reviewedTaskS=['tw-034-P02','tw-036-P01','tw-082-P01','jp-010-P01','us-071-P01'];
  for(const row of index.place_index.opportunities){
    const basename=row.opportunity_id+'.json';
    let bytes;
    if(pinnedOriginal.includes(row.opportunity_id)){
      readPinned(basename);
      bytes=readFileSync(new URL(`./fixtures/worker2/${basename}`,import.meta.url));
    }else if(reviewedTaskS.includes(row.opportunity_id)){
      bytes=readFileSync(new URL(`./fixtures/task-s/${basename}`,import.meta.url));
    }else{
      // Admitted no-review-gate records: byte-identity against the staged skeleton source.
      bytes=readFileSync(new URL(`../../../data/v2/opportunities/${basename}`,import.meta.url));
    }
    assert.equal(blob(bytes),row.source_blob_sha,basename);
    assert.deepEqual(source.opportunities.find(x=>x.opportunity_id===row.opportunity_id),JSON.parse(bytes));
  }
  assert.equal(catalog.evaluations.length,0);
  assert.equal(index.index_status.forecast_available,false);
  assert.equal(index.index_status.counts.verified_timezones,0);
});
test('partial multilingual name search and topic OR filter only matching opportunities',()=>{
  assert.equal(browse(index,catalog,{search:' OiShI '}).length,1);
  assert.equal(browse(index,catalog,{search:'井仔脚'}).length,1);
  assert.equal(browse(index,catalog,{search:'[.*]'}).length,0);
  assert.equal(browse(index,catalog,{search:'  '}).length,239);
  const both=browse(index,catalog,{topicIds:['topic:sunset','topic:colorful-clouds']});
  assert.deepEqual(both.map(x=>x.place.place_id),['tw-026','tw-006']); // tw-006-P02 sunset joins tw-026 (CL-DATA-20)
  assert.deepEqual(both[0].opportunities.map(x=>x.opportunity_id),['tw-026-P01','tw-026-P02']);
  assert.deepEqual(browse(index,catalog,{topicIds:['topic:sunset']})[0].opportunities.map(x=>x.opportunity_id),['tw-026-P01']);
  assert.equal(browse(index,catalog,{search:'Oishi',topicIds:['topic:sunset']}).length,0);
  assert.throws(()=>browse(index,catalog,{topicIds:['topic:invented']}),/INVALID_FILTER/);
});
test('unknown joins, revisions, approval and metadata guesses fail closed',()=>{
  for(const mutate of [
    x=>x.topic_index.opportunity_topics[0].topic_ids=['topic:invented'],
    x=>x.topic_index.taxonomy_revision='stale',
    x=>x.place_index.opportunities[0].publication='GUIDE_ELIGIBLE',
    x=>x.place_index.places[0].time_zone.iana_id='Asia/Tokyo',
    x=>x.place_index.opportunities[0].source_blob_sha='forged',
  ]){const changed=structuredClone(index);mutate(changed);assert.throws(()=>validateBrowseIndex(changed,catalog),/INVALID_RESEARCH_INDEX/);}
});
test('duplicate display names retain two distinct stable Place identities',()=>{
  const x=structuredClone(index),c=structuredClone(catalog);
  const first=x.place_index.places.find(p=>p.place_id==='jp-010');
  const second=x.place_index.places.find(p=>p.place_id==='tw-016');
  second.name_i18n=structuredClone(first.name_i18n);
  c.places.find(p=>p.place_id===second.place_id).name_i18n=structuredClone(first.name_i18n);
  validateBrowseIndex(x,c);
  const rows=browse(x,c,{search:'Oishi',locale:'en'});
  assert.deepEqual(rows.map(r=>r.place.place_id),['jp-010','tw-016']);
});
