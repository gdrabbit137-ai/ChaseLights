#!/usr/bin/env python3
"""CL-DATA-30 topup: targeted extra queries for places whose first-pass vision
found zero representative photos. Appends new candidates (dedup) to existing
photo lists in progress JSON."""
import json, sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scenic_v3_fetch as F

QUERIES = {
    "jp-002": ["Asahidake", "旭岳 大雪山"],
    "jp-011": ["東京タワー", "Tokyo Tower night"],
    "tw-009": ["望幽谷", "Wangyou Valley Keelung"],
    "tw-023": ["頂石棹", "Shizhuo Alishan"],
    "tw-052": ["小崗山", "Xiaogangshan Kaohsiung"],
    "tw-065": ["南竿", "Nangan Matsu"],
    "tw-071": ["小琉球", "Lamay Island"],
    "tw-080": ["帆船鼻", "Lanyu Cape Fanchun"],
    "tw-085": ["南子吝步道", "Nanzi-comment Trail"],
    "tw-091": ["司馬庫斯", "Smangus"],
    "us-045": ["Seward Alaska"],
    "us-048": ["Portage Glacier Alaska"],
    "us-063": ["Talkeetna Alaska"],
    "us-072": ["Golden Gardens Park"],
    "us-073": ["Alki Beach"],
    "us-083": ["Sunrise Mount Rainier", "Mount Rainier Sunrise visitor"],
    "us-088": ["Hoh Rain Forest"],
    "us-089": ["Palouse Falls"],
}

OUT = "D:/Dick/Project/ChaseLights-CL-DATA-30/data/v2/audits/discovery/scenic-v3-full-progress.json"
p = json.loads(open(OUT, encoding="utf-8").read())
have = {t.lower() for e in p["stage_photos"].values() for t in [ph.get("title", "").lower() for ph in e.get("photos", [])]}
for pid, qs in QUERIES.items():
    e = p["stage_photos"].get(pid)
    if not e:
        continue
    cands = []
    for q in qs:
        cands += F.commons_search(q, 6)
        time.sleep(0.5)
    cands = F.dedupe_filter(cands)
    good = [c for c in cands if not c.get("filtered_out") and c["title"].lower() not in have]
    for c in good:
        c.setdefault("source", "commons-search-topup")
    e["photos"] = (e.get("photos") or []) + good[:6]
    e["sources_tried"] = sorted(set((e.get("sources_tried") or []) + ["commons-search-topup"]))
    print(pid, e["name"], "+", len(good), [c["title"][:44] for c in good[:3]])
tmp = OUT.replace(".json", ".json.tmp")
open(tmp, "w", encoding="utf-8").write(json.dumps(p, ensure_ascii=False, indent=1))
os.replace(tmp, OUT)
