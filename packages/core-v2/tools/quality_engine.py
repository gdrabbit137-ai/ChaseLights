"""CL-DATA-79 Phase 2 — QUALITY trapezoid membership scoring engine.

Implements spec-quality-engine.md §3 (rule JSON v2 schema) and §4
(Gatekeeper G(t) -> trapezoid membership q_i(x) -> weighted S_quality ->
recommend/good/marginal tiers). Reads the v2 quality-config rule files under
data/v2/templates/quality-configs/ — these coexist with the official
opportunity contracts: the official contract evaluation path is NOT touched
here (engine bypass; Phase 3 will switch the official contracts over).

Provenance: data/v2/audits/spec-quality-engine.md (owner-frozen 2026-11-20),
§5 weight/abcd tables, and the owner-ruled any_of moonlight gate for
astrophotography (§1.2). Reference prototype was Gemini's
spec-quality-engine-prototype-gemini.py — re-implemented locally
(fail-closed on unknown metrics, no external code merged).

Fail-closed rules:
- a required metric that is missing/None fails the gate (propagate_unknown).
- a quality metric that is missing/None scores q=0 (it cannot prove quality).
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

TIER_RECOMMEND_MIN = 75.0
TIER_GOOD_MIN = 45.0
NO_QUALITY_RULES_DEFAULT = 75.0
S_RANK_ALPHA = 0.35  # S_rank = AGLI^0.35 * S_quality^0.65 (spec §4.4)
MOON_OVERRIDE_TAG = "astrophotography"
MOON_OVERRIDE_METRIC = "moon_illumination"
MOON_GATE_METRIC = "moon_altitude_deg"

REQUIRED_KEYS = ("opportunity_id", "place_id", "tag", "windows", "conditions")


@dataclass
class ScoreBreakdownItem:
    metric: str
    raw_value: float
    membership_q: float
    weight: float
    weighted_score: float
    overridden: bool = False


@dataclass
class QualityScoreResult:
    opportunity_id: str
    place_id: str
    tag: str
    eligible: bool
    s_quality: float
    tier: str  # recommend / good / marginal / ineligible
    s_rank: float | None = None
    failed_reasons: list[str] = field(default_factory=list)
    breakdown: list[ScoreBreakdownItem] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Rule JSON v2 loading (spec §3)
# ---------------------------------------------------------------------------

def load_quality_rules(source: Any) -> list[dict[str, Any]]:
    """Load one/many v2 rule dicts from a path, JSON string, dict or list."""
    if isinstance(source, Path):
        data = json.loads(source.read_text(encoding="utf-8"))
    elif isinstance(source, str):
        stripped = source.strip()
        data = json.loads(stripped) if stripped.startswith(("{", "[")) else json.loads(
            Path(stripped).read_text(encoding="utf-8"))
    else:
        data = source
    rules = [data] if isinstance(data, dict) else list(data)
    for rule in rules:
        for key in REQUIRED_KEYS:
            if key not in rule:
                raise ValueError(
                    f"rule missing required key '{key}': {rule.get('opportunity_id', '<unknown>')}")
        conds = rule["conditions"]
        if "required" not in conds or "quality" not in conds:
            raise ValueError(f"rule '{rule['opportunity_id']}' conditions need 'required' and 'quality'")
    return rules


def load_quality_config_dir(config_dir: str | Path) -> dict[str, dict[str, Any]]:
    """Load every quality-config JSON in a dir, keyed by tag."""
    configs: dict[str, dict[str, Any]] = {}
    for path in sorted(Path(config_dir).glob("*.json")):
        cfg = json.loads(path.read_text(encoding="utf-8"))
        tag = cfg["tag"]
        if tag in configs:
            raise ValueError(f"duplicate quality-config tag '{tag}': {path.name}")
        configs[tag] = cfg
    return configs


# ---------------------------------------------------------------------------
# Gatekeeper G(t) = I(time_of_day ∧ seasonal ∧ required)  (spec §4.1)
# ---------------------------------------------------------------------------

def _date_in_seasonal_windows(target_date: date,
                              seasonal_windows: list[dict[str, str]] | None) -> bool:
    """null/absent seasonal = all year; supports cross-year (12-15 .. 02-25)."""
    if not seasonal_windows:
        return True
    target_md = (target_date.month, target_date.day)
    for window in seasonal_windows:
        s_m, s_d = (int(x) for x in window["start"].split("-"))
        e_m, e_d = (int(x) for x in window["end"].split("-"))
        start_md, end_md = (s_m, s_d), (e_m, e_d)
        if start_md <= end_md:
            if start_md <= target_md <= end_md:
                return True
        elif target_md >= start_md or target_md <= end_md:
            return True
    return False


def _eval_leaf(node: dict[str, Any], metrics: dict[str, Any]) -> tuple[bool, str]:
    metric = node["metric"]
    op = node["op"]
    if metric not in metrics or metrics[metric] is None:
        return False, f"missing_metric:{metric}"
    val = float(metrics[metric])
    if op == "lt":
        ok = val < float(node["value"])
    elif op == "lte":
        ok = val <= float(node["value"])
    elif op == "gt":
        ok = val > float(node["value"])
    elif op == "gte":
        ok = val >= float(node["value"])
    elif op == "eq":
        ok = val == float(node["value"])
    elif op == "between":
        low, high = (float(x) for x in node["range"])
        ok = low <= val <= high
    else:
        raise ValueError(f"unsupported operator: {op}")
    return ok, ("" if ok else f"failed:{metric}({val})_{op}_{node.get('value', node.get('range'))}")


def _eval_required_node(node: dict[str, Any], metrics: dict[str, Any]) -> tuple[bool, list[str]]:
    if "any_of" in node:
        sub: list[str] = []
        for child in node["any_of"]:
            ok, reasons = _eval_required_node(child, metrics)
            if ok:
                return True, []
            sub.extend(reasons)
        return False, [f"any_of_failed({' | '.join(sub)})"]
    if "all_of" in node:
        acc: list[str] = []
        for child in node["all_of"]:
            ok, reasons = _eval_required_node(child, metrics)
            if not ok:
                acc.extend(reasons)
        return len(acc) == 0, acc
    ok, reason = _eval_leaf(node, metrics)
    return ok, ([] if ok else [reason])


def evaluate_gatekeeper(rule: dict[str, Any], metrics: dict[str, Any],
                        active_time_windows: set[str], target_date: date) -> tuple[bool, list[str]]:
    """Hard gate: time_of_day ∧ seasonal ∧ all required conditions."""
    reasons: list[str] = []
    allowed_tods = set(rule["windows"].get("time_of_day") or [])
    if allowed_tods and not (allowed_tods & set(active_time_windows)):
        reasons.append(
            f"time_of_day_mismatch:need={sorted(allowed_tods)},got={sorted(active_time_windows)}")
    if not _date_in_seasonal_windows(target_date, rule["windows"].get("seasonal")):
        reasons.append(f"seasonal_closed:{target_date.isoformat()}")
    for req_node in rule["conditions"].get("required") or []:
        ok, sub = _eval_required_node(req_node, metrics)
        if not ok:
            reasons.extend(sub)
    return len(reasons) == 0, reasons


# ---------------------------------------------------------------------------
# Trapezoid membership q_i(x)  (spec §4.2)
# ---------------------------------------------------------------------------

def _bound(val: Any, default: float) -> float:
    if val is None:
        return default
    if isinstance(val, str) and val.lower() in ("inf", "+inf", "infinity"):
        return math.inf
    return float(val)


def normalize_abcd(q_rule: dict[str, Any]) -> tuple[float, float, float, float]:
    """Accept 'abcd': [a,b,c,d] or the split form ideal:[b,c] + acceptable:[a,d]."""
    if "abcd" in q_rule:
        raw = q_rule["abcd"]
        return (_bound(raw[0], -math.inf), _bound(raw[1], -math.inf),
                _bound(raw[2], math.inf), _bound(raw[3], math.inf))
    ideal, acceptable = q_rule["ideal"], q_rule["acceptable"]
    return (_bound(acceptable[0], -math.inf), _bound(ideal[0], -math.inf),
            _bound(ideal[1], math.inf), _bound(acceptable[1], math.inf))


def trapezoid_membership(x: float, a: float, b: float, c: float, d: float) -> float:
    """q_i(x) ∈ [0,1]; [b,c] is ideal, [a,d] acceptable. Left-shoulder [0,0,c,d]
    and right-shoulder [a,b,inf,inf] shapes supported."""
    if not (a <= b <= c <= d):
        raise ValueError(f"abcd must satisfy a<=b<=c<=d, got [{a}, {b}, {c}, {d}]")
    if b <= x <= c:
        return 1.0
    if x <= a or x >= d:
        return 0.0
    if a < x < b:
        return (x - a) / (b - a)
    return (d - x) / (d - c)  # c < x < d


# ---------------------------------------------------------------------------
# Weighted S_quality, tiers, S_rank  (spec §4.3-4.4)
# ---------------------------------------------------------------------------

def classify_tier(s_quality: float, eligible: bool) -> str:
    if not eligible:
        return "ineligible"
    if s_quality >= TIER_RECOMMEND_MIN:
        return "recommend"
    if s_quality >= TIER_GOOD_MIN:
        return "good"
    return "marginal"


def score_opportunity(rule: dict[str, Any], metrics: dict[str, Any],
                      active_time_windows: set[str], target_date: date,
                      agli_score: float | None = None) -> QualityScoreResult:
    """Score one v2 rule at time t. G(t)=0 -> eligible=False, S_quality=0."""
    base = dict(opportunity_id=rule["opportunity_id"], place_id=rule["place_id"], tag=rule["tag"])
    eligible, failed = evaluate_gatekeeper(rule, metrics, active_time_windows, target_date)
    if not eligible:
        return QualityScoreResult(eligible=False, s_quality=0.0, tier="ineligible",
                                  s_rank=(0.0 if agli_score is not None else None),
                                  failed_reasons=failed, **base)

    quality_rules = rule["conditions"].get("quality") or []
    breakdown: list[ScoreBreakdownItem] = []
    if not quality_rules:
        # G(t)=1 with no quality rules -> spec §4.3 default baseline 75.0
        s_quality = NO_QUALITY_RULES_DEFAULT
    else:
        weighted_sum = total_weight = 0.0
        for q_rule in quality_rules:
            metric = q_rule["metric"]
            weight = float(q_rule["weight"])
            overridden = False
            if "bonus_window" in q_rule and metric not in metrics:
                raw = 1.0 if q_rule["bonus_window"] in set(active_time_windows) else 0.0
            elif metric not in metrics or metrics[metric] is None:
                raw = 0.0  # missing quality metric cannot prove quality (fail-low)
            else:
                raw = float(metrics[metric])
            if (rule["tag"] == MOON_OVERRIDE_TAG and metric == MOON_OVERRIDE_METRIC
                    and metrics.get(MOON_GATE_METRIC) is not None
                    and float(metrics[MOON_GATE_METRIC]) < 0.0):
                # spec §4.2 月光覆寫: moon below horizon -> moonlight penalty is 0
                q_val, overridden = 1.0, True
            else:
                q_val = trapezoid_membership(raw, *normalize_abcd(q_rule))
            weighted_sum += weight * q_val
            total_weight += weight
            breakdown.append(ScoreBreakdownItem(
                metric=metric, raw_value=raw, membership_q=round(q_val, 6), weight=weight,
                weighted_score=round(weight * q_val, 6), overridden=overridden))
        s_quality = round(100.0 * weighted_sum / total_weight, 2) if total_weight > 0 else NO_QUALITY_RULES_DEFAULT

    tier = classify_tier(s_quality, True)
    s_rank = None
    if agli_score is not None:
        s_rank = round((float(agli_score) ** S_RANK_ALPHA) * (s_quality ** (1.0 - S_RANK_ALPHA)), 2)
    return QualityScoreResult(eligible=True, s_quality=s_quality, tier=tier,
                              s_rank=s_rank, breakdown=breakdown, **base)


def score_config_tag(tag: str, configs: dict[str, dict[str, Any]], metrics: dict[str, Any],
                     active_time_windows: set[str], target_date: date,
                     agli_score: float | None = None, seasonal: list | None = None) -> QualityScoreResult:
    """Convenience: instantiate a genre template config for a concrete
    opportunity (fills opportunity_id/place_id and optional per-place seasonal
    windows) and score it."""
    if tag not in configs:
        raise KeyError(f"unknown quality-config tag: {tag}")
    cfg = configs[tag]
    rule = json.loads(json.dumps(cfg))  # deep copy
    rule["windows"]["seasonal"] = seasonal if seasonal is not None else rule["windows"].get("seasonal")
    return score_opportunity(rule, metrics, active_time_windows, target_date, agli_score)
