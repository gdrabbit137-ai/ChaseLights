# ChaseLights V2 specification index

Status: draft. Owner: Worker 1 (architecture and schema).

`ACCESS_ADVISORY_SPEC.md` is the normative V2 separation: access/closure information is a prominent warning and navigation guard only, not a photography REQUIRED/BLOCKER, score or forecast-result gate. Legacy ACCESS_SAFETY conditions must be migrated out of Condition Contract; a climate-favorable forecast may coexist with a closed-area warning.

Canonical research schema: `schema/opportunity-v2.1.schema.json`. Separate timestamped runtime result contract: `schema/evaluation-result-v0.1.schema.json`. Its structural validation is necessary but cannot by itself authorize a live recommendation: canonical contract approval, justified threshold and AUTO model binding, real provider coverage/freshness/time/provenance, and evidence must also be checked semantically.

## Composition and evaluation

`FREE_COMPOSITION_SPEC.md` defines the per-claim geometry dependency and fail-closed evaluation rules. Ordinary Place-specific photography defaults to user-selected framing within an actually permitted area or route. A fixed camera GPS, one tripod position or recommended viewpoint is not required for research or an independently supported regional condition. The optional viewpoint and W1–W5 acceptance checklist are in `CAMERA_AREA_COMPOSITION_POLICY.md`.

Only a claim that actually depends on precise distance, bearing, elevation angle, reflection or alignment needs the corresponding verified geometry. Missing geometry leaves that condition UNKNOWN/NOT_EVALUABLE without invalidating independent conditions. If it is REQUIRED or BLOCKER for the selected overall claim, the overall claim cannot become FAVORABLE. R4.2's forecast-derived sea-of-clouds environmental exception retains its own spatial prerequisites. A schema-valid research draft, GUIDANCE condition or test-only result is never a live forecast.

All V2 workers must check the latest `main` and current R4.2 research and navigation specifications before editing and before merge. CameraContext, PhotographyTarget, ObservationRelation and NavigationTarget have separate responsibilities. Dynamic targets need no invented fixed subject coordinate. Unknown critical conditions cannot count as favorable. An area, a candidate viewpoint, a photograph or a target coordinate never proves lawful access or a practical arrival point. Directions require a separately verified NavigationTarget. User-facing zh-TW, en and ja content must be complete and semantically equivalent.

Legacy website and V2 must remain independent; V2 does not overwrite Legacy routes, data or scoring. A Legacy-to-V2 link is added only after the V2 URL is verified. No automatic Legacy/V2 comparison is required.

This index is not an approval to merge or publish a live forecast. Schema and reference validation, semantic runtime gates, evidence/access audit, translation review, current-head CI, and latest-main spec gate remain required.
