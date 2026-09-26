#!/usr/bin/env python3
"""Audit production Opportunities for evidence-sensitive subject claims.

This is deliberately conservative: it creates a research queue, not a verdict.
A high-risk semantic trigger without machine-verifiable provenance is
`review_required`; it does NOT mean the Opportunity is false.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from regions import get_spots
from opportunities import get_opportunities

HIGH_RISK = {
    "mist": (r"霧|煙嵐|fog|mist|haze",),
    "cloud_sea": (r"雲海|sea of clouds|cloud sea",),
    "sunbeam": (r"雲隙光|耶穌光|光束|sunbeam|crepuscular|cloud.?gap",),
    "reflection": (r"倒影|鏡面|reflection|mirror",),
    "astro": (r"銀河|星空|milky way|starfield|night sky",),
    "seasonal_flora": (r"花海|花季|楓紅|紅葉|櫻花|金針花|梅花|芒草|紫藤|繡球|桐花|花田",),
    "waterfall": (r"瀑布|waterfall",),
    "wildlife": (r"螢火蟲|水鳥|候鳥|野生動物|賞鳥|firefl|wildlife|bird",),
    "event": (r"光影節|燈會|illumination|festival|祭典|花火|煙火|fireworks",),
    "snow_ice": (r"雪景|積雪|冰瀑|霧冰|樹冰|snow|icefall|rime",),
}

EVIDENCE_KEYS = {
    "evidence_sources",
    "evidence_source",
    "subject_evidence_status",
    "subject_evidence_grade",
    "evidence_grade",
    "research_evidence",
    "source_urls",
    "source_url",
    "verification_evidence",
}

EVIDENCE_MARKERS = (
    "subject_evidence",
    "photography_evidence",
    "verified_subject",
    "place_specific_subject",
    "official_morning_mist_photography_evidence",
    "official_sunbeam_subject_evidence",
)


def _subject_blob(op):
    """Text that asserts what the photographic subject actually is.

    Do not inspect penalties/required conditions here: e.g. "fog is bad" must
    not turn a normal landscape Opportunity into a mist Opportunity.
    """
    bits = [
        str(op.get("name_zh") or ""),
        str(op.get("name_en") or ""),
        str(op.get("legacy_theme") or ""),
    ]
    for variant in op.get("condition_variants", []) or []:
        bits.append(str(variant.get("variant_name") or ""))
        geometry = variant.get("condition_geometry")
        if isinstance(geometry, str):
            bits.append(geometry)
        elif geometry:
            bits.append(json.dumps(geometry, ensure_ascii=False))
    return " ".join(bits)

def _risk_classes(blob):
    out = []
    for cls, patterns in HIGH_RISK.items():
        if any(re.search(p, blob, re.I) for p in patterns):
            out.append(cls)
    return out


def _explicit_evidence(op):
    for key in EVIDENCE_KEYS:
        value = op.get(key)
        if value not in (None, "", [], {}):
            return True, f"opportunity.{key}"
    for vp in op.get("viewpoints", []) or []:
        status = str(vp.get("verification_status", "")).lower()
        note = str(vp.get("note", "")).lower()
        geom = str(vp.get("geometry_note", "")).lower()
        joined = " ".join((status, note, geom))
        if any(marker in joined for marker in EVIDENCE_MARKERS):
            return True, "viewpoint metadata"
    return False, None


def build_report():
    records = []
    counts = {"documented": 0, "review_required": 0, "lower_risk_legacy": 0}
    for region in ("tw", "jp", "us"):
        for spot in get_spots(region):
            sid = spot["spot_id"]
            for op in get_opportunities(region, sid):
                blob = _subject_blob(op)
                risks = _risk_classes(blob)
                has_evidence, evidence_location = _explicit_evidence(op)
                if risks and has_evidence:
                    status = "documented"
                elif risks:
                    status = "review_required"
                else:
                    status = "lower_risk_legacy"
                counts[status] += 1
                records.append(
                    {
                        "region": region,
                        "spot_id": sid,
                        "place": spot.get("name_i18n", {}).get("zh-TW") or spot.get("name"),
                        "opportunity_id": op.get("opportunity_id"),
                        "name_zh": op.get("name_zh"),
                        "risk_classes": risks,
                        "audit_status": status,
                        "machine_verifiable_evidence": has_evidence,
                        "evidence_location": evidence_location,
                        "formula_status": op.get("formula_status"),
                    }
                )
    return {
        "schema_version": "research-evidence-audit-1",
        "policy": "RESEARCH_EVIDENCE_SPEC_R4_2.md",
        "counts": counts,
        "review_required": [r for r in records if r["audit_status"] == "review_required"],
        "documented_high_risk": [r for r in records if r["audit_status"] == "documented"],
        "all_records": records,
    }


def main():
    report = build_report()
    out = Path("research_evidence_audit.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"], ensure_ascii=False))
    print(f"review_required={len(report['review_required'])}")
    for row in report["review_required"]:
        print(
            "REVIEW",
            row["region"],
            row["spot_id"],
            row["opportunity_id"],
            row["place"],
            row["name_zh"],
            ",".join(row["risk_classes"]),
        )


if __name__ == "__main__":
    main()
