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
test('W2 index and canonical sources remain source pinned (CL-DATA-66 wave7: 460 places / 692 opportunities)',()=>{
  assert.equal(sha256(rawIndex),'7940b21c7862109f4bc05984b005c0cb0948b400865758cb69dbec8297a3bdce'); // re-measured CL-DATA-66 wave6 (449 places / 681 opportunities)
  assert.equal(sha256(rawCatalog),'bdf6a9a681d3c94cac56ccdda263ba4362bfaab97de084d256816de705bf558c'); // re-measured CL-DATA-66 wave6 (449 places / 681 opportunities)
  assert.equal(validateBrowseIndex(index,catalog),index);
  assert.equal(source.opportunities.length,692);assert.equal(source.places.length,460); // re-anchored CL-DATA-66 wave7 (tw-217..227)
  const pinnedOriginal=['tw-016-P01','tw-026-P01','tw-026-P02'];
  const reviewedTaskS=['tw-034-P02','tw-036-P01','tw-082-P01','jp-010-P01','us-071-P01'];
  for(const row of index.place_index.opportunities){
    const basename=row.opportunity_id+'.json';
    let bytes;
    // CL-DATA-57: tw-016-P01 is a repinned canonical record — the W2 fixture
    // keeps freezing the ORIGINAL review bytes (2af08fb9 provenance), while
    // the canonical record evolved via the owner-rule semantic correction
    // (sunset_window promoted REQUIRED/MAIN). Its index row must match the
    // live canonical bytes, not the frozen fixture.
    if(row.opportunity_id==='tw-016-P01'){
      readPinned(basename);
      bytes=readFileSync(new URL(`../../../data/v2/opportunities/${basename}`,import.meta.url));
    }else if(pinnedOriginal.includes(row.opportunity_id)){
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
  assert.equal(browse(index,catalog,{search:'  '}).length,460); // re-anchored CL-DATA-66 wave7 (460 places)
  const both=browse(index,catalog,{topicIds:['topic:sunset','topic:colorful-clouds']});
  assert.deepEqual(both.map(x=>x.place.place_id),['tw-148','tw-161','tw-150','us-155','tw-026','tw-162','tw-166','us-156','tw-137','tw-168','tw-138','tw-139','tw-169','tw-142','tw-143','tw-171','tw-153','us-121','tw-216','tw-178','tw-156','tw-186','tw-188','tw-191','tw-147','tw-006','tw-157','tw-194','tw-195','tw-159']); // re-anchored CL-DATA-66 wave7 (460 places; sunset OR colorful-clouds; wave7 adds no sunset/colorful-clouds contracts)
  assert.deepEqual(both[0].opportunities.map(x=>x.opportunity_id),['tw-148-P02']); // re-anchored CL-DATA-66 wave3 (tw-148 leads the sunset OR colorful-clouds list)
  assert.deepEqual(browse(index,catalog,{topicIds:['topic:sunset']})[0].opportunities.map(x=>x.opportunity_id),['tw-148-P02']); // re-anchored CL-DATA-66 wave2
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
