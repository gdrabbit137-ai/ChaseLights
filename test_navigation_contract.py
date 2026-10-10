import unittest

from regions import NAVIGATION_TARGET_OVERRIDES, REGIONS, get_spots

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

    def test_shinhotaka_directions_use_base_station_not_summit_camera_zone(self):
        spot = next(
            s for s in get_spots("jp")
            if s["name_i18n"]["zh-TW"] == "新穗高・西穗高口展望台"
        )
        target = spot["navigation_target"]
        self.assertEqual("verified", target["status"])
        self.assertEqual("station", target["target_type"])
        self.assertAlmostEqual(36.2858894, float(target["lat"]), places=6)
        self.assertAlmostEqual(137.5753158, float(target["lon"]), places=6)
        self.assertNotEqual((float(spot["lat"]), float(spot["lon"])), (float(target["lat"]), float(target["lon"])))

    def test_default_target_for_unreviewed_coordinate_is_provisional(self):
        reviewed_spot_ids = {
            f"{region}-{index:03d}"
            for region in ("tw", "jp", "us")
            for index, raw_spot in enumerate(REGIONS[region]["spots"], start=1)
            if raw_spot[2] in NAVIGATION_TARGET_OVERRIDES
        }
        for spot in self.all_spots():
            if spot["spot_id"] in reviewed_spot_ids:
                continue
            target = spot["navigation_target"]
            with self.subTest(spot_id=spot["spot_id"]):
                self.assertEqual("provisional_camera_anchor", target["status"])
                self.assertEqual("camera_zone_or_place_anchor", target["target_type"])
                self.assertEqual(float(spot["lat"]), float(target["lat"]))
                self.assertEqual(float(spot["lon"]), float(target["lon"]))


if __name__ == "__main__":
    unittest.main()
