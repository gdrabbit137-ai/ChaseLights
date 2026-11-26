#!/usr/bin/env python3
"""CL-PHYS-03 replay recount — count what a before/after replay actually moved.

Usage:
    python packages/core-v2/tools/phys03_recount.py \
        --before /tmp/base/bundle.json \
        --after  /tmp/branch/bundle.json \
        [--after-details /tmp/branch/details]

Why this exists: the CL-PHYS-03 ticket quoted before/after totals from a 168 h
replay of the 2026-11-26 live bundle, but that replay (the provider artifact it
was built from) is not in the repository, so nobody can re-derive those numbers
from the code alone. This script does not reproduce the snapshot — it recounts
an artifact pair you produced yourself with the recipe in
packages/core-v2/tools/evaluate_batch.py (PHYS03_REPLAY_RECIPE). It prints only
counts it can derive from the files it was given, and explicitly lists the
questions it CANNOT answer from a published bundle, so a number is never
invented.

What is derivable from an evaluations bundle:
  * total good_hours labels (the published recommendation surface),
  * opportunities with at least one good_hour,
  * hour_counts sums (GUIDANCE_SATISFIED / UNFAVORABLE / NOT_EVALUABLE).

What is NOT derivable from the bundle alone (needs --after-details, and even
then only partially):
  * how many published recommendations sat on a white-wall hour (raw visibility
    < 2 km, or < 10 km with low cloud >= 90 %). The raw visibility cell is NOT
    part of the published bundle or the details rows unless the owner contract
    happens to carry a `visibility` condition, so this script reports it as
    undeterminable instead of guessing. Use the archived provider snapshot for
    that count.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def load_bundle(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def opportunities(bundle):
    for place in bundle.get("places") or []:
        for opportunity in place.get("opportunities") or []:
            yield opportunity


def recount(bundle):
    totals = Counter()
    with_good = 0
    for opportunity in opportunities(bundle):
        good = 0
        for day in opportunity.get("days") or []:
            good += len(day.get("good_hours") or [])
            for key, value in (day.get("hour_counts") or {}).items():
                totals[f"hour_counts.{key}"] += value
        totals["good_hours"] += good
        totals["opportunities"] += 1
        if good:
            with_good += 1
    totals["opportunities_with_good_hours"] = with_good
    return totals


def detail_summary(details_dir):
    """Per-day capped-hour labels, if the details artifact carries them."""
    if not details_dir:
        return None
    root = Path(details_dir)
    if not root.is_dir():
        return None
    summary = {"documents": 0, "opportunities": 0,
               "days_with_capped_hours": 0, "capped_hours": 0,
               "rows_missing_night_window_for_night_genres": None}
    for path in sorted(root.glob("*.json")):
        summary["documents"] += 1
        doc = json.loads(path.read_text(encoding="utf-8"))
        for opportunity in doc.get("opportunities") or []:
            summary["opportunities"] += 1
            for day in opportunity.get("days") or []:
                capped = day.get("capped_hours") or []
                if capped:
                    summary["days_with_capped_hours"] += 1
                    summary["capped_hours"] += len(capped)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--before", required=True, help="bundle.json of the baseline tree")
    parser.add_argument("--after", required=True, help="bundle.json of this branch")
    parser.add_argument("--after-details", default=None,
                        help="details dir of this branch (optional; adds capped-hour counts)")
    arguments = parser.parse_args(argv)

    before = recount(load_bundle(arguments.before))
    after = recount(load_bundle(arguments.after))
    keys = sorted(set(before) | set(after))
    report = {
        "before": {key: before.get(key, 0) for key in keys},
        "after": {key: after.get(key, 0) for key in keys},
        "delta": {key: after.get(key, 0) - before.get(key, 0) for key in keys},
        "not_derivable_from_bundle": [
            "white-wall recommendations remaining (raw visibility is not in the "
            "published bundle/details unless a contract carries a visibility "
            "condition) — recount from the archived provider snapshot",
            "how many of the removed good_hours were removed by which gate "
            "(the bundle keeps per-condition day verdicts, not per-hour gate "
            "attribution across all conditions)",
        ],
    }
    details = detail_summary(arguments.after_details)
    if details is not None:
        report["after_details"] = details
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
