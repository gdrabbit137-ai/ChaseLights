"""Ten W3 M6b source adapter regressions; deterministic NOAA-shaped fixtures.

No live network required. TEST_FIXTURE records cannot pass as authenticated
provider observations, cannot score photography, and cannot provide Directions.
"""
from copy import deepcopy
from datetime import datetime, timezone
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import unittest

ADAPTER = Path(__file__).resolve().parents[1] / "adapters/nws_gridpoint.py"
spec = spec_from_file_location("m6b_nws_gridpoint", ADAPTER)
nws = module_from_spec(spec)
spec.loader.exec_module(nws)

POINTS_URL = "https://api.weather.gov/points/47.6,-122.33"
GRID_URL = "https://api.weather.gov/gridpoints/SEW/100,100"
AS_OF = "2026-10-13T15:15:00Z"
RETRIEVED = "2026-10-13T13:00:00Z"
POLICY = {"approved": True, "source": "M6b test freshness policy, not production approval",
          "max_age_seconds": 7200}


def fixture():
    points = {
        "geometry": {"type": "Point", "coordinates": [-122.33, 47.6]},
        "properties": {"gridId": "SEW", "gridX": 100, "gridY": 100,
                       "forecastGridData": GRID_URL}
    }
    grid = {
        "properties": {
            "updateTime": "2026-10-13T12:00:00+00:00",
            "skyCover": {"uom": "wmoUnit:percent",
                         "values": [{"validTime": "2026-10-13T14:00:00Z/PT3H",
                                     "value": 46}]},
            "windSpeed": {"uom": "wmoUnit:km_h-1",
                          "values": [{"validTime": "2026-10-13T14:00:00Z/PT3H",
                                      "value": 7}]},
        }
    }
    return points, grid


def normalize(points=None, grid=None, **kw):
    p, g = fixture()
    p = points if points is not None else p
    g = grid if grid is not None else g
    raw = json.dumps(g, sort_keys=True).encode()
    args = dict(points_url=POINTS_URL, grid_url=GRID_URL, field="skyCover",
                valid_at=AS_OF, retrieved_at=RETRIEVED,
                coordinate_source="Seattle named-region research only; no Camera GPS",
                freshness_policy=POLICY)
    args.update(kw)
    return nws.normalize_fixture(p, g, raw, **args)


class FakeResponse:
    def __init__(self, url, content, *, effective_url=None, status=200):
        self.url, self.content, self.effective_url, self.status = (
            url, content, effective_url or url, status)
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def geturl(self):
        return self.effective_url
    def read(self, size):
        return self.content[:size]


class FakeOpener:
    def __init__(self, points, grid, *, redirected=False, oversize=False):
        self.calls = []
        self.documents = {POINTS_URL: json.dumps(points).encode(),
                          GRID_URL: json.dumps(grid).encode()}
        self.redirected, self.oversize = redirected, oversize
    def open(self, req, timeout):
        self.calls.append((req.full_url, timeout, req.get_header("User-agent")))
        assert req.full_url in self.documents, req.full_url
        raw = (b"x" * (nws.MAX_BYTES + 1)
               if self.oversize and req.full_url == GRID_URL
               else self.documents[req.full_url])
        effective = "https://evil.test/a" if self.redirected else req.full_url
        return FakeResponse(req.full_url, raw, effective_url=effective)


class GridpointSourceGate(unittest.TestCase):
    def assert_unknown(self, result, reason):
        self.assertEqual("UNKNOWN", result["source_state"])
        self.assertIsNone(result["record"])
        self.assertEqual("NOT_EVALUABLE", result["photography_verdict"])
        self.assertIn(reason, result["reasons"])
        self.assertFalse(result["live_recommendation"])

    def test_01_raw_original_value_and_sha256_are_not_photo_score(self):
        import hashlib
        result = normalize()
        self.assertEqual("RAW_SOURCE_ONLY", result["source_state"])
        r = result["record"]
        self.assertEqual(46, r["raw_value"])
        self.assertEqual("wmoUnit:percent", r["uom"])
        self.assertEqual("2026-10-13T14:00:00Z", r["valid_from_utc"])
        self.assertEqual("2026-10-13T17:00:00Z", r["valid_until_utc"])
        self.assertEqual("TEST_FIXTURE", r["retrieval_mode"])
        self.assertEqual(hashlib.sha256(json.dumps(fixture()[1], sort_keys=True).encode()).hexdigest(),
                         r["source_sha256"])
        self.assertFalse(r["recommendation_eligible"])
        self.assertEqual("NOT_EVALUABLE", r["photography_verdict"])
        self.assertIsNone(r["provider_issued_at_utc"])
        self.assertIsNone(r["provider_run_id"])
        self.assertIsNone(r["grid"]["native_resolution_m"])
        self.assertEqual("representative_place_sample", r["grid"]["coordinate_role"])
        self.assertEqual({"zh-TW", "en", "ja"}, set(r["limitations_i18n"]))

    def test_02_merged_grid_validtime_and_non_hourly_boundaries(self):
        good = normalize(valid_at="2026-10-13T16:59:59Z")
        self.assertEqual("RAW_SOURCE_ONLY", good["source_state"])
        absent = normalize(valid_at="2026-10-13T17:00:00Z")
        self.assert_unknown(absent, "MISSING_OR_OVERLAPPING_INTERVAL")
        before = normalize(valid_at="2026-10-13T13:59:59Z")
        self.assert_unknown(before, "MISSING_OR_OVERLAPPING_INTERVAL")

    def test_03_stale_future_or_unapproved_source_policy_fail(self):
        self.assert_unknown(normalize(retrieved_at="2026-10-13T20:00:00Z"),
                            "STALE_SOURCE")
        self.assert_unknown(normalize(retrieved_at="2026-10-13T11:00:00Z"),
                            "FUTURE_SOURCE_UPDATE")
        self.assert_unknown(normalize(freshness_policy={"approved": False,
             "max_age_seconds": 7200, "source": "test"}),
             "FRESHNESS_POLICY_UNAPPROVED")
        self.assert_unknown(normalize(freshness_policy={"approved": True,
             "max_age_seconds": 7200, "source": ""}),
             "FRESHNESS_POLICY_UNAPPROVED")

    def test_04_null_non_numeric_nonfinite_and_out_of_range_never_coerce(self):
        for value in (None, "46", True, float("nan"), float("inf"), -1, 101):
            with self.subTest(value=str(value)):
                _, g = fixture()
                g["properties"]["skyCover"]["values"][0]["value"] = value
                expected = ("RAW_VALUE_OUT_OF_RANGE" if value in (-1, 101)
                            else "RAW_VALUE_MISSING_OR_INVALID")
                self.assert_unknown(normalize(grid=g), expected)

    def test_05_units_field_type_and_forecast_data_type_not_guessed(self):
        _, grid = fixture()
        grid["properties"]["skyCover"]["uom"] = "wmoUnit:degC"
        self.assert_unknown(normalize(grid=grid), "UNSUPPORTED_UNIT")
        self.assert_unknown(normalize(field="fogProbability"), "UNSUPPORTED_FIELD")
        good = normalize(field="windSpeed")
        self.assertEqual(7, good["record"]["raw_value"])
        self.assertEqual("wmoUnit:km_h-1", good["record"]["uom"])

    def test_06_missing_or_overlapping_intervals_fail_closed(self):
        _, grid = fixture()
        grid["properties"]["skyCover"]["values"][0]["validTime"] = "not a duration"
        self.assert_unknown(normalize(grid=grid), "INVALID_VALIDTIME_INTERVAL")
        _, grid = fixture()
        grid["properties"]["skyCover"]["values"].append(
            {"validTime": "2026-10-13T15:00:00Z/PT1H", "value": 44})
        self.assert_unknown(normalize(grid=grid), "MISSING_OR_OVERLAPPING_INTERVAL")
        _, grid = fixture()
        grid["properties"]["skyCover"]["values"][0]["validTime"] = (
            "2026-10-13T14:00:00Z/P0D")
        self.assert_unknown(normalize(grid=grid), "UNSUPPORTED_DURATION")

    def test_07_points_mapping_wrong_office_or_coordinates_fail(self):
        p, g = fixture()
        p["properties"]["gridX"] = 101
        self.assert_unknown(normalize(points=p), "GRID_MAPPING_CHANGED")
        p, g = fixture()
        p["geometry"]["coordinates"] = [121.6, 25.0]
        self.assert_unknown(normalize(points=p), "POINTS_COORDINATE_MISMATCH")
        p, g = fixture()
        p["properties"]["forecastGridData"] = "https://evil.test/raw"
        self.assert_unknown(normalize(points=p), "GRID_MAPPING_CHANGED")

    def test_08_unsafe_source_host_and_unverifiable_sampling_rejected(self):
        self.assert_unknown(normalize(grid_url="https://api.weather.gov.evil.com/gridpoints/SEW/100,100"),
                            "INVALID_SOURCE_URL")
        self.assert_unknown(normalize(points_url="http://api.weather.gov/points/47.6,-122.33"),
                            "INVALID_SOURCE_URL")
        self.assert_unknown(normalize(coordinate_source=""), "COORDINATE_SOURCE_UNVERIFIED")
        self.assert_unknown(normalize(points_url="https://api.weather.gov/points/95,-122.33"),
                            "OUT_OF_RANGE_LOCATION")

    def test_09_bounded_no_redirect_http_and_fixture_transport_guard(self):
        p, g = fixture()
        fake = FakeOpener(p, g)
        args = dict(latitude=47.6, longitude=-122.33, field="skyCover",
                    valid_at=AS_OF, coordinate_source="Seattle regional sample",
                    freshness_policy=POLICY, retrieved_at=RETRIEVED, opener=fake)
        res = nws.fetch_nws_gridpoint(**args)
        self.assertEqual("RAW_SOURCE_ONLY", res["source_state"])
        self.assertEqual("TEST_FIXTURE", res["record"]["retrieval_mode"])
        self.assertEqual([POINTS_URL, GRID_URL], [x[0] for x in fake.calls])
        self.assertTrue(all(x[2].startswith("ChaseLights") for x in fake.calls))
        self.assert_unknown(nws.fetch_nws_gridpoint(
            **{**args, "opener": FakeOpener(p, g, redirected=True)}),
            "REDIRECT_OR_BAD_HTTP_RESPONSE")
        self.assert_unknown(nws.fetch_nws_gridpoint(
            **{**args, "opener": FakeOpener(p, g, oversize=True)}),
            "INVALID_GRID_BYTES")

    def test_10_no_access_or_camera_status_may_become_photography_verdict(self):
        res = normalize()
        rec = deepcopy(res["record"])
        self.assertEqual("NOT_EVALUABLE", rec["photography_verdict"])
        self.assertFalse(rec["recommendation_eligible"])
        self.assertEqual("RAW_ONLY", rec["data_state"])
        self.assertEqual("UNVALIDATED", rec["calibration_status"])
        # Its source grid coordinates are representative, never a Camera Zone
        # or an arrival point. No access status, score, Directions or cloud
        # occurrence boolean appears in the schema.
        for key in ("camera_gps", "navigation_target", "access_status",
                    "score", "favorable", "cloud_sea_probability"):
            self.assertNotIn(key, rec)
        self.assertEqual("NO_APPROVED_PHOTO_THRESHOLD", res["reasons"][0])


if __name__ == "__main__":
    unittest.main()
