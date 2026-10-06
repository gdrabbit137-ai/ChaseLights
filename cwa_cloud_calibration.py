"""Calibrate the experimental CWA low-cloud proxy against Himawari observations.

The observed label is deliberately conservative:
- positive: Himawari cloud mask is cloudy AND retrieved cloud-top height is at
  or below LOW_CLOUD_TOP_MAX_M;
- negative: Himawari cloud mask is clear;
- ambiguous/excluded: cloudy pixels whose retrieved top is above the low-cloud
  threshold, because an upper cloud layer cannot prove that a lower deck is
  absent.

This module produces calibration evidence. It does not change production
Photography Opportunity scoring by itself.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path

LOW_CLOUD_TOP_MAX_M = 3700.0
MIN_TIME_MATCH_MINUTES = 1.0
CANDIDATE_FEATURES = (
    "rh_min",
    "rh_avg",
    "rh_avg_spread25",
    "rh_avg_spread50",
    "rh_avg_spread75",
)


def _utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"timestamp must be timezone-aware: {value}")
    return parsed.astimezone(timezone.utc)


def _decode(values, meta):
    scale = float(meta.get("scale", 1.0))
    return [None if value is None else float(value) * scale for value in values]


def _nearest_index(axis, value):
    if len(axis) < 2:
        return 0
    step = float(axis[1]) - float(axis[0])
    if step == 0:
        raise ValueError("grid axis step must be non-zero")
    index = int(round((float(value) - float(axis[0])) / step))
    return max(0, min(len(axis) - 1, index))


def _find_cwa_frame(cwa, observed_time):
    best = None
    best_delta = None
    for frame in cwa.get("frames", []):
        valid = _utc(frame["valid_time_utc"])
        delta = abs((valid - observed_time).total_seconds())
        if best_delta is None or delta < best_delta:
            best = frame
            best_delta = delta
    if best is None or best_delta is None:
        raise ValueError("CWA bundle has no frames")
    if best_delta > MIN_TIME_MATCH_MINUTES * 60:
        raise ValueError(
            f"no exact-enough CWA/Himawari time match: delta={best_delta / 60:.1f} min"
        )
    return best, best_delta


def collocate_snapshot(cwa, himawari, *, low_cloud_top_max_m=LOW_CLOUD_TOP_MAX_M):
    observed_time = _utc(himawari["observation"]["slot_utc"])
    frame, delta_seconds = _find_cwa_frame(cwa, observed_time)

    cwa_lats = [float(x) for x in cwa["grid"]["latitudes"]]
    cwa_lons = [float(x) for x in cwa["grid"]["longitudes"]]
    him_lats = [float(x) for x in himawari["grid"]["latitudes"]]
    him_lons = [float(x) for x in himawari["grid"]["longitudes"]]
    him_cols = int(himawari["grid"]["cols"])

    mask = himawari["values"]["observed_cloud_mask"]
    height = _decode(
        himawari["values"]["cloud_top_height_m"],
        himawari["fields"]["cloud_top_height_m"],
    )

    def field(name):
        if name not in frame.get("values", {}):
            raise ValueError(f"CWA frame missing field {name}")
        return _decode(frame["values"][name], cwa["fields"][name])

    rh925 = field("relative_humidity_925hpa_percent")
    rh850 = field("relative_humidity_850hpa_percent")
    rh2 = field("relative_humidity_2m_percent")
    lcl = field("lcl_height_m_agl")
    wind = field("wind_speed_10m_m_s")
    baseline = field("rh_cloud_potential_low_percent")

    rows = []
    positives = clear_negatives = ambiguous = 0
    for row, lat in enumerate(cwa_lats):
        if lat < him_lats[0] or lat > him_lats[-1]:
            continue
        hrow = _nearest_index(him_lats, lat)
        for col, lon in enumerate(cwa_lons):
            if lon < him_lons[0] or lon > him_lons[-1]:
                continue
            hcol = _nearest_index(him_lons, lon)
            hi = hrow * him_cols + hcol
            observed_mask = mask[hi]
            observed_height = height[hi]

            label = None
            if observed_mask == 0:
                label = 0
                clear_negatives += 1
            elif (
                observed_mask == 1
                and observed_height is not None
                and math.isfinite(observed_height)
                and observed_height <= low_cloud_top_max_m
            ):
                label = 1
                positives += 1
            else:
                ambiguous += 1
                continue

            ci = row * len(cwa_lons) + col
            values = (
                rh925[ci],
                rh850[ci],
                rh2[ci],
                lcl[ci],
                wind[ci],
                baseline[ci],
            )
            if any(value is None or not math.isfinite(float(value)) for value in values):
                continue

            low = min(float(rh925[ci]), float(rh850[ci]))
            high = max(float(rh925[ci]), float(rh850[ci]))
            average = (low + high) / 2.0
            spread = high - low
            rows.append(
                {
                    "y": label,
                    "lat": lat,
                    "lon": lon,
                    "rh925": float(rh925[ci]),
                    "rh850": float(rh850[ci]),
                    "rh_min": low,
                    "rh_max": high,
                    "rh_avg": average,
                    "rh_spread": spread,
                    "rh_avg_spread25": average - 0.25 * spread,
                    "rh_avg_spread50": average - 0.50 * spread,
                    "rh_avg_spread75": average - 0.75 * spread,
                    "rh2": float(rh2[ci]),
                    "lcl_m": float(lcl[ci]),
                    "wind_m_s": float(wind[ci]),
                    "baseline_potential": float(baseline[ci]),
                }
            )

    if not rows:
        raise ValueError("no unambiguous CWA/Himawari collocations")

    return {
        "slot_utc": observed_time.isoformat().replace("+00:00", "Z"),
        "cwa_valid_time_utc": frame["valid_time_utc"],
        "time_delta_seconds": delta_seconds,
        "label_policy": {
            "positive": f"cloudy and cloud_top_height_m <= {low_cloud_top_max_m:g}",
            "negative": "Himawari cloud mask clear",
            "excluded": "cloudy with higher/missing cloud top",
        },
        "label_counts": {
            "positive_low_cloud": positives,
            "negative_clear": clear_negatives,
            "ambiguous_excluded": ambiguous,
            "usable": len(rows),
        },
        "rows": rows,
    }


def _auc(rows, score_fn):
    ranked = sorted(
        ((float(score_fn(row)), int(row["y"])) for row in rows),
        key=lambda item: item[0],
    )
    positives = sum(label for _, label in ranked)
    negatives = len(ranked) - positives
    if not positives or not negatives:
        return None

    rank_sum = 0.0
    index = 0
    while index < len(ranked):
        end = index + 1
        while end < len(ranked) and ranked[end][0] == ranked[index][0]:
            end += 1
        average_rank = ((index + 1) + end) / 2.0
        rank_sum += average_rank * sum(label for _, label in ranked[index:end])
        index = end
    return (
        rank_sum - positives * (positives + 1) / 2.0
    ) / (positives * negatives)


def _metrics(rows, score_fn, *, threshold=50.0, include_auc=True):
    tp = tn = fp = fn = 0
    squared_error = 0.0
    for row in rows:
        score = max(0.0, min(100.0, float(score_fn(row))))
        observed = int(row["y"])
        predicted = int(score >= threshold)
        squared_error += (score / 100.0 - observed) ** 2
        if observed and predicted:
            tp += 1
        elif not observed and not predicted:
            tn += 1
        elif not observed and predicted:
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
    return {
        "n": len(rows),
        "positive": tp + fn,
        "negative": tn + fp,
        "brier": squared_error / len(rows),
        "auc": _auc(rows, score_fn) if include_auc else None,
        "threshold": threshold,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "balanced_accuracy": balanced,
        "confusion": {"tp": tp, "tn": tn, "fp": fp, "fn": fn},
    }


def _linear_score(feature, lower, upper):
    width = upper - lower
    if width <= 0:
        raise ValueError("upper RH endpoint must exceed lower endpoint")

    def score(row):
        return max(
            0.0,
            min(100.0, (float(row[feature]) - lower) / width * 100.0),
        )

    return score


def fit_linear_transfer(rows, feature):
    best = None
    for lower in range(60, 91):
        for upper in range(max(82, lower + 5), 101):
            score = _linear_score(feature, lower, upper)
            metrics = _metrics(rows, score, include_auc=False)
            candidate = {
                "feature": feature,
                "lower_rh_percent": lower,
                "upper_rh_percent": upper,
                "metrics": metrics,
            }
            if best is None:
                best = candidate
                continue
            left = (
                metrics["brier"],
                -(metrics["balanced_accuracy"] or 0.0),
                lower,
                upper,
            )
            right = (
                best["metrics"]["brier"],
                -(best["metrics"]["balanced_accuracy"] or 0.0),
                best["lower_rh_percent"],
                best["upper_rh_percent"],
            )
            if left < right:
                best = candidate
    return best


def _round_metrics(metrics):
    out = dict(metrics)
    for key in ("brier", "auc", "sensitivity", "specificity", "balanced_accuracy"):
        if out.get(key) is not None:
            out[key] = round(float(out[key]), 4)
    return out


def calibrate(cwa, himawari_bundles):
    snapshots = [
        collocate_snapshot(cwa, bundle)
        for bundle in sorted(
            himawari_bundles,
            key=lambda item: _utc(item["observation"]["slot_utc"]),
        )
    ]
    if len({item["slot_utc"] for item in snapshots}) != len(snapshots):
        raise ValueError("duplicate Himawari calibration slots")

    train_snapshots = snapshots[:-1] if len(snapshots) >= 2 else snapshots
    validation_snapshot = snapshots[-1] if len(snapshots) >= 2 else None
    train_rows = [row for item in train_snapshots for row in item["rows"]]

    baseline_fn = lambda row: row["baseline_potential"]
    candidates = [fit_linear_transfer(train_rows, feature) for feature in CANDIDATE_FEATURES]
    selected = min(
        candidates,
        key=lambda item: (
            item["metrics"]["brier"],
            -(item["metrics"]["balanced_accuracy"] or 0.0),
        ),
    )
    selected_fn = _linear_score(
        selected["feature"],
        selected["lower_rh_percent"],
        selected["upper_rh_percent"],
    )

    train_baseline = _metrics(train_rows, baseline_fn)
    train_candidate = _metrics(train_rows, selected_fn)
    validation = None
    validation_candidates = []
    promotion = {
        "eligible": False,
        "reason": "requires at least two exact-time snapshots",
    }
    if validation_snapshot is not None:
        validation_rows = validation_snapshot["rows"]
        validation_baseline = _metrics(validation_rows, baseline_fn)
        validation_candidate = _metrics(validation_rows, selected_fn)
        validation = {
            "slot_utc": validation_snapshot["slot_utc"],
            "baseline": _round_metrics(validation_baseline),
            "candidate": _round_metrics(validation_candidate),
        }
        for item in candidates:
            score_fn = _linear_score(
                item["feature"],
                item["lower_rh_percent"],
                item["upper_rh_percent"],
            )
            validation_candidates.append(
                {
                    "feature": item["feature"],
                    "transfer": {
                        "lower_rh_percent": item["lower_rh_percent"],
                        "upper_rh_percent": item["upper_rh_percent"],
                    },
                    "metrics": _round_metrics(_metrics(validation_rows, score_fn)),
                    "exploratory_only": item["feature"] != selected["feature"],
                }
            )

        brier_gain = validation_baseline["brier"] - validation_candidate["brier"]
        specificity_gain = (
            validation_candidate["specificity"] - validation_baseline["specificity"]
        )
        sensitivity_loss = (
            validation_baseline["sensitivity"] - validation_candidate["sensitivity"]
        )
        eligible = (
            brier_gain >= 0.015
            and specificity_gain >= 0.10
            and sensitivity_loss <= 0.20
            and (validation_candidate["auc"] or 0.0)
            >= (validation_baseline["auc"] or 0.0)
        )
        promotion = {
            "eligible": bool(eligible),
            "gate": {
                "minimum_brier_improvement": 0.015,
                "minimum_specificity_improvement": 0.10,
                "maximum_sensitivity_loss": 0.20,
                "auc_must_not_decrease": True,
            },
            "observed": {
                "brier_improvement": round(brier_gain, 4),
                "specificity_improvement": round(specificity_gain, 4),
                "sensitivity_loss": round(sensitivity_loss, 4),
                "auc_change": round(
                    (validation_candidate["auc"] or 0.0)
                    - (validation_baseline["auc"] or 0.0),
                    4,
                ),
            },
            "reason": (
                "candidate passes provisional two-slot promotion gate"
                if eligible
                else "candidate does not yet pass provisional two-slot promotion gate"
            ),
        }

    snapshot_summary = []
    for item in snapshots:
        rows = item["rows"]
        snapshot_summary.append(
            {
                "slot_utc": item["slot_utc"],
                "cwa_valid_time_utc": item["cwa_valid_time_utc"],
                "time_delta_seconds": item["time_delta_seconds"],
                "label_counts": item["label_counts"],
                "baseline": _round_metrics(_metrics(rows, baseline_fn)),
                "candidate": _round_metrics(_metrics(rows, selected_fn)),
            }
        )

    return {
        "schema_version": 1,
        "calibration_id": "cwa-low-cloud-himawari-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "semantics": {
            "product": "experimental CWA low-cloud presence potential",
            "observation": "Himawari-9 AHI cloud mask + cloud-top height",
            "not_native_cloud_fraction": True,
            "not_photography_opportunity_scoring": True,
        },
        "label_policy": snapshots[0]["label_policy"],
        "split": {
            "training_slots": [item["slot_utc"] for item in train_snapshots],
            "validation_slot": (
                validation_snapshot["slot_utc"] if validation_snapshot is not None else None
            ),
        },
        "baseline": {
            "feature": "max(rh925,rh850)",
            "transfer": {"lower_rh_percent": 70, "upper_rh_percent": 95},
            "training_metrics": _round_metrics(train_baseline),
        },
        "selected_candidate": {
            "feature": selected["feature"],
            "transfer": {
                "lower_rh_percent": selected["lower_rh_percent"],
                "upper_rh_percent": selected["upper_rh_percent"],
            },
            "training_metrics": _round_metrics(train_candidate),
        },
        "candidate_search": [
            {
                "feature": item["feature"],
                "transfer": {
                    "lower_rh_percent": item["lower_rh_percent"],
                    "upper_rh_percent": item["upper_rh_percent"],
                },
                "training_metrics": _round_metrics(item["metrics"]),
            }
            for item in candidates
        ],
        "validation": validation,
        "validation_candidates": validation_candidates,
        "promotion": promotion,
        "snapshots": snapshot_summary,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwa", type=Path, required=True)
    parser.add_argument(
        "--himawari",
        type=Path,
        action="append",
        required=True,
        help="Repeat for each exact-slot Himawari browser bundle.",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    cwa = json.loads(args.cwa.read_text(encoding="utf-8"))
    himawari = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in args.himawari
    ]
    report = calibrate(cwa, himawari)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    print(payload)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
