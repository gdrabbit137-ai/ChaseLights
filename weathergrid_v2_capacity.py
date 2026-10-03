"""WeatherGrid V2 valid-time tile and viewport working-set budget.

V2 transfers only the cells intersecting the viewport/prefetch ring for one
selected valid time.  Publication/storage may retain several valid times, but
browser transfer estimates must not multiply by the whole forecast horizon.

JMA calibration comes from the 2026-10-03 native benchmark: a 2°x2° cell
(41 x 33 = 1,353 grid points, four cloud fields) exported to 26,392 bytes of
compact JSON for one valid time.
"""
from __future__ import annotations

import math

MIB = 1024 * 1024
PROVIDERS = {
    "jma": {"dx": 0.0625, "dy": 0.05, "fields": 4},
    "gfs": {"dx": 0.25, "dy": 0.25, "fields": 7},
}
JMA_BENCHMARK_GRIDPOINTS = 41 * 33
JMA_BENCHMARK_TILE_BYTES = 26392
DEFAULT_REFRESH_BUDGET_MIB = 150.0
DEFAULT_VIEWPORT_BUDGET_MIB = 1.0


def _shape(provider, bbox):
    p = PROVIDERS[provider]
    cols = math.floor((bbox["east"] - bbox["west"]) / p["dx"] + 1e-9) + 1
    rows = math.floor((bbox["north"] - bbox["south"]) / p["dy"] + 1e-9) + 1
    return rows, cols


def estimate_cell(provider, bbox, json_multiplier=2.5):
    """Estimate one cell for one valid time (not an entire forecast run)."""
    p = PROVIDERS[provider]
    rows, cols = _shape(provider, bbox)
    gridpoints = rows * cols
    values = gridpoints * p["fields"]
    raw = values * 4
    if provider == "jma":
        estimated = math.ceil(
            gridpoints * JMA_BENCHMARK_TILE_BYTES / JMA_BENCHMARK_GRIDPOINTS
        )
        calibration = "measured_jma_2deg_valid_time_tile"
    else:
        estimated = math.ceil(raw * json_multiplier)
        calibration = "raw_float32_x_compact_json_multiplier"
    return {
        "provider": provider,
        "rows": rows,
        "cols": cols,
        "fields": p["fields"],
        "valid_times": 1,
        "gridpoints": gridpoints,
        "values": values,
        "raw_float32_bytes": raw,
        "estimated_compact_json_bytes": estimated,
        "calibration": calibration,
    }


def estimate_working_set(provider, cells, *, valid_times_loaded=1, measured_bytes=None):
    """Estimate browser transfer for the supplied viewport/prefetch cells."""
    if valid_times_loaded < 1:
        raise ValueError("valid_times_loaded must be >= 1")
    estimates = [estimate_cell(provider, c["bbox"]) for c in cells]
    one_time = 0
    for cell, estimate in zip(cells, estimates):
        one_time += (
            measured_bytes.get(cell["id"], estimate["estimated_compact_json_bytes"])
            if measured_bytes is not None
            else estimate["estimated_compact_json_bytes"]
        )
    total = one_time * valid_times_loaded
    return {
        "provider": provider,
        "cell_count": len(cells),
        "valid_times_loaded": valid_times_loaded,
        "estimated_transfer_bytes": total,
        "estimated_transfer_mib": round(total / MIB, 3),
        "within_default_viewport_budget": total <= DEFAULT_VIEWPORT_BUDGET_MIB * MIB,
    }


def estimate_region(provider, cells, measured_bytes=None, *, valid_times_published=1):
    """Estimate storage generated for a regional publication."""
    working = estimate_working_set(
        provider,
        cells,
        valid_times_loaded=valid_times_published,
        measured_bytes=measured_bytes,
    )
    total = working["estimated_transfer_bytes"]
    return {
        "provider": provider,
        "cell_count": len(cells),
        "valid_times_published": valid_times_published,
        "estimated_refresh_bytes": total,
        "estimated_refresh_mib": round(total / MIB, 2),
        "within_default_budget": total <= DEFAULT_REFRESH_BUDGET_MIB * MIB,
    }


def recommend_storage(region_estimates):
    total = sum(x["estimated_refresh_bytes"] for x in region_estimates)
    return {
        "estimated_refresh_mib": round(total / MIB, 2),
        "publish_generated_cells_to_git": False,
        "preferred": "deployment/object storage",
        "reason": "ephemeral generated forecast grids should not accumulate in Git history",
    }
