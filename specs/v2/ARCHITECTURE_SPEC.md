# ChaseLights V2 — Architecture and Product Specification

**ID:** CL-V2-ARCH-001 · **Version:** 0.3 Draft · **Owner:** Worker 1 · **Date:** 2026-10-09

## 1. Scope and non-negotiable boundaries

V2 is an evidence-backed, explainable photography-opportunity prediction system. Research proves **what** can be photographed; runtime weather, astronomy and other observations estimate **when** that verified opportunity may work. No model may invent a Place-specific photography subject from generic weather or terrain. Preserve the narrow R4.2 cloud-sea environmental exception without treating it as proof of composition.

Legacy stays online unchanged while V2 is built separately. Both versions may coexist in one repository, but V2 must not import Legacy runtime modules or rely on Legacy data paths. A localized Legacy-to-V2 link is permitted only after V2's public URL passes smoke tests. No automatic Legacy/V2 comparison UI or result matching is required; the owner will spot-check.

## 2. Layered system

Research and Evidence → Draft Intake → Evidence Review → Schema and Human/Machine Crosswalk → Canonical Release → Condition Contract → Data Adapters and Phenomenon Models → Opportunity Evaluation → Versioned Result Store → V2 API/UI.

Start as a modular monolith, with separate batch ingestion/evaluation jobs. Canonical revisions and provenance are authoritative; JSON is interchange, SQLite is an acceptable initial database, Excel is a human review export rather than source of truth. All external data adapters must preserve provider, forecast issue time, valid time, units, grid coverage/resolution, quality, freshness and license.

## 3. Canonical entities

- **Place:** stable geographic identity, administrative location, aliases and source.
- **PhotographyOpportunity:** stable ID, revision, Place ID, subject/composition, lifecycle and review status.
- **CameraContext:** point, area, route or mobile platform; verified geometry and legal/safe access are separate claims.
- **PhotographyTarget:** fixed geographic feature, celestial body, dynamic sky, atmospheric volume, observer-dependent phenomenon, environmental state or multi-component composition. A fixed Subject Zone is **not required** for a dynamic target.
- **ObservationRelation:** typed link between camera and target, such as line-of-sight, sky visibility, reflection, alignment, terrain-cloud or observer-dependent geometry. Direction, distance and elevation angle may be unknown.
- **NavigationTarget:** practical arrival point, never inferred automatically from a camera point, photographed subject or map search text. Retain R4.2 verified/provisional/review/multiple-route distinctions.
- **EvidenceClaim:** specific assertion, source references, scope, grade, provenance and audit status.
- **ConditionContract:** researched criteria with roles, evaluation modes, unknown policy and model bindings.
- **EvaluationResult:** versioned runtime judgment with reproducible input and explanation references.

Stable IDs must not be derived from translated names. Geometry must declare verification status, derivation method and uncertainty. A photograph alone does not establish exact GPS, camera orientation, capture time or forecast threshold.

## 4. Condition semantics

Each condition has a unique ID, domain, metric, operator, threshold/unit where justified, evidence/claim references, role and evaluation mode. Roles: REQUIRED, BLOCKER, QUALITY. Modes: AUTO, GUIDANCE, VERIFY. These axes are independent. Domains include WEATHER, ASTRONOMY, SEASON_TIME, ACCESS_SAFETY, SUBJECT_STATE, GEOMETRY_COMPOSITION, SPACE_WEATHER, OCEAN and HYDROLOGY.

Capabilities are WINDOW (deterministic temporal geometry), CONDITIONS (favorable conditions, not certainty), PROBABILITY (only calibrated probability) and OBSERVATION (verified state with time/provenance). A missing threshold remains null/unknown; it never silently becomes zero or passing. An unverified required bloom, snow, aurora or fog state cannot be reported as confirmed. Quality score must never override blockers or safety.

## 5. Models and data

Maintain a versioned Model Registry declaring model ID/version, required inputs, capability, spatial scope, forecast horizon, native resolution, output contract, confidence/limitations and fallback. Shared adapters: weather, celestial geometry, terrain/visibility, ocean/tides, hydrology, space weather and field observations. Specialized models may include aurora, Milky Way, meteor showers, cloud sea, fog, rainbow, coastal waves, waterfalls, phenology, snow/ice and forest light beams. Specialized models provide evidence/condition results; the common evaluation engine owns the final status.

Start with verifiable celestial windows and basic weather conditions. Local cloud sea/fog/light beams need cautious limited capability. Do not invent event probabilities or turn an interpolated grid into higher native forecast precision.
