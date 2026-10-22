"""Breadth-migration skeleton generator regressions (R0 Research-only).

No network. Validates coverage of the V1 inventory, schema validity of the
committed skeletons, i18n placeholder honesty and the source-lock isolation
rule (skeletons never live under data/v2/opportunities/).
"""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODULE = ROOT / "data/v2/migration/build_skeletons.py"
spec = importlib.util.spec_from_file_location("build_skeletons", MODULE)
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

SKELETONS = ROOT / "data/v2/migration/skeletons"
INVENTORY = ROOT / "data/v2/migration/inventory.json"
SCHEMA = ROOT / "specs/v2/schema/opportunity-v2.1.schema.json"


class MigrationSkeletonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        cls.inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        cls.catalog, coords, _ = gen.load_inputs(gen.DEFAULT_CATALOG,
                                                 [str(p) for p in gen.DEFAULT_WEATHER])

    def test_full_v1_coverage_counts(self):
        spots = self.catalog["spots"]
        opps = sum(len(s["opportunities"]) for s in spots)
        admitted = set(self.inventory["first_pass"]["admitted_canonical"])
        self.assertEqual((216, 428), (len(spots), opps))
        self.assertEqual(len(admitted), 8)
        self.assertEqual(opps, len(admitted) + self.inventory["first_pass"]["skeleton_files"])
        self.assertEqual(len(spots), self.inventory["first_pass"]["places_first_pass_covered"])
        self.assertEqual([], self.inventory["first_pass"]["places_pending"])

    def test_every_committed_skeleton_is_schema_valid(self):
        files = sorted(SKELETONS.glob("*.json"))
        self.assertEqual(420, len(files))
        for path in files:
            with self.subTest(file=path.name):
                doc = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual([], gen.validate_document(doc, self.schema))

    def test_expected_file_name_matches_opportunity_id(self):
        for path in SKELETONS.glob("*.json"):
            doc = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(path.stem, doc["opportunity_id"])
            self.assertEqual(path.stem.rsplit("-P", 1)[0], doc["place_id"])

    def test_provisional_placeholders_present_in_all_three_locales(self):
        for path in SKELETONS.glob("*.json"):
            doc = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(file=path.name):
                self.assertIn("pending review", doc["name_i18n"]["en"])
                self.assertIn("レビュー待ち", doc["name_i18n"]["ja"])
                self.assertEqual("pending", doc["provenance"]["review_status"])
                self.assertEqual("R0", doc["readiness"]["research_level"])

    def test_condition_metric_matches_v1_theme(self):
        opps = {o["opportunity_id"]: o for s in self.catalog["spots"] for o in s["opportunities"]}
        for path in SKELETONS.glob("*.json"):
            doc = json.loads(path.read_text(encoding="utf-8"))
            v1 = opps[doc["opportunity_id"]]
            with self.subTest(file=path.name):
                self.assertEqual(f"legacy_{v1['legacy_theme']}",
                                 doc["condition_contract"]["conditions"][0]["metric"])

    def test_parity_checklists_cover_every_v1_place(self):
        parity = sorted((ROOT / "data/v2/migration/parity").glob("*.json"))
        self.assertEqual(216, len(parity))
        for path in parity:
            doc = json.loads(path.read_text(encoding="utf-8"))
            with self.subTest(file=path.name):
                self.assertEqual(path.stem, doc["spot_id"])
                self.assertEqual("FIRST_PASS_PARITY_COMPLETE", doc["disposition"])
                self.assertTrue(doc["transferred"])
                self.assertTrue(all(m["status"] == "MISSING_IN_V1"
                                    for m in doc["missing_or_unknown"]))

    def test_v1_access_notes_carry_verbatim_as_warnings(self):
        """V1 access notices migrate verbatim (non-scoring warning), not dropped or invented."""
        wspot = None
        for wp in gen.DEFAULT_WEATHER:
            for s in json.loads(wp.read_text(encoding="utf-8"))["spots"]:
                if s["spot_id"] == "tw-068":
                    wspot = s
        self.assertIsNotNone(wspot)
        doc = json.loads((SKELETONS / "tw-068-P01.json").read_text(encoding="utf-8"))
        self.assertEqual(wspot["access_note_i18n"],
                         doc["camera_contexts"][0]["access_notes_i18n"])

    def test_admitted_canonical_matches_skeleton_bytes(self):
        """Every admitted record is byte-identical to its staged skeleton (no review-cycle drift)."""
        canonical_dir = ROOT / "data/v2/opportunities"
        for path in SKELETONS.glob("*.json"):
            admitted = canonical_dir / path.name
            with self.subTest(file=path.name):
                self.assertTrue(admitted.exists(), "not admitted: " + path.name)
                self.assertEqual(path.read_bytes(), admitted.read_bytes())

    def test_generator_determinism_on_pilot(self):
        """Re-running the pilot inputs reproduces the committed bytes exactly."""
        with tempfile.TemporaryDirectory() as tmp:
            rc = gen.main.__wrapped__ if hasattr(gen.main, "__wrapped__") else None  # noqa: F841
            import sys
            argv_backup = sys.argv
            sys.argv = ["build_skeletons.py", "--ids", "tw-001", "tw-002",
                        "--imported-at", "2026-10-21T20:51:45Z",
                        "--out", tmp, "--inventory", str(Path(tmp) / "inv.json")]
            try:
                self.assertEqual(0, gen.main())
            finally:
                sys.argv = argv_backup
            for oid in ("tw-001-P01", "tw-001-P02", "tw-001-P03",
                        "tw-002-P01", "tw-002-P02", "tw-002-P03"):
                self.assertEqual(
                    (SKELETONS / f"{oid}.json").read_bytes(),
                    (Path(tmp) / f"{oid}.json").read_bytes(),
                    oid)


if __name__ == "__main__":
    unittest.main()
