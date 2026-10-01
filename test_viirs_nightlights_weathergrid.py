import unittest

from viirs_nightlights_weathergrid import (
    ENCODING_SCALE,
    FIELD_QUALITY,
    FIELD_RADIANCE,
    MAX_BROWSER_CELLS,
    build_bundle,
    sample_bundle_at_location,
)


class ViirsNightLightsWeatherGridTest(unittest.TestCase):
    def test_contract_preserves_radiance_semantics(self):
        bundle, qc = build_bundle(
            [25.0, 24.5],
            [121.0, 121.5],
            [0.2, 1.5, 8.4, 42.0],
            [0, 0, 1, 2],
            2025,
        )
        self.assertEqual(bundle["source"], "nasa_black_marble_vnp46a4")
        self.assertEqual(bundle["fields"][FIELD_RADIANCE]["unit"], "nW/(cm²·sr)")
        self.assertEqual(bundle["fields"][FIELD_RADIANCE]["scale"], ENCODING_SCALE)
        self.assertIn("not Bortle class", bundle["provenance"]["semantics"])
        self.assertEqual(bundle["frames"][0]["values"][FIELD_RADIANCE], [2, 15, 84, 420])
        self.assertEqual(qc["quality_counts"]["poor"], 1)
        self.assertEqual(qc["quality_counts"]["gap_filled"], 1)

    def test_fill_and_invalid_radiance_remain_missing(self):
        bundle, qc = build_bundle(
            [25.0, 24.5],
            [121.0, 121.5],
            [0.2, -999.9, None, 4.0],
            [0, 255, 0, 255],
            2025,
        )
        values = bundle["frames"][0]["values"][FIELD_RADIANCE]
        quality = bundle["frames"][0]["values"][FIELD_QUALITY]
        self.assertEqual(values, [2, None, None, None])
        self.assertEqual(quality, [0, None, 0, None])
        self.assertEqual(qc["radiance"]["missing"], 3)

    def test_bad_grid_shape_fails_closed(self):
        with self.assertRaises(ValueError):
            build_bundle([25.0], [121.0, 121.5], [1, 2], [0, 0], 2025)


    def test_large_native_grid_is_sampled_to_browser_budget(self):
        rows, cols = 100, 100
        lats = [25.0 - i * 0.01 for i in range(rows)]
        lons = [120.0 + i * 0.01 for i in range(cols)]
        radiance = [1.0] * (rows * cols)
        quality = [0] * (rows * cols)
        bundle, qc = build_bundle(
            lats, lons, radiance, quality, 2025, max_browser_cells=2500
        )
        self.assertLessEqual(bundle["grid"]["rows"] * bundle["grid"]["cols"], 2500)
        self.assertEqual(bundle["provenance"]["native_resolution"], "15 arc-second")
        self.assertGreater(bundle["provenance"]["browser_sampling_stride"], 1)
        self.assertEqual(qc["source_cell_count"], 10000)
        self.assertEqual(qc["browser_budget_cells"], 2500)

    def test_default_browser_budget_is_explicit(self):
        self.assertEqual(MAX_BROWSER_CELLS, 250_000)

    def test_tiny_browser_budget_fails_closed(self):
        with self.assertRaises(ValueError):
            build_bundle(
                [25.0, 24.5],
                [121.0, 121.5],
                [1, 2, 3, 4],
                [0, 0, 0, 0],
                2025,
                max_browser_cells=3,
            )


    def test_point_sampler_preserves_quality_and_sampling_provenance(self):
        bundle, qc = build_bundle(
            [25.0, 24.5],
            [121.0, 121.5],
            [0.2, 1.5, 8.4, 42.0],
            [0, 1, 2, 0],
            2025,
        )
        sample = sample_bundle_at_location(bundle, 24.96, 121.04, qc=qc)
        self.assertAlmostEqual(sample[FIELD_RADIANCE], 0.2)
        self.assertEqual(sample[FIELD_QUALITY], 0)
        self.assertEqual(sample["viirs_sample"]["composite_year"], 2025)
        self.assertEqual(sample["viirs_sample"]["browser_sampling_stride"], 1)
        self.assertIn("not native-resolution", sample["viirs_sample"]["sampling_semantics"])

    def test_point_sampler_fails_closed_outside_bbox_or_bad_qc(self):
        bundle, qc = build_bundle(
            [25.0, 24.5],
            [121.0, 121.5],
            [1, 2, 3, 4],
            [0, 0, 0, 0],
            2025,
        )
        self.assertIsNone(sample_bundle_at_location(bundle, 26.0, 121.0, qc=qc))
        bad_qc = dict(qc)
        bad_qc["flags"] = ["all_missing"]
        self.assertIsNone(sample_bundle_at_location(bundle, 25.0, 121.0, qc=bad_qc))


if __name__ == "__main__":
    unittest.main()
