import test from 'node:test';
import assert from 'node:assert/strict';
import {importV21Catalog,CatalogImportError} from '../catalog-loader.mjs';
import {navigationAction,runtimeEvaluation,localized} from '../model.mjs';
const tr=(zh,en,ja)=>({'zh-TW':zh,en,ja});
const doc=()=>({
 schema_version:'2.1.0',opportunity_id:'tw-016-P01',place_id:'tw-016',revision:1,lifecycle_status:'evidence_review',
 name_i18n:tr('鳶嘴山岩稜','Yanzui ridge','鳶嘴山の岩稜'),
 camera_contexts:[{id:'camera1',geometry:{kind:'area',status:'unknown'},access_notes_i18n:tr('合法步道','Legal trail','指定登山道')}],
 targets:[{id:'target1',kind:'fixed_geographic',name_i18n:tr('山稜','Ridge','岩稜'),geometry:{kind:'ridge',status:'unknown'}}],
 observation_relations:[{id:'rel1',camera_context_id:'camera1',target_id:'target1',type:'line_of_sight',geometry_mode:'unknown'}],
 navigation_targets:[{id:'nav1',status:'needs_review',target_type:'other',lat:null,lon:null,evidence_refs:[]}],
 condition_contract:{contract_id:'c1',status:'draft',conditions:[{id:'condition1',role:'REQUIRED',domain:'ACCESS_SAFETY',metric:'safe_trail',notes_i18n:tr('安全','Safe','安全')}]},
 evidence_claims:[],readiness:{research_level:'R1',gaps:['GEOMETRY_GAP','RESEARCH_GAP']},
 provenance:{source_catalog:'worker2-offline-batch03',source_revision:'research-shard-batch03',imported_at:'2026-10-08T17:26:40Z',review_status:'reviewed'}
});
const fails=(x,code)=>assert.throws(()=>importV21Catalog(x),e=>e instanceof CatalogImportError&&e.code===code);
test('V2.1 research projection preserves unknown, provenance, 3 locales, and no runtime',()=>{
 const c=importV21Catalog(doc());assert.equal(c.opportunities.length,1);assert.equal(c.view_relations[0].distance,null);
 assert.equal(c.view_relations[0].azimuth,null);assert.equal(c.unknowns.length,2);assert.equal(c.evaluations.length,0);
 assert.equal(localized(c.opportunities[0],'name','ja'),'鳶嘴山の岩稜');
 assert.equal(c.opportunities[0].provenance.imported_at,'2026-10-08T17:26:40Z');
});
test('three Opportunity records preserve two distinct Place IDs',()=>{
 const a=doc(),b=doc(),c=doc();b.opportunity_id='tw-026-P01';b.place_id='tw-026';c.opportunity_id='tw-026-P02';c.place_id='tw-026';
 const catalog=importV21Catalog({schema_version:'2.1.0',opportunities:[a,b,c]});
 assert.equal(catalog.places.length,2);assert.equal(catalog.opportunities.length,3);assert.equal(catalog.evaluations.length,0);
});
test('invalid version, no data and missing translations fail closed',()=>{
 const a=doc();a.schema_version='2.2.0';fails(a,'SCHEMA_MISMATCH');
 fails({schema_version:'2.1.0',opportunities:[]},'NO_DATA');
 const b=doc();delete b.name_i18n.en;fails(b,'INVALID_SCHEMA');
});
test('Directions require separately evidenced arrival, no fabricated live result',()=>{
 assert.equal(navigationAction({status:'verified',lat:25,lon:121,target_type:'parking'}),null);
 assert.equal(navigationAction({status:'verified',lat:25,lon:121,target_type:'camera_zone_or_place_anchor',evidence_refs:['e1']}),null);
 assert.match(navigationAction({status:'verified',lat:25,lon:121,target_type:'parking',evidence_refs:['e1']}).url,/\/maps\/dir\//);
 assert.equal(runtimeEvaluation({kind:'runtime',contract_status:'ready',source:'unreviewed',generated_at:'2026-10-09T00:00:00Z',verdict:'favorable'}),null);
});
