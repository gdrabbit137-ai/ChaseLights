import tempfile
import unittest
from pathlib import Path

from weathergrid_v2_gfs_pack import (
    GFS_BINARY_TILE_DEG,
    MISSING_UINT8,
    encode_cloud_tile,
    global_binary_cells,
)


def synthetic_decoded():
    # Deliberately use the native-style 0..360 longitude convention and
    # descending latitude to prove the packer normalizes both axes.
    lat = [1.0, 0.0, -1.0]
    lon = [358.0, 359.0, 0.0, 1.0]
    base = [
        [10, 20, 30, 40],
        [11, 21, 31, 41],
        [12, 22, 32, 42],
    ]
    out = {}
    for offset, field in enumerate(
        ("cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high")
    ):
        values = [[value + offset for value in row] for row in base]
        out[field] = {"latitudes": lat, "longitudes": lon, "values": values}
    return out


class GfsBinaryPackTests(unittest.TestCase):
    def test_global_30_degree_partition_is_72_cells(self):
        self.assertEqual(GFS_BINARY_TILE_DEG, 30.0)
        cells = global_binary_cells()
        self.assertEqual(len(cells), 12 * 6)
        self.assertEqual(len({c["id"] for c in cells}), len(cells))

    def test_western_longitude_tile_normalizes_0_360_axis(self):
        cell = {
            "id": "test",
            "bbox": {"west": -2.0, "south": -1.0, "east": 0.0, "north": 2.0},
        }
        payload, meta = encode_cloud_tile(synthetic_decoded(), cell)
        self.assertEqual(meta["rows"], 3)
        self.assertEqual(meta["cols"], 2)
        self.assertEqual(meta["lon_start"], -2.0)
        self.assertEqual(meta["lon_end"], -1.0)
        self.assertEqual(len(payload), 3 * 2 * 4)

    def test_missing_value_is_reserved_255(self):
        decoded = synthetic_decoded()
        decoded["cloud_cover"]["values"][0][0] = float("nan")
        cell = {
            "id": "test",
            "bbox": {"west": -2.0, "south": -1.0, "east": 0.0, "north": 2.0},
        }
        payload, _ = encode_cloud_tile(decoded, cell)
        self.assertIn(MISSING_UINT8, payload)

    def test_incomplete_fields_fail_closed(self):
        decoded = synthetic_decoded()
        del decoded["cloud_cover_high"]
        cell = {
            "id": "test",
            "bbox": {"west": -2.0, "south": -1.0, "east": 0.0, "north": 2.0},
        }
        with self.assertRaises(ValueError):
            encode_cloud_tile(decoded, cell)


if __name__ == "__main__":
    unittest.main(verbosity=2)
