"""CL-DATA-71: viewpoint-relative cloud_base_height condition tests (offline).

Covers the owner verification cases (墨硯山晴天無雲夜 ✗ / 典型雲海夜 ✓), the
contract↔evaluator composition on the real patched contracts, the DEM−200
fallback semantics, and the honesty paths (missing elevation / missing cell /
malformed threshold all propagate UNKNOWN, never a fabricated verdict).
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

AUDIT = {
    "tw-128-P01": ("between", [50, 120]),
    "tw-145-P01": ("lt", 105),
    "tw-148-P01": ("lt", 201),
    "tw-163-P01": ("lt", 218),
    "tw-179-P01": ("lt", 53),
    "tw-035-P06": ("lt", 744),
    "tw-043-P02": ("lt", 3360),
    "tw-047-P01": ("lt", 2892),
    "tw-047-P02": ("lt", 2892),
    "tw-049-P03": ("lt", 3125),
    "jp-037-P02": ("lt", 888),
    "us-087-P01": ("lt", 1390),
    "us-113-P01": ("lt", 2855),
}


def cb1(opportunity_id):
    doc = json.loads((ROOT / f"data/v2/opportunities/{opportunity_id}.json")
                     .read_text(encoding="utf-8"))
    matches = [c for c in doc["condition_contract"]["conditions"]
               if c["metric"] == "cloud_base_height"]
    return doc, matches


def available(m):
    return {"value": m, "state": "AVAILABLE"}


class ContractAuditTests(unittest.TestCase):
    """Every audited contract carries exactly one CL-DATA-71 condition."""

    def test_all_13_patched_contracts_carry_the_condition(self):
        for oid, (operator, threshold) in AUDIT.items():
            with self.subTest(oid=oid):
                _, matches = cb1(oid)
                self.assertEqual(len(matches), 1)
                cond = matches[0]
                self.assertEqual(cond["id"], f"C-{oid}-CB1")
                self.assertEqual(cond["role"], "REQUIRED")
                self.assertEqual(cond["condition_tier"], "MAIN")
                self.assertEqual(cond["domain"], "WEATHER")
                self.assertEqual(cond["evaluation_mode"], "GUIDANCE")
                self.assertEqual(cond["operator"], operator)
                self.assertEqual(cond["threshold"], threshold)
                self.assertEqual(cond["unit"], "m")
                self.assertEqual(cond["unknown_policy"], "propagate_unknown")
                self.assertTrue(cond["claim_refs"]
                                and all(isinstance(x, str) for x in cond["claim_refs"]))
                self.assertEqual(cond["calibration_status"], "provisional")
                self.assertIn(cond["threshold_source"],
                              ("evidence_review", "computed"))

    def test_catalog_band_points_use_evidence_review(self):
        # The owner-recorded band (liuli-cloudheights.json) is evidence_review;
        # every DEM−200 fallback is computed.
        _, cond = cb1("tw-128-P01")
        self.assertEqual(cond[0]["threshold_source"], "evidence_review")
        for oid in ("tw-145-P01", "tw-179-P01", "jp-037-P02", "us-113-P01"):
            _, cond = cb1(oid)
            self.assertEqual(cond[0]["threshold_source"], "computed")

    def test_derivation_rules_annotated_in_notes(self):
        for oid in AUDIT:
            _, matches = cb1(oid)
            zh = matches[0]["notes_i18n"]["zh-TW"]
            self.assertIn("CL-DATA-71", zh, oid)


class MoyanshanOwnerCaseTests(unittest.TestCase):
    """墨硯山琉璃光 (tw-128-P01, band 50–120 m): the owner's two cases."""

    @classmethod
    def setUpClass(cls):
        cls.doc, _ = cb1("tw-128-P01")
        cls.cond = next(c for c in cls.doc["condition_contract"]["conditions"]
                        if c["metric"] == "cloud_base_height")
        cls.cond = dict(cls.cond, viewpoint_elevation_m=157.0)

    def test_clear_night_fails(self):
        # Owner's discovery: a cloudless night (LCL proxy ~549 m from the
        # 2 m T/Td pipeline) used to judge ✓; the new condition FAILs it.
        verdict, detail = eb.condition_verdict(self.cond,
                                               {"lcl_height_m_agl": available(549)}, {})
        self.assertEqual((verdict, detail.split("(")[0]), ("FAIL", "CLOUD_BASE_HEIGHT"))

    def test_typical_cloud_glow_night_passes(self):
        # A deck hanging inside the recorded band (LCL proxy 80 m) passes.
        verdict, _ = eb.condition_verdict(self.cond,
                                          {"lcl_height_m_agl": available(80)}, {})
        self.assertEqual(verdict, "PASS")

    def test_band_edges(self):
        self.assertEqual(eb.condition_verdict(
            self.cond, {"lcl_height_m_agl": available(50)}, {})[0], "PASS")
        self.assertEqual(eb.condition_verdict(
            self.cond, {"lcl_height_m_agl": available(120)}, {})[0], "PASS")
        self.assertEqual(eb.condition_verdict(
            self.cond, {"lcl_height_m_agl": available(121)}, {})[0], "FAIL")
        self.assertEqual(eb.condition_verdict(
            self.cond, {"lcl_height_m_agl": available(49)}, {})[0], "FAIL")

    def test_required_fail_makes_the_hour_unfavorable(self):
        verdict, _ = eb.condition_verdict(self.cond,
                                          {"lcl_height_m_agl": available(549)}, {})
        roles = {self.cond["id"]: "REQUIRED"}
        status, fails, _ = eb.hour_status(roles, {self.cond["id"]: verdict})
        self.assertEqual(status, "UNFAVORABLE")
        self.assertEqual(fails, [self.cond["id"]])


class DerivedThresholdTests(unittest.TestCase):
    """DEM−200 fallback semantics (e.g. jp-037-P02, viewpoint 1088 m)."""

    @classmethod
    def setUpClass(cls):
        doc, _ = cb1("jp-037-P02")
        cls.cond = next(c for c in doc["condition_contract"]["conditions"]
                        if c["metric"] == "cloud_base_height")
        cls.cond = dict(cls.cond, viewpoint_elevation_m=1088.0)

    def test_deck_below_sight_line_passes(self):
        self.assertEqual(eb.condition_verdict(
            self.cond, {"lcl_height_m_agl": available(500)}, {})[0], "PASS")

    def test_clear_night_fails(self):
        self.assertEqual(eb.condition_verdict(
            self.cond, {"lcl_height_m_agl": available(900)}, {})[0], "FAIL")
        self.assertEqual(eb.condition_verdict(
            self.cond, {"lcl_height_m_agl": available(888)}, {})[0], "FAIL")

    def test_threshold_is_viewpoint_minus_200(self):
        self.assertEqual(self.cond["threshold"], 1088 - 200)


class HonestyPathTests(unittest.TestCase):
    def test_missing_viewpoint_elevation_unknown(self):
        cond = {"metric": "cloud_base_height", "operator": "lt",
                "threshold": 105, "role": "REQUIRED"}
        self.assertEqual(eb.condition_verdict(
            cond, {"lcl_height_m_agl": available(50)}, {}),
            ("UNKNOWN", "VIEWPOINT_ELEVATION_UNKNOWN"))

    def test_missing_lcl_cell_unknown(self):
        cond = {"metric": "cloud_base_height", "operator": "lt",
                "threshold": 105, "role": "REQUIRED",
                "viewpoint_elevation_m": 305.0}
        self.assertEqual(eb.condition_verdict(cond, {}, {}),
                         ("UNKNOWN", "CELL_NOT_AVAILABLE"))
        self.assertEqual(eb.condition_verdict(
            cond, {"lcl_height_m_agl": {"value": None, "state": "UNAVAILABLE"}}, {}),
            ("UNKNOWN", "CELL_NOT_AVAILABLE"))

    def test_malformed_between_unknown(self):
        cond = {"metric": "cloud_base_height", "operator": "between",
                "threshold": [50], "role": "REQUIRED",
                "viewpoint_elevation_m": 157.0}
        self.assertEqual(eb.condition_verdict(
            cond, {"lcl_height_m_agl": available(80)}, {}),
            ("UNKNOWN", "INVALID_THRESHOLD"))

    def test_non_numeric_operator_unknown(self):
        cond = {"metric": "cloud_base_height", "operator": "is_true",
                "threshold": None, "role": "REQUIRED",
                "viewpoint_elevation_m": 157.0}
        self.assertEqual(eb.condition_verdict(
            cond, {"lcl_height_m_agl": available(80)}, {}),
            ("UNKNOWN", "NON_NUMERIC_OPERATOR"))

    def test_display_value_is_the_lcl_proxy(self):
        cond = {"metric": "cloud_base_height", "operator": "lt",
                "threshold": 105, "role": "REQUIRED",
                "viewpoint_elevation_m": 305.0}
        self.assertEqual(eb.condition_value(
            cond, {"lcl_height_m_agl": available(549)}, {}), 549)
        self.assertIsNone(eb.condition_value(cond, {}, {}))


class CatalogDemElevationTests(unittest.TestCase):
    def test_curated_elevation_wins_and_dem_fallback(self):
        elevations = eb.v1_place_elevations()
        # tw-047 北大武山 carries a curated elevation (3092).
        self.assertEqual(elevations.get("tw-047"), 3092.0)
        # tw-128 has none — the DEM api_elevation is the fallback.
        self.assertEqual(elevations.get("tw-128"), 156.0)
        self.assertEqual(elevations.get("us-087"), 1590.0)


if __name__ == "__main__":
    unittest.main()
