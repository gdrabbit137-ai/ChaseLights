# V2 Readiness and Release Governance

Status: Draft 2026-10-09. Owner: Worker 1. Companion to ARCHITECTURE_SPEC.md.

## Readiness

Research maturity R0: lead only; R1: existence/camera/target evidenced; R2: contract supports limited evaluation; R3: validated prediction capability. Runtime availability is separate: FULL, LIMITED, GUIDANCE_ONLY, UNAVAILABLE. A record may be R3 but lack fresh forecast inputs today.

Unknown reasons: RESEARCH_GAP, GEOMETRY_GAP, DATA_UNAVAILABLE, MODEL_UNSUPPORTED, DYNAMIC_UNVERIFIED, SOURCE_CONFLICT, LOW_CONFIDENCE, STALE_DATA.

## Evaluation

Statuses: FAVORABLE, UNFAVORABLE, UNCERTAIN, NOT_EVALUABLE. An essential unknown prevents FAVORABLE. A blocker prevents favorable recommendation regardless of quality score. A missing threshold is not zero. An uncalibrated CONDITIONS result is not an occurrence probability.

## Evidence and validation

Preserve R4.2 place-specific evidence and navigation rules. Use Draft → Evidence Review → Schema Validation → Crosswalk Audit → Approval → Canonical Release. Grade C is research discovery, not sufficient production proof. Record sources, evidence scope, confidence, limitations and reviewer. Photos and EXIF may suggest Place association but cannot silently alter camera, subject or navigation geometry. Unknown EXIF remains unknown. Human-machine claim crosswalk status MISMATCH blocks publication.

## Traceability and language

Evaluation results must identify opportunity revision, contract revision, model versions, provider runs, issue/valid times, input quality, per-condition outcomes, unknown reasons and explanation references. User-facing names, explanations, navigation/access notices and statuses must be semantically equivalent in zh-TW, en and ja.

## Merge and deploy

Read latest main and effective R4.2 specs before merging. Require Draft 2020-12 schema validation, valid/invalid fixtures, reference checks, negative unknown tests, localization presence tests and human review of evidence/semantic parity. CI success alone does not prove geographic correctness. V2 must deploy independently; only after its URL and smoke checks pass may Worker 5 add the Legacy-to-V2 link. Do not build a Legacy/V2 comparison feature.
