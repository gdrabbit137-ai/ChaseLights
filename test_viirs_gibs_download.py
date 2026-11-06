"""Tile-matrix geometry + fail-closed behavior of the GIBS downloader."""
import unittest
from urllib.parse import urlparse

from viirs_gibs_download import (
    LAYER_NOAA20,
    LAYER_SNPP_HISTORICAL,
    REGION_BBOXES,
    level_extent,
    tile_geometry,
    tile_url,
    tiles_for_bbox,
)


class TileMatrixGeometryTest(unittest.TestCase):
    def test_level_7_is_native_500m_grid(self):
        self.assertEqual(level_extent(7), (160, 80))

    def test_tile_geometry_matches_wmts_grid(self):
        # Level 6 tile (row 14, col 66): 4.5 deg tiles.
        left, bottom, right, top = tile_geometry(6, 14, 66)
        self.assertAlmostEqual(left, 117.0)
        self.assertAlmostEqual(right, 121.5)
        self.assertAlmostEqual(top, 27.0)
        self.assertAlmostEqual(bottom, 22.5)

    def test_tiles_for_bbox_covers_region(self):
        tiles = tiles_for_bbox(6, REGION_BBOXES["tw"])
        self.assertEqual(tiles, [(14, 66), (14, 67), (15, 66), (15, 67)])
        for row, col in tiles:
            left, bottom, right, top = tile_geometry(6, row, col)
            self.assertTrue(left <= REGION_BBOXES["tw"][2] and right >= REGION_BBOXES["tw"][0])

    def test_us_bbox_is_large_but_bounded(self):
        tiles = tiles_for_bbox(6, REGION_BBOXES["us"])
        self.assertTrue(50 <= len(tiles) <= 150)

    def test_out_of_range_tile_raises(self):
        with self.assertRaises(ValueError):
            tile_geometry(6, 40, 0)

    def test_invalid_bbox_raises(self):
        with self.assertRaises(ValueError):
            tiles_for_bbox(6, (200, 0, 210, 10))


class UrlContractTest(unittest.TestCase):
    def test_rest_pattern_noaa20_primary(self):
        url = tile_url("2026-11-04", 6, 14, 66)
        parsed = urlparse(url)
        self.assertEqual(
            parsed.path,
            "/wmts/epsg4326/best/VIIRS_NOAA20_DayNightBand_At_Sensor_Radiance/"
            "default/2026-11-04/500m/6/14/66.png",
        )

    def test_snpp_layer_is_explicit_historical_only(self):
        self.assertIn("SNPP", LAYER_SNPP_HISTORICAL)
        self.assertIn("noaa20", LAYER_NOAA20.lower())


if __name__ == "__main__":
    unittest.main()
