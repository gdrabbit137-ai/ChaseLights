# Field Intake Upload and Admission Contract R4.2

Status: normative companion to RESEARCH_EVIDENCE_SPEC_R4_2.md Section 14.

## Scope

Production field-intake.html submits photographs and structured observations to ChaseLights for validation. Upload, automated assessment, and admission as validation evidence are separate states. Automated assessment is not ground-truth admission.

## Workflow

The user-facing flow MUST distinguish file selection, metadata inspection, Place association, observation confirmation, upload/submission, analysis, assessment, review/admission, rejection, and failure. The UI MUST NOT require users to edit JSON or internal schema/enums.

Missing metadata MUST remain unknown unless explicitly supplied. The system MUST NOT invent time, location, camera/lens data, Place, Opportunity, or outcome.

## Place association

The primary Place matcher MUST be searchable by available display name, canonical name or ID, aliases, and region text. A catalog-sized plain select MUST NOT be the only primary control.

GPS-derived nearby Places are suggestions only. No first, previous, arbitrary, or suggested Place may be silently confirmed. Unmatched/manual-selection MUST remain valid. Persist suggestion method and confidence/distance basis plus later confirmation or override.

Photograph location and Place association MUST NOT create, overwrite, or validate canonical Place coordinates, Camera Zone, Photo Target, or Navigation Target. NAVIGATION_SPEC_R4_2.md owns those semantics.

## Observation

The primary form SHOULD minimize required fields and let a photographer express where/when the image was made, intended Opportunity when known, what was observed, whether it held/failed/was uncertain, and a concise reason/note. Internal bookkeeping MUST NOT become required primary-form concepts.

## Submission, privacy, and provenance

Submitted photographs and capture-location metadata are non-public by default. Validation permission MUST NOT be treated as publication permission; any publication choice MUST be separate.

Persist provenance for user facts/corrections, original metadata and missing fields, Place suggestion/confirmation/override, automated assessment method/version/confidence, relevant Field Snapshot/replay evidence, and later review/admission decision.

Upload or assessment MUST NOT mutate canonical research, navigation data, provider/forecast truth, or Opportunity definitions.

## Assessment and admission

System semantics MUST distinguish pre-submit, uploading, submitted, analyzing, assessed, review-required/unresolved, admitted, rejected/not-admitted, and failed/retryable states. Implementations MAY use different internal names only if these meanings remain distinguishable.

Assessment MAY combine image content, metadata, capture time/location, confirmed Place/Opportunity association, and Field Snapshot/replay evidence. Insufficient or conflicting evidence MUST permit unknown/unresolved.

Successful upload, nearest-Place suggestion, user-reported outcome, or automated image classification alone MUST NOT admit ground truth. Admission remains governed by the evidence rules in RESEARCH_EVIDENCE_SPEC_R4_2.md Sections 1-13.

## Localization and responsive UX

Mobile and desktop MUST support correction, unmatched state, keyboard/touch-appropriate Place search, and clear upload/analysis state. All user-facing semantic content MUST obey supported-locale completeness; locale changes MUST NOT alter structured meaning.

## Machine enforcement

Automated coverage SHOULD verify: unmatched is legal; no silent Place default; matcher is searchable; association provenance persists; missing metadata stays missing; upload/analysis/admission states are not conflated; automated assessment cannot silently admit ground truth; validation permission does not imply publication; localization keys are covered; desktop/mobile search/select/clear flows work; upload failure or pending analysis cannot report success/admission.

Candidate quality, geographic meaning, image interpretation, evidence sufficiency, and usability remain human/research review gates where deterministic automation would create false certainty.

## Ownership

RESEARCH_EVIDENCE_SPEC_R4_2.md remains the evidence source of truth. This companion owns the Field Intake upload/assessment contract only where Section 14 cross-references it. NAVIGATION_SPEC_R4_2.md remains authoritative for Camera Zone, Photo Target, and Navigation Target.

Backend/storage/API/analysis implementation belongs to ChaseLights main development. Production field-intake.html interaction and wording belong to ChaseLights photographer UI/UX. Both MUST re-read latest main specifications before merge.
