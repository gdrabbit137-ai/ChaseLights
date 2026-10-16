import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {importV21Catalog, CatalogImportError} from '../catalog-loader.mjs';
import {localized} from '../model.mjs';
import {readOriginals, W2_SHA} from './pinned-worker2.mjs';

const records=readOriginals();
const defaultCatalog=JSON.parse(readFileSync(new URL('../catalog.v2.json',import.meta.url),'utf8'));
const locales=['zh-TW','en','ja'];

test('declared source commit survives projection without promoting research or persisting across imports',()=>{
  const projected=importV21Catalog(defaultCatalog);
  assert.equal(projected.metadata.source_commit_sha,null);
  assert.equal(projected.metadata.source_pins['tw-026-P01'].source_commit_sha,W2_SHA);
  assert.equal(projected.metadata.research_only,true);
  assert.deepEqual(projected.evaluations,[]);
  assert.equal(importV21Catalog(records[0]).metadata.source_commit_sha,null);
  for(const sha of ['main','7f10e9bd','<script>','',null])
    assert.equal(importV21Catalog({...defaultCatalog,source_commit_sha:sha}).metadata.source_commit_sha,null);
});

for(const locale of locales){
  test(`${locale}: real descriptions, access/safety, targets and conditions preserve exact W2 meaning`,()=>{
    const c=importV21Catalog({opportunities:records});
    for(const original of records){
      const opportunity=c.opportunities.find(x=>x.opportunity_id===original.opportunity_id);
      assert.equal(localized(opportunity,'name',locale),original.name_i18n[locale].trim());
      for(const camera of original.camera_contexts){
        const row=c.camera_zones.find(x=>x.camera_zone_id===`${original.opportunity_id}/${camera.id}`);
        for(const key of ['access_notes','safety_notes'])
          assert.equal(localized(row,key,locale),camera[key+'_i18n'][locale].trim());
      }
      for(const condition of original.condition_contract.conditions){
        const row=c.conditions.find(x=>x.condition_id===`${original.opportunity_id}/${condition.id}`);
        assert.equal(localized(row,'human_description',locale),condition.notes_i18n[locale].trim());
      }
      for(const target of original.targets){
        const row=c.subject_geometries.find(x=>x.subject_geometry_id===`${original.opportunity_id}/${target.id}`);
        assert.equal(localized(row,'name',locale),target.name_i18n[locale].trim());
      }
    }
  });
  test(`${locale}: incomplete optional safety/access and navigation translations fail closed`,()=>{
    for(const key of ['access_notes_i18n','safety_notes_i18n']){
      const doc=structuredClone(records[1]);delete doc.camera_contexts[0][key][locale];
      assert.throws(()=>importV21Catalog(doc),e=>e instanceof CatalogImportError && e.code==='INVALID_SCHEMA');
    }
    // Test-only labels do not add coordinates, evidence or navigation verification.
    for(const kind of ['description','navigation','place']){
      const doc=structuredClone(records[1]);
      const text={...doc.name_i18n};delete text[locale];
      if(kind==='description')doc.description_i18n=text;
      if(kind==='navigation')doc.navigation_targets=[{id:'test-only-pending',status:'needs_review',label_i18n:text}];
      const envelope=kind==='place'?{opportunities:[doc],places:[{spot_id:doc.place_id,name_i18n:text}]}:doc;
      assert.throws(()=>importV21Catalog(envelope),e=>e instanceof CatalogImportError && e.code==='INVALID_SCHEMA');
    }
  });
}
