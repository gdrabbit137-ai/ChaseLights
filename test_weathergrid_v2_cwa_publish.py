import json
import tempfile
import unittest
from pathlib import Path

from weathergrid_v2_cache_index import write_index
from weathergrid_v2_cwa_publish import publish_cwa_bundle


def _encoded(values):
    return [int(round(v)) for v in values]


class WeatherGridV2CwaPublishTests(unittest.TestCase):
    def _bundle(self):
        lats = [22.0, 23.0, 24.0, 25.0, 26.0]
        lons = [120.0, 121.0, 122.0, 123.0]
        count = len(lats) * len(lons)
        field_names = [
            "temperature_2m_c",
            "relative_humidity_2m_percent",
            "relative_humidity_1000hpa_percent",
            "relative_humidity_925hpa_percent",
            "relative_humidity_850hpa_percent",
            "relative_humidity_700hpa_percent",
            "relative_humidity_500hpa_percent",
            "relative_humidity_400hpa_percent",
            "relative_humidity_300hpa_percent",
            "rh_cloud_potential_low_percent",
            "rh_cloud_potential_mid_percent",
            "rh_cloud_potential_high_percent",
            "lcl_height_m_agl",
            "fog_potential_percent",
            "wind_speed_10m_m_s",
        ]
        fields = {
            name: {"scale": 1.0, "unit": "%", "encoding": "integer_scaled"}
            for name in field_names
        }
        frames = []
        for fh, valid in ((0, "2026-10-07T00:00:00Z"), (6, "2026-10-07T06:00:00Z")):
            values = {name: _encoded([80.0 + (i % 5) for i in range(count)]) for name in field_names}
            frames.append({"forecast_hour": fh, "valid_time_utc": valid, "values": values})
        return {
            "schema_version": 2,
            "model": "CWA_WRF_3KM",
            "cycle": {"cycle_time_utc": "2026-10-07T00:00:00Z"},
            "provenance": {"native_resolution_km": 3.0, "browser_grid_spacing_degrees": 0.03},
            "grid": {"rows": len(lats), "cols": len(lons), "latitudes": lats, "longitudes": lons},
            "fields": fields,
            "frames": frames,
        }

    def test_publishes_derived_tiles_and_preserves_other_provider_runs(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_index(
                root / "index.json",
                provider_runs={
                    "jma": {
                        "provider": "jma",
                        "model": "JMA_MSM",
                        "published_regions": ["tw"],
                        "published_cell_ids": ["example"],
                        "supported_fields": ["cloud_cover_low"],
                    }
                },
            )
            bundle_path = root / "cwa.json"
            bundle_path.write_text(json.dumps(self._bundle()), encoding="utf-8")
            summary = publish_cwa_bundle(bundle_path, root)
            self.assertEqual(summary["provider"], "cwa")
            self.assertGreater(summary["tiles"], 0)

            index = json.loads((root / "index.json").read_text())
            self.assertIn("jma", index["provider_runs"])
            self.assertIn("cwa", index["provider_runs"])
            run = index["provider_runs"]["cwa"]
            self.assertIn("cwa_cloud_potential_low", run["supported_fields"])
            self.assertIn("cwa_lcl_height", run["supported_fields"])
            self.assertIn("cwa_fog_potential", run["supported_fields"])
            self.assertEqual(run["published_regions"], ["tw"])

            token = run["valid_times"][0]["token"]
            first_cell = run["published_cell_ids"][0]
            tile = json.loads((root / "cwa/current" / token / f"{first_cell}.json").read_text())
            self.assertFalse(tile["native_grid"])
            self.assertTrue(tile["regular_grid"])
            self.assertEqual(tile["provider"], "cwa")
            self.assertIn("cwa_rh_1000", tile["values"])
            self.assertIn("cwa_rh_925", tile["values"])
            self.assertIn("cwa_cloud_potential_high", tile["values"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
