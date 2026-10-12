import test from "node:test";
import assert from "node:assert/strict";
import {LOCALES,normalizeCatalog,placeId,opportunityId,localized,navigationAction,relationValue,runtimeEvaluation,safeUrl,geometryType} from "../model.mjs";
const fixture={places:[{spot_id:"tw-001",name_i18n:{"zh-TW":"測試地點",en:"Test place",ja:"テスト地点"},navigation_target:{status:"needs_review",lat:25,lon:121}}],opportunities:[{opportunity_id:"tw-001-P01",place_id:"tw-001"}],conditions:[{opportunity_id:"tw-001-P01",role:"REQUIRED",human_description:"僅繁中研究文字"}]};
test("supports all three locales and stable place/opportunity IDs",()=>{assert.deepEqual(LOCALES,["zh-TW","en","ja"]);const c=normalizeCatalog(fixture);assert.equal(placeId(c.places[0]),"tw-001");assert.equal(opportunityId(c.opportunities[0]),"tw-001-P01");});
test("does not silently fall back to Chinese for missing translations",()=>{const c=normalizeCatalog(fixture);assert.equal(localized(c.conditions[0],"human_description","en"),null);assert.equal(localized(c.places[0],"name","ja"),"テスト地点");});
test("does not invent camera-to-subject numbers",()=>{assert.equal(relationValue(null,"km"),null);assert.equal(relationValue(20,null),null);assert.equal(relationValue(20,"km"),"20 km");});
test("never routes to unverified or multiple access targets",()=>{assert.equal(navigationAction(fixture.places[0].navigation_target),null);assert.equal(navigationAction({status:"multiple_access_routes",lat:25,lon:121}),null);assert.equal(navigationAction({status:"verified",lat:999,lon:121}),null);assert.equal(navigationAction({status:"verified",lat:25,lon:121}),null);assert.match(navigationAction({status:"verified",lat:25,lon:121,target_type:"parking",evidence_refs:["e1"]}).url,/\/maps\/dir\/\?/);assert.equal(navigationAction({status:"provisional_camera_anchor",lat:25,lon:121}),null);});
test("provisional camera anchors without evidence cannot yield Directions or map links",()=>{
  for (const nav of [
    {status:"provisional_camera_anchor",lat:25,lon:121},
    {status:"provisional_camera_anchor",lat:25,lon:121,map_query:"Unverified camera point"},
    {status:"provisional_camera_anchor",lat:25,lon:121,evidence_refs:[]}
  ]) {
    const action=navigationAction(nav);
    assert.equal(action,null);
    assert.notEqual(action?.kind,"directions");
    assert.equal(action?.url?.includes("/maps/dir/")??false,false);
  }
});
test("never turns research scores into live forecasts",()=>{assert.equal(runtimeEvaluation({score:10}),null);assert.equal(runtimeEvaluation({kind:"runtime",contract_status:"ready",source:"engine"}),null);assert.equal(runtimeEvaluation({kind:"runtime",contract_status:"ready",source:"engine",generated_at:"2026-10-08T00:00:00Z"}),null);});
test("rejects unsafe evidence URLs and unsupported geometry types",()=>{assert.equal(safeUrl("javascript:alert(1)"),null);assert.equal(geometryType({geometry_type:"guess"}),null);assert.equal(geometryType({geometry_type:"water_surface"}),"water_surface");});
test("rejects empty and malformed V2 catalogs",()=>{assert.throws(()=>normalizeCatalog({places:[]}));assert.throws(()=>normalizeCatalog(null));});
