"""CL-DATA-18 human-review gate reform tests (owner ruling 2026-11-06).

The worker2 human-review precondition is replaced by AI verification: a change
to a human-review/byte-pinned geometry or light-window field is admitted only
when its provenance is complete — an authoritative source URL, a verification
date, and a derivation_method marker on the machine-readable field. The gate
itself is RETAINED as a provenance admission control: this module encodes that
admission rule and fails any filled geometry/light-window record that lacks it.
"""
import json
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
OPS = ROOT / "data/v2/opportunities"
RULE = "owner ruling 2026-11-06 (AI fact-check with source URL+date replaces human review)"

# The CL-DATA-18 fills: provenance-complete AI verification expected.
FILLED_IDS = ("tw-034-P02", "tw-036-P01", "tw-082-P01", "jp-010-P01",
              "us-071-P01", "tw-026-P01", "tw-026-P02")
KEEP_UNKNOWN_IDS = ("tw-016-P01", "tw-086-P01", "tw-086-P02", "tw-086-P03")


def admission_violations(doc):
    """Return provenance violations for one opportunity document.

    Admission rule (CL-DATA-18): every filled (non-null) camera geometry point
    or navigation coordinate must carry (a) a derivation_method/evidence provenance
    with an authoritative source URL or in-repo sibling reference, and (b) a
    verification date. Fills without complete provenance are violations — this
    is the reformed gate: same guard, new admission condition.
    """
    problems = []
    oid = doc.get("opportunity_id", "?")
    for cam in doc.get("camera_contexts", []):
        geo = cam.get("geometry") or {}
        if geo.get("geojson") is not None:
            dm = geo.get("derivation_method") or ""
            if not dm:
                problems.append(f"{oid}: camera {cam.get('id')} filled without derivation_method")
            elif not (re.search(r"https?://", dm) or "sibling" in dm):
                problems.append(f"{oid}: camera {cam.get('id')} derivation_method lacks a source")
            elif not re.search(r"\d{4}-\d{2}-\d{2}", dm):
                problems.append(f"{oid}: camera {cam.get('id')} derivation_method lacks a date")
    for nav in doc.get("navigation_targets", []):
        if nav.get("lat") is not None or nav.get("lon") is not None:
            if not nav.get("evidence_refs"):
                problems.append(f"{oid}: nav {nav.get('id')} filled without evidence_refs")
    return problems


class AiVerificationAdmissionGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = {p.stem: json.loads(p.read_text(encoding="utf-8"))
                    for p in sorted(OPS.glob("*.json"))}

    def test_filled_records_carry_complete_provenance(self):
        for oid in FILLED_IDS:
            with self.subTest(oid=oid):
                self.assertEqual([], admission_violations(self.docs[oid]),
                                 admission_violations(self.docs[oid]))
                doc = self.docs[oid]
                prov = doc["provenance"]
                self.assertIn("AI-verification 2026-11-06", prov["reviewed_by"])
                self.assertIn("https://", prov["reviewed_by"])
                self.assertIn("replaces human review", prov["reviewed_by"])
                self.assertNotIn("GEOMETRY_GAP", doc["readiness"]["gaps"])

    def test_no_source_fill_is_rejected(self):
        # The reform keeps the gate: a coordinate fill WITHOUT provenance must
        # be flagged by the admission rule.
        broken = json.loads(json.dumps(self.docs["tw-016-P01"], ensure_ascii=False))
        broken["camera_contexts"][0]["geometry"]["geojson"] = {
            "type": "Point", "coordinates": [121.0, 24.0]}
        broken["camera_contexts"][0]["geometry"]["status"] = "derived"
        # CL-INT-83 merge note: CL-DATA-16 put an elevation provenance
        # derivation_method on this camera's geometry; a fill WITHOUT
        # provenance must also clear it to exercise the admission rule.
        broken["camera_contexts"][0]["geometry"]["derivation_method"] = None
        self.assertTrue(any("derivation_method" in v for v in admission_violations(broken)))

    def test_honest_unknowns_are_preserved(self):
        # Ghost gaps with NO authoritative source stay honestly unknown.
        for oid in KEEP_UNKNOWN_IDS:
            with self.subTest(oid=oid):
                doc = self.docs[oid]
                for cam in doc["camera_contexts"]:
                    if oid != "tw-016-P01":
                        continue  # tw-016 camera stays unknown
                    # CL-INT-83 merge note: CL-DATA-20 AI-verified the tw-016
                    # summit geometry (with provenance); the honest-unknown
                    # assertion becomes the admission rule instead — a fill
                    # must carry a complete derivation_method.
                    if cam["geometry"].get("geojson") is not None:
                        dm = cam["geometry"].get("derivation_method") or ""
                        self.assertRegex(dm, r"https?://")
                        self.assertRegex(dm, r"\d{4}-\d{2}-\d{2}")
                for nav in doc["navigation_targets"]:
                    if oid.startswith("tw-086"):
                        self.assertIsNone(nav.get("lat"))
                        self.assertIsNone(nav.get("lon"))
                        self.assertEqual("needs_review", nav["status"])

    def test_us057_high_latitude_light_window(self):
        doc = self.docs["us-057-P01"]
        lw = [c for c in doc["condition_contract"]["conditions"]
              if c["metric"] == "light_window"]
        self.assertEqual(1, len(lw))
        w = lw[0]
        self.assertEqual("REQUIRED", w["role"])
        self.assertEqual("MAIN", w["condition_tier"])
        self.assertEqual("computed", w["threshold_source"])
        self.assertEqual("provisional", w["validation_status"])
        zh = w["notes_i18n"]["zh-TW"]
        self.assertIn("CL-DATA-18", zh)
        self.assertIn("66.56", zh)
        self.assertIn("CL-DATA-11", zh)
        self.assertIn("2026-11-06", zh)
        self.assertIn("−6", zh)
        self.assertIn("owner 裁決 2026-11-06：AI 查證取代人審", zh)
        self.assertNotIn("CL-DATA-12", zh)

    def test_machine_readable_derivation_method_coverage(self):
        # Every record in the repo that ships a non-null camera geojson carries
        # a derivation_method (machine-readable provenance marker field).
        missing = []
        for oid, doc in self.docs.items():
            for cam in doc.get("camera_contexts", []):
                geo = cam.get("geometry") or {}
                if geo.get("geojson") is not None and not (geo.get("derivation_method") or ""):
                    missing.append(oid + ":" + str(cam.get("id")))
        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
