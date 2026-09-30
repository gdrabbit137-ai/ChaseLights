import unittest

import numpy as np

from jma_msm_aws_om import (
    IN_PROGRESS_METADATA_URL,
    LATEST_METADATA_URL,
    SOURCE_TO_TARGET,
    fetch_best_metadata,
    grid_slice_for_bbox,
    spatial_s3_uri,
)
from jma_msm_cloud_poc import (
    API_VARIABLES,
    JMA_MSM_CLOUD_VERTICAL_DEFINITIONS,
    JMA_MSM_NATIVE_DOMAIN,
    JMA_MSM_TAIWAN_BROWSER_BBOX,
    build_grid,
    fetch_snapshot,
)


class _MetadataResponse:
    def __init__(self, payload):
        self.payload = payload
        self.text = ""

    def raise_for_status(self):
        return None

    def json(self):
        return dict(self.payload)


class _MetadataSession:
    def __init__(self, by_url):
        self.by_url = by_url

    def get(self, url, timeout):
        return _MetadataResponse(self.by_url[url])


class JmaMsmAwsOmProviderTests(unittest.TestCase):
    def setUp(self):
        self.bbox = {
            "leftlon": 120.0625,
            "rightlon": 120.125,
            "bottomlat": 22.45,
            "toplat": 22.5,
        }
        self.metadata = {
            "completed": True,
            "last_modified_time": "2026-09-30T05:45:00Z",
            "reference_time": "2026-09-30T03:00:00Z",
            "valid_times": [
                "2026-09-30T03:00Z",
                "2026-09-30T04:00Z",
            ],
            "variables": list(SOURCE_TO_TARGET),
        }

    def test_native_domain_and_taiwan_bbox_follow_jma_boundary(self):
        self.assertEqual(JMA_MSM_NATIVE_DOMAIN["leftlon"], 120.0)
        self.assertEqual(JMA_MSM_NATIVE_DOMAIN["bottomlat"], 22.4)
        self.assertEqual(JMA_MSM_TAIWAN_BROWSER_BBOX["leftlon"], 120.0625)
        self.assertEqual(JMA_MSM_TAIWAN_BROWSER_BBOX["bottomlat"], 22.45)

    def test_grid_uses_native_surface_spacing(self):
        lats, lons, points = build_grid(self.bbox)
        self.assertEqual(lats, [22.45, 22.5])
        self.assertEqual(lons, [120.0625, 120.125])
        self.assertEqual(len(points), 4)

    def test_aws_grid_slice_maps_exact_native_indices(self):
        grid = grid_slice_for_bbox(self.bbox)
        self.assertEqual((grid.y.start, grid.y.stop), (1, 3))
        self.assertEqual((grid.x.start, grid.x.stop), (1, 3))
        self.assertEqual(grid.latitudes, [22.45, 22.5])
        self.assertEqual(grid.longitudes, [120.0625, 120.125])

    def test_spatial_uri_uses_model_run_and_valid_time(self):
        self.assertEqual(
            spatial_s3_uri(
                "2026-09-30T03:00:00Z",
                "2026-09-30T04:00Z",
            ),
            "s3://openmeteo/data_spatial/jma_msm/"
            "2026/09/30/0300Z/2026-09-30T0400.om",
        )

    def test_cloud_fields_remain_native_jma_layers(self):
        self.assertEqual(API_VARIABLES, SOURCE_TO_TARGET)

    def test_metadata_resolver_prefers_fresher_usable_in_progress_run(self):
        latest = dict(self.metadata)
        latest["reference_time"] = "2026-09-30T09:00:00Z"
        progress = dict(self.metadata)
        progress["reference_time"] = "2026-09-30T12:00:00Z"
        session = _MetadataSession({
            IN_PROGRESS_METADATA_URL: progress,
            LATEST_METADATA_URL: latest,
        })
        chosen = fetch_best_metadata(
            forecast_hours=2,
            session=session,
        )
        self.assertEqual(chosen["reference_time"], "2026-09-30T12:00:00Z")
        self.assertEqual(chosen["_metadata_url"], IN_PROGRESS_METADATA_URL)

    def test_metadata_resolver_falls_back_when_new_run_is_incomplete(self):
        latest = dict(self.metadata)
        latest["reference_time"] = "2026-09-30T09:00:00Z"
        progress = dict(self.metadata)
        progress["reference_time"] = "2026-09-30T12:00:00Z"
        progress["valid_times"] = ["2026-09-30T12:00Z"]
        session = _MetadataSession({
            IN_PROGRESS_METADATA_URL: progress,
            LATEST_METADATA_URL: latest,
        })
        chosen = fetch_best_metadata(
            forecast_hours=2,
            session=session,
        )
        self.assertEqual(chosen["reference_time"], "2026-09-30T09:00:00Z")
        self.assertEqual(chosen["_metadata_url"], LATEST_METADATA_URL)

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

    def test_fetch_snapshot_uses_aws_cycle_and_true_model_leads(self):
        calls = []

        def reader(uri, grid):
            calls.append(uri)
            shape = (len(grid.latitudes), len(grid.longitudes))
            return {
                source: np.full(shape, 10 + idx, dtype=np.float32)
                for idx, source in enumerate(SOURCE_TO_TARGET)
            }

        snapshot = fetch_snapshot(
            bbox=self.bbox,
            forecast_hours=2,
            metadata=self.metadata,
            reader=reader,
        )
        self.assertEqual(snapshot["model"], "JMA_MSM")
        self.assertEqual(snapshot["cycle"]["cycle_time_utc"], "2026-09-30T03:00:00Z")
        self.assertEqual(
            [f["forecast_hour"] for f in snapshot["frames"]],
            [0, 1],
        )
        self.assertEqual(snapshot["grid"]["rows"], 2)
        self.assertEqual(snapshot["grid"]["cols"], 2)
        self.assertEqual(len(calls), 2)
        provenance = snapshot["provenance"]
        self.assertEqual(
            provenance["production_transport"],
            "open_meteo_aws_open_data_om",
        )
        self.assertEqual(
            provenance["forecast_hour_semantics"],
            "hours_from_model_cycle",
        )
        self.assertTrue(provenance["cycle_timestamp_available"])
        self.assertNotIn("OPEN_METEO_API_KEY", str(snapshot))

    def test_unaligned_bbox_is_rejected(self):
        bad = dict(self.bbox)
        bad["leftlon"] = 120.07
        with self.assertRaisesRegex(ValueError, "not aligned"):
            grid_slice_for_bbox(bad)


if __name__ == "__main__":
    unittest.main()
