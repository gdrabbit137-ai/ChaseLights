import unittest
from datetime import datetime, timezone

from cams_aod_weathergrid import (
    ENCODING_SCALE,
    FIELD_GRID,
    PM25_FIELD_GRID,
    PM25_ENCODING_SCALE,
    build_bundle,
    request_grid,
)


def fake_responses(hours=13):
    lats, lons, points = request_grid()
    times = [f"2026-10-01T{hour:02d}:00" for hour in range(hours)]
    responses = []
    for index, (lat, lon) in enumerate(points):
        base = 0.05 + (index % len(lons)) * 0.002
        responses.append(
            {
                "latitude": round(lat, 1),
                "longitude": round(lon, 1),
                "hourly_units": {"aerosol_optical_depth": "", "pm2_5": "µg/m³"},
                "hourly": {
                    "time": times,
                    "aerosol_optical_depth": [
                        round(base + hour * 0.001, 3) for hour in range(hours)
                    ],
                    "pm2_5": [
                        round(8.0 + (index % len(lons)) * 0.2 + hour * 0.1, 1)
                        for hour in range(hours)
                    ],
                },
            }
        )
    return responses


class CamsAodWeatherGridTests(unittest.TestCase):
    def test_request_grid_covers_taiwan_region_on_point_four_degree_lattice(self):
        lats, lons, points = request_grid()
        self.assertEqual(lats[0], 20.4)
        self.assertEqual(lats[-1], 26.8)
        self.assertEqual(lons[0], 117.6)
        self.assertEqual(lons[-1], 123.6)
        self.assertEqual(len(points), len(lats) * len(lons))
        self.assertEqual((len(lats), len(lons)), (17, 16))

    def test_bundle_publishes_native_three_hour_timeline(self):
        bundle, qc = build_bundle(
            fake_responses(),
            retrieved_at=datetime(2026, 10, 1, 8, tzinfo=timezone.utc),
        )
        self.assertEqual(bundle["model"], "CAMS_GLOBAL")
        self.assertEqual(
            [frame["valid_time_utc"] for frame in bundle["frames"]],
            [
                "2026-10-01T00:00:00Z",
                "2026-10-01T03:00:00Z",
                "2026-10-01T06:00:00Z",
                "2026-10-01T09:00:00Z",
                "2026-10-01T12:00:00Z",
            ],
        )
        self.assertEqual(
            bundle["provenance"]["native_time_interval_hours"], 3
        )
        self.assertEqual(
            bundle["provenance"]["api_output_interval_hours"], 1
        )
        self.assertEqual(qc["frame_count"], 5)

    def test_bundle_keeps_presentation_grid_distinct_from_native_resolution(self):
        bundle, qc = build_bundle(fake_responses())
        provenance = bundle["provenance"]
        self.assertEqual(provenance["native_resolution_km"], 45.0)
        self.assertEqual(
            provenance["browser_grid_semantics"],
            "request_presentation_lattice",
        )
        self.assertEqual(provenance["provider_cell_selection"], "nearest")
        self.assertEqual(qc["request_point_count"], 272)

    def test_aod_uses_milli_aod_integer_encoding(self):
        bundle, _ = build_bundle(fake_responses())
        meta = bundle["fields"][FIELD_GRID]
        self.assertEqual(meta["scale"], ENCODING_SCALE)
        encoded = bundle["frames"][0]["values"][FIELD_GRID][0]
        self.assertEqual(encoded, 50)
        self.assertAlmostEqual(encoded * meta["scale"], 0.05, places=6)

    def test_pm25_uses_tenth_microgram_encoding_and_distinct_semantics(self):
        bundle, _ = build_bundle(fake_responses())
        meta = bundle["fields"][PM25_FIELD_GRID]
        self.assertEqual(meta["unit"], "µg/m³")
        self.assertEqual(meta["scale"], PM25_ENCODING_SCALE)
        self.assertIn("near-surface", meta["semantics"])
        encoded = bundle["frames"][0]["values"][PM25_FIELD_GRID][0]
        self.assertEqual(encoded, 80)
        self.assertAlmostEqual(encoded * meta["scale"], 8.0, places=6)

    def test_pm25_is_retained_when_aod_is_missing_at_same_cell(self):
        responses = fake_responses()
        responses[0]["hourly"]["aerosol_optical_depth"][0] = None
        bundle, _ = build_bundle(responses)
        self.assertIsNone(bundle["frames"][0]["values"][FIELD_GRID][0])
        self.assertEqual(bundle["frames"][0]["values"][PM25_FIELD_GRID][0], 80)

    def test_pm25_missing_values_are_preserved_and_flagged(self):
        responses = fake_responses()
        responses[0]["hourly"]["pm2_5"][0] = None
        bundle, qc = build_bundle(responses)
        self.assertIsNone(bundle["frames"][0]["values"][PM25_FIELD_GRID][0])
        self.assertIn(
            "partial_missing",
            qc["frames"][0]["fields"][PM25_FIELD_GRID]["flags"],
        )

    def test_trailing_frames_with_all_fields_missing_are_not_published(self):
        responses = fake_responses()
        for item in responses:
            item["hourly"]["aerosol_optical_depth"][12] = None
            item["hourly"]["pm2_5"][12] = None
        bundle, qc = build_bundle(responses)
        self.assertEqual([frame["forecast_hour"] for frame in bundle["frames"]], [0, 3, 6, 9])
        self.assertEqual(qc["frame_count"], 4)
        self.assertEqual(qc["trimmed_trailing_all_missing_frames"], 1)
        self.assertFalse(any(flag["flag"] == "all_missing" for flag in qc["flags"]))

    def test_trailing_frame_is_retained_when_one_production_field_is_available(self):
        responses = fake_responses()
        for item in responses:
            item["hourly"]["aerosol_optical_depth"][12] = None
        bundle, qc = build_bundle(responses)
        self.assertEqual(bundle["frames"][-1]["forecast_hour"], 12)
        self.assertEqual(qc["trimmed_trailing_all_missing_frames"], 0)
        self.assertIn(
            "all_missing",
            qc["frames"][-1]["fields"][FIELD_GRID]["flags"],
        )

    def test_missing_values_are_preserved_and_flagged(self):
        responses = fake_responses()
        responses[0]["hourly"]["aerosol_optical_depth"][0] = None
        bundle, qc = build_bundle(responses)
        self.assertIsNone(bundle["frames"][0]["values"][FIELD_GRID][0])
        self.assertIn(
            "partial_missing",
            qc["frames"][0]["fields"][FIELD_GRID]["flags"],
        )


if __name__ == "__main__":
    unittest.main()
