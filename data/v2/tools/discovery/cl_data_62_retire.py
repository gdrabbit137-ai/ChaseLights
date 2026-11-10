"""CL-DATA-62 stage-1 data edits (run inside the task worktree).

Retire tw-068/tw-083/tw-084/us-075/us-076/us-077 per owner ruling 2026-11-10
(CL-DATA-61 suitability audit):
- drop the 6 spots from the legacy canonical runtime catalog + manifest
  (tw-063 precedent: entries hidden, ids reserved in taxonomy_v004),
- prune retired ids from runtime policy hooks (event calendar, min-sufficient
  profile sets, runtime dependency hooks),
- splice the published evaluation bundle (remove the 6 places, honest
  PRODUCT_RETIRED skip rows) and delete their detail shards.
All writes are LF bytes; round-trip serialization is verified first.
"""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TG = {"tw-068", "tw-083", "tw-084", "us-075", "us-076", "us-077"}
MIN_SUFF_DROP = {
    "tw-084-P09", "tw-083-P02", "tw-083-P03", "tw-083-P04", "tw-083-P05",
    "tw-084-P01", "tw-084-P02", "tw-084-P03", "tw-084-P04", "tw-084-P05",
    "tw-084-P06", "tw-084-P07", "tw-084-P08",
}
EVENT_DROP = {"tw-084-P04", "tw-084-P05", "tw-084-P06"}


def enc(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def enc_indent1(value):
    return (json.dumps(value, ensure_ascii=False, indent=1) + "\n").encode("utf-8")


def enc_compact(value):
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def check_roundtrip(path, encoder=enc):
    raw = Path(path).read_bytes()
    doc = json.loads(raw.decode("utf-8"))
    if encoder(doc) != raw:
        raise SystemExit(f"serialization convention mismatch: {path}")
    return doc


def write(path, doc, encoder=enc):
    raw = encoder(doc)
    assert b"\r" not in raw
    Path(path).write_bytes(raw)
    print("wrote", Path(path).name, len(raw))


# --- prune runtime hooks BEFORE importing policy modules --------------------
ort_path = ROOT / "opportunity_runtime.py"
text = ort_path.read_text(encoding="utf-8")
out = []
for line in text.splitlines(keepends=True):
    if re.search(r'\b(?:tw-083-P\d\d|tw-084-P\d\d)\b', line) \
            and 'oid ==' not in line and 'oid !=' not in line \
            and 'opportunity_id' not in line:
        continue
    out.append(line)
text = "".join(out)
text = text.replace(
    'def validate_event_calendar():\n    errors = []\n    events = EVENT_CALENDAR.get("events", {})',
    'def validate_event_calendar():\n    errors = []\n'
    '    expected_ids = {"tw-082-P04", "tw-082-P06"}\n'
    '    events = EVENT_CALENDAR.get("events", {})')
assert 'expected_ids = {"tw-082-P04", "tw-082-P06"}' in text
leftover = [ln for ln in text.splitlines()
            if re.search(r'\b(?:tw-083-P\d\d|tw-084-P\d\d)\b', ln)
            and not ('oid ==' in ln or 'oid !=' in ln or 'opportunity_id' in ln)]
assert not leftover, leftover
ort_path.write_bytes(text.encode("utf-8"))
print("opportunity_runtime.py pruned")

rd_path = ROOT / "runtime_dependencies.py"
text = rd_path.read_text(encoding="utf-8")
needle = '"tw-064-P01", "tw-068-P01", "tw-069-P01",'
if needle in text:
    text = text.replace(needle, '"tw-064-P01", "tw-069-P01",')
    rd_path.write_bytes(text.encode("utf-8"))
    print("runtime_dependencies.py pruned")
else:
    assert '"tw-068-P01"' not in text
    print("runtime_dependencies.py already pruned")

# --- event calendar ---------------------------------------------------------
ec_path = ROOT / "runtime_event_calendar_r4_2.json"
ec = check_roundtrip(ec_path)
dropped = [k for k in list(ec["events"]) if k.split("-P")[0] in TG]
if dropped:
    assert set(dropped) == EVENT_DROP, dropped
    for k in dropped:
        del ec["events"][k]
    write(ec_path, ec)
else:
    print("event calendar already pruned")

# --- legacy canonical runtime catalog ---------------------------------------
cat_path = ROOT / "runtime_catalog_v004_r4_2.json"
catalog = check_roundtrip(cat_path, enc_indent1)
removed = [s for s in catalog["spots"] if s["spot_id"] in TG]
if removed:
    assert sorted(s["spot_id"] for s in removed) == sorted(TG)
    catalog["spots"] = [s for s in catalog["spots"] if s["spot_id"] not in TG]
counts = {
    "spots": len(catalog["spots"]),
    "opportunities": sum(len(s.get("opportunities", [])) for s in catalog["spots"]),
    "condition_variants": sum(
        len(o.get("condition_variants", [])) for s in catalog["spots"] for o in s.get("opportunities", [])),
    "profile_viewpoint_relations": sum(
        len(o.get("viewpoints", [])) for s in catalog["spots"] for o in s.get("opportunities", [])),
}
catalog["counts"] = counts
write(cat_path, catalog, enc_indent1)
print("legacy catalog counts:", counts)

# --- manifest ---------------------------------------------------------------
mf_path = ROOT / "runtime_catalog_manifest_r4_2.json"


def update_manifest(pol=None, ms_count=None):
    mf = check_roundtrip(mf_path, enc_indent1)
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
        for sid in sorted(TG):
            if sid.startswith(f"{rkey}-") and sid not in retired:
                retired.append(sid)
        region["retired_spot_ids"] = sorted(retired)
    mf["totals"] = counts
    if pol is not None:
        mf["runtime_policy_counts"] = pol
    if ms_count is not None:
        mf["minimum_sufficient_visibility_profile_count"] = ms_count
    write(mf_path, mf, enc_indent1)
    return mf


import sys
sys.path.insert(0, str(ROOT))
import opportunity_runtime as ort  # noqa: E402

ms_count = len(ort.MINIMUM_SUFFICIENT_VISIBILITY_PROFILES)
# Pass 1: totals first — opportunities.py validates manifest totals at import.
mf = update_manifest(ms_count=ms_count)
import opportunities as opps  # noqa: E402

all_ops = [o for s in catalog["spots"] for o in s.get("opportunities", [])]
pol = dict(Counter(opps.runtime_policy(o) for o in all_ops))
errors = ort.validate_event_calendar()
assert not errors, errors
# Pass 2: recomputed runtime policy counts.
mf = update_manifest(pol=pol)
print("manifest tw:", json.dumps(mf["regions"]["tw"]["counts"]),
      "us:", json.dumps(mf["regions"]["us"]["counts"]), pol, ms_count)

# --- evaluation bundle splice -----------------------------------------------
latest = ROOT / "apps/web-v2/evaluations-latest.json"
doc = check_roundtrip(latest, enc_compact)
before_p, before_o = doc["place_count"], doc["opportunity_count"]
removed_places = [p for p in doc["places"] if p.get("place_id") in TG]
assert {p["place_id"] for p in removed_places} == TG
op_removed = sum(len(p.get("opportunities", [])) for p in removed_places)
doc["places"] = [p for p in doc["places"] if p.get("place_id") not in TG]
doc["place_count"] = len(doc["places"])
doc["opportunity_count"] = before_o - op_removed
for pid in sorted(TG):
    doc["skipped"].append({"place_id": pid, "reason": "PRODUCT_RETIRED"})
write(latest, doc, enc_compact)
print(f"bundle spliced: places {before_p}->{doc['place_count']} "
      f"opportunities {before_o}->{doc['opportunity_count']} (op_removed={op_removed})")

details = ROOT / "apps/web-v2/evaluations-details"
for pid in sorted(TG):
    shard = details / f"{pid}.json"
    if shard.exists():
        shard.unlink()
        print("deleted shard", shard.name)

# archived bundles under data/v2/evaluations are historical records: untouched.
print("STAGE1_OK")
