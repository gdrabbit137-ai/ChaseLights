import unittest

from regions import NAVIGATION_TARGET_OVERRIDES, get_spots

STATUSES = {"verified", "provisional_camera_anchor", "needs_review", "multiple_access_routes"}
TARGET_TYPES = {"entrance", "trailhead", "parking", "station", "street_access", "viewpoint", "camera_zone_or_place_anchor"}
CONFIDENCES = {"high", "medium", "low"}
LOCALES = {"zh-TW", "en", "ja"}


class NavigationContractTests(unittest.TestCase):
    def all_spots(self):
        for region in ("tw", "jp", "us"):
            yield from get_spots(region)

    def test_contract_enums_and_locale_parity(self):
        for spot in self.all_spots():
            target = spot["navigation_target"]
            with self.subTest(spot_id=spot["spot_id"]):
                self.assertIn(target.get("status"), STATUSES)
                self.assertIn(target.get("target_type"), TARGET_TYPES)
                self.assertIn(target.get("confidence"), CONFIDENCES)
                self.assertEqual(LOCALES, set(target["label_i18n"]))
                self.assertTrue(all(target["label_i18n"].values()))
                if "note_i18n" in target:
                    self.assertEqual(LOCALES, set(target["note_i18n"]))
                    self.assertTrue(all(target["note_i18n"].values()))

    def test_verified_targets_have_valid_arrival_coordinates(self):
        for spot in self.all_spots():
            target = spot["navigation_target"]
            if target["status"] != "verified":
                continue
            with self.subTest(spot_id=spot["spot_id"]):
                self.assertTrue(-90 <= float(target["lat"]) <= 90)
                self.assertTrue(-180 <= float(target["lon"]) <= 180)
                self.assertNotEqual("camera_zone_or_place_anchor", target["target_type"])

    def test_default_target_for_unreviewed_coordinate_is_provisional(self):
        reviewed = set(NAVIGATION_TARGET_OVERRIDES)
        for spot in self.all_spots():
            source_name = spot["name_local"]
            if source_name in reviewed or spot["name_i18n"]["zh-TW"] in reviewed:
                continue
            target = spot["navigation_target"]
            with self.subTest(spot_id=spot["spot_id"]):
                self.assertEqual("provisional_camera_anchor", target["status"])
                self.assertEqual("camera_zone_or_place_anchor", target["target_type"])
                self.assertEqual(float(spot["lat"]), float(target["lat"]))
                self.assertEqual(float(spot["lon"]), float(target["lon"]))


if __name__ == "__main__":
    unittest.main()
