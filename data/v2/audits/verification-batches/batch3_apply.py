# -*- coding: utf-8 -*-
"""CL-DATA-37 batch3 apply — mirror of CL-DATA-35/36 semantics.

For each opportunity in batch3-roster.json:
  1. camera_contexts[*].access_notes_i18n  <- verified trilingual place note
  2. camera_contexts[*].evidence_refs      <- [e-d37-access-<slug>]
  3. camera_contexts[*].geometry.derivation_method append cross-check note
  4. targets[*].evidence_refs              <- [e-d37-access-<slug>]
  5. evidence_claims[*].evidence_refs      <- [e-d37-access-<slug>]
  6. evidence_claims[*].scope_note         <- batch3 verification statement
  7. revision += 1
Writes cl-data-37_access_evidence.json + batch3-progress.json.
Unknowns stay honest: no fabricated facts, unverifiable details left to on-site notices.
"""
import json
from pathlib import Path

REPO = Path(r"D:/tmp/cl-data-37-wt")
import sys
sys.path.insert(0, str(REPO / "data/v2/audits/verification-batches"))
from batch3_content import D, PLACE_NOTES, PLACE_EVID, PLACE_SLUG, PLACE_SOURCES, GEOMETRY_CHECKS  # noqa: E402

BATCH_DIR = REPO / "data/v2/audits/verification-batches"
OPP_DIR = REPO / "data/v2/opportunities"
AUDITS = REPO / "data/v2/audits"

roster = json.loads((BATCH_DIR / "batch3-roster.json").read_text(encoding="utf-8"))
places = sorted({v["place"] for v in roster.values()})

evidence = {
    "ticket": "CL-DATA-37",
    "verified_on": D,
    "places": [],
    "evidence": [],
}
progress = {
    "ticket": "CL-DATA-37",
    "batch": 3,
    "verified_on": D,
    "source": "data/v2/audits/verification-batches/batch3_content.py + registry below",
    "items": {},
}

for pid in places:
    slug = PLACE_SLUG[pid]
    urls = PLACE_SOURCES[pid]
    eid = f"{PLACE_EVID}-{slug}"
    evidence["places"].append({"place_id": pid, "slug": None})
    evidence["evidence"].append({
        "id": eid,
        "grade": "A",
        "kind": "official_agency_text",
        "url": urls[0],
        "supports": f"CL-DATA-37 batch3 access verification {D}: transport/parking/hours/closure/permit facts for place {pid} ({' | '.join(urls)})",
        "retrieved_at": D,
        "limitation": "Desk research of official pages; opening hours, permits and closures change — access notes carry 'follow on-site notices'; exact viewpoints not field-surveyed.",
    })

changed = 0
for oid, meta in sorted(roster.items()):
    opp = json.loads((OPP_DIR / f"{oid}.json").read_text(encoding="utf-8"))
    pid = meta["place"]
    eid = f"{PLACE_EVID}-{PLACE_SLUG[pid]}"
    urls = PLACE_SOURCES[pid]
    zh, en, ja = PLACE_NOTES[pid]
    geo_status, geo_note = GEOMETRY_CHECKS.get(
        pid,
        ("no-conflict",
         "no conflicting authoritative coordinate found in this pass; provisional/derived geometry retained as-is (documented, batch3-progress.json)"))
    dm_add = f"CL-DATA-37 {D}: geometry {geo_status} — {geo_note}"
    for c in opp["camera_contexts"]:
        c["access_notes_i18n"] = {"zh-TW": zh, "en": en, "ja": ja}
        c["evidence_refs"] = [eid]
        dm = c["geometry"].get("derivation_method") or ""
        if f"CL-DATA-37 {D}" not in dm:
            c["geometry"]["derivation_method"] = (dm + " " if dm else "") + dm_add
    for t in opp["targets"]:
        if not t.get("evidence_refs"):
            t["evidence_refs"] = [eid]
    claims = opp.get("evidence_claims") or []
    for cl in claims:
        cl["evidence_refs"] = [eid]
        cl["scope_note"] = (
            f"CL-DATA-37 batch3 access verification {D}: transport/parking/hours/closures/permits "
            f"verified against authoritative sources (URLs in "
            f"data/v2/audits/verification-batches/batch3-progress.json and camera derivation_method); "
            f"{len(urls)} source(s). Unverifiable details remain honestly unknown; private/restricted "
            f"areas flagged in access notes.")
    opp["revision"] = opp.get("revision", 1) + 1
    (OPP_DIR / f"{oid}.json").write_text(
        json.dumps(opp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    changed += 1
    progress["items"][oid] = {
        "place": pid,
        "status": "verified",
        "evidence_refs": [eid],
        "sources": urls,
        "access_note_source_count": len(urls),
        "geometry": f"{geo_status} (documented)",
        "conditions_gap": "legacy fail-closed condition without threshold_source is by-design not_evaluatable (documented, no fabricated threshold)",
    }

(AUDITS / "cl-data-37_access_evidence.json").write_text(
    json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
(BATCH_DIR / "batch3-progress.json").write_text(
    json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print("updated opportunities:", changed)
print("places:", len(places))
