import unittest

from weathergrid_v2_gfs_global import (
    GFS_CLOUD_FIELDS,
    all_global_cells,
    cells_for_viewport,
    coverage_complete,
    nomads_segments,
)


class GlobalGfsCellContractTests(unittest.TestCase):
    def test_four_cloud_fields_include_total_cloud(self):
        self.assertEqual(
            GFS_CLOUD_FIELDS,
            ("cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high"),
        )

    def test_antimeridian_viewport_stays_local_and_deduplicated(self):
        cells = cells_for_viewport(
            {"west": 178.0, "south": 20.0, "east": -178.0, "north": 24.0},
            cell_deg=4.0,
        )
        ids = [cell["id"] for cell in cells]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(cells), 2)
        self.assertTrue(any(c["bbox"]["east"] == 180.0 for c in cells))
        self.assertTrue(any(c["bbox"]["west"] == -180.0 for c in cells))

    def test_nomads_bbox_splits_at_antimeridian(self):
        self.assertEqual(
            nomads_segments(
                {"west": 178.0, "south": 20.0, "east": -178.0, "north": 24.0}
            ),
            [
                {"leftlon": 178.0, "rightlon": 180.0, "bottomlat": 20.0, "toplat": 24.0},
                {"leftlon": -180.0, "rightlon": -178.0, "bottomlat": 20.0, "toplat": 24.0},
            ],
        )

    def test_prefetch_clamps_at_poles(self):
        cells = cells_for_viewport(
            {"west": 0.0, "south": 88.0, "east": 4.0, "north": 90.0},
            cell_deg=4.0,
            prefetch_cells=1,
        )
        self.assertTrue(cells)
        self.assertTrue(all(c["bbox"]["north"] <= 90.0 for c in cells))

    def test_global_grid_is_finite_and_complete_address_space(self):
        cells = all_global_cells(cell_deg=4.0)
        self.assertEqual(len(cells), 90 * 45)
        self.assertEqual(len({c["id"] for c in cells}), len(cells))

    def test_coverage_is_fail_closed(self):
        required = ["a", "b"]
        self.assertFalse(coverage_complete(required, []))
        self.assertFalse(coverage_complete(required, ["a"]))
        self.assertTrue(coverage_complete(required, ["a", "b", "extra"]))
        self.assertFalse(coverage_complete([], ["a"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
