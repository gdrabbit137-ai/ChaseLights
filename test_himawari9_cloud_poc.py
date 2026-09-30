import unittest
from datetime import datetime, timezone

from himawari9_cloud_poc import (
    candidate_slots,
    floor_to_ten_minutes,
    projected_xy_to_pixel,
    select_product_pair,
    slot_prefix,
)


class Himawari9CloudPocContractTest(unittest.TestCase):
    def test_floor_to_ten_minutes(self):
        value = datetime(2026, 9, 30, 15, 47, 52, tzinfo=timezone.utc)
        self.assertEqual(
            floor_to_ten_minutes(value),
            datetime(2026, 9, 30, 15, 40, tzinfo=timezone.utc),
        )

    def test_slot_prefix(self):
        value = datetime(2026, 9, 30, 15, 40, tzinfo=timezone.utc)
        self.assertEqual(
            slot_prefix(value),
            "AHI-L2-FLDK-Clouds/2026/09/30/1540/",
        )

    def test_candidate_slots_cross_midnight(self):
        now = datetime(2026, 10, 1, 0, 4, tzinfo=timezone.utc)
        slots = candidate_slots(now, 3)
        self.assertEqual(
            slots,
            [
                datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc),
                datetime(2026, 9, 30, 23, 50, tzinfo=timezone.utc),
                datetime(2026, 9, 30, 23, 40, tzinfo=timezone.utc),
            ],
        )

    def test_projection_plane_center_maps_to_full_disk_center(self):
        row, col = projected_xy_to_pixel(0.0, 0.0)
        self.assertEqual((row, col), (2750.0, 2750.0))

    def test_select_product_pair_requires_same_listing(self):
        root = "noaa-himawari9/AHI-L2-FLDK-Clouds/2026/09/30/1540/"
        pair = select_product_pair(
            [
                root + "AHI-CPHS_v1r1_h09_sample.nc",
                root + "AHI-CMSK_v1r1_h09_sample.nc",
                root + "AHI-CHGT_v1r1_h09_sample.nc",
            ]
        )
        self.assertEqual(
            pair,
            {
                "cloud_mask": root + "AHI-CMSK_v1r1_h09_sample.nc",
                "cloud_height": root + "AHI-CHGT_v1r1_h09_sample.nc",
            },
        )
        self.assertIsNone(
            select_product_pair([root + "AHI-CMSK_v1r1_h09_sample.nc"])
        )


if __name__ == "__main__":
    unittest.main()
