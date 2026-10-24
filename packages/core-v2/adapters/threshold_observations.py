"""Deterministic threshold-to-boolean observation bridge (read-only).

Turns numeric RAW_ONLY pilot-artifact cells into the pre-evaluated boolean
observations that ``core_v2.evaluator`` consumes. The bridge itself performs
no validation of thresholds: conditions marked ``unvalidated``/``provisional``
or with non-AUTO modes are never observed, so the conservative evaluator
propagates UNKNOWN exactly as its contract requires. No network I/O.
"""
from __future__ import annotations

import math

OPERATORS = ("gt", "gte", "lt", "lte", "eq", "neq", "between", "in", "not_in",
             "is_true", "is_false", "none")
METRIC_FIELDS = {
    "temperature_2m": "temperature_2m",
    "dew_point_2m": "dew_point_2m",
    "relative_humidity_2m": "relative_humidity_2m",
    "cloud_cover_low": "cloud_cover_low",
    "cloud_cover_mid": "cloud_cover_mid",
    "cloud_cover_high": "cloud_cover_high",
    "wind_speed_10m": "wind_speed_10m",
    "visibility": "visibility",
    "precipitation": "precipitation",
    "precipitation_probability": "precipitation_probability",
    # Genre-template metrics (specs/v2/GENRE_CONDITION_TEMPLATES.md).
    # Registered ahead of the data landing so contract metric names are
    # stable; rows that do not carry the field yet resolve to UNKNOWN /
    # NOT_EVALUABLE, never to a fabricated comparison.
    "relative_humidity_925hpa": "relative_humidity_925hpa",
    "relative_humidity_850hpa": "relative_humidity_850hpa",
    "lcl_height_m_agl": "lcl_height_m_agl",
    "aod_550nm": "aod_550nm",
    "temperature_delta_850_925_c": "temperature_delta_850_925_c",
    "wind_speed_850hpa": "wind_speed_850hpa",
    "cloud_cover_total": "cloud_cover_total",
    "cloud_cover_mid_and_high": "cloud_cover_mid_and_high",
}


class BridgeFailure(ValueError):
    """Raised for structurally invalid inputs; never silently coerced."""


def _numeric(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BridgeFailure("NON_NUMERIC_THRESHOLD")
    if not math.isfinite(value):
        raise BridgeFailure("NON_FINITE_THRESHOLD")
    return float(value)


def comparable(condition):
    """Return (metric_field, operator, threshold) for an observable condition.

    Only AUTO-mode numeric-threshold conditions over supported pilot metrics
    are comparable; everything else returns None (evaluator then reports
    UNKNOWN for it, never a fabricated boolean).
    """
    if not isinstance(condition, dict):
        raise BridgeFailure("INVALID_CONDITION")
    if condition.get("evaluation_mode") != "AUTO":
        return None
    if condition.get("validation_status") != "validated":
        return None
    if condition.get("unknown_policy") != "propagate_unknown":
        raise BridgeFailure("INVALID_UNKNOWN_POLICY")
    metric = condition.get("metric")
    if not isinstance(metric, str) or metric not in METRIC_FIELDS:
        return None
    operator = condition.get("operator")
    if operator not in OPERATORS:
        raise BridgeFailure("INVALID_OPERATOR")
    threshold = condition.get("threshold")
    if operator in ("is_true", "is_false", "none"):
        return metric, operator, threshold
    if operator in ("between", "in", "not_in"):
        if not isinstance(threshold, list) or len(threshold) != 2:
            raise BridgeFailure("INVALID_THRESHOLD_SHAPE")
        return metric, operator, [_numeric(threshold[0]), _numeric(threshold[1])]
    return metric, operator, _numeric(threshold)


def compare(value, operator, threshold):
    if operator == "gt":
        return value > threshold
    if operator == "gte":
        return value >= threshold
    if operator == "lt":
        return value < threshold
    if operator == "lte":
        return value <= threshold
    if operator == "eq":
        return value == threshold
    if operator == "neq":
        return value != threshold
    if operator == "between":
        return threshold[0] <= value <= threshold[1]
    raise BridgeFailure("UNSUPPORTED_OPERATOR_FOR_NUMERIC")


def cell_observation(condition, cell, *, at_iso, provider, source, issued_at,
                     freshness, unit_expected=None):
    """Build one evaluator-ready observation from a single artifact cell."""
    if not isinstance(cell, dict) or cell.get("state") != "AVAILABLE":
        return {"value": None, "state": "UNKNOWN", "reason": "CELL_NOT_AVAILABLE"}
    value = cell.get("value")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return {"value": None, "state": "UNKNOWN", "reason": "CELL_VALUE_INVALID"}
    if unit_expected is not None and cell.get("unit") != unit_expected:
        return {"value": None, "state": "UNKNOWN", "reason": "CELL_UNIT_MISMATCH"}
    metric, operator, threshold = comparable(condition)
    if operator in ("is_true", "is_false", "none"):
        return {"value": None, "state": "UNKNOWN", "reason": "NON_NUMERIC_OPERATOR"}
    boolean = compare(float(value), operator, threshold)
    return {"value": boolean, "state": "PASS" if boolean else "FAIL",
            "provider": provider, "source": source, "issued_at": issued_at,
            "valid_at": at_iso, "freshness": freshness, "test_only": True}
