import unittest
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

from gfs_raw_poc import (
    GFSRun,
    TAIWAN_BBOX,
    build_nomads_url,
    candidate_runs,
    parse_forecast_hours,
    sample_grid_bilinear,
    sample_grid_nearest,
    validate_cycle,
    validate_forecast_hour,
)


class GFSRawPOCTest(unittest.TestCase):
    def test_run_filename_directory_and_valid_time(self):
        run = GFSRun("20260929", "00", 6)
        self.assertEqual(run.filename, "gfs.t00z.pgrb2.0p25.f006")
        self.assertEqual(run.directory, "/gfs.20260929/00/atmos")
        self.assertEqual(run.id, "20260929T00Z_f006")
        self.assertEqual(
            run.valid_time_utc,
            datetime(2026, 9, 29, 6, 0, tzinfo=timezone.utc),
        )

    def test_nomads_query_requests_only_low_cloud_over_taiwan(self):
        run = GFSRun("20260929", "06", 0)
        url = build_nomads_url(run)
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        self.assertEqual(query["file"], ["gfs.t06z.pgrb2.0p25.f000"])
        self.assertEqual(query["var_LCDC"], ["on"])
        self.assertEqual(query["lev_low_cloud_layer"], ["on"])
        self.assertNotIn("var_TCDC", query)
        self.assertEqual(float(query["leftlon"][0]), TAIWAN_BBOX["leftlon"])
        self.assertEqual(float(query["rightlon"][0]), TAIWAN_BBOX["rightlon"])
        self.assertEqual(float(query["toplat"][0]), TAIWAN_BBOX["toplat"])
        self.assertEqual(float(query["bottomlat"][0]), TAIWAN_BBOX["bottomlat"])
        self.assertEqual(query["dir"], ["/gfs.20260929/06/atmos"])

    def test_candidate_runs_respect_publication_lag_and_cycle_order(self):
        now = datetime(2026, 9, 29, 5, 30, tzinfo=timezone.utc)
        runs = candidate_runs(now=now, forecast_hour=3, count=4)
        self.assertEqual(
            [(x.date, x.cycle, x.forecast_hour) for x in runs],
            [
                ("20260929", "00", 3),
                ("20260928", "18", 3),
                ("20260928", "12", 3),
                ("20260928", "06", 3),
            ],
        )

    def test_forecast_hour_series_is_sorted_and_deduplicated(self):
        self.assertEqual(
            parse_forecast_hours("12,0,6,6,3"),
            [0, 3, 6, 12],
        )
        with self.assertRaises(ValueError):
            parse_forecast_hours("")
        with self.assertRaises(ValueError):
            parse_forecast_hours("0,385")

    def test_nearest_grid_sampling_is_traceable(self):
        grid = {
            "latitudes": [25.0, 24.75],
            "longitudes": [121.0, 121.25, 121.5],
            "values": [
                [10.0, 20.0, 30.0],
                [40.0, 50.0, 60.0],
            ],
        }
        sample = sample_grid_nearest(grid, lat=24.79, lon=121.22)
        self.assertEqual(sample["low_cloud_percent_nearest"], 50.0)
        self.assertEqual(sample["grid_lat"], 24.75)
        self.assertEqual(sample["grid_lon"], 121.25)
        self.assertEqual(sample["grid_row"], 1)
        self.assertEqual(sample["grid_col"], 1)
        self.assertGreater(sample["grid_distance_km"], 0)

    def test_bilinear_sampling_handles_descending_latitude(self):
        grid = {
            "latitudes": [25.0, 24.75],
            "longitudes": [121.0, 121.25],
            "values": [
                [0.0, 20.0],
                [40.0, 60.0],
            ],
        }
        center = sample_grid_bilinear(grid, lat=24.875, lon=121.125)
        self.assertEqual(center["interpolation_status"], "bilinear")
        self.assertAlmostEqual(center["low_cloud_percent_bilinear"], 30.0, places=2)

        corner = sample_grid_bilinear(grid, lat=25.0, lon=121.0)
        self.assertAlmostEqual(corner["low_cloud_percent_bilinear"], 0.0, places=2)

    def test_validation(self):
        self.assertEqual(validate_cycle("6"), "06")
        self.assertEqual(validate_forecast_hour(384), 384)
        with self.assertRaises(ValueError):
            validate_cycle("03")
        with self.assertRaises(ValueError):
            validate_forecast_hour(385)


if __name__ == "__main__":
    unittest.main()
