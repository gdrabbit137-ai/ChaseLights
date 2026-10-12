"""Conservative V2.1 condition-contract evaluator (test-only, no network I/O).

This module consumes *pre-evaluated boolean* observations. It never computes
weather/astronomy thresholds, verifies geographic facts, or recommends live use.
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
             "evaluation_mode": mode, "state": "UNKNOWN", "reason": ""}
    if mode != "AUTO":
        trace["reason"] = "NON_AUTO_MODE"
        return trace
    if condition.get("unknown_policy") != "propagate_unknown":
        trace["reason"] = "INVALID_UNKNOWN_POLICY"
        return trace
    if condition.get("validation_status") != "validated":
        trace["reason"] = "UNVALIDATED_CONDITION"
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
    for condition in conditions:
        if (not isinstance(condition, dict) or
                not isinstance(condition.get("id"), str) or not condition["id"] or
                condition["id"] in seen or condition.get("role") not in ROLES or
                condition.get("evaluation_mode") not in MODES):
            return {"decision": "UNKNOWN", "reasons": ["INVALID_CONTRACT_CONDITION"],
                    "unknown": True, "live_recommendation": False, "conditions": [], "axes": {}}
        seen.add(condition["id"])
        traces.append(_observe(condition, observations, at))
    axes = {role: {mode: {state: 0 for state in ("PASS", "FAIL", "UNKNOWN")}
                   for mode in MODES} for role in ROLES}
    for trace in traces:
        axes[trace["role"]][trace["evaluation_mode"]][trace["state"]] += 1
    blocking = any((t["role"] == "REQUIRED" and t["state"] == "FAIL") or
                   (t["role"] == "BLOCKER" and t["state"] == "PASS") for t in traces)
    critical_unknown = any(t["role"] in ("REQUIRED", "BLOCKER") and
                           t["state"] == "UNKNOWN" for t in traces)
    # An all-QUALITY contract must not generate a favorable result.
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
            "conditions": traces, "axes": axes}
