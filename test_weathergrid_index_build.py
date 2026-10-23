"""Tests for the WeatherGrid cache index builder."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from weathergrid_index_build import build_index


class IndexBuildTests(unittest.TestCase):
    def _populate(self, root: Path):
        (root / "weathergrid").mkdir()
        g = root / "weathergrid"
        (g / "gfs_tw_weather_browser.json").write_text('{"a":1}')
        (g / "gfs_tw_weather_qc.json").write_text('{"b":2}')
        (g / "himawari9_tw_cloud_browser.json").write_text('{"c":3}')
        (g / "unrelated.txt").write_text("skip me")
        (g / "notes.md").write_text("skip me too")
        (g / "index.json").write_text("{}")

    def test_index_covers_only_published_bundles(self):
        with tempfile.TemporaryDirectory() as tmp:
            g = Path(tmp) / "weathergrid"
            self._populate(Path(tmp))
            index = build_index(g)
            self.assertEqual(set(index["files"]), {
                "gfs_tw_weather_browser.json",
                "gfs_tw_weather_qc.json",
                "himawari9_tw_cloud_browser.json",
            })

    def test_hashes_match_file_contents(self):
        with tempfile.TemporaryDirectory() as tmp:
            g = Path(tmp) / "weathergrid"
            self._populate(Path(tmp))
            index = build_index(g)
            entry = index["files"]["gfs_tw_weather_browser.json"]
            self.assertEqual(entry["sha256"],
                             hashlib.sha256(b'{"a":1}').hexdigest())
            self.assertEqual(entry["bytes"], 7)

    def test_removed_bundle_disappears_from_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            g = Path(tmp) / "weathergrid"
            self._populate(Path(tmp))
            (g / "himawari9_tw_cloud_browser.json").unlink()
            index = build_index(g)
            self.assertNotIn("himawari9_tw_cloud_browser.json", index["files"])

    def test_index_shape_is_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            g = Path(tmp) / "weathergrid"
            self._populate(Path(tmp))
            index = build_index(g)
            self.assertEqual(index["index_version"], 1)
            self.assertRegex(index["generated_at_utc"], r"^\d{4}-\d{2}-\d{2}T")
            for entry in index["files"].values():
                self.assertRegex(entry["sha256"], r"^[a-f0-9]{64}$")


if __name__ == "__main__":
    unittest.main()
