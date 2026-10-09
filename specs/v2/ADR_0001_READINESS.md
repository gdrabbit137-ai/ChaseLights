# ADR-0001: Separate canonical readiness from runtime availability

Status: proposed (Worker 1, 2026-10-09). This ADR is normative for the V2 schema review.

- Canonical Opportunity stores research readiness (R0–R3) and research evidence gaps only.
- Runtime availability (FULL/LIMITED/GUIDANCE_ONLY/UNAVAILABLE), data freshness, provider status, and dynamic-state unknowns belong to timestamped EvaluationResult records, not the canonical Opportunity.
- The current `opportunity-v2.1.schema.json` already **does not require or allow** `readiness.runtime_availability`: the canonical `readiness` object has `additionalProperties: false`. Keep this invariant; regression-test rejection both inside `readiness` and at the Opportunity top level. Do not add dynamic `availability` or provider freshness to the canonical record.
- Do not infer FAVORABLE from R2/R3 or from missing required conditions. Unknown essential conditions propagate UNCERTAIN or NOT_EVALUABLE.
- Worker 2 must not import runtime status as a stable place attribute. Worker 3 owns the evaluation-result representation, subject to Worker 1 schema approval.

Acceptance: the canonical fixture passes the real `validate_record()` validator without runtime availability; the same fixture fails if `runtime_availability` is added to canonical `readiness` (or the Opportunity root). A separately versioned, timestamped runtime EvaluationResult contract must cover freshness, unknown reasons, and model/provider versions before live recommendation; defining that runtime contract is a distinct pending gate.
