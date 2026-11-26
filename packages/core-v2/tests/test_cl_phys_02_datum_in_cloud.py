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

import importlib.util
import json
import sys
import unittest
from pathlib import Path

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

    def test_datum_corrected_cloud_base_is_overhead_and_fails(self):
        c = next(c for c in self.contract["conditions"]
                 if c["metric"] == "lcl_height_m_agl")
        bound = dict(c, viewpoint_elevation_m=1092.0)
        verdict, detail = eb.condition_verdict(bound, datunshan_values(), ASTRO)
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
        # contradiction tag) but 低雲 100 % + RH 100 % is the humid deck the
        # in-cloud block needs; the cloud-sea inversion criterion also passes
        # — the block is the only thing standing between this hour and a
        # white-wall recommendation.
        self.assertEqual(self.states["EVALGATE-data-contradiction"], "PASS")
        self.assertEqual(self.states["EVALGATE-cloud-sea-inversion"], "PASS")


class InCloudBoundaryTests(unittest.TestCase):
    """The 50 m margin boundary, just inside and just outside."""

    def values(self, lcl=50, low=85, rh850=None):
        v = {"lcl_height_m_agl": available(lcl),
             "grid_elevation_m": available(1000),
             "cloud_cover_low": available(low)}
        if rh850 is not None:
            v["relative_humidity_850hpa"] = available(rh850)
        v["visibility"] = available(12)
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
    def values(self, rh850=None, rh925=None, low=None):
        v = {"cloud_cover_low": available(low) if low is not None else
             {"value": None, "state": "UNAVAILABLE"}}
        if rh850 is not None:
            v["relative_humidity_850hpa"] = available(rh850)
        if rh925 is not None:
            v["relative_humidity_925hpa"] = available(rh925)
        return v

    def test_humid_inversion_with_low_cloud_passes(self):
        cell = eb.cloud_sea_inversion_state(self.values(rh850=92, low=70))
        self.assertEqual(cell["value"], "inversion")

    def test_dry_layer_fails(self):
        cell = eb.cloud_sea_inversion_state(self.values(rh850=80, rh925=85, low=90))
        self.assertEqual(cell["value"], "no_inversion")

    def test_clear_low_cloud_fails(self):
        cell = eb.cloud_sea_inversion_state(self.values(rh925=99, low=20))
        self.assertEqual(cell["value"], "no_inversion")

    def test_missing_cells_propagate_unknown(self):
        gate = dict(eb.CLOUD_SEA_INVERSION_GATE)
        verdict, detail = eb.phys_gate_verdict(gate, self.values(rh850=92))
        self.assertEqual(verdict, "UNKNOWN")
        self.assertEqual(detail, "CLOUD_SEA_INVERSION_UNAVAILABLE")


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


if __name__ == "__main__":
    unittest.main()
