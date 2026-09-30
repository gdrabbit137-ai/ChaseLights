"""Build compact browser/QC artifacts from ICON Global cloud frames."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from weathergrid_browser_bundle import field_stats, qc_flags, quantize


ICON_FIELD_ENCODINGS = {
    "low_cloud_percent": {
        "unit": "%",
        "scale": 1.0,
        "min": 0.0,
        "max": 100.0,
    },
    "mid_cloud_percent": {
        "unit": "%",
        "scale": 1.0,
        "min": 0.0,
        "max": 100.0,
    },
    "high_cloud_percent": {
        "unit": "%",
        "scale": 1.0,
        "min": 0.0,
        "max": 100.0,
    },
}


def _flatten(values):
    return [item for row in values for item in row]


def _grid_signature(field: dict) -> tuple:
    return (
        tuple(round(float(v), 6) for v in field["latitudes"]),
        tuple(round(float(v), 6) for v in field["longitudes"]),
    )


def build_icon_bundle(input_dir: Path) -> tuple[dict, dict]:
    manifest = json.loads(
        (input_dir / "icon_tw_cloud_manifest.json").read_text(encoding="utf-8")
    )
    if not manifest.get("frames"):
        raise ValueError("ICON manifest has no frames")

    common_signature = None
    common_latitudes = None
    common_longitudes = None
    frames_out = []
    qc_frames = []
    spots = None

    for ref in manifest["frames"]:
        frame = json.loads(
            (input_dir / ref["json"]).read_text(encoding="utf-8")
        )
        encoded_fields = {}
        qc_fields = {}

        for field_name, encoding in ICON_FIELD_ENCODINGS.items():
            field = frame["fields"][field_name]
            signature = _grid_signature(field)
            if common_signature is None:
                common_signature = signature
                common_latitudes = field["latitudes"]
                common_longitudes = field["longitudes"]
            elif signature != common_signature:
                raise ValueError(
                    f"ICON grid coordinates changed for "
                    f"{field_name} in {ref['json']}"
                )

            raw = _flatten(field["values"])
            stats = field_stats(raw)
            flags = qc_flags(field_name, stats, raw)
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
                "normalized_units": "%",
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
        elif [x["spot_id"] for x in frame_spots] != [
            x["spot_id"] for x in spots
        ]:
            raise ValueError(f"Place set/order changed in {ref['json']}")

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
    expected = rows * cols
    for frame in frames_out:
        for field_name, encoded in frame["values"].items():
            if len(encoded) != expected:
                raise ValueError(
                    f"{field_name} encoded cell count "
                    f"{len(encoded)} != {expected}"
                )

    fields_meta = {
        key: {
            "unit": meta["unit"],
            "encoding": "integer_scaled",
            "scale": meta["scale"],
            "decode": f"value * {meta['scale']}",
            "null": "missing",
        }
        for key, meta in ICON_FIELD_ENCODINGS.items()
    }

    bundle = {
        "schema_version": 2,
        "provider": manifest["provider"],
        "model": manifest["model"],
        "cycle": manifest["cycle"],
        "bbox": manifest["bbox"],
        "provenance": {
            "native_grid": manifest.get("native_grid"),
            "native_resolution_km": manifest.get("native_resolution_km"),
            "remap_grid_spacing_degrees": manifest.get(
                "remap_grid_spacing_degrees"
            ),
            "native_to_regular": "DWD_CDO_precomputed_weights",
            "browser_interpolation": "bilinear_subcell",
        },
        "grid": {
            "rows": rows,
            "cols": cols,
            "latitudes": common_latitudes,
            "longitudes": common_longitudes,
        },
        "fields": fields_meta,
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
        "native_resolution_km": manifest.get("native_resolution_km"),
        "remap_grid_spacing_degrees": manifest.get(
            "remap_grid_spacing_degrees"
        ),
        "frames": qc_frames,
        "flags": all_flags,
        "notes": [
            (
                "ICON native icosahedral cloud fields are remapped with "
                "DWD's official 0.125 degree CDO weights."
            ),
            (
                "Browser bilinear interpolation is presentation-only and "
                "does not increase model resolution."
            ),
            "QC flags are diagnostics, not automatic rejection rules.",
        ],
    }
    return bundle, qc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default="icon_cloud_output")
    parser.add_argument("--output-dir", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir) if args.output_dir else input_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    bundle, qc = build_icon_bundle(input_dir)
    bundle_path = output_dir / "icon_tw_cloud_browser.json"
    qc_path = output_dir / "icon_tw_cloud_qc.json"
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
