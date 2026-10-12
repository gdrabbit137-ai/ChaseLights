# ChaseLights V2 — Free composition and optional viewpoint policy

Status: W1 integration proposal; binding only after review and merge. This document owns the detailed composition and per-condition rule. `CAMERA_AREA_COMPOSITION_POLICY.md` supplies the worker acceptance checklist. Read alongside latest main `AGENTS.md`, `RESEARCH_EVIDENCE_SPEC_R4_2.md`, `NAVIGATION_SPEC_R4_2.md`, and canonical v2.1 schema.

## Default: the photographer chooses the composition

For ordinary Place-specific Photography Opportunities, the photographer normally chooses framing within a researched, lawfully accessible area or route. A fixed tripod location, precise verified Camera GPS, unique camera-to-target azimuth/distance/elevation, recommended viewpoint, or explicit FIXED/FREE/MOBILE classification is **not** a prerequisite for Opportunity research, R1 research-only delivery, general forecast evaluation or acceptance. Do not impose a classification enum or a breaking schema requirement. Composition dependencies are identified **only where a particular claim requires them**.

A Place-specific subject/existence claim still needs evidence appropriate to its geographic scope under R4.2. An Opportunity is not established by weather or a generic landscape tag. Do not infer public access from an area or fabricate a polygon for an unknown access boundary. Existing CameraContext.kind values are `point`, `area`, `route`, and `mobile_platform`; the v2.1 schema requires a `geometry` envelope but permits `status=unknown` and `geojson=null`. For a mobile platform or route, one point cannot stand in for a verified trajectory.

## Optional candidate viewpoints, not verified facts

W2 may research, infer or calculate candidate viewpoints as **nonblocking enrichment**, with source provenance, assumptions, confidence, positional precision, and access uncertainty. Clearly distinguish a calculated/representative candidate from an observed, separately verified camera location. A candidate must not be described as uniquely optimal, upgraded to verified GPS, or used as a Directions destination without independent navigation/access evidence. Missing candidate viewpoints do not block R1 research-only delivery or independent area-level conditions.

CameraContext, PhotographyTarget, ObservationRelation and NavigationTarget remain separate. An ObservationRelation may be absent when a fixed camera-to-target relation is not supported. NavigationTarget describes a practical arrival point, not the subject or an inferred camera location. Directions are allowed only for independently verified lawful arrival targets with coordinates and evidence; never use a place keyword as a fallback. Access restrictions, closures, and lawful entry uncertainty remain prominent independent advisories; they never downgrade photographic weather suitability or become REQUIRED/BLOCKER conditions. They still forbid unsafe entry advice and unverifiable Directions.

## Per-condition evaluation and fail-closed behavior

For an ordinary regional WEATHER, ASTRONOMY, SEASON_TIME or environmental condition, evaluate independently of precise camera GPS **only when** that condition's prerequisites are actually met: researched Place-specific claim, appropriate real provider, spatial coverage/representativeness, freshness, approved AUTO contract, scientifically justified threshold/model binding; access/safety is separately warned and controls navigation only. If required provider, calibration, threshold, freshness or coverage is missing, return UNKNOWN/NOT_EVALUABLE; do not manufacture a favorable result. GUIDANCE, provisional or null threshold/model binding and research-only/test-only records never authorize live FAVORABLE.

Only an **explicit precision-composition claim** (such as a sun alignment between specific buildings, reflection from a defined camera position, or a named-peak alignment) requires its own supported camera/target geometry. When necessary geometry is unknown, only that claim/condition becomes UNKNOWN/NOT_EVALUABLE; independently evaluable regional conditions are not invalidated. However, if the unknown precision condition is a REQUIRED/BLOCKER condition for the **selected overall claim**, it still prevents that overall claim from becoming FAVORABLE. Favorable regional weather alone never proves an exact composition or subject presence.

**R4.2 §4.1 sea-of-clouds exception:** A forecast-derived cloud-sea *environmental state* requires a known Camera Zone coordinate, surrounding/target spatial and vertical weather samples, terrain separation and the other §4.1 gates. Free composition does not waive these specific spatial-model prerequisites. This does **not** impose a unique fixed tripod point or precise alignment on ordinary Opportunities, and does not prove a scenic composition, access or safety. Missing spatial inputs fail closed for that derived condition only.

## Synthetic contract examples (not live forecasts)

- **Positive, structural only:** `CameraContext.kind=area`, `geometry.kind=area`, `geometry.status=unknown`, `geojson=null`, empty `observation_relations`, and a regional `GUIDANCE` condition with null threshold/model binding can be a valid *research draft*. It is **not** live FAVORABLE.
- **Positive, evaluator acceptance for W3:** An independently researched ordinary regional condition with valid approved AUTO binding, real provider, coverage, freshness and threshold must remain eligible for evaluation when exact camera GPS is absent.
- **Negative, evaluator acceptance for W3:** An explicit precision-alignment condition without required geometry is UNKNOWN/NOT_EVALUABLE, without poisoning a separate ordinary regional condition; a required unknown still blocks overall FAVORABLE.
- **Negative, navigation:** A candidate viewpoint or unverified arrival point must never generate verified Directions.
- **Negative, research/runtime:** Unproven subject existence, provisional GUIDANCE or missing threshold/model binding must not be promoted to a live recommendation.

Example: Jingzaijiao salt fields can support general salt-field sunset photography when supported by Place-specific evidence. A photographer chooses a permitted composition; any particular reflection/alignment is a separately evidenced claim. Weather and sun timing are not proof of reflective geometry, and a candidate viewpoint is not automatically a verified arrival point.

## Worker acceptance and localization

W1 owns schema/spec and structural tests; W2 owns researched catalog and optional viewpoint enrichment; W3 owns runtime evaluator regression for independent regional AUTO versus precision-geometry UNKNOWN; W4 owns UI copy; W5 owns integration/CI/review gates. W3 #447 and W5 #449 provide the latest tested worker heads at this proposal's creation; W5 must pin and retest the new W1 HEAD after integration. W1 structural tests alone cannot prove runtime behavior.

All user-visible content must be semantically equivalent in zh-TW, en and ja; e.g. 「可在已確認開放的區域內自行取景」 / “Choose your composition within the confirmed accessible area” / 「立ち入り可能と確認された範囲内で自由に構図を選べます」. Never claim confirmed access unless independently verified. Preserve Legacy/V2 isolation and do not build automatic Legacy/V2 comparisons.
