"""Conservative V2.1 evaluator (test booleans/raw diagnostics, no network I/O).

This module consumes *pre-evaluated boolean* observations. It never computes
weather/astronomy thresholds, verifies geographic facts, or recommends live use.
Raw provider context can be traced separately; it never becomes a passing boolean.
"""

from datetime import datetime

ROLES = ("REQUIRED", "BLOCKER", "QUALITY")
MODES = ("AUTO", "GUIDANCE", "VERIFY")


def _instant(value):
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else None
    except ValueError:
        return None


def _observe(condition, observations, at):
    """Return (PASS|FAIL|UNKNOWN, reason, trace); never coerce values."""
    cid = condition["id"]
    mode = condition.get("evaluation_mode")
    obs = observations.get(cid)
    trace = {"condition_id": cid, "role": condition["role"],
             "evaluation_mode": mode, "domain": condition.get("domain"),
             "state": "UNKNOWN", "reason": ""}
    if mode != "AUTO":
        trace["reason"] = "NON_AUTO_MODE"
        return trace
    if condition.get("unknown_policy") != "propagate_unknown":
        trace["reason"] = "INVALID_UNKNOWN_POLICY"
        return trace
    if condition.get("validation_status") != "validated":
        trace["reason"] = "UNVALIDATED_CONDITION"
        return trace
    # A precision-composition claim needs a separate verified geometry engine.
    # No synthetic boolean may stand in for alignment/reflection geometry.
    # General WEATHER/ASTRONOMY conditions are never gated on this geometry.
    if condition.get("domain") == "GEOMETRY_COMPOSITION":
        trace["reason"] = "PRECISION_COMPOSITION_NOT_EVALUABLE"
        return trace
    if not isinstance(obs, dict):
        trace["reason"] = "MISSING_OBSERVATION"
        return trace
    for field in ("provider", "source", "issued_at", "valid_at", "freshness", "test_only"):
        if field in obs:
            trace[field] = obs[field]
    if obs.get("test_only") is not True:
        trace["reason"] = "UNSUPPORTED_NON_TEST_INPUT"
        return trace
    if not all(isinstance(obs.get(key), str) and obs[key].strip()
               for key in ("provider", "source")):
        trace["reason"] = "MISSING_PROVENANCE"
        return trace
    if obs.get("freshness") != "fresh":
        trace["reason"] = "STALE_OR_UNKNOWN_FRESHNESS"
        return trace
    issued = _instant(obs.get("issued_at"))
    valid = _instant(obs.get("valid_at"))
    if not (at and issued and valid and issued <= valid and issued <= at and valid == at):
        trace["reason"] = "INVALID_OR_MISMATCHED_TIME"
        return trace
    if type(obs.get("value")) is not bool:
        trace["reason"] = "NON_BOOLEAN_VALUE"
        return trace
    trace["state"] = "PASS" if obs["value"] else "FAIL"
    trace["reason"] = "BOOLEAN_TRUE" if obs["value"] else "BOOLEAN_FALSE"
    return trace


def evaluate(contract, observations, readiness):
    """Evaluate V2.1 conditions deterministically; NEVER issue live favorable.

    `readiness` holds research maturity separately from runtime availability.
    `evaluated_at` is an explicit timestamp to make evaluation reproducible.
    """
    if not isinstance(contract, dict) or not isinstance(observations, dict) or not isinstance(readiness, dict):
        return {"decision": "UNKNOWN", "reasons": ["INVALID_ARGUMENTS"],
                "unknown": True, "live_recommendation": False, "conditions": [], "axes": {}}
    conditions = contract.get("conditions")
    if not isinstance(conditions, list) or not conditions:
        return {"decision": "UNKNOWN", "reasons": ["NO_CONDITIONS"],
                "unknown": True, "live_recommendation": False, "conditions": [], "axes": {}}
    at = _instant(readiness.get("evaluated_at"))
    seen = set()
    traces = []
    access_advisories = []
    for condition in conditions:
        if (not isinstance(condition, dict) or
                not isinstance(condition.get("id"), str) or not condition["id"] or
                condition["id"] in seen or condition.get("role") not in ROLES or
                condition.get("evaluation_mode") not in MODES):
            return {"decision": "UNKNOWN", "reasons": ["INVALID_CONTRACT_CONDITION"],
                    "unknown": True, "live_recommendation": False, "conditions": [], "axes": {}}
        seen.add(condition["id"])
        # Legacy canonical contracts incorrectly encoded closures as REQUIRED/
        # BLOCKER ACCESS_SAFETY. Never evaluate them as photography conditions.
        # This quarantine is defensive; new canonical documents omit them.
        if condition.get("domain") == "ACCESS_SAFETY":
            access_advisories.append({
                "condition_id": condition["id"],
                "reason": "ACCESS_ADVISORY_ONLY",
                "legacy_role": condition["role"],
                "notes_i18n": condition.get("notes_i18n"),
                "affects_photography_suitability": False,
            })
            continue
        traces.append(_observe(condition, observations, at))
    axes = {role: {mode: {state: 0 for state in ("PASS", "FAIL", "UNKNOWN")}
                   for mode in MODES} for role in ROLES}
    for trace in traces:
        axes[trace["role"]][trace["evaluation_mode"]][trace["state"]] += 1
    # Access advisories never count as a photo REQUIRED/BLOCKER or missing
    # critical observation. Source-confirmed legal navigation is a separate UI
    # safeguard and cannot change environmental suitability.
    # Never silently exclude a REQUIRED/BLOCKER precision-composition claim.
    # The current contract has claim_refs but no explicit selected-claim gate:
    # we cannot prove that a geometry dependency is merely optional. Treat
    # its UNKNOWN as critical until W1 defines selection/dependency semantics.
    # General regional contracts without geometry remain independently testable.
    blocking = any((t["role"] == "REQUIRED" and t["state"] == "FAIL") or
                   (t["role"] == "BLOCKER" and t["state"] == "PASS") for t in traces)
    critical_unknown = any(t["role"] in ("REQUIRED", "BLOCKER") and
                           t["state"] == "UNKNOWN" for t in traces)
    # An all-QUALITY contract cannot pass; an all-geometry contract stays
    # UNKNOWN because geometry evaluation itself is not implemented.
    missing_critical = not any(t["role"] in ("REQUIRED", "BLOCKER") for t in traces)
    research_only = (contract.get("status") != "approved" or
                     readiness.get("lifecycle_status") != "approved" or
                     readiness.get("research_only") is not False)
    reasons = []
    if blocking:
        decision = "BLOCKED"
        reasons.append("REQUIRED_FAILED_OR_BLOCKER_TRIGGERED")
    elif research_only:
        decision = "UNKNOWN"
        reasons.append("CONTRACT_OR_OPPORTUNITY_NOT_APPROVED")
    elif critical_unknown or missing_critical:
        decision = "UNKNOWN"
        reasons.append("CRITICAL_UNKNOWN_OR_ABSENT")
    else:
        decision = "TEST_ONLY_CONDITIONS_MET"
        reasons.append("TEST_ONLY_NOT_LIVE_RECOMMENDATION")
    reasons.extend(sorted({t["reason"] for t in traces if t["state"] == "UNKNOWN"}))
    return {"decision": decision, "reasons": reasons,
            "unknown": critical_unknown or missing_critical or research_only,
            "live_recommendation": False, "evaluated_at": readiness.get("evaluated_at"),
            "research_level": readiness.get("research_level"),
            "conditions": traces, "access_advisories": access_advisories, "axes": axes}


def evaluate_raw_forecast(contract, source_inputs, readiness):
    """Send raw provider context through the existing conservative evaluator.

    No raw field is a boolean condition observation. Even a fresh real forecast
    cannot establish skyline visibility or city-light overlap. This diagnostic
    bridge preserves the engine's REQUIRED/BLOCKER/GUIDANCE behavior and records
    *why* the available input cannot satisfy each condition. Caller-supplied
    source_inputs are context, never authenticated evidence or permission to pass.
    """
    result = evaluate(contract, {}, readiness)
    for trace in result["conditions"]:
        domain = trace.get("domain")
        context = source_inputs.get(domain, {}) if isinstance(source_inputs, dict) else {}
        context = context if isinstance(context, dict) else {}
        trace["input_refs"] = list(context.get("refs", []))
        trace["input_relationship"] = "CONTEXT_ONLY_NOT_CONDITION_EVIDENCE"
        trace["input_reasons"] = list(context.get("reasons", ["MISSING_SOURCE"]))
        trace["input_reasons"].append("NO_APPROVED_METRIC_PROVIDER_BINDING")
    result["photography_verdict"] = "NOT_EVALUABLE"
    result["recommendation_eligible"] = False
    return result
