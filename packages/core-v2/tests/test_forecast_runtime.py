"""Offline contract/integration tests. Synthetic weather is NEVER live proof.

The Opportunity bytes come from the real W2 Canonical on main. Weather JSON
below is test-only. Transport mocks test control flow, not actual NOAA access.
"""
from base64 import b64encode
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import URLError

CORE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CORE))
import forecast_runtime as runtime
from adapters import nws_snapshot as snapshot

POINTS = "https://api.weather.gov/points/47.6,-122.33"
GRID = "https://api.weather.gov/gridpoints/SEW/100,100"
VALID = "2026-10-14T01:24:00Z"
RETRIEVED = "2026-10-13T13:00:00Z"
POLICY = {"approved": True, "source": "TEST ONLY operational age policy", "max_age_seconds": 7200}
CANONICAL = runtime.ROOT / "data/v2/opportunities/us-071-P01.json"


def documents():
    points = {"geometry": {"type": "Point", "coordinates": [-122.33, 47.6]},
              "properties": {"gridId": "SEW", "gridX": 100, "gridY": 100,
                             "forecastGridData": GRID, "timeZone": runtime.ZONE}}
    grid = {"properties": {"gridId": "SEW", "gridX": 100, "gridY": 100,
                           "updateTime": "2026-10-13T12:00:00Z",
                           "skyCover": {"uom": "wmoUnit:percent", "values": [
                               {"validTime": "2026-10-14T01:00:00Z/PT3H", "value": 46}]},
                           "windSpeed": {"uom": "wmoUnit:km_h-1", "values": [
                               {"validTime": "2026-10-14T01:00:00Z/PT3H", "value": 7}]}}}
    return [snapshot._document(url, json.dumps(body).encode())
            for url, body in ((POINTS, points), (GRID, grid))]


def change_document(docs, index, fn):
    raw = snapshot.b64decode(docs[index]["body_base64"])
    body = json.loads(raw)
    fn(body)
    docs[index] = snapshot._document(docs[index]["url"], json.dumps(body).encode())


def replay(docs=None, **changes):
    args = dict(valid_at=VALID, retrieved_at=RETRIEVED, as_of=RETRIEVED,
                coordinate_source=runtime.SAMPLE["coordinate_source"], freshness_policy=POLICY,
                expected_time_zone=runtime.ZONE)
    args.update(changes)
    return snapshot.replay_nws_snapshot(documents() if docs is None else docs, **args)


class FixedClock:
    @staticmethod
    def now(zone):
        return datetime(2026, 10, 13, 13, tzinfo=timezone.utc)


class SnapshotTests(unittest.TestCase):
    def assert_unknown(self, result, reason):
        self.assertEqual(result["source_state"], "UNKNOWN")
        self.assertEqual(result["records"], [])
        self.assertIn(reason, result["reasons"])
        self.assertEqual(result["photography_verdict"], "NOT_EVALUABLE")

    def test_replay_has_exact_original_bytes_and_fixture_identity(self):
        docs = documents()
        result = replay(docs)
        self.assertEqual(result["documents"], docs)
        self.assertEqual(result["retrieval_mode"], "TEST_FIXTURE")
        self.assertEqual(len(result["records"]), 2)
        for record in result["records"]:
            self.assertEqual(record["source_sha256"], docs[1]["sha256"])
            self.assertEqual(record["retrieval_mode"], "TEST_FIXTURE")
            self.assertIsNone(record["provider_issued_at_utc"])
            self.assertIsNone(record["provider_run_id"])
            self.assertIsNone(record["grid"]["native_resolution_m"])
            self.assertEqual(record["source_kind"], "FORECAST")
            self.assertEqual(record["calibration_status"], "UNVALIDATED")

    def test_missing_field_preserved_without_erasing_other_fields(self):
        result = replay()
        self.assertIsNone(result["fields"]["probabilityOfPrecipitation"]["record"])
        self.assertIn("MISSING_FIELD", result["reasons"])
        self.assertEqual(result["records"][0]["raw_value"], 46)

    def test_cache_expires_using_as_of_not_historical_retrieval_clock(self):
        self.assertEqual(replay(as_of="2026-10-13T14:00:00Z")["source_state"], "RAW_SOURCE_ONLY")
        self.assert_unknown(replay(as_of="2026-10-13T14:00:01Z"), "STALE_SOURCE")
        self.assertEqual(replay()["expires_at_utc"], "2026-10-13T14:00:00Z")

    def test_future_retrieval_and_naive_time_rejected(self):
        self.assert_unknown(replay(as_of="2026-10-13T12:59:59Z"), "FUTURE_RETRIEVAL")
        self.assert_unknown(replay(valid_at="2026-10-14T01:24:00"), "NAIVE_TIME")

    def test_future_source_refresh_is_not_valid_model_issuance(self):
        docs = documents()
        change_document(docs, 1, lambda d: d["properties"].update(updateTime="2026-10-13T14:00:00Z"))
        self.assert_unknown(replay(docs), "FUTURE_SOURCE_UPDATE")

    def test_half_open_interval_never_rounded_to_hour(self):
        self.assertEqual(replay(valid_at="2026-10-14T03:59:59Z")["source_state"], "RAW_SOURCE_ONLY")
        self.assert_unknown(replay(valid_at="2026-10-14T04:00:00Z"),
                            "MISSING_OR_OVERLAPPING_INTERVAL")

    def test_wrong_forecast_date_and_historical_event_no_data(self):
        self.assert_unknown(replay(valid_at="2026-10-15T01:24:00Z"),
                            "MISSING_OR_OVERLAPPING_INTERVAL")
        self.assert_unknown(replay(valid_at="2026-10-13T12:59:59Z"), "PAST_EVENT_NOT_FORECASTABLE")

    def test_modified_bytes_and_missing_archive_rejected(self):
        docs = documents()
        docs[1]["body_base64"] = b64encode(b"{}").decode()
        self.assert_unknown(replay(docs), "ARCHIVE_HASH_MISMATCH")
        self.assert_unknown(replay([]), "MISSING_ARCHIVE_DOCUMENTS")

    def test_grid_identity_and_points_coordinates_are_independent_checks(self):
        docs = documents()
        change_document(docs, 1, lambda d: d["properties"].update(gridX=101))
        self.assert_unknown(replay(docs), "GRID_BODY_MAPPING_MISMATCH")
        docs = documents()
        change_document(docs, 0, lambda d: d["geometry"].update(coordinates=[121.6, 25]))
        self.assert_unknown(replay(docs), "POINTS_COORDINATE_MISMATCH")

    def test_malformed_geometry_never_crashes_new_runtime(self):
        for geometry in (True, 1, "Point", [1, 2], None):
            docs = documents()
            change_document(docs, 0, lambda d: d.update(geometry=geometry))
            self.assert_unknown(replay(docs), "POINTS_COORDINATE_MISMATCH")

    def test_provider_zone_must_match_pilot_zone(self):
        docs = documents()
        change_document(docs, 0, lambda d: d["properties"].update(timeZone="Asia/Taipei"))
        self.assert_unknown(replay(docs), "PROVIDER_TIME_ZONE_MISMATCH")

    def test_malformed_points_properties_and_nonfinite_json_fail_closed(self):
        docs = documents()
        change_document(docs, 0, lambda d: d.update(properties=[]))
        self.assert_unknown(replay(docs), "INVALID_SOURCE_DOCUMENT")
        docs = documents()
        docs[1] = snapshot._document(GRID, b'{"properties": {"skyCover": NaN}}')
        self.assert_unknown(replay(docs), "NONFINITE_SOURCE_JSON")

    def test_duplicate_json_keys_rejected_even_when_bytes_hash_matches(self):
        docs = documents()
        docs[1] = snapshot._document(GRID, b'{"properties": {}, "properties": {}}')
        self.assert_unknown(replay(docs), "AMBIGUOUS_SOURCE_JSON")

    def test_units_null_and_overlap_never_become_clear_sky(self):
        for value in (None, True, "0", -1, 101):
            docs = documents()
            change_document(docs, 1, lambda d: d["properties"]["skyCover"]["values"][0].update(value=value))
            result = replay(docs)
            self.assertIsNone(result["fields"]["skyCover"]["record"])
            self.assertFalse(result["live_recommendation"])
        docs = documents()
        change_document(docs, 1, lambda d: d["properties"]["skyCover"].update(uom="wmoUnit:degC"))
        self.assertIn("UNSUPPORTED_UNIT", replay(docs)["reasons"])
        docs = documents()
        change_document(docs, 1, lambda d: d["properties"]["skyCover"]["values"].append(
            {"validTime": "2026-10-14T01:00:00Z/PT1H", "value": 0}))
        self.assertIn("MISSING_OR_OVERLAPPING_INTERVAL", replay(docs)["reasons"])

    def test_no_policy_no_network_and_no_clock_injection(self):
        args = dict(latitude=47.6, longitude=-122.33, valid_at=VALID,
                    coordinate_source="Seattle regional sample", freshness_policy={})
        with patch.object(snapshot.nws, "build_opener") as transport:
            self.assert_unknown(snapshot.fetch_nws_snapshot(**args), "FRESHNESS_POLICY_UNAPPROVED")
            transport.assert_not_called()
        with self.assertRaises(TypeError):
            snapshot.fetch_nws_snapshot(**args, retrieved_at=RETRIEVED)

    def test_real_transport_failure_stays_unknown_without_fallback(self):
        with patch.object(snapshot.nws, "build_opener", side_effect=URLError("offline")):
            result = snapshot.fetch_nws_snapshot(latitude=47.6, longitude=-122.33,
                valid_at=VALID, coordinate_source="Seattle regional sample", freshness_policy=POLICY)
        self.assert_unknown(result, "PROVIDER_TRANSPORT_UNAVAILABLE")
        self.assertEqual(result["documents"], [])

    def test_default_transport_two_requests_one_clock_for_all_fields(self):
        # Mocked control-flow test, NOT real source verification.
        docs = documents()
        raw = [snapshot.b64decode(d["body_base64"]) for d in docs]
        with patch.object(snapshot, "datetime", FixedClock), \
             patch.object(snapshot.nws, "_get_json_bytes", side_effect=[({}, r) for r in raw]) as get:
            result = snapshot.fetch_nws_snapshot(latitude=47.6, longitude=-122.33,
                valid_at=VALID, coordinate_source="Seattle regional sample", freshness_policy=POLICY,
                expected_time_zone=runtime.ZONE)
        self.assertEqual(get.call_count, 2)
        self.assertEqual([call.args[0] for call in get.call_args_list], [POINTS, GRID])
        self.assertEqual(result["retrieved_at_utc"], RETRIEVED)
        self.assertTrue(all(r["retrieved_at_utc"] == RETRIEVED for r in result["records"]))


class RuntimeTests(unittest.TestCase):
    def run_pilot(self, raw=None, **kw):
        def fixture_fetch(**args):
            return replay(valid_at=args["valid_at"])
        with patch.object(runtime, "datetime", FixedClock), \
             patch.object(runtime, "fetch_nws_snapshot", side_effect=fixture_fetch):
            return runtime.run_forecast(CANONICAL.read_bytes() if raw is None else raw,
                local_date=kw.pop("local_date", "2026-10-13"), freshness_policy=POLICY, **kw)

    def test_canonical_solar_forecast_condition_trace_end_to_end(self):
        result = self.run_pilot()
        self.assertEqual(hashlib.sha256(CANONICAL.read_bytes()).hexdigest(),
                         "7546ab2c1cad9a1e3c0b5d7a7e8604eda7743cc8f24618510df9ea204ce75e8d")
        self.assertEqual(result["canonical_sha256"], hashlib.sha256(CANONICAL.read_bytes()).hexdigest())
        self.assertEqual(result["solar_window"]["sunset"]["time_local"][:10], "2026-10-13")
        self.assertEqual(result["solar_window"]["sunset"]["time_utc"][:10], "2026-10-14")
        self.assertEqual(result["weather"]["source_state"], "RAW_SOURCE_ONLY")
        self.assertEqual(result["evaluation"]["decision"], "UNKNOWN")
        self.assertEqual(result["photography_verdict"], "NOT_EVALUABLE")
        self.assertFalse(result["recommendation_eligible"])
        self.assertFalse(result["directions_eligible"])
        self.assertEqual(result["source_kinds"]["observation"], "UNAVAILABLE")
        for condition in result["evaluation"]["conditions"]:
            self.assertEqual(condition["state"], "UNKNOWN")
            self.assertTrue(condition["input_refs"])
            self.assertTrue(condition["claim_refs"])
            self.assertIsNone(condition["threshold"])
            self.assertEqual(condition["input_relationship"], "CONTEXT_ONLY_NOT_CONDITION_EVIDENCE")
            self.assertIn("NO_APPROVED_METRIC_PROVIDER_BINDING", condition["input_reasons"])

    def test_even_forged_approval_flags_cannot_turn_raw_cloud_into_photo_pass(self):
        canonical = json.loads(CANONICAL.read_bytes())
        canonical["lifecycle_status"] = "approved"
        canonical["condition_contract"]["status"] = "approved"
        for condition in canonical["condition_contract"]["conditions"]:
            condition["evaluation_mode"] = "AUTO"
            condition["validation_status"] = "validated"
        result = self.run_pilot(json.dumps(canonical).encode())
        self.assertEqual(result["evaluation"]["decision"], "UNKNOWN")
        self.assertTrue(all(c["state"] == "UNKNOWN" for c in result["evaluation"]["conditions"]))

    def test_access_notice_changes_no_weather_or_evaluation(self):
        original = self.run_pilot()
        canonical = json.loads(CANONICAL.read_bytes())
        for locale in ("zh-TW", "en", "ja"):
            canonical["camera_contexts"][0]["access_notes_i18n"][locale] = "TEST closure warning"
        changed = self.run_pilot(json.dumps(canonical).encode())
        self.assertEqual(original["evaluation"], changed["evaluation"])
        self.assertEqual(original["solar_window"], changed["solar_window"])
        self.assertEqual(original["weather"], changed["weather"])
        self.assertNotEqual(original["access_advisories"], changed["access_advisories"])

    def test_taiwan_pilot_rejected_before_network(self):
        other = runtime.ROOT / "data/v2/opportunities/tw-026-P01.json"
        with patch.object(runtime, "fetch_nws_snapshot") as fetch:
            with self.assertRaisesRegex(ValueError, "UNSUPPORTED_PILOT"):
                runtime.run_forecast(other.read_bytes(), local_date="2026-10-13", freshness_policy=POLICY)
            fetch.assert_not_called()

    def test_invalid_date_and_event_rejected_before_network(self):
        with self.assertRaises(ValueError):
            self.run_pilot(local_date="2026-02-30")
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_SOLAR_EVENT"):
            self.run_pilot(event="dusk")

    def test_dst_and_forecast_unavailable_still_no_score(self):
        result = self.run_pilot(local_date="2026-11-01")
        self.assertTrue(result["solar_window"]["sunset"]["time_local"].endswith("-08:00"))
        self.assertEqual(result["weather"]["source_state"], "UNKNOWN")
        self.assertEqual(result["evaluation"]["decision"], "UNKNOWN")
        self.assertNotIn("score", result)

    def test_real_fetch_failure_preserved_through_existing_evaluator(self):
        with patch.object(runtime, "datetime", FixedClock), \
             patch.object(runtime, "fetch_nws_snapshot", return_value=snapshot._unknown("PROVIDER_TRANSPORT_UNAVAILABLE")):
            result = runtime.run_forecast(CANONICAL.read_bytes(), local_date="2026-10-13", freshness_policy=POLICY)
        weather_trace = result["evaluation"]["conditions"][0]
        self.assertIn("PROVIDER_TRANSPORT_UNAVAILABLE", weather_trace["input_reasons"])
        self.assertEqual(weather_trace["input_refs"], [])
        self.assertEqual(weather_trace["state"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
