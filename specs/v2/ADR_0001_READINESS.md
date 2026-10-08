# ADR-0001: Separate canonical readiness from runtime availability

Status: proposed (Worker 1, 2026-10-09). This ADR is normative for the V2 schema review.

- Canonical Opportunity stores research readiness (R0–R3) and research evidence gaps only.
- Runtime availability (FULL/LIMITED/GUIDANCE_ONLY/UNAVAILABLE), data freshness, provider status, and dynamic-state unknowns belong to timestamped EvaluationResult records, not the canonical Opportunity.
- The current `opportunity-v2.1.schema.json` incorrectly requires `readiness.runtime_availability`. Remove it and prohibit that field in canonical records before merge.
- Do not infer FAVORABLE from R2/R3 or from missing required conditions. Unknown essential conditions propagate UNCERTAIN or NOT_EVALUABLE.
- Worker 2 must not import runtime status as a stable place attribute. Worker 3 owns the evaluation-result representation, subject to Worker 1 schema approval.

Acceptance: canonical fixture validates without runtime availability; fixture containing it fails; runtime result records freshness, unknown reasons, and model/provider versions.
