import json
import tempfile
import unittest
from pathlib import Path

from cwa_weathergrid_browser_bundle import build_cwa_bundle


def field(values, unit):
    return {
        "latitudes": [23.0, 23.03],
        "longitudes": [120.0, 120.03],
        "values": values,
        "field_attrs": {
            "source_units": unit,
            "normalized_units": unit,
        },
    }


class CwaWeatherGridBrowserBundleTests(unittest.TestCase):
    def test_bundle_keeps_cwa_resolution_boundary_and_time_cadence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fields0 = {
                "temperature_2m_c": field([[20.0, 21.0], [22.0, 23.0]], "°C"),
                "relative_humidity_2m_percent": field(
                    [[70.0, 71.0], [72.0, 73.0]], "%"
                ),
                "wind_speed_10m_m_s": field(
                    [[2.0, 3.0], [4.0, 5.0]], "m/s"
                ),
                "wind_direction_10m_deg": field(
                    [[350.0, 5.0], [10.0, 20.0]], "degree"
                ),
                "precip_total_mm": field(
                    [[0.0, 1.0], [2.0, 3.0]], "mm"
                ),
                "shortwave_flux_w_m2": field(
                    [[100.0, 200.0], [300.0, 400.0]], "W/m²"
                ),
            }
            for fh, valid in (
                (0, "2026-09-30T00:00:00+00:00"),
                (6, "2026-09-30T06:00:00+00:00"),
            ):
                payload = {
                    "run": {
                        "forecast_hour": fh,
                        "valid_time_utc": valid,
                    },
                    "fields": fields0,
                    "spots": [
                        {
                            "spot_id": "tw-test",
                            "name": "test",
                            "lat": 23.0,
                            "lon": 120.0,
                        }
                    ],
                }
                (root / f"f{fh:03d}.json").write_text(
                    json.dumps(payload),
                    encoding="utf-8",
                )

            manifest = {
                "provider": "Central Weather Administration (CWA)",
                "model": "CWA_WRF_3KM",
                "cycle": {
                    "cycle_time_utc": "2026-09-30T00:00:00+00:00",
                },
                "bbox": {
                    "leftlon": 117.5,
                    "rightlon": 125.5,
                    "bottomlat": 20.0,
                    "toplat": 27.0,
                },
                "native_resolution_km": 3.0,
                "model_output_interval_hours": 1,
                "model_forecast_horizon_hours": 126,
                "public_product_interval_hours": 6,
                "public_product_horizon_hours": 84,
                "native_domain_reference": {
                    "grid_shape": [673, 1158],
                },
                "browser_grid_spacing_degrees": 0.03,
                "frames": [
                    {
                        "forecast_hour": 0,
                        "valid_time_utc": "2026-09-30T00:00:00+00:00",
                        "json": "f000.json",
                    },
                    {
                        "forecast_hour": 6,
                        "valid_time_utc": "2026-09-30T06:00:00+00:00",
                        "json": "f006.json",
                    },
                ],
            }
            (root / "cwa_wrf3_tw_weather_manifest.json").write_text(
                json.dumps(manifest),
                encoding="utf-8",
            )

            bundle, qc = build_cwa_bundle(root)
            self.assertEqual(bundle["model_id"], "cwa_wrf3")
            self.assertEqual(bundle["model"], "CWA_WRF_3KM")
            self.assertEqual(bundle["provenance"]["native_resolution_km"], 3.0)
            self.assertEqual(
                bundle["provenance"]["model_output_interval_hours"],
                1,
            )
            self.assertEqual(
                bundle["provenance"]["model_forecast_horizon_hours"],
                126,
            )
            self.assertEqual(
                bundle["provenance"]["public_product_interval_hours"],
                6,
            )
            self.assertEqual(
                bundle["provenance"]["public_product_horizon_hours"],
                84,
            )
            self.assertEqual(
                bundle["provenance"]["published_time_interval_hours"],
                6,
            )
            self.assertEqual(bundle["bbox"]["rightlon"], 125.5)
            self.assertIn("temperature_2m_c", bundle["fields"])
            self.assertIn("shortwave_flux_w_m2", bundle["fields"])
            self.assertEqual(qc["frame_count"], 2)


if __name__ == "__main__":
    unittest.main()
