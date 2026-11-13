"""CL-UI-62: derived subject-card layer over evaluation bundles.

Builds, from an evaluation bundle, a per-place per-day derived summary:

    {suitable: [{subject_short: <trilingual genre short name>, window: [hour buckets]}],
     dominant_reason: <trilingual short weather word or null>,
     status: "clear" | "failed" | "not_evaluable"}

Inputs (committed, W2-owned):
  - data/v2/copy/genre_short_names.json  (genre_template -> short name, trilingual)
  - data/v2/copy/fail_reason_short.json  (metric -> short weather word, trilingual,
                                          + metric_priority + dominant_reason rule)

CLI:
  python data/v2/tools/build_subject_cards.py --latest            # newest bundle in data/v2/evaluations
  python data/v2/tools/build_subject_cards.py --bundle <path> --out <path>

Output is deterministic for a given bundle; bytes are LF on disk.

Dominant-reason rule (full text in fail_reason_short.json): each failed subject
casts one vote for its most core violated metric (FAIL conditions ranked by
metric_priority, then REQUIRED>QUALITY, MAIN>other tiers, then declaration
order; fallback REQUIRED+MAIN UNKNOWN, then PARTIAL with pass_hours=0);
highest vote count wins, ties break to earlier metric_priority then metric id.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COPY_DIR = ROOT / "data/v2/copy"
EVAL_DIR = ROOT / "data/v2/evaluations"

STATUS_CLEAR = "clear"
STATUS_FAILED = "failed"
STATUS_NOT_EVALUABLE = "not_evaluable"


def load_copy():
    genres = json.loads((COPY_DIR / "genre_short_names.json").read_bytes().decode("utf-8"))["genres"]
    fails = json.loads((COPY_DIR / "fail_reason_short.json").read_bytes().decode("utf-8"))
    return genres, fails


def _condition_sort_key(cond, priority_map):
    """Most-core-first sort key: priority, then role, then tier, then order."""
    role_rank = 0 if cond.get("role") == "REQUIRED" else 1
    tier_rank = 0 if cond.get("tier") == "MAIN" else 1
    return (priority_map.get(cond.get("metric"), len(priority_map)),
            role_rank, tier_rank, cond.get("_order", 0))


def _core_violation_metric(conds, priority_map):
    """One metric id (or None) = the subject's most core violated condition."""
    fails = [c for c in conds if c.get("day_verdict") == "FAIL"]
    pool = fails or [c for c in conds if c.get("day_verdict") == "UNKNOWN"
                     and c.get("role") == "REQUIRED" and c.get("tier") == "MAIN"]
    pool = pool or [c for c in conds if c.get("day_verdict") == "PARTIAL"
                    and c.get("pass_hours") == 0]
    if not pool:
        return None
    best = min(pool, key=lambda c: _condition_sort_key(c, priority_map))
    return best.get("metric")


def derive_place_days(bundle, genres, fails):
    """Return (derived subject-card tree, set of unknown metric/genre refs)."""
    priority = {m: i for i, m in enumerate(fails["metric_priority"])}
    unknown_metrics = set()

    def prio_index(metric):
        if metric not in priority:
            unknown_metrics.add(metric)
            return len(priority)
        return priority[metric]

    def short_word(metric):
        return fails["words"].get(metric)

    places_out = {}
    for place in bundle["places"]:
        place_id = place["place_id"]
        by_date = {}
        for opp in place["opportunities"]:
            genre = opp.get("genre_template")
            genre_short = genres.get(genre)
            for day in opp.get("days", []):
                date = day["local_date"]
                row = by_date.setdefault(date, {
                    "status": STATUS_CLEAR, "suitable": [], "votes": {}, "not_evaluable": 0})
                state = day.get("state")
                if state == "NOT_EVALUABLE":
                    row["not_evaluable"] += 1
                    row["status"] = STATUS_NOT_EVALUABLE
                    continue
                if state == "GUIDANCE_SATISFIED" and day.get("good_hours"):
                    if genre_short is None:
                        unknown_metrics.add("genre:%s" % genre)
                        continue
                    row["suitable"].append({
                        "subject_short": dict(genre_short),
                        "window": list(day["good_hours"]),
                    })
                elif state == "UNFAVORABLE":
                    row["status"] = STATUS_FAILED
                    conds = list(day.get("conditions", []))
                    for i, c in enumerate(conds):
                        c["_order"] = i
                    metric = _core_violation_metric(conds, priority)
                    if metric is not None:
                        row["votes"][metric] = row["votes"].get(metric, 0) + 1

        dates_out = {}
        for date in sorted(by_date):
            row = by_date[date]
            dominant = None
            best = None
            if row["votes"]:
                best = min(sorted(row["votes"]), key=lambda m: (-row["votes"][m], prio_index(m), m))
                dominant = short_word(best)
            dates_out[date] = {
                "status": row["status"],
                "suitable": row["suitable"],
                "dominant_metric": best if row["votes"] and dominant else None,
                "dominant_reason": dict(dominant) if dominant else None,
            }
        places_out[place_id] = dates_out

    return {
        "schema_version": "1.0",
        "ticket": "CL-UI-62",
        "layer": "subject_cards",
        "derived_from": {
            "source_bundle": Path(bundle["_source_path"]).name,
            "source_bundle_sha256": bundle["_source_sha256"],
            "generator": "data/v2/tools/build_subject_cards.py",
            "rule_version": fails["dominant_reason_rule"]["rule_version"],
        },
        "dictionaries": {"genre_short_names": genres, "fail_reason_short": fails["words"]},
        "places": places_out,
    }, unknown_metrics


def read_bundle(path):
    raw = Path(path).read_bytes()
    bundle = json.loads(raw.decode("utf-8"))
    bundle["_source_path"] = str(path)
    bundle["_source_sha256"] = hashlib.sha256(raw).hexdigest()
    return bundle


def latest_bundle_path():
    bundles = sorted(EVAL_DIR.glob("bundle-*.json"))
    if not bundles:
        raise FileNotFoundError("no evaluation bundles under %s" % EVAL_DIR)
    return bundles[-1]


def main(argv=None):
    ap = argparse.ArgumentParser(description="CL-UI-62: build the derived subject-card layer from an evaluation bundle.")
    ap.add_argument("--bundle", help="path to an evaluation bundle JSON")
    ap.add_argument("--latest", action="store_true", help="use newest bundle in data/v2/evaluations")
    ap.add_argument("--out", help="output path (default: stdout)")
    args = ap.parse_args(argv)

    if not args.bundle and not args.latest:
        ap.error("pass --bundle <path> or --latest")
    path = args.bundle or latest_bundle_path()

    genres, fails = load_copy()
    out, unknown = derive_place_days(read_bundle(path), genres, fails)
    if unknown:
        ap.exit(2, "FAIL: metrics/genres missing from the copy dictionaries: %s\n" % sorted(unknown))
    text = json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    if args.out:
        with open(args.out, "wb") as fh:
            fh.write(text.encode("utf-8"))
        print("wrote %s (%d places)" % (args.out, len(out["places"])))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
