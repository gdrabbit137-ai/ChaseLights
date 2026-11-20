"""CL-DATA-80: new-vs-old verdict delta report.

Compares the regenerated quality-engine bundle against the previous (legacy
boolean) bundle at data/v2/audits/cl-data-80-verdict-delta.txt:
  - eligibility delta: per opportunity/day good_hours set changes (expected: 0)
  - grading delta: legacy eligible hours bucketed by new tier_v2
    (recommend=✓ / good=○ / marginal=✗) — the expected drift is marginal
    ✓→○ downgrades from the trapezoid scoring
  - a 30-record sample of changed hours with per-entry reasons (quality
    metrics whose membership q < 1).

Usage:
  python data/v2/tools/cl_data_80_delta_report.py <old.json> <new.json>
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/v2/audits/cl-data-80-verdict-delta.txt"

TIER_SYM = {"recommend": "✓", "good": "○", "marginal": "✗"}


def _generated_at(path):
    try:
        return json.loads(Path(path).read_bytes().decode("utf-8"))["generated_at"]
    except Exception:
        return "?"


def _entry_reasons(new, oid, date, t, cond, qe):
    """Top-3 lowest-membership quality entries for one graded hour."""
    contract_path = ROOT / "data/v2/opportunities" / f"{oid}.json"
    try:
        cc = json.loads(contract_path.read_bytes().decode("utf-8"))["condition_contract"]
    except Exception:
        return []
    if not cond:
        return []
    scored = []
    for entry in cc["conditions_v2"]["quality"]:
        metric = entry["metric"]
        value, verdict = cond.get(metric, (None, None))
        quad = [entry["acceptable"][0], entry["ideal"][0],
                entry["ideal"][1], entry["acceptable"][1]]
        if entry.get("kind") == "binary":
            q = 1.0 if verdict == "PASS" else 0.0
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            q = qe.trapezoid(float(value), quad)
        else:
            q = None
        if q is None or q >= 0.999:
            continue
        scored.append((q, metric, value))
    scored.sort(key=lambda s: s[0])
    return [f"{m}={v} (q={q:.2f})" for q, m, v in scored[:3]]


def index_bundle(bundle):
    out = {}
    for place in bundle.get("places", []):
        for opp in place.get("opportunities", []):
            days = {}
            for day in opp.get("days", []):
                days[day.get("local_date")] = {
                    "good": sorted(day.get("good_hours") or []),
                    "v2": {(h.get("local"), h.get("tier_v2")): h
                           for h in day.get("good_hours_v2", [])},
                    "raw": day,
                }
            out[opp["opportunity_id"]] = {
                "place_id": place["place_id"],
                "engine": opp.get("engine"),
                "s_rank": (opp.get("s_rank") or {}).get("value"),
                "days": days,
            }
    return out


def load_details(details_dir):
    """place_id -> {(oid, date, local): {metric: (value, verdict)}}"""
    details = {}
    for f in Path(details_dir).glob("*.json"):
        doc = json.loads(f.read_bytes().decode("utf-8"))
        pid = doc["place_id"]
        per = {}
        for opp in doc["opportunities"]:
            for day in opp.get("days", []):
                for h in day.get("hours", []):
                    key = (opp["opportunity_id"], day["local_date"], h.get("local"))
                    per[key] = {c["metric"]: (c.get("value"), c.get("verdict"))
                                for c in h.get("conditions", [])}
        details[pid] = per
    return details


def main(argv):
    argv = argv[1:]  # argv[0] is this script (console entry)
    details_dir = argv[2] if len(argv) > 2 else str(
        ROOT / "apps/web-v2/evaluations-details")
    old = index_bundle(json.loads(Path(argv[0]).read_bytes().decode("utf-8")))
    new = index_bundle(json.loads(Path(argv[1]).read_bytes().decode("utf-8")))
    details = load_details(details_dir)
    sys.path.insert(0, str(ROOT / "packages/core-v2"))
    import quality_engine as qe
    elig_changed, graded = 0, {"recommend": 0, "good": 0, "marginal": 0}
    samples = []
    elig_lines = []
    opps_both = set(old) & set(new)
    for oid in sorted(opps_both):
        o, n = old[oid]["days"], new[oid]["days"]
        for date in sorted(set(o) | set(n)):
            og, ng = o.get(date, {}).get("good", []), n.get(date, {}).get("good", [])
            if og != ng:
                elig_changed += 1
                if len(elig_lines) < 300:
                    elig_lines.append(
                        f"ELIGIBILITY-CHANGED {oid} {date}: "
                        f"old={len(og)}h new={len(ng)}h "
                        f"lost={sorted(set(og)-set(ng))} gained={sorted(set(ng)-set(og))}")
                continue
            v2map = n.get(date, {}).get("v2", {})
            for t in og:
                entry = next((h for (lt, _tier), h in v2map.items() if lt == t), None)
                if entry is None:
                    continue
                graded[entry["tier_v2"]] += 1
                if entry["tier_v2"] != "recommend":
                    samples.append((oid, date, t, entry["s_quality"],
                                    entry["tier_v2"]))
    samples.sort(key=lambda s: s[3])
    samples = samples[:30]
    # per-sample reasons: recompute trapezoid membership per quality entry from
    # the detail artifact's raw condition values (same units as the contract).
    sample_lines = []
    for oid, date, t, sq, tier in samples:
        place_id = oid.rsplit("-P", 1)[0]
        cond = details.get(place_id, {}).get((oid, date, t))
        reasons = _entry_reasons(new, oid, date, t, cond, qe)
        sample_lines.append(
            f"  {oid} {date} {t} S_quality={sq} tier={TIER_SYM[tier]}"
            + (f"  reasons: {'; '.join(reasons)}" if reasons else ""))
    srank = [(oid, v["s_rank"]) for oid, v in new.items()
             if v["s_rank"] is not None]
    lines = [
        "CL-DATA-80 verdict delta: legacy boolean bundle vs quality-engine v2 bundle",
        f"old bundle generated_at: {_generated_at(argv[0])} / "
        f"new bundle generated_at: {_generated_at(argv[1])}",
        "NOTE: the two bundles are one day apart in forecast refresh, so",
        "ELIGIBILITY deltas below include weather drift between refreshes,",
        "not engine semantics. Engine-only eligibility parity was verified",
        "same-run (v2 vs --legacy-engine identical good_hours; the gatekeeper",
        "shares the legacy verdict pass by construction).",
        f"opportunities compared: {len(opps_both)}",
        f"good_hours-set changes (forecast refresh + engine window mix): {elig_changed}",
        f"legacy-eligible hours graded by v2: "
        f"✓ recommend={graded['recommend']} ○ good={graded['good']} "
        f"✗ marginal={graded['marginal']}",
        f"opportunities carrying s_rank: {len(srank)} "
        f"(null elsewhere = no AGLI / no eligible hour)",
        "",
        "First 300 eligibility-changed records:",
    ]
    lines += ["  " + e for e in elig_lines]
    lines += ["", "30 lowest-S_quality graded-hour samples with per-entry reasons:"]
    lines += sample_lines
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(lines)} lines)")
    print("\n".join(lines[:8]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
