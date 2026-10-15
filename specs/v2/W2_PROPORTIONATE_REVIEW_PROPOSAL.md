# V2 W2 proportionate research review policy (proposal)

Status: W1 normative V2 R1 review policy upon merge; applies to R1 research records only. R4.2's place-specific subject-existence evidence remains mandatory. This policy does not authorize live forecasts, legal access, verified navigation, automatic merges or deployments.

## Separate independent gates
1. **Research admission R1:** place-specific primary Grade A or independently reviewable Grade B evidence supports each claimed subject. Keep source URL, access date, claim scope, uncertainty, source pointer, human-readable review and machine canonical crosswalk. Grade C alone is R0/HOLD. An AI-generated assertion never substitutes for evidence.
2. **Safety and navigation:** uncertain access or closure produces conspicuous independent advisory, not a photography score penalty. Do not assert lawful entry. Directions require a separately verified navigation target. Broad free composition needs no exact tripod GPS.
3. **Runtime promotion:** R1 alone never yields AUTO, FAVORABLE or calibrated probability. W3 must verify real provider/time/coverage/provenance, approved condition thresholds and geometry only for geometry-dependent claims; missing critical inputs yield UNKNOWN/NOT_EVALUABLE.
4. **Publication:** R1 research-only publication may proceed with documented unknowns and automated tests, without blanket human signoff. Actual live recommendation, legal-access assurance, or disputed/high-risk claims require independent scoped review.

## Three-level exception-based checks (NOT R4.2 evidence grades)
- **A / AUTO-PASS:** place-specific evidence adequately supports limited R1 subject claim; schema, source pointer, crosswalk and zh-TW/en/ja completeness and semantic checks pass. Record evidence and machine review. Human blanket signature not required for research-only.
- **B / WARN-PASS:** core subject is supported, but optional viewpoint/photo EXIF, exact camera polygon, seasonal timing or nonessential geometry is unknown. Record per-field UNKNOWN and independent safety advisory; never upgrade unsupported claims. Research-only eligible.
- **C / HOLD:** subject existence not supported by Grade A/B, fabricated/inaccessible evidence, unresolved material contradiction, false lawful access assertion, missing critical translations or canonical mismatch. Hold affected claim/record; do not block unrelated records in batch. Security or legal hazard receives human escalation, never AI self-certification.

## W2 batch procedure
For each five candidates: (1) research actual place-specific primary evidence and explicit claim; (2) write canonical, human review, audit source ledger and exact crosswalk; (3) run deterministic schema/pointer/translation checks and independent semantic AI review; (4) classify A/B/C per record, with C isolated and clear correction; (5) submit owner-only Draft PR with IDs, A/B/C counts, UNKNOWN fields, sources, tests and exact SHA; (6) W5 separately reviews source-pin transitions and CI before any merge or Research-only publish. No fake source/threshold and no test bypass.

## Normative release decision

R1 Research-only eligibility and a public deploy are separate decisions: A/B classification alone cannot trigger deployment. W5 may merge a scoped research-only change only after independent source/semantic checks, current-head CI and applicable approvals. A C/HOLD item remains isolated. Existing signed-off data is not silently downgraded; existing pending signoff is not silently marked approved. This document does not grant an exception to a GitHub branch-protection rule.

## Worker handoff
- W1: reconcile this policy with R4.2 and existing V2 specs; no silent supersession of normative rules.
- W2: apply A/B/C to Batch05, retain human/machine crosswalk and evidence, avoid redundant mandatory human signoff for every R1 field.
- W3: never infer AUTO/FAVORABLE from R1 A/B status; fail closed on missing scientific inputs.
- W4: expose research-only status, unknowns and separate access advisories in all three languages; no verified Directions without evidence.
- W5: keep source hashes, tests, CI and explicit release approvals; do not treat pending noncritical human research signoff as an automatic R1 publication blocker.

## Compatibility and rollout
This policy refines the *review workflow* for V2 R1 Research-only, not R4.2's evidence grades or minimum subject-existence proof. R4.2 sections 1–5 and 7.1–7.2 retain precedence for claim eligibility and presentation; NAVIGATION_SPEC_R4_2 governs directions; ACCESS_ADVISORY_SPEC governs closure warnings. AGENTS.md ownership, independent CI, three-language semantic parity and no-automatic-deploy remain unchanged. Prior explicit human signoff flags must remain PENDING unless actual human review occurred; automatic review may enable research-only publication where separately permitted but MUST NOT forge a human signature, change a verified claim, or bypass branch protections. W5 must check applicable gates and record exceptions; #465/#474 human review tasks remain tracked for material claims and any future live promotion.
