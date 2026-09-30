"""Build compact browser/QC artifacts from CWA WRF 3 km frames."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from weathergrid_browser_bundle import field_stats, qc_flags, quantize


FIELD_ENCODINGS = {
    "temperature_2m_c": {
        "unit": "°C",
        "scale": 0.1,
        "min": -50.0,
        "max": 60.0,
    },
    "relative_humidity_2m_percent": {
        "unit": "%",
        "scale": 1.0,
        "min": 0.0,
        "max": 100.0,
    },
    "precip_total_mm": {
        "unit": "mm",
        "scale": 0.1,
        "min": 0.0,
        "max": 1000.0,
    },
    "shortwave_flux_w_m2": {
        "unit": "W/m²",
        "scale": 1.0,
        "min": -200.0,
        "max": 1600.0,
    },
    "wind_speed_10m_m_s": {
        "unit": "m/s",
        "scale": 0.1,
        "min": 0.0,
        "max": 100.0,
    },
    "wind_direction_10m_deg": {
        "unit": "°",
        "scale": 1.0,
        "min": 0.0,
        "max": 359.0,
        "wrap": 360.0,
    },
}

REQUIRED_FIELDS = {
    "temperature_2m_c",
    "relative_humidity_2m_percent",
    "wind_speed_10m_m_s",
    "wind_direction_10m_deg",
}


def _flatten(values):
    return [item for row in values for item in row]


def _grid_signature(field: dict) -> tuple:
    return (
        tuple(round(float(v), 6) for v in field["latitudes"]),
        tuple(round(float(v), 6) for v in field["longitudes"]),
    )


def _common_fields(frames: list[dict]) -> list[str]:
    if not frames:
        return []
    common = set(FIELD_ENCODINGS)
    for frame in frames:
        common &= set(frame.get("fields", {}))
    missing = REQUIRED_FIELDS - common
    if missing:
        raise ValueError(f"CWA frames missing required browser fields: {sorted(missing)}")
    return [name for name in FIELD_ENCODINGS if name in common]


def build_cwa_bundle(input_dir: Path) -> tuple[dict, dict]:
    manifest = json.loads(
        (input_dir / "cwa_wrf3_tw_weather_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    refs = manifest.get("frames", [])
    if not refs:
        raise ValueError("CWA WRF3 manifest has no frames")

    source_frames = [
        json.loads((input_dir / ref["json"]).read_text(encoding="utf-8"))
        for ref in refs
    ]
    field_names = _common_fields(source_frames)

    common_signature = None
    common_latitudes = None
    common_longitudes = None
    spots = None
    frames_out = []
    qc_frames = []

    for ref, frame in zip(refs, source_frames):
        encoded_fields = {}
        qc_fields = {}

        for field_name in field_names:
            field = frame["fields"][field_name]
            signature = _grid_signature(field)
            if common_signature is None:
                common_signature = signature
                common_latitudes = field["latitudes"]
                common_longitudes = field["longitudes"]
            elif signature != common_signature:
                raise ValueError(
                    f"CWA grid coordinates changed for {field_name} "
                    f"in {ref['json']}"
                )

            encoding = FIELD_ENCODINGS[field_name]
            raw = _flatten(field["values"])
            stats = field_stats(raw)
            flags = qc_flags(field_name, stats, raw)
            encoded = quantize(
                field["values"],
                scale=encoding["scale"],
                minimum=encoding["min"],
                maximum=encoding["max"],
            )
            if encoding.get("wrap"):
                wrap_units = int(round(encoding["wrap"] / encoding["scale"]))
                encoded = [
                    None if value is None else value % wrap_units
                    for value in encoded
                ]

            encoded_fields[field_name] = encoded
            qc_fields[field_name] = {
                **stats,
                "flags": flags,
                "source_units": field["field_attrs"].get("source_units"),
                "normalized_units": field["field_attrs"].get(
                    "normalized_units"
                ),
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
            raise ValueError(f"CWA Place set/order changed in {ref['json']}")

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
        for field_name, encoded in frame["values"].items():
            if len(encoded) != expected_cells:
                raise ValueError(
                    f"CWA {field_name} encoded cell count "
                    f"{len(encoded)} != {expected_cells}"
                )

    fields_meta = {}
    for key in field_names:
        meta = FIELD_ENCODINGS[key]
        fields_meta[key] = {
            "unit": meta["unit"],
            "encoding": "integer_scaled",
            "scale": meta["scale"],
            "decode": f"value * {meta['scale']}",
            "null": "missing",
            **({"wrap": meta["wrap"]} if meta.get("wrap") else {}),
        }

    published_steps = []
    for left, right in zip(frames_out, frames_out[1:]):
        published_steps.append(
            int(right["forecast_hour"]) - int(left["forecast_hour"])
        )
    published_step = published_steps[0] if published_steps and all(
        x == published_steps[0] for x in published_steps
    ) else None

    bundle = {
        "schema_version": 2,
        "model_id": "cwa_wrf3",
        "provider": manifest["provider"],
        "model": manifest["model"],
        "cycle": manifest["cycle"],
        "bbox": manifest["bbox"],
        "provenance": {
            "native_resolution_km": manifest["native_resolution_km"],
            "model_output_interval_hours": manifest[
                "model_output_interval_hours"
            ],
            "model_forecast_horizon_hours": manifest[
                "model_forecast_horizon_hours"
            ],
            "public_product_interval_hours": manifest[
                "public_product_interval_hours"
            ],
            "public_product_horizon_hours": manifest[
                "public_product_horizon_hours"
            ],
            "native_domain_reference": manifest["native_domain_reference"],
            "browser_grid_spacing_degrees": manifest[
                "browser_grid_spacing_degrees"
            ],
            "published_time_interval_hours": published_step,
            "native_to_regular": "linear",
            "edge_fill": "nearest",
            "browser_interpolation": "bilinear_subcell",
            "cloud_layer_capability": {
                "native_low_mid_high": False,
                "pressure_level_rh_available": True,
                "policy": "do_not_infer_cloud_cover_from_rh",
                "verified_public_feed": "M-A0064",
            },
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
        "model_id": "cwa_wrf3",
        "provider": manifest["provider"],
        "model": manifest["model"],
        "cycle": manifest["cycle"],
        "frame_count": len(frames_out),
        "grid_rows": rows,
        "grid_cols": cols,
        "spot_count": len(spots or []),
        "fields": field_names,
        "frames": qc_frames,
        "flags": flags,
        "notes": [
            "CWA WRF3 native regional fields are remapped to a regular browser grid.",
            "Browser interpolation is presentation-only and does not increase model resolution.",
            "Wind direction is circular and should be rendered/sampled with nearest-cell semantics.",
            "Optional CWA fields are published only when present in every frame of the snapshot.",
            "Live M-A0064 verification found pressure-level relative humidity but no native low/mid/high cloud-cover fields.",
            "Pressure-level RH is not relabeled as cloud cover.",
        ],
    }
    return bundle, qc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default="cwa_wrf3_output")
    parser.add_argument("--output-dir", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir) if args.output_dir else input_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    bundle, qc = build_cwa_bundle(input_dir)
    bundle_path = output_dir / "cwa_wrf3_tw_weather_browser.json"
    qc_path = output_dir / "cwa_wrf3_tw_weather_qc.json"
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
        "spots": len(bundle["spots"]),
        "grid": [bundle["grid"]["rows"], bundle["grid"]["cols"]],
        "flags": len(qc["flags"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
