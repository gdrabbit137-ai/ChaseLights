// Read-only projection of Worker 1's opportunity-v2.1.schema.json.
// The canonical documents remain unchanged; no weather or forecast is inferred.
const GAP_LABELS = {
 RESEARCH_GAP:["研究證據不足","Research evidence gap","調査根拠が不足"],
 GEOMETRY_GAP:["攝影幾何未確認","Geometry not verified","撮影幾何が未確認"],
 DATA_UNAVAILABLE:["資料尚未取得","Data unavailable","データ未取得"],
 MODEL_UNSUPPORTED:["模型尚未支援","Model not supported","モデル未対応"],
 DYNAMIC_UNVERIFIED:["動態主體未驗證","Dynamic subject unverified","動的被写体が未確認"],
 SOURCE_CONFLICT:["證據來源有衝突","Conflicting sources","資料間に矛盾"],
 LOW_CONFIDENCE:["證據信心較低","Low confidence","信頼度が低い"],
 STALE_DATA:["資料可能過期","Potentially stale data","データが古い可能性"]
};
const localeText = values => Object.fromEntries(["zh-TW","en","ja"].map((key,i)=>[key,values[i]]));
const isV21 = doc => doc && doc.schema_version === "2.1.0" && Array.isArray(doc.camera_contexts) && Array.isArray(doc.targets);
const scopedId = (doc,id) => doc.opportunity_id + "/" + id;
const list = value => Array.isArray(value) ? value : [];
export function projectV21(input) {
 const source = input?.data || input;
 const docs = isV21(source) ? [source] : list(source?.opportunities);
 if (!docs.length || !docs.every(isV21)) return null;
 const output = {metadata:{source_schema:"2.1.0",adapter:"read-only"},places:[],opportunities:[],camera_zones:[],subject_geometries:[],view_relations:[],condition_contracts:[],conditions:[],evidence:[],research_status:[],unknowns:[],evaluations:[]};
 const sourcePlaces = list(source?.places);
 const seen = new Set();
 for (const doc of docs) {
   if (!doc.opportunity_id || !doc.place_id || !doc.name_i18n || !["zh-TW","en","ja"].every(l=>typeof doc.name_i18n[l]==="string" && doc.name_i18n[l].trim())) throw new Error("Incomplete V2.1 identity/localization");
   if (!seen.has(doc.place_id)) {
     seen.add(doc.place_id);
     // The place ID is a transparent identifier, never a fabricated place name.
     output.places.push(sourcePlaces.find(p=>[p.spot_id,p.place_id,p.id].includes(doc.place_id)) || {spot_id:doc.place_id,name_i18n:localeText([doc.place_id,doc.place_id,doc.place_id])});
   }
   const cameraIds=list(doc.camera_contexts).map(c=>scopedId(doc,c.id));
   const targetIds=list(doc.targets).map(t=>scopedId(doc,t.id));
   output.opportunities.push({opportunity_id:doc.opportunity_id,place_id:doc.place_id,name_i18n:doc.name_i18n,description_i18n:doc.description_i18n,camera_zone_ids:cameraIds,subject_geometry_ids:targetIds,readiness:doc.readiness,lifecycle_status:doc.lifecycle_status,provenance:doc.provenance,condition_contract_id:doc.condition_contract?.contract_id});
   for (const c of list(doc.camera_contexts)) output.camera_zones.push({camera_zone_id:scopedId(doc,c.id),opportunity_id:doc.opportunity_id,name_i18n:localeText([c.id,c.id,c.id]),geometry_type:c.geometry?.kind,geometry_status:c.geometry?.status,verification_status:c.verification_status,access_notes_i18n:c.access_notes_i18n,safety_notes_i18n:c.safety_notes_i18n,evidence_refs:c.evidence_refs||[]});
   for (const t of list(doc.targets)) output.subject_geometries.push({subject_geometry_id:scopedId(doc,t.id),opportunity_id:doc.opportunity_id,name_i18n:t.name_i18n,geometry_type:t.geometry?.kind,geometry_status:t.geometry?.status,target_kind:t.kind,evidence_refs:t.evidence_refs||[]});
   for (const r of list(doc.observation_relations)) output.view_relations.push({view_relation_id:scopedId(doc,r.id),opportunity_id:doc.opportunity_id,camera_zone_id:scopedId(doc,r.camera_context_id),subject_geometry_id:scopedId(doc,r.target_id),distance:r.distance_m??null,distance_unit:"m",azimuth:r.azimuth_deg??null,azimuth_unit:"°",elevation_angle:r.elevation_deg??null,elevation_angle_unit:"°",geometry_mode:r.geometry_mode,relation_type:r.type,evidence_refs:r.evidence_refs||[]});
   const nav=list(doc.navigation_targets);
   // Multiple alternatives are not silently collapsed to one Directions target.
   if (nav.length===1) output.opportunities[output.opportunities.length-1].navigation_target=nav[0];
   else output.opportunities[output.opportunities.length-1].navigation_target={status:nav.length?"multiple_access_routes":"needs_review"};
   const contract=doc.condition_contract||{};
   output.condition_contracts.push({contract_id:contract.contract_id,opportunity_id:doc.opportunity_id,status:contract.status});
   for (const c of list(contract.conditions)) output.conditions.push({condition_id:scopedId(doc,c.id),opportunity_id:doc.opportunity_id,role:c.role,domain:c.domain,metric:c.metric,operator:c.operator??null,threshold:c.threshold??null,unit:c.unit??null,unknown_policy:c.unknown_policy,confidence:c.validation_status||"unvalidated",human_description_i18n:c.notes_i18n||null,evidence_refs:c.claim_refs||[]});
   // Claim classification is not a resolved publisher, source URL or authority.
   for (const claim of list(doc.evidence_claims)) output.evidence.push({evidence_id:scopedId(doc,claim.claim_id),opportunity_id:doc.opportunity_id,claim_type:claim.claim_type,audit_status:claim.audit_status,evidence_refs:claim.evidence_refs||[],source:null,source_status:"unresolved_reference"});
   output.research_status.push({opportunity_id:doc.opportunity_id,status:doc.lifecycle_status,readiness:doc.readiness,provenance:doc.provenance});
   for (const gap of list(doc.readiness?.gaps)) if (GAP_LABELS[gap]) output.unknowns.push({opportunity_id:doc.opportunity_id,text_i18n:localeText(GAP_LABELS[gap])});
 }
 return output;
}
