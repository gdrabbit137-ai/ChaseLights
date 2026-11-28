"""CL-PHYS-03: fog/visibility gate, data floor, season + venue policy gates.

Four defects from the 2026-11-26T11:02:09Z live bundle, all fixed in the
EVALUATION layer (no contract edits, schema_version 10, contract_sha256 still
over the owner contract):

1. white-wall hours recommended (tw-112-P01 11-28 14:00: visibility 0.1 km,
   low cloud 100 %; us-162-P01 11-28 10:00: 1.1 km).
2. in_cloud_fog over-block (us-158-P01 12-02 10:00: low cloud 17 %,
   visibility 13.62 km, still 不宜).
3. no data floor (內洞瀑布 with no weather at all, 宇老觀景台 visibility 0.2 km).
4. season/venue hours (合掌村點燈 11/27 outside 01-15..02-28; 名古屋城 02:00-05:00
   against 09:00-16:30).

Every gate is a pure predicate; the boundary cases either side of each
threshold are asserted here.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "evaluate_batch", ROOT / "packages/core-v2/tools/evaluate_batch.py")
eb = importlib.util.module_from_spec(spec)
sys.modules["evaluate_batch"] = eb
spec.loader.exec_module(eb)


def available(value):
    return {"value": value, "state": "AVAILABLE"}


def hour(visibility=None, low=None, **extra):
    values = dict(extra)
    if visibility is not None:
        values["visibility"] = available(visibility)
    if low is not None:
        values["cloud_cover_low"] = available(low)
    return values


class FogVisibilityBoundaryTests(unittest.TestCase):
    """Eight bands: 2 km white-out edge and 10 km deck edge."""

    def test_whiteout_just_below_two_km(self):
        self.assertEqual(eb.fog_visibility_state(hour(1.99))["value"], "whiteout")

    def test_exactly_two_km_is_not_a_whiteout(self):
        self.assertEqual(eb.fog_visibility_state(hour(2.0))["value"], "hazy")

    def test_deck_white_wall_below_ten_km(self):
        cell = eb.fog_visibility_state(hour(9.99, low=90))
        self.assertEqual(cell["value"], "fogged")
        self.assertEqual(cell["cloud_cover_low_pct"], 90.0)

    def test_low_cloud_just_under_the_deck_threshold_is_clear(self):
        # 9.99 km with a 89.9 % low deck is not a white wall (the deck band
        # needs >= 90 %), and it is above the 5 km haze band: clear.
        self.assertEqual(eb.fog_visibility_state(hour(9.99, low=89.9))["value"],
                         "clear")

    def test_ten_km_releases_the_deck_gate(self):
        self.assertEqual(eb.fog_visibility_state(hour(10.0, low=100))["value"],
                         "clear")

    def test_haze_band_ends_at_five_km(self):
        self.assertEqual(eb.fog_visibility_state(hour(4.99))["value"], "hazy")
        self.assertEqual(eb.fog_visibility_state(hour(5.0))["value"], "clear")

    def test_missing_visibility_abstains(self):
        cell = eb.fog_visibility_state(hour(low=100))
        self.assertEqual((cell["state"], cell["reason_code"]),
                         ("UNKNOWN", "VISIBILITY_UNAVAILABLE"))

    def test_negative_visibility_is_not_trusted(self):
        self.assertEqual(eb.fog_visibility_state(hour(-1.0))["state"], "UNKNOWN")

    def test_gate_vetoes_whiteout_and_deck_but_not_haze(self):
        gate = dict(eb.FOG_VISIBILITY_GATE)
        self.assertEqual(eb.phys_gate_verdict(gate, hour(0.1))[0], "FAIL")
        self.assertEqual(eb.phys_gate_verdict(gate, hour(9.0, low=95))[0], "FAIL")
        self.assertEqual(eb.phys_gate_verdict(gate, hour(4.0))[0], "PASS")
        self.assertEqual(eb.phys_gate_verdict(gate, hour(4.0))[1][:30],
                         "FOG_VISIBILITY(hazy, vis=4.0km")

    def test_gate_abstains_when_it_cannot_see(self):
        self.assertEqual(eb.phys_gate_verdict(dict(eb.FOG_VISIBILITY_GATE),
                                              hour(low=100)),
                         ("PASS", "FOG_VISIBILITY_UNVERIFIED"))

    def test_haze_is_capped_but_not_vetoed(self):
        self.assertTrue(eb.visibility_cap_applies(hour(4.0)))
        self.assertFalse(eb.visibility_cap_applies(hour(6.0)))
        self.assertFalse(eb.visibility_cap_applies(hour(0.5)))  # vetoed, not capped


class RegisteredFogHourTests(unittest.TestCase):
    """The two ticket hours (tw-112-P01 / us-162-P01) can never be recommended."""

    def contract(self):
        # geological_landform shape: NO cloud_cover_low / visibility condition.
        return {"genre_template": "geological_landform",
                "conditions": [{"id": "C-1", "metric": "landform_present",
                                "role": "REQUIRED", "condition_tier": "MAIN",
                                "operator": "none", "threshold": None}]}

    def status(self, values):
        conditions = self.contract()["conditions"] + eb.phys_gates_for(
            self.contract(), 209.0)
        roles = {c["id"]: c["role"] for c in conditions}
        states = {c["id"]: eb.condition_verdict(c, values, {})[0]
                  for c in conditions}
        return eb.hour_status(roles, states)[0]

    def test_tw_112_p01_white_wall_hour_is_unfavorable(self):
        # 2026-11-28 14:00Z+8: visibility 0.1 km, low cloud 100 %, base 269 m
        # ASL against a 209 m viewpoint.
        values = hour(0.1, 100, temperature_2m=available(11.0),
                      relative_humidity_2m=available(100),
                      cloud_cover_total=available(100),
                      wind_speed_10m=available(2.0),
                      precipitation=available(0.2),
                      lcl_height_m_agl=available(60),
                      grid_elevation_m=available(209))
        self.assertEqual(self.status(values), "UNFAVORABLE")

    def test_us_162_p01_shallow_fog_hour_is_unfavorable(self):
        values = hour(1.1, 100, temperature_2m=available(9.0),
                      relative_humidity_2m=available(100),
                      cloud_cover_total=available(100),
                      wind_speed_10m=available(2.0),
                      precipitation=available(0.0))
        self.assertEqual(self.status(values), "UNFAVORABLE")

    def test_a_clear_hour_is_still_satisfied(self):
        values = hour(20.0, 10, temperature_2m=available(20.0),
                      relative_humidity_2m=available(60),
                      cloud_cover_total=available(20),
                      wind_speed_10m=available(2.0),
                      precipitation=available(0.0))
        self.assertEqual(self.status(values), "GUIDANCE_SATISFIED")

    def test_haze_hour_stays_satisfied_but_capped(self):
        values = hour(4.0, 20, temperature_2m=available(20.0),
                      relative_humidity_2m=available(95),
                      cloud_cover_total=available(80),
                      wind_speed_10m=available(2.0),
                      precipitation=available(0.0))
        self.assertEqual(self.status(values), "GUIDANCE_SATISFIED")
        self.assertTrue(eb.visibility_cap_applies(values))

    def test_fog_genre_is_exempt_from_the_visibility_veto(self):
        metrics = [g["metric"] for g in
                   eb.phys_gates_for({"genre_template": "misty_forest"}, 100.0)]
        self.assertNotIn(eb.FOG_VISIBILITY_METRIC, metrics)
        # ... and the floor is still injected, armed with the fog exemption.
        floor = next(g for g in eb.phys_gates_for(
            {"genre_template": "misty_forest"}, 100.0)
            if g["metric"] == eb.DATA_FLOOR_METRIC)
        self.assertTrue(floor.get("fog_subject"))


class InCloudClearSkyTests(unittest.TestCase):
    """Defect 2: the 53-hour over-block (us-158-P01 12-02 10:00)."""

    def values(self, visibility=13.62, low=17, rh850=96, lcl=30):
        v = {"lcl_height_m_agl": available(lcl),
             "grid_elevation_m": available(1500),
             "cloud_cover_low": available(low),
             "relative_humidity_850hpa": available(rh850)}
        if visibility is not None:
            v["visibility"] = available(visibility)
        return v

    def test_us_158_p01_clear_hour_is_not_in_cloud(self):
        cell = eb.in_cloud_fog_state(self.values(), 1580.0)
        self.assertEqual(cell["value"], "clear")
        self.assertEqual(cell["reason_code"], "VISIBILITY_DISPROVES_IN_CLOUD")

    def test_gate_no_longer_fires_on_the_clear_hour(self):
        self.assertEqual(
            eb.phys_gate_verdict(dict(eb.IN_CLOUD_FOG_GATE,
                                      viewpoint_elevation_m=1580.0),
                                 self.values())[0], "PASS")

    def test_true_white_out_still_vetoed(self):
        # Same geometry, visibility 0.3 km: the fog signature stands.
        cell = eb.in_cloud_fog_state(self.values(visibility=0.3, low=100),
                                     1580.0)
        self.assertEqual(cell["value"], "in_cloud")

    def test_just_below_ten_km_keeps_the_geometry_verdict(self):
        cell = eb.in_cloud_fog_state(self.values(visibility=9.99), 1580.0)
        self.assertEqual(cell["value"], "in_cloud")

    def test_missing_visibility_cannot_disprove_in_cloud(self):
        cell = eb.in_cloud_fog_state(self.values(visibility=None), 1580.0)
        self.assertEqual(cell["value"], "in_cloud")


class DataFloorTests(unittest.TestCase):
    """Defect 3: 內洞瀑布 (no weather at all) and 宇老觀景台 (0.2 km)."""

    def test_no_weather_fields_at_all_fails(self):
        cell = eb.data_floor_state({"grid_elevation_m": available(230)})
        self.assertEqual((cell["value"], cell["reason_code"]),
                         ("no_data", "NO_CORE_WEATHER_FIELDS"))

    def test_two_core_fields_are_thin(self):
        cell = eb.data_floor_state(hour(0.2, 100))
        self.assertEqual(cell["value"], "thin")

    def test_three_core_fields_without_visibility_is_not_recommendable(self):
        values = hour(None, 10, temperature_2m=available(20.0),
                      relative_humidity_2m=available(80))
        self.assertEqual(eb.data_floor_state(values)["value"],
                         "visibility_missing")

    def test_visibility_floor_boundary(self):
        base = dict(temperature_2m=available(20.0),
                    relative_humidity_2m=available(80),
                    cloud_cover_total=available(20))
        self.assertEqual(eb.data_floor_state(
            hour(1.99, None, **base))["value"], "visibility_low")
        self.assertEqual(eb.data_floor_state(
            hour(2.0, None, **base))["value"], "ok")

    def test_floor_is_a_fail_not_an_abstain(self):
        gate = dict(eb.DATA_FLOOR_GATE)
        self.assertEqual(eb.phys_gate_verdict(gate, {})[0], "FAIL")
        self.assertIn("NO_CORE_WEATHER_FIELDS",
                      eb.phys_gate_verdict(gate, {})[1])

    def test_ok_hour_passes(self):
        values = hour(20.0, 10, temperature_2m=available(20.0),
                      relative_humidity_2m=available(60),
                      cloud_cover_total=available(20))
        self.assertEqual(eb.phys_gate_verdict(dict(eb.DATA_FLOOR_GATE), values),
                         ("PASS", "DATA_FLOOR(ok)"))

    # -- reviewer COND 1: the fog exemption and the floor must not contradict --


    def misty_hour(self, visibility=0.5):
        """A misty_forest hour: fog is the picture, every field is present."""
        return hour(visibility, 40, temperature_2m=available(14.0),
                    relative_humidity_2m=available(99),
                    cloud_cover_total=available(70),
                    wind_speed_10m=available(1.5),
                    precipitation=available(0.0))

    def test_half_km_misty_forest_hour_is_not_failed_by_the_floor(self):
        values = self.misty_hour()
        # The floor's verdict alone, as it is armed for a fog subject: PASS,
        # with the exemption named in the detail.
        verdict, detail = eb.phys_gate_verdict(
            dict(eb.DATA_FLOOR_GATE, fog_subject=True), values)
        self.assertEqual(verdict, "PASS", detail)
        self.assertIn("fog_visibility_exempt", detail)
        # ... and through the gate the evaluation layer actually injects.
        floor_gate = next(g for g in eb.phys_gates_for(
            {"genre_template": "misty_forest"}, 100.0)
            if g["metric"] == eb.DATA_FLOOR_METRIC)
        self.assertTrue(floor_gate.get("fog_subject"))
        self.assertEqual(eb.phys_gate_verdict(floor_gate, values)[0], "PASS")

    def test_misty_forest_hour_survives_every_injected_gate(self):
        # No gate in the fog subject's own set vetoes the 0.5 km hour: the
        # visibility gate is absent, and the floor exempts visibility.
        gates = eb.phys_gates_for({"genre_template": "misty_forest"}, 100.0)
        self.assertNotIn(eb.FOG_VISIBILITY_METRIC,
                         [g["metric"] for g in gates])
        for gate in gates:
            self.assertEqual(
                eb.phys_gate_verdict(gate, self.misty_hour())[0], "PASS", gate["id"])

    def test_misty_forest_is_still_held_to_the_field_count_floor(self):
        # The exemption is about VISIBILITY only: a fog subject with too few
        # usable inputs is still refused (fog genre is not a data licence).
        thin = hour(0.5, None, temperature_2m=available(14.0))
        self.assertEqual(eb.data_floor_state(thin, fog_subject=True)["value"],
                         "thin")
        empty = {"grid_elevation_m": available(230)}
        self.assertEqual(eb.data_floor_state(empty, fog_subject=True)["value"],
                         "no_data")
        floor_gate = next(g for g in eb.phys_gates_for(
            {"genre_template": "misty_forest"}, 100.0)
            if g["metric"] == eb.DATA_FLOOR_METRIC)
        self.assertEqual(eb.phys_gate_verdict(floor_gate, empty)[0], "FAIL")

    def test_non_fog_subjects_keep_the_visibility_floor(self):
        # Same 0.5 km hour, a general landscape subject: still refused.
        self.assertEqual(eb.data_floor_state(self.misty_hour())["value"],
                         "visibility_low")
        floor_gate = next(g for g in eb.phys_gates_for(
            {"genre_template": "geological_landform"}, 100.0)
            if g["metric"] == eb.DATA_FLOOR_METRIC)
        self.assertFalse(floor_gate.get("fog_subject"))
        self.assertEqual(eb.phys_gate_verdict(floor_gate, self.misty_hour())[0],
                         "FAIL")


class SeasonPolicyTests(unittest.TestCase):
    """Defect 4: 合掌村點燈 recommended on 11/27 outside 01-15..02-28."""

    WINDOW = {"start": "01-15", "end": "02-28"}

    def test_inside_window_boundaries(self):
        for day in (date(2027, 1, 15), date(2027, 1, 31), date(2027, 2, 28)):
            self.assertEqual(eb.season_policy_verdict(self.WINDOW, day)[0], "PASS")

    def test_outside_window_boundaries(self):
        for day in (date(2026, 11, 27), date(2027, 1, 14), date(2027, 3, 1)):
            self.assertEqual(eb.season_policy_verdict(self.WINDOW, day)[0], "FAIL")

    def test_wrap_window_across_new_year(self):
        window = {"start": "12-15", "end": "01-05"}
        self.assertEqual(eb.season_policy_verdict(window, date(2026, 12, 20))[0],
                         "PASS")
        self.assertEqual(eb.season_policy_verdict(window, date(2027, 1, 5))[0],
                         "PASS")
        self.assertEqual(eb.season_policy_verdict(window, date(2027, 1, 6))[0],
                         "FAIL")

    def test_malformed_or_missing_abstains(self):
        self.assertEqual(eb.season_policy_verdict({"start": "x"}, date(2027, 1, 1))[0],
                         "UNKNOWN")
        self.assertEqual(eb.season_policy_verdict(self.WINDOW, None)[0], "UNKNOWN")

    def test_gate_injection_is_abstaining_by_default(self):
        self.assertEqual(eb.policy_gates_for("no-such-opportunity", {}, {}), [])
        gates = eb.policy_gates_for("jp-072-P01", {"jp-072-P01": self.WINDOW}, {})
        self.assertEqual([g["metric"] for g in gates], [eb.SEASON_POLICY_METRIC])

    def test_shipped_policy_table_opens_the_gate_for_jp_072(self):
        windows = eb.load_subject_season_windows()
        self.assertIn("jp-072-P01", windows)
        gate = eb.policy_gates_for("jp-072-P01", windows, {})[0]
        self.assertEqual(
            eb.phys_gate_verdict(gate, {}, local_date=date(2026, 11, 27))[0], "FAIL")
        self.assertEqual(
            eb.phys_gate_verdict(gate, {}, local_date=date(2027, 2, 1))[0], "PASS")


class VenueHoursTests(unittest.TestCase):
    """Defect 4: 名古屋城 recommended 02:00-05:00 against 09:00-16:30."""

    HOURS = {"open": "09:00", "close": "16:30"}

    def test_opening_boundary_is_inclusive(self):
        self.assertEqual(eb.venue_hours_verdict(self.HOURS, 9 * 60)[0], "PASS")
        self.assertEqual(eb.venue_hours_verdict(self.HOURS, 8 * 60 + 59)[0], "FAIL")

    def test_closing_boundary_is_exclusive(self):
        self.assertEqual(eb.venue_hours_verdict(self.HOURS, 16 * 60 + 29)[0], "PASS")
        self.assertEqual(eb.venue_hours_verdict(self.HOURS, 16 * 60 + 30)[0], "FAIL")

    def test_night_hours_are_closed(self):
        for minute in (2 * 60, 3 * 60, 4 * 60, 5 * 60):
            self.assertEqual(eb.venue_hours_verdict(self.HOURS, minute)[0], "FAIL")

    def test_overnight_and_malformed_windows_abstain(self):
        self.assertEqual(eb.venue_hours_verdict({"open": "16:00", "close": "09:00"},
                                                600)[0], "UNKNOWN")
        self.assertEqual(eb.venue_hours_verdict({"open": "9am"}, 600)[0], "UNKNOWN")
        self.assertEqual(eb.venue_hours_verdict(self.HOURS, None)[0], "UNKNOWN")

    def test_unknown_venue_is_never_invented(self):
        self.assertEqual(
            eb.policy_gates_for("jp-072-P01", {}, {"jp-018-P01": self.HOURS}), [])

    def test_shipped_table_covers_nagoya_castle_only(self):
        venues = eb.load_venue_hours()
        # CL-PHYS-04 added the owner-asserted 內洞 (tw-151) window for all
        # THREE opportunities at the place (P01 waterfall, P02 firefly,
        # P03 misty_forest) — one park window, three rows.
        self.assertEqual(sorted(venues), ["jp-018-P01", "tw-151-P01",
                                          "tw-151-P02", "tw-151-P03"])
        self.assertEqual({v["place_id"] for v in venues.values()},
                         {"jp-018", "tw-151"})
        gate = eb.policy_gates_for("jp-018-P01", {}, venues)[0]
        self.assertEqual(
            eb.phys_gate_verdict(gate, {}, local_start_min=3 * 60)[0], "FAIL")
        self.assertEqual(
            eb.phys_gate_verdict(gate, {}, local_start_min=10 * 60)[0], "PASS")


class NightWindowTests(unittest.TestCase):
    """Defect 5 (data half): deep night 00-04, blue hour, city night 22-23."""

    def test_deep_night_window(self):
        for h in (0, 1, 2, 3):
            self.assertEqual(eb.night_window_code("night_sky", h, {}),
                             "NIGHT_DEEP_WINDOW")
        self.assertIsNone(eb.night_window_code("night_sky", 4, {}))

    def test_city_night_window(self):
        for h in (22, 23):
            self.assertEqual(eb.night_window_code("city_night", h, {}),
                             "NIGHT_CITY_WINDOW")

    def test_evening_window(self):
        for h in (18, 19, 20, 21):
            self.assertEqual(eb.night_window_code("moonlit_scene", h, {}),
                             "NIGHT_EVENING_WINDOW")

    def test_blue_hour_wins_when_the_astro_window_passes(self):
        self.assertEqual(
            eb.night_window_code("blue_hour_city", 18, {"blue_hour_window": True}),
            "NIGHT_BLUE_HOUR_WINDOW")

    def test_daytime_and_non_night_genres_have_no_night_window(self):
        self.assertIsNone(eb.night_window_code("night_sky", 12, {}))
        self.assertIsNone(eb.night_window_code("sunset", 23, {}))

    def test_every_code_has_a_trilingual_reason(self):
        for h in (2, 18, 22):
            ellipse = eb.night_window_code("night_sky", h, {})
            reason = eb.night_window_reason(ellipse)
            self.assertEqual(set(reason), {"zh-TW", "en", "ja"})

    def test_moonlit_scene_gate_supplies_the_window_condition(self):
        contract = {"genre_template": "moonlit_scene", "conditions": []}
        metrics = [c["metric"] for c in eb.eval_conditions_for(contract)]
        self.assertIn("astronomical_darkness", metrics)

    def test_city_night_gate_id_is_unchanged(self):
        contract = {"genre_template": "city_night", "conditions": []}
        ids = [c["id"] for c in eb.eval_conditions_for(contract)]
        self.assertIn(eb.GATE_CONDITION_ID, ids)


class RealPathCapTests(unittest.TestCase):
    """Reviewer COND 2: drive evaluate_batch.main() for the haze cap.

    Everything else in this file calls the predicates directly, which proves the
    rule but not that the evaluation path USES it: the cap is computed in
    main()'s per-hour loop, carried in a per-day `capped` set, consumed by
    good_hours and by the next_good scan, and (details side) exposed as a
    capped_hours list next to the hour rows. The stub provider is the same
    pattern test_cl_phys_02_datum_in_cloud.py uses for the datum case.

    Fixture: place tw-001, 168 h from 2026-11-26T00:00Z, visibility 3.0 km
    (haze, shootable) for the first 48 h and 20 km after. tw-001-P03 is a
    blue_hour_city contract whose weather conditions all pass on this fixture,
    so its blue-hour bucket is GUIDANCE_SATISFIED every day — capped on the
    first two days, uncapped afterwards.
    """

    HOURS = 168
    CAPPED_HOURS = 48          # first 48 UTC hours are 3 km visibility
    OID = "tw-001-P03"         # blue_hour_city
    NIGHT_OID = "tw-001-P04"   # city_night (night_window data)

    START = datetime(2026, 11, 26, 0, 0, tzinfo=timezone.utc)

    def artifact(self):
        hours = []
        for index in range(self.HOURS):
            visibility = 3.0 if index < self.CAPPED_HOURS else 20.0
            values = {
                "temperature_2m": available(20.0),
                "dew_point_2m": available(12.0),
                "relative_humidity_2m": available(60),
                "cloud_cover_low": available(10),
                "cloud_cover_mid": available(30),
                "cloud_cover_high": available(30),
                "cloud_cover_total": available(20),
                "wind_speed_10m": available(3.0),
                "visibility": available(visibility),
                "precipitation": available(0.0),
                "precipitation_probability": available(0),
                "relative_humidity_925hpa": available(60),
                "relative_humidity_850hpa": available(60),
                "wind_speed_850hpa": available(3.0),
                "aod_550nm": available(0.2),
                "temperature_delta_850_925_c": available(0.5),
                "cloud_cover_mid_and_high": available(30),
                "lcl_height_m_agl": available(800),
            }
            hours.append({
                "valid_at_utc": (self.START + timedelta(hours=index))
                .strftime("%Y-%m-%dT%H:%M:%SZ"),
                "values": values})
        return {
            "adapter_version": "open-meteo-batch-0.1", "provider": "open-meteo",
            "place_coordinate": {"latitude": 25.0330, "longitude": 121.5654},
            "grid": {"latitude": 25.03, "longitude": 121.56, "elevation_m": 20.0},
            "retrieved_at_utc": "2026-11-26T00:00:00Z",
            "sources": [
                {"source_url": "stub://forecast", "source_sha256": "0" * 64,
                 "kind": "forecast", "fields": []},
                {"source_url": "stub://air-quality", "source_sha256": "0" * 64,
                 "kind": "air_quality", "fields": []}],
            "freshness_policy": {}, "notes": {},
            "hours": hours,
        }

    def run_main(self):
        scratch = Path(tempfile.mkdtemp(prefix="cl-phys03-"))
        captured = {}

        def fake_fetch(lat, lon, forecast_hours):
            self.assertEqual(forecast_hours, self.HOURS)
            captured["artifact"] = self.artifact()
            return captured["artifact"]

        out = scratch / "bundle.json"
        details_dir = scratch / "details"
        argv = ["evaluate_batch.py", "--forecast-hours", str(self.HOURS),
                "--only-place-id", "tw-001", "--out", str(out),
                "--archive", str(scratch / "archive"),
                "--details-dir", str(details_dir)]
        with mock.patch.object(eb.adapter, "fetch_place", fake_fetch), \
                mock.patch.object(sys, "argv", argv):
            eb.main()
        bundle = json.loads(out.read_text(encoding="utf-8"))
        details = json.loads(
            (details_dir / "tw-001.json").read_text(encoding="utf-8"))
        return bundle, details

    @staticmethod
    def opportunity(bundle, oid):
        return next(o for place in bundle["places"]
                    for o in place["opportunities"] if o["opportunity_id"] == oid)

    @staticmethod
    def detail_opportunity(details, oid):
        return next(o for o in details["opportunities"]
                    if o["opportunity_id"] == oid)

    def capped_day_date(self):
        """The local date of the first capped bucket (the fixture starts 08:00)."""
        return (self.START + timedelta(hours=8)).date().isoformat()

    def test_the_fixture_really_caps_the_blue_hour(self):
        # Guard for the assertions below: without this, a fixture that stopped
        # passing the contract would make them vacuously true.
        bundle, details = self.run_main()
        opportunity = self.detail_opportunity(details, self.OID)
        day = next(d for d in opportunity["days"]
                   if d["local_date"] == self.capped_day_date())
        self.assertTrue(day["capped_hours"],
                        "fixture no longer produces a capped hour")
        satisfied = [row for row in day["hours"]
                     if row["status"] == "GUIDANCE_SATISFIED"]
        self.assertTrue(satisfied)
        self.assertEqual({row["local"] for row in satisfied},
                         set(day["capped_hours"]))

    def test_cap_removes_the_hour_from_good_hours_but_not_its_status(self):
        bundle, _ = self.run_main()
        opportunity = self.opportunity(bundle, self.OID)
        day = next(d for d in opportunity["days"]
                   if d["local_date"] == self.capped_day_date())
        # (a) the HOUR is still a satisfied hour ...
        self.assertGreaterEqual(day["hour_counts"]["GUIDANCE_SATISFIED"], 1)
        # ... but the cap keeps it out of the published recommendation surface,
        # so there is no window at all.
        self.assertEqual(day["good_hours"], [])
        # A day with no publishable window must not claim a recommendation: the
        # day-cell cannot print a window for it and the card would promise
        # something the user cannot act on (tw-205-P01 2026-12-04 in the
        # 2026-11-27 refresh). The day is UNFAVORABLE and says why.
        self.assertEqual(day["state"], "UNFAVORABLE")
        self.assertIs(day.get("capped_only"), True)

    def test_the_capped_set_is_exposed_on_the_details_day(self):
        # (b) the per-day capped set is observable without re-deriving it.
        _, details = self.run_main()
        opportunity = self.detail_opportunity(details, self.OID)
        capped_days = {d["local_date"]: d["capped_hours"] for d in opportunity["days"]
                       if d["capped_hours"]}
        self.assertEqual(sorted(capped_days), ["2026-11-26", "2026-11-27"])
        for labels in capped_days.values():
            self.assertTrue(all(len(label) == 5 for label in labels))
        # the clear days carry none
        self.assertNotIn("2026-11-28", capped_days)

    def test_next_good_skips_the_capped_hour(self):
        # (c) next_good is the first satisfied NON-capped hour: on this fixture
        # the capped blue hours of 11-26/11-27 must be skipped for 11-28's.
        bundle, _ = self.run_main()
        opportunity = self.opportunity(bundle, self.OID)
        next_good = (opportunity.get("live") or {}).get("next_good")
        self.assertIsNotNone(next_good)
        assert next_good is not None
        self.assertEqual(next_good["status"], "GUIDANCE_SATISFIED")
        when = datetime.fromisoformat(
            next_good["utc"].replace("Z", "+00:00"))
        self.assertGreaterEqual((when - self.START).total_seconds() / 3600,
                                self.CAPPED_HOURS)
        self.assertTrue(next_good["local"].startswith("2026-11-28"),
                        next_good["local"])

    def test_detail_row_carries_the_night_window(self):
        # (d) the details row of a night genre names the window it sits in.
        _, details = self.run_main()
        opportunity = self.detail_opportunity(details, self.NIGHT_OID)
        rows = {row["local"]: row for day in opportunity["days"]
                for row in day["hours"]}
        self.assertEqual(rows["23:00"]["night_window"]["code"],
                         "NIGHT_CITY_WINDOW")
        self.assertEqual(rows["22:00"]["night_window"]["code"],
                         "NIGHT_CITY_WINDOW")
        self.assertTrue(rows["23:00"]["night_window"]["reason"]["zh-TW"])
        self.assertNotIn("night_window", rows["12:00"])


if __name__ == "__main__":
    unittest.main()
