"""Acceptance-verifier regressions; synthetic timestamps, never live evidence."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nws_provider_acceptance import event_instant, interval


class PrecisionChecks(unittest.TestCase):
    def test_documented_second_serialization_preserves_exact_solar_instant(self):
        exact = event_instant('2026-10-20T01:13:25Z', '2026-10-20T01:13:25.716934Z')
        self.assertEqual(exact.microsecond, 716934)
        start, end = interval('2026-10-20T00:00:00+00:00/PT3H')
        self.assertTrue(start <= exact < end)

    def test_one_second_shift_is_rejected(self):
        for serialized in ('2026-10-20T01:13:24Z', '2026-10-20T01:13:26Z'):
            with self.assertRaisesRegex(ValueError, 'differs beyond'):
                event_instant(serialized, '2026-10-20T01:13:25.716934Z')

    def test_native_end_is_exclusive_without_hour_rounding(self):
        start, end = interval('2026-10-20T00:00:00Z/PT1H')
        before = event_instant('2026-10-20T00:59:59Z', '2026-10-20T00:59:59.999999Z')
        boundary = event_instant('2026-10-20T01:00:00Z', '2026-10-20T01:00:00Z')
        self.assertTrue(start <= before < end)
        self.assertFalse(start <= boundary < end)


if __name__ == '__main__':
    unittest.main()
