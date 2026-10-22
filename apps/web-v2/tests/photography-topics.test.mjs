import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {importV21Catalog} from '../catalog-loader.mjs';
import {researchTopic} from '../model.mjs';

const source=JSON.parse(readFileSync(new URL('../catalog.v2.json',import.meta.url),'utf8'));
const before=JSON.stringify(source);
for(const locale of ['zh-TW','en','ja']){
  test(`${locale}: all eight real subjects preserve descriptions, targets and independent role/mode`,()=>{
    const catalog=importV21Catalog(source);
    assert.equal(catalog.places.length,216);
    assert.equal(catalog.opportunities.length,428);
    for(const original of source.opportunities){
      const opp=catalog.opportunities.find(row=>row.opportunity_id===original.opportunity_id);
      const topic=researchTopic(catalog,opp,locale);
      assert.equal(topic.name,original.name_i18n[locale].trim());
      assert.equal(topic.description,original.description_i18n[locale].trim());
      assert.deepEqual(topic.targets,original.targets.map(row=>row.name_i18n[locale].trim()));
      assert.deepEqual(topic.conditions.map(row=>[row.description,row.role,row.mode,row.domain]),
        original.condition_contract.conditions.filter(row=>row.domain!=='ACCESS_SAFETY')
          .map(row=>[row.notes_i18n[locale].trim(),row.role,row.evaluation_mode,row.domain]));
      for(const condition of original.condition_contract.conditions){
        const projected=catalog.conditions.find(row=>row.condition_id===original.opportunity_id+'/'+condition.id);
        for(const key of ['evaluation_mode','capability','validation_status','model_binding'])
          assert.equal(projected[key],condition[key]??null,`${original.opportunity_id}: lost ${key}`);
      }
      assert.equal(topic.automaticEvaluationConnected,false);
      assert.equal(topic.evaluation,null);
    }
    assert.equal(JSON.stringify(source),before,'presentation must not edit Canonical source');
  });
}

test('seasonal verification remains QUALITY; REQUIRED does not imply AUTO or a successful result',()=>{
  const catalog=importV21Catalog(source);
  const jp=catalog.opportunities.find(row=>row.opportunity_id==='jp-010-P01');
  const topic=researchTopic(catalog,jp,'en');
  assert.ok(topic.conditions.some(row=>row.role==='QUALITY'&&row.mode==='VERIFY'&&row.domain==='SEASON_TIME'));
  assert.ok(topic.conditions.some(row=>row.role==='REQUIRED'&&row.mode==='GUIDANCE'));
  assert.equal(topic.evaluation,null);
});

test('missing optional topic information does not hide the other seven subjects',()=>{
  const changed=structuredClone(source);
  delete changed.opportunities[0].description_i18n;
  changed.opportunities[0].condition_contract.conditions=[];
  const catalog=importV21Catalog(changed);
  assert.equal(catalog.opportunities.length,428);
  const incomplete=researchTopic(catalog,catalog.opportunities[0],'en');
  assert.equal(incomplete.description,null);
  assert.deepEqual(incomplete.conditions,[]);
  for(const original of source.opportunities.slice(1)){
    const topic=researchTopic(catalog,catalog.opportunities.find(row=>row.opportunity_id===original.opportunity_id),'en');
    assert.equal(topic.description,original.description_i18n.en);
    assert.equal(topic.conditions.length,original.condition_contract.conditions.length);
  }
});

test('an AUTO declaration or forged imported result cannot enable research condition assessment',()=>{
  // Adversarial metadata only, not new weather or scientific evidence.
  const changed=structuredClone(source);
  changed.opportunities[0].condition_contract.conditions[0].evaluation_mode='AUTO';
  changed.evaluations=[{opportunity_id:changed.opportunities[0].opportunity_id,verdict:'PASS',score:100}];
  const catalog=importV21Catalog(changed);
  const topic=researchTopic(catalog,catalog.opportunities[0],'en');
  assert.equal(topic.conditions[0].mode,'AUTO');
  assert.equal(topic.automaticEvaluationConnected,false);
  assert.equal(topic.evaluation,null);
  assert.deepEqual(catalog.evaluations,[]);
});

test('access warnings stay outside photography conditions, and unsupported modes remain unspecified',()=>{
  const catalog=importV21Catalog(source);
  const opp=catalog.opportunities.find(row=>row.opportunity_id==='tw-016-P01');
  const original=source.opportunities.find(row=>row.opportunity_id==='tw-016-P01');
  catalog.conditions.push({opportunity_id:opp.opportunity_id,condition_id:'test-only-access',domain:'ACCESS_SAFETY',role:'BLOCKER',evaluation_mode:'VERIFY'});
  const first=catalog.conditions.find(row=>row.opportunity_id===opp.opportunity_id);
  delete first.evaluation_mode;
  const topic=researchTopic(catalog,opp,'en');
  assert.equal(topic.conditions.length,
    original.condition_contract.conditions.filter(row=>row.domain!=='ACCESS_SAFETY').length);
  assert.ok(topic.conditions.every(row=>row.domain!=='ACCESS_SAFETY'));
  assert.equal(topic.conditions[0].mode,null);
  assert.equal(topic.evaluation,null);
});
