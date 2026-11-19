"""CL-DATA-76 stage B: retire us-111 Brooks Falls per owner ruling 2026-11-20.

Product status = retired (current retirement convention, CL-DATA-62 recipe):
- V2 contract doc: lifecycle_status -> "retired" (stays pinned on disk; the id
  is reserved — never delete the regions.py tuple or the contract file);
- legacy canonical runtime catalog: spot entry removed + manifest recount with
  retired_spot_ids reservation;
- published evaluation bundle spliced: the place leaves the product with an
  honest PRODUCT_RETIRED skip row, its detail shard is deleted;
- catalog-scoring weakness row disposition -> 已裁撤 with the ruling text.

Ruling text (owner 2026-11-20): 低天氣光影依賴（弱點清單 score 2）＋題材無適配
模板→裁撤入候選池（owner 裁決 2026-11-20）.

All writes are LF bytes; round-trip serialization verified before writing.
"""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SID = "us-111"
RULING = ("低天氣光影依賴（弱點清單 score 2）＋題材無適配模板→裁撤入候選池"
          "（owner 裁決 2026-11-20）")
RULING_EN = ("Low weather/light dependency (weakness-list score 2) + no fitting "
             "genre template -> retired into the candidate pool "
             "(owner ruling 2026-11-20).")
RULING_JA = ("気象・光依存が低く（弱点リスト score 2）、適合する題材テンプレートが"
             "ないため候補プールへ裁撤（オーナー裁定 2026-11-20）。")


def enc(value, indent=2):
    raw = (json.dumps(value, ensure_ascii=False, indent=indent) + "\n").encode("utf-8")
    return raw


def enc_preserve_crlf(value, indent=2):
    raw = enc(value, indent)
    return raw.replace(b"\n", b"\r\n") if raw.endswith(b"\n") else raw


def enc_compact(value, indent=None):
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def enc_indent1(value, indent=1):
    return (json.dumps(value, ensure_ascii=False, indent=indent) + "\n").encode("utf-8")


def check_roundtrip(path, encoder=enc, indent=2, crlf=False):
    raw = Path(path).read_bytes()
    doc = json.loads(raw.decode("utf-8"))
    out = encoder(doc, indent)
    if crlf:
        out = out.replace(b"\n", b"\r\n")
    if out != raw:
        raise SystemExit(f"serialization convention mismatch: {path}")
    return doc


def write(path, doc, encoder=enc, indent=2, crlf=False):
    raw = encoder(doc, indent)
    if crlf:
        raw = raw.replace(b"\n", b"\r\n")
    assert b"\r" not in raw or crlf
    Path(path).write_bytes(raw)
    print("wrote", Path(path).name, len(raw))


# --- V2 contract doc: lifecycle_status -> retired ---------------------------
path = ROOT / "data/v2/opportunities/us-111-P01.json"
doc = check_roundtrip(path, crlf=True, indent=1)
if doc.get("lifecycle_status") != "retired":
    assert doc.get("lifecycle_status") == "draft", doc.get("lifecycle_status")
    doc["lifecycle_status"] = "retired"
    doc["revision"] = doc["revision"] + 1
    write(path, doc, crlf=True, indent=1)
else:
    print("us-111-P01 already retired")
# keep the ruling on the doc itself without inventing schema-unknown keys:
# the retirement semantics live in lifecycle_status; the ruling text is
# recorded in the audit report + the weakness-list disposition (see below).

# --- legacy canonical runtime catalog + manifest ----------------------------
cat_path = ROOT / "runtime_catalog_v004_r4_2.json"
catalog = check_roundtrip(cat_path, enc_indent1, indent=1)
removed = [s for s in catalog["spots"] if s["spot_id"] == SID]
if removed:
    assert len(removed) == 1, removed
    op_removed = len(removed[0].get("opportunities", []))
    catalog["spots"] = [s for s in catalog["spots"] if s["spot_id"] != SID]
else:
    print("runtime catalog already pruned of", SID)
    assert not any(s["spot_id"] == SID for s in catalog["spots"])
op_removed = 0
counts = {
    "spots": len(catalog["spots"]),
    "opportunities": sum(len(s.get("opportunities", [])) for s in catalog["spots"]),
    "condition_variants": sum(
        len(o.get("condition_variants", [])) for s in catalog["spots"] for o in s.get("opportunities", [])),
    "profile_viewpoint_relations": sum(
        len(o.get("viewpoints", [])) for s in catalog["spots"] for o in s.get("opportunities", [])),
}
catalog["counts"] = counts
write(cat_path, catalog, enc_indent1, indent=1)

mf_path = ROOT / "runtime_catalog_manifest_r4_2.json"


def update_manifest(pol=None, ms_count=None):
    mf = check_roundtrip(mf_path, enc_indent1, indent=1)
    for rkey, region in mf["regions"].items():
        rspots = [s for s in catalog["spots"] if s["spot_id"].startswith(f"{rkey}-")]
        region["counts"] = {
            "spots": len(rspots),
            "opportunities": sum(len(s.get("opportunities", [])) for s in rspots),
            "condition_variants": sum(
                len(o.get("condition_variants", [])) for s in rspots for o in s.get("opportunities", [])),
            "profile_viewpoint_relations": sum(
                len(o.get("viewpoints", [])) for s in rspots for o in s.get("opportunities", [])),
        }
        retired = region.get("retired_spot_ids", [])
        if SID.startswith(f"{rkey}-") and SID not in retired:
            retired.append(SID)
        region["retired_spot_ids"] = sorted(retired)
    mf["totals"] = counts
    if pol is not None:
        mf["runtime_policy_counts"] = pol
    if ms_count is not None:
        mf["minimum_sufficient_visibility_profile_count"] = ms_count
    write(mf_path, mf, enc_indent1, indent=1)


import sys
sys.path.insert(0, str(ROOT))
import opportunity_runtime as ort_module  # noqa: E402

ms_count = len(ort_module.MINIMUM_SUFFICIENT_VISIBILITY_PROFILES)
errors = ort_module.validate_event_calendar()
assert not errors, errors
# Pass 1: totals first — opportunities.py validates manifest totals at import.
update_manifest()
import opportunities as opps  # noqa: E402
all_ops = [o for s in catalog["spots"] for o in s.get("opportunities", [])]
pol = dict(Counter(opps.runtime_policy(o) for o in all_ops))
# Pass 2: recomputed runtime policy counts.
update_manifest(pol=pol, ms_count=ms_count)
print("manifest tw:", json.dumps({k: v for k, v in pol.items()}), ms_count)

# --- published evaluation bundle splice -------------------------------------
latest = ROOT / "apps/web-v2/evaluations-latest.json"
doc = check_roundtrip(latest, encoder=enc_compact, crlf=True)
before_p, before_o = doc["place_count"], doc["opportunity_count"]
removed_places = [p for p in doc["places"] if p.get("place_id") == SID]
assert len(removed_places) == 1
op_removed_bundle = sum(len(p.get("opportunities", [])) for p in removed_places)
doc["places"] = [p for p in doc["places"] if p.get("place_id") != SID]
doc["place_count"] = len(doc["places"])
doc["opportunity_count"] = before_o - op_removed_bundle
skipped_ids = {s.get("place_id") for s in doc.get("skipped", [])}
if SID not in skipped_ids:
    doc["skipped"].append({"place_id": SID, "reason": "PRODUCT_RETIRED"})
write(latest, doc, enc_compact, crlf=True)
print(f"bundle spliced: places {before_p}->{doc['place_count']} "
      f"opportunities {before_o}->{doc['opportunity_count']} (op_removed={op_removed_bundle})")

shard = ROOT / "apps/web-v2/evaluations-details" / f"{SID}.json"
if shard.exists():
    shard.unlink()
    print("deleted shard", shard.name)

# --- weakness-list disposition ----------------------------------------------
score_path = ROOT / "data/v2/audits/discovery/catalog-scoring.json"
score = check_roundtrip(score_path, encoder=enc_indent1, indent=1, crlf=True)
changed = 0
for row in score["weakness_lists"].get("low_weather_light", []):
    if row.get("opportunity_id") == f"{SID}-P01":
        row["recommendation"] = f"已裁撤：{RULING}"
        row["recommendation_en"] = RULING_EN
        row["recommendation_ja"] = RULING_JA
        changed += 1
assert changed == 1, changed
write(score_path, score, enc_indent1, indent=1, crlf=True)
print("STAGE_B_OK")
