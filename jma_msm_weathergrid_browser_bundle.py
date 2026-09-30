"""Build compact browser/QC artifacts from a JMA MSM cloud snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from weathergrid_browser_bundle import field_stats, qc_flags, quantize


JMA_FIELD_ENCODINGS = {
    "total_cloud_percent": {
        "unit": "%",
        "scale": 1.0,
        "min": 0.0,
        "max": 100.0,
    },
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


def build_jma_bundle(input_dir: Path) -> tuple[dict, dict]:
    raw_path = input_dir / "jma_msm_tw_cloud_raw.json"
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    if raw.get("model") != "JMA_MSM":
        raise ValueError(f"unexpected JMA model: {raw.get('model')}")
    frames = raw.get("frames") or []
    if not frames:
        raise ValueError("JMA MSM snapshot has no frames")

    grid = raw["grid"]
    rows = int(grid["rows"])
    cols = int(grid["cols"])
    expected = rows * cols

    fields_meta = {}
    for key, encoding in JMA_FIELD_ENCODINGS.items():
        raw_meta = raw.get("fields", {}).get(key)
        if not raw_meta:
            raise KeyError(f"JMA MSM snapshot missing field metadata: {key}")
        fields_meta[key] = {
            "unit": encoding["unit"],
            "encoding": "integer_scaled",
            "scale": encoding["scale"],
            "decode": f"value * {encoding['scale']}",
            "null": "missing",
            "vertical_definition": raw_meta.get("vertical_definition"),
        }

    frames_out = []
    qc_frames = []
    flags_out = []

    for frame in frames:
        encoded_fields = {}
        qc_fields = {}
        for field_name, encoding in JMA_FIELD_ENCODINGS.items():
            values = frame.get("values", {}).get(field_name)
            if values is None:
                raise KeyError(
                    f"JMA MSM frame missing field {field_name} at "
                    f"{frame.get('valid_time_utc')}"
                )
            if len(values) != expected:
                raise ValueError(
                    f"JMA MSM {field_name} cell count {len(values)} != {expected}"
                )

            stats = field_stats(values)
            flags = qc_flags(field_name, stats, values)
            encoded_fields[field_name] = quantize(
                [values],
                scale=encoding["scale"],
                minimum=encoding["min"],
                maximum=encoding["max"],
            )
            qc_fields[field_name] = {
                **stats,
                "flags": flags,
                "source_units": "%",
                "normalized_units": "%",
            }
            for flag in flags:
                flags_out.append(
                    {
                        "forecast_hour": frame["forecast_hour"],
                        "field": field_name,
                        "flag": flag,
                    }
                )

        frames_out.append(
            {
                "forecast_hour": frame["forecast_hour"],
                "valid_time_utc": frame["valid_time_utc"],
                "values": encoded_fields,
            }
        )
        qc_frames.append(
            {
                "forecast_hour": frame["forecast_hour"],
                "valid_time_utc": frame["valid_time_utc"],
                "fields": qc_fields,
            }
        )

    provenance = dict(raw.get("provenance") or {})
    provenance.update(
        {
            "browser_interpolation": "bilinear_subcell",
            "cloud_fields_native_to_jma_msm": True,
            "transport_adapter": raw.get("transport", {}).get("adapter"),
            "transport_cell_selection": raw.get("transport", {}).get(
                "cell_selection"
            ),
            "transport_elevation_downscaling": raw.get("transport", {}).get(
                "elevation_downscaling"
            ),
        }
    )

    bundle = {
        "schema_version": 2,
        "model_id": "jma_msm",
        "provider": raw["provider"],
        "model": raw["model"],
        "attribution": raw.get("attribution"),
        "cycle": raw.get("cycle"),
        "bbox": raw["bbox"],
        "native_domain": raw.get("native_domain"),
        "provenance": provenance,
        "grid": grid,
        "fields": fields_meta,
        "frames": frames_out,
        "spots": [],
    }

    qc = {
        "schema_version": 1,
        "model_id": "jma_msm",
        "provider": raw["provider"],
        "model": raw["model"],
        "cycle": raw.get("cycle"),
        "frame_count": len(frames_out),
        "grid_rows": rows,
        "grid_cols": cols,
        "fields": list(JMA_FIELD_ENCODINGS),
        "frames": qc_frames,
        "flags": flags_out,
        "notes": [
            (
                "JMA MSM total/low/mid/high cloud cover are native JMA "
                "surface GPV cloud fields exposed through the Open-Meteo "
                "JMA API transport adapter."
            ),
            (
                "Requests use nearest native model cell with elevation "
                "downscaling disabled."
            ),
            (
                "JMA cloud-layer pressure boundaries are model-specific and "
                "are stored in each field's vertical_definition metadata."
            ),
            (
                "Browser bilinear interpolation is presentation-only and "
                "does not increase the native ~5 km model resolution."
            ),
        ],
    }
    return bundle, qc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default="jma_msm_output")
    parser.add_argument("--output-dir", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir) if args.output_dir else input_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    bundle, qc = build_jma_bundle(input_dir)
    bundle_path = output_dir / "jma_msm_tw_cloud_browser.json"
    qc_path = output_dir / "jma_msm_tw_cloud_qc.json"
    bundle_path.write_text(
        json.dumps(bundle, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    qc_path.write_text(
        json.dumps(qc, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "browser_bundle": str(bundle_path),
                "qc_report": str(qc_path),
                "frames": len(bundle["frames"]),
                "grid": [bundle["grid"]["rows"], bundle["grid"]["cols"]],
                "fields": list(bundle["fields"]),
                "flags": len(qc["flags"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
