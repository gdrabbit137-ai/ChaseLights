import json
import tempfile
import unittest
from pathlib import Path

from weathergrid_v2_tile_export import (
    frame_to_tile,
    run_manifest,
    valid_time_token,
    write_frame_tile,
)


class TileExportTest(unittest.TestCase):
    def sample(self):
        return {
            "reference_time_utc": "2026-10-03T00:00:00Z",
            "grid": {
                "rows": 2,
                "cols": 2,
                "latitudes": [35, 34.95],
                "longitudes": [138, 138.0625],
            },
            "frames": [
                {
                    "forecast_hour": 1,
                    "valid_time_utc": "2026-10-03T01:00:00Z",
                    "values": {
                        "total_cloud_percent": [1, 2, 3, 4],
                        "low_cloud_percent": [5, 6, 7, 8],
                        "mid_cloud_percent": [9, 10, 11, 12],
                        "high_cloud_percent": [13, 14, 15, 16],
                    },
                },
                {
                    "forecast_hour": 2,
                    "valid_time_utc": "2026-10-03T02:00:00Z",
                    "values": {
                        "total_cloud_percent": [2, 3, 4, 5],
                        "low_cloud_percent": [6, 7, 8, 9],
                        "mid_cloud_percent": [10, 11, 12, 13],
                        "high_cloud_percent": [14, 15, 16, 17],
                    },
                },
            ],
            "transport": {"layout": "data_spatial"},
        }

    def test_exports_one_valid_time_only(self):
        t = frame_to_tile(self.sample())
        self.assertEqual(t["valid_time_utc"], "2026-10-03T01:00:00Z")
        self.assertEqual(t["valid_time_token"], "20261003T0100Z")
        self.assertNotIn("frames", t)
        self.assertEqual(len(t["values"]["cloud_cover"]), 4)

    def test_normalizes_native_jma_field_names_for_browser(self):
        t = frame_to_tile(self.sample())
        self.assertEqual(
            sorted(t["values"]),
            [
                "cloud_cover",
                "cloud_cover_high",
                "cloud_cover_low",
                "cloud_cover_mid",
            ],
        )
        self.assertEqual(t["values"]["cloud_cover_low"], [5, 6, 7, 8])

    def test_rejects_wrong_grid_length(self):
        s = self.sample()
        s["frames"][0]["values"]["low_cloud_percent"] = [1]
        with self.assertRaises(ValueError):
            frame_to_tile(s)

    def test_compact_json(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "tile.json"
            write_frame_tile(self.sample(), p)
            self.assertEqual(json.loads(p.read_text())["provider"], "jma")

    def test_run_manifest_advertises_valid_times_and_supported_fields(self):
        m = run_manifest(self.sample())
        self.assertEqual(m["reference_time_utc"], "2026-10-03T00:00:00Z")
        self.assertEqual(m["default_valid_time_utc"], "2026-10-03T01:00:00Z")
        self.assertEqual(
            [x["token"] for x in m["valid_times"]],
            ["20261003T0100Z", "20261003T0200Z"],
        )
        self.assertIn("cloud_cover_low", m["supported_fields"])

    def test_valid_time_token_is_canonical_utc(self):
        self.assertEqual(
            valid_time_token("2026-10-03T09:00:00+08:00"),
            "20261003T0100Z",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
