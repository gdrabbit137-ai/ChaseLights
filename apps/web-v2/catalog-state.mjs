// Operational UI state only; this does not extend W1's canonical contract.
import {importV21Catalog, SUPPORTED_OPPORTUNITY_SCHEMA} from './catalog-loader.mjs';
import {placeId} from './model.mjs';

export function createCatalogState({fetchImpl = (...args) => fetch(...args),
  onChange = () => {}, now = () => new Date().toISOString()} = {}) {
  let state = {status:'loading', catalog:null, selected:null, source:null, loaded:null};
  let generation = 0, active = null, preferred = null;
  const publish = update => {state = {...state, ...update}; onChange(state);};
  const clear = status => publish({status, catalog:null, selected:null, source:null, loaded:null});
  function begin() {
    if (state.selected) preferred = state.selected;
    active?.controller.abort();
    const request = {id:++generation, controller:new AbortController(), promise:null};
    active = request;
    clear('loading');
    return request;
  }
  function accept(text, source) {
    if (!text.trim()) {clear('empty'); return;}
    const input = JSON.parse(text);
    const payload = input?.data ?? input;
    // Empty transport is an operational state, never a schema-valid document.
    if (payload?.schema_version != null && payload.schema_version !== SUPPORTED_OPPORTUNITY_SCHEMA) {
      clear('invalid'); return;
    }
    if (payload === null || Array.isArray(payload) && !payload.length ||
        payload && typeof payload === 'object' && !Array.isArray(payload) &&
        (Object.keys(payload).length === 0 || Array.isArray(payload.opportunities) && !payload.opportunities.length)) {
      clear('empty'); return;
    }
    const catalog = importV21Catalog(input);
    const selected = catalog.places.some(p => placeId(p) === preferred) ? preferred : placeId(catalog.places[0]);
    preferred = selected;
    publish({status:'ready', catalog, selected, source, loaded:now()});
  }
  function run(request, operation) {
    request.promise = (async () => {
      try {await operation(request);}
      catch (error) {
        if (request.id === generation) clear(error?.code === 'NETWORK_ERROR' ? 'error' : 'invalid');
      } finally {if (active === request) active = null;}
      return state;
    })();
    return request.promise;
  }
  function load() {
    if (active) return active.promise;
    const request = begin();
    return run(request, async () => {
      let response;
      try {response = await fetchImpl('./catalog.v2.json', {cache:'no-store', signal:request.controller.signal});}
      catch {throw {code:'NETWORK_ERROR'};}
      if (request.id !== generation) return;
      if (response.status === 404) {clear('unavailable'); return;}
      if (!response.ok) {clear('error'); return;}
      let text;
      try {text = await response.text();} catch {throw {code:'NETWORK_ERROR'};}
      if (request.id === generation) accept(text, 'catalog.v2.json');
    });
  }
  function importFile(file) {
    // Local imports supersede pending requests. Even a transport ignoring abort
    // cannot overwrite a newer import after it eventually resolves.
    const request = begin();
    return run(request, async () => {
      const text = await file.text();
      if (request.id === generation) accept(text, file.name);
    });
  }
  function select(id) {
    if (state.catalog?.places.some(p => placeId(p) === id)) {
      preferred = id; publish({selected:id});
    }
  }
  return {load, importFile, select, getState:() => state};
}
