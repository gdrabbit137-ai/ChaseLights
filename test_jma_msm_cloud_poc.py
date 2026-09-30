import unittest

from jma_msm_cloud_poc import (
    API_VARIABLES,
    JMA_MSM_CLOUD_VERTICAL_DEFINITIONS,
    JMA_MSM_NATIVE_DOMAIN,
    JMA_MSM_TAIWAN_BROWSER_BBOX,
    build_grid,
    fetch_snapshot,
)


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _FakeSession:
    def __init__(self):
        self.calls = []

    def get(self, url, params, timeout):
        self.calls.append((url, dict(params), timeout))
        lats = [float(x) for x in params["latitude"].split(",")]
        lons = [float(x) for x in params["longitude"].split(",")]
        rows = []
        for idx, (lat, lon) in enumerate(zip(lats, lons)):
            base = idx * 10
            rows.append(
                {
                    "latitude": lat,
                    "longitude": lon,
                    "hourly": {
                        "time": [
                            "2026-09-30T12:00",
                            "2026-09-30T13:00",
                        ],
                        "cloud_cover": [10 + base, 20 + base],
                        "cloud_cover_low": [11 + base, 21 + base],
                        "cloud_cover_mid": [12 + base, 22 + base],
                        "cloud_cover_high": [13 + base, 23 + base],
                    },
                }
            )
        return _FakeResponse(rows)


class JmaMsmCloudProviderTests(unittest.TestCase):
    def test_native_domain_and_taiwan_bbox_follow_jma_boundary(self):
        self.assertEqual(JMA_MSM_NATIVE_DOMAIN["leftlon"], 120.0)
        self.assertEqual(JMA_MSM_NATIVE_DOMAIN["bottomlat"], 22.4)
        self.assertEqual(JMA_MSM_TAIWAN_BROWSER_BBOX["leftlon"], 120.0625)
        self.assertEqual(JMA_MSM_TAIWAN_BROWSER_BBOX["bottomlat"], 22.45)

    def test_grid_uses_native_surface_spacing(self):
        bbox = {
            "leftlon": 120.0,
            "rightlon": 120.0625,
            "bottomlat": 22.4,
            "toplat": 22.45,
        }
        lats, lons, points = build_grid(bbox)
        self.assertEqual(lats, [22.4, 22.45])
        self.assertEqual(lons, [120.0, 120.0625])
        self.assertEqual(len(points), 4)

    def test_api_cloud_fields_are_native_jma_layers(self):
        self.assertEqual(
            API_VARIABLES,
            {
                "cloud_cover": "total_cloud_percent",
                "cloud_cover_low": "low_cloud_percent",
                "cloud_cover_mid": "mid_cloud_percent",
                "cloud_cover_high": "high_cloud_percent",
            },
        )

    def test_vertical_definitions_preserve_jma_boundary_rule(self):
        low = JMA_MSM_CLOUD_VERTICAL_DEFINITIONS["low_cloud_percent"]
        mid = JMA_MSM_CLOUD_VERTICAL_DEFINITIONS["mid_cloud_percent"]
        high = JMA_MSM_CLOUD_VERTICAL_DEFINITIONS["high_cloud_percent"]
        self.assertIn("Ps×0.85", low["native_definition"])
        self.assertEqual(
            mid["boundary_rule"]["mid_high_hpa"],
            "min(low_mid_hpa * 0.8, 500)",
        )
        self.assertIn("<~500 hPa", high["native_definition"])

    def test_fetch_snapshot_disables_downscaling_and_keeps_hourly_axis(self):
        session = _FakeSession()
        bbox = {
            "leftlon": 120.0,
            "rightlon": 120.0625,
            "bottomlat": 22.4,
            "toplat": 22.45,
        }
        snapshot = fetch_snapshot(
            bbox=bbox,
            forecast_hours=2,
            batch_size=2,
            session=session,
        )

        self.assertEqual(snapshot["model"], "JMA_MSM")
        self.assertEqual(snapshot["grid"]["rows"], 2)
        self.assertEqual(snapshot["grid"]["cols"], 2)
        self.assertEqual(len(snapshot["frames"]), 2)
        self.assertEqual(
            snapshot["frames"][0]["valid_time_utc"],
            "2026-09-30T12:00:00Z",
        )
        self.assertEqual(
            len(snapshot["frames"][0]["values"]["low_cloud_percent"]),
            4,
        )
        self.assertEqual(len(session.calls), 2)
        self.assertEqual(
            snapshot["provenance"]["forecast_hour_semantics"],
            "hours_from_first_published_valid_time_not_model_cycle",
        )
        self.assertFalse(snapshot["provenance"]["cycle_timestamp_available"])

        for _, params, _ in session.calls:
            self.assertEqual(params["models"], "jma_msm")
            self.assertEqual(params["cell_selection"], "nearest")
            self.assertTrue(
                all(x == "nan" for x in params["elevation"].split(","))
            )
            self.assertEqual(
                len(params["elevation"].split(",")),
                len(params["latitude"].split(",")),
            )
            self.assertEqual(params["timezone"], "GMT")


if __name__ == "__main__":
    unittest.main()
