"""Ingest a NASA Black Marble VNP46A4 HDF5 tile into WeatherGrid JSON."""

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


def read_tile(path, bbox):
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
            raise ValueError("requested bbox does not intersect VNP46A4 tile")

        out_lats = [lats[i] for i in row_idx]
        out_lons = [lons[i] for i in col_idx]
        values = []
        quality = []
        for ri in row_idx:
            for ci in col_idx:
                q_raw = quality_ds[ri, ci]
                q = int(q_raw)
                quality.append(q)
                values.append(_decode(radiance_ds[ri, ci], radiance_ds))

    return out_lats, out_lons, values, quality


def ingest(path, bbox, year):
    lats, lons, values, quality = read_tile(path, bbox)
    return build_bundle(lats, lons, values, quality, year)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-h5", required=True)
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

    bundle, qc = ingest(args.input_h5, bbox, args.year)
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
        "year": args.year,
    }))


if __name__ == "__main__":
    main()
