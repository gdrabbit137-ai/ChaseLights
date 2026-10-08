import {normalizeCatalog} from './model.mjs';
import {projectV21} from './v21-adapter.mjs';

// Defensive reader only. Worker 1's JSON Schema remains the sole canonical validator.
export const SUPPORTED_OPPORTUNITY_SCHEMA = '2.1.0';
export class CatalogImportError extends Error {
  constructor(code, details='') { super(code + (details ? ': ' + details : '')); this.name='CatalogImportError'; this.code=code; }
}
const isObject = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const hasThree = x => isObject(x) && ['zh-TW','en','ja'].every(k=>typeof x[k]==='string' && x[k].trim());
function assertOpportunity(doc) {
  if (!isObject(doc)) throw new CatalogImportError('INVALID_SCHEMA','opportunity is not an object');
  if (doc.schema_version !== SUPPORTED_OPPORTUNITY_SCHEMA) throw new CatalogImportError('SCHEMA_MISMATCH',String(doc.schema_version ?? 'missing'));
  const textKeys=['opportunity_id','place_id','lifecycle_status'];
  if (!textKeys.every(k=>typeof doc[k]==='string' && doc[k].trim()) || !Number.isInteger(doc.revision) || doc.revision<1 || !hasThree(doc.name_i18n)) throw new CatalogImportError('INVALID_SCHEMA','identity/revision/localization');
  if (!Array.isArray(doc.camera_contexts) || !doc.camera_contexts.length || !Array.isArray(doc.targets) || !doc.targets.length || !Array.isArray(doc.observation_relations) || !Array.isArray(doc.navigation_targets) || !Array.isArray(doc.evidence_claims)) throw new CatalogImportError('INVALID_SCHEMA','camera/target/relation/navigation/evidence');
  if (!isObject(doc.condition_contract) || !Array.isArray(doc.condition_contract.conditions) || !isObject(doc.readiness) || !Array.isArray(doc.readiness.gaps) || !isObject(doc.provenance)) throw new CatalogImportError('INVALID_SCHEMA','condition/readiness/provenance');
  for (const t of doc.targets) if (!hasThree(t.name_i18n)) throw new CatalogImportError('INVALID_SCHEMA','target localization');
  for (const c of doc.condition_contract.conditions) if (c.notes_i18n != null && !hasThree(c.notes_i18n)) throw new CatalogImportError('INVALID_SCHEMA','condition localization');
}
export function importV21Catalog(input) {
  if (!isObject(input) && !Array.isArray(input)) throw new CatalogImportError('INVALID_DOCUMENT');
  const source=isObject(input?.data) ? input.data : input;
  const docs=Array.isArray(source) ? source : Array.isArray(source.opportunities) ? source.opportunities : [source];
  if (!docs.length || docs.length===1 && docs[0]===source && !('schema_version' in source)) throw new CatalogImportError('NO_DATA');
  if (isObject(source) && source.schema_version != null && source.schema_version!==SUPPORTED_OPPORTUNITY_SCHEMA) throw new CatalogImportError('SCHEMA_MISMATCH',String(source.schema_version));
  for (const doc of docs) assertOpportunity(doc);
  const envelope=Array.isArray(source) ? {opportunities:docs} : Array.isArray(source.opportunities) ? source : {opportunities:docs};
  const projected=projectV21(envelope);
  if (!projected) throw new CatalogImportError('INVALID_SCHEMA','projection rejected');
  const result=normalizeCatalog(projected);
  result.generated_at=isObject(source) && typeof source.generated_at==='string' ? source.generated_at : null;
  result.metadata={...result.metadata,source_schema:SUPPORTED_OPPORTUNITY_SCHEMA,imported_opportunities:docs.length};
  result.evaluations=[]; // Fail closed pending Worker 3's authoritative evaluation contract.
  return result;
}
