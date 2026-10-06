import unittest

from cwa_wrf3_poc import (
    CWA_BROWSER_GRID_DEG,
    CWA_NATIVE_DOMAIN_REFERENCE,
    CWA_MODEL_FORECAST_HORIZON_HOURS,
    CWA_MODEL_OUTPUT_INTERVAL_HOURS,
    CWA_PUBLIC_FORECAST_HORIZON_HOURS,
    CWA_PUBLIC_FORECAST_INTERVAL_HOURS,
    CWA_PRESSURE_RH_LEVELS_HPA,
    CWA_NATIVE_RESOLUTION_KM,
    CWA_TAIWAN_BROWSER_BBOX,
    CORE_FIELD_SPECS,
    OPTIONAL_FIELD_SPECS,
    candidate_s3_keys,
    dataset_id,
    legacy_public_url,
    validate_forecast_hours,
)


class CwaWrf3ProviderTests(unittest.TestCase):
    def test_official_resolution_cadence_and_horizon_contract(self):
        self.assertEqual(CWA_NATIVE_RESOLUTION_KM, 3.0)
        self.assertEqual(CWA_MODEL_OUTPUT_INTERVAL_HOURS, 1)
        self.assertEqual(CWA_MODEL_FORECAST_HORIZON_HOURS, 126)
        self.assertEqual(CWA_PUBLIC_FORECAST_INTERVAL_HOURS, 6)
        self.assertEqual(CWA_PUBLIC_FORECAST_HORIZON_HOURS, 84)
        self.assertEqual(
            CWA_NATIVE_DOMAIN_REFERENCE["grid_shape"],
            [673, 1158],
        )

    def test_public_product_hours_follow_six_hour_cadence(self):
        self.assertEqual(
            validate_forecast_hours([0, 6, 12, 84]),
            [0, 6, 12, 84],
        )
        with self.assertRaises(ValueError):
            validate_forecast_hours([3])
        with self.assertRaises(ValueError):
            validate_forecast_hours([90])

    def test_dataset_id_and_public_paths_use_a0064(self):
        self.assertEqual(dataset_id(0), "M-A0064-000")
        self.assertEqual(dataset_id(84), "M-A0064-084")
        keys = candidate_s3_keys(6)
        self.assertIn("MIC/M-A0064-006.grb2", keys)
        self.assertTrue(any(x.startswith("Model/") for x in keys))
        self.assertIn(
            "/MIC/M-A0064-006.grb2",
            legacy_public_url(6),
        )

    def test_browser_bbox_is_provider_owned(self):
        self.assertLess(CWA_TAIWAN_BROWSER_BBOX["leftlon"], 120)
        self.assertGreater(CWA_TAIWAN_BROWSER_BBOX["rightlon"], 124)
        self.assertEqual(CWA_BROWSER_GRID_DEG, 0.03)

    def test_pressure_level_rh_contract(self):
        self.assertEqual(
            CWA_PRESSURE_RH_LEVELS_HPA,
            (1000, 925, 850, 700, 500, 400, 300),
        )

    def test_surface_fields_match_cwa_wrf_strengths(self):
        self.assertIn("temperature_2m_c", CORE_FIELD_SPECS)
        self.assertIn("relative_humidity_2m_percent", CORE_FIELD_SPECS)
        self.assertIn("wind_u_10m_m_s", CORE_FIELD_SPECS)
        self.assertIn("wind_v_10m_m_s", CORE_FIELD_SPECS)
        self.assertIn("precip_total_mm", OPTIONAL_FIELD_SPECS)
        self.assertIn("shortwave_flux_w_m2", OPTIONAL_FIELD_SPECS)
        self.assertIn("snswrf", OPTIONAL_FIELD_SPECS["shortwave_flux_w_m2"]["aliases"])


if __name__ == "__main__":
    unittest.main()
