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
            # CL-DATA-08: pressure-level U/V for the particle-flow layer.
            "lev_925_mb", "lev_850_mb", "lev_700_mb",
        ]:
            self.assertEqual(query[key], ["on"], key)

        self.assertEqual(query["file"], ["gfs.t00z.pgrb2.0p25.f006"])
        self.assertEqual(query["dir"], ["/gfs.20260929/00/atmos"])

    def test_request_accepts_subject_aware_custom_bbox(self):
        bbox = {
            "leftlon": 121.25,
            "rightlon": 122.0,
            "bottomlat": 23.75,
            "toplat": 24.5,
        }
        url = build_multilayer_url(
            GFSRun("20260929", "00", 3),
            bbox=bbox,
        )
        query = parse_qs(urlparse(url).query)
        self.assertEqual(query["leftlon"], ["121.25"])
        self.assertEqual(query["rightlon"], ["122.0"])
        self.assertEqual(query["bottomlat"], ["23.75"])
        self.assertEqual(query["toplat"], ["24.5"])

    def test_field_contract_contains_all_photography_basics(self):
        self.assertEqual(
            set(FIELD_SPECS),
            {
                "total_cloud_percent",
                "low_cloud_percent",
                "mid_cloud_percent",
                "high_cloud_percent",
                "visibility_km",
                "precip_rate_mm_h",
                "wind_u_10m_m_s",
                "wind_v_10m_m_s",
                # CL-DATA-08: pressure-level U/V vector components.
                "wind_u_925hpa_m_s", "wind_v_925hpa_m_s",
                "wind_u_850hpa_m_s", "wind_v_850hpa_m_s",
                "wind_u_700hpa_m_s", "wind_v_700hpa_m_s",
            },
        )

    def test_pressure_level_uv_specs_pin_exact_hpa_levels(self):
        from gfs_multilayer_poc import _field_candidates
        import types

        def fake_array(level, type_of_level, short):
            attrs = {
                "GRIB_shortName": short,
                "GRIB_typeOfLevel": type_of_level,
                "GRIB_level": level,
            }
            arr = types.SimpleNamespace()
            arr.attrs = attrs
            arr.ndim = 2
            arr.values = [[0.0, 0.0], [0.0, 0.0]]
            return arr

        ds = types.SimpleNamespace()
        ds.data_vars = {
            "u925": fake_array(925, "isobaricInhPa", "u"),
            "u850": fake_array(850, "isobaricInhPa", "u"),
            "u10": fake_array(10, "heightAboveGround", "u"),
        }
        spec = FIELD_SPECS["wind_u_925hpa_m_s"]
        best = _field_candidates([ds], spec)[0]
        self.assertEqual(best[2], "u925",
            "the 925 hPa U spec must select exactly the 925 hPa GRIB message")
        spec10 = FIELD_SPECS["wind_u_10m_m_s"]
        best10 = _field_candidates([ds], spec10)[0]
        self.assertEqual(best10[2], "u10",
            "the 10 m U spec must keep selecting the heightAboveGround message")

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
