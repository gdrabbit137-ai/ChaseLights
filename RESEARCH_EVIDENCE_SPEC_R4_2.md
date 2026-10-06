# ChaseLights Research Evidence Specification R4.2

## 1. Core rule

Photography Opportunity existence is a **research claim about a Place**.

An Opportunity MAY be added to the production catalog only when there is Place-specific evidence that the subject, scene, event, or composition actually exists at that Place and is photographically meaningful.

Weather, terrain, elevation, hydrology, vegetation type, Scene tags, Theme tags, or generic destination categories may help discover a research lead or predict **when an already verified Opportunity may work**. They MUST NOT, by themselves, create or prove an Opportunity, except for the narrowly defined forecast-derived **sea-of-clouds environmental condition** in Section 4.1.

In short:

`Place-specific evidence proves WHAT can be photographed.`

`Forecast/runtime data estimates WHEN that verified subject may work.`

The two layers MUST NOT be reversed.

## 2. Evidence scope

Evidence must match the scope of the claim.

Examples:

- A lake being humid does not prove it has a worthwhile morning-mist photography Opportunity.
- A mountain being high does not prove a sea-of-clouds Opportunity.
- A west-facing coast does not prove a famous or usable sunset composition.
- Calm wind does not prove a reflection composition exists; the foreground/background geometry must be researched.
- Dark sky does not prove a Milky Way composition; access, horizon, orientation and subject geometry must be researched.
- Seasonal climate does not prove flowers, foliage, fireflies, birds or other subjects are present.
- Rainfall does not prove a waterfall is photographically usable from a legal Camera Zone.
- Broken cloud does not prove crepuscular rays are a repeatable Place-specific subject.

## 3. Evidence grades

### Grade A — authoritative Place-specific evidence
Examples:
- official scenic-area / park / forestry / municipality / tourism material,
- official trail, facility, event or habitat documentation,
- official image/caption explicitly showing or describing the subject at the Place,
- primary operator information for a recurring event or managed seasonal subject.

Grade A can establish Opportunity existence when the evidence actually supports the photographic claim.

### Grade B — reliable Place-specific observational evidence
Examples:
- established photography publication,
- reputable hiking/outdoor publication with identifiable Place-specific imagery or description,
- multiple independent dated photographs / field reports that consistently demonstrate the subject.

Grade B may establish Opportunity existence when the claim is concrete and independently reviewable. Prefer corroboration for rare or highly variable phenomena.

### Grade C — discovery-only evidence
Examples:
- generic travel blogs,
- social posts,
- unsourced photo captions,
- search snippets,
- map reviews,
- AI-generated summaries.

Grade C may create a research lead but MUST NOT alone promote an Opportunity to production.

## 4. High-risk subject rule

The following subjects require explicit Place-specific evidence and MUST NOT be inferred from terrain/weather alone:

- fog / mist / morning mist / haze as a photographic subject,
- crepuscular rays / sunbeams / cloud-gap light,
- reflection compositions,
- Milky Way / star-field compositions,
- seasonal flowers and foliage,
- waterfalls where flow/visibility/access is part of the photographic claim,
- wildlife / birds / fireflies or other biological presence,
- recurring festivals, illuminations and events,
- snow/ice-specific compositions.

### 4.1 Sea-of-clouds derived-condition exception

"Sea of clouds" is treated differently from ordinary fog/mist. It MAY be surfaced as a **forecast-derived environmental condition** without prior photographic evidence, but only when the Opportunity is explicitly configured for spatial/vertical weather evaluation rather than inferred from a Scene/Theme tag or one weather point.

Minimum requirements:
- a known Camera Zone coordinate,
- a spatial-weather profile with multiple surrounding/target samples,
- materially lower terrain relative to the camera (current production minimum: at least 250 m),
- at least two lower-terrain samples required to show coherent low-cloud/fog evidence,
- the camera level remains sufficiently clear,
- a camera-in-cloud veto using visibility plus local saturation context; when temperature/dew point are available, a planning-grade dew-point-spread/LCL proxy is used to reject a viewpoint brushing orographic cloud,
- precipitation and local whiteout remain blockers.

A single-point combination such as high humidity + low cloud, or elevation alone, MUST NOT create a cloud-sea condition. Near-sea-level locations without materially lower terrain MUST NOT qualify merely because marine fog or stratus is forecast.

This exception predicts only the environmental state **"cloud layer below the camera while the camera remains clear."** It does not prove a specific foreground composition, exact target zone, scenic quality, legal access, or safety. Those claims still require Place/Camera-Zone evidence when asserted.

The evidence audit records this exception explicitly as `derived_condition`; it must not be mislabeled as Place-specific photographic evidence.

A high-risk Opportunity should record enough provenance to answer:
1. What evidence proves this subject exists here?
2. What geographic scope does that evidence support?
3. What part of the claim is forecastable?
4. What remains unforecastable or uncertain?

## 5. Camera Zone and evidence

Evidence for the subject does not automatically verify a Camera Zone.

A Camera Zone must be supported by location-specific evidence or explicitly marked representative/provisional.

Do not convert:
- an attraction center coordinate,
- a weather sampling coordinate,
- a map search result,
- a road point,
into an exact tripod point without separate evidence.

Navigation Target remains governed by `NAVIGATION_SPEC_R4_2.md` and is separate from Camera Zone evidence.

## 6. Runtime contract

Runtime modules evaluate an already-researched Opportunity.

They MAY:
- test visibility,
- wind,
- cloud layers,
- cloud base,
- precipitation,
- time window,
- sun/moon geometry,
- access state,
- tide/marine state,
- verified seasonal/event dates.

They MUST NOT:
- create a new subject because weather looks favorable,
- claim subject presence when presence is not forecastable,
- upgrade a generic Scene/Theme tag into a researched Opportunity,
- present terrain suitability as proof that a photographic phenomenon occurs there.

When subject presence is not forecastable, the model must expose that uncertainty and cap/qualify the recommendation as defined by the Opportunity contract.

## 7. Visible-copy rule

User-facing reasons must distinguish:
- observed/provider weather facts,
- runtime inference,
- researched Place facts,
- unknown subject presence.

Do not say a scene is present merely because its meteorological prerequisites are present.

Example:
- Allowed: "Low visibility and high humidity match the researched morning-mist window."
- Not allowed: "Morning mist is present" unless an observation source confirms it.

## 7.1 Independent evidence dimensions and user-facing status

A Photography Opportunity has multiple evidence dimensions. They MUST remain semantically independent:

1. **Opportunity existence** — whether Place-specific evidence establishes that the subject / scene / composition can actually be photographed at this Place.
2. **Seasonality** — whether evidence establishes a recurring best or applicable season.
3. **Formation / environmental conditions** — whether the conditions that produce the subject are known and evidence-supported.
4. **Forecastability / runtime readiness** — whether ChaseLights currently has sufficient provider data and executable logic to predict those conditions.
5. **Scoring calibration** — whether thresholds, weights and score interpretation are sufficiently validated.

A verified value in one dimension MUST NOT be downgraded or contradicted merely because another dimension is unknown, provisional, pending research, or not forecastable. In particular, unknown/provisional seasonality, formation conditions, forecastability, runtime readiness, or scoring parameters MUST NOT turn a separately verified Opportunity-existence claim into an unverified claim.

Conversely, a verified Opportunity-existence claim MUST NOT be used to invent a best season, formation rule, forecast capability, or calibrated score. Unknown remains unknown at the owning dimension.

Canonical data, evidence registries, runtime adapters, generated output and UI copy MUST preserve this separation. Generic labels such as `待氣候驗證` / "climate verification pending" MUST NOT be used where they make it ambiguous whether the Opportunity itself is unverified. When an unresolved dimension is intentionally exposed to the user, the copy SHOULD identify that dimension explicitly, for example `最佳季節尚無足夠證據`, `形成條件研究中`, or `目前無可靠預報能力`. However, unresolved research/system state that is not needed for the user's current photography decision SHOULD remain in canonical/evidence data and MUST NOT be surfaced merely because the field exists. Section 7.2 governs presentation eligibility.

When the evidence registry says Opportunity existence is `verified`, CI/audit SHOULD reject canonical or derived user-facing status that semantically represents that same Opportunity as existence-unverified solely because seasonality, formation, forecastability, runtime readiness, or scoring is incomplete. Fix the conflict at the owning source-of-truth layer rather than hiding it in the UI.


## 7.2 Decision-focused presentation and retained hidden data

### Core principle: database completeness is not UI completeness

ChaseLights stores a complete, auditable photography knowledge model, but the normal user interface is a **decision view**, not a serialization of that model.

Information MAY and often SHOULD remain in the canonical catalog, evidence registry, runtime diagnostics, or generated detail data without being shown in the default photographer UI.

The presentation rule is:

`Store what the system needs to know; show what the photographer needs to decide.`

A field MUST NOT become user-facing merely because it exists in the database. Conversely, hiding a field from the normal UI MUST NOT delete, weaken, overwrite, or reclassify the underlying evidence or runtime state.

UI visibility is therefore a product/presentation policy independent from:
- evidence classification,
- research completeness,
- runtime readiness,
- score calibration,
- provenance retention,
- auditability.

A downstream UI MUST NOT repair an evidence conflict by hiding it, but it also MUST NOT expose internal research state when that state does not help the user make the current photography decision.

### Durable Opportunity vs selected-date recommendation

The system MUST distinguish:

1. **Photography Opportunity** — a durable, researched statement about what can be photographed at a Place.
2. **Opportunity evaluation** — the runtime result for a selected date/time, including applicable window, score/status, confidence, blockers and decision reasons.
3. **User-facing recommendation** — a decision-focused projection of a sufficiently supported evaluation.

These are not interchangeable.

A verified Photography Opportunity MAY remain in the database even when seasonality, formation conditions, forecastability, runtime readiness, or scoring calibration is incomplete. Such incompleteness does not invalidate Opportunity existence.

However, a verified Opportunity that cannot be meaningfully evaluated for the selected date MUST NOT be displayed as a peer of actionable selected-date recommendations merely to fill the UI.

If product design offers a separate, user-initiated **"what can be photographed here" / Place photography guide** view, a verified Opportunity MAY appear there with conservative copy that does not imply selected-date viability. Research-only candidates whose Opportunity existence is not verified MUST NOT appear in the normal photographer-facing guide or recommendation UI.

### Default primary recommendation content

For the selected date, the default Place detail UI SHOULD prioritize only information that directly answers the photographer's next decision:

1. what photographic subject/composition is worth considering;
2. whether it is viable for the selected date;
3. the best actionable local-time window;
4. whether the recommended shooting period is upcoming, active now, or has already passed when the selected date is today;
5. the score or qualitative status, only when the scoring interpretation is valid for that Opportunity;
6. the Camera Zone / shooting location when sufficiently supported;
7. a short photographer-facing explanation of the decisive conditions.

Optional second-level content MAY include composition guidance, shooting direction, focal-length guidance, or concise explanations of why the conditions are favorable.

The primary UI SHOULD NOT repeat equivalent signals such as the same numeric score in multiple places or a score plus multiple prose labels that communicate the same conclusion.

### Research/system information is hidden by default

The following information SHOULD remain hidden from the default photographer decision surface unless the user deliberately opens an advanced/technical view or the information materially changes the decision:

- evidence grade and source-provenance bookkeeping;
- source URLs and audit references;
- unresolved internal research dimensions;
- rule IDs, formula versions, thresholds and weights;
- provider/model diagnostics and fallback internals;
- machine confidence components;
- calibration/debug state;
- internal field names and enum/status values;
- "pending research" labels whose only purpose is to describe database completeness.

In particular, labels such as `最佳季節待證據`, `形成條件研究中`, `待氣候驗證`, or `目前無可靠預報能力` MUST NOT automatically occupy primary recommendation-card space simply because those states are stored.

If one of those limitations materially affects what the user can safely infer from a visible recommendation, surface a concise photographer-facing consequence instead of exposing raw internal state. For example, prefer "今天無法可靠判斷最佳時段" over a database-status label when that is the actual user impact.

### No-fill rule

The UI MUST NOT backfill the primary recommendation area with immature, unevaluable, low-evidence, or research-only Opportunities merely to avoid an empty screen.

If no Opportunity meets the selected-date presentation gate, show a clear empty state such as:

- no qualified high-quality shooting window for the selected date; or
- no currently evaluable verified Opportunity.

The empty state MAY offer an explicit action to browse the Place's verified photography subjects, but those subjects must remain visually and semantically separate from selected-date recommendations.

### Time-awareness rule

When the selected date is today, the UI MUST interpret the recommended shooting period relative to the current Place-local time.

The internal/runtime concept may continue to use a `window` field, but ordinary photographer-facing copy SHOULD use natural photography language such as `最佳拍攝時段`, `建議拍攝時段`, or their localized equivalents. Raw terms such as `窗口已結束` SHOULD NOT be shown in the normal UI.

Preferred selected-date wording is:
- before the period: `最佳拍攝時段尚未開始` or, when useful, a concise countdown;
- during the period: `現在正值最佳拍攝時段`;
- after the period: `今日最佳拍攝時段已過`.

A high score for a shooting period that has already passed MUST NOT be presented in a way that implies the user should still depart now. The temporal state of the recommended shooting period is more decision-relevant than repeating the score.

Avoid blame-oriented copy such as `你已錯過` unless the product intentionally adopts that tone. The UI should describe the state of the photography opportunity, not judge the user's action.

Historical or future selected dates do not require a real-time "now" state, but their Place-local shooting period must remain explicit.

### Progressive disclosure rule

The normal explanation path SHOULD be:

`Recommendation -> Why this is suitable -> Photographer guidance -> Advanced technical details`

The first explanation layer should use photographer-facing reasons such as sun geometry, cloud structure, visibility, wind, precipitation, tide or access state.

Raw thresholds, formula internals, evidence provenance, and diagnostic/provider details belong to an advanced/debug/admin layer unless they are necessary to avoid misleading the user.

A control named like "查看完整判定條件" / "view full evaluation criteria" SHOULD NOT be the primary explanation affordance for ordinary users. Prefer a photographer-facing question such as "為什麼適合？" / "Why is this suitable?" and place technical detail behind a deeper disclosure when retained.

### Presentation-gate requirements

A selected-date Opportunity may enter the primary recommendation surface only when all applicable conditions are satisfied:

- Opportunity existence is verified or admitted under an explicit specification exception such as Section 4.1;
- the UI can represent the selected-date evaluation without inventing unknown dimensions;
- any shown score/status is valid under the Opportunity's runtime/scoring contract;
- any shown best window is supported by the runtime data actually available;
- uncertainty that materially changes the user's interpretation is communicated in photographer-facing terms;
- the card is not being shown solely because the Opportunity exists in the database.

The exact gate MAY vary by Opportunity type. The implementation SHOULD derive presentation eligibility from canonical evidence/runtime state rather than maintain an unrelated manual UI-only truth that can drift from the source data.

### Selected-date semantic consistency

A selected-date evaluation MUST preserve the distinction between a prerequisite/dimension match and the overall Opportunity verdict. Temporal eligibility, season eligibility, access eligibility, astronomy geometry, or any other single prerequisite becoming true MUST NOT, by itself, produce an overall photographer-facing `suitable`, `match`, `key conditions met`, or equivalent positive verdict.

The overall selected-date verdict and recommendation eligibility MUST reflect the complete applicable runtime contract for that Opportunity, including required conditions, decisive blockers, applicable adverse conditions/penalties, score interpretation, confidence, and temporal state. A favorable prerequisite MAY be shown as a supporting reason, but it MUST NOT semantically override decisive adverse conditions.

Numeric score, qualitative status/verdict, recommendation eligibility, and photographer-facing explanation MUST NOT materially contradict one another. In particular, when decisive adverse conditions make the researched subject unlikely or unsuitable under the owning runtime/scoring contract, runtime output MUST NOT simultaneously characterize the Opportunity as an overall positive match merely because its shooting time, season, sun geometry, or another prerequisite is valid.

The presentation layer MUST NOT repair contradictory runtime truth by inventing a UI-only score threshold or reclassifying canonical runtime state. If runtime output contains a materially contradictory combination (for example, a strongly adverse/low evaluation together with an overall positive-match status), the normal recommendation surface MUST fail conservatively: do not present it as an actionable positive recommendation, use photographer-facing uncertainty/unfavorable copy where the existing structured state safely supports it, and hand the root-cause correction to the owning runtime/scoring layer.

A `best_time` / `window` value identifies the best or applicable time within the evaluated Opportunity contract; its existence alone does not prove that the selected date is worth a trip. The normal UI MUST use `最佳拍攝時段` / “best shooting time” / equivalent positive recommendation wording only when the Opportunity passes the selected-date recommendation/presentation gate. When an otherwise evaluable but unfavorable selected date retains a meaningful relative time, the product MAY expose it using explicitly non-recommendation wording such as `今日相對較佳時段` / “relatively better time today”, provided this cannot be mistaken for an actionable positive recommendation. If that distinction cannot be represented safely, the time SHOULD be omitted from the primary recommendation surface.

### Recommendation-policy ownership and score semantics

The selected-date recommendation decision is an owned domain policy, not a presentation convenience and not an adapter fallback.

The architecture MUST preserve these responsibilities:

1. **Opportunity evaluation / scoring contract** owns the evaluated facts for the Opportunity, including score components, required conditions, decisive blockers, confidence, temporal state, and any calibrated interpretation of those values.
2. **Recommendation policy** consumes that complete evaluation and produces a structured overall decision such as `recommended`, `candidate/conditional`, `not_recommended`, or `unavailable/unknown`, together with machine-readable decisive reason/blocker codes where applicable.
3. **Adapters / generated-data transport** MAY serialize and carry that decision but MUST NOT invent a new global score band, threshold, or semantic reclassification merely because downstream UI needs a verdict.
4. **Presentation/UI** translates the structured decision and reasons into photographer-facing localized copy. It MUST NOT infer recommendation state from a numeric score when the owning evaluation/recommendation contract has not already defined that interpretation.

A numeric score is therefore diagnostic/evaluative data, not universal permission to recommend. A repository-wide constant such as “score >= X means recommended” or “score >= Y means candidate” MUST NOT be introduced unless the owning scoring/recommendation specification explicitly establishes that calibration and its scope. Opportunity-specific calibrated thresholds MAY exist when supported by the owning contract; they MUST NOT silently become global policy.

**Decisive blockers have semantic precedence over aggregate score.** When an applicable required condition or hard blocker makes the researched subject non-viable, an otherwise high aggregate score MUST NOT promote the evaluation to an actionable positive recommendation. Conversely, absence of a calibrated numeric threshold MUST NOT be repaired by inventing one downstream. Unknown or uncalibrated interpretation remains unknown/unavailable until the owning domain defines it.

The structured recommendation result SHOULD be stable enough that adapters and presentation do not need to reconstruct policy from status strings. At minimum, where the runtime exposes a recommendation decision, it SHOULD preserve:
- overall recommendation state;
- recommendation eligibility/actionability;
- decisive blocker/reason codes;
- confidence/uncertainty needed to interpret the decision;
- temporal applicability.

This ownership rule does not require every Opportunity type to use identical thresholds or identical scoring formulas. It requires the semantic decision to be made by the domain contract that owns those formulas and constraints, rather than by transport or UI code.

#### Required semantic-consistency regressions

Automated runtime/presentation regression coverage MUST include cases where a temporal prerequisite is valid but decisive environmental conditions fail. At minimum, tests MUST demonstrate that:

- valid sunset/twilight geometry does not by itself yield an overall suitable/match verdict when decisive visibility/cloud conditions fail for the subject;
- a low/adverse overall evaluation is not paired with photographer-facing `關鍵條件符合`, “key conditions met”, or equivalent positive copy;
- a retained relative time on an unfavorable day is not labeled as an unqualified `最佳拍攝時段` / “best shooting time”;
- the UI does not introduce an arbitrary numeric threshold to conceal a contradictory runtime status;
- the same semantic conclusion is preserved across all supported locales.

A concrete replay fixture such as Datunshan Navigation Station / `tw-001-P01` on 2026-10-05 (sunset timing valid while visibility and low-cloud conditions are strongly adverse) MAY be retained as a regression fixture. The fixture is evidence of the failure mode, not a special-case product rule: implementation MUST generalize through the Opportunity runtime/scoring contract rather than hard-code that Place, date, or score.

### Data-retention rule

Suppressing a field or Opportunity from the default UI does not authorize deletion.

Research notes, unresolved dimensions, provenance, calibration state, derived diagnostics, and other non-visible fields SHOULD remain available to:
- audits,
- regression tests,
- future model improvements,
- admin/research tooling,
- replay of older/newer scoring versions,
- later promotion when evidence/runtime readiness improves.

"Not displayed" is therefore not a synonym for "not stored", "false", "rejected", or "unverified".

### UI regression requirements

Automated browser/contract tests SHOULD cover at least:

- primary recommendation cards do not expose raw internal research-status labels by default;
- a verified but selected-date-unevaluable Opportunity is not rendered as a peer actionable recommendation;
- an unverified research candidate is not rendered in normal photographer-facing recommendation/guide surfaces;
- no qualified recommendation produces an explicit empty state rather than immature-card backfill;
- a today's recommended shooting period that has already passed is shown with natural photographer-facing copy (for example `今日最佳拍攝時段已過`) and does not imply a current departure recommendation;
- score/status is not redundantly repeated without additional decision value;
- "Why is this suitable?" exposes concise photographer-facing reasons while technical criteria remain progressively disclosed;
- hiding fields from the UI does not remove them from canonical/evidence/runtime data.


## 7.3 Supported-locale semantic parity

The production presentation layer currently supports `zh-TW`, `en`, and `ja`. For any researched Place / Photography Opportunity semantic content admitted to a normal user-facing surface, every supported locale MUST express the same underlying photographic fact and decision meaning. Translation MAY be idiomatic and culturally natural, but it MUST NOT omit or materially weaken decision-relevant content that is present in another supported locale, including the researched subject/composition, timing, seasonality, required conditions, favorable conditions, adverse conditions/risks, Camera Zone or viewpoint guidance, or another user-facing fact used to decide what/when/where to photograph.

Localized strings are presentation projections of canonical researched truth. They MUST NOT create new photographic claims, strengthen evidence, change Opportunity identity, alter Camera Zone / Photo Target / Navigation Target semantics, or substitute translated prose for stable IDs and structured canonical fields.

A catalog change that adds or changes user-facing semantic content MUST update the corresponding locale map for every supported locale in the same change. This applies at minimum, when the source field exists and is presented to photographers, to:

- Photography Opportunity name / researched subject;
- best time;
- best season;
- Condition Variant name;
- required conditions;
- boosters / favorable conditions;
- penalties / adverse conditions;
- displayed viewpoint / Camera Zone name;
- any future equivalent semantic field that becomes part of the production photographer-facing decision surface.

The existing proper-name/original-language fallback exception remains limited to names for which that fallback is explicitly allowed. A generic theme label such as `sunset`, `Milky Way`, `reflection`, or `mountain view` MUST NOT be presented as a semantic substitute for a missing translation of a researched Opportunity name. Avoiding mixed-language leakage is necessary but not sufficient: suppressing researched detail or replacing it with a generic category does not satisfy semantic parity.

Generated/runtime presentation payloads MUST preserve supported-locale maps from the canonical catalog using stable IDs. UI code MUST select the requested locale from those maps and MUST NOT treat translated display text as canonical identity or research truth.

### 7.3.1 Existing localization debt and same-change gate

The catalog state that predates this policy may contain missing locale maps. That state is migration debt, not a permanent exception. A frozen baseline MAY be used only to permit incremental backfill without blocking unrelated work, under all of these constraints:

- the baseline MUST NOT grow;
- a new Place/Opportunity semantic field MUST NOT enter the baseline debt;
- if the canonical source text of a baselined deficient field changes, that same change MUST complete all supported locales for that field;
- an already present locale value MUST NOT be removed or blanked;
- backfill MUST monotonically reduce the debt and MUST reach zero before the migration item is closed;
- once the debt reaches zero, the temporary baseline MUST be removed or the audit switched to strict zero-debt enforcement.

This migration rule does not authorize semantic shortcuts. Existing English/Japanese generic-theme fallback and hidden researched content remain implementation debt to be corrected by the owning data/UI workstreams.

### 7.3.2 Machine enforcement and semantic review

CI/static audit MUST cover the machine-checkable portion of this contract. At minimum it MUST:

- require non-empty values for every supported locale on newly added user-facing semantic fields;
- reject a change to canonical user-facing source text when that field still lacks one or more supported locales;
- reject a supported locale regressing from present to missing;
- verify that generated regional runtime output preserves locale maps from canonical data;
- expose the remaining historical debt count so migration progress is auditable.

Machine checks can establish presence, non-regression, and propagation. They cannot prove that translations are semantically equivalent. Backfill and later edits therefore still require human/AI content review against the canonical researched meaning; CI green MUST NOT be treated as proof of translation quality. Proper names may follow the explicit local/original-name fallback rule, but researched decision content remains subject to this semantic-equivalence review.


## 8. Admission checklist

Before adding a new Opportunity:

- [ ] Place-specific evidence found.
- [ ] Evidence grade recorded.
- [ ] Claim scope matches evidence scope.
- [ ] Camera Zone evidence reviewed separately.
- [ ] Forecastable vs non-forecastable parts identified.
- [ ] Required conditions / boosters / penalties are not being used as proof of subject existence.
- [ ] High-risk subject has explicit provenance.
- [ ] UI copy does not overstate uncertain presence.
- [ ] Tests cover the evidence/runtime boundary.
- [ ] Primary UI projection exposes only decision-relevant information by default.
- [ ] Research/system-only fields remain retained and auditable even when hidden from the default UI.
- [ ] Verified-but-unevaluable Opportunities are not presented as actionable selected-date recommendations.
- [ ] Empty recommendation states do not backfill with immature or research-only Opportunities.

## 9. Audit policy

Existing production Opportunities are grandfathered for operation, not automatically certified under this specification.

The evidence audit classifies them into:
- `documented`: explicit Place-specific evidence metadata/reference is present,
- `review_required`: a high-risk subject exists but explicit evidence provenance is not machine-verifiable in the current runtime catalog,
- `lower_risk_legacy`: no high-risk semantic trigger; still subject to normal research requirements.

`review_required` is a research queue, not an assertion that the Opportunity is false.

## 10. Origin

This specification formalizes the existing B29 principles:
- every active Place requires Place-specific photography research,
- curated Opportunity data must not be synthesized from legacy Scene/Theme labels,
- visible scene claims such as forest mist / reflection require Place research plus corresponding model/data support.

B35 made the same boundary explicit for Liyu Lake morning mist. R4.2 now applies it project-wide.
## 11. Production admission gate

As of B41, the initial high-risk backlog has been fully classified and the evidence audit is an enforced CI admission gate.

For every pull request to `main` and relevant push to `main`:

- the audit runs with `--enforce`,
- any high-risk Opportunity left as `review_required` fails CI,
- `verified`, `narrow_scope`, `insufficient_evidence`, and `remove_or_rewrite` are explicit research outcomes and do not fail merely because they are conservative,
- a new high-risk Opportunity must therefore include Place-specific provenance or an explicit conservative classification before merge.

The gate protects the evidence boundary; it does not require promotion to `verified`.

## 12. Repository file ownership and source-of-truth classification

The repository MUST distinguish **authoritative product data**, **research evidence**, **runtime logic**, **Place/navigation metadata**, **generated forecast output**, and **historical handoff/migration material**. A file in one class MUST NOT silently become the source of truth for another class.

### 12.1 Canonical Photography Opportunity catalog

`runtime_catalog_v004_r4_2.json` is the canonical, human-readable production catalog for all active researched Places and Photography Opportunities.

It owns:
- Place-level Opportunity membership,
- `opportunity_id`, names and compatibility theme,
- `best_time` and `best_season`,
- `condition_variants`,
- `hard_gates`,
- `required_conditions`,
- `boosters`,
- `penalties`,
- curated `viewpoints` / Camera Zones,
- formula/runtime status metadata.

After canonical-catalog cutover, production code MUST read this file rather than reconstructing the catalog from batch fragments.

The following files are legacy migration inputs / historical batch artifacts and are NOT independent production sources of truth after cutover:
- `runtime_catalog_v004_r4_2_b15.compact.part1.b64` through `part5.b64`,
- `runtime_catalog_v004_r4_2_b28_additions.json`,
- `runtime_catalog_v004_r4_2_b32_jp_batch01.json`,
- `runtime_catalog_v004_r4_2_b33_hualien_additions.json`,
- `runtime_catalog_v004_r4_2_b34_liushishishan_additions.json`,
- `runtime_catalog_v004_r4_2_b35_liyu_subjects.json`.

New Opportunity work MUST update the canonical catalog. A later batch file may be used as a temporary review artifact, but it must be folded into the canonical catalog before the change is considered complete.

### 12.2 Research evidence registry

`runtime_evidence_registry_r4_2.json` is the source of truth for **why a high-risk or audited photographic subject is admitted, narrowed, held, or rejected**.

It owns:
- evidence status,
- evidence scope,
- source provenance,
- forecast boundary,
- conservative audit outcome.

It does NOT own scoring formulas or live forecast values.

### 12.3 Runtime formula and condition evaluation

Runtime code is the source of truth for **how current conditions are evaluated**.

Primary files include:
- `opportunity_runtime.py` — Opportunity runtime policy and shared evaluators,
- `spatial_weather.py` — vertical/spatial low-cloud and cloud-sea diagnostics,
- `marine_state.py` — wave/swell diagnostics,
- `tide_state.py` — relative tide-state diagnostics,
- `access_state.py` and provider-specific access modules — dynamic access,
- `fetch_data.py` — provider acquisition, hourly data assembly and score integration.

Catalog prose such as `required_conditions`, `boosters`, and `penalties` documents the photographic contract; it MUST NOT replace the executable runtime implementation when a dedicated formula exists.

### 12.4 Place identity, navigation and compatibility metadata

`regions.py` owns Place identity and compatibility metadata such as:
- Place coordinates used by the legacy/weather layer,
- display names and aliases,
- broad Scene/Theme compatibility tags,
- navigation/search metadata where still defined there.

Legacy tags such as `coast`, `starlight`, or `cloud_sea` are discovery/compatibility metadata. They MUST NOT be treated as proof that a researched Photography Opportunity exists.

Navigation-specific semantics remain governed by `NAVIGATION_SPEC_R4_2.md`.

### 12.5 Generated weather/output data

Files such as `tw_weather.json`, `jp_weather.json`, `us_weather.json`, regional detail JSON, and `weather_details/**` are generated runtime/output artifacts.

They MAY cache or expose:
- current/past/forecast weather,
- calculated scores,
- runtime diagnostics,
- UI-ready hourly details.

They MUST NOT become the authoritative source for Place research, Opportunity definitions, or evidence provenance.

### 12.6 Specifications, research notes and handoff files

Files such as:
- `RESEARCH_EVIDENCE_SPEC_R4_2.md`,
- `NAVIGATION_SPEC_R4_2.md`,
- `B*_RESEARCH*.md`,
- `B*_HANDOFF*.md`,
- `handoff/**`

document requirements, research history, decisions and transfer state.

Specifications define policy. Research/handoff documents preserve context, but they MUST NOT override the canonical catalog or evidence registry merely because they contain newer prose. Any accepted product-data change must be reflected in the corresponding canonical machine-readable file.

### 12.7 Tests and CI

`test_opportunity_adapter.py`, audit scripts, and `.github/workflows/**` enforce schema, counts, evidence boundaries and runtime behavior.

Tests and CI are enforcement mechanisms, not product-data stores.

### 12.8 Conflict-resolution order

When two files disagree, use this ownership order for the disputed field:

1. Specification for policy/semantics.
2. `runtime_catalog_v004_r4_2.json` for researched Opportunity definitions and photographic-condition contracts.
3. `runtime_evidence_registry_r4_2.json` for evidence/provenance classification.
4. Runtime modules for executable current-condition evaluation.
5. `regions.py` for Place identity/legacy compatibility metadata.
6. Generated weather JSON for the latest computed output only.
7. Research notes and handoff files for historical context.

A conflict SHOULD be fixed at the owning layer rather than patched downstream.


## 13. Photography Place discovery and admission workflow

This section standardizes how humans and AI agents discover, classify, research, and admit new photography Places without overfitting the catalog to famous fixed-tripod viewpoints.

### 13.1 Discovery is a funnel, not a completeness gate

A candidate MUST NOT be rejected merely because the first discovery pass lacks an exact tripod coordinate, exact subject coordinate, parking coordinate, azimuth, or fully documented access route.

Research SHOULD proceed in stages: broad candidate discovery; photography-value evidence screening; photographic-field classification; Place-specific Opportunity research; Camera Zone and subject-geometry research at the precision supported by evidence; independent Navigation Target research; minimum-viable production admission; and later evidence enrichment.

Early discovery asks whether a Place is worth deeper research. It MUST NOT require all later-stage fields to be complete.

### 13.2 Photography-value screening and Visual Evidence

Discovery SHOULD use multiple independent signals rather than popularity, one search result, or one attractive photograph. Useful signals include authoritative scenic/park/tourism material, established photography/outdoor publications, multiple independent Place-specific photographs or field reports, repeated identifiable subjects/compositions, multiple useful viewpoints, seasonal subjects, map/terrain context consistent with imagery, and legal/practical access information.

Publicly accessible photographs MAY be used as Visual Evidence to determine what is actually visible, whether compositions recur, whether camera positions are concentrated or distributed, and whether multiple subjects or viewing directions are supported. A single attractive image, unsourced repost, search thumbnail, social-media volume, review count, or AI-generated image MUST NOT alone establish a production Opportunity. Visual Evidence SHOULD be corroborated when practical. Image scarcity MUST NOT by itself reject an otherwise well-supported Place.

Agents MUST NOT claim access to private, login-restricted, or unavailable imagery.

### 13.3 Photographic-field classification

After initial screening, research SHOULD classify the Place as:
- `fixed_viewpoint`: photography is materially concentrated at one verified or representative Camera Zone;
- `area_field`: photography is viable across a meaningful area and no defensible single best tripod point exists;
- `multi_viewpoint`: multiple materially different Camera Zones, subjects, or viewing directions are supported;
- `unresolved`: photographic value is supported but current evidence cannot honestly choose a more specific class.

This is descriptive, not a quality ranking. `area_field`, `multi_viewpoint`, and `unresolved` MUST NOT be downgraded merely because they lack one exact tripod coordinate.

### 13.4 Camera Zone precision and minimum-viable admission

The system MUST prefer honest uncertainty over fabricated precision. Camera Zones may be exact/verified, representative, provisional, area/range-level where the data model permits, or unresolved pending research.

Agents MUST NOT invent exact GPS, azimuth, subject coordinates, parking points, trailheads, or arrival routes merely to satisfy a schema field. If the schema cannot faithfully represent an area or multiple Camera Zones, research MUST preserve the broader truth and use the least misleading supported representation, clearly marked representative/provisional.

A Place may enter production without every enrichment field when: its identity is resolved; at least one Opportunity has adequate Place-specific evidence; location representation is not misleading; Camera Zone precision/status is honest; navigation complies with `NAVIGATION_SPEC_R4_2.md`; forecastable versus non-forecastable parts are identified; runtime does not invent subject presence; and required schema/audit/tests pass.

Exact tripod GPS, exact target GPS, exact azimuth, parking, trailhead, season detail, and access enrichment are follow-up fields unless the particular photographic, safety, or navigation claim depends on them.

### 13.5 Geometry depth and repeatable AI workflow

Geometry research MUST be as precise as the claim requires. Narrow alignments such as skyline, reflection, Milky Way, sunrise/sunset, or constrained sightlines may require Camera Zone, subject direction, horizon context, and/or azimuth evidence. Broad mountain panoramas or flower-field Opportunities may be supportable at area level without one target coordinate.

An AI agent performing Place expansion MUST: read the latest specifications/canonical data/schema/tests; search broadly without requiring complete metadata; screen using multiple photography-value signals; research Place-specific Opportunities; inspect accessible public Visual Evidence when useful; classify the photographic field; research Camera Zone/subject geometry only to justified precision; research Navigation Target independently; use conservative/provisional states for unresolved details; update canonical data/evidence; run required tests/audits; and preserve unresolved enrichment work rather than fabricating completeness.

Unknown MUST remain unknown. Provisional MUST remain provisional.


## 14. Field Intake observation-association and UX contract

This section governs the production `field-intake.html` flow that turns a photographer's local image metadata and explicit observations into an **unreviewed observation draft**. It does not admit a Field Validation case, alter scoring thresholds, or turn an observation into ground truth.

### 14.1 Human-facing workflow and data boundary

The normal photographer UI MUST NOT require the user to understand, edit, or supply observation JSON, internal schema keys, replay bookkeeping, or internal enums. The UI collects human-understandable facts and decisions; the application produces the structured observation/export.

The flow MUST make these stages understandable and distinguishable:

1. select one or more photographs/files;
2. inspect local EXIF/metadata and identify what was found or is missing;
3. associate the observation with a researched Place, or explicitly leave it unmatched;
4. confirm/supplement the actual observation, including the intended Photography Opportunity/subject where applicable and whether it was observed/held/failed/uncertain, with a concise failure reason or note when useful;
5. show the final export/submission state and the privacy/data boundary.

A missing EXIF field MUST remain unknown/unavailable unless the user explicitly supplies a value that the UI is designed to accept safely. The implementation MUST NOT invent capture time, GPS, camera/lens metadata, Place identity, Opportunity identity, or observation outcome to complete a draft.

If original photographs remain local and only structured JSON is exported, the production UI MUST say so plainly. It MUST NOT imply that the photograph or draft has been uploaded or submitted to ChaseLights when no network submission occurred.

### 14.2 Place matcher contract

A large plain `<select>`/long drop-down containing the catalog MUST NOT be the only primary Place-association control.

The production matcher MUST provide a searchable combobox/typeahead or equivalent search-first interaction. Search MUST cover, when present in the canonical/identity sources:

- user-facing Place name;
- canonical name;
- stable Place/spot ID;
- aliases;
- administrative/region text useful for disambiguation.

Search results MUST expose enough region/administrative context to distinguish ambiguous or similarly named Places. Region grouping/filtering MAY supplement search but MUST NOT replace search with another long browsing burden.

The matcher MUST be usable on desktop and mobile and MUST support the interaction modes appropriate to each surface, including keyboard operation on desktop and touch operation on mobile. Long result sets MUST NOT create a surface that is impractical to close, locate within, or correct after a mistaken selection.

### 14.3 GPS suggestion is not confirmation

When the photograph contains trustworthy GPS, the UI MAY rank nearby researched Places and SHOULD expose distance or another understandable ranking basis. A nearest-Place result is a **suggestion**, not evidence that the photograph belongs to that Place.

The observation association MUST distinguish at least:

- `unmatched` — no Place has been confirmed;
- explicit user selection/confirmation;
- a GPS-derived suggestion and its provenance;
- a user override of a suggestion.

The implementation MUST NOT silently confirm the first catalog entry, the previous Place, an arbitrary Place, or a GPS suggestion merely to avoid an empty value. When GPS is missing, unreliable, too distant, ambiguous, or otherwise below the matching policy's confidence threshold, an explicit unmatched/manual-selection state MUST remain valid.

An automatic suggestion/export MUST preserve enough provenance to explain the method and, when applicable, the distance/confidence basis. A later user selection MUST be distinguishable from the original automatic suggestion.

### 14.4 Spatial semantic boundary

Field Intake Place association is an **observation-to-Place association**. It does not redefine spatial truth.

A photograph's embedded GPS is the capture-location observation supplied by the image metadata. It MUST NOT automatically become or overwrite:

- the canonical Place coordinate;
- a researched Camera Zone;
- a Photo Target / Subject coordinate;
- a Navigation Target.

Likewise, a nearby Camera Zone is useful for candidate ranking but is not proof that the photograph was made there. Navigation semantics remain owned by `NAVIGATION_SPEC_R4_2.md`.

### 14.5 Minimum photographer-facing observation content

The primary form SHOULD minimize required fields and use photographer language. It MUST provide a comprehensible path to express, to the extent known:

- where the photograph/observation is associated;
- when it was captured;
- which researched Photography Opportunity/subject was being validated, when applicable;
- what was actually observed and whether the expected opportunity/condition held, partially held, failed, or cannot be determined;
- a concise failure reason and/or note when needed for later review.

Internal evidence status, replay identifiers, schema keys, calibration state, and provider/debug fields MAY be retained in structured data but MUST NOT be exposed as required primary-form concepts merely because the database contains them.

An exported draft remains unreviewed. Neither Place association nor a user-reported outcome alone promotes it to admitted ground truth or authorizes scoring/model changes.

### 14.6 Localization and presentation

All user-facing Field Intake semantic content is subject to the same supported-locale completeness contract as the production presentation layer. Changing locale MUST change presentation only; it MUST NOT change association identity, observation meaning, evidence semantics, or structured truth.

User-facing labels, matcher states, missing-data explanations, outcome choices, privacy/export states, validation messages, and dynamically composed messages MUST NOT leak untranslated semantic content from another supported locale except where an explicit proper-name/original-language fallback policy permits it.

### 14.7 Machine-enforcement and review gate

CI/audit/browser coverage SHOULD enforce every invariant that can be checked without pretending to resolve human/geographic judgment. At minimum, automated coverage SHOULD verify:

- an explicit unmatched state is valid;
- no arbitrary Place is silently selected when no trustworthy match is confirmed;
- the production Place matcher is search-capable rather than relying only on a catalog-sized plain select;
- exported Place association preserves method/provenance needed to distinguish unmatched, automatic suggestion, user confirmation and override;
- missing EXIF remains missing unless explicitly supplied;
- supported localization keys/states used by the Field Intake flow are covered;
- the local-photo/no-upload boundary remains truthful;
- representative desktop and mobile browser interactions can search, select, clear/correct and leave a Place unmatched.

Candidate quality, GPS trustworthiness, geographic semantics, and usability judgments that cannot be safely reduced to deterministic tests remain human/research review gates. CI green MUST NOT be treated as proof of those judgments.

### 14.8 Ownership and compliance

This section owns the Field Intake observation-association/presentation policy. It does not supersede the evidence boundary in Sections 1–13, the Camera Zone/Photo Target/Navigation Target separation in `NAVIGATION_SPEC_R4_2.md`, or the canonical ownership rules in Section 12.

A production Field Intake implementation MUST be reviewed against the latest version of this section on `main` before merge. If this specification changes while an implementation PR is open, that PR MUST be rechecked against the new normative text before it is considered ready.
