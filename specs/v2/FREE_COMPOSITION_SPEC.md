# ChaseLights V2 — Free composition and geometry-dependent conditions

Status: Draft; W1-owned normative contract upon merge. Follow latest main AGENTS.md, RESEARCH_EVIDENCE_SPEC_R4_2.md, NAVIGATION_SPEC_R4_2.md and canonical v2.1 schema.

## Per-opportunity composition dependency

A Place or PhotographyOpportunity does not inherently require a fixed camera point. Classify composition dependencies per opportunity and, where needed, per condition:

- FIXED_COMPOSITION: a claim depends on precise alignment, foreground, reflection, occlusion or other camera-to-target geometry; an unknown essential geometry-dependent condition remains UNKNOWN/NOT_EVALUABLE.
- FREE_COMPOSITION: the photographer may select framing within a researched and legally accessible field. Do not require one precise Camera GPS, unique camera-to-target azimuth, distance or elevation angle for conditions that do not depend on them.
- MOBILE_COMPOSITION: position changes along a route or aboard a platform; one coordinate must not be misrepresented as a verified complete trajectory.

These are conceptual classifications, not new enum values. A Place can support several classes and an Opportunity can mix independent regional and geometry-dependent conditions.

## Canonical representation without breaking schema changes

The v2.1 CameraContext.kind already supports point, area, route and mobile_platform. Its geometry envelope is required, but precise geojson may be null with an honest unknown/provisional status. Do not invent boundaries, polygons, GPS, routes or platform tracks. PhotographyTarget remains distinct; dynamic sky need not have fixed subject geometry. ObservationRelation may be empty where a fixed camera-to-target relation is unsupported. NavigationTarget remains independent; Directions require separately verified practical arrival coordinates and access evidence, never an inferred camera position or keyword fallback.

## Independent evaluation and fail-closed policy

Weather, astronomy, season and other area-level conditions may be evaluated independently of fixed camera geometry, provided their own evidence, approved condition contract, provider coverage, freshness and thresholds are sufficient. Unknown composition geometry makes only dependent conditions UNKNOWN/NOT_EVALUABLE, not every condition in a free-composition Opportunity. An unknown REQUIRED/BLOCKER condition essential to the selected claim still prevents FAVORABLE. Never waive a genuinely essential alignment requirement or treat GUIDANCE/provisional, missing model_binding/threshold, research-only or test-only data as a live favorable recommendation.

Place-specific evidence must establish that the subject and photographic field actually exist; legal access must be separately supported. Unknown accessible boundaries cannot be replaced by invented polygons. Structural schema PASS does not certify research, access, sources, semantic localization or runtime availability.

## Examples and language parity

Positive structural-only example: CameraContext kind=area with geometry.kind=area, status=unknown, geojson=null, no fixed ObservationRelation, and a separate regional GUIDANCE condition. This may be a structurally valid research draft but is not live FAVORABLE.

Negative examples: rejecting this research draft solely for lacking a precise GPS or unique azimuth; claiming verified Directions without separate navigation evidence; or upgrading provisional GUIDANCE to live FAVORABLE. A truly geometry-dependent required condition with unknown alignment must still fail closed.

Photographer-facing copy must be semantically equivalent in zh-TW/en/ja, for example 「可在已確認開放的區域內自行取景」 / “Choose your composition within the confirmed accessible area” / 「立ち入り可能と確認された範囲内で自由に構図を選べます」. Do not claim confirmed access unless verified.

W1 owns specs/v2 only; W2 data, W3 evaluation, W4 UI, W5 CI/integration. Preserve Legacy/V2 isolation; do not build automated Legacy/V2 comparison.
