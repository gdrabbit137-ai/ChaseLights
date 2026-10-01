"""Ingest NASA Black Marble VNP46A4 HDF5 tiles into WeatherGrid JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from viirs_nightlights_weathergrid import build_bundle

GROUP = "/HDFEOS/GRIDS/VIIRS_Grid_DNB_2d/Data Fields"
RADIANCE = "AllAngle_Composite_Snow_Free"
QUALITY = "AllAngle_Composite_Snow_Free_Quality"


def _attr_number(dataset, name, default):
    value = dataset.attrs.get(name, default)
    try:
        if hasattr(value, "item"):
            value = value.item()
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _decode(value, dataset):
    fill = dataset.attrs.get("_FillValue")
    if fill is not None:
        try:
            fill = fill.item()
        except AttributeError:
            pass
        if value == fill:
            return None
    scale = _attr_number(dataset, "scale_factor", 1.0)
    offset = _attr_number(dataset, "offset", 0.0)
    decoded = float(value) * scale + offset
    return decoded if decoded >= 0 else None


def read_tile(path, bbox, allow_empty=False):
    """Read/crop one VNP46A4 tile.

    bbox is (leftlon, bottomlat, rightlon, toplat).
    """
    try:
        import h5py
    except ImportError as exc:
        raise RuntimeError("h5py is required for VNP46A4 ingestion") from exc

    left, bottom, right, top = [float(v) for v in bbox]
    with h5py.File(path, "r") as h5:
        group = h5[GROUP]
        radiance_ds = group[RADIANCE]
        quality_ds = group[QUALITY]
        lats = [float(v) for v in group["lat"][:]]
        lons = [float(v) for v in group["lon"][:]]

        row_idx = [i for i, lat in enumerate(lats) if bottom <= lat <= top]
        col_idx = [i for i, lon in enumerate(lons) if left <= lon <= right]
        if not row_idx or not col_idx:
            if allow_empty:
                return None
            raise ValueError("requested bbox does not intersect VNP46A4 tile")

        out_lats = [lats[i] for i in row_idx]
        out_lons = [lons[i] for i in col_idx]
        values = []
        quality = []
        for ri in row_idx:
            for ci in col_idx:
                q = int(quality_ds[ri, ci])
                quality.append(q)
                values.append(_decode(radiance_ds[ri, ci], radiance_ds))

    return out_lats, out_lons, values, quality


def _coord(value):
    # 15 arc-second coordinates are deterministic, but rounding protects the
    # mosaic against harmless HDF floating-point representation differences.
    return round(float(value), 10)


def mosaic_tiles(tiles):
    """Merge cropped row-major tiles onto one regular lat/lon union grid."""
    cells = {}
    latitudes = set()
    longitudes = set()
    for lats, lons, values, quality in tiles:
        if len(values) != len(lats) * len(lons):
            raise ValueError("cropped tile cell count does not match coordinates")
        for row, lat in enumerate(lats):
            lat_key = _coord(lat)
            latitudes.add(lat_key)
            for col, lon in enumerate(lons):
                lon_key = _coord(lon)
                longitudes.add(lon_key)
                idx = row * len(lons) + col
                candidate = (values[idx], quality[idx])
                key = (lat_key, lon_key)
                if key in cells and cells[key] != candidate:
                    raise ValueError(f"conflicting VNP46A4 mosaic cell at {key}")
                cells[key] = candidate

    if not cells:
        raise ValueError("no VNP46A4 cells intersect requested bbox")

    out_lats = sorted(latitudes, reverse=True)
    out_lons = sorted(longitudes)
    out_values = []
    out_quality = []
    for lat in out_lats:
        for lon in out_lons:
            value, quality = cells.get((lat, lon), (None, 255))
            out_values.append(value)
            out_quality.append(quality)
    return out_lats, out_lons, out_values, out_quality


def ingest_many(paths, bbox, year):
    cropped = []
    used = []
    for path in paths:
        tile = read_tile(path, bbox, allow_empty=True)
        if tile is not None:
            cropped.append(tile)
            used.append(Path(path).name)
    lats, lons, values, quality = mosaic_tiles(cropped)
    bundle, qc = build_bundle(lats, lons, values, quality, year)
    bundle["provenance"]["source_tile_count"] = len(used)
    bundle["provenance"]["source_tiles"] = used
    qc["source_tile_count"] = len(used)
    qc["source_tiles"] = used
    return bundle, qc


def ingest(path, bbox, year):
    """Backward-compatible single-tile entry point."""
    return ingest_many([path], bbox, year)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-h5", required=True, action="append")
    parser.add_argument("--year", required=True, type=int)
    parser.add_argument(
        "--bbox",
        default="119.5,21.5,122.5,25.5",
        help="leftlon,bottomlat,rightlon,toplat",
    )
    parser.add_argument("--output", default="weathergrid/viirs_nightlights_tw_browser.json")
    parser.add_argument("--qc-output", default="weathergrid/viirs_nightlights_tw_qc.json")
    args = parser.parse_args()
    bbox = tuple(float(v) for v in args.bbox.split(","))
    if len(bbox) != 4:
        raise SystemExit("--bbox requires four comma-separated numbers")

    bundle, qc = ingest_many(args.input_h5, bbox, args.year)
    output = Path(args.output)
    qc_output = Path(args.qc_output)
    output.parent.mkdir(parents=True, exist_ok=True)
    qc_output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    qc_output.write_text(json.dumps(qc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "qc_output": str(qc_output),
        "rows": bundle["grid"]["rows"],
        "cols": bundle["grid"]["cols"],
        "source_tile_count": bundle["provenance"]["source_tile_count"],
        "year": args.year,
    }))


if __name__ == "__main__":
    main()
