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
import sys
import unittest
from datetime import date
from pathlib import Path

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
        # ... but the data floor still applies to it.
        self.assertIn(eb.DATA_FLOOR_METRIC, metrics)


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
        self.assertEqual(list(venues), ["jp-018-P01"])
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


if __name__ == "__main__":
    unittest.main()
