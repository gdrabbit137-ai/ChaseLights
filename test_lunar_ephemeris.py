import unittest
from datetime import datetime, timezone

from lunar_ephemeris import lunar_ephemeris, lunar_ephemeris_for_galactic_core


class LunarEphemerisTest(unittest.TestCase):
    def setUp(self):
        self.dt = datetime(2026, 9, 28, 12, 0, tzinfo=timezone.utc)

    def test_contract_is_deterministic_and_bounded(self):
        a = lunar_ephemeris_for_galactic_core(self.dt, 25.033, 121.5654)
        b = lunar_ephemeris_for_galactic_core(self.dt, 25.033, 121.5654)
        self.assertEqual(a, b)
        self.assertGreaterEqual(a["moon_altitude_deg"], -90)
        self.assertLessEqual(a["moon_altitude_deg"], 90)
        self.assertGreaterEqual(a["moon_illumination_fraction"], 0)
        self.assertLessEqual(a["moon_illumination_fraction"], 1)
        self.assertGreaterEqual(a["moon_target_separation_deg"], 0)
        self.assertLessEqual(a["moon_target_separation_deg"], 180)
        self.assertFalse(a["scientific_astrometry"])

    def test_timezone_equivalent_instants_match(self):
        utc = lunar_ephemeris_for_galactic_core(self.dt, 24.18, 121.31)
        same = lunar_ephemeris_for_galactic_core(
            datetime.fromisoformat("2026-09-28T20:00:00+08:00"), 24.18, 121.31
        )
        self.assertEqual(utc, same)

    def test_generic_target_requires_ra_and_dec_together(self):
        with self.assertRaises(ValueError):
            lunar_ephemeris(self.dt, 25, 121, target_ra_deg=266.4)

    def test_naive_datetime_fails_closed(self):
        with self.assertRaises(ValueError):
            lunar_ephemeris_for_galactic_core(datetime(2026, 9, 28, 12), 25, 121)


if __name__ == "__main__":
    unittest.main()
