import tempfile
import unittest
from pathlib import Path

import h5py

from viirs_nightlights_ingest import GROUP, ingest
from viirs_nightlights_weathergrid import FIELD_RADIANCE


class ViirsNightLightsIngestTest(unittest.TestCase):
    def make_tile(self, path):
        with h5py.File(path, "w") as h5:
            group = h5.require_group(GROUP)
            group.create_dataset("lat", data=[25.5, 25.0, 24.5, 24.0])
            group.create_dataset("lon", data=[120.0, 120.5, 121.0, 121.5])
            radiance = group.create_dataset(
                "AllAngle_Composite_Snow_Free",
                data=[
                    [1.0, 2.0, 3.0, 4.0],
                    [5.0, 6.0, 7.0, 8.0],
                    [9.0, 10.0, -999.9, 12.0],
                    [13.0, 14.0, 15.0, 16.0],
                ],
            )
            radiance.attrs["_FillValue"] = -999.9
            radiance.attrs["scale_factor"] = 1.0
            radiance.attrs["offset"] = 0.0
            quality = group.create_dataset(
                "AllAngle_Composite_Snow_Free_Quality",
                data=[
                    [0, 0, 0, 0],
                    [0, 0, 1, 0],
                    [0, 2, 255, 0],
                    [0, 0, 0, 0],
                ],
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
        self.assertEqual(
            bundle["frames"][0]["values"][FIELD_RADIANCE],
            [60, 70, 100, None],
        )
        self.assertEqual(qc["quality_counts"]["poor"], 1)
        self.assertEqual(qc["quality_counts"]["gap_filled"], 1)
        self.assertEqual(qc["quality_counts"]["fill"], 1)

    def test_non_intersecting_bbox_fails(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "VNP46A4.synthetic.h5"
            self.make_tile(path)
            with self.assertRaises(ValueError):
                ingest(path, (130, 30, 131, 31), 2025)


if __name__ == "__main__":
    unittest.main()
