import unittest
from datetime import datetime, timezone
from pathlib import Path

from icon_global_cloud_poc import (
    build_cdo_command,
    build_icon_url,
    candidate_runs_for_forecast_hour,
    icon_run,
)


UTC = timezone.utc


class IconGlobalCloudPocTests(unittest.TestCase):
    def test_icon_url_matches_dwd_native_global_pattern(self):
        run = icon_run(datetime(2026, 9, 30, 0, tzinfo=UTC), 12)
        url = build_icon_url(run, "clcl", "CLCL")
        self.assertEqual(
            url,
            (
                "https://opendata.dwd.de/weather/nwp/icon/grib/00/clcl/"
                "icon_global_icosahedral_single-level_2026093000_012_CLCL.grib2.bz2"
            ),
        )

    def test_18z_cycle_is_skipped_for_forecast_beyond_120h(self):
        now = datetime(2026, 9, 30, 23, tzinfo=UTC)
        runs = candidate_runs_for_forecast_hour(150, now=now)
        self.assertTrue(runs)
        self.assertEqual(
            runs[0].cycle_time_utc,
            datetime(2026, 9, 30, 12, tzinfo=UTC),
        )

    def test_cdo_command_uses_official_remap_then_regional_subset(self):
        command = build_cdo_command(
            input_grib=Path("input.grib2"),
            output_netcdf=Path("output.nc"),
            target_grid=Path("target_grid_world_0125.txt"),
            weights=Path("weights_icogl2world_0125.nc"),
            bbox={
                "leftlon": 117.5,
                "rightlon": 123.5,
                "bottomlat": 20.5,
                "toplat": 26.75,
            },
        )
        joined = " ".join(str(x) for x in command)
        self.assertIn("-f nc4", joined)
        self.assertIn(
            "-sellonlatbox,117.5,123.5,20.5,26.75",
            joined,
        )
        self.assertIn(
            "-remap,target_grid_world_0125.txt,weights_icogl2world_0125.nc",
            joined,
        )
        self.assertTrue(joined.endswith("input.grib2 output.nc"))


if __name__ == "__main__":
    unittest.main()
