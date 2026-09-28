import unittest
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

from gfs_raw_poc import (
    GFSRun,
    TAIWAN_BBOX,
    build_nomads_url,
    candidate_runs,
    validate_cycle,
    validate_forecast_hour,
)


class GFSRawPOCTest(unittest.TestCase):
    def test_run_filename_and_directory(self):
        run = GFSRun("20260929", "00", 6)
        self.assertEqual(run.filename, "gfs.t00z.pgrb2.0p25.f006")
        self.assertEqual(run.directory, "/gfs.20260929/00/atmos")
        self.assertEqual(run.id, "20260929T00Z_f006")

    def test_nomads_query_requests_only_low_cloud_over_taiwan(self):
        run = GFSRun("20260929", "06", 0)
        url = build_nomads_url(run)
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        self.assertEqual(query["file"], ["gfs.t06z.pgrb2.0p25.f000"])
        self.assertEqual(query["var_TCDC"], ["on"])
        self.assertEqual(query["lev_low_cloud_layer"], ["on"])
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

    def test_validation(self):
        self.assertEqual(validate_cycle("6"), "06")
        self.assertEqual(validate_forecast_hour(384), 384)
        with self.assertRaises(ValueError):
            validate_cycle("03")
        with self.assertRaises(ValueError):
            validate_forecast_hour(385)


if __name__ == "__main__":
    unittest.main()
