"""CL-DATA-13: light_direction evaluator semantics — month-sector arc tests.

Root rule (CL-PHOTO-02 evidence report): the solar azimuth at the relevant
light event swings ~51 deg across the year (Tamsui winter ~244, summer ~296),
so a single fixed arc would aim at the wrong direction for half of the year.
The contract stores 12 monthly sectors; the evaluator selects the current
month's sector. Known-coordinate/value pins below use the same NOAA/Meeus
chain that feeds sun_azimuth_deg.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[3]


def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


eb = _load("evaluate_batch", "packages/core-v2/tools/evaluate_batch.py")

# tw-003 monthly sunset azimuths (V2 chain, measured 2026-11-06, ticket 3/5)
SECTORS = [{"arc_center_deg": c, "arc_half_width_deg": 27.5}
           for c in (246.6, 256.0, 267.7, 280.9, 291.0, 295.9,
                     293.9, 285.5, 273.3, 260.5, 249.4, 244.1)]


def _cond(sectors=SECTORS, view=285.0):
    return {"id": "C-LD", "metric": "light_direction", "role": "REQUIRED",
            "operator": "none", "threshold": None, "unknown_policy": "propagate_unknown",
            "condition_tier": "MODIFIER", "sectors": sectors,
            "view_azimuth_deg": view}


class LightDirectionMonthSectorTests(unittest.TestCase):
    def test_month_selection_flips_verdict(self):
        """Same sun azimuth 260 deg: January center 246.6 (diff 13.4 < 27.5)
        passes; July center 295.9 (diff 35.9 > 27.5) fails. A single fixed
        arc cannot reproduce this — the month-sector table is the fix."""
        row = {"sun_azimuth_deg": 260.0}
        jan = eb.condition_verdict(_cond(), {}, row, month=1)
        jul = eb.condition_verdict(_cond(), {}, row, month=7)
        self.assertEqual(jan[0], "PASS")
        self.assertEqual(jul[0], "FAIL")
        self.assertIn("1:", jan[1])
        self.assertIn("7:", jul[1])

    def test_sunset_hour_passes_morning_fails_november(self):
        """Real pinned azimuths (Tamsui, 2026-11-07): sunset hours 244-257 are
        inside the November arc (249.4±27.5); morning sun at ~31 is not."""
        row_sunset = {"sun_azimuth_deg": 244.13181428927388}
        row_morning = {"sun_azimuth_deg": 30.666213312371013}
        self.assertEqual(eb.condition_verdict(_cond(), {}, row_sunset, month=11)[0], "PASS")
        self.assertEqual(eb.condition_verdict(_cond(), {}, row_morning, month=11)[0], "FAIL")

    def test_wrap_around_north(self):
        """Angular distance is circular: center 10, sun 355 → diff 15 <= 27.5."""
        sectors = [{"arc_center_deg": 10.0, "arc_half_width_deg": 27.5}] * 12
        verdict = eb.condition_verdict(_cond(sectors=sectors), {},
                                       {"sun_azimuth_deg": 355.0}, month=3)
        self.assertEqual(verdict[0], "PASS")

    def test_propagate_unknown_view_and_astro_and_sectors(self):
        row = {"sun_azimuth_deg": 250.0}
        self.assertEqual(eb.condition_verdict(_cond(view=None), {}, row, month=11)[0],
                         "UNKNOWN")  # view azimuth unknown → honest unknown
        self.assertEqual(eb.condition_verdict(_cond(view=285.0), {}, {}, month=11)[0],
                         "UNKNOWN")  # astronomy missing
        self.assertEqual(eb.condition_verdict(_cond(view=285.0), {},
                                              {"sun_azimuth_deg": None}, month=11)[0],
                         "UNKNOWN")
        bad = [s for s in SECTORS[:6]]
        self.assertEqual(eb.condition_verdict(_cond(sectors=bad), {}, row, month=11)[0],
                         "UNKNOWN")  # malformed sectors table
        self.assertEqual(eb.condition_verdict(_cond(view=285.0), {}, row, month=None)[0],
                         "UNKNOWN")  # no month context

    def test_value_display_is_sun_azimuth(self):
        v = eb.condition_value(_cond(), {}, {"sun_azimuth_deg": 249.4})
        self.assertEqual(v, 249.4)


class LightDirectionContractTests(unittest.TestCase):
    schema = json.loads(
        (ROOT / "specs/v2/schema/opportunity-v2.1.schema.json").read_text(encoding="utf-8"))

    def test_pilot_contracts_valid_and_sectored(self):
        for oid in ("tw-003-P01", "tw-001-P01"):
            doc = json.loads(
                (ROOT / f"data/v2/opportunities/{oid}.json").read_text(encoding="utf-8"))
            errors = list(jsonschema.Draft202012Validator(self.schema).iter_errors(doc))
            self.assertEqual(errors, [], [e.message for e in errors])
            cond = next(c for c in doc["condition_contract"]["conditions"]
                        if c["metric"] == "light_direction")
            self.assertEqual(len(cond["sectors"]), 12)
            self.assertEqual(cond["condition_tier"], "MODIFIER")
            self.assertEqual(cond["calibration_status"], "provisional")

    def test_fail_reason_override_trilingual(self):
        overrides = json.loads(
            (ROOT / "data/v2/copy/fail_reason_overrides.json").read_text(encoding="utf-8"))
        for oid in ("tw-003-P01", "tw-001-P01"):
            copy = overrides[oid]["light_direction"]
            for lang in ("zh-TW", "en", "ja"):
                self.assertTrue(copy[lang].strip())
            self.assertEqual(copy["zh-TW"], "光線方向不對（逆光／未照亮主體）")


if __name__ == "__main__":
    unittest.main()
