import unittest

from viirs_lads_download import (
    authorization_headers,
    extract_filenames,
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

    def test_token_header_uses_bearer_without_logging_token(self):
        headers = authorization_headers("secret-value")
        self.assertEqual(headers["Authorization"], "Bearer secret-value")
        self.assertEqual(headers["X-Requested-With"], "XMLHttpRequest")

    def test_missing_token_fails_closed(self):
        with self.assertRaises(ValueError):
            authorization_headers(None)


if __name__ == "__main__":
    unittest.main()
