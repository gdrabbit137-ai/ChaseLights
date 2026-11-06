"""CL-CI-20: the LAADS path is a documented DEAD END and must fail closed."""
import unittest
from pathlib import Path

from viirs_lads_download import DEAD_END_REASON, fail_dead_end, main


class ViirsLadsDeadEndTest(unittest.TestCase):
    def test_module_fails_closed_with_dead_end_reason(self):
        with self.assertRaises(SystemExit) as ctx:
            main()
        self.assertIn("dead end", str(ctx.exception))
        self.assertIn("terminated 2026-11-01", str(ctx.exception))
        self.assertIn("VNP46A4", str(ctx.exception))

    def test_dead_end_reason_documents_product_lifecycle_and_replacement(self):
        self.assertIn("product lifecycle", DEAD_END_REASON)
        self.assertIn("viirs_gibs_download.py", DEAD_END_REASON)

    def test_no_laads_network_code_survives(self):
        import viirs_lads_download as module
        source = Path(module.__file__).read_text(encoding="utf-8")
        self.assertNotIn("ladsweb.modaps.eosdis.nasa.gov", source)
        self.assertNotIn("urllib.request", source)
        self.assertNotIn("Authorization", source)


if __name__ == "__main__":
    unittest.main()
