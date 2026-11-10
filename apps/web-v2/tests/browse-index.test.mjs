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
test('W2 index and 420 canonical sources remain source pinned (CL-DATA-32 southern-Japan discovery admission: jp-051..jp-064, PM judgment 2026-11-08)',()=>{
  assert.equal(sha256(rawIndex),'dd75a6ee6812751e6bf2b2f191237ab12e0043f89aab5e910bb76c1b026e3d54'); // CL-DATA-66: re-measured after round12 contract fixes + index re-anchor (sha256:b02bde2d56dd)
  assert.equal(sha256(rawCatalog),'060538cfaf2d93af4118323c845db3e46f9e76ee1192c614448d0cd6f27012c4'); // CL-DATA-66: re-measured after round12 contract fixes + index re-anchor (sha256:b02bde2d56dd)
  assert.equal(validateBrowseIndex(index,catalog),index);
  assert.equal(source.opportunities.length,539);assert.equal(source.places.length,344); // CL-DATA-62 retirement on the merged tree (CL-INT-134): 6 places / 13 opportunities retired
  const pinnedOriginal=['tw-016-P01','tw-026-P01','tw-026-P02'];
  const reviewedTaskS=['tw-034-P02','tw-036-P01','tw-082-P01','jp-010-P01','us-071-P01'];
  for(const row of index.place_index.opportunities){
    const basename=row.opportunity_id+'.json';
    let bytes;
    // CL-DATA-57: tw-016-P01 is a repinned canonical record — the W2 fixture
    // keeps freezing the ORIGINAL review bytes, while the canonical record
    // evolved via the owner-rule semantic correction. Its index row must match
    // the live canonical bytes, not the frozen fixture. (CL-INT-134: restored
    // after branch-side conflict resolution dropped it.)
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
  assert.equal(browse(index,catalog,{search:'  '}).length,344); // CL-DATA-62 retirement on the merged tree
  const both=browse(index,catalog,{topicIds:['topic:sunset','topic:colorful-clouds']});
  assert.deepEqual(both.map(x=>x.place.place_id),['us-155','tw-026','us-156','us-121','tw-006']); // CL-INT-134 merged re-anchor: us-155/us-156/us-121 gained sunset/colorful-clouds topics (CL-DATA-53/54 waves)
  assert.deepEqual(both.find(x=>x.place.place_id==='tw-026').opportunities.map(x=>x.opportunity_id),['tw-026-P01','tw-026-P02']); // tw-006-P02 sunset joins tw-026 (CL-DATA-20)
  assert.deepEqual(browse(index,catalog,{topicIds:['topic:sunset']}).find(x=>x.place.place_id==='tw-026').opportunities.map(x=>x.opportunity_id),['tw-026-P01']);
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
