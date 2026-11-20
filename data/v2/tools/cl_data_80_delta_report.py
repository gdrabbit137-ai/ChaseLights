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


def main(argv):
    old = index_bundle(json.loads(Path(argv[0]).read_text(encoding="utf-8")))
    new = index_bundle(json.loads(Path(argv[1]).read_text(encoding="utf-8")))
    lines = []
    elig_changed, graded = 0, {"recommend": 0, "good": 0, "marginal": 0}
    samples = []
    opps_both = set(old) & set(new)
    for oid in sorted(opps_both):
        o, n = old[oid]["days"], new[oid]["days"]
        for date in sorted(set(o) | set(n)):
            og, ng = o.get(date, {}).get("good", []), n.get(date, {}).get("good", [])
            if og != ng:
                elig_changed += 1
                lines.append(f"ELIGIBILITY-CHANGED {oid} {date}: "
                             f"old={len(og)}h new={len(ng)}h "
                             f"lost={sorted(set(og)-set(ng))} gained={sorted(set(ng)-set(og))}")
                continue
            v2map = n.get(date, {}).get("v2", {})
            for t in og:
                entry = v2map.get((t, None)) or next(
                    (h for (lt, _tier), h in v2map.items() if lt == t), None)
                if entry is None:
                    continue
                graded[entry["tier_v2"]] += 1
                if entry["tier_v2"] != "recommend" and len(samples) < 40:
                    samples.append((oid, date, t, entry["s_quality"],
                                    entry["tier_v2"]))
    srank = [(oid, v["s_rank"]) for oid, v in new.items()
             if v["s_rank"] is not None]
    lines[:0] = [
        "CL-DATA-80 verdict delta: legacy boolean bundle vs quality-engine v2 bundle",
        f"opportunities compared: {len(opps_both)}",
        f"ELIGIBILITY changes (good_hours sets): {elig_changed}",
        f"legacy-eligible hours graded by v2: "
        f"✓ recommend={graded['recommend']} ○ good={graded['good']} "
        f"✗ marginal={graded['marginal']}",
        f"opportunities carrying s_rank: {len(srank)} "
        f"(null elsewhere = no AGLI / no eligible hour)",
        "",
        "Sample of graded hours (max 40):",
    ]
    lines += [f"  {oid} {date} {t} S_quality={sq} tier={TIER_SYM[tier]}"
              for oid, date, t, sq, tier in samples]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(lines)} lines)")
    print("\n".join(lines[:8]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
