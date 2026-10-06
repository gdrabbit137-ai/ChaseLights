"""Persist compact CWA low-cloud calibration history.

The history intentionally stores metrics/labels only, never raw satellite pixels.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median

HISTORY_SCHEMA_VERSION = 1
DEFAULT_MAX_ENTRIES = 120
LONGITUDINAL_MIN_VALIDATION_SLOTS = 6


def compact_entry(report: dict) -> dict:
    split = report.get("split") or {}
    training_slots = list(split.get("training_slots") or [])
    validation_slot = split.get("validation_slot")
    if not training_slots or not validation_slot:
        raise ValueError("calibration report requires train/validation slots")

    pair_id = "__".join([*training_slots, str(validation_slot)])
    return {
        "pair_id": pair_id,
        "generated_at": report.get("generated_at"),
        "calibration_id": report.get("calibration_id"),
        "training_slots": training_slots,
        "validation_slot": validation_slot,
        "baseline": report.get("baseline"),
        "selected_candidate": report.get("selected_candidate"),
        "validation": report.get("validation"),
        "validation_candidates": report.get("validation_candidates") or [],
        "promotion": report.get("promotion"),
        "snapshots": report.get("snapshots") or [],
    }


def longitudinal_readiness(entries, *, minimum_slots=LONGITUDINAL_MIN_VALIDATION_SLOTS):
    if minimum_slots < 2:
        raise ValueError("minimum_slots must be >= 2")

    latest_by_slot = {}
    for entry in entries:
        slot = str(entry.get("validation_slot") or "")
        observed = (entry.get("promotion") or {}).get("observed") or {}
        required = (
            "brier_improvement",
            "specificity_improvement",
            "sensitivity_loss",
            "auc_change",
        )
        if not slot or any(key not in observed for key in required):
            continue
        previous = latest_by_slot.get(slot)
        if previous is None or str(entry.get("generated_at") or "") >= str(previous.get("generated_at") or ""):
            latest_by_slot[slot] = entry

    ordered = [latest_by_slot[key] for key in sorted(latest_by_slot)]
    window = ordered[-minimum_slots:]
    observed_slots = len(ordered)
    enough = observed_slots >= minimum_slots

    medians = None
    if window:
        medians = {
            key: round(
                median(float((entry["promotion"]["observed"])[key]) for entry in window),
                4,
            )
            for key in (
                "brier_improvement",
                "specificity_improvement",
                "sensitivity_loss",
                "auc_change",
            )
        }

    gates = {
        "minimum_distinct_validation_slots": enough,
        "median_brier_improvement_at_least_0p015": bool(
            medians and medians["brier_improvement"] >= 0.015
        ),
        "median_specificity_improvement_at_least_0p10": bool(
            medians and medians["specificity_improvement"] >= 0.10
        ),
        "median_sensitivity_loss_at_most_0p20": bool(
            medians and medians["sensitivity_loss"] <= 0.20
        ),
        "median_auc_change_nonnegative": bool(
            medians and medians["auc_change"] >= 0.0
        ),
    }
    eligible = all(gates.values())
    return {
        "status": (
            "eligible_for_model_review"
            if eligible
            else ("collect_more_validation_slots" if not enough else "longitudinal_metrics_not_stable")
        ),
        "eligible_for_model_review": eligible,
        "automatic_production_change": False,
        "minimum_distinct_validation_slots": minimum_slots,
        "observed_distinct_validation_slots": observed_slots,
        "window_validation_slots": [entry["validation_slot"] for entry in window],
        "median_improvements": medians,
        "candidate_features_in_window": [
            (entry.get("selected_candidate") or {}).get("feature")
            for entry in window
        ],
        "gates": gates,
        "note": (
            "Longitudinal readiness only permits model review; it never changes "
            "the production CWA proxy or Photography Opportunity scoring automatically."
        ),
    }


def update_history(existing: dict | None, report: dict, *, max_entries=DEFAULT_MAX_ENTRIES) -> dict:
    if max_entries < 1:
        raise ValueError("max_entries must be >= 1")
    payload = existing or {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "calibration_id": report.get("calibration_id"),
        "entries": [],
    }
    if payload.get("schema_version") != HISTORY_SCHEMA_VERSION:
        raise ValueError("unsupported calibration history schema")
    if payload.get("calibration_id") not in (None, report.get("calibration_id")):
        raise ValueError("calibration history id mismatch")

    entry = compact_entry(report)
    entries = [
        item for item in payload.get("entries", [])
        if item.get("pair_id") != entry["pair_id"]
    ]
    entries.append(entry)
    entries.sort(
        key=lambda item: (
            str(item.get("validation_slot") or ""),
            str(item.get("generated_at") or ""),
        )
    )
    entries = entries[-max_entries:]
    return {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "calibration_id": report.get("calibration_id"),
        "entries": entries,
        "review_readiness": longitudinal_readiness(entries),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--latest", type=Path, required=True)
    parser.add_argument("--max-entries", type=int, default=DEFAULT_MAX_ENTRIES)
    args = parser.parse_args()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    existing = None
    if args.history.exists():
        existing = json.loads(args.history.read_text(encoding="utf-8"))
    merged = update_history(existing, report, max_entries=args.max_entries)

    args.history.parent.mkdir(parents=True, exist_ok=True)
    args.history.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    args.latest.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "history_entries": len(merged["entries"]),
        "latest_validation_slot": report["split"]["validation_slot"],
        "promotion": report.get("promotion"),
        "review_readiness": merged.get("review_readiness"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
