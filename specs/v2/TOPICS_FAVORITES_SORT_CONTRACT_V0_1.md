# U-W4-02C — Topics, favorites and sorting v0.1

Owner W1. Normative proposed contract. Schemas: [topic index](schema/topic-index-v0.1.schema.json), [local preferences](schema/local-preferences-v0.1.schema.json), [browse query](schema/browse-query-v0.1.schema.json), [sort capabilities](schema/sort-capabilities-v0.1.schema.json). These add no W4 UI, W2 Canonical records or runtime scores.

## Taxonomy and joins

`taxonomy_revision` identifies an immutable vocabulary. Each `topics[]` row has a stable opaque `topic_id`, equivalent nonblank `name_i18n` and `definition_i18n` in zh-TW/en/ja, `status=ACTIVE|DEPRECATED`, and nullable `replaced_by`. IDs are never derived at runtime from translated names and are never reused. Deprecated IDs persist for saved filters; replacement is explicit, acyclic and reviewed. Reject unknown IDs; do not guess a new tag. New semantic concepts require a new registry revision, not renaming an unrelated ID.

Initial vocabulary for W2 review (classification only, not claims that these subjects exist at any Place):

| Stable ID | zh-TW / en / ja name | Scope |
| --- | --- | --- |
| `topic:sunrise` | 日出 / Sunrise / 日の出 | Researched sunrise photography, not proof of visibility. |
| `topic:sunset` | 夕照 / Sunset light / 夕景 | Sunset light/composition; no automatic colorful-cloud inference. |
| `topic:colorful-clouds` | 彩霞 / Colorful clouds / 彩雲・朝焼けと夕焼けの雲 | Researched illuminated colored clouds; not any sunset or guaranteed weather. |
| `topic:reflection` | 倒影 / Reflections / 水面の映り込み | Evidenced reflective composition; geometry constraints remain independent. |
| `topic:mountain-landscape` | 山岳景觀 / Mountain landscape / 山岳風景 | Evidenced mountain scene; no inferred cloud sea, snow or access. |
| `topic:coastal-landscape` | 海岸景觀 / Coastal landscape / 海岸風景 | Evidenced coast scene; no inferred surf/tide/weather opportunity. |
| `topic:flowers` | 花卉 / Flowers / 花 | Evidenced floral subject; no inferred bloom presence or season. |
| `topic:cityscape` | 城市景觀 / Cityscape / 都市風景 | Evidenced urban scene; no inferred illumination schedule. |

W2 must supply reviewed three-language definitions and source-aligned assignments. The vocabulary is open to future astronomy/wildlife/etc.; eight existing Opportunity records do not imply eight categories or fixed model limits. No taxonomy assignment promotes existence, research readiness or forecastability.

`opportunity_topics[]` maps an existing eligible-for-research Opportunity ID to a nonempty set of topic IDs with nonempty `evidence_refs` supporting classification. Join through 02A's canonical binding to Place. One Opportunity may have many topics; a Place's topics are the union of the Opportunities eligible **on the requested surface**. Unclassified is an empty derived union, not a fabricated `other` subject; no topic filter may include it. W2 assigns topics from canonical content/evidence, never generic terrain/weather. Reject duplicate bindings, unresolved topics/Opportunities and taxonomy/index revision mismatch. Do not add subject tags or new fields to Opportunity v2.1 in this task.

## Filter and surface contract

The browse request carries immutable `index_revision` and `taxonomy_revision`, `locale`, `surface`, `region_ids`, `topic_ids`, `search`, `favorites_only`, `sort` and `direction`. Empty arrays mean no restriction; selections are unique stable IDs. Direction is explicit ASC or DESC. Initial product order is REGION ASC; explicit NAME/REGION selections default to ASC, SCORE to DESC and DISTANCE to ASC.

- `RESEARCH`: only explicitly opened research workspace/preview; RESEARCH_ONLY and GUIDE_ELIGIBLE may appear with clear research context, WITHHELD never appears.
- `GUIDE`: only GUIDE_ELIGIBLE Opportunities; describes durable subjects without selected-date implication.
- `RECOMMENDATIONS`: additionally requires independently validated current 02B/EvaluationResult and owned recommendation/presentation policy. A research record cannot fill this surface. A browse request/index alone yields no recommendation candidates.

OR within regions; OR within topics; AND between regions/topics/search/favorites. When topics are selected, retain only matching eligible Opportunities, then group/deduplicate Places; never show an unrelated Opportunity merely because another one at its Place matched. An unknown filter ID is INVALID_FILTER. Locale changes do not alter IDs, matching semantics or favorites. Empty matches remain EMPTY with clear filters action. Loading, invalid metadata and error are separate from a successful empty result. Search and incomplete metadata follow 02A.

## Local favorites and future expansion

Storage key: `chaselights.v2.preferences.v1` in same-origin `localStorage`, serialized UTF-8 JSON governed by local-preferences schema. `schema_version=0.1.0`, monotonic nonnegative `storage_revision`, `favorites[]`, `preferred_locale`, `updated_at_utc`. Favorites contain only `entity_type=PLACE|OPPORTUNITY`, stable `entity_id`, `added_at_utc`; uniqueness is `(entity_type,entity_id)`. Revisions/copies of canonical data, research approval, scores, timezone, precise user location, tokens and navigation are **not** stored in a favorite. A Place favorite covers all of its eligible Opportunities; an Opportunity favorite covers only that Opportunity and its containing Place in grouped results. If both are saved, show one Place card. Favoriting never grants publication or recommendation eligibility.

Add/remove is idempotent. Validate before write; write the complete new document atomically via `setItem`. A storage exception (blocked/quota/private browsing) keeps session memory usable and shows a localized notice that favorites will not persist. Never claim cloud sync. A malformed document is isolated from active state; do not silently overwrite it during startup, offer explicit reset. Unknown future `schema_version` is preserved untouched and read-only until an explicit supported migration; do not downgrade it. Missing key starts empty. Unknown/deleted/withheld entity IDs remain saved and removable as unavailable, are excluded from current matches, and must not be reattached by translated name. Retired IDs require a reviewed W2 migration map and user-visible migration policy.

Listen for storage events and re-read/validate the latest document before edits. v0.1 is a local single-document last-write-wins store; concurrent tab writes can lose an edit and are not a transactional sync service. Do not delete unknown entries when the current Catalog is smaller. Export/import or future accounts use a new versioned repository adapter preserving entity keys, explicit migrations, conflict/deletion semantics and opt-in privacy/authentication; no backend is implemented or implied here. Filters/sort are ephemeral in v0.1; persisting those later requires a reviewed schema version, not extra ad hoc keys.

## Sort capabilities and order

A separate sort-capabilities document is bound to `query_id` and `candidate_set_revision` (exact filtered set + locale + date/data revision). Each NAME/REGION/SCORE/DISTANCE entry has `enabled`, nullable `reason_code`, `explanation_i18n` and `comparison_key`. Enabled requires a real comparison key and null explanation/reason; disabled requires nonblank machine reason + all three explanation strings and null key. The capability is evidence of available inputs only after semantic checks; a supplied `enabled=true` is not self-authenticating.

NAME and REGION use eligible metadata and explicit missing-value fallbacks in research. NAME compares localized Place names using NFKC/casefold code-point order, then Place ID, avoiding browser-ICU-dependent order. REGION uses the lexicographically smallest `(country_code, admin1 ISO code)` among **matching selected memberships** (all memberships when none selected), then normalized localized name and Place ID. Thus cross-region Places are stable and not duplicated. Unknown name/region sorts last in either direction in explicit research, using Place ID as fallback; no guessed administrative rank. Reverse the primary sort for DESC, retain missing-last and ascending Place ID tie-breaks.

SCORE requires all displayed candidate Opportunities to have authentic, fresh, selected-date-matched and comparable scores from the owning calibrated scoring/recommendation policy. `comparison_key` identifies that policy/scale/version and scope. Do not compare arbitrary model scales, R-levels, raw weather, solar WINDOW or missing scores. Grouped Place value is the maximum valid score of its currently matching eligible Opportunities, only when every matching Opportunity is comparable. If any is missing/incomparable, disable the whole SCORE control (`NO_COMPARABLE_SCORE`) and explain; do not use zero or a hidden global threshold.

DISTANCE requires user permission for a fresh location (or explicitly selected sourced origin), a documented verified Place representative distance reference (never substitute a subject/arrival/camera point silently), uncertainty fit for the distance claim, same origin and method, and finite nonnegative distances for all candidates. `comparison_key` identifies origin snapshot + method + target-role/version. Distance is straight-line representative proximity in v0.1, never route length/travel time or proof of safe access. Missing/denied/stale/approximate-unfit location, unknown target or inconsistent method disables the whole control (`NO_TRUSTED_DISTANCE`). Request geolocation only after an explicit user action selecting distance; never on initial render or merely to populate capabilities. Denial returns to REGION ASC with a concise localized explanation. Keep Places with unknown distance in the candidate set; missing distance disables the distance order rather than dropping those Places. No exact user origin is persisted in favorites.

If active SCORE/DISTANCE becomes unavailable on date/filter/revision change, return UNSUPPORTED_SORT with reason, show REGION ASC as an explicitly communicated fallback and update the selected control; never label fallback region order as score/distance order. NAME/REGION require no paid service. Capability, sorting, favorites and publication do not change photographic verdicts or independent closure/navigation warnings.

## Acceptance

W1 tests validate registry/joins, multilingual strings, unknown/duplicate IDs, active/deprecated replacement, favorites type/uniqueness/unknown retention, strict versions, disabled explanations, multi-topic/region OR+AND truth tables, grouping and research isolation. W4/W5 must add actual localStorage quota/corruption/future-version/cross-tab/add-remove tests, locale/keyboard/mobile states, stable/missing-last/tie orders, unavailable score/distance explanations and selection fallback, same-Place two-Opportunity filtering, and no research/withheld content in primary recommendations. Genuine score/distance enabling requires W3/W2 provenance and human approval; synthetic fixtures cannot enable live controls.
