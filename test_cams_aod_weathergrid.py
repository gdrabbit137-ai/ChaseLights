import unittest
from datetime import datetime, timezone

from cams_aod_weathergrid import (
    ENCODING_SCALE,
    FIELD_GRID,
    PM25_FIELD_GRID,
    PM25_ENCODING_SCALE,
    REGION_BBOXES,
    US_BBOX,
    build_bundle,
    fetch_responses,
    region_bundle_filename,
    region_qc_filename,
    request_grid,
)
import time as _time


def fake_responses(hours=13, bbox=None):
    lats, lons, points = request_grid(bbox)
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
    def test_fetch_responses_retries_transient_429_then_succeeds(self):
        # CL-CI-07: scheduled runs hit Open-Meteo 429s; the fetcher must
        # retry transient statuses instead of failing the whole refresh.
        payload = fake_responses(hours=3)
        calls = {"n": 0}

        class FakeResponse:
            status_code = 429
            headers = {"Retry-After": "0"}

            def json(self):
                return payload

            def raise_for_status(self):
                if calls["n"] < 2:
                    raise AssertionError("429 must not be raised while retryable")

        class FakeSession:
            def get(self, url, params=None, timeout=None):
                calls["n"] += 1
                count = len(params["latitude"].split(","))
                response = FakeResponse()
                if calls["n"] >= 2:
                    response.status_code = 200
                    response.json = lambda count=count: payload[:count]
                return response

        sleeps = []
        original_sleep = _time.sleep
        _time.sleep = sleeps.append
        try:
            responses = fetch_responses(
                [(10.0, 120.0), (10.4, 120.4)],
                forecast_hours=3,
                batch_size=2,
                session=FakeSession(),  # type: ignore[arg-type]
                batch_delay_s=0.0,
            )
        finally:
            _time.sleep = original_sleep
        self.assertEqual(calls["n"], 2)  # one 429 retry + one success
        self.assertEqual(len(responses), 2)
        self.assertTrue(sleeps)  # backoff actually slept before retrying

    def test_fetch_responses_gives_up_after_retries_and_raises(self):
        class Always429:
            status_code = 429
            headers = {}

            def raise_for_status(self):
                raise RuntimeError("HTTP 429")

        class FakeSession:
            def get(self, url, params=None, timeout=None):
                return Always429()

        original_sleep = _time.sleep
        _time.sleep = lambda *_: None
        try:
            with self.assertRaises(RuntimeError):
                fetch_responses(
                    [(10.0, 120.0)],
                    forecast_hours=3,
                    batch_size=1,
                    retries=2,
                    batch_delay_s=0.0,
                    session=FakeSession(),  # type: ignore[arg-type]
                )
        finally:
            _time.sleep = original_sleep

    def test_fetch_responses_retries_read_timeout_then_succeeds(self):
        # CL-CI-08: CAMS reads can hang past the client timeout; a
        # ReadTimeout is transient and must be retried, not raised.
        import requests as _requests
        payload = fake_responses(hours=3)
        calls = {"n": 0}
        session_probe = {}

        class FakeResponse:
            status_code = 200
            headers = {}

            def __init__(self, count):
                self._count = count

            def json(self):
                return payload[: self._count]

            def raise_for_status(self):
                pass

        class FakeSession:
            def get(self, url, params=None, timeout=None):
                calls["n"] += 1
                session_probe["timeout"] = timeout
                if calls["n"] < 2:
                    raise _requests.ReadTimeout("read timed out")
                count = len(params["latitude"].split(","))
                return FakeResponse(count)

        sleeps = []
        original_sleep = _time.sleep
        _time.sleep = sleeps.append
        try:
            responses = fetch_responses(
                [(10.0, 120.0), (10.4, 120.4)],
                forecast_hours=3,
                batch_size=2,
                session=FakeSession(),  # type: ignore[arg-type]
                batch_delay_s=0.0,
            )
        finally:
            _time.sleep = original_sleep
        self.assertEqual(calls["n"], 2)  # one ReadTimeout retry + one success
        self.assertEqual(len(responses), 2)
        self.assertTrue(sleeps)  # backoff actually slept before retrying
        # Read timeout is widened so a slow CAMS response does not fail.
        self.assertGreater(session_probe["timeout"][1], 60)

    def test_fetch_responses_raises_after_retries_on_read_timeout(self):
        import requests as _requests

        class AlwaysTimeout:
            def get(self, url, params=None, timeout=None):
                raise _requests.ReadTimeout("read timed out")

        original_sleep = _time.sleep
        _time.sleep = lambda *_: None
        try:
            with self.assertRaises(_requests.ReadTimeout):
                fetch_responses(
                    [(10.0, 120.0)],
                    forecast_hours=3,
                    batch_size=1,
                    retries=2,
                    batch_delay_s=0.0,
                    session=AlwaysTimeout(),  # type: ignore[arg-type]
                )
        finally:
            _time.sleep = original_sleep

    def test_request_grid_covers_taiwan_region_on_point_four_degree_lattice(self):
        lats, lons, points = request_grid()
        self.assertEqual(lats[0], 4.8)
        self.assertEqual(lats[-1], 40.0)
        self.assertEqual(lons[0], 104.8)
        self.assertEqual(lons[-1], 145.2)
        self.assertEqual(len(points), len(lats) * len(lons))
        self.assertEqual((len(lats), len(lons)), (89, 102))

    def test_request_grid_covers_us_region_on_point_four_degree_lattice(self):
        # CL-DATA-07: us window (125–70.5°W / 25–49.5°N region bbox) on the
        # same 0.4° request lattice, with the same small outward margin.
        lats, lons, points = request_grid(US_BBOX)
        self.assertEqual(lats[0], 24.8)
        self.assertEqual(lats[-1], 49.6)
        self.assertEqual(lons[0], -125.2)
        self.assertEqual(lons[-1], -70.4)
        self.assertEqual(len(points), len(lats) * len(lons))
        self.assertEqual((len(lats), len(lons)), (63, 138))

    def test_us_window_fully_contains_the_us_region_bbox(self):
        # The GFS/ICON us convention (weather-map-regions.js REGION_BBOXES.us);
        # a source that does not fully contain it must not be offered in the
        # us dropdown (sourcesForRegion coverage rule).
        region = {"leftlon": -125.0, "rightlon": -70.5, "bottomlat": 25.0, "toplat": 49.5}
        self.assertLessEqual(US_BBOX["leftlon"], region["leftlon"])
        self.assertGreaterEqual(US_BBOX["rightlon"], region["rightlon"])
        self.assertLessEqual(US_BBOX["bottomlat"], region["bottomlat"])
        self.assertGreaterEqual(US_BBOX["toplat"], region["toplat"])
        self.assertEqual(REGION_BBOXES["tw"], {
            "leftlon": 104.8, "rightlon": 145.2, "bottomlat": 4.8, "toplat": 40.0,
        })

    def test_us_bundle_carries_us_window_and_legacy_tw_filenames_unchanged(self):
        bundle, qc = build_bundle(
            fake_responses(bbox=US_BBOX),
            region="us",
            retrieved_at=datetime(2026, 10, 1, 8, tzinfo=timezone.utc),
        )
        self.assertEqual(bundle["model"], "CAMS_GLOBAL")
        self.assertEqual(bundle["bbox"], US_BBOX)
        self.assertEqual(qc["grid_rows"], 63)
        self.assertEqual(qc["grid_cols"], 138)
        self.assertEqual(qc["request_point_count"], 63 * 138)
        self.assertEqual(region_bundle_filename("us"), "cams_global_us_aod_browser.json")
        self.assertEqual(region_qc_filename("us"), "cams_global_us_aod_qc.json")
        self.assertEqual(region_bundle_filename("tw"), "cams_global_tw_aod_browser.json")

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
        self.assertEqual(qc["request_point_count"], 89 * 102)

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
