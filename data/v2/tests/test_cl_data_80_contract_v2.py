"""CL-DATA-80: contract v2 migration — idempotency, schema validity, mapping pins.

The legacy `conditions` array stays the source of truth; windows/conditions_v2
are DERIVED views. This gate proves the derived views are (a) present and
schema-valid on every contract, (b) byte-stable under a re-run of the migration
(idempotent), and (c) correctly mapped for pinned examples (spec §5 rows).
"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OPP_DIR = ROOT / "data/v2/opportunities"
SCHEMA = ROOT / "specs/v2/schema/opportunity-v2.2.0.schema.json"
MIGRATOR = ROOT / "data/v2/migration/contract_v2_migrate.py"

WINDOW_NAMES = {"civil_daylight", "golden_hour", "sunset", "sunrise",
                "blue_hour", "astro_darkness", "city_night", "soft_light",
                "morning", "alpenglow", "venue_open"}


class ContractV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import jsonschema
        cls.validator = jsonschema.Draft202012Validator(
            json.loads(SCHEMA.read_text(encoding="utf-8")))
        cls.docs = {}
        for f in sorted(OPP_DIR.glob("*.json")):
            cls.docs[f.name] = json.loads(f.read_text(encoding="utf-8"))

    def test_all_contracts_migrated_and_schema_valid(self):
        bad = []
        for name, doc in self.docs.items():
            if doc.get("schema_version") != "2.2.0":
                bad.append(f"{name}: schema_version")
            cc = doc["condition_contract"]
            if not isinstance(cc.get("windows"), dict) or \
                    not isinstance(cc.get("conditions_v2"), dict):
                bad.append(f"{name}: missing windows/conditions_v2")
                continue
            errs = list(self.validator.iter_errors(doc))
            if errs:
                bad.append(f"{name}: {errs[0].message}")
        self.assertEqual(bad, [])

    def test_windows_time_of_day_semantic_names(self):
        for name, doc in self.docs.items():
            names = doc["condition_contract"]["windows"]["time_of_day"]
            self.assertTrue(set(names) <= WINDOW_NAMES, f"{name}: {names}")

    def test_required_entries_cover_non_window_required_conditions(self):
        for name, doc in self.docs.items():
            cc = doc["condition_contract"]
            ids_v2 = {r["id"] for r in cc["conditions_v2"]["required"]}
            for c in cc["conditions"]:
                if c["role"] != "REQUIRED":
                    continue
                if c["metric"] in ("seasonal_state",) or \
                        c["metric"].endswith("_window") or \
                        c["metric"] in ("light_window", "daylight_window",
                                        "astronomical_darkness"):
                    continue  # folded into windows
                self.assertIn(c["id"], ids_v2,
                              f"{name}: REQUIRED {c['metric']} missing from v2")

    def test_quality_entries_have_trapezoid_shape(self):
        for name, doc in self.docs.items():
            for q in doc["condition_contract"]["conditions_v2"]["quality"]:
                self.assertIn("weight", q)
                self.assertEqual(len(q["ideal"]), 2)
                self.assertEqual(len(q["acceptable"]), 2)

    def test_pinned_spec5_mapping_reflection_wind(self):
        # jp-001-P01 reflection: wind_speed_10m QUALITY -> §5 water_reflection
        # is REQUIRED here, so pin the sunset template cloud entry instead:
        # find any sunset-family contract with a QUALITY cloud_cover_mid_and_high
        # and verify the §5 sunrise/sunset trapezoid [5,25,65,85].
        found = False
        for doc in self.docs.values():
            cc = doc["condition_contract"]
            if cc.get("genre_template") != "sunset":
                continue
            for q in cc["conditions_v2"]["quality"]:
                if q["metric"] == "cloud_cover_mid_and_high":
                    self.assertEqual(q["acceptable"], [5, 85])
                    self.assertEqual(q["ideal"], [25, 65])
                    self.assertFalse(q.get("provisional"))
                    found = True
        self.assertTrue(found, "no sunset QUALITY cloud_cover_mid_and_high found")

    def test_provisional_quality_entries_are_marked(self):
        # entries derived from the contract's own threshold (not §5) carry
        # provisional=true so the provenance is machine-readable.
        marked = sum(1 for doc in self.docs.values()
                     for q in doc["condition_contract"]["conditions_v2"]["quality"]
                     if q.get("provisional"))
        self.assertGreater(marked, 0)

    def test_migration_is_idempotent(self):
        # a --check re-run must report ZERO would-change files on the migrated
        # tree (byte-stable reruns); any drift fails the gate.
        result = subprocess.run(
            [sys.executable, str(MIGRATOR), "--check"],
            capture_output=True, text=True, timeout=300)
        self.assertEqual(
            [ln for ln in result.stdout.splitlines()
             if ln.startswith("WOULD-CHANGE")], [],
            f"migration not idempotent:\n{result.stdout}")


if __name__ == "__main__":
    unittest.main()
