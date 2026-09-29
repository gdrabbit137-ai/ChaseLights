import unittest
from urllib.parse import parse_qs, urlparse

from gfs_raw_poc import GFSRun
from gfs_multilayer_poc import (
    FIELD_SPECS,
    REQUEST_PARAMS,
    build_multilayer_url,
    sample_field_bilinear,
    sample_field_nearest,
)


class GFSMultilayerPOCTest(unittest.TestCase):
    def test_request_contains_expected_variables_and_levels(self):
        url = build_multilayer_url(GFSRun("20260929", "00", 6))
        query = parse_qs(urlparse(url).query)

        for key in [
            "var_LCDC", "var_MCDC", "var_HCDC",
            "var_VIS", "var_PRATE", "var_UGRD", "var_VGRD",
            "lev_low_cloud_layer", "lev_middle_cloud_layer",
            "lev_high_cloud_layer", "lev_surface", "lev_10_m_above_ground",
        ]:
            self.assertEqual(query[key], ["on"], key)

        self.assertEqual(query["file"], ["gfs.t00z.pgrb2.0p25.f006"])
        self.assertEqual(query["dir"], ["/gfs.20260929/00/atmos"])

    def test_field_contract_contains_all_photography_basics(self):
        self.assertEqual(
            set(FIELD_SPECS),
            {
                "low_cloud_percent",
                "mid_cloud_percent",
                "high_cloud_percent",
                "visibility_km",
                "precip_rate_mm_h",
                "wind_u_10m_m_s",
                "wind_v_10m_m_s",
            },
        )

    def test_generic_sampling(self):
        field = {
            "latitudes": [25.0, 24.75],
            "longitudes": [121.0, 121.25],
            "values": [
                [0.0, 20.0],
                [40.0, 60.0],
            ],
        }
        nearest = sample_field_nearest(field, 24.79, 121.22)
        self.assertEqual(nearest["value"], 60.0)
        self.assertEqual(nearest["grid_lat"], 24.75)
        self.assertEqual(nearest["grid_lon"], 121.25)

        bilinear = sample_field_bilinear(field, 24.875, 121.125)
        self.assertAlmostEqual(bilinear, 30.0, places=2)


if __name__ == "__main__":
    unittest.main()
