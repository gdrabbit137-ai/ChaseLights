import unittest

from weathergrid_v2_cache_index import JMA_DOMAIN, build_index, cells_for_region


class CacheIndexTest(unittest.TestCase):
    def test_regions_cover_target_countries(self):
        i = build_index()
        self.assertIn("tw", i["regions"])
        self.assertIn("jp", i["regions"])
        self.assertIn("us", i["regions"])
        self.assertIn("us_alaska", i["regions"])
        self.assertGreater(len(i["regions"]["jp"]["cells"]), 20)

    def test_provider_paths_follow_native_domains(self):
        index = build_index()
        jp = index["regions"]["jp"]["cells"]
        us = index["regions"]["us"]["cells"]
        self.assertTrue(all("gfs" in c["providers"] for c in jp + us))
        self.assertTrue(any("jma" in c["providers"] for c in jp))
        self.assertTrue(all("jma" not in c["providers"] for c in us))

    def test_partial_jma_cells_are_clipped_not_dropped(self):
        index = build_index()
        tw = index["regions"]["tw"]["cells"]
        partial = [
            c for c in tw
            if "jma" in c["providers"]
            and c["providers"]["jma"]["coverage_bbox"] != c["bbox"]
        ]
        self.assertTrue(partial)
        for cell in partial:
            b = cell["providers"]["jma"]["coverage_bbox"]
            self.assertGreaterEqual(b["west"], JMA_DOMAIN["west"])
            self.assertGreaterEqual(b["south"], JMA_DOMAIN["south"])
            self.assertLessEqual(b["east"], JMA_DOMAIN["east"])
            self.assertLessEqual(b["north"], JMA_DOMAIN["north"])

    def test_cell_bounds_do_not_exceed_region(self):
        index = build_index()
        for r in ("tw", "jp", "us", "us_alaska"):
            b = index["regions"][r]["bbox"]
            for c in cells_for_region(r):
                x = c["bbox"]
                self.assertGreaterEqual(x["west"], b["west"])
                self.assertLessEqual(x["east"], b["east"])
                self.assertGreaterEqual(x["south"], b["south"])
                self.assertLessEqual(x["north"], b["north"])


class TimeShardContract(unittest.TestCase):
    def test_payloads_are_valid_time_sharded(self):
        d = build_index()
        self.assertEqual(d["payload_partition"], "valid_time")
        cell = d["regions"]["jp"]["cells"][0]
        for p in cell["providers"].values():
            self.assertTrue(p["time_sharded"])
            self.assertIn("{valid_time}", p["url_template"])

    def test_provider_run_metadata_is_embedded(self):
        run = {
            "reference_time_utc": "2026-10-03T00:00:00Z",
            "default_valid_time_utc": "2026-10-03T01:00:00Z",
            "valid_times": [],
            "supported_fields": ["cloud_cover_low"],
        }
        d = build_index(provider_runs={"jma": run})
        self.assertEqual(d["provider_runs"]["jma"], run)


if __name__ == "__main__":
    unittest.main(verbosity=2)
