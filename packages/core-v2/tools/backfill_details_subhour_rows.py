#!/usr/bin/env python3
"""CL-INT-91 one-off backfill: add sub-hour details rows for sub-hour good_hours.

CL-DATA-31 made the summary stamp qualifying hour buckets at their earliest
passing sub-hour sample (good_hours like 17:25), but evaluations-details kept
only hourly bucket rows, so cl-ui-23's summary->details lookup missed every
sub-hour stamp (480 stamps / 105 places on the 2026-11-08 bundle). The writer
fix (same ticket) emits the extra row at the next regeneration; this script
backfills the PUBLISHED details files offline — recomputing the precise stamp
with the SAME astro_hourly.window_pass_profiles grid the evaluator used — so
bundle and details return to the same vintage without a full-catalog refetch.

Idempotent: a bucket that already carries its sub-hour row is skipped.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for p in ("packages/core-v2/tools", "packages/models-v2"):
    sys.path.insert(0, str(ROOT / p))

import astro_hourly as ah  # noqa: E402
import evaluate_batch as eb  # noqa: E402


def window_metrics_by_opportunity():
    """Window metrics the EVALUATOR saw per opportunity — the owner contract
    conditions PLUS the evaluation-layer time-window gate (eval_conditions_for),
    since CL-DATA-31 stamps precise stamps against that effective set."""
    metrics = {}
    for path in sorted((ROOT / "data/v2/opportunities").glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        for opp in doc if isinstance(doc, list) else [doc]:
            oid = opp.get("opportunity_id")
            contract = opp.get("condition_contract") or {}
            effective = eb.eval_conditions_for(contract)
            m = sorted({c["metric"] for c in effective
                        if c.get("metric") in eb.TIME_WINDOW_METRICS})
            if oid and m:
                metrics[oid] = m
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--details-dir",
                        default=str(ROOT / "apps/web-v2/evaluations-details"))
    parser.add_argument("--only-place-id", default=None)
    arguments = parser.parse_args()

    opp_metrics = window_metrics_by_opportunity()
    details_dir = Path(arguments.details_dir)
    touched = rows_added = 0
    for path in sorted(details_dir.glob("*.json")):
        if arguments.only_place_id and path.stem != arguments.only_place_id:
            continue
        detail = json.loads(path.read_text(encoding="utf-8"))
        lat, lon = detail["coordinate"]
        changed = False
        for opp in detail["opportunities"]:
            metrics = opp_metrics.get(opp["opportunity_id"])
            if not metrics:
                continue
            olat, olon = (opp.get("coordinate") or detail["coordinate"])
            events = None
            for day in opp["days"]:
                for row in day["hours"]:
                    if row["status"] != "GUIDANCE_SATISFIED":
                        continue
                    if row["local"].endswith(":00") is False:
                        continue  # already a sub-hour row
                    if any("sub_hour_of_bucket" in r
                           for r in day["hours"]
                           if r.get("sub_hour_of_bucket") == row["local"]):
                        continue  # idempotent re-run
                    at = datetime.fromisoformat(
                        row["utc"].replace("Z", "+00:00"))
                    if events is None:
                        epoch = at.timestamp()
                        events = ah.sun_events_span(olat, olon,
                                                    epoch - 86400 * 9,
                                                    epoch + 86400 * 9)
                    profiles = ah.window_pass_profiles(at, olat, olon,
                                                       events=events)
                    for i, off in enumerate(ah.WINDOW_SAMPLE_OFFSETS):
                        if all(profiles[m][i] for m in metrics):
                            if not off:
                                # window already passes at the bucket start:
                                # the hourly row keys the stamp; no extra row.
                                break
                            hh, mm = map(int, row["local"].split(":"))
                            precise_local = (
                                datetime(2000, 1, 1, hh, mm)
                                + timedelta(minutes=off)).strftime("%H:%M")
                            sub = dict(row)
                            sub["local"] = precise_local
                            sub["sub_hour_of_bucket"] = row["local"]
                            sub["sample_offset_min"] = off
                            day["hours"].append(sub)
                            changed = True
                            rows_added += 1
                            break
        if changed:
            for o in detail["opportunities"]:
                for d in o["days"]:
                    # chronological by local stamp; the sub-hour row of a
                    # bucket always sorts after its bucket row (off > 0).
                    d["hours"].sort(key=lambda r: r["local"])
            path.write_bytes(
                (json.dumps(detail, ensure_ascii=False, separators=(",", ":"))
                 + "\n").encode("utf-8").replace(b"\r\n", b"\n"))
            touched += 1
    print(f"backfilled {rows_added} sub-hour rows across {touched} detail files")


if __name__ == "__main__":
    main()
