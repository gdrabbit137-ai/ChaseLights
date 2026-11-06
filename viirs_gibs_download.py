"""Download daily NASA GIBS VIIRS DNB night-lights tiles (public WMTS).

CL-CI-20: the legacy LAADS VNP46A4 path is a DEAD END (product lifecycle
termination, see viirs_lads_download.py). The replacement main source is the
public NASA EOSDIS GIBS WMTS layer

    VIIRS_NOAA20_DayNightBand_At_Sensor_Radiance   (NOAA-20, primary)
    VIIRS_SNPP_DayNightBand_At_Sensor_Radiance     (Suomi NPP, historical only)

GIBS serves rendered daily DNB tiles with NO authentication. The tiles are the
raw daily product: they CONTAIN CLOUD CONTAMINATION and are NOT a cloud-free
composite. Per-pixel quality flags are not available from the rendered layer.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

GIBS_WMTS_BASE = "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best"
TILE_MATRIX_SET = "500m"
FORMAT_EXT = "png"

# Main source (owner ruling CL-CI-20): NOAA-20 DNB. SNPP layers survive on GIBS
# only as a historical archive (gaps; supply ended 2026-11-02 on GIBS and the
# LAADS SNPP supply terminated 2026-11-01).
LAYER_NOAA20 = "VIIRS_NOAA20_DayNightBand_At_Sensor_Radiance"
LAYER_SNPP_HISTORICAL = "VIIRS_SNPP_DayNightBand_At_Sensor_Radiance"
LAYERS = {"noaa20": LAYER_NOAA20, "snpp_historical": LAYER_SNPP_HISTORICAL}

# EPSG:4326 "500m" tile matrix set (GIBS WMTSCapabilities, verified 2026-11-07):
# level 7 is the native 500 m level (160x80 tiles, 2.25 deg per 512 px tile).
TILE_COLS_PER_LEVEL = [2, 3, 5, 10, 20, 40, 80, 160]
TILE_ROWS_PER_LEVEL = [1, 2, 3, 5, 10, 20, 40, 80]
DEFAULT_LEVEL = 6  # ~1 km/px display sampling; enough for the browser bundle

# WeatherGrid region bboxes (leftlon, bottomlat, rightlon, toplat).
REGION_BBOXES = {
    "tw": (119.5, 21.5, 122.5, 25.5),
    "jp": (122.0, 24.0, 146.0, 46.0),
    "us": (-125.0, 25.0, -70.5, 49.5),
    "ak": (-158.0, 55.0, -132.0, 69.5),
    "hi": (-160.3, 18.8, -154.8, 22.4),
}

USER_AGENT = "ChaseLights-VIIRS-GIBS/1.0"


def level_extent(level):
    """Return (cols_total, rows_total) for a 500m tile-matrix level."""
    if not 0 <= level < len(TILE_COLS_PER_LEVEL):
        raise ValueError(f"tile-matrix level out of range: {level}")
    return TILE_COLS_PER_LEVEL[level], TILE_ROWS_PER_LEVEL[level]


def tile_geometry(level, row, col):
    """Return (leftlon, bottomlat, rightlon, toplat) of one WMTS tile."""
    cols_total, rows_total = level_extent(level)
    if not (0 <= row < rows_total and 0 <= col < cols_total):
        raise ValueError(f"tile index out of range at level {level}: row={row} col={col}")
    lon_span = 360.0 / cols_total
    lat_span = 180.0 / rows_total
    left = -180.0 + col * lon_span
    top = 90.0 - row * lat_span
    return (left, top - lat_span, left + lon_span, top)


def tiles_for_bbox(level, bbox):
    """Return sorted (row, col) tile indices covering the bbox (inclusive)."""
    left, bottom, right, top = [float(v) for v in bbox]
    if not (-180 <= left < right <= 180 and -90 <= bottom < top <= 90):
        raise ValueError(f"invalid bbox: {bbox}")
    cols_total, rows_total = level_extent(level)
    lon_span = 360.0 / cols_total
    lat_span = 180.0 / rows_total
    col0 = int((left + 180.0) / lon_span)
    col1 = min(int((right + 180.0) / lon_span), cols_total - 1)
    row0 = int((90.0 - top) / lat_span)
    row1 = min(int((90.0 - bottom) / lat_span), rows_total - 1)
    return [(row, col) for row in range(row0, row1 + 1) for col in range(col0, col1 + 1)]


def tile_url(date, level, row, col, layer=LAYER_NOAA20):
    return (
        f"{GIBS_WMTS_BASE}/{layer}/default/{date}/"
        f"{TILE_MATRIX_SET}/{level}/{row}/{col}.{FORMAT_EXT}"
    )


def _fetch(url, dest, max_retries=4):
    """Download one tile with 429/5xx backoff; fail closed on any error."""
    last_error = None
    for attempt in range(max_retries):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = response.read()
            if payload[:8] != b"\x89PNG\r\n\x1a\n":
                raise ValueError(f"not a PNG tile: {url}")
            dest.write_bytes(payload)
            return len(payload)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as exc:
            last_error = exc
            status = getattr(exc, "code", None)
            if status is not None and status not in (429, 500, 502, 503, 504):
                break  # permanent failure (e.g. 404 = no data for that date)
            time.sleep(min(2 ** attempt * 2, 30))
    raise SystemExit(
        f"GIBS tile download failed after {max_retries} attempts: {url} ({last_error})"
    )


def download_tiles(date, level, bbox, output_dir, layer=LAYER_NOAA20):
    """Download all tiles covering bbox for date. Returns a manifest dict.

    Fail-closed: a missing/failing tile aborts the run (missing-data day must
    never produce a partial silent mosaic).
    """
    tiles = tiles_for_bbox(level, bbox)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for row, col in tiles:
        left, bottom, right, top = tile_geometry(level, row, col)
        dest = out_dir / f"tile_{level}_{row:03d}_{col:03d}.png"
        size = _fetch(tile_url(date, level, row, col, layer), dest)
        records.append(
            {
                "path": str(dest),
                "row": row,
                "col": col,
                "leftlon": left,
                "bottomlat": bottom,
                "rightlon": right,
                "toplat": top,
                "bytes": size,
            }
        )
    manifest = {
        "schema_version": "viirs-gibs-tiles-v1",
        "source_layer": layer,
        "observation_date": date,
        "tile_matrix_set": TILE_MATRIX_SET,
        "level": level,
        "native_resolution": "500 m (level 7); level {0} is coarser display sampling".format(level),
        "bbox": list(bbox),
        "tiles": records,
        "distribution": "NASA EOSDIS GIBS public WMTS (no authentication)",
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True, help="observation date YYYY-MM-DD")
    parser.add_argument("--region", choices=sorted(REGION_BBOXES), required=True)
    parser.add_argument("--bbox", default="", help="leftlon,bottomlat,rightlon,toplat override")
    parser.add_argument("--level", type=int, default=DEFAULT_LEVEL)
    parser.add_argument("--layer", choices=sorted(LAYERS), default="noaa20")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    bbox = REGION_BBOXES[args.region]
    if args.bbox:
        bbox = tuple(float(v) for v in args.bbox.split(","))
        if len(bbox) != 4:
            raise SystemExit("--bbox requires four comma-separated numbers")
    manifest = download_tiles(
        args.date, args.level, bbox, args.output_dir, layer=LAYERS[args.layer]
    )
    print(
        json.dumps(
            {
                "manifest": str(Path(args.output_dir) / "manifest.json"),
                "tiles": len(manifest["tiles"]),
                "source_layer": manifest["source_layer"],
                "observation_date": manifest["observation_date"],
                "level": args.level,
            }
        )
    )


if __name__ == "__main__":
    main()
