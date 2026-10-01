import tempfile
import unittest
from pathlib import Path

import h5py

from viirs_nightlights_ingest import GROUP, ingest, ingest_many
from viirs_nightlights_weathergrid import FIELD_RADIANCE


class ViirsNightLightsIngestTest(unittest.TestCase):
    def make_tile(self, path, lons=(120.0, 120.5, 121.0, 121.5), base=0.0):
        lats = [25.5, 25.0, 24.5, 24.0]
        with h5py.File(path, "w") as h5:
            group = h5.require_group(GROUP)
            group.create_dataset("lat", data=lats)
            group.create_dataset("lon", data=list(lons))
            data = []
            quality_data = []
            for row in range(len(lats)):
                data.append([base + row * len(lons) + col + 1 for col in range(len(lons))])
                quality_data.append([0 for _ in lons])
            radiance = group.create_dataset("AllAngle_Composite_Snow_Free", data=data)
            radiance.attrs["_FillValue"] = -999.9
            radiance.attrs["scale_factor"] = 1.0
            radiance.attrs["offset"] = 0.0
            quality = group.create_dataset(
                "AllAngle_Composite_Snow_Free_Quality",
                data=quality_data,
                dtype="u1",
            )
            quality.attrs["_FillValue"] = 255

    def test_crop_and_decode_real_hdf_structure(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "VNP46A4.synthetic.h5"
            self.make_tile(path)
            bundle, qc = ingest(path, (120.5, 24.5, 121.0, 25.0), 2025)

        self.assertEqual(bundle["grid"]["rows"], 2)
        self.assertEqual(bundle["grid"]["cols"], 2)
        self.assertEqual(bundle["grid"]["latitudes"], [25.0, 24.5])
        self.assertEqual(bundle["grid"]["longitudes"], [120.5, 121.0])
        self.assertEqual(bundle["frames"][0]["values"][FIELD_RADIANCE], [60, 70, 100, 110])
        self.assertEqual(bundle["provenance"]["source_tile_count"], 1)
        self.assertEqual(qc["source_tile_count"], 1)

    def test_two_adjacent_tiles_mosaic_without_losing_boundary_area(self):
        with tempfile.TemporaryDirectory() as td:
            west = Path(td) / "VNP46A4.A2025001.h29v06.002.synthetic.h5"
            east = Path(td) / "VNP46A4.A2025001.h30v06.002.synthetic.h5"
            self.make_tile(west, lons=(119.0, 119.5, 120.0), base=0)
            self.make_tile(east, lons=(120.5, 121.0, 121.5), base=100)
            bundle, qc = ingest_many(
                [west, east],
                (119.5, 24.5, 121.0, 25.0),
                2025,
            )

        self.assertEqual(bundle["grid"]["latitudes"], [25.0, 24.5])
        self.assertEqual(bundle["grid"]["longitudes"], [119.5, 120.0, 120.5, 121.0])
        self.assertEqual(bundle["grid"]["rows"], 2)
        self.assertEqual(bundle["grid"]["cols"], 4)
        self.assertEqual(bundle["provenance"]["source_tile_count"], 2)
        self.assertEqual(qc["source_tile_count"], 2)
        self.assertEqual(
            bundle["frames"][0]["values"][FIELD_RADIANCE],
            [50, 60, 1040, 1050, 80, 90, 1070, 1080],
        )

    def test_non_intersecting_bbox_fails(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "VNP46A4.synthetic.h5"
            self.make_tile(path)
            with self.assertRaises(ValueError):
                ingest(path, (130, 30, 131, 31), 2025)

    def test_conflicting_overlap_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            a = Path(td) / "a.h5"
            b = Path(td) / "b.h5"
            self.make_tile(a, lons=(120.0, 120.5), base=0)
            self.make_tile(b, lons=(120.5, 121.0), base=100)
            with self.assertRaisesRegex(ValueError, "conflicting VNP46A4 mosaic cell"):
                ingest_many([a, b], (120.0, 24.0, 121.0, 25.5), 2025)


if __name__ == "__main__":
    unittest.main()
