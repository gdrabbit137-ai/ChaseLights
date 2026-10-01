import unittest

from viirs_nightlights_weathergrid import (
    ENCODING_SCALE,
    FIELD_QUALITY,
    FIELD_RADIANCE,
    build_bundle,
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


if __name__ == "__main__":
    unittest.main()
