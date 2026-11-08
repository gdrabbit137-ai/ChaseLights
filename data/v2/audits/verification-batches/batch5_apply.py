# -*- coding: utf-8 -*-
"""CL-DATA-39 batch5 apply — mirror of CL-DATA-35/36/37/38 semantics.

For each opportunity in batch5-roster.json:
  1. camera_contexts[*].access_notes_i18n  <- verified trilingual place note
  2. camera_contexts[*].evidence_refs      <- [e-d39-access-<slug>]
  3. camera_contexts[*].geometry.derivation_method append cross-check note
  4. targets[*].evidence_refs              <- [e-d39-access-<slug>] (only where empty)
  5. evidence_claims[*].evidence_refs      <- [e-d39-access-<slug>]
  6. evidence_claims[*].scope_note         <- batch5 verification statement
  7. revision += 1
Writes cl-data-39_access_evidence.json + batch5-progress.json.
Unknowns stay honest: no fabricated facts, unverifiable details left to on-site notices.
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
import sys
sys.path.insert(0, str(REPO / "data/v2/audits/verification-batches"))
from batch5_content import D, PLACE_NOTES, PLACE_EVID, PLACE_SLUG, PLACE_SOURCES, GEOMETRY_CHECKS  # noqa: E402

BATCH_DIR = REPO / "data/v2/audits/verification-batches"
OPP_DIR = REPO / "data/v2/opportunities"
AUDITS = REPO / "data/v2/audits"

roster = json.loads((BATCH_DIR / "batch5-roster.json").read_text(encoding="utf-8"))
roster = roster["items"]
places = sorted({v["place"] for v in roster.values()})

evidence = {"ticket": "CL-DATA-39", "verified_on": D, "places": [], "evidence": []}
progress = {
    "ticket": "CL-DATA-39",
    "batch": 5,
    "verified_on": D,
    "source": "data/v2/audits/verification-batches/batch5_content.py + registry below",
    "items": {},
}

def trilingual(pid):
    return {"zh-TW": PLACE_NOTES[pid][0], "en": PLACE_NOTES[pid][1], "ja": PLACE_NOTES[pid][2]}

for pid in places:
    slug = PLACE_SLUG[pid]
    urls = PLACE_SOURCES[pid]
    eid = f"{PLACE_EVID}-{slug}"
    evidence["places"].append({"place_id": pid, "slug": slug})
    evidence["evidence"].append({
        "id": eid,
        "grade": "A",
        "kind": "official_agency_text",
        "url": urls[0],
        "supports": f"CL-DATA-39 batch5 access verification {D}: transport/parking/hours/closure/permit facts for place {pid} ({' | '.join(urls)})",
        "retrieved_at": D,
        "limitation": "Desk research of official pages; opening hours, permits and closures change — access notes carry 'follow on-site notices'; exact viewpoints not field-surveyed.",
    })

changed = 0
for oid, meta in sorted(roster.items()):
    opp = json.loads((OPP_DIR / f"{oid}.json").read_text(encoding="utf-8"))
    pid = meta["place"]
    eid = f"{PLACE_EVID}-{PLACE_SLUG[pid]}"
    notes = trilingual(pid)
    geo_status, geo_note = GEOMETRY_CHECKS.get(
        pid,
        ("no-conflict",
         "no conflicting authoritative coordinate found in this pass; provisional/derived geometry retained as-is (documented, batch5-progress.json)"))
    dm_add = f"CL-DATA-39 {D}: geometry {geo_status} — {geo_note}"
    if f"CL-DATA-39 {D}" in (c0dm := opp["camera_contexts"][0]["geometry"].get("derivation_method") or ""):
        continue  # already applied this pass — idempotent rerun, no double revision bump
    for c in opp["camera_contexts"]:
        c["access_notes_i18n"] = notes
        c["evidence_refs"] = [eid]
        dm = c["geometry"].get("derivation_method") or ""
        if f"CL-DATA-39 {D}" not in dm:
            c["geometry"]["derivation_method"] = (dm + " " if dm else "") + dm_add
    for t in opp["targets"]:
        if not t.get("evidence_refs"):
            t["evidence_refs"] = [eid]
    claims = opp.get("evidence_claims") or []
    for cl in claims:
        cl["evidence_refs"] = [eid]
        cl["scope_note"] = (
            f"CL-DATA-39 batch5 access verification {D}: transport/parking/hours/closures/permits "
            f"verified against official sources ({' | '.join(PLACE_SOURCES[pid])}); "
            "unverifiable on-site details left to on-site notices (honest unknown)")
    opp["revision"] = int(opp.get("revision", 0)) + 1
    out = (json.dumps(opp, ensure_ascii=False, indent=2) + "\n").replace("\r\n", "\n").encode("utf-8")
    (OPP_DIR / f"{oid}.json").write_bytes(out)
    progress["items"][oid] = {
        "place": pid,
        "status": "verified",
        "evidence_refs": [eid],
        "sources": PLACE_SOURCES[pid],
        "geometry": geo_status,
    }
    changed += 1

(AUDITS / "cl-data-39_access_evidence.json").write_bytes(
    json.dumps(evidence, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")
(BATCH_DIR / "batch5-progress.json").write_bytes(
    json.dumps(progress, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")
print(f"changed {changed} opportunities across {len(places)} places")
