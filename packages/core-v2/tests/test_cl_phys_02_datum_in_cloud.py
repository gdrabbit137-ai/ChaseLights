"""CL-PHYS-02 stage 1: AGL→ASL datum, In-Cloud Fog block, contradiction.

Regression anchor: 大屯山助航站 (tw-001-P02) was recommended 「可拍」 while the
camera showed a solid white fog wall — 低雲 100 %, LCL 25 m AGL, raw visibility
2.84 km, Open-Meteo grid elevation 1082 m, viewpoint 1092 m. The contract's
cloud-sea condition is `lcl_height_m_agl lt 892` (the DEM−200 rule, ASL); the
AGL number was compared to that ASL threshold (`25 < 892 → PASS`), so a cloud
base actually OVERHEAD at 1107 m ASL read as a cloud sea below the feet.

The fixture below reproduces that hour and asserts it is no longer
recommendable — by the datum-corrected cloud-base verdict AND by the In-Cloud
Fog hard block — plus the boundary cases either side of the in-cloud
threshold, the fog-subject exemption, the contradiction downgrade and the
cloud-sea inversion criterion.
"""
from __future__ import annotations

import contextlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "evaluate_batch", ROOT / "packages/core-v2/tools/evaluate_batch.py")
eb = importlib.util.module_from_spec(spec)
sys.modules["evaluate_batch"] = eb
spec.loader.exec_module(eb)


def available(value, unit=None):
    cell = {"value": value, "state": "AVAILABLE"}
    if unit is not None:
        cell["unit"] = unit
    return cell


def datunshan_values():
    """The 2026-11-26 white-wall hour at 大屯山助航站 (tw-001-P02).

    Grid elevation 1082 m, viewpoint 1092 m, LCL 25 m AGL → cloud base
    1107 m ASL = 15 m ABOVE the camera, i.e. the viewpoint is inside the
    deck (1107 <= 1092 + 50).
    """
    return {
        "lcl_height_m_agl": available(25),
        "grid_elevation_m": available(1082),
        "cloud_cover_low": available(100),
        "relative_humidity_925hpa": available(100),
        "relative_humidity_850hpa": available(100),
        "visibility": available(2.84),
        "aod_550nm": available(0.2),
        "temperature_delta_850_925_c": available(1.0),
        "wind_speed_850hpa": available(3.0),
    }


ASTRO = {"light_window": True}


def contract_doc(opportunity_id):
    return json.loads((ROOT / f"data/v2/opportunities/{opportunity_id}.json")
                      .read_text(encoding="utf-8"))


def evaluated_conditions(contract, viewpoint_elevation_m):
    """The evaluation-layer condition set: demotion + bound viewpoint + gates."""
    conditions = eb.demote_cloud_sea_lcl(list(contract["conditions"]), contract)
    conditions = eb.demote_unresolvable_cloud_base(
        conditions, contract, viewpoint_elevation_m)
    for condition in conditions:
        if condition.get("metric") in ("cloud_base_height", "lcl_height_m_agl"):
            condition["viewpoint_elevation_m"] = viewpoint_elevation_m
    return conditions + eb.phys_gates_for(contract, viewpoint_elevation_m)


class DatunshanWhiteWallRegression(unittest.TestCase):
    """tw-001-P02: the white-out hour must never recommend again."""

    @classmethod
    def setUpClass(cls):
        cls.doc = contract_doc("tw-001-P02")
        cls.contract = cls.doc["condition_contract"]
        cls.conditions = evaluated_conditions(cls.contract, 1092.0)
        cls.states = {c["id"]: eb.condition_verdict(c, datunshan_values(),
                                                   ASTRO)[0]
                      for c in cls.conditions}
        cls.roles = {c["id"]: c.get("role") for c in cls.conditions}

    def test_contract_is_the_cloud_sea_lcl_form(self):
        c = next(c for c in self.contract["conditions"]
                 if c["metric"] == "lcl_height_m_agl")
        self.assertEqual((c["operator"], c["threshold"]), ("lt", 892))

    def test_pre_fix_agl_comparison_would_have_passed(self):
        # The exact bug: 25 (AGL) < 892 (ASL) evaluated PASS.
        self.assertTrue(eb.compare(25.0, "lt", 892))

    def test_datum_corrected_cloud_base_is_overhead(self):
        c = next(c for c in self.contract["conditions"]
                 if c["metric"] == "lcl_height_m_agl")
        bound = dict(c, viewpoint_elevation_m=1092.0)
        # The ASL base (1082 grid + 25 AGL) is 1107 m — 15 m ABOVE the camera.
        self.assertEqual(eb.condition_value(bound, datunshan_values(), ASTRO),
                         1107.0)

    def test_window_below_the_grid_ground_is_unresolvable_not_fail(self):
        # `lt 892` (viewpoint 1092 − 200) lies BELOW the 1082 m grid ground.
        # base_asl >= grid always, so this window can never be met: refusing
        # it as UNKNOWN (reviewer blocker 2) is the honest verdict — FAIL here
        # would pin the cloud_sea subject at 不宜 forever.
        c = next(c for c in self.contract["conditions"]
                 if c["metric"] == "lcl_height_m_agl")
        bound = dict(c, viewpoint_elevation_m=1092.0)
        verdict, detail = eb.condition_verdict(bound, datunshan_values(), ASTRO)
        self.assertEqual(verdict, "UNKNOWN", detail)
        self.assertIn("CLOUD_BASE_WINDOW_UNRESOLVABLE", detail)

    def test_implementable_window_still_judges_on_the_asl_datum(self):
        # Same hour, a window that CAN be resolved: `lt 1100` is satisfied by
        # the raw AGL 25 (the origin/main bug) but not by the ASL base 1107.
        c = {"metric": "cloud_base_height", "operator": "lt", "threshold": 1100,
             "role": "REQUIRED", "viewpoint_elevation_m": 1092.0}
        self.assertTrue(eb.compare(25.0, "lt", 1100))
        verdict, detail = eb.condition_verdict(c, datunshan_values(), ASTRO)
        self.assertEqual(verdict, "FAIL", detail)
        self.assertIn("base_asl=1107m", detail)

    def test_in_cloud_fog_gate_fails(self):
        gate = next(c for c in self.conditions
                    if c["metric"] == eb.IN_CLOUD_FOG_METRIC)
        self.assertEqual(gate["role"], "REQUIRED")
        self.assertEqual(self.states[gate["id"]], "FAIL")
        cell = eb.in_cloud_fog_state(datunshan_values(), 1092.0)
        self.assertEqual(cell["value"], "in_cloud")
        self.assertEqual(cell["cloud_base_asl_m"], 1107.0)
        self.assertEqual(cell["effective_visibility_km"],
                         eb.IN_CLOUD_EFFECTIVE_VISIBILITY_KM)

    def test_hour_is_unfavorable_and_not_guidance_satisfied(self):
        status, fails, _unknowns = eb.hour_status(self.roles, self.states)
        self.assertEqual(status, "UNFAVORABLE")
        self.assertIn("EVALGATE-in-cloud-fog", fails)

    def test_no_recommendation_path_remains_for_the_hour(self):
        # A recommend tier requires a GUIDANCE_SATISFIED hour (build_subject_
        # cards only appends `suitable` entries from those buckets). The
        # gate makes that impossible for this hour, whatever the score.
        self.assertNotEqual(
            eb.hour_status(self.roles, self.states)[0], "GUIDANCE_SATISFIED")

    def test_several_gates_agree_on_the_same_hour(self):
        # 低雲 100 % with 2.84 km visibility is internally consistent (no
        # contradiction tag). The 1107 m ASL deck sits ABOVE the 1092 m
        # summit — but that is the SUMMIT CELL's base, not a valley deck, so
        # the inversion criterion ABSTAINS (UNKNOWN → 資料不足) instead of
        # failing on a geometry this model cannot see (CL-DATA-85). The
        # in-cloud block is still the gate that names the hour, because the
        # evaluation-layer gate precedence puts in_cloud_fog first (see
        # data/v2/tools/build_subject_cards.py SKY_VETO_METRICS).
        self.assertEqual(self.states["EVALGATE-data-contradiction"], "PASS")
        self.assertEqual(self.states["EVALGATE-cloud-sea-inversion"], "UNKNOWN")
        gate = eb.cloud_sea_inversion_state(datunshan_values(), 1092.0)
        self.assertEqual(gate["state"], "UNKNOWN")
        self.assertEqual(gate["reason_code"], "DECK_AT_OR_ABOVE_VIEWPOINT")
        self.assertEqual(gate["deck_ceiling_asl_m"], 1107.0)
        self.assertIn("EVALGATE-in-cloud-fog",
                      eb.hour_status(self.roles, self.states)[1])


class InCloudBoundaryTests(unittest.TestCase):
    """The 50 m margin boundary, just inside and just outside."""

    def values(self, lcl=50, low=85, rh850=None):
        v = {"lcl_height_m_agl": available(lcl),
             "grid_elevation_m": available(1000),
             "cloud_cover_low": available(low)}
        if rh850 is not None:
            v["relative_humidity_850hpa"] = available(rh850)
        # CL-PHYS-03 §2: raw visibility >= 10 km now DISPROVES in-cloud (a veto
        # may not override the provider's own visibility observation). These
        # boundary fixtures describe air you are inside of, so they carry a
        # visibility consistent with that (3 km); the clear-sky override has its
        # own cases in VisibilityDisprovesInCloudTests below.
        v["visibility"] = available(3.0)
        return v

    def test_exactly_fifty_metres_above_the_viewpoint_is_in_cloud(self):
        cell = eb.in_cloud_fog_state(self.values(lcl=50), 1000.0)
        self.assertEqual(cell["value"], "in_cloud")

    def test_one_metre_higher_is_clear(self):
        cell = eb.in_cloud_fog_state(self.values(lcl=51), 1000.0)
        self.assertEqual(cell["value"], "clear")

    def test_deck_evidence_is_required(self):
        # ceiling inside, but neither low cloud >= 80 % nor RH850 >= 95 %.
        cell = eb.in_cloud_fog_state(self.values(lcl=50, low=79, rh850=94), 1000.0)
        self.assertEqual(cell["value"], "clear")

    def test_rh850_branch_alone_is_enough(self):
        cell = eb.in_cloud_fog_state(self.values(lcl=50, low=10, rh850=96), 1000.0)
        self.assertEqual(cell["value"], "in_cloud")

    def test_missing_grid_elevation_is_never_zero_filled(self):
        values = self.values(lcl=5)
        del values["grid_elevation_m"]
        self.assertEqual(eb.in_cloud_fog_state(values, 1000.0)["state"], "UNKNOWN")


class FogSubjectExemptionTests(unittest.TestCase):
    def test_misty_forest_is_exempt_from_the_in_cloud_block(self):
        gates = eb.phys_gates_for({"genre_template": "misty_forest"}, 1000.0)
        metrics = [g["metric"] for g in gates]
        self.assertNotIn(eb.IN_CLOUD_FOG_METRIC, metrics)
        self.assertIn(eb.DATA_CONTRADICTION_METRIC, metrics)

    def test_general_subjects_carry_the_block(self):
        for genre in ("landscape", "sunrise_sunset", "cloud_sea", "city_night"):
            metrics = [g["metric"] for g in
                       eb.phys_gates_for({"genre_template": genre}, 1000.0)]
            self.assertIn(eb.IN_CLOUD_FOG_METRIC, metrics, genre)

    def test_cloud_sea_gets_the_inversion_criterion(self):
        metrics = [g["metric"] for g in
                   eb.phys_gates_for({"genre_template": "cloud_sea"}, 1000.0)]
        self.assertIn(eb.CLOUD_SEA_INVERSION_METRIC, metrics)
        metrics = [g["metric"] for g in
                   eb.phys_gates_for({"genre_template": "landscape"}, 1000.0)]
        self.assertNotIn(eb.CLOUD_SEA_INVERSION_METRIC, metrics)


class ContradictionDowngradeTests(unittest.TestCase):
    def values(self, low, vis):
        return {"cloud_cover_low": available(low), "visibility": available(vis)}

    def test_low_cloud_100_with_24km_visibility_is_contradicting(self):
        cell = eb.data_contradiction_state(self.values(100, 24))
        self.assertEqual(cell["value"], "contradiction")

    def test_thresholds_are_inclusive(self):
        self.assertEqual(eb.data_contradiction_state(self.values(90, 10))["value"],
                         "contradiction")
        self.assertEqual(eb.data_contradiction_state(self.values(89, 24))["value"],
                         "consistent")
        self.assertEqual(eb.data_contradiction_state(self.values(100, 9.9))["value"],
                         "consistent")

    def test_gate_fails_and_caps_the_slot(self):
        gate = dict(eb.DATA_CONTRADICTION_GATE)
        verdict, detail = eb.phys_gate_verdict(gate, self.values(100, 24))
        self.assertEqual((verdict, detail), ("FAIL", "DATA_CONTRADICTION(contradiction)"))
        roles = {gate["id"]: gate["role"]}
        status, fails, _ = eb.hour_status(roles, {gate["id"]: verdict})
        self.assertEqual(status, "UNFAVORABLE")
        self.assertEqual(fails, [gate["id"]])

    def test_unverifiable_pair_never_fabricates_a_downgrade(self):
        gate = dict(eb.DATA_CONTRADICTION_GATE)
        self.assertEqual(eb.phys_gate_verdict(gate, {"cloud_cover_low": available(100)}),
                         ("PASS", "DATA_CONTRADICTION_UNVERIFIED"))


class CloudSeaInversionTests(unittest.TestCase):
    """RH inversion + low cloud + a deck that actually lies BELOW the summit."""

    VIEW = 1092.0

    def values(self, rh850=None, rh925=None, low=None, lcl=None,
               grid=1082.0, viewpoint=None, lcl_reason="NULL_OR_INVALID"):
        v = {"cloud_cover_low": available(low) if low is not None else
             {"value": None, "state": "UNAVAILABLE"}}
        if rh850 is not None:
            v["relative_humidity_850hpa"] = available(rh850)
        if rh925 is not None:
            v["relative_humidity_925hpa"] = available(rh925)
        if grid is not None:
            v["grid_elevation_m"] = available(grid)
        if lcl is not None:
            v["lcl_height_m_agl"] = available(lcl)
        elif lcl_reason is not None:
            v["lcl_height_m_agl"] = {"value": None, "unit": "m",
                                     "state": "UNAVAILABLE",
                                     "reason_code": lcl_reason}
        return v

    def state(self, values, viewpoint=None):
        return eb.cloud_sea_inversion_state(
            values, self.VIEW if viewpoint is None else viewpoint)

    def test_humid_inversion_with_low_cloud_and_deck_below_passes(self):
        # grid 1082 + LCL 5 = 1087 m ASL, below the 1092 m viewpoint.
        cell = self.state(self.values(rh850=92, low=70, lcl=5))
        self.assertEqual(cell["value"], "inversion")
        self.assertEqual(cell["deck_ceiling_asl_m"], 1087.0)

    def test_high_deck_above_the_summit_abstains_never_fails(self):
        # Reviewer COND 1: grid 1082 + LCL 1200 = 2282 m ASL — the SUMMIT
        # cell's base is overhead. A valley deck is invisible to this model
        # (CL-DATA-85), so the criterion must abstain (資料不足), not call
        # 逆溫濕層不足 on humidity structure that actually passed.
        cell = self.state(self.values(rh850=95, low=80, lcl=1200))
        self.assertEqual(cell["state"], "UNKNOWN")
        self.assertIsNone(cell["value"])
        self.assertEqual(cell["reason_code"], "DECK_AT_OR_ABOVE_VIEWPOINT")
        self.assertEqual(cell["deck_ceiling_asl_m"], 2282.0)
        self.assertFalse(cell["deck_below_viewpoint"])
        self.assertTrue(cell["humid_structure"])
        gate = dict(eb.CLOUD_SEA_INVERSION_GATE, viewpoint_elevation_m=self.VIEW)
        verdict, detail = eb.phys_gate_verdict(
            gate, self.values(rh850=95, low=80, lcl=1200))
        self.assertEqual(verdict, "UNKNOWN")
        self.assertEqual(detail,
                         "CLOUD_SEA_INVERSION_DECK_AT_OR_ABOVE_VIEWPOINT")
        # and the hour is NOT_EVALUABLE, never UNFAVORABLE: 資料不足, not 不宜.
        roles = {gate["id"]: gate["role"]}
        self.assertEqual(eb.hour_status(roles, {gate["id"]: verdict})[0],
                         "NOT_EVALUABLE")

    def test_dry_summit_above_a_valley_sea_is_unknown(self):
        # The reviewer's exact case: LCL 800 m AGL over the 1082 m grid =
        # 1882 m ASL ceiling, RH850 96 %, 低雲 80 %. Humidity says "a sea
        # exists", the summit-cell base says "overhead" — the model cannot
        # place the valley deck, so the answer is 資料不足 (UNKNOWN).
        values = self.values(rh850=96, low=80, lcl=800)
        cell = self.state(values)
        self.assertEqual((cell["state"], cell["reason_code"]),
                         ("UNKNOWN", "DECK_AT_OR_ABOVE_VIEWPOINT"))
        gate = dict(eb.CLOUD_SEA_INVERSION_GATE, viewpoint_elevation_m=self.VIEW)
        verdict, _detail = eb.phys_gate_verdict(gate, values)
        self.assertEqual(verdict, "UNKNOWN")

    def test_the_twelve_equal_elevation_spots_survive_only_at_lcl_zero(self):
        # Cond 1's scan: for a spot whose viewpoint equals its grid, the
        # modelled deck is below the viewpoint ONLY at LCL == 0. Anything
        # above abstains; the humidity pair still decides when it does not.
        for lcl, expected in ((0, "AVAILABLE"), (1, "UNKNOWN"), (800, "UNKNOWN")):
            cell = self.state(self.values(rh850=96, low=80, lcl=lcl, grid=1092.0))
            self.assertEqual(cell["state"], expected, lcl)
            if expected == "AVAILABLE":
                self.assertEqual(cell["value"], "inversion")

    def test_refused_lcl_caps_the_deck_at_the_grid_ground(self):
        # Supersaturated along with a humid deck: the deck cannot be above the
        # grid ground, so it is below the summit — a cloud sea is structurally
        # possible (the in-cloud gate handles the white-out itself).
        cell = self.state(self.values(rh850=95, low=80, lcl_reason="SUPERSATURATED"))
        self.assertEqual(cell["value"], "inversion")
        self.assertEqual(cell["deck_ceiling_asl_m"], 1082.0)

    def test_deck_at_the_viewpoint_counts_as_below(self):
        cell = self.state(self.values(rh925=92, low=70, lcl=10))
        self.assertEqual(cell["value"], "inversion")

    def test_dry_layer_fails(self):
        cell = self.state(self.values(rh850=80, rh925=85, low=90, lcl=5))
        self.assertEqual(cell["value"], "no_inversion")

    def test_clear_low_cloud_fails(self):
        cell = self.state(self.values(rh925=99, low=20, lcl=5))
        self.assertEqual(cell["value"], "no_inversion")

    def test_missing_cells_propagate_unknown(self):
        gate = dict(eb.CLOUD_SEA_INVERSION_GATE)
        verdict, detail = eb.phys_gate_verdict(gate, self.values(rh850=92))
        self.assertEqual(verdict, "UNKNOWN")
        self.assertEqual(detail, "CLOUD_SEA_INVERSION_INVERSION_CELLS_UNAVAILABLE")

    def test_missing_viewpoint_is_unknown_not_a_guess(self):
        values = self.values(rh850=92, low=70, lcl=5)
        self.assertEqual(
            eb.cloud_sea_inversion_state(values, None)["state"], "UNKNOWN")
        gate = dict(eb.CLOUD_SEA_INVERSION_GATE)
        self.assertEqual(eb.phys_gate_verdict(
            gate, self.values(rh850=92, low=70, lcl=5))[0], "UNKNOWN")


class CloudBaseDatumTests(unittest.TestCase):
    """Both cloud-base metrics share one ASL datum."""

    COND = {"metric": "cloud_base_height", "operator": "lt", "threshold": 892,
            "role": "REQUIRED", "viewpoint_elevation_m": 1092.0}

    def test_missing_grid_elevation_is_unknown(self):
        verdict, reason = eb.condition_verdict(
            self.COND, {"lcl_height_m_agl": available(25)}, {})
        self.assertEqual((verdict, reason), ("UNKNOWN", "GRID_ELEVATION_UNKNOWN"))

    def test_asl_base_below_the_threshold_passes(self):
        # 200 m AGL over a 300 m grid = 500 m ASL < 892 → a real cloud sea.
        values = {"lcl_height_m_agl": available(200),
                  "grid_elevation_m": available(300)}
        verdict, _ = eb.condition_verdict(self.COND, values, {})
        self.assertEqual(verdict, "PASS")

    def test_catalog_band_stays_viewpoint_relative(self):
        # 琉璃光 tw-128-P01: band 50–120 m, viewpoint 157 m, grid 157 m.
        cond = {"metric": "cloud_base_height", "operator": "between",
                "threshold": [50, 120], "role": "REQUIRED",
                "viewpoint_elevation_m": 157.0}
        values = {"lcl_height_m_agl": available(80),
                  "grid_elevation_m": available(157)}
        self.assertEqual(eb.condition_verdict(cond, values, {})[0], "PASS")
        values["lcl_height_m_agl"] = available(121)
        self.assertEqual(eb.condition_verdict(cond, values, {})[0], "FAIL")

    def test_display_value_is_the_asl_base(self):
        values = {"lcl_height_m_agl": available(25),
                  "grid_elevation_m": available(1082)}
        self.assertEqual(eb.condition_value(self.COND, values, {}), 1107.0)


class CloudSeaLclDemotionTests(unittest.TestCase):
    def test_cloud_sea_lcl_becomes_advisory(self):
        contract = contract_doc("tw-001-P02")["condition_contract"]
        conditions = eb.demote_cloud_sea_lcl(list(contract["conditions"]), contract)
        lcl = next(c for c in conditions if c["metric"] == "lcl_height_m_agl")
        self.assertEqual((lcl["role"], lcl["condition_tier"]), ("QUALITY", "MODIFIER"))
        self.assertEqual(lcl["cl_phys_02"], "cloud_sea_lcl_is_advisory_until_cl_data_85")
        # the owner contract object itself is untouched
        original = next(c for c in contract["conditions"]
                        if c["metric"] == "lcl_height_m_agl")
        self.assertEqual(original["role"], "REQUIRED")

    def test_other_genres_keep_the_lcl_gate(self):
        contract = contract_doc("tw-020-P03")["condition_contract"]
        conditions = eb.demote_cloud_sea_lcl(list(contract["conditions"]), contract)
        lcl = next(c for c in conditions if c["metric"] == "lcl_height_m_agl")
        self.assertEqual(lcl["role"], "REQUIRED")

    def test_cloud_base_height_spelling_is_demoted_too(self):
        # Reviewer blocker 2(b): tw-035-P06 / tw-047-P01 / tw-049-P03 carry
        # the window as `cloud_base_height`, which the metric-keyed demotion
        # missed — they stayed REQUIRED and permanently 不宜.
        for oid in ("tw-035-P06", "tw-047-P01", "tw-049-P03"):
            contract = contract_doc(oid)["condition_contract"]
            conditions = eb.demote_cloud_sea_lcl(
                list(contract["conditions"]), contract)
            window = next(c for c in conditions
                          if c["metric"] == "cloud_base_height")
            self.assertEqual((window["role"], window["condition_tier"]),
                             ("QUALITY", "MODIFIER"), oid)
            self.assertEqual(window["cl_phys_02"],
                             "cloud_sea_lcl_is_advisory_until_cl_data_85")
            original = next(c for c in contract["conditions"]
                            if c["metric"] == "cloud_base_height")
            self.assertEqual(original["role"], "REQUIRED", oid)

    def test_non_cloud_sea_genre_is_demoted_too(self):
        # Reviewer COND 3: outside cloud_sea the DEM−200 window is REGARDED as
        # advisory when it sits below the viewpoint ground — the nine dead
        # subjects must not be pinned at 不宜 forever.
        contract = contract_doc("tw-145-P01")["condition_contract"]
        conditions = eb.demote_unresolvable_cloud_base(
            list(contract["conditions"]), contract, 305.0)
        window = next(c for c in conditions
                      if c["metric"] == "cloud_base_height")
        self.assertEqual((window["role"], window["condition_tier"]),
                         ("QUALITY", "MODIFIER"))
        self.assertEqual(window["cl_phys_02"],
                         "cloud_base_window_below_grid_is_advisory")
        original = next(c for c in contract["conditions"]
                        if c["metric"] == "cloud_base_height")
        self.assertEqual(original["role"], "REQUIRED")

    def test_the_nine_named_subjects_all_get_advisory_windows(self):
        elevations = eb.v1_place_elevations()
        for oid in ("tw-145-P01", "tw-148-P01", "tw-163-P01", "tw-179-P01",
                    "jp-037-P02", "us-113-P01", "tw-043-P02", "tw-047-P02",
                    "us-087-P01"):
            doc = contract_doc(oid)
            contract = doc["condition_contract"]
            camera = next(
                (c.get("altitude_m") for c in doc.get("camera_contexts", [])
                 if isinstance(c.get("altitude_m"), (int, float))), None)
            viewpoint = camera if camera is not None else elevations[doc["place_id"]]
            conditions = eb.demote_unresolvable_cloud_base(
                list(contract["conditions"]), contract, viewpoint)
            window = next(c for c in conditions
                          if c["metric"] in ("cloud_base_height", "lcl_height_m_agl"))
            self.assertEqual(window["role"], "QUALITY", oid)
            # and the hour no longer reads UNFAVORABLE on that clause alone
            values = {"lcl_height_m_agl": available(100),
                      "grid_elevation_m": available(viewpoint),
                      "cloud_cover_low": available(30),
                      "relative_humidity_850hpa": available(70),
                      "visibility": available(20)}
            bound = dict(window, viewpoint_elevation_m=viewpoint)
            verdict = eb.condition_verdict(bound, values, ASTRO)[0]
            self.assertEqual(verdict, "UNKNOWN", oid)
            status = eb.hour_status({window["id"]: window["role"]},
                                    {window["id"]: verdict})[0]
            self.assertNotEqual(status, "UNFAVORABLE", oid)

    def test_a_resolvable_band_window_keeps_its_required_role(self):
        # tw-128-P01 (琉璃光) is a `between 50–120` band, not a DEM−200
        # threshold below the ground: it must NOT be demoted.
        contract = contract_doc("tw-128-P01")["condition_contract"]
        conditions = eb.demote_unresolvable_cloud_base(
            list(contract["conditions"]), contract, 157.0)
        window = next(c for c in conditions
                      if c["metric"] == "cloud_base_height")
        self.assertEqual(window["role"], "REQUIRED")


class SupersaturatedLclFailClosedTests(unittest.TestCase):
    """Reviewer blocker 1: a refused LCL must not dissolve the veto.

    T2m − Td2m < 0 makes the parcel LCL undefined; the adapter tags the cell
    SUPERSATURATED. With a saturated deck alongside, that refusal IS the fog
    signature (the air is at or beyond saturation at the ground), so the gate
    must FAIL, not return UNKNOWN — an UNKNOWN veto is a PASS.
    """

    def values(self, lcl_reason="SUPERSATURATED", low=100, rh850=100):
        return {"lcl_height_m_agl": {"value": None, "unit": "m",
                                     "state": "UNAVAILABLE",
                                     "reason_code": lcl_reason},
                "grid_elevation_m": available(1082),
                "cloud_cover_low": available(low),
                "relative_humidity_850hpa": available(rh850),
                "visibility": available(2.84)}

    def gate(self):
        return dict(eb.IN_CLOUD_FOG_GATE, viewpoint_elevation_m=1092.0)

    def test_adapter_tags_a_refused_lcl(self):
        spec = importlib.util.spec_from_file_location(
            "omb_test", ROOT / "packages/core-v2/adapters/open_meteo_batch.py")
        omb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(omb)
        self.assertEqual(omb._lcl_height_m(10.0, 10.5), None)
        self.assertEqual(omb._lcl_cell(10.0, 10.5)["reason_code"], "SUPERSATURATED")
        self.assertEqual(omb._lcl_cell(10.0, 9.0)["value"], 125.0)
        self.assertEqual(omb._lcl_cell(None, 9.0)["reason_code"], "NULL_OR_INVALID")

    def test_lcl_asl_reports_the_refusal_distinctly(self):
        self.assertEqual(eb.lcl_asl_m(self.values())[1], "LCL_SUPERSATURATED")
        self.assertEqual(eb.lcl_asl_m(self.values(lcl_reason="NULL_OR_INVALID"))[1],
                         "CELL_NOT_AVAILABLE")

    def test_refused_lcl_with_saturated_deck_fails_closed(self):
        cell = eb.in_cloud_fog_state(self.values(), 1092.0)
        self.assertEqual(cell["state"], "AVAILABLE")
        self.assertEqual(cell["value"], "in_cloud")
        self.assertEqual(cell["reason_code"], "LCL_UNAVAILABLE_SATURATED_DECK")
        self.assertEqual(eb.phys_gate_verdict(self.gate(), self.values()),
                         ("FAIL", "IN_CLOUD_FOG(in_cloud)"))

    def test_absent_lcl_keeps_its_own_reason_and_does_not_close(self):
        # Reviewer COND 2: a plainly absent LCL (NULL_OR_INVALID — the
        # provider shipped no dew-point pair) is NOT a saturation claim. On an
        # overcast day it must stay UNKNOWN (資料不足) with its own reason, not
        # become a hard ✕. Only SUPERSATURATED fails closed.
        cell = eb.in_cloud_fog_state(self.values(lcl_reason="NULL_OR_INVALID"),
                                     1092.0)
        self.assertEqual(cell["state"], "UNKNOWN")
        self.assertEqual(cell["reason_code"], "CELL_NOT_AVAILABLE")
        self.assertEqual(eb.phys_gate_verdict(
            self.gate(), self.values(lcl_reason="NULL_OR_INVALID")),
            ("PASS", "IN_CLOUD_FOG_UNVERIFIED"))

    def test_supersaturated_lcl_is_the_only_fail_closed_branch(self):
        cell = eb.in_cloud_fog_state(self.values(lcl_reason="SUPERSATURATED"),
                                     1092.0)
        self.assertEqual(cell["state"], "AVAILABLE")
        self.assertEqual(cell["reason_code"], "LCL_UNAVAILABLE_SATURATED_DECK")

    def test_rh850_branch_alone_closes_the_gate(self):
        verdict, _ = eb.phys_gate_verdict(self.gate(), self.values(low=10, rh850=96))
        self.assertEqual(verdict, "FAIL")

    def test_dry_air_with_a_refused_lcl_stays_unverified(self):
        # No saturated deck: the refusal alone is not a white-out.
        self.assertEqual(eb.phys_gate_verdict(
            self.gate(), self.values(low=10, rh850=50)), ("PASS", "IN_CLOUD_FOG_UNVERIFIED"))

    def test_missing_grid_geometry_still_propagates_unknown(self):
        values = {"lcl_height_m_agl": available(25),
                  "cloud_cover_low": available(100)}
        self.assertEqual(eb.in_cloud_fog_state(values, 1092.0)["state"], "UNKNOWN")

    def test_fog_subjects_stay_exempt_from_the_fail_closed_gate(self):
        metrics = [g["metric"] for g in
                   eb.phys_gates_for({"genre_template": "misty_forest"}, 1092.0)]
        self.assertNotIn(eb.IN_CLOUD_FOG_METRIC, metrics)


class BelowGridWindowTests(unittest.TestCase):
    """Reviewer blocker 2: the 12 contracts whose window sits below the ground."""

    CONTRACTS = (
        "tw-145-P01", "tw-148-P01", "tw-163-P01", "tw-179-P01",   # city_night
        "jp-037-P02", "us-113-P01",                                # sunrise
        "tw-043-P02", "tw-047-P02",                                # sunset
        "us-087-P01",                                              # mountain_view
        "tw-035-P06", "tw-047-P01", "tw-049-P03",                  # cloud_sea
    )

    def test_all_twelve_are_unknown_not_fail(self):
        elevations = eb.v1_place_elevations()
        for oid in self.CONTRACTS:
            doc = json.loads((ROOT / f"data/v2/opportunities/{oid}.json")
                             .read_text(encoding="utf-8"))
            contract = doc["condition_contract"]
            camera = next(
                (c.get("altitude_m") for c in doc.get("camera_contexts", [])
                 if isinstance(c.get("altitude_m"), (int, float))), None)
            viewpoint = camera if camera is not None else elevations[doc["place_id"]]
            window = next(c for c in contract["conditions"]
                          if c["metric"] in ("cloud_base_height", "lcl_height_m_agl")
                          and c.get("operator") in ("lt", "lte"))
            # The reviewer's finding: viewpoint == grid elevation (V1
            # api_elevation), so base_asl >= viewpoint > threshold forever.
            values = {"lcl_height_m_agl": available(100),
                      "grid_elevation_m": available(viewpoint),
                      "cloud_cover_low": available(30),
                      "relative_humidity_850hpa": available(70),
                      "visibility": available(20)}
            bound = dict(window, viewpoint_elevation_m=viewpoint)
            verdict, detail = eb.condition_verdict(bound, values, ASTRO)
            self.assertEqual(verdict, "UNKNOWN", f"{oid}: {detail}")
            self.assertIn("CLOUD_BASE_WINDOW_UNRESOLVABLE", detail, oid)
            # and the subject is no longer pinned at 不宜 by this window
            demoted = eb.demote_cloud_sea_lcl([bound], contract)
            demoted = eb.demote_unresolvable_cloud_base(demoted, contract,
                                                        viewpoint)
            roles = {c["id"]: c["role"] for c in demoted}
            status = eb.hour_status(roles, {bound["id"]: verdict})[0]
            self.assertNotEqual(status, "UNFAVORABLE", oid)

    def test_window_that_can_be_resolved_is_not_swallowed(self):
        # grid 300, `lt 500`: a base at 450 m ASL (150 m AGL) is reachable.
        cond = {"id": "C", "metric": "cloud_base_height", "operator": "lt",
                "threshold": 500, "role": "REQUIRED", "viewpoint_elevation_m": 500.0}
        values = {"grid_elevation_m": available(300), "lcl_height_m_agl": available(150)}
        self.assertEqual(eb.condition_verdict(cond, values, ASTRO)[0], "PASS")
        values["lcl_height_m_agl"] = available(250)
        self.assertEqual(eb.condition_verdict(cond, values, ASTRO)[0], "FAIL")


def prefix_cloud_base_verdict(condition, values, require_viewpoint=True):
    """origin/main semantics: judge the raw AGL number (no ASL conversion).

    Kept only as documentation of the pre-fix comparison; the REAL
    before/after contrast runs the whole fixture against a pristine
    origin/main worktree (BaselineContrastTests below), never a monkeypatch.
    """
    lcl = eb._cell_value(values, "lcl_height_m_agl")
    if lcl is None:
        return "UNKNOWN", "CELL_NOT_AVAILABLE"
    try:
        passed = eb.compare(lcl, condition.get("operator"),
                            condition.get("threshold"))
    except Exception:
        return "UNKNOWN", "INVALID_THRESHOLD"
    return ("PASS" if passed else "FAIL"), "PREFIX_AGL"


# The integration gate refuses a skipped case ("SKIP/expected failure cannot
# satisfy integration"), and a floating `origin/main` stops being "before" as
# soon as the fix merges — so the before leg is a COMMITTED transcript of the
# same script run against 71b1299a2 (the last main before the datum fix). The
# after leg runs the shipped tree in this process. Reproducible everywhere,
# no worktree, no environment variable, nothing skipped.
BEFORE_COMMIT = "71b1299a2"
BEFORE_FIXTURE = (ROOT / "packages/core-v2/tests/fixtures"
                  / f"cl_phys_02_before_{BEFORE_COMMIT}.txt")


class RealPathMainTests(unittest.TestCase):
    """Drive evaluate_batch.main() end to end (stubbed provider only).

    This exercises the per-hour `grid_elevation_m` injection, the viewpoint
    binding, the evaluation-layer gates and the day summarisation — none of
    which the hand-built fixtures above can prove.
    """

    HOURS = 168
    OID = "tw-001-P02"

    def artifact(self, lcl_cell):
        start = datetime(2026, 11, 26, 0, 0, tzinfo=timezone.utc)
        hours = []
        for index in range(self.HOURS):
            values = {
                "temperature_2m": available(12.0), "dew_point_2m": available(12.1),
                "relative_humidity_2m": available(100), "cloud_cover_low": available(100),
                "cloud_cover_mid": available(100), "cloud_cover_high": available(100),
                "cloud_cover_total": available(100), "wind_speed_10m": available(3.0),
                "visibility": available(2.84), "precipitation": available(0.2),
                "precipitation_probability": available(80),
                "relative_humidity_925hpa": available(100),
                "relative_humidity_850hpa": available(100),
                "wind_speed_850hpa": available(3.0),
                "aod_550nm": available(0.2),
                "temperature_delta_850_925_c": available(1.0),
                "cloud_cover_mid_and_high": available(100),
                "lcl_height_m_agl": dict(lcl_cell),
            }
            hours.append({
                "valid_at_utc": (start + timedelta(hours=index))
                .strftime("%Y-%m-%dT%H:%M:%SZ"),
                "values": values})
        return {
            "adapter_version": "open-meteo-batch-0.1", "provider": "open-meteo",
            "place_coordinate": {"latitude": 25.1833, "longitude": 121.5333},
            "grid": {"latitude": 25.18, "longitude": 121.53, "elevation_m": 1082.0},
            "retrieved_at_utc": "2026-11-26T00:00:00Z",
            "sources": [
                {"source_url": "stub://forecast", "source_sha256": "0" * 64,
                 "kind": "forecast", "fields": []},
                {"source_url": "stub://air-quality", "source_sha256": "0" * 64,
                 "kind": "air_quality", "fields": []}],
            "freshness_policy": {}, "notes": {},
            "hours": hours,
        }

    def run_main(self, lcl_cell):
        scratch = Path(tempfile.mkdtemp(prefix="cl-phys02-"))
        captured = {}

        def fake_fetch(lat, lon, forecast_hours):
            self.assertEqual(forecast_hours, self.HOURS)
            captured["artifact"] = self.artifact(lcl_cell)
            captured["forecast_hours"] = forecast_hours
            return captured["artifact"]

        out = scratch / "bundle.json"
        argv = ["evaluate_batch.py", "--forecast-hours", str(self.HOURS),
                "--only-place-id", "tw-001", "--out", str(out),
                "--archive", str(scratch / "archive"),
                "--details-dir", str(scratch / "details")]
        with mock.patch.object(eb.adapter, "fetch_place", fake_fetch), \
                mock.patch.object(sys, "argv", argv):
            eb.main()
        bundle = json.loads(out.read_text(encoding="utf-8"))
        opportunity = next(
            o for place in bundle["places"] for o in place["opportunities"]
            if o["opportunity_id"] == self.OID)
        return captured, opportunity

    def refused_lcl(self):
        return {"value": None, "unit": "m", "state": "UNAVAILABLE",
                "reason_code": "SUPERSATURATED"}

    def test_grid_elevation_is_injected_on_every_hour_row(self):
        captured, _ = self.run_main(available(25))
        self.assertEqual(captured["forecast_hours"], self.HOURS)
        # the fixture and the declared horizon agree: no 48 h of data behind a
        # 168 h claim (reviewer COND 5).
        self.assertEqual(len(captured["artifact"]["hours"]), self.HOURS)
        for hour_row in captured["artifact"]["hours"]:
            cell = hour_row["values"]["grid_elevation_m"]
            self.assertEqual(cell["state"], "AVAILABLE")
            self.assertEqual(cell["value"], 1082.0)

    def test_branch_blocks_the_white_wall_hour_on_the_real_path(self):
        _, opportunity = self.run_main(available(25))
        self.assertTrue(opportunity["days"])
        for day in opportunity["days"]:
            self.assertEqual(day["state"], "UNFAVORABLE", day["local_date"])
            gate = next(c for c in day["conditions"]
                        if c["metric"] == "in_cloud_fog")
            self.assertEqual(gate["day_verdict"], "FAIL")
            self.assertEqual(day["hour_counts"]["GUIDANCE_SATISFIED"], 0)

    def test_refused_lcl_is_blocked_on_the_real_path(self):
        # Reviewer blocker 1 end to end: LCL refused + 低雲 100 + RH850 100.
        _, opportunity = self.run_main(self.refused_lcl())
        for day in opportunity["days"]:
            self.assertEqual(day["state"], "UNFAVORABLE", day["local_date"])
            gate = next(c for c in day["conditions"]
                        if c["metric"] == "in_cloud_fog")
            self.assertEqual(gate["day_verdict"], "FAIL")

    def test_contrast_branch_blocks_the_hour(self):
        _, after = self.run_main(available(25))
        self.assertFalse(any(d["state"] == "GUIDANCE_SATISFIED"
                             for d in after["days"]))
        named = [c["metric"] for d in after["days"] for c in d["conditions"]
                 if c["day_verdict"] == "FAIL"]
        self.assertIn("in_cloud_fog", named)


class BaselineContrastTests(unittest.TestCase):
    """The contrast is REAL: the same fixture, two checkouts, two processes.

    `cl_phys_02_contrast.py` imports the evaluate_batch of the tree it is
    pointed at and drives main() with the identical 168 h artifact. The
    "before" leg is a pristine `git worktree add --detach ... origin/main`,
    not this branch's code with old semantics monkeypatched back in.
    """

    SCRIPT = ROOT / "packages/core-v2/tests/cl_phys_02_contrast.py"


    def run_tree(self, root):
        out = subprocess.run([sys.executable, str(self.SCRIPT), str(root)],
                             capture_output=True, text=True, timeout=600)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        return out.stdout

    def test_before_transcript_is_the_pre_fix_behaviour(self):
        """The committed before-leg must still show the bug the fix removed.

        If this fails, either the fixture was hand-edited or the contrast script
        changed what it prints — regenerate it from 71b1299a2, never edit it.
        """
        self.assertTrue(BEFORE_FIXTURE.exists(), str(BEFORE_FIXTURE))
        before = BEFORE_FIXTURE.read_text(encoding="utf-8")
        self.assertIn("state=GUIDANCE_SATISFIED", before,
                      "the pre-fix tree recommended the white-wall day")
        self.assertIn("lcl_height_m_agl: PASS", before,
                      "the pre-fix verdict came from the AGL comparison")
        self.assertNotIn("in_cloud_fog", before,
                         "the pre-fix tree had no in-cloud gate at all")

    def test_branch_blocks_the_white_wall(self):
        after = self.run_tree(ROOT)
        self.assertNotIn("state=GUIDANCE_SATISFIED", after)
        self.assertIn("state=UNFAVORABLE", after)
        self.assertIn("in_cloud_fog: FAIL", after)


if __name__ == "__main__":
    unittest.main()


class DemotionBoundTests(unittest.TestCase):
    """CL-PHYS-02 §4b: the demotion bound is the GRID GROUND, not the viewpoint.

    Reviewer condition: a mountain viewpoint whose DEM sits well below it
    (vp 3055 / grid 2700 / threshold 2855) has a satisfiable window — keying
    the demotion on the viewpoint would silently downgrade a live REQUIRED
    clause to advisory.
    """

    @staticmethod
    def _cond(threshold):
        return {"metric": "cloud_base_height", "role": "REQUIRED",
                "operator": "lt", "threshold": threshold}

    def test_threshold_above_grid_ground_stays_required(self):
        out = eb.demote_unresolvable_cloud_base(
            [self._cond(2855)], {}, 3055, 2700)
        self.assertEqual(out[0]["role"], "REQUIRED")
        self.assertNotIn("cl_phys_02", out[0])

    def test_threshold_below_grid_ground_is_demoted(self):
        out = eb.demote_unresolvable_cloud_base(
            [self._cond(2655)], {}, 3055, 2700)
        self.assertEqual(out[0]["role"], "QUALITY")
        self.assertEqual(out[0]["cl_phys_02"],
                         "cloud_base_window_below_grid_is_advisory")

    def test_no_grid_ground_falls_back_to_viewpoint(self):
        out = eb.demote_unresolvable_cloud_base(
            [self._cond(2655)], {}, 2700, None)
        self.assertEqual(out[0]["role"], "QUALITY")
