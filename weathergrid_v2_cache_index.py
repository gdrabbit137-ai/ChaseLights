"""Static regional cache index for WeatherGrid V2.

Generated forecast payloads are time-sharded: the manifest advertises URL
templates keyed by valid time, so a browser pan fetches only visible cells for
the selected time instead of downloading an entire forecast per cell.
"""
from __future__ import annotations

import json
from pathlib import Path

REGIONS = {
    "tw": {
        "bbox": {"west": 119.5, "south": 21.5, "east": 123.5, "north": 26.5},
        "cell_deg": 2.0,
    },
    "jp": {
        "bbox": {"west": 122.0, "south": 24.0, "east": 146.0, "north": 46.0},
        "cell_deg": 2.0,
    },
    "us": {
        "bbox": {"west": -125.0, "south": 24.0, "east": -66.0, "north": 50.0},
        "cell_deg": 4.0,
    },
    "us_alaska": {
        "bbox": {"west": -170.0, "south": 51.0, "east": -129.0, "north": 72.0},
        "cell_deg": 4.0,
    },
}
JMA_DOMAIN = {"west": 120.0, "south": 22.4, "east": 150.0, "north": 47.6}
VALID_TOKEN = "{valid_time}"


def cells_for_region(region):
    spec = REGIONS[region]
    b = spec["bbox"]
    d = spec["cell_deg"]
    out = []
    y = b["south"]
    while y < b["north"] - 1e-9:
        x = b["west"]
        while x < b["east"] - 1e-9:
            e = min(x + d, b["east"])
            n = min(y + d, b["north"])
            cid = (
                f"{region}_{x:g}_{y:g}_{e:g}_{n:g}"
                .replace("-", "m")
                .replace(".", "p")
            )
            out.append(
                {
                    "id": cid,
                    "bbox": {"west": x, "south": y, "east": e, "north": n},
                }
            )
            x = e
        y = n
    return out


def _intersection(a, b):
    west = max(a["west"], b["west"])
    south = max(a["south"], b["south"])
    east = min(a["east"], b["east"])
    north = min(a["north"], b["north"])
    if west >= east or south >= north:
        return None
    return {"west": west, "south": south, "east": east, "north": north}


def _provider_template(provider, cid):
    return f"weathergrid/v2/{provider}/current/{VALID_TOKEN}/{cid}.json"


def build_index(*, provider_runs=None):
    regions = {}
    for name, spec in REGIONS.items():
        indexed = []
        for cell in cells_for_region(name):
            providers = {
                "gfs": {
                    "url_template": _provider_template("gfs", cell["id"]),
                    "time_sharded": True,
                    "coverage_bbox": cell["bbox"],
                }
            }
            jma_coverage = _intersection(cell["bbox"], JMA_DOMAIN)
            if jma_coverage:
                providers["jma"] = {
                    "url_template": _provider_template("jma", cell["id"]),
                    "time_sharded": True,
                    "coverage_bbox": jma_coverage,
                }
            indexed.append({**cell, "providers": providers})
        regions[name] = {**spec, "cells": indexed}
    return {
        "schema_version": 2,
        "mode": "static_regional_cache",
        "payload_partition": "valid_time",
        "valid_time_token": VALID_TOKEN,
        "provider_runs": provider_runs or {},
        "regions": regions,
    }


def write_index(path, *, provider_runs=None):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(
            build_index(provider_runs=provider_runs),
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    import argparse

    a = argparse.ArgumentParser()
    a.add_argument("--output", default="weathergrid/v2/index.json")
    ns = a.parse_args()
    write_index(ns.output)
