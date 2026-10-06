#!/usr/bin/env python3
"""Calibrate CWA low-cloud RH diagnostics against time-matched Himawari-9.

This tool is intentionally conservative:
- clear Himawari cloud-mask pixels are negative examples;
- cloudy pixels with cloud-top height <= the configured low-cloud ceiling are
  positive examples;
- cloudy pixels whose top is above the low-cloud ceiling are ambiguous and
  excluded because a high cloud top cannot prove a lower deck is absent.

The latest observed CWA valid time is always held out from parameter fitting.
No production model is modified by this script.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from typing import Callable

from himawari9_cloud_poc import (
    BUCKET,
    TAIWAN_QC_BBOX,
    build_fs,
    fixed_grid_window,
    select_product_pair,
    slot_prefix,
)
from himawari9_weathergrid_browser_bundle import (
    MAX_NEAREST_DISTANCE_M,
    _read_source_arrays,
    nearest_regular_grid,
)

PRIMARY_LOW_CLOUD_TOP_M = 3700.0
BASELINE_FEATURE = "max_rh_925_850"
BASELINE_LOW_RH = 70.0
BASELINE_HIGH_RH = 95.0
CALIBRATION_VERSION = "cwa-low-cloud-calibration-v1"


@dataclass(frozen=True)
class Sample:
    slot_utc: str
    label: int
    rh925: float
    rh850: float
    rh2: float
    lcl_m: float
    wind_m_s: float

    @property
    def max_rh_925_850(self) -> float:
        return max(self.rh925, self.rh850)

    @property
    def min_rh_925_850(self) -> float:
        return min(self.rh925, self.rh850)

    @property
    def mean_rh_925_850(self) -> float:
        return (self.rh925 + self.rh850) / 2.0


FEATURES: dict[str, Callable[[Sample], float]] = {
    "max_rh_925_850": lambda item: item.max_rh_925_850,
    "min_rh_925_850": lambda item: item.min_rh_925_850,
    "mean_rh_925_850": lambda item: item.mean_rh_925_850,
}


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _decode_frame_field(bundle: dict, frame: dict, field_name: str) -> list[float | None]:
    meta = bundle["fields"][field_name]
    scale = float(meta.get("scale", 1.0))
    values = frame["values"][field_name]
    return [
        None if value is None else float(value) * scale
        for value in values
    ]


def _exact_himawari_pair(fs, valid_time: datetime) -> dict[str, str] | None:
    if valid_time.minute % 10:
        return None
    prefix = f"{BUCKET}/{slot_prefix(valid_time)}"
    try:
        paths = fs.ls(prefix, detail=False)
    except FileNotFoundError:
        return None
    return select_product_pair(paths)


def _build_labels(
    mask_values,
    height_values,
    *,
    low_cloud_top_m: float,
) -> list[int | None]:
    labels: list[int | None] = []
    for mask, height in zip(mask_values, height_values):
        if mask is None:
            labels.append(None)
            continue
        if int(mask) == 0:
            labels.append(0)
            continue
        if int(mask) == 1 and height is not None:
            top = float(height)
            if math.isfinite(top) and top <= low_cloud_top_m:
                labels.append(1)
                continue
        # Cloudy with a higher/failed cloud top is deliberately ambiguous.
        labels.append(None)
    return labels


def _frame_samples(
    bundle: dict,
    frame: dict,
    *,
    fs,
    low_cloud_top_m: float,
) -> tuple[list[Sample], dict] | None:
    valid_time = _parse_utc(frame["valid_time_utc"])
    pair = _exact_himawari_pair(fs, valid_time)
    if pair is None:
        return None

    grid = bundle["grid"]
    all_latitudes = [float(value) for value in grid["latitudes"]]
    all_longitudes = [float(value) for value in grid["longitudes"]]
    west, south, east, north = TAIWAN_QC_BBOX
    lat_indices = [
        index for index, value in enumerate(all_latitudes)
        if south <= value <= north
    ]
    lon_indices = [
        index for index, value in enumerate(all_longitudes)
        if west <= value <= east
    ]
    if not lat_indices or not lon_indices:
        raise RuntimeError(
            f"CWA grid does not overlap Himawari Taiwan calibration bbox: {TAIWAN_QC_BBOX}"
        )
    latitudes = [all_latitudes[index] for index in lat_indices]
    longitudes = [all_longitudes[index] for index in lon_indices]
    expected = len(latitudes) * len(longitudes)

    source_window = fixed_grid_window(TAIWAN_QC_BBOX)
    source = _read_source_arrays(fs, pair, source_window)
    mask, mask_distance = nearest_regular_grid(
        source["cloud_mask"]["lat"],
        source["cloud_mask"]["lon"],
        source["cloud_mask"]["values"],
        target_latitudes=latitudes,
        target_longitudes=longitudes,
        fill_value=source["cloud_mask"]["fill"],
    )
    height, height_distance = nearest_regular_grid(
        source["cloud_height"]["lat"],
        source["cloud_height"]["lon"],
        source["cloud_height"]["values"],
        target_latitudes=latitudes,
        target_longitudes=longitudes,
        fill_value=source["cloud_height"]["fill"],
    )
    if len(mask) != expected or len(height) != expected:
        raise RuntimeError("Himawari/CWA aligned grid length mismatch")
    if mask_distance["p99_m"] > MAX_NEAREST_DISTANCE_M:
        raise RuntimeError(f"cloud-mask alignment exceeds QC: {mask_distance}")
    if height_distance["p99_m"] > MAX_NEAREST_DISTANCE_M:
        raise RuntimeError(f"cloud-height alignment exceeds QC: {height_distance}")

    labels = _build_labels(mask, height, low_cloud_top_m=low_cloud_top_m)
    fields = {
        name: _decode_frame_field(bundle, frame, name)
        for name in (
            "relative_humidity_925hpa_percent",
            "relative_humidity_850hpa_percent",
            "relative_humidity_2m_percent",
            "lcl_height_m_agl",
            "wind_speed_10m_m_s",
        )
    }

    slot = valid_time.isoformat().replace("+00:00", "Z")
    samples: list[Sample] = []
    full_cols = len(all_longitudes)
    target_index = 0
    for source_row in lat_indices:
        for source_col in lon_indices:
            label = labels[target_index]
            target_index += 1
            if label is None:
                continue
            source_index = source_row * full_cols + source_col
            values = [fields[name][source_index] for name in fields]
            if any(value is None or not math.isfinite(float(value)) for value in values):
                continue
            samples.append(
                Sample(
                    slot_utc=slot,
                    label=int(label),
                    rh925=float(fields["relative_humidity_925hpa_percent"][source_index]),
                    rh850=float(fields["relative_humidity_850hpa_percent"][source_index]),
                    rh2=float(fields["relative_humidity_2m_percent"][source_index]),
                    lcl_m=float(fields["lcl_height_m_agl"][source_index]),
                    wind_m_s=float(fields["wind_speed_10m_m_s"][source_index]),
                )
            )

    positives = sum(item.label for item in samples)
    return samples, {
        "slot_utc": slot,
        "sample_count": len(samples),
        "calibration_bbox": {
            "west": west,
            "south": south,
            "east": east,
            "north": north,
        },
        "target_grid": {
            "rows": len(latitudes),
            "cols": len(longitudes),
            "cells": expected,
        },
        "positive_low_cloud": positives,
        "clear_negative": len(samples) - positives,
        "ambiguous_excluded": sum(label is None for label in labels),
        "cloud_mask_alignment": mask_distance,
        "cloud_height_alignment": height_distance,
        "source_products": pair,
    }


def _linear_probability(value: float, low_rh: float, high_rh: float) -> float:
    if high_rh <= low_rh:
        raise ValueError((low_rh, high_rh))
    return max(0.0, min(1.0, (float(value) - low_rh) / (high_rh - low_rh)))


def _auc(labels: list[int], scores: list[float]) -> float | None:
    positives = sum(labels)
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        return None

    ordered = sorted(zip(scores, labels), key=lambda item: item[0])
    positive_rank_sum = 0.0
    index = 0
    while index < len(ordered):
        stop = index + 1
        while stop < len(ordered) and ordered[stop][0] == ordered[index][0]:
            stop += 1
        average_rank = ((index + 1) + stop) / 2.0
        positive_rank_sum += average_rank * sum(
            label for _, label in ordered[index:stop]
        )
        index = stop
    return (
        positive_rank_sum - positives * (positives + 1) / 2.0
    ) / (positives * negatives)


def evaluate(
    samples: list[Sample],
    *,
    feature: str,
    low_rh: float,
    high_rh: float,
) -> dict:
    feature_fn = FEATURES[feature]
    labels = [item.label for item in samples]
    probabilities = [
        _linear_probability(feature_fn(item), low_rh, high_rh)
        for item in samples
    ]
    if not labels:
        raise ValueError("no calibration samples")

    brier = sum(
        (probability - label) ** 2
        for probability, label in zip(probabilities, labels)
    ) / len(labels)

    tp = tn = fp = fn = 0
    for probability, label in zip(probabilities, labels):
        predicted = probability >= 0.5
        if label == 1 and predicted:
            tp += 1
        elif label == 0 and not predicted:
            tn += 1
        elif label == 0 and predicted:
            fp += 1
        else:
            fn += 1

    sensitivity = tp / (tp + fn) if tp + fn else None
    specificity = tn / (tn + fp) if tn + fp else None
    balanced = (
        (sensitivity + specificity) / 2.0
        if sensitivity is not None and specificity is not None
        else None
    )
    auc = _auc(labels, probabilities)
    positives = sum(labels)

    return {
        "feature": feature,
        "low_rh": float(low_rh),
        "high_rh": float(high_rh),
        "sample_count": len(labels),
        "positive_count": positives,
        "negative_count": len(labels) - positives,
        "base_rate": round(positives / len(labels), 6),
        "brier": round(brier, 6),
        "auc": None if auc is None else round(auc, 6),
        "threshold_50": {
            "tp": tp,
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "sensitivity": None if sensitivity is None else round(sensitivity, 6),
            "specificity": None if specificity is None else round(specificity, 6),
            "balanced_accuracy": None if balanced is None else round(balanced, 6),
        },
    }


def fit_linear_candidate(samples: list[Sample]) -> dict:
    best = None
    for feature in FEATURES:
        for low_rh in range(55, 91):
            for high_rh in range(max(75, low_rh + 5), 101):
                metrics = evaluate(
                    samples,
                    feature=feature,
                    low_rh=low_rh,
                    high_rh=high_rh,
                )
                balanced = metrics["threshold_50"]["balanced_accuracy"]
                specificity = metrics["threshold_50"]["specificity"]
                key = (
                    -(
                        balanced
                        if balanced is not None
                        else -1.0
                    ),
                    metrics["brier"],
                    -(
                        specificity
                        if specificity is not None
                        else -1.0
                    ),
                    feature,
                    low_rh,
                    high_rh,
                )
                if best is None or key < best[0]:
                    best = (key, metrics)
    if best is None:
        raise RuntimeError("no candidate model")
    return best[1]


def _promotion_decision(
    *,
    observed_slots: int,
    minimum_slots: int,
    baseline_holdout: dict,
    candidate_holdout: dict,
) -> dict:
    baseline_t = baseline_holdout["threshold_50"]
    candidate_t = candidate_holdout["threshold_50"]
    improvements = {
        "brier_absolute": round(
            baseline_holdout["brier"] - candidate_holdout["brier"], 6
        ),
        "specificity_absolute": round(
            candidate_t["specificity"] - baseline_t["specificity"], 6
        ),
        "balanced_accuracy_absolute": round(
            candidate_t["balanced_accuracy"] - baseline_t["balanced_accuracy"], 6
        ),
        "sensitivity_absolute": round(
            candidate_t["sensitivity"] - baseline_t["sensitivity"], 6
        ),
    }
    gates = {
        "minimum_independent_slots": observed_slots >= minimum_slots,
        "brier_improves_by_0p02": improvements["brier_absolute"] >= 0.02,
        "specificity_improves_by_0p15": improvements["specificity_absolute"] >= 0.15,
        "balanced_accuracy_improves_by_0p05": (
            improvements["balanced_accuracy_absolute"] >= 0.05
        ),
        "sensitivity_at_least_0p50": candidate_t["sensitivity"] >= 0.50,
    }
    passed = all(gates.values())
    return {
        "status": "eligible_for_model_review" if passed else (
            "collect_more_independent_slots"
            if not gates["minimum_independent_slots"]
            else "keep_current_model"
        ),
        "automatic_production_change": False,
        "minimum_slots_for_review": minimum_slots,
        "observed_slots": observed_slots,
        "improvements": improvements,
        "gates": gates,
        "note": (
            "Passing this gate permits human/model review only; calibration never "
            "changes Photography Opportunity scoring automatically."
        ),
    }


def calibrate_bundle(
    bundle: dict,
    *,
    fs,
    now: datetime,
    low_cloud_top_m: float = PRIMARY_LOW_CLOUD_TOP_M,
    minimum_slots: int = 6,
) -> dict:
    required = {
        "relative_humidity_925hpa_percent",
        "relative_humidity_850hpa_percent",
        "relative_humidity_2m_percent",
        "lcl_height_m_agl",
        "wind_speed_10m_m_s",
    }
    missing = required - set(bundle.get("fields", {}))
    if missing:
        raise ValueError(f"CWA calibration bundle missing fields: {sorted(missing)}")

    observed: list[tuple[dict, list[Sample], dict]] = []
    skipped = []
    for frame in sorted(bundle.get("frames", []), key=lambda item: item["valid_time_utc"]):
        valid = _parse_utc(frame["valid_time_utc"])
        if valid > now:
            skipped.append({
                "valid_time_utc": frame["valid_time_utc"],
                "reason": "future_valid_time",
            })
            continue
        result = _frame_samples(
            bundle,
            frame,
            fs=fs,
            low_cloud_top_m=low_cloud_top_m,
        )
        if result is None:
            skipped.append({
                "valid_time_utc": frame["valid_time_utc"],
                "reason": "exact_himawari_pair_unavailable",
            })
            continue
        samples, qc = result
        if not samples or not qc["positive_low_cloud"] or not qc["clear_negative"]:
            skipped.append({
                "valid_time_utc": frame["valid_time_utc"],
                "reason": "insufficient_label_diversity",
            })
            continue
        observed.append((frame, samples, qc))

    if len(observed) < 2:
        return {
            "schema_version": 1,
            "calibration_version": CALIBRATION_VERSION,
            "status": "insufficient_time_holdout",
            "low_cloud_label_ceiling_m": low_cloud_top_m,
            "observed_slots": [item[2] for item in observed],
            "skipped_slots": skipped,
            "minimum_required_for_time_holdout": 2,
            "minimum_slots_for_model_review": minimum_slots,
            "automatic_production_change": False,
        }

    holdout_frame, holdout_samples, holdout_qc = observed[-1]
    train_groups = observed[:-1]
    train_samples = [
        sample
        for _, samples, _ in train_groups
        for sample in samples
    ]

    baseline_train = evaluate(
        train_samples,
        feature=BASELINE_FEATURE,
        low_rh=BASELINE_LOW_RH,
        high_rh=BASELINE_HIGH_RH,
    )
    baseline_holdout = evaluate(
        holdout_samples,
        feature=BASELINE_FEATURE,
        low_rh=BASELINE_LOW_RH,
        high_rh=BASELINE_HIGH_RH,
    )
    fitted = fit_linear_candidate(train_samples)
    candidate_holdout = evaluate(
        holdout_samples,
        feature=fitted["feature"],
        low_rh=fitted["low_rh"],
        high_rh=fitted["high_rh"],
    )

    per_slot = []
    for frame, samples, qc in observed:
        per_slot.append({
            **qc,
            "baseline": evaluate(
                samples,
                feature=BASELINE_FEATURE,
                low_rh=BASELINE_LOW_RH,
                high_rh=BASELINE_HIGH_RH,
            ),
            "candidate": evaluate(
                samples,
                feature=fitted["feature"],
                low_rh=fitted["low_rh"],
                high_rh=fitted["high_rh"],
            ),
            "role": (
                "time_holdout"
                if frame["valid_time_utc"] == holdout_frame["valid_time_utc"]
                else "calibration_train"
            ),
        })

    decision = _promotion_decision(
        observed_slots=len(observed),
        minimum_slots=minimum_slots,
        baseline_holdout=baseline_holdout,
        candidate_holdout=candidate_holdout,
    )
    return {
        "schema_version": 1,
        "calibration_version": CALIBRATION_VERSION,
        "status": "complete",
        "source_model": bundle.get("model"),
        "source_cycle": bundle.get("cycle"),
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "low_cloud_observation_label": {
            "positive": f"Himawari cloudy and cloud-top height <= {low_cloud_top_m:g} m",
            "negative": "Himawari cloud mask clear",
            "excluded": (
                "cloudy with cloud top above threshold or failed cloud-top retrieval"
            ),
            "semantic_guardrail": (
                "A high cloud top cannot prove lower cloud is absent; ambiguous cloudy "
                "pixels are excluded rather than mislabeled as no-low-cloud."
            ),
        },
        "time_split": {
            "training_slots": [item[2]["slot_utc"] for item in train_groups],
            "holdout_slot": holdout_qc["slot_utc"],
        },
        "baseline": {
            "feature": BASELINE_FEATURE,
            "low_rh": BASELINE_LOW_RH,
            "high_rh": BASELINE_HIGH_RH,
            "train": baseline_train,
            "holdout": baseline_holdout,
        },
        "candidate": {
            "selection_objective": "maximize_train_balanced_accuracy_then_minimize_brier",
            "feature": fitted["feature"],
            "low_rh": fitted["low_rh"],
            "high_rh": fitted["high_rh"],
            "train": fitted,
            "holdout": candidate_holdout,
        },
        "decision": decision,
        "slots": per_slot,
        "skipped_slots": skipped,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cwa-bundle",
        type=Path,
        default=Path("weathergrid/cwa_wrf3_tw_weather_browser.json"),
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--low-cloud-top-m", type=float, default=PRIMARY_LOW_CLOUD_TOP_M)
    parser.add_argument("--min-slots-for-promotion", type=int, default=6)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle = json.loads(args.cwa_bundle.read_text(encoding="utf-8"))
    report = calibrate_bundle(
        bundle,
        fs=build_fs(),
        now=datetime.now(timezone.utc),
        low_cloud_top_m=args.low_cloud_top_m,
        minimum_slots=args.min_slots_for_promotion,
    )
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    print(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    if report.get("status") == "insufficient_time_holdout":
        raise SystemExit(2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
