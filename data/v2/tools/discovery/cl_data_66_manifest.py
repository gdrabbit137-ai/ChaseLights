#!/usr/bin/env python3
"""CL-DATA-66 Wave 1 step 1: Tier A manifest from new-candidates-v2.json (612 candidates).

Tier A criteria (owner ruling 2026-11-11, scoreless intake):
- topics >= 2 (multi-topic composite), OR
- mentioned by >= 2 owner-gemini lists, OR
- strict-major regrade candidates: national parks / forest farms / geological
  wonders / extreme-point lighthouses / trail groups / high-mountain farms.
Exclusions (never Tier A, recorded with reject reason): urban parks, alley/
street-corner spots, homestays, single light poles, pure swimming beaches.
Note: scale 'major' from merge scouts is unreliable (607/612) - regraded here by
name/subject heuristics only; score fields stay empty (scoring paused).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "data/v2/audits/subject-lists/new-candidates-v2.json"
OUT = ROOT / "data/v2/audits/subject-lists/tier-a-manifest.json"

# ---- exclusion heuristics (市區公園/巷弄/民宿/單體燈桿/純戲水沙灘) ----
EXCLUDE = [
    (r"民宿", "homestay"),
    (r"街 ?\d+ ?巷|巷弄|街角", "alley/street-corner spot"),
    (r"燈桿|路燈", "single light pole"),
    (r"海水浴場", "pure swimming beach"),
    (r"(^|[^山濱])[沙灘]($|場$)|沙灘$|白沙灘", "pure swimming beach (needs coastal-geology/firefly/other composite topic to re-enter via topics>=2 check)"),
    (r"中正公園|羅東運動公園|前山公園|紅葉公園|親水公園|環保公園|主普壇|運動公園|都會|市區公園", "urban/urban-adjacent park"),
    (r"高跟鞋教堂", "street-side landmark"),
]
# pure-swim beach guard: '沙灘' alone with only beach-ish topics is excluded
BEACHISH = {"beach", "coastline"}

def excluded(c):
    name = c["name"]
    for pat, why in EXCLUDE:
        if re.search(pat, name):
            # composite non-beach topics can rescue a beach name (e.g. 北關海潮公園單面山/豆腐岩 reef geology)
            nonbeach = [t for t in c["topics"] if t not in BEACHISH]
            if why.startswith("pure swimming") and nonbeach:
                continue
            return why
    if "沙灘" in name and set(c["topics"]) <= BEACHISH:
        return "pure swimming beach"
    return None

# ---- strict-major regrade heuristics (name/subject, NOT scout 'major' labels) ----
MAJOR = [
    (r"國家公園|國家風景區", "national park / national scenic area"),
    (r"林場|森林遊樂區", "forest recreation / forestry"),
    (r"地質|奇岩|單面山|豆腐岩|海蝕|柱狀|壺穴|火口|溫泉露頭|惡地|月世界|石梯坪|野柳", "geological wonder"),
    (r"燈塔", "lighthouse (extreme-point regrade)"),
    (r"古道|步道群|登山步道|越嶺", "trail group"),
    (r"高山農場|農場|牧場|休閒農場", "high-mountain farm (elevation regrade)"),
    (r"雲海|日出|琉璃|夜景|星空|觀星|銀河", "major viewpoint subject (cloudsea/sunrise/night)"),
]

def strict_major(c):
    hits = [why for pat, why in MAJOR if re.search(pat, c["name"])]
    return hits

def main():
    d = json.loads(SRC.read_bytes().decode("utf-8"))
    cands = d["candidates"]
    rows, rejected, tier_a = [], [], 0
    for i, c in enumerate(cands):
        name = c["name"]
        topics = c["topics"] or []
        lists = c.get("source_lists") or []
        why_excl = excluded(c)
        major_hits = strict_major(c)
        reasons = []
        if len(topics) >= 2:
            reasons.append("topics>=2 multi-topic composite (%s)" % ",".join(topics[:6]))
        if len(lists) >= 2:
            reasons.append("mentioned by %d lists" % len(lists))
        if major_hits:
            reasons.append("strict-major regrade: %s" % "; ".join(major_hits[:2]))
        if why_excl:
            if reasons and not why_excl.startswith("pure swimming"):
                reasons.append("EXCLUDED: %s" % why_excl)
            rejected.append({"index": i, "name": name, "region": c.get("region"),
                             "reason": why_excl,
                             "would_have": reasons if reasons else None})
            continue
        if not reasons:
            rejected.append({"index": i, "name": name, "region": c.get("region"),
                             "reason": "not Tier A (single topic, single list, no strict-major regrade)",
                             "would_have": None})
            continue
        tier_a += 1
        rows.append({
            "index": i, "name": name, "region": c.get("region"),
            "elevation": c.get("elevation"), "topics": topics,
            "n_topics": len(topics), "source_lists": lists, "n_lists": len(lists),
            "scale_field": c.get("scale"),  # unreliable scout field, kept for reference only
            "selection_reason": " + ".join(reasons),
            "wave": None, "status": "pending",
            "lat": None, "lon": None, "elev_m": None,
            "coord_conf": None, "coord_source": None, "coord_sources": [],
        })
    # rank: multi-topic count desc, then list count desc, then name
    rows.sort(key=lambda r: (-r["n_topics"], -r["n_lists"], r["name"]))
    for n, r in enumerate(rows[:30], 1):
        r["wave"] = 1
    manifest = {
        "ticket": "CL-DATA-66", "generated_from": "data/v2/audits/subject-lists/new-candidates-v2.json",
        "total_candidates": len(cands),
        "tier_a_total": len(rows),
        "rejected_total": len(rejected),
        "rules": ("Tier A = topics>=2 OR mentioned by >=2 lists OR strict-major regrade "
                  "(national parks/forest farms/geological wonders/extreme-point lighthouses/"
                  "trail groups/high-mountain farms); excluded = urban parks/alley spots/"
                  "homestays/single light poles/pure swimming beaches. Scoreless intake: "
                  "rubric v2 gates and AGLI dual-board NOT run; score fields left empty."),
        "wave1": {"planned": 30, "order": "n_topics desc, n_lists desc", "done": 0, "rejected": 0},
        "tier_a": rows,
        "rejected": rejected,
    }
    OUT.write_bytes((json.dumps(manifest, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    print("tier A:", len(rows), "rejected:", len(rejected))
    print("top 12:")
    for r in rows[:12]:
        print(" ", r["name"], "|", r["n_topics"], "topics |", r["n_lists"], "lists |", r["region"])

if __name__ == "__main__":
    main()
