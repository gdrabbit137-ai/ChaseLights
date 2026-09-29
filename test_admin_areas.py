import unittest

from regions import get_spots


class AdminAreaMetadataTests(unittest.TestCase):
    def _spots_by_id(self, region):
        return {spot["spot_id"]: spot for spot in get_spots(region)}

    def test_all_supported_regions_emit_admin_areas(self):
        for region in ("tw", "jp", "us"):
            with self.subTest(region=region):
                spots = get_spots(region)
                self.assertTrue(spots)
                missing = [spot["spot_id"] for spot in spots if not spot.get("admin_areas")]
                self.assertEqual([], missing)

    def test_japan_uses_prefecture_level_areas(self):
        spots = self._spots_by_id("jp")
        self.assertEqual(["山梨県"], spots["jp-010"]["admin_areas"])
        self.assertEqual(["東京都"], spots["jp-011"]["admin_areas"])
        self.assertEqual(["青森県", "秋田県"], spots["jp-007"]["admin_areas"])

    def test_us_uses_state_level_areas(self):
        spots = self._spots_by_id("us")
        self.assertEqual(["Arizona"], spots["us-001"]["admin_areas"])
        self.assertEqual(["California"], spots["us-015"]["admin_areas"])
        self.assertEqual(["Alaska"], spots["us-041"]["admin_areas"])
        self.assertEqual(["California", "Nevada"], spots["us-014"]["admin_areas"])
        self.assertEqual(
            ["Tennessee", "North Carolina"],
            spots["us-038"]["admin_areas"],
        )

    def test_taiwan_boundary_places_are_multi_area(self):
        spots = self._spots_by_id("tw")
        self.assertEqual(["南投縣", "花蓮縣"], spots["tw-019"]["admin_areas"])

    def test_admin_areas_are_nonempty_unique_lists(self):
        for region in ("tw", "jp", "us"):
            for spot in get_spots(region):
                areas = spot["admin_areas"]
                self.assertIsInstance(areas, list)
                self.assertTrue(areas)
                self.assertEqual(len(areas), len(set(areas)))

    def test_legacy_macro_categories_remain_data_only(self):
        jp = self._spots_by_id("jp")
        us = self._spots_by_id("us")
        self.assertEqual("關東/中部", jp["jp-010"]["category"])
        self.assertEqual("美西", us["us-001"]["category"])


if __name__ == "__main__":
    unittest.main()
