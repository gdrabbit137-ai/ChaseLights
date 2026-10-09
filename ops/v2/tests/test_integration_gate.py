"""Deterministic tests for Worker 5's V2 isolation gate; no network required."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integration_gate import check_local, check_public, check_v2_assets, v2_link


class V2IntegrationGateTests(unittest.TestCase):
    def root(self, tmp):
        root = Path(tmp)
        for name in ("index.html", "CNAME", "RESEARCH_EVIDENCE_SPEC_R4_2.md", "NAVIGATION_SPEC_R4_2.md"):
            (root / name).write_text("<html><title>Legacy</title></html>", encoding="utf-8")
        return root

    def test_legacy_only_is_pending_not_deployed(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(check_local(self.root(tmp)), ([], "v2_pending", False))

    def test_legacy_link_before_v2_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.root(tmp)
            (root / "index.html").write_text('<a href="./apps/web-v2/" data-i18n="v2_link">V2</a>', encoding="utf-8")
            errors, _, linked = check_local(root)
            self.assertTrue(linked)
            self.assertTrue(any("forbidden" in e for e in errors))

    def test_data_without_schema_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.root(tmp)
            (root / "data/v2").mkdir(parents=True)
            errors, _, _ = check_local(root)
            self.assertTrue(any("canonical" in e for e in errors))

    def test_local_v2_assets_must_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.root(tmp)
            (root / "specs/v2/schema").mkdir(parents=True)
            (root / "specs/v2/schema/opportunity-v2.1.schema.json").write_text("{}", encoding="utf-8")
            (root / "apps/web-v2").mkdir(parents=True)
            (root / "apps/web-v2/index.html").write_text('<title>ChaseLights V2</title><script src="./app.mjs"></script>', encoding="utf-8")
            errors, _, _ = check_local(root)
            self.assertTrue(any("missing" in e for e in errors))
            (root / "apps/web-v2/app.mjs").write_text("export {}", encoding="utf-8")
            self.assertEqual(check_local(root)[0], [])

    def test_path_escape_and_external_assets_blocked(self):
        html = '<title>V2</title><script src="../app.js"></script><script src="https://example.com/lib.js"></script>'
        self.assertEqual(len(check_v2_assets(html, lambda _: True)), 2)

    def test_legacy_v2_entry_rejects_external_origin(self):
        self.assertTrue(v2_link({"href": "./apps/web-v2/"}))
        self.assertTrue(v2_link({"href": "/apps/web-v2/"}))
        for href in ("https://evil.example/apps/web-v2/",
                     "//evil.example/apps/web-v2/",
                     "http://chaselights.app/apps/web-v2/"):
            with self.subTest(href=href):
                self.assertFalse(v2_link({"href": href}))

    def test_public_url_must_be_canonical(self):
        self.assertTrue(check_public("https://example.com/v2/"))
        self.assertTrue(check_public("http://chaselights.app/apps/web-v2/"))


if __name__ == "__main__":
    unittest.main()
