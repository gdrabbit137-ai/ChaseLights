import json
import tempfile
import unittest
from pathlib import Path

from jma_msm_weathergrid_browser_bundle import build_jma_bundle


def field(values, vertical=None):
    attrs = {
        "source_units": "%",
        "normalized_units": "%",
    }
    if vertical:
        attrs["vertical_definition"] = vertical
    return {
        "field_attrs": attrs,
        "latitudes": [22.4, 22.45],
        "longitudes": [120.0, 120.0625],
        "values": values,
    }


class JmaMsmBrowserBundleTests(unittest.TestCase):
    def test_build_bundle_preserves_hourly_timeline_and_vertical_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            verticals = {
                "low_cloud_percent": {
                    "native_definition": "low",
                    "reference_pressure_bounds_hpa": {"bottom": "surface", "top": 850},
                },
                "mid_cloud_percent": {
                    "native_definition": "mid",
                    "reference_pressure_bounds_hpa": {"bottom": 850, "top": 500},
                },
                "high_cloud_percent": {
                    "native_definition": "high",
                    "reference_pressure_bounds_hpa": {"bottom": 500, "top": "model_top"},
                },
            }
            manifest = {
                "provider": "Japan Meteorological Agency (JMA)",
                "transport": "Open-Meteo AWS Open Data spatial mirror",
                "transport_license": "CC-BY-4.0",
                "model": "JMA_MSM_5KM",
                "cycle": {"cycle_time_utc": "2026-09-30T06:00:00+00:00"},
                "bbox": {
                    "leftlon": 120.0, "rightlon": 123.0,
                    "bottomlat": 22.4, "toplat": 26.0,
                },
                "native_domain": {
                    "leftlon": 120.0, "rightlon": 150.0,
                    "bottomlat": 22.4, "toplat": 47.6,
                    "dx": 0.0625, "dy": 0.05, "nx": 481, "ny": 505,
                },
                "native_resolution_km": 5.0,
                "native_time_interval_hours": 1,
                "update_interval_hours": 3,
                "max_forecast_hour": 39,
                "cloud_vertical_definitions": verticals,
                "frames": [],
            }
            for fh in (0, 1, 2):
                name = f"f{fh:03d}.json"
                manifest["frames"].append({
                    "forecast_hour": fh,
                    "valid_time_utc": f"2026-09-30T{6+fh:02}:00:00+00:00",
                    "json": name,
                    "source_uri": "s3://example",
                })
                frame = {
                    "run": {
                        "forecast_hour": fh,
                        "valid_time_utc": f"2026-09-30T{6+fh:02}:00:00+00:00",
                    },
                    "fields": {
                        "total_cloud_percent": field([[10,20],[30,40]]),
                        "low_cloud_percent": field([[10,20],[30,40]]),
                        "mid_cloud_percent": field([[20,30],[40,50]]),
                        "high_cloud_percent": field([[30,40],[50,60]]),
                    },
                    "spots": [],
                }
                (root / name).write_text(json.dumps(frame), encoding="utf-8")

            (root / "jma_msm_tw_cloud_manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            bundle, qc = build_jma_bundle(root)
            self.assertEqual(bundle["model_id"], "jma_msm")
            self.assertEqual(bundle["model"], "JMA_MSM_5KM")
            self.assertEqual(bundle["provenance"]["native_resolution_km"], 5.0)
            self.assertEqual(bundle["provenance"]["published_time_interval_hours"], 1)
            self.assertEqual(len(bundle["frames"]), 3)
            self.assertEqual(
                bundle["fields"]["low_cloud_percent"]["vertical_definition"]
                ["reference_pressure_bounds_hpa"]["top"],
                850,
            )
            self.assertEqual(qc["frame_count"], 3)


if __name__ == "__main__":
    unittest.main()
