import math
import unittest
from datetime import datetime, timezone

import numpy as np

from himawari9_weathergrid_browser_bundle import (
    HEIGHT_SCALE_M,
    _attr_text,
    nearest_regular_grid,
    parse_slot_utc,
    quantize_height,
    regular_axis,
)


class Himawari9WeatherGridBundleTest(unittest.TestCase):
    def test_attr_text_decodes_netcdf_bytes(self):
        self.assertEqual(_attr_text(b"2026-09-30T16:20:21Z"), "2026-09-30T16:20:21Z")

    def test_parse_slot_utc_for_replay(self):
        self.assertEqual(
            parse_slot_utc("2026-10-06T18:00:00Z"),
            datetime(2026, 10, 6, 18, 0, tzinfo=timezone.utc),
        )
        with self.assertRaises(ValueError):
            parse_slot_utc("2026-10-06T18:03:00Z")

    def test_regular_axis_includes_both_ends(self):
        self.assertEqual(
            regular_axis(21.5, 21.54, 0.02),
            [21.5, 21.52, 21.54],
        )

    def test_quantize_height_uses_100m_step_and_missing(self):
        self.assertEqual(
            quantize_height([0.0, 149.0, 151.0, None, math.nan, 21000.0]),
            [0, 1, 2, None, None, None],
        )
        self.assertEqual(HEIGHT_SCALE_M, 100.0)

    def test_nearest_regular_grid_preserves_fill(self):
        source_lat = np.array([[23.0, 23.0], [23.02, 23.02]])
        source_lon = np.array([[121.0, 121.02], [121.0, 121.02]])
        source_values = np.array([[0, 1], [1, -128]], dtype=np.int16)
        sampled, qc = nearest_regular_grid(
            source_lat,
            source_lon,
            source_values,
            target_latitudes=[23.0, 23.02],
            target_longitudes=[121.0, 121.02],
            fill_value=-128,
            max_distance_m=100.0,
        )
        self.assertEqual(sampled, [0, 1, 1, None])
        self.assertEqual(qc["outside_max_distance"], 0)
        self.assertLess(qc["max_m"], 1.0)


if __name__ == "__main__":
    unittest.main()
