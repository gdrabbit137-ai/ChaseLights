#!/usr/bin/env python3
"""CL-DATA-52 stage 3: source-lock repin/append + curation entries for jp-065..jp-091."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if (ROOT / 'data/v2/opportunities').exists():
    WROOT = ROOT
else:
    WROOT = Path(__file__).resolve().parents[4]

def blob(raw):
    return hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()

head = subprocess.check_output(["git", "-C", str(WROOT), "rev-parse", "HEAD"]).decode().strip()

lock_path = WROOT / "data/v2/indexes/research/source-lock.json"
lock = json.loads(lock_path.read_text(encoding="utf-8"))
have_ids = {r["opportunity_id"] for r in lock["canonical_records"]}
have_paths = {s["path"] for s in lock["supporting_sources"]}

new_records, new_support = [], []
for i in range(65, 92):
    place = f"jp-{i:03d}"
    for p in sorted((WROOT / "data/v2/opportunities").glob(f"{place}-P*.json")):
        oid = p.stem
        if oid in have_ids:
            continue
        raw = subprocess.check_output(["git", "-C", str(WROOT), "show", f"{head}:{p.relative_to(WROOT).as_posix()}"])
        rec = {"opportunity_id": oid, "path": p.as_posix(),
               "blob_sha": blob(raw), "sha256": hashlib.sha256(raw).hexdigest(),
               "commit_sha": head}
        # tree-verify
        assert hashlib.sha256(p.read_bytes()).hexdigest() == rec["sha256"], f"tree mismatch {oid}"
        new_records.append(rec)
ev = "data/v2/audits/cl-data-52_web_evidence.json"
if ev not in have_paths:
    p = WROOT / ev
    raw = subprocess.check_output(["git", "-C", str(WROOT), "show", f"{head}:{ev}"])
    new_support.append({"path": ev, "commit_sha": head, "blob_sha": blob(raw),
                        "sha256": hashlib.sha256(raw).hexdigest()})
# repin changed existing canonical records (contract bytes unchanged so far, but be safe)
changed = 0
for rec in lock["canonical_records"]:
    path = WROOT / rec["path"]
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != rec["sha256"]:
        rec["sha256"] = hashlib.sha256(raw).hexdigest()
        rec["blob_sha"] = blob(raw)
        rec["commit_sha"] = head
        changed += 1
lock["canonical_records"].extend(new_records)
lock["supporting_sources"].extend(new_support)
lock_path.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({"new_canonical": len(new_records), "new_supporting": len(new_support),
                  "repinned_existing": changed, "head": head}))

# curation entries
cur_path = WROOT / "data/v2/indexes/research/curation.json"
cur = json.loads(cur_path.read_text(encoding="utf-8"))
THEME = {
    "mountain_view": "mountain_view", "cloud_sea": "cloud_sea", "reflection": "reflection",
    "overlook": "mountain_view", "sunrise": "sunrise", "sunset": "sunset",
    "night_sky": "milky_way", "city_night": "city_night", "seasonal_plant": "seasonal_foreground",
    "snow_ice": "snow_scene", "geological_landform": "geology", "waterfall": "waterfall",
}
import importlib.util
spec = importlib.util.spec_from_file_location('c52', str(WROOT / 'data/v2/tools/discovery/cl_data_52_build.py'))
c52 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c52)
n_names, n_opp = 0, 0
for p in c52.PLACES:
    pid = p["place_id"]
    if pid not in cur["names"]:
        cur["names"][pid] = {
            "zh-TW": {"direct_source": True, "source_path": "jp_weather.json", "spot_id": pid, "pointer": "/name_i18n/zh-TW"},
            "en": {"direct_source": True, "source_path": "jp_weather.json", "spot_id": pid, "pointer": "/name_i18n/en"},
            "ja": {"direct_source": True, "source_path": "jp_weather.json", "spot_id": pid, "pointer": "/name_i18n/ja"}}
        n_names += 1
    for subj in p["subjects"]:
        oid = f"{pid}-{subj['suffix']}"
        if oid not in cur["classifications"]:
            cur["classifications"][oid] = {
                "topic_ids": [],
                "canonical_pointers": ["/targets/0/name_i18n", "/description_i18n"],
                "evidence_claim_id": f"{oid}-claim-01",
                "evidence_refs": [f"e-d52-web-{p['slug']}"],
                "classification_basis": f"legacy_theme={THEME[subj['template']]}",
            }
            n_opp += 1
cur_path.write_text(json.dumps(cur, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({"names_added": n_names, "opp_added": n_opp,
                  "total_places": len(cur["names"]), "total_opps": len(cur["classifications"])}))
