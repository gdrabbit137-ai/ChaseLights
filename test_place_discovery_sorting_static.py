import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class PlaceDiscoverySortingStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = (ROOT / "assets" / "app.js").read_text(encoding="utf-8")
        cls.css = (ROOT / "assets" / "app.css").read_text(encoding="utf-8")
        cls.index = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_sort_control_exposes_required_modes(self):
        for value in (
            'value="region"',
            'value="score_desc"',
            'value="score_asc"',
            'value="distance_near"',
            'value="distance_far"',
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.index)
        self.assertIn('onchange="setSortMode(this.value)"', self.index)

    def test_geographic_sort_is_safe_default(self):
        self.assertIn(
            "let currentSortMode=VALID_SORT_MODES.includes(storedSortMode)&&!storedSortMode.startsWith('distance_')?storedSortMode:'region'",
            self.app,
        )
        self.assertIn("if(currentSortMode==='region')return compareGeographic(a,b)", self.app)

    def test_geographic_browse_groups_are_country_aware(self):
        for needle in (
            "TW_BROWSE_AREA_GROUPS",
            "jp_hokkaido",
            "jp_kyushu_okinawa",
            "us_northeast",
            "us_west",
            "BROWSE_AREA_GROUPS",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.app)

    def test_distance_sort_requests_location_only_on_demand(self):
        self.assertIn("if(mode.startsWith('distance_')&&!userLocation)", self.app)
        self.assertIn("navigator.geolocation.getCurrentPosition(", self.app)
        self.assertIn("function setSortMode(mode)", self.app)
        self.assertNotIn("chaselights_user_location", self.app)
        self.assertNotIn("localStorage.setItem('chaselights_location", self.app)

    def test_zero_place_areas_are_hidden_by_default_but_revealable(self):
        self.assertIn("let showEmptyAdminAreas=false", self.app)
        self.assertIn(
            "group.areas.filter(a=>showEmptyAdminAreas||counts[a]>0||currentAdminAreas.has(a))",
            self.app,
        )
        self.assertIn("data-admin-empty-toggle", self.app)
        self.assertIn("admin_area_show_empty", self.app)

    def test_global_sorts_do_not_render_geographic_sections(self):
        self.assertIn("if(currentSortMode!=='region')", self.app)
        self.assertIn("rows.forEach(({spot,metric})=>target.appendChild(createSpotCard(spot,metric)))", self.app)
        self.assertIn("spot-region-section", self.app)
        self.assertIn("grid-column: 1 / -1", self.css)

    def test_cross_boundary_place_is_appended_once_per_sorted_row(self):
        self.assertIn("const grouped=new Map(),ungrouped=[]", self.app)
        self.assertIn("grouped.get(key).push(row)", self.app)
        self.assertIn("groupRows.forEach(({spot,metric})=>grid.appendChild(createSpotCard(spot,metric)))", self.app)


if __name__ == "__main__":
    unittest.main()
