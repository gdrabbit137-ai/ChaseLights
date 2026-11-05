import json
import tempfile
import unittest
from pathlib import Path

from weathergrid_browser_bundle import (
    SIDECAR_FIELDS,
    build_bundle,
    dequantize,
    quantize,
    split_uv_bundle,
)


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

    def test_direction_quantization_wraps_360_to_zero(self):
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
            base = _field([[0, 0], [0, 0]], "%")
            fields = {
                "total_cloud_percent": base,
                "low_cloud_percent": base,
                "mid_cloud_percent": base,
                "high_cloud_percent": base,
                "visibility_km": _field([[10, 10], [10, 10]], "km"),
                "precip_rate_mm_h": _field([[0, 0], [0, 0]], "mm/h"),
                "wind_speed_10m_m_s": _field([[1, 1], [1, 1]], "m/s"),
                "wind_direction_10m_deg": _field(
                    [[359.6, 359.4], [0.4, 180.0]], "degree"
                ),
                    "wind_u_10m_m_s": _field([[1, 1], [1, 1]], "m/s"),
                    "wind_v_10m_m_s": _field([[1, 1], [1, 1]], "m/s"),
                    "wind_u_925hpa_m_s": _field([[1, 1], [1, 1]], "m/s"),
                    "wind_v_925hpa_m_s": _field([[1, 1], [1, 1]], "m/s"),
                    "wind_u_850hpa_m_s": _field([[1, 1], [1, 1]], "m/s"),
                    "wind_v_850hpa_m_s": _field([[1, 1], [1, 1]], "m/s"),
                    "wind_u_700hpa_m_s": _field([[1, 1], [1, 1]], "m/s"),
                    "wind_v_700hpa_m_s": _field([[1, 1], [1, 1]], "m/s"),
            }
            frame = {
                "run": {"forecast_hour": 0, "valid_time_utc": "x"},
                "fields": fields,
                "spots": [],
            }
            (root / "f000.json").write_text(json.dumps(frame), encoding="utf-8")
            bundle, _ = build_bundle(root)
            encoded = bundle["frames"][0]["values"]["wind_direction_10m_deg"]
            self.assertEqual(encoded, [0, 359, 0, 180])
            self.assertEqual(bundle["fields"]["wind_direction_10m_deg"]["wrap"], 360)

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
                    "total_cloud_percent": _field([[10, 60], [85, 100]], "%"),
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
                    "wind_u_10m_m_s": _field([[-3, 0], [5, 12]], "m/s"),
                    "wind_v_10m_m_s": _field([[-3, 0], [5, 12]], "m/s"),
                    "wind_u_925hpa_m_s": _field([[-3, 0], [5, 12]], "m/s"),
                    "wind_v_925hpa_m_s": _field([[-3, 0], [5, 12]], "m/s"),
                    "wind_u_850hpa_m_s": _field([[-3, 0], [5, 12]], "m/s"),
                    "wind_v_850hpa_m_s": _field([[-3, 0], [5, 12]], "m/s"),
                    "wind_u_700hpa_m_s": _field([[-3, 0], [5, 12]], "m/s"),
                    "wind_v_700hpa_m_s": _field([[-3, 0], [5, 12]], "m/s"),
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

    def test_split_uv_bundle_sidecar_partition(self):
        # CL-WG-22: the main bundle returns to the pre-CL-DATA-08 field set;
        # the eight u/v fields move to a per-region sidecar (identical
        # bbox/grid/frame structure) for the on-demand particle layer.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = {
                "provider": "NOAA/NCEP NOMADS",
                "model": "GFS",
                "cycle": {"date": "20260929", "cycle": "00"},
                "bbox": {"leftlon": 121.0, "rightlon": 121.25,
                         "bottomlat": 24.75, "toplat": 25.0},
                "frames": [{
                    "forecast_hour": 0,
                    "valid_time_utc": "x",
                    "json": "f000.json",
                }],
            }
            (root / "gfs_tw_weather_manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            base = _field([[0, 0], [0, 0]], "%")
            uv = _field([[-3, 0], [5, 12]], "m/s")
            fields = {
                "total_cloud_percent": base,
                "low_cloud_percent": base,
                "mid_cloud_percent": base,
                "high_cloud_percent": base,
                "visibility_km": _field([[10, 10], [10, 10]], "km"),
                "precip_rate_mm_h": base,
                "wind_speed_10m_m_s": _field([[1, 1], [1, 1]], "m/s"),
                "wind_direction_10m_deg": _field([[0, 90], [180, 270]], "degree"),
                "wind_u_10m_m_s": uv,
                "wind_v_10m_m_s": uv,
                "wind_u_925hpa_m_s": uv,
                "wind_v_925hpa_m_s": uv,
                "wind_u_850hpa_m_s": uv,
                "wind_v_850hpa_m_s": uv,
                "wind_u_700hpa_m_s": uv,
                "wind_v_700hpa_m_s": uv,
            }
            (root / "f000.json").write_text(
                json.dumps({"run": {"forecast_hour": 0, "valid_time_utc": "x"},
                            "fields": fields, "spots": []}), encoding="utf-8"
            )
            bundle, _ = build_bundle(root)
            main, sidecar = split_uv_bundle(bundle)

            self.assertEqual(
                sorted(main["fields"].keys()),
                sorted(k for k in bundle["fields"] if k not in SIDECAR_FIELDS),
            )
            self.assertEqual(sorted(sidecar["fields"].keys()), sorted(SIDECAR_FIELDS))
            self.assertEqual(
                sorted(sidecar["frames"][0]["values"].keys()), sorted(SIDECAR_FIELDS)
            )
            self.assertFalse(
                SIDECAR_FIELDS & set(main["frames"][0]["values"].keys())
            )
            # Sidecar carries the identical bbox/grid/frame structure so the
            # frontend can merge it against the main bundle frame-by-frame.
            for key in ("schema_version", "provider", "model", "cycle",
                        "bbox", "grid", "spots"):
                self.assertEqual(main[key], sidecar[key])
            self.assertEqual(
                [(f["forecast_hour"], f["valid_time_utc"]) for f in sidecar["frames"]],
                [(f["forecast_hour"], f["valid_time_utc"]) for f in main["frames"]],
            )
            self.assertEqual(sidecar["frames"][0]["values"]["wind_u_10m_m_s"],
                             bundle["frames"][0]["values"]["wind_u_10m_m_s"])
            # Reconstruction: main + sidecar == original bundle fields.
            merged = {**main["fields"], **sidecar["fields"]}
            self.assertEqual(merged, bundle["fields"])
            self.assertEqual(sidecar["sidecar"]["purpose"], "wind_uv_particle_flow")

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
                "total_cloud_percent",
                "low_cloud_percent",
                "mid_cloud_percent",
                "high_cloud_percent",
                "visibility_km",
                "precip_rate_mm_h",
                "wind_speed_10m_m_s",
                "wind_direction_10m_deg",
                "wind_u_10m_m_s", "wind_v_10m_m_s",
                "wind_u_925hpa_m_s", "wind_v_925hpa_m_s",
                "wind_u_850hpa_m_s", "wind_v_850hpa_m_s",
                "wind_u_700hpa_m_s", "wind_v_700hpa_m_s",
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
