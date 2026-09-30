import json
import tempfile
import unittest
from pathlib import Path

from jma_msm_weathergrid_browser_bundle import build_jma_bundle


class JmaMsmBrowserBundleTests(unittest.TestCase):
    def test_build_bundle_preserves_vertical_metadata_and_quantizes_clouds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = {
                "schema_version": 1,
                "model_id": "jma_msm",
                "provider": "Japan Meteorological Agency (JMA)",
                "model": "JMA_MSM",
                "transport": {
                    "adapter": "Open-Meteo JMA API",
                    "cell_selection": "nearest",
                    "elevation_downscaling": False,
                },
                "cycle": {
                    "cycle_time_utc": None,
                    "label": "latest available JMA MSM API snapshot",
                },
                "bbox": {
                    "leftlon": 120.0,
                    "rightlon": 120.0625,
                    "bottomlat": 22.4,
                    "toplat": 22.45,
                },
                "native_domain": {
                    "leftlon": 120.0,
                    "rightlon": 150.0,
                    "bottomlat": 22.4,
                    "toplat": 47.6,
                },
                "provenance": {
                    "native_resolution_km": 5.0,
                    "native_lat_step_degrees": 0.05,
                    "native_lon_step_degrees": 0.0625,
                    "native_time_interval_hours": 1,
                    "update_interval_hours": 3,
                    "standard_forecast_horizon_hours": 39,
                    "extended_forecast_horizon_hours": 78,
                    "published_forecast_hours": 2,
                },
                "grid": {
                    "rows": 2,
                    "cols": 2,
                    "latitudes": [22.4, 22.45],
                    "longitudes": [120.0, 120.0625],
                },
                "fields": {
                    "total_cloud_percent": {
                        "unit": "%",
                        "vertical_definition": {
                            "coordinate": "full_column",
                            "native_definition": "full atmospheric column",
                            "approx_height": "全大氣柱",
                        },
                    },
                    "low_cloud_percent": {
                        "unit": "%",
                        "vertical_definition": {
                            "coordinate": "pressure",
                            "native_definition": "surface–~850 hPa",
                            "approx_height": "約地面～1.5 km",
                        },
                    },
                    "mid_cloud_percent": {
                        "unit": "%",
                        "vertical_definition": {
                            "coordinate": "pressure",
                            "native_definition": "~850–500 hPa",
                            "approx_height": "約1.5～5.6 km",
                        },
                    },
                    "high_cloud_percent": {
                        "unit": "%",
                        "vertical_definition": {
                            "coordinate": "pressure",
                            "native_definition": "<~500 hPa",
                            "approx_height": "約5.6 km 以上",
                        },
                    },
                },
                "frames": [
                    {
                        "forecast_hour": 0,
                        "valid_time_utc": "2026-09-30T12:00:00Z",
                        "values": {
                            "total_cloud_percent": [0, 25.4, 50.6, 100],
                            "low_cloud_percent": [10, 20, 30, 40],
                            "mid_cloud_percent": [1, 2, 3, 4],
                            "high_cloud_percent": [70, 80, 90, 100],
                        },
                    },
                    {
                        "forecast_hour": 1,
                        "valid_time_utc": "2026-09-30T13:00:00Z",
                        "values": {
                            "total_cloud_percent": [5, 15, 25, 35],
                            "low_cloud_percent": [11, 21, 31, 41],
                            "mid_cloud_percent": [2, 3, 4, 5],
                            "high_cloud_percent": [60, 70, 80, 90],
                        },
                    },
                ],
            }
            (root / "jma_msm_tw_cloud_raw.json").write_text(
                json.dumps(raw, ensure_ascii=False),
                encoding="utf-8",
            )

            bundle, qc = build_jma_bundle(root)

            self.assertEqual(bundle["model"], "JMA_MSM")
            self.assertEqual(bundle["grid"]["rows"], 2)
            self.assertEqual(bundle["grid"]["cols"], 2)
            self.assertEqual(len(bundle["frames"]), 2)
            self.assertEqual(
                bundle["frames"][0]["values"]["total_cloud_percent"],
                [0, 25, 51, 100],
            )
            self.assertEqual(
                bundle["fields"]["low_cloud_percent"]["vertical_definition"][
                    "native_definition"
                ],
                "surface–~850 hPa",
            )
            self.assertTrue(
                bundle["provenance"]["cloud_fields_native_to_jma_msm"]
            )
            self.assertEqual(
                bundle["provenance"]["transport_cell_selection"],
                "nearest",
            )
            self.assertFalse(
                bundle["provenance"]["transport_elevation_downscaling"]
            )
            self.assertEqual(qc["frame_count"], 2)
            self.assertEqual(
                qc["fields"],
                [
                    "total_cloud_percent",
                    "low_cloud_percent",
                    "mid_cloud_percent",
                    "high_cloud_percent",
                ],
            )


if __name__ == "__main__":
    unittest.main()
