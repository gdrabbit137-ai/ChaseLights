import http.cookiejar
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import patch

from viirs_lads_download import (
    archive_url,
    authenticated_opener,
    authorization_headers,
    extract_filenames,
    extract_file_references,
    download_file,
    search_url,
)


class ViirsLadsDownloadTest(unittest.TestCase):
    def test_search_url_uses_product_year_and_bbox(self):
        url = search_url(2025, (119.5, 21.5, 122.5, 25.5))
        self.assertIn("products=VNP46A4", url)
        self.assertIn("archiveSets=5200", url)
        self.assertIn("2025-001..2025-001", url)
        self.assertIn("%5BBBOX%5D", url)

    def test_extract_filenames_is_shape_tolerant(self):
        payload = {
            "content": [
                {"name": "VNP46A4.A2025001.h30v06.002.2026261093500.h5"},
                {"download": "/x/VNP46A4.A2025001.h31v06.002.2026261093501.h5"},
                {"name": "README"},
            ]
        }
        self.assertEqual(
            extract_filenames(payload),
            [
                "VNP46A4.A2025001.h30v06.002.2026261093500.h5",
                "VNP46A4.A2025001.h31v06.002.2026261093501.h5",
            ],
        )

    def test_extract_file_references_preserves_exact_laads_value(self):
        value = "/archive/path/VNP46A4.A2025001.h30v06.002.2026261093500.h5"
        refs = extract_file_references({"content": [{"downloadsLink": value}]})
        self.assertEqual(refs, [{
            "filename": "VNP46A4.A2025001.h30v06.002.2026261093500.h5",
            "reference": value,
        }])

    def test_extract_file_references_preserves_laads_download_url(self):
        ref = "https://ladsweb.modaps.eosdis.nasa.gov/api/v2/content/archives/VNP46A4.A2025001.h30v06.002.2026261093501.h5"
        self.assertEqual(
            extract_file_references({"download": ref}),
            [{"filename": "VNP46A4.A2025001.h30v06.002.2026261093501.h5", "reference": ref}],
        )

    def test_archive_url_uses_collection2_year_day_tree(self):
        filename = "VNP46A4.A2025001.h30v06.002.2026261093500.h5"
        self.assertEqual(
            archive_url(filename),
            "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/5200/VNP46A4/2025/001/" + filename,
        )

    def test_archive_url_rejects_unexpected_filename(self):
        with self.assertRaises(ValueError):
            archive_url("../README")

    def test_token_header_uses_bearer_without_logging_token(self):
        headers = authorization_headers("secret-value")
        self.assertEqual(headers["Authorization"], "Bearer secret-value")
        self.assertEqual(headers["X-Requested-With"], "XMLHttpRequest")

    def test_authenticated_opener_installs_cookie_processor(self):
        opener = authenticated_opener()
        processors = [handler for handler in opener.handlers if isinstance(handler, urllib.request.HTTPCookieProcessor)]
        self.assertEqual(len(processors), 1)
        self.assertIsInstance(processors[0].cookiejar, http.cookiejar.CookieJar)

    @patch("viirs_lads_download.subprocess.run")
    def test_download_uses_nasa_documented_curl_edl_flow(self, run):
        filename = "VNP46A4.A2025001.h30v06.002.2026261093500.h5"
        destination = Path(".cache/test") / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"\\x89HDF\\r\\n\\x1a\\n")
        discovery_reference = (
            "https://ladsweb.modaps.eosdis.nasa.gov/api/v2/content/archives/" + filename
        )
        download_file(filename, "secret-value", destination, reference=discovery_reference)
        command = run.call_args.args[0]
        self.assertEqual(command[0], "curl")
        self.assertIn("--location", command)
        self.assertIn("--cookie", command)
        self.assertIn("Authorization: Bearer secret-value", command)
        self.assertIn(str(destination), command)
        self.assertIn(archive_url(filename), command)
        self.assertNotIn(discovery_reference, command)
        self.assertTrue(run.call_args.kwargs["check"])

    @patch("viirs_lads_download.subprocess.run")
    def test_download_rejects_non_hdf5_payload(self, run):
        filename = "VNP46A4.A2025001.h30v06.002.2026261093500.h5"
        destination = Path(".cache/test-invalid") / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("<html>Earthdata login</html>")
        with self.assertRaisesRegex(RuntimeError, "did not return an HDF5 payload"):
            download_file(filename, "secret-value", destination)
        self.assertFalse(destination.exists())

    def test_missing_token_fails_closed(self):
        with self.assertRaises(ValueError):
            authorization_headers(None)


if __name__ == "__main__":
    unittest.main()
