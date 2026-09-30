"""Build compact browser/QC artifacts from JMA MSM native cloud frames."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from weathergrid_browser_bundle import field_stats, qc_flags, quantize


FIELD_ENCODINGS = {
    "total_cloud_percent": {"unit": "%", "scale": 1.0, "min": 0.0, "max": 100.0},
    "low_cloud_percent": {"unit": "%", "scale": 1.0, "min": 0.0, "max": 100.0},
    "mid_cloud_percent": {"unit": "%", "scale": 1.0, "min": 0.0, "max": 100.0},
    "high_cloud_percent": {"unit": "%", "scale": 1.0, "min": 0.0, "max": 100.0},
}


def _flatten(values):
    return [item for row in values for item in row]


def _grid_signature(field: dict) -> tuple:
    return (
        tuple(round(float(v), 6) for v in field["latitudes"]),
        tuple(round(float(v), 6) for v in field["longitudes"]),
    )


def build_jma_bundle(input_dir: Path) -> tuple[dict, dict]:
    manifest = json.loads(
        (input_dir / "jma_msm_tw_cloud_manifest.json").read_text(encoding="utf-8")
    )
    refs = manifest.get("frames", [])
    if not refs:
        raise ValueError("JMA MSM manifest has no frames")

    source_frames = [
        json.loads((input_dir / ref["json"]).read_text(encoding="utf-8"))
        for ref in refs
    ]

    common_signature = None
    latitudes = None
    longitudes = None
    spots = None
    frames_out = []
    qc_frames = []

    for ref, frame in zip(refs, source_frames):
        encoded_fields = {}
        qc_fields = {}
        for field_name, encoding in FIELD_ENCODINGS.items():
            field = frame["fields"].get(field_name)
            if field is None:
                raise KeyError(
                    f"missing required JMA field {field_name} in {ref['json']}"
                )
            signature = _grid_signature(field)
            if common_signature is None:
                common_signature = signature
                latitudes = field["latitudes"]
                longitudes = field["longitudes"]
            elif signature != common_signature:
                raise ValueError(
                    f"JMA grid coordinates changed for {field_name} "
                    f"in {ref['json']}"
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

    rows = len(latitudes)
    cols = len(longitudes)
    expected = rows * cols
    for frame in frames_out:
        for key, values in frame["values"].items():
            if len(values) != expected:
                raise ValueError(
                    f"JMA {key} encoded cell count {len(values)} != {expected}"
                )

    fields_meta = {}
    for key, meta in FIELD_ENCODINGS.items():
        entry = {
            "unit": meta["unit"],
            "encoding": "integer_scaled",
            "scale": meta["scale"],
            "decode": f"value * {meta['scale']}",
            "null": "missing",
        }
        if key in manifest.get("cloud_vertical_definitions", {}):
            entry["vertical_definition"] = manifest[
                "cloud_vertical_definitions"
            ][key]
        fields_meta[key] = entry

    published_steps = [
        int(b["forecast_hour"]) - int(a["forecast_hour"])
        for a, b in zip(frames_out, frames_out[1:])
    ]
    published_step = (
        published_steps[0]
        if published_steps and all(v == published_steps[0] for v in published_steps)
        else None
    )

    bundle = {
        "schema_version": 2,
        "model_id": "jma_msm",
        "provider": manifest["provider"],
        "transport": manifest["transport"],
        "transport_license": manifest["transport_license"],
        "model": manifest["model"],
        "cycle": manifest["cycle"],
        "bbox": manifest["bbox"],
        "provenance": {
            "native_domain": manifest["native_domain"],
            "native_resolution_km": manifest["native_resolution_km"],
            "native_time_interval_hours": manifest["native_time_interval_hours"],
            "update_interval_hours": manifest["update_interval_hours"],
            "max_forecast_hour": manifest["max_forecast_hour"],
            "published_time_interval_hours": published_step,
            "native_grid": "regular_latlon",
            "browser_interpolation": "bilinear_subcell",
            "native_cloud_fields": [
                "cloud_cover",
                "cloud_cover_low",
                "cloud_cover_mid",
                "cloud_cover_high",
            ],
        },
        "grid": {
            "rows": rows,
            "cols": cols,
            "latitudes": latitudes,
            "longitudes": longitudes,
        },
        "fields": fields_meta,
        "frames": frames_out,
        "spots": spots or [],
    }

    flags = []
    for frame in qc_frames:
        for field_name, details in frame["fields"].items():
            for flag in details["flags"]:
                flags.append({
                    "forecast_hour": frame["forecast_hour"],
                    "field": field_name,
                    "flag": flag,
                })

    qc = {
        "schema_version": 1,
        "model_id": "jma_msm",
        "provider": manifest["provider"],
        "model": manifest["model"],
        "frame_count": len(frames_out),
        "grid_rows": rows,
        "grid_cols": cols,
        "spot_count": len(spots or []),
        "fields": list(FIELD_ENCODINGS),
        "frames": qc_frames,
        "flags": flags,
        "notes": [
            "JMA MSM cloud layers are native JMA cloud-cover diagnostics.",
            "The Open-Meteo AWS dataset is used only as the transport/mirror.",
            "Browser interpolation is presentation-only and does not increase native ~5 km resolution.",
            "The published Taiwan subset begins at the native southern boundary 22.4N.",
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
    print(json.dumps({
        "browser_bundle": str(bundle_path),
        "qc_report": str(qc_path),
        "frames": len(bundle["frames"]),
        "fields": list(bundle["fields"]),
        "grid": [bundle["grid"]["rows"], bundle["grid"]["cols"]],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
