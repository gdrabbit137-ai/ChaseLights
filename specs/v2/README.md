# ChaseLights V2 specification index

Status: draft. Owner: Worker 1 (architecture and schema).

Canonical schema: `schema/opportunity-v2.1.schema.json`.

All V2 workers must check the latest `main` and current R4.2 research and navigation specifications before editing and before merge. The V2 domain separates Camera Context, Photography Target, Observation Relation and Navigation Target. Fixed target geometry is optional for dynamic phenomena. Unknown critical conditions cannot count as favorable. User-facing zh-TW, en and ja content must be semantically equivalent.

Legacy website and V2 must remain independent; V2 does not overwrite Legacy routes, data or scoring. A Legacy-to-V2 link is added only after the V2 URL is verified. No automatic Legacy/V2 comparison is required.

This index is not an approval to merge. Schema validation, evidence audit, translation audit, and latest-main spec gate remain required.

## Default composition and optional viewpoint guidance

**Photographers normally choose their own composition.** Fixed camera GPS, a unique tripod location and camera-to-subject geometry are **not prerequisites** for ordinary Opportunity research or regional condition evaluation. Verified or computed candidate viewpoints are optional extra information, with evidence and uncertainty labels; they are never implicitly verified navigation points. Only a separately claimed precision-alignment composition requires the corresponding geometry evidence, and failure blocks that specific claim rather than unrelated conditions. See `CAMERA_AREA_COMPOSITION_POLICY.md` for the binding V2 worker acceptance requirements after merge. Do not weaken unknown propagation, access verification, source validity or three-language parity.
