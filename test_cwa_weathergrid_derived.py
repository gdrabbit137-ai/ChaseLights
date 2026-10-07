import unittest

import numpy as np

from cwa_weathergrid_derived import (
    HIGH_RH_LEVELS_HPA,
    LOW_RH_LEVELS_HPA,
    MID_RH_LEVELS_HPA,
    derive_cwa_photography_fields,
    lcl_height_m_agl,
)


def field(values):
    return {
        "latitudes": [23.0, 23.03],
        "longitudes": [120.0, 120.03],
        "values": values,
        "field_attrs": {"normalized_units": "%"},
    }


class CwaWeatherGridDerivedTests(unittest.TestCase):
    def test_pressure_bands_are_explicit_and_nonoverlapping(self):
        self.assertEqual(LOW_RH_LEVELS_HPA, (925, 850))
        self.assertEqual(MID_RH_LEVELS_HPA, (700, 500))
        self.assertEqual(HIGH_RH_LEVELS_HPA, (400, 300))

    def test_lcl_drops_as_surface_air_approaches_saturation(self):
        humid = float(lcl_height_m_agl([[20.0]], [[98.0]])[0, 0])
        dry = float(lcl_height_m_agl([[20.0]], [[60.0]])[0, 0])
        self.assertLess(humid, dry)
        self.assertLess(humid, 100.0)
        self.assertGreater(dry, 500.0)

    def test_derives_cloud_lcl_and_fog_products_without_calling_them_cloud_cover(self):
        fields = {
            "temperature_2m_c": field([[20.0, 20.0], [20.0, 20.0]]),
            "relative_humidity_2m_percent": field([[98.0, 75.0], [92.0, 60.0]]),
            "wind_speed_10m_m_s": field([[0.5, 5.0], [1.5, 8.0]]),
        }
        level_values = {
            925: [[98.0, 80.0], [95.0, 70.0]],
            850: [[96.0, 75.0], [90.0, 65.0]],
            700: [[85.0, 75.0], [80.0, 70.0]],
            500: [[80.0, 72.0], [78.0, 65.0]],
            400: [[75.0, 70.0], [68.0, 60.0]],
            300: [[72.0, 68.0], [65.0, 55.0]],
        }
        for level, values in level_values.items():
            fields[f"relative_humidity_{level}hpa_percent"] = field(values)

        out = derive_cwa_photography_fields(fields)
        self.assertEqual(
            set(out),
            {
                "rh_cloud_potential_low_percent",
                "rh_cloud_potential_mid_percent",
                "rh_cloud_potential_high_percent",
                "lcl_height_m_agl",
                "fog_potential_percent",
            },
        )
        self.assertGreater(out["rh_cloud_potential_low_percent"]["values"][0][0], 90.0)
        self.assertGreater(
            out["fog_potential_percent"]["values"][0][0],
            out["fog_potential_percent"]["values"][1][1],
        )
        for item in out.values():
            attrs = item["field_attrs"]
            self.assertEqual(attrs["product_type"], "derived_proxy")
            self.assertFalse(attrs["native_cloud_fraction"])
            self.assertNotIn("cloud cover", attrs["long_name"].lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
