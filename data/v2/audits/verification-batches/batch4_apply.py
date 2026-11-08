# -*- coding: utf-8 -*-
"""CL-DATA-38 batch4 apply — mirror of CL-DATA-35/36/37 semantics.

For each opportunity in batch4-roster.json:
  1. camera_contexts[*].access_notes_i18n  <- verified trilingual place note
  2. camera_contexts[*].evidence_refs      <- [e-d38-access-<slug>]
  3. camera_contexts[*].geometry.derivation_method append cross-check note
  4. targets[*].evidence_refs              <- [e-d38-access-<slug>]
  5. evidence_claims[*].evidence_refs      <- [e-d38-access-<slug>]
  6. evidence_claims[*].scope_note         <- batch4 verification statement
  7. revision += 1
Writes cl-data-38_access_evidence.json + batch4-progress.json.
Unknowns stay honest: no fabricated facts, unverifiable details left to on-site notices.
NOTE: us-* PLACE_NOTES tuples were authored as (en, zh-with-（zh）marker, ja);
the swap below normalizes them to (zh, en, ja).
"""
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
import sys
sys.path.insert(0, str(REPO / "data/v2/audits/verification-batches"))
from batch4_content import D, PLACE_NOTES, PLACE_EVID, PLACE_SLUG, PLACE_SOURCES, GEOMETRY_CHECKS  # noqa: E402

BATCH_DIR = REPO / "data/v2/audits/verification-batches"
OPP_DIR = REPO / "data/v2/opportunities"
AUDITS = REPO / "data/v2/audits"

roster = json.loads((BATCH_DIR / "batch4-roster.json").read_text(encoding="utf-8"))
places = sorted({v["place"] for v in roster.values()})

evidence = {"ticket": "CL-DATA-38", "verified_on": D, "places": [], "evidence": []}
progress = {
    "ticket": "CL-DATA-38",
    "batch": 4,
    "verified_on": D,
    "source": "data/v2/audits/verification-batches/batch4_content.py + registry below",
    "items": {},
}

def trilingual(pid):
    raw = PLACE_NOTES[pid]
    zh, en, ja = raw
    if en.startswith("（zh）"):          # us-* rows authored as (en, zh, ja)
        zh, en = en, zh
    if zh.startswith("（zh）"):
        zh = zh[4:]
    return {"zh-TW": zh, "en": en, "ja": ja}

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
        "supports": f"CL-DATA-38 batch4 access verification {D}: transport/parking/hours/closure/permit facts for place {pid} ({' | '.join(urls)})",
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
         "no conflicting authoritative coordinate found in this pass; provisional/derived geometry retained as-is (documented, batch4-progress.json)"))
    dm_add = f"CL-DATA-38 {D}: geometry {geo_status} — {geo_note}"
    if f"CL-DATA-38 {D}" in (c0dm := opp["camera_contexts"][0]["geometry"].get("derivation_method") or ""):
        continue  # already applied this pass — idempotent rerun, no double revision bump
    for c in opp["camera_contexts"]:
        c["access_notes_i18n"] = notes
        c["evidence_refs"] = [eid]
        dm = c["geometry"].get("derivation_method") or ""
        if f"CL-DATA-38 {D}" not in dm:
            c["geometry"]["derivation_method"] = (dm + " " if dm else "") + dm_add
    for t in opp["targets"]:
        if not t.get("evidence_refs"):
            t["evidence_refs"] = [eid]
    claims = opp.get("evidence_claims") or []
    for cl in claims:
        cl["evidence_refs"] = [eid]
        cl["scope_note"] = (
            f"CL-DATA-38 batch4 access verification {D}: transport/parking/hours/closures/permits "
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

(AUDITS / "cl-data-38_access_evidence.json").write_bytes(
    json.dumps(evidence, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")
(BATCH_DIR / "batch4-progress.json").write_bytes(
    json.dumps(progress, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")
print(f"changed {changed} opportunities across {len(places)} places")
