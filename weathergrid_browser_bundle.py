"""Build a compact browser bundle and QC report from B117 GFS WeatherGrid output.

This step does not fetch weather data. It consumes the already-decoded B117
frame JSON files and produces:

- gfs_tw_weather_browser.json
- gfs_tw_weather_qc.json

The browser bundle uses simple quantization metadata so the front end can load
several weather layers without parsing GRIB2 or carrying full float precision.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

FIELD_ENCODINGS = {
    "low_cloud_percent": {"unit": "%", "scale": 1.0, "min": 0.0, "max": 100.0},
    "mid_cloud_percent": {"unit": "%", "scale": 1.0, "min": 0.0, "max": 100.0},
    "high_cloud_percent": {"unit": "%", "scale": 1.0, "min": 0.0, "max": 100.0},
    "visibility_km": {"unit": "km", "scale": 0.1, "min": 0.0, "max": 100.0},
    "precip_rate_mm_h": {"unit": "mm/h", "scale": 0.01, "min": 0.0, "max": 500.0},
    "wind_speed_10m_m_s": {"unit": "m/s", "scale": 0.1, "min": 0.0, "max": 100.0},
    "wind_direction_10m_deg": {"unit": "degree", "scale": 1.0, "min": 0.0, "max": 359.0},
}


def _flatten(values):
    return [item for row in values for item in row]


def _finite_number(value) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def quantize(values, *, scale: float, minimum: float, maximum: float):
    encoded = []
    for value in _flatten(values):
        if not _finite_number(value):
            encoded.append(None)
            continue
        clipped = min(max(float(value), minimum), maximum)
        encoded.append(int(round(clipped / scale)))
    return encoded


def dequantize(encoded, scale: float):
    return [None if value is None else value * scale for value in encoded]


def field_stats(values: list[float | None]) -> dict:
    finite = [float(v) for v in values if _finite_number(v)]
    if not finite:
        return {
            "count": 0,
            "missing": len(values),
            "min": None,
            "max": None,
            "mean": None,
            "unique_rounded": 0,
            "range": None,
        }
    rounded = {round(v, 3) for v in finite}
    return {
        "count": len(finite),
        "missing": len(values) - len(finite),
        "min": round(min(finite), 4),
        "max": round(max(finite), 4),
        "mean": round(sum(finite) / len(finite), 4),
        "unique_rounded": len(rounded),
        "range": round(max(finite) - min(finite), 4),
    }


def qc_flags(field_name: str, stats: dict, values: list[float | None]) -> list[str]:
    flags = []
    if stats["missing"]:
        flags.append("missing_values")
    if stats["count"] and stats["range"] == 0:
        flags.append("constant_field")
    elif stats["count"] and stats["range"] is not None:
        threshold = 0.01 if field_name == "precip_rate_mm_h" else 0.1
        if stats["range"] <= threshold:
            flags.append("near_constant_field")

    finite = [float(v) for v in values if _finite_number(v)]
    if field_name == "visibility_km" and finite:
        peak = max(finite)
        share_at_peak = sum(abs(v - peak) <= 0.01 for v in finite) / len(finite)
        if share_at_peak >= 0.9:
            flags.append("visibility_ceiling_dominant")
    return flags


def _grid_signature(field: dict) -> tuple:
    return (
        tuple(round(float(v), 6) for v in field["latitudes"]),
        tuple(round(float(v), 6) for v in field["longitudes"]),
    )


def build_bundle(input_dir: Path) -> tuple[dict, dict]:
    manifest_path = input_dir / "gfs_tw_weather_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if not manifest.get("frames"):
        raise ValueError("manifest has no frames")

    frames_out = []
    qc_frames = []
    common_signature = None
    common_latitudes = None
    common_longitudes = None
    spots = None

    for frame_ref in manifest["frames"]:
        frame_path = input_dir / frame_ref["json"]
        frame = json.loads(frame_path.read_text(encoding="utf-8"))
        fields = frame["fields"]

        encoded_fields = {}
        qc_fields = {}

        for field_name, encoding in FIELD_ENCODINGS.items():
            if field_name not in fields:
                raise KeyError(f"missing required field {field_name} in {frame_path.name}")
            field = fields[field_name]
            signature = _grid_signature(field)
            if common_signature is None:
                common_signature = signature
                common_latitudes = field["latitudes"]
                common_longitudes = field["longitudes"]
            elif signature != common_signature:
                raise ValueError(
                    f"grid coordinates changed for {field_name} in {frame_path.name}"
                )

            raw_flat = _flatten(field["values"])
            stats = field_stats(raw_flat)
            flags = qc_flags(field_name, stats, raw_flat)
            encoded_fields[field_name] = quantize(
                field["values"],
                scale=encoding["scale"],
                minimum=encoding["min"],
                maximum=encoding["max"],
            )
            qc_fields[field_name] = {
                **stats,
                "flags": flags,
                "source_units": field["field_attrs"].get("source_units"),
                "normalized_units": field["field_attrs"].get("normalized_units"),
            }

        frame_spots = frame.get("spots", [])
        if spots is None:
            spots = [
                {
                    "spot_id": item["spot_id"],
                    "name": item["name"],
                    "lat": item["lat"],
                    "lon": item["lon"],
                }
                for item in frame_spots
            ]
        elif [s["spot_id"] for s in frame_spots] != [s["spot_id"] for s in spots]:
            raise ValueError(f"Place set/order changed in {frame_path.name}")

        run = frame["run"]
        frames_out.append({
            "forecast_hour": run["forecast_hour"],
            "valid_time_utc": run["valid_time_utc"],
            "values": encoded_fields,
        })
        qc_frames.append({
            "forecast_hour": run["forecast_hour"],
            "valid_time_utc": run["valid_time_utc"],
            "fields": qc_fields,
        })

    rows = len(common_latitudes)
    cols = len(common_longitudes)
    expected_cells = rows * cols
    for frame in frames_out:
        for key, encoded in frame["values"].items():
            if len(encoded) != expected_cells:
                raise ValueError(
                    f"{key} encoded cell count {len(encoded)} != {expected_cells}"
                )

    encoding_meta = {
        key: {
            "unit": meta["unit"],
            "encoding": "integer_scaled",
            "scale": meta["scale"],
            "decode": f"value * {meta['scale']}",
            "null": "missing",
        }
        for key, meta in FIELD_ENCODINGS.items()
    }

    bundle = {
        "schema_version": 1,
        "provider": manifest["provider"],
        "model": manifest["model"],
        "cycle": manifest["cycle"],
        "bbox": manifest["bbox"],
        "grid": {
            "rows": rows,
            "cols": cols,
            "latitudes": common_latitudes,
            "longitudes": common_longitudes,
        },
        "fields": encoding_meta,
        "frames": frames_out,
        "spots": spots or [],
    }

    all_flags = []
    for frame in qc_frames:
        for field_name, details in frame["fields"].items():
            for flag in details["flags"]:
                all_flags.append({
                    "forecast_hour": frame["forecast_hour"],
                    "field": field_name,
                    "flag": flag,
                })

    qc = {
        "schema_version": 1,
        "provider": manifest["provider"],
        "model": manifest["model"],
        "cycle": manifest["cycle"],
        "frame_count": len(frames_out),
        "grid_rows": rows,
        "grid_cols": cols,
        "spot_count": len(spots or []),
        "frames": qc_frames,
        "flags": all_flags,
        "notes": [
            "QC flags are diagnostics, not automatic rejection rules.",
            "GFS visibility can be capped/saturated over broad clear-air regions.",
            "Bilinear Place sampling remains separate from this grid bundle.",
        ],
    }
    return bundle, qc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default="gfs_multilayer_output")
    parser.add_argument("--output-dir", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir) if args.output_dir else input_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    bundle, qc = build_bundle(input_dir)
    bundle_path = output_dir / "gfs_tw_weather_browser.json"
    qc_path = output_dir / "gfs_tw_weather_qc.json"
    bundle_path.write_text(
        json.dumps(bundle, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    qc_path.write_text(
        json.dumps(qc, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps({
        "browser_bundle": str(bundle_path),
        "qc_report": str(qc_path),
        "frames": len(bundle["frames"]),
        "spots": len(bundle["spots"]),
        "grid": [bundle["grid"]["rows"], bundle["grid"]["cols"]],
        "flags": len(qc["flags"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
