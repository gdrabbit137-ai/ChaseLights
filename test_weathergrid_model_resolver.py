import unittest
from datetime import datetime, timezone

from weathergrid_model_resolver import (
    candidate_icon_cycles,
    icon_forecast_hour_is_published,
    icon_horizon_hours,
    resolve_cloud_run,
    select_icon_run,
)


UTC = timezone.utc


class WeatherGridModelResolverTests(unittest.TestCase):
    def test_icon_cycle_horizons(self):
        self.assertEqual(icon_horizon_hours(0), 180)
        self.assertEqual(icon_horizon_hours(6), 120)
        self.assertEqual(icon_horizon_hours(12), 180)
        self.assertEqual(icon_horizon_hours(18), 120)

    def test_icon_schedule_is_hourly_then_three_hourly(self):
        self.assertTrue(icon_forecast_hour_is_published(78))
        self.assertFalse(icon_forecast_hour_is_published(79))
        self.assertTrue(icon_forecast_hour_is_published(81))

    def test_candidate_cycles_respect_publication_lag(self):
        now = datetime(2026, 9, 30, 3, 0, tzinfo=UTC)
        cycles = candidate_icon_cycles(now, publication_lag_hours=4, count=3)
        self.assertEqual(
            [x.strftime("%Y-%m-%d %H") for x in cycles],
            ["2026-09-29 18", "2026-09-29 12", "2026-09-29 06"],
        )

    def test_icon_uses_older_long_cycle_when_newer_short_cycle_cannot_cover_target(self):
        now = datetime(2026, 9, 30, 23, 0, tzinfo=UTC)
        target = datetime(2026, 10, 5, 21, 0, tzinfo=UTC)
        run = select_icon_run(target, now=now)
        self.assertIsNotNone(run)
        self.assertEqual(
            run.cycle_time_utc,
            datetime(2026, 9, 30, 12, 0, tzinfo=UTC),
        )
        self.assertEqual(run.forecast_hour, 129)

    def test_resolver_prefers_icon_when_both_models_cover_target(self):
        now = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)
        target = datetime(2026, 10, 1, 0, 0, tzinfo=UTC)
        run = resolve_cloud_run(target, now=now)
        self.assertIsNotNone(run)
        self.assertEqual(run.model, "ICON_GLOBAL")

    def test_resolver_falls_back_to_gfs_when_icon_is_unavailable(self):
        now = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)
        target = datetime(2026, 10, 1, 0, 0, tzinfo=UTC)
        run = resolve_cloud_run(target, now=now, icon_available=False)
        self.assertIsNotNone(run)
        self.assertEqual(run.model, "GFS")

    def test_resolver_uses_gfs_beyond_icon_horizon(self):
        now = datetime(2026, 9, 30, 12, 0, tzinfo=UTC)
        target = datetime(2026, 10, 9, 12, 0, tzinfo=UTC)
        run = resolve_cloud_run(target, now=now)
        self.assertIsNotNone(run)
        self.assertEqual(run.model, "GFS")


if __name__ == "__main__":
    unittest.main()
