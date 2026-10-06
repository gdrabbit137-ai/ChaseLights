import unittest

from cwa_cloud_calibration import calibrate, collocate_snapshot


def cwa_bundle():
    fields = {
        name: {"scale": 1.0}
        for name in (
            "relative_humidity_925hpa_percent",
            "relative_humidity_850hpa_percent",
            "relative_humidity_2m_percent",
            "lcl_height_m_agl",
            "wind_speed_10m_m_s",
            "rh_cloud_potential_low_percent",
        )
    }
    frames = []
    for valid in ("2026-10-06T12:00:00Z", "2026-10-06T18:00:00Z"):
        frames.append(
            {
                "valid_time_utc": valid,
                "values": {
                    "relative_humidity_925hpa_percent": [95, 70, 92, 65],
                    "relative_humidity_850hpa_percent": [96, 98, 91, 70],
                    "relative_humidity_2m_percent": [90, 60, 88, 55],
                    "lcl_height_m_agl": [200, 1200, 250, 1500],
                    "wind_speed_10m_m_s": [2, 5, 3, 4],
                    "rh_cloud_potential_low_percent": [100, 100, 88, 0],
                },
            }
        )
    return {
        "grid": {
            "rows": 2,
            "cols": 2,
            "latitudes": [23.0, 23.02],
            "longitudes": [121.0, 121.02],
        },
        "fields": fields,
        "frames": frames,
    }


def himawari(slot):
    return {
        "observation": {"slot_utc": slot},
        "grid": {
            "rows": 2,
            "cols": 2,
            "latitudes": [23.0, 23.02],
            "longitudes": [121.0, 121.02],
        },
        "fields": {
            "cloud_top_height_m": {"scale": 100.0},
        },
        "values": {
            "observed_cloud_mask": [1, 0, 1, 0],
            "cloud_top_height_m": [10, None, 15, None],
        },
    }


class CwaLowCloudCalibrationTests(unittest.TestCase):
    def test_high_cloud_is_excluded_not_used_as_negative(self):
        h = himawari("2026-10-06T12:00:00Z")
        h["values"]["observed_cloud_mask"][1] = 1
        h["values"]["cloud_top_height_m"][1] = 80
        result = collocate_snapshot(cwa_bundle(), h)
        self.assertEqual(result["label_counts"]["positive_low_cloud"], 2)
        self.assertEqual(result["label_counts"]["negative_clear"], 1)
        self.assertEqual(result["label_counts"]["ambiguous_excluded"], 1)
        self.assertEqual(result["label_counts"]["usable"], 3)

    def test_two_slot_calibration_selects_layer_consistency_feature(self):
        result = calibrate(
            cwa_bundle(),
            [
                himawari("2026-10-06T12:00:00Z"),
                himawari("2026-10-06T18:00:00Z"),
            ],
        )
        self.assertIn(
            result["selected_candidate"]["feature"],
            {
                "rh_min",
                "rh_avg",
                "rh_avg_spread25",
                "rh_avg_spread50",
                "rh_avg_spread75",
            },
        )
        self.assertEqual(result["split"]["validation_slot"], "2026-10-06T18:00:00Z")
        self.assertIsNotNone(result["validation"])
        self.assertEqual(
            {item["feature"] for item in result["validation_candidates"]},
            {
                "rh_min",
                "rh_avg",
                "rh_avg_spread25",
                "rh_avg_spread50",
                "rh_avg_spread75",
            },
        )
        self.assertGreater(
            result["validation"]["candidate"]["specificity"],
            result["validation"]["baseline"]["specificity"],
        )
        self.assertTrue(result["semantics"]["not_native_cloud_fraction"])
        self.assertTrue(result["semantics"]["not_photography_opportunity_scoring"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
