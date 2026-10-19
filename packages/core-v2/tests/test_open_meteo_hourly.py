"""Pinned W1/W2 contract tests of a single raw adapter; no provider I/O."""
from copy import deepcopy
from datetime import timedelta
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "adapters"))
import open_meteo_hourly as om

FIXTURE = Path(__file__).parent / "fixtures/open-meteo/synthetic-hourly.json"
INPUTS = om.load_inputs()
RETRIEVED = "2026-10-19T16:05:00Z"


def example():
    return json.loads(FIXTURE.read_text())


def normalize(source=None, raw=None, **overrides):
    raw = raw if raw is not None else json.dumps(source if source is not None else example()).encode()
    args = dict(inputs=INPUTS, source_url=om.build_request(INPUTS), expected_sha256=hashlib.sha256(raw).hexdigest(),
                requested_at=RETRIEVED, retrieved_at=RETRIEVED,
                normalized_at=RETRIEVED, checked_at=RETRIEVED)
    args.update(overrides)
    return om.normalize_fixture(raw, **args)


class OpenMeteoHourly(unittest.TestCase):
    def reject(self, result, reason):
        self.assertIsNone(result["artifact"])
        self.assertEqual(result["reasons"], [reason])
        self.assertEqual(result["photography_verdict"], "NOT_EVALUABLE")
        self.assertFalse(result["recommendation_eligible"])

    def test_complete_is_raw_and_schema_valid_not_a_photography_result(self):
        r = normalize(); a = r["artifact"]
        self.assertEqual(r["availability"], "COMPLETE")
        self.assertEqual(len(a["hours"]), 72)
        self.assertEqual(set(a["hours"][0]["values"]), set(om.FIELDS))
        self.assertEqual(a["source"]["retrieval_mode"], "TEST_FIXTURE")
        self.assertEqual(a["data_state"], "RAW_ONLY")
        self.assertEqual(a["calibration_status"], "UNVALIDATED")
        self.assertEqual(a["photography_verdict"], "NOT_EVALUABLE")
        self.assertEqual(list(INPUTS.validator.iter_errors(a)), [])
        self.assertEqual(set(a["limitations_i18n"]), {"zh-TW", "en", "ja"})
        self.assertEqual(set(a["attribution"]["modifications_i18n"]), {"zh-TW", "en", "ja"})

    def test_exact_request_without_role_auto_models_or_other_provider(self):
        from urllib.parse import parse_qs, urlsplit
        url = om.build_request(INPUTS); query = parse_qs(urlsplit(url).query)
        self.assertEqual(urlsplit(url).netloc, "api.open-meteo.com")
        self.assertEqual(query["hourly"], [",".join(om.FIELDS)])
        self.assertEqual(query["latitude"], ["24.031426"])
        self.assertEqual(query["longitude"], ["121.62717"])
        self.assertEqual(query["forecast_hours"], ["72"])
        self.assertEqual(query["timezone"], ["GMT"])
        self.assertNotIn("coordinate_role", query)
        self.assertNotIn("models", query)
        for suffix in ["&models=guessed", "&latitude=0", "#fragment"]:
            self.reject(normalize(source_url=url + suffix), "REQUEST_IDENTITY_MISMATCH")
        self.reject(normalize(source_url=url.replace("https:", "http:")), "REQUEST_IDENTITY_MISMATCH")

    def test_pinned_binding_and_schema_bytes_are_not_mutable_substitutes(self):
        for path, expected in [("binding_raw", "PILOT_BINDING_HASH_MISMATCH"), ("schema_raw", "PILOT_SCHEMA_HASH_MISMATCH")]:
            args = {"binding_raw": INPUTS.binding_raw, "schema_raw": INPUTS.schema_raw}
            args[path] += b" "
            with self.assertRaisesRegex(om.PilotFailure, expected): om.PilotInputs(**args)
        with patch.object(om.subprocess, "check_output", side_effect=om.subprocess.CalledProcessError(128, "git")):
            with self.assertRaisesRegex(om.PilotFailure, "PINNED_CONTRACT_UNAVAILABLE"): om.load_inputs()

    def test_changed_original_bytes_or_claimed_hash_rejected(self):
        self.reject(normalize(expected_sha256="0" * 64), "SOURCE_SHA256_MISMATCH")
        raw = FIXTURE.read_bytes()
        self.reject(normalize(raw=raw + b" ", expected_sha256=hashlib.sha256(raw).hexdigest()), "SOURCE_SHA256_MISMATCH")

    def test_invalid_json_duplicate_keys_html_error_array_and_empty_body(self):
        for raw, reason in [(b"", "EMPTY_OR_OVERSIZED_BODY"), (b"<html>error</html>", "INVALID_JSON"),
                            (b'{"latitude":0,"latitude":1}', "DUPLICATE_JSON_KEY"),
                            (b"[]", "INVALID_SOURCE_OBJECT"), (b'{"error":true}', "INVALID_SOURCE_OBJECT"),
                            (b'{"value":NaN}', "NONFINITE_JSON"), (b"\xff", "INVALID_JSON")]:
            with self.subTest(raw=raw): self.reject(normalize(raw=raw), reason)

    def test_oversized_body_rejected_before_decode(self):
        self.reject(normalize(raw=b"x" * (om.MAX_BYTES + 1)), "EMPTY_OR_OVERSIZED_BODY")

    def test_invalid_sample_and_distant_grid_rejected_but_grid_snapping_kept(self):
        a = normalize()["artifact"]
        self.assertNotEqual(a["request"]["latitude"], a["source"]["response_grid_latitude"])
        self.assertEqual(a["source"]["response_grid_latitude"], 24.0)
        for key, value in [("latitude", True), ("latitude", 121.62717), ("longitude", 181), ("latitude", None)]:
            x = example(); x[key] = value
            with self.subTest(key=key,value=value): self.reject(normalize(x), "INVALID_RESPONSE_GRID")
        x = example(); x.update(latitude=0, longitude=0)
        self.reject(normalize(x), "RESPONSE_GRID_OUTSIDE_PILOT_AREA")
        x = example(); x["elevation"] = "unknown"
        self.reject(normalize(x), "INVALID_RESPONSE_ELEVATION")

    def test_provider_zone_never_replaces_verified_place_zone(self):
        for key, value in [("timezone", "auto"), ("timezone", "Asia/Taipei"), ("utc_offset_seconds", 28800), ("utc_offset_seconds", False)]:
            x = example(); x[key] = value
            with self.subTest(key=key,value=value): self.reject(normalize(x), "PROVIDER_TIME_ZONE_MISMATCH")
        with patch.object(om, "taipei_zone", side_effect=om.PilotFailure("TIME_ZONE_UNAVAILABLE")):
            self.reject(normalize(), "TIME_ZONE_UNAVAILABLE")

    def test_missing_and_empty_time_axis_is_empty_not_zero_weather(self):
        for x in [{**example(), "hourly": None}, example(), example()]:
            if isinstance(x["hourly"], dict): x["hourly"].pop("time", None)
            self.reject(normalize(x), "EMPTY_TIME_AXIS")
        x = example(); x["hourly"]["time"] = []
        self.reject(normalize(x), "EMPTY_TIME_AXIS")

    def test_invalid_time_axis_types_lengths_and_units(self):
        for times in ["bad", [0] * 73]:
            x = example(); x["hourly"]["time"] = times
            self.reject(normalize(x), "INVALID_TIME_AXIS_LENGTH")
        for value in [True, "1792425600", None, 1792425600.5]:
            x = example(); x["hourly"]["time"][0] = value
            with self.subTest(value=value): self.reject(normalize(x), "INVALID_HOUR_AXIS")
        x = example(); x["hourly_units"]["time"] = "iso8601"
        self.reject(normalize(x), "INVALID_TIME_UNIT")

    def test_duplicate_descending_gap_and_reordered_axis(self):
        for delta in [0, -3600, 7200]:
            x = example(); x["hourly"]["time"][1] = x["hourly"]["time"][0] + delta
            with self.subTest(delta=delta): self.reject(normalize(x), "NONCONTIGUOUS_HOUR_AXIS")
        x = example(); x["hourly"]["time"][1:3] = reversed(x["hourly"]["time"][1:3])
        self.reject(normalize(x), "NONCONTIGUOUS_HOUR_AXIS")

    def test_old_or_future_response_cannot_be_relabelled_as_this_request(self):
        for delta in [-86400, 3600]:
            x = example(); x["hourly"]["time"] = [t + delta for t in x["hourly"]["time"]]
            with self.subTest(delta=delta): self.reject(normalize(x), "RESPONSE_HORIZON_MISMATCH")
        # A request spanning the hour accepts either actual starting hour.
        self.assertIsNotNone(normalize(requested_at="2026-10-19T15:59:59Z")["artifact"])

    def test_short_actual_horizon_is_partial_and_never_padded(self):
        for size in [1, 71]:
            x = example(); x["hourly"] = {key: values[:size] for key, values in x["hourly"].items()}
            a = normalize(x)["artifact"]
            self.assertEqual(a["availability"], "PARTIAL"); self.assertEqual(len(a["hours"]), size)

    def test_short_array_missing_row_is_unavailable_but_other_fields_remain(self):
        x = example(); x["hourly"]["visibility"] = [0]
        a = normalize(x)["artifact"]
        self.assertEqual(a["availability"], "PARTIAL")
        self.assertEqual(a["hours"][1]["values"]["visibility"]["reason_code"], "MISSING_FIELD")
        self.assertEqual(a["hours"][1]["values"]["wind_speed_10m"]["value"], 0)

    def test_long_array_is_invalid_and_not_silently_truncated(self):
        x = example(); x["hourly"]["cloud_cover_low"].append(0)
        self.reject(normalize(x), "FIELD_LONGER_THAN_TIME_AXIS: cloud_cover_low")

    def test_wrong_field_type_does_not_hide_independent_field(self):
        x = example(); x["hourly"]["visibility"] = {"value": 0}
        a = normalize(x)["artifact"]
        self.assertEqual(a["hours"][0]["values"]["visibility"]["reason_code"], "INVALID_VALUE")
        self.assertEqual(a["hours"][0]["values"]["precipitation"]["value"], 0)

    def test_missing_or_invalid_unit_metadata_is_never_assumed(self):
        for unit in [None, False, 0]:
            x=example(); x["hourly_units"]["wind_speed_10m"]=unit
            a=normalize(x)["artifact"]; cell=a["hours"][0]["values"]["wind_speed_10m"]
            self.assertEqual(cell["reason_code"], "UNIT_MISMATCH")
            self.assertIsNone(cell["source_unit"])
        x=example(); del x["hourly_units"]["visibility"]
        self.assertEqual(normalize(x)["artifact"]["hours"][0]["values"]["visibility"]["reason_code"], "UNIT_MISMATCH")

    def test_all_missing_columns_keep_the_actual_axis_as_partial(self):
        x=example(); x["hourly"]={"time":x["hourly"]["time"]}
        a=normalize(x)["artifact"]
        self.assertEqual(a["availability"], "PARTIAL")
        self.assertEqual(len(a["hours"]), 72)
        self.assertTrue(all(c["reason_code"]=="MISSING_FIELD" for row in a["hours"] for c in row["values"].values()))

    def test_boolean_strings_nan_infinity_negative_and_percent_range(self):
        for field in om.FIELDS:
            for value in [True, "0", float("nan"), float("inf"), 10**1000]:
                cell = om._cell(field, {field: [value]}, {field: om.FIELDS[field]}, 0)
                with self.subTest(field=field,value=value):
                    self.assertIsNone(cell["value"]); self.assertEqual(cell["reason_code"], "INVALID_VALUE")
            if om.FIELDS[field] in ("%", "m/s", "m", "mm"):
                self.assertEqual(om._cell(field, {field: [-1]}, {field: om.FIELDS[field]}, 0)["reason_code"], "INVALID_VALUE")
            if om.FIELDS[field] == "%":
                self.assertEqual(om._cell(field, {field: [101]}, {field: "%"}, 0)["reason_code"], "INVALID_VALUE")
        self.assertEqual(om._cell("temperature_2m", {"temperature_2m": [-130]}, {"temperature_2m": "°C"}, 0)["value"], -130)

    def test_instant_and_preceding_hour_at_taipei_midnight(self):
        a = normalize()["artifact"]; row = a["hours"][0]
        self.assertEqual(row["valid_at_utc"], "2026-10-19T16:00:00Z")
        self.assertEqual(row["preceding_hour"], {"start_utc":"2026-10-19T15:00:00Z", "end_utc":"2026-10-19T16:00:00Z"})
        self.assertEqual(om.ACCUMULATED, {"precipitation", "precipitation_probability"})
        selected = om.select_local_date(a, "2026-10-20", INPUTS)
        self.assertEqual(len(selected), 24); self.assertEqual(selected[0], row)
        self.assertEqual(om.select_local_date(a, "2026-10-19", INPUTS), [])
        zone, version = om.taipei_zone()
        self.assertEqual(om.utc(row["valid_at_utc"]).astimezone(zone).isoformat(), "2026-10-20T00:00:00+08:00")
        self.assertRegex(version, r"^20\d{2}[a-z]$")

    def test_retrieval_age_boundary_and_later_replay_staleness(self):
        for seconds, state in [(21600, "COMPLETE"), (21601, "STALE")]:
            a = normalize(checked_at=om.utc(RETRIEVED)+timedelta(seconds=seconds))["artifact"]
            self.assertEqual(a["availability"], state)
            self.assertEqual(a["source"]["source_freshness"], "UNKNOWN")

    def test_future_or_reversed_or_naive_clock_is_not_accepted(self):
        for overrides in [{"checked_at":"2026-10-19T16:04:59Z"}, {"normalized_at":"2026-10-19T16:04:59Z"},
                          {"requested_at":"2026-10-19T16:05:01Z"}]:
            self.reject(normalize(**overrides), "CLOCK_ORDER_OR_FUTURE_RETRIEVAL")
        self.reject(normalize(retrieved_at="2026-10-19T16:05:00"), "NAIVE_OR_INVALID_CLOCK")

    def test_processing_time_http_metadata_and_fake_model_metadata_never_become_issue(self):
        x = example(); x.update(generationtime_ms=42, model_run="invented", update_time=1792425600)
        a = normalize(x)["artifact"]
        for key in ["source_update_time_utc", "provider_issued_at_utc", "provider_run_id", "resolved_model_ids", "native_resolution_m", "native_time_resolution_seconds"]:
            self.assertIsNone(a["source"][key])
        self.assertEqual(a["source"]["output_step_seconds"], 3600)

    def test_open_closed_advisory_is_not_a_weather_input(self):
        x = example(); y = deepcopy(x)
        x["access_advisory"] = "OPEN"; y["access_advisory"] = "CLOSED"
        a, b = normalize(x)["artifact"], normalize(y)["artifact"]
        self.assertEqual(a["hours"], b["hours"])
        self.assertEqual(a["availability"], b["availability"])
        self.assertEqual(a["photography_verdict"], b["photography_verdict"])

    def test_artifact_validation_rejects_binding_zone_score_directions_and_forged_approval(self):
        a = normalize()["artifact"]
        for key, value in [("pilot_binding_sha256", "0"*64), ("place_id", "us-071"), ("time_zone", "UTC"),
                           ("score", 100), ("directions", "forbidden"), ("recommendation_eligible", True),
                           ("photography_verdict", "FAVORABLE")]:
            x = deepcopy(a); x[key] = value
            with self.subTest(key=key), self.assertRaises(om.PilotFailure): om.validate_artifact(x, INPUTS)
        x = deepcopy(a); x["source"]["source_update_time_utc"] = RETRIEVED
        with self.assertRaises(om.PilotFailure): om.validate_artifact(x, INPUTS)

    def test_semantic_axis_preceding_hour_and_stale_consistency_are_checked(self):
        a = normalize()["artifact"]
        for kind in ["axis", "previous", "stale"]:
            x = deepcopy(a)
            if kind == "axis": x["hours"][1]["valid_at_utc"] = x["hours"][0]["valid_at_utc"]
            elif kind == "previous": x["hours"][0]["preceding_hour"]["start_utc"] = x["hours"][0]["valid_at_utc"]
            else: x["availability"] = "STALE"
            with self.subTest(kind=kind), self.assertRaises(om.PilotFailure): om.validate_artifact(x, INPUTS)

    def test_nonfinite_artifact_metadata_and_tzdb_drift_fail_closed(self):
        a=normalize()["artifact"]
        x=deepcopy(a); x["source"]["response_elevation_m"]=float("nan")
        with self.assertRaisesRegex(om.PilotFailure,"NONFINITE_ARTIFACT"): om.validate_artifact(x, INPUTS)
        x=deepcopy(a); x["tzdb_version"]="2000a"
        with self.assertRaisesRegex(om.PilotFailure,"TZDB_VERSION_MISMATCH"): om.select_local_date(x,"2026-10-20",INPUTS)


def field_case(field, case):
    def run(self):
        x = example()
        if case == "missing": del x["hourly"][field]
        elif case == "null": x["hourly"][field][0] = None
        elif case == "wrong_unit": x["hourly_units"][field] = "incorrect"
        a = normalize(x)["artifact"]; cell = a["hours"][0]["values"][field]
        expected = {"missing":"MISSING_FIELD", "null":"NULL_VALUE", "wrong_unit":"UNIT_MISMATCH", "zero":None}[case]
        self.assertEqual(cell["reason_code"], expected)
        self.assertEqual(cell["value"], 0 if case == "zero" else None)
        self.assertEqual(cell["state"], "AVAILABLE" if case == "zero" else "UNAVAILABLE")
        self.assertEqual(a["availability"], "COMPLETE" if case == "zero" else "PARTIAL")
    return run


for _field in om.FIELDS:
    for _case in ["missing", "null", "zero", "wrong_unit"]:
        setattr(OpenMeteoHourly, "test_field_" + _field + "_" + _case, field_case(_field, _case))


if __name__ == "__main__": unittest.main()
