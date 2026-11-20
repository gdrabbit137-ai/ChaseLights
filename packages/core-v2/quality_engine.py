"""CL-DATA-80 QUALITY scoring engine (spec: data/v2/audits/spec-quality-engine.md §4).

Pure functions, no network I/O, no weather/astronomy computation of its own — it
consumes the per-hour verdicts and observations the evaluate_batch loop already
computes for the legacy boolean path (the two paths share ONE verdict pass so a
dual-path divergence is structurally impossible).

Gatekeeper  G(t) = I(windows ∧ required): an hour is eligible only when every
REQUIRED condition (incl. the window metrics the migration folded into
windows.time_of_day) is PASS — i.e. exactly the legacy GUIDANCE_SATISFIED state.
If G(t)=0 the hour is eligible=false and S_quality(t)=0 (tier marginal).

Trapezoid membership  q_i(x) ∈ [0,1] with [a,b,c,d] (ideal [b,c], acceptable [a,d];
null bound = ±inf):
    x <= a or x >= d            -> 0
    a < x < b                   -> (x-a)/(b-a)
    b <= x <= c                 -> 1
    c < x < d                   -> (d-x)/(d-c)

S_quality(t) = 100 * Σ w_i·q_i / Σ w_i   (G=1 with no quality rules -> 75.0)
Tier: recommend (>=75) / good (45..<75) / marginal (<45 or ineligible).
S_rank(t) = AGLI^0.35 · S_quality(t)^0.65 (AGLI per place; None -> s_rank None).
"""

MOON_OVERRIDE_METRICS = {"moon_illumination_fraction", "moon_illuminance_proxy",
                         "moon_illumination"}
MOON_ALTITUDE_KEYS = ("moon_altitude_deg", "moon_altitude")


def trapezoid(x, quad):
    """q(x) for [a, b, c, d]; None bound = unbounded. x None/unknown -> None."""
    if x is None:
        return None
    a, b, c, d = quad
    if b is not None and c is not None and b <= x <= c:
        return 1.0
    if b is not None and c is None and x >= b:
        return 1.0
    if a is not None and x <= a:
        return 0.0
    if d is not None and x >= d:
        return 0.0
    if c is not None and d is not None and c < x < d:
        span = d - c
        return (d - x) / span if span > 0 else 1.0
    if a is not None and b is not None and a < x < b:
        span = b - a
        return (x - a) / span if span > 0 else 1.0
    return 1.0


def _numeric_value(metric, values, astro_row):
    cell = values.get(metric) if isinstance(values, dict) else None
    if isinstance(cell, dict) and cell.get("state") == "AVAILABLE":
        v = cell.get("value")
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return float(v)
    if isinstance(astro_row, dict):
        v = astro_row.get(metric)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return float(v)
    return None


def moon_down(astro_row):
    if not isinstance(astro_row, dict):
        return None
    for key in MOON_ALTITUDE_KEYS:
        v = astro_row.get(key)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return v < 0
    return None


def evaluate_hour(conditions_v2, states, values, astro_row, eligible):
    """Return {"eligible", "s_quality", "tier"} for one hour.

    `states` maps condition_id -> PASS/FAIL/UNKNOWN for the legacy verdicts of
    the SAME contract; `eligible` is the hour_status gatekeeper result (the
    windows+required AND over those verdicts).
    """
    quality = (conditions_v2 or {}).get("quality") or []
    if not eligible:
        return {"eligible": False, "s_quality": 0.0, "tier": "marginal"}
    if not quality:
        return {"eligible": True, "s_quality": 75.0, "tier": "recommend"}
    moon_down_ = moon_down(astro_row)
    total_w = 0.0
    acc = 0.0
    unknown = False
    for entry in quality:
        weight = entry.get("weight") or 1.0
        quad_a = entry.get("acceptable", [None, None])[0]
        quad_d = entry.get("acceptable", [None, None])[1]
        ideal = entry.get("ideal", [1, 1])
        quad = [quad_a, ideal[0], ideal[1], quad_d]
        metric = entry.get("metric")
        if entry.get("kind") == "binary":
            cid = entry.get("id")
            verdict = states.get(cid)
            if verdict == "UNKNOWN":
                q = None
            else:
                q = 1.0 if verdict == "PASS" else 0.0
        else:
            x = _numeric_value(metric, values, astro_row)
            q = trapezoid(x, quad) if x is not None else None
            if moon_down_ and metric in MOON_OVERRIDE_METRICS:
                q = 1.0  # spec §4: moon below horizon forces q_moon = 1.0
            elif q is None and moon_down_ and metric in MOON_OVERRIDE_METRICS:
                q = 1.0
        if q is None:
            unknown = True
            q = 0.5  # neutral midpoint; the hour stays honest via tier UNKNOWN flag
        acc += weight * q
        total_w += weight
    s = 100.0 * acc / total_w if total_w > 0 else 75.0
    tier = "recommend" if s >= 75 else ("good" if s >= 45 else "marginal")
    return {"eligible": True, "s_quality": round(s, 1),
            "tier": tier, "quality_unknown": unknown}


def s_rank(agli, s_quality):
    """AGLI^0.35 · S_quality^0.65, rounded to 1 decimal. agli None -> None."""
    if agli is None or s_quality is None:
        return None
    return round((float(agli) ** 0.35) * (max(0.0, float(s_quality)) ** 0.65), 1)
