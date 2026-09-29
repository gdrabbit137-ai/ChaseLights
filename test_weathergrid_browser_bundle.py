import json
import tempfile
import unittest
from pathlib import Path

from weathergrid_browser_bundle import build_bundle, dequantize, quantize


def _field(values, unit):
    return {
        "field_attrs": {
            "source_units": unit,
            "normalized_units": unit,
        },
        "latitudes": [25.0, 24.75],
        "longitudes": [121.0, 121.25],
        "values": values,
    }


class WeatherGridBrowserBundleTest(unittest.TestCase):
    def test_quantization_round_trip(self):
        encoded = quantize(
            [[0.0, 12.34], [55.55, 100.0]],
            scale=0.1,
            minimum=0.0,
            maximum=100.0,
        )
        self.assertEqual(encoded, [0, 123, 556, 1000])
        decoded = dequantize(encoded, 0.1)
        self.assertEqual(decoded, [0.0, 12.3, 55.6, 100.0])

    def test_build_bundle_and_qc(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = {
                "provider": "NOAA/NCEP NOMADS",
                "model": "GFS",
                "cycle": {
                    "date": "20260929",
                    "cycle": "00",
                    "cycle_time_utc": "2026-09-29T00:00:00+00:00",
                },
                "bbox": {
                    "leftlon": 117.5,
                    "rightlon": 123.5,
                    "toplat": 26.75,
                    "bottomlat": 20.5,
                },
                "frames": [
                    {
                        "forecast_hour": 0,
                        "valid_time_utc": "2026-09-29T00:00:00+00:00",
                        "json": "f000.json",
                    }
                ],
            }
            (root / "gfs_tw_weather_manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )

            frame = {
                "run": {
                    "forecast_hour": 0,
                    "valid_time_utc": "2026-09-29T00:00:00+00:00",
                },
                "fields": {
                    "low_cloud_percent": _field([[0, 50], [75, 100]], "%"),
                    "mid_cloud_percent": _field([[0, 0], [0, 0]], "%"),
                    "high_cloud_percent": _field([[10, 20], [30, 40]], "%"),
                    "visibility_km": _field(
                        [[24.135, 24.135], [24.135, 24.135]], "km"
                    ),
                    "precip_rate_mm_h": _field([[0, 0.12], [0.5, 1.0]], "mm/h"),
                    "wind_speed_10m_m_s": _field([[1, 2], [3, 4]], "m/s"),
                    "wind_direction_10m_deg": _field(
                        [[0, 90], [180, 270]], "degree"
                    ),
                },
                "spots": [
                    {
                        "spot_id": "tw-001",
                        "name": "測試景點",
                        "lat": 25.0,
                        "lon": 121.0,
                    }
                ],
            }
            (root / "f000.json").write_text(
                json.dumps(frame, ensure_ascii=False), encoding="utf-8"
            )

            bundle, qc = build_bundle(root)

            self.assertEqual(bundle["grid"]["rows"], 2)
            self.assertEqual(bundle["grid"]["cols"], 2)
            self.assertEqual(len(bundle["frames"]), 1)
            self.assertEqual(len(bundle["spots"]), 1)
            self.assertEqual(
                bundle["frames"][0]["values"]["low_cloud_percent"],
                [0, 50, 75, 100],
            )
            flags = {(x["field"], x["flag"]) for x in qc["flags"]}
            self.assertIn(("mid_cloud_percent", "constant_field"), flags)
            self.assertIn(
                ("visibility_km", "visibility_ceiling_dominant"),
                flags,
            )

    def test_rejects_grid_coordinate_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = {
                "provider": "NOAA/NCEP NOMADS",
                "model": "GFS",
                "cycle": {"date": "20260929", "cycle": "00"},
                "bbox": {},
                "frames": [{"forecast_hour": 0, "json": "f000.json"}],
            }
            (root / "gfs_tw_weather_manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )

            fields = {}
            for key in [
                "low_cloud_percent",
                "mid_cloud_percent",
                "high_cloud_percent",
                "visibility_km",
                "precip_rate_mm_h",
                "wind_speed_10m_m_s",
                "wind_direction_10m_deg",
            ]:
                fields[key] = _field([[0, 0], [0, 0]], "%")
            fields["visibility_km"]["longitudes"] = [121.0, 121.5]

            frame = {
                "run": {"forecast_hour": 0, "valid_time_utc": "x"},
                "fields": fields,
                "spots": [],
            }
            (root / "f000.json").write_text(json.dumps(frame), encoding="utf-8")

            with self.assertRaises(ValueError):
                build_bundle(root)


if __name__ == "__main__":
    unittest.main()
