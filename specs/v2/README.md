# ChaseLights V2 specification index

Status: draft. Owner: Worker 1 (architecture and schema).

Canonical schema: `schema/opportunity-v2.1.schema.json`.

**Composition and CameraContext:** `FREE_COMPOSITION_SPEC.md` is the V2 domain contract for free framing, fixed composition and mobile composition. A researched photography Opportunity need not have one fixed tripod point. CameraContext supports `point` / `area` / `route` / `mobile_platform`; exact GPS, polygon, single camera-to-target azimuth, distance or elevation are required only for a specific claim that depends on them. Unknown geometry affects the dependent condition, not independent regional weather/astronomy/season evaluation. An unknown essential condition still prevents overall FAVORABLE. This is a per-Opportunity/per-condition dependency decision, not a new breaking enum.

All V2 workers must check the latest `main` and current R4.2 research and navigation specifications before editing and before merge. The V2 domain separates Camera Context, Photography Target, Observation Relation and Navigation Target. Fixed target geometry is optional for dynamic phenomena. Place-specific subject evidence remains necessary; do not invent access boundaries or geometry. Directions require an independently verified NavigationTarget. Research-only, provisional and test-only records cannot become live FAVORABLE. User-facing zh-TW, en and ja content must be semantically equivalent.

Legacy website and V2 must remain independent; V2 does not overwrite Legacy routes, data or scoring. A Legacy-to-V2 link is added only after the V2 URL is verified. No automatic Legacy/V2 comparison is required.

This index is not an approval to merge. Schema validation, evidence audit, translation audit, and latest-main spec gate remain required.
