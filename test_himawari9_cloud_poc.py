import unittest
from datetime import datetime, timezone

from himawari9_cloud_poc import (
    candidate_slots,
    find_pair_for_slot,
    floor_to_ten_minutes,
    normalize_slot_utc,
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

    def test_exact_slot_pair_requires_same_exact_prefix(self):
        slot = datetime(2026, 10, 6, 18, 0, tzinfo=timezone.utc)
        prefix = "noaa-himawari9/AHI-L2-FLDK-Clouds/2026/10/06/1800/"

        class FakeFs:
            def ls(self, value, detail=False):
                self.value = value
                return [
                    prefix + "AHI-CMSK_v1r1_h09_sample.nc",
                    prefix + "AHI-CHGT_v1r1_h09_sample.nc",
                ]

        fs = FakeFs()
        resolved, pair = find_pair_for_slot(fs, slot=slot)
        self.assertEqual(resolved, slot)
        self.assertEqual(fs.value, prefix)
        self.assertIn("cloud_mask", pair)
        self.assertIn("cloud_height", pair)

    def test_exact_slot_rejects_non_ten_minute_time(self):
        with self.assertRaises(ValueError):
            normalize_slot_utc(
                datetime(2026, 10, 6, 18, 3, tzinfo=timezone.utc)
            )

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
