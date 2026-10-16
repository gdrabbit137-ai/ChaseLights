// W2's source-pinned research index is classification data, never a forecast.
const locales = ['zh-TW', 'en', 'ja'];
const unique = rows => new Set(rows).size === rows.length;
const names = value => locales.every(locale => typeof value?.[locale] === 'string' && value[locale].trim());
const id = record => record?.spot_id || record?.place_id || record?.id;

export function validateBrowseIndex(index, catalog) {
  const fail = message => { throw new Error('INVALID_RESEARCH_INDEX: ' + message); };
  const place = index?.place_index, topic = index?.topic_index, status = index?.index_status;
  if (index?.source_commit_sha !== catalog?.metadata?.source_index_commit_sha ||
      index?.manifest?.index_revision !== catalog?.metadata?.source_index_revision ||
      place?.index_revision !== index.manifest.index_revision ||
      topic?.index_revision !== index.manifest.index_revision ||
      topic?.taxonomy_revision !== index.manifest.taxonomy_revision ||
      status?.index_revision !== index.manifest.index_revision ||
      status?.mode !== 'RESEARCH_ONLY' || status.forecast_available !== false ||
      status.selected_date_recommendation_eligible !== false ||
      status.evaluations?.length !== 0 || status.counts?.regions !== 0 ||
      status.counts?.verified_timezones !== 0 || status.counts?.guide_eligible !== 0)
    fail('revision or publication');
  if (!Array.isArray(place.places) || !Array.isArray(place.opportunities) ||
      !Array.isArray(topic.topics) || !Array.isArray(topic.opportunity_topics)) fail('missing rows');
  const placeIds = place.places.map(p => p.place_id);
  const opportunityIds = place.opportunities.map(o => o.opportunity_id);
  const topicIds = topic.topics.map(t => t.topic_id);
  if(status.counts.places!==placeIds.length || status.counts.opportunities!==opportunityIds.length ||
     status.counts.topic_ids!==topicIds.length || status.unclassified_opportunity_ids?.length!==0 ||
     topic.opportunity_topics.length!==opportunityIds.length ||
     status.counts.opportunity_topic_links!==topic.opportunity_topics.reduce((n,o)=>n+o.topic_ids.length,0)) fail('status counts');
  if (![placeIds, opportunityIds, topicIds].every(unique) ||
      !place.places.every(p => names(p.name_i18n) && p.admin_status === 'UNKNOWN' &&
        p.time_zone?.status === 'UNKNOWN' && p.time_zone.iana_id === null) ||
      !topic.topics.every(t => names(t.name_i18n) && t.status === 'ACTIVE')) fail('identity or unknown metadata');
  if (!unique(topic.opportunity_topics.map(o => o.opportunity_id)) ||
      !topic.opportunity_topics.every(o => opportunityIds.includes(o.opportunity_id) &&
        Array.isArray(o.topic_ids) && o.topic_ids.length && unique(o.topic_ids) &&
        o.topic_ids.every(t => topicIds.includes(t)))) fail('topic join');
  if (!unique(catalog.places.map(id)) || !unique(catalog.opportunities.map(o => o.opportunity_id)) ||
      catalog.places.length !== placeIds.length || catalog.opportunities.length !== opportunityIds.length ||
      !catalog.places.every(p => placeIds.includes(id(p))) ||
      !catalog.opportunities.every(o => opportunityIds.includes(o.opportunity_id))) fail('catalog join');
  for(const row of place.places){
    const item=catalog.places.find(p=>id(p)===row.place_id);
    if(!locales.every(locale=>item?.name_i18n?.[locale]===row.name_i18n[locale]))fail('place name source');
  }
  for (const binding of place.opportunities) {
    const doc = catalog.opportunities.find(o => o.opportunity_id === binding.opportunity_id);
    const pin = catalog.metadata.source_pins?.[binding.opportunity_id];
    if (binding.publication !== 'RESEARCH_ONLY' || binding.publication_approval_ref !== null ||
        doc?.place_id !== binding.place_id || !placeIds.includes(binding.place_id) ||
        !pin || ['source_commit_sha','source_path','source_blob_sha','revision'].some(k => pin[k] !== binding[k]))
      fail('canonical binding');
  }
  return index;
}

export function browse(index, catalog, {search = '', topicIds = [], locale = 'zh-TW'} = {}) {
  const q = search.trim().normalize('NFKC').toLocaleLowerCase();
  const chosen = new Set(topicIds);
  if ([...chosen].some(id => !index.topic_index.topics.some(t => t.topic_id === id))) throw new Error('INVALID_FILTER');
  const bindings = new Map(index.place_index.opportunities.map(o => [o.opportunity_id, o]));
  const tags = new Map(index.topic_index.opportunity_topics.map(o => [o.opportunity_id, o.topic_ids]));
  const visible = catalog.opportunities.filter(o => bindings.has(o.opportunity_id) &&
    (!chosen.size || tags.get(o.opportunity_id)?.some(t => chosen.has(t))));
  const grouped = new Map();
  for (const opportunity of visible) {
    const key = opportunity.place_id;
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(opportunity);
  }
  const places = index.place_index.places.filter(p => {
    if (!grouped.has(p.place_id)) return false;
    if (!q) return true;
    return [p.place_id, ...locales.map(l => p.name_i18n[l]),
      ...locales.flatMap(l => p.aliases_i18n?.[l] || [])]
      .some(s => String(s).normalize('NFKC').toLocaleLowerCase().includes(q));
  }).map(p => ({place:catalog.places.find(c => id(c) === p.place_id), opportunities:grouped.get(p.place_id)}));
  // The code-point order is deterministic across browser engines; IDs break name ties.
  places.sort((a,b) => {
    const x = a.place.name_i18n?.[locale]?.normalize('NFKC').toLocaleLowerCase() || '';
    const y = b.place.name_i18n?.[locale]?.normalize('NFKC').toLocaleLowerCase() || '';
    return (x < y ? -1 : x > y ? 1 : 0) || (id(a.place) < id(b.place) ? -1 : 1);
  });
  return places;
}
