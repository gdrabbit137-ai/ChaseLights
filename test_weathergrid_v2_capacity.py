import unittest

from weathergrid_v2_cache_index import cells_for_region
from weathergrid_v2_capacity import (
    JMA_BENCHMARK_TILE_BYTES,
    estimate_cell,
    estimate_region,
    estimate_working_set,
    recommend_storage,
)


class CapacityTest(unittest.TestCase):
    def test_native_resolution_changes_cost(self):
        b = {"west": 120, "south": 22.4, "east": 122, "north": 24.4}
        self.assertGreater(
            estimate_cell("jma", b)["gridpoints"],
            estimate_cell("gfs", b)["gridpoints"],
        )

    def test_jma_valid_time_estimate_uses_measured_benchmark(self):
        b = {"west": 138, "south": 34, "east": 140, "north": 36}
        e = estimate_cell("jma", b)
        self.assertEqual(e["rows"], 41)
        self.assertEqual(e["cols"], 33)
        self.assertEqual(e["estimated_compact_json_bytes"], JMA_BENCHMARK_TILE_BYTES)
        self.assertEqual(e["valid_times"], 1)

    def test_viewport_working_set_does_not_assume_full_forecast(self):
        cells = cells_for_region("jp")[:4]
        one = estimate_working_set("jma", cells, valid_times_loaded=1)
        six = estimate_working_set("jma", cells, valid_times_loaded=6)
        self.assertEqual(
            six["estimated_transfer_bytes"],
            one["estimated_transfer_bytes"] * 6,
        )
        self.assertLess(one["estimated_transfer_mib"], 1.0)

    def test_region_budget_is_reported_per_published_valid_time(self):
        cells = cells_for_region("jp")
        one = estimate_region("jma", cells, valid_times_published=1)
        six = estimate_region("jma", cells, valid_times_published=6)
        self.assertGreater(one["cell_count"], 20)
        self.assertGreater(one["estimated_refresh_mib"], 0)
        self.assertGreater(six["estimated_refresh_bytes"], one["estimated_refresh_bytes"])

    def test_twelve_hour_taiwan_native_publish_is_small(self):
        twelve = estimate_region(
            "jma",
            cells_for_region("tw"),
            valid_times_published=12,
        )
        self.assertLess(twelve["estimated_refresh_mib"], 2.0)

    def test_generated_cells_are_not_committed_by_default(self):
        x = recommend_storage([estimate_region("gfs", cells_for_region("us"))])
        self.assertFalse(x["publish_generated_cells_to_git"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
