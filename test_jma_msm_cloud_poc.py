import unittest
from datetime import datetime, timezone

from jma_msm_cloud_poc import (
    JMA_CLOUD_VERTICAL_DEFINITIONS,
    JMA_MSM_NATIVE,
    JMA_TAIWAN_BROWSER_BBOX,
    SOURCE_FIELDS,
    JmaMsmRun,
    candidate_runs,
    spatial_key,
    subset_slices,
    validate_forecast_hours,
)


class JmaMsmCloudPocTests(unittest.TestCase):
    def test_native_grid_contract(self):
        self.assertEqual(JMA_MSM_NATIVE["nx"], 481)
        self.assertEqual(JMA_MSM_NATIVE["ny"], 505)
        self.assertEqual(JMA_MSM_NATIVE["dx"], 0.0625)
        self.assertEqual(JMA_MSM_NATIVE["dy"], 0.05)
        self.assertEqual(JMA_MSM_NATIVE["surface_time_interval_hours"], 1)
        self.assertEqual(JMA_MSM_NATIVE["update_interval_hours"], 3)

    def test_forecast_horizon_depends_on_cycle(self):
        run00 = JmaMsmRun(datetime(2026, 9, 30, 0, tzinfo=timezone.utc))
        run03 = JmaMsmRun(datetime(2026, 9, 30, 3, tzinfo=timezone.utc))
        self.assertEqual(run00.max_forecast_hour, 78)
        self.assertEqual(run03.max_forecast_hour, 39)

    def test_candidate_runs_follow_three_hour_cycles_and_lag(self):
        now = datetime(2026, 9, 30, 10, 40, tzinfo=timezone.utc)
        runs = candidate_runs(now, publication_lag_hours=2.5, count=3)
        self.assertEqual(
            [r.cycle_time_utc.hour for r in runs],
            [6, 3, 0],
        )

    def test_spatial_key_uses_run_directory_and_valid_time(self):
        run = JmaMsmRun(datetime(2026, 9, 30, 6, tzinfo=timezone.utc))
        self.assertEqual(
            spatial_key(run, 3),
            "data_spatial/jma_msm/2026/09/30/0600Z/2026-09-30T0900.om",
        )

    def test_taiwan_subset_preserves_native_spacing(self):
        rows, cols, lats, lons = subset_slices(JMA_TAIWAN_BROWSER_BBOX)
        self.assertEqual((rows.start, rows.stop), (0, 73))
        self.assertEqual((cols.start, cols.stop), (0, 49))
        self.assertEqual(len(lats), 73)
        self.assertEqual(len(lons), 49)
        self.assertAlmostEqual(lats[-1], 26.0)
        self.assertAlmostEqual(lons[-1], 123.0)

    def test_native_cloud_fields_are_explicit(self):
        self.assertEqual(SOURCE_FIELDS["low_cloud_percent"], "cloud_cover_low")
        self.assertEqual(SOURCE_FIELDS["mid_cloud_percent"], "cloud_cover_mid")
        self.assertEqual(SOURCE_FIELDS["high_cloud_percent"], "cloud_cover_high")
        self.assertEqual(SOURCE_FIELDS["total_cloud_percent"], "cloud_cover")

    def test_jma_vertical_reference_boundaries(self):
        low = JMA_CLOUD_VERTICAL_DEFINITIONS["low_cloud_percent"]
        mid = JMA_CLOUD_VERTICAL_DEFINITIONS["mid_cloud_percent"]
        high = JMA_CLOUD_VERTICAL_DEFINITIONS["high_cloud_percent"]
        self.assertEqual(low["reference_pressure_bounds_hpa"]["top"], 850)
        self.assertEqual(mid["reference_pressure_bounds_hpa"], {"bottom": 850, "top": 500})
        self.assertEqual(high["reference_pressure_bounds_hpa"]["bottom"], 500)
        self.assertIn("地上気圧1000 hPa", low["native_definition"])

    def test_forecast_hour_validation(self):
        self.assertEqual(validate_forecast_hours([2, 0, 1, 2]), [0, 1, 2])
        with self.assertRaises(ValueError):
            validate_forecast_hours([79])


if __name__ == "__main__":
    unittest.main()
