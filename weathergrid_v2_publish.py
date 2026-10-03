"""Publish browser-ready WeatherGrid V2 JMA native tiles.

The first static-site rollout intentionally supports a small regional working
set (Taiwan by default).  Each run resolves one JMA MSM model cycle, exports
valid-time-sharded cell payloads, writes a provider run manifest, and embeds
that run metadata into weathergrid/v2/index.json so the browser can select a
native valid time on first load.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from weathergrid_v2_cache_index import build_index, write_index
from weathergrid_v2_tile_export import (
    run_manifest,
    valid_time_token,
    write_frame_tile,
)


def _adapter_bbox(provider_spec: dict) -> dict[str, float]:
    b = provider_spec["coverage_bbox"]
    return {
        "leftlon": b["west"],
        "bottomlat": b["south"],
        "rightlon": b["east"],
        "toplat": b["north"],
    }


def _manifest_signature(manifest: dict) -> tuple:
    return (
        manifest["reference_time_utc"],
        manifest["nearest_valid_time_token"],
        tuple(x["token"] for x in manifest["valid_times"]),
        tuple(manifest["supported_fields"]),
    )


def publish_jma_regions(
    regions: list[str],
    output_root: str | Path,
    *,
    forecast_hours: int = 12,
    metadata: dict | None = None,
    fetcher=None,
    max_cells: int | None = None,
    selection_time_utc: str | datetime | None = None,
) -> dict:
    if forecast_hours < 1:
        raise ValueError("forecast_hours must be >= 1")
    index = build_index()
    unknown = [r for r in regions if r not in index["regions"]]
    if unknown:
        raise ValueError(f"unknown regions: {', '.join(unknown)}")

    if fetcher is None:
        from jma_msm_aws_om import fetch_aws_snapshot, fetch_best_metadata
        fetcher = fetch_aws_snapshot
        if metadata is None:
            metadata = fetch_best_metadata(forecast_hours=forecast_hours)
    elif metadata is None:
        raise ValueError("metadata is required when a custom fetcher is supplied")
    run_metadata = metadata
    if selection_time_utc is None:
        selection_time_utc = datetime.now(timezone.utc)
    root = Path(output_root)
    first_snapshot = None
    provider_manifest = None
    published_cells = []
    tile_count = 0

    candidates = []
    for region in regions:
        for cell in index["regions"][region]["cells"]:
            if "jma" in cell["providers"]:
                candidates.append((region, cell))
    if max_cells is not None:
        candidates = candidates[:max_cells]
    if not candidates:
        raise ValueError("selected regions contain no JMA native cells")

    for region, cell in candidates:
        snapshot = fetcher(
            bbox=_adapter_bbox(cell["providers"]["jma"]),
            forecast_hours=forecast_hours,
            metadata=run_metadata,
        )
        manifest = run_manifest(snapshot, target_time_utc=selection_time_utc)
        if provider_manifest is None:
            provider_manifest = manifest
            first_snapshot = snapshot
        elif _manifest_signature(manifest) != _manifest_signature(provider_manifest):
            raise RuntimeError(
                f"JMA cell {cell['id']} resolved a different run/valid-time set"
            )

        for frame_index, frame in enumerate(snapshot["frames"]):
            token = valid_time_token(frame["valid_time_utc"])
            output = root / "jma" / "current" / token / f"{cell['id']}.json"
            write_frame_tile(snapshot, output, frame_index)
            tile_count += 1
        published_cells.append({"region": region, "cell_id": cell["id"]})

    assert first_snapshot is not None
    assert provider_manifest is not None
    provider_manifest["published_regions"] = list(regions)
    provider_manifest["published_cell_ids"] = [
        item["cell_id"] for item in published_cells
    ]
    manifest_path = root / "jma" / "current" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(provider_manifest, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    write_index(root / "index.json", provider_runs={"jma": provider_manifest})

    return {
        "provider": "jma",
        "model": "JMA_MSM",
        "regions": regions,
        "reference_time_utc": provider_manifest["reference_time_utc"],
        "nearest_valid_time_utc": provider_manifest["nearest_valid_time_utc"],
        "valid_times": len(provider_manifest["valid_times"]),
        "cells": len(published_cells),
        "tiles": tile_count,
        "published_cells": published_cells,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--region",
        action="append",
        dest="regions",
        choices=("tw", "jp"),
        help="Region to publish; repeat for multiple regions. Defaults to tw.",
    )
    parser.add_argument("--forecast-hours", type=int, default=12)
    parser.add_argument("--output-root", default="weathergrid/v2")
    parser.add_argument("--max-cells", type=int)
    args = parser.parse_args()
    summary = publish_jma_regions(
        args.regions or ["tw"],
        args.output_root,
        forecast_hours=args.forecast_hours,
        max_cells=args.max_cells,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
