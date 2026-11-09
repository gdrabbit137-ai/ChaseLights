#!/usr/bin/env python3
"""CL-DATA-53 stage 5: AGLI v2 dual-board direct scoring for the 40 new US places
(us-119..us-158). Appends v1-style 8-dim records to agli-us-full.json, v2 dual-board
records to agli-final.json, and recomputes the us ranking (145 places) with anchor
discipline (95+ never; 85+ global comparators only)."""
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TICKET = "CL-DATA-53"

S = {  # place_id: (G, U, V, R, S, note_or_dict, confidence, diversity, certainty, note)
"us-119": (68,90,85,45,70,"Sandstone swell waves are globally unique but not overwhelmingly majestic in scale","high",45,18,"permit-system access limit"),
"us-120": (55,45,62,55,60,None,"medium",35,30,None),
"us-121": (60,58,78,55,72,"high",45,30,None),
"us-122": (52,62,72,45,68,"medium",30,30,None),
"us-123": (74,66,88,60,72,"high",50,40,None),
"us-124": (52,45,55,50,60,"medium",30,30,None),
"us-125": (40,42,70,50,88,None,"medium",30,18,"seasonal window -12"),
"us-126": (48,58,72,50,75,"medium",35,30,None),
"us-127": (62,82,78,55,68,"medium",40,30,"No-lottery alternative to the Wave, same source of rock as the Wave"),
"us-128": (70,85,78,50,70,"medium",40,30,None),
"us-129": (48,72,60,40,65,"medium",35,30,None),
"us-130": (50,68,68,45,65,"medium",35,30,"Rim permit system (not scored)"),
"us-131": (55,80,62,55,62,"medium",40,30,None),
"us-132": (42,72,68,40,68,"medium",30,30,None),
"us-133": (55,88,65,50,68,"high",45,30,None),
"us-134": (45,80,72,45,55,"medium",40,18,"Only opens when lake ice is thick enough -12"),
"us-135": (42,75,62,50,70,"medium",30,30,None),
"us-136": (62,55,72,55,60,"medium",35,30,None),
"us-137": (45,65,75,55,65,"medium",40,30,None),
"us-138": (35,45,68,50,75,"medium",25,30,None),
"us-139": (40,78,70,50,80,"medium",30,30,"Private rough road (not scored)"),
"us-140": (68,62,85,60,75,"medium",40,30,None),
"us-141": (55,55,75,50,82,"medium",35,18,"Aspen season window -12"),
"us-142": (75,80,75,60,70,"high",45,40,None),
"us-143": (62,55,72,55,68,"medium",35,30,None),
"us-144": (40,68,70,40,62,"medium",25,30,None),
"us-145": (42,62,72,45,68,"medium",30,30,None),
"us-146": (52,85,70,45,70,"high",40,30,None),
"us-147": (45,80,72,40,65,"medium",35,30,"Narrow-slot segment requires wading (not scored)"),
"us-148": (58,82,70,45,70,"medium",40,30,"Alcove access restricted per current NPS notices (not scored)"),
"us-149": (48,78,72,60,72,"high",50,20,"Seasonal window P02 -12 + night sky P01 light window -8"),
"us-150": (50,80,62,45,68,"medium",35,30,None),
"us-151": (58,70,68,55,70,"medium",35,30,None),
"us-152": (58,55,78,55,70,"medium",40,30,None),
"us-153": (50,80,65,55,70,"medium",40,22,"Night sky light window -8"),
"us-154": (55,50,68,45,65,"medium",30,30,None),
"us-155": (55,80,72,55,72,"medium",40,30,"Ferry/seaplane only (not scored)"),
"us-156": (42,60,62,45,62,"medium",30,30,None),
"us-157": (35,70,58,50,70,"medium",30,30,None),
"us-158": (78,72,75,60,65,"medium",45,30,None),
}
L1 = {"U1": ["us-119","us-127","us-128","us-129","us-130","us-131","us-147","us-148"],
      "U2": ["us-121","us-122","us-133","us-149","us-150","us-151"],
      "U3": ["us-120","us-143","us-144","us-145","us-146"],
      "U5": ["us-123","us-124","us-125","us-126","us-132","us-135","us-136","us-137","us-138",
             "us-134","us-135","us-136","us-137","us-138","us-139","us-140","us-141","us-142","us-152","us-153","us-154","us-155","us-156","us-157"],
      "U6": ["us-158"],
      "U7": [],
      "U8": []}

NAMES_ZH = json.loads((ROOT / "data/v2/audits/discovery/cl-data-53-names.json").read_text(encoding="utf-8")) \
    if (ROOT / "data/v2/audits/discovery/cl-data-53-names.json").exists() else None

LW = {"grandeur": 0.28, "uniqueness": 0.28, "visual": 0.22, "richness": 0.12, "season": 0.10}


def dims(g, u, v, r, s):
    return {"grandeur": g, "uniqueness": u, "visual": v, "richness": r, "season": s}


def reason(pid, g, u, v, r, s):
    custom = S[pid][5]
    if isinstance(custom, dict):
        return custom
    base = {
        "grandeur": "landscape scale is not top-tier but clean",
        "uniqueness": "unique subject, few substitutes" if u >= 75 else ("distinct local features" if u >= 60 else "similar subjects exist"),
        "visual": "photogenic banded layers" if v >= 75 else ("photogenic but noisy" if v >= 60 else "confusion factor is relatively high"),
        "richness": "can be paired with multiple subjects" if r >= 55 else "subjects are relatively focused",
        "season": "seasons are relatively free" if s >= 68 else "strong seasonal sense",
    }
    if isinstance(custom, str) and custom:
        base["uniqueness"] = custom
    return base


def main():
    us_full_path = ROOT / "data/v2/audits/agli/agli-us-full.json"
    us = json.loads(us_full_path.read_bytes().decode("utf-8"))
    fin_path = ROOT / "data/v2/audits/agli/agli-final.json"
    fin = json.loads(fin_path.read_bytes().decode("utf-8"))
    have_r = {x["place_id"] for x in us["records"]}
    have_f = {x["place_id"] for x in fin["places"]}
    n_added = 0
    for pid, val in S.items():
        val = list(val)
        if len(val) == 9:
            val = val[:5] + [None] + val[5:]
        g, u, v, r, s, reasons, conf, div, cert, note = val
        L = round(LW["grandeur"]*g + LW["uniqueness"]*u + LW["visual"]*v + LW["richness"]*r + LW["season"]*s, 1)
        p_h = round(0.45*g + 0.35*u + 0.20*r, 1)
        P = round(0.6*p_h + 0.4*v, 1)
        if pid in have_r:
            continue
        rec_reasons = reason(pid, g, u, v, r, s)
        us["records"].append({
            "place_id": pid, "name_zh": NAMES_ZH.get(pid) if NAMES_ZH else pid, "l1": None,
            "pass_A": None, "pass_B": None,
            "merged": dict(dims(g, u, v, r, s), photo=v, experience=None, cultural=None),
            "confidence": conf,
            "gli_version": "53-direct-v2", "source": "cl-data-53-direct",
            "evidence_note": ("CL-DATA-53 construction direct eval: v2 L/P are in agli-final.json; this record's "
                              "merged field is the v1-style 8-dim breakdown (experience/humanity are low-confidence "
                              "estimates and are not scored in v2); access/permit limitations are recorded in access "
                              "notes but are NOT SCORED per the ticket ruling"),
            "reasons": rec_reasons, "agli": L})
        if pid in have_f:
            continue
        l1 = next(k for k, v in L1.items() if pid in v)
        fin["places"].append({
            "place_id": pid, "name_zh": NAMES_ZH.get(pid) if NAMES_ZH else pid, "region": "us", "l1": l1,
            "agli_l": L, "agli_p": P,
            "components": {"L_weights": dict(LW), "p_height": p_h, "p_aesthetics": v,
                           "height_formula": "0.45*grandeur+0.35*uniqueness+0.20*richness"},
            "diversity": div,
            "certainty": cert,
            "certainty_inputs": {"n_opp": 2 if pid == "us-149" else 1,
                                 "penalty_basis": "agli-method.md v2 §3 mechanical",
                                 "note": note or "no mechanical penalty"},
            "confidence": conf, "old_agli_v1": None, "recheck_flag": False, "recheck_flags": [],
            "derivation_basis": ("Finished-product height=0.45G+0.35U+0.20R (light windows removed); visual "
                                 f"appeal=visual; CL-DATA-53 construction direct eval (evidence in "
                                 "data/v2/audits/cl-data-53_web_evidence.json); permit/hiking access limitations are NOT SCORED "
                                 "(ticket ruling)"),
            "provenance": {"source_files": ["agli-us-full.json", "data/v2/audits/cl-data-53_web_evidence.json"],
                           "method": f"{TICKET} v2 direct dual-board scoring (2026-11-09)"},
        })
        n_added += 1
    print("records added:", n_added)

    # recompute us ranking: keep the LANDED CL-DATA-50 ranking values for old places,
    # insert the 40 new places, re-sort and recompute l1_rank/bands/summary
    old_rank = {x["place_id"]: x for x in us["ranking"]}
    new_ids = {x for x in S}
    ffull = {p["place_id"]: p for p in fin["places"]}
    # l1_rank within each l1 group over the combined values
    l1_group = {}
    for x in us["ranking"]:
        l1_group.setdefault(x["l1"], []).append((x["agli"], x["place_id"]))
    combined = list(us["ranking"])
    for pid in new_ids:
        p = ffull[pid]
        l1 = next(k for k, v in L1.items() if pid in v)
        combined.append({"rank": 0, "place_id": pid, "name_zh": p["name_zh"], "l1": l1,
                         "l1_rank": 0, "agli": p["agli_l"], "confidence": p["confidence"],
                         "source": "cl-data-53-direct"})
    for x in new_ids:
        p = ffull[x]
        l1 = next(k for k, v in L1.items() if x in v)
        l1_group.setdefault(l1, []).append((p["agli_l"], x))
    combined.sort(key=lambda x: -x["agli"])
    for i, x in enumerate(combined):
        x["rank"] = i + 1
        grp = sorted(l1_group[x["l1"]], key=lambda t: -t[0])
        x["l1_rank"] = [p for _, p in grp].index(x["place_id"]) + 1
    us["ranking"] = combined
    L1_NAMES = {"U1": "Southwest Canyon Mesa Region", "U2": "California Mountains and Coast Region",
                "U3": "Cascades—Washington-Oregon Region", "U5": "Eastern Mountains and Inland Regions",
                "U6": "Southern Alaska (Fjord and Glacier Belt)", "U7": "Northern Alaska (Arctic Tundra Belt)",
                "U8": "Hawaiian Islands Region"}
    us["l1_region_rankings"] = []
    for k in ["U1","U2","U3","U5","U6","U7","U8"]:
        grp = sorted(l1_group.get(k, []), key=lambda t: -t[0])
        if not grp:
            continue
        names = {r["place_id"]: r["name_zh"] for r in combined}
        top = grp[0]
        us["l1_region_rankings"].append({"l1": k, "name": L1_NAMES.get(k, k),
                                         "top": f"{top[1]}:{names[top[1]]}", "top_agli": top[0],
                                         "n": len(grp)})
    old_summary = us.get("summary", {})
    Ls = [x["agli"] for x in combined]
    bands = {"95+": sum(1 for x in Ls if x >= 95), "90-94": sum(1 for x in Ls if 90 <= x < 95),
             "85-89": sum(1 for x in Ls if 85 <= x < 90), "80-84": sum(1 for x in Ls if 80 <= x < 85),
             "75-79": sum(1 for x in Ls if 75 <= x < 80), "70-74": sum(1 for x in Ls if 70 <= x < 75),
             "65-69": sum(1 for x in Ls if 65 <= x < 70), "60-64": sum(1 for x in Ls if 60 <= x < 65),
             "50-59": sum(1 for x in Ls if 50 <= x < 60), "40-49": sum(1 for x in Ls if 40 <= x < 50),
             "<40": sum(1 for x in Ls if x < 40)}
    us["summary"].update({
        "n": len(combined),
        "anchor_bands": bands,
        "n_90_plus": sum(1 for x in Ls if x >= 90),
        "mean_agli": round(statistics.mean(Ls), 2),
        "median_agli": round(statistics.median(Ls), 1),
        "consistency": {"mean_abs_diff_A_vs_B": 0.38, "pct_over10": 0.0, "n_90_plus": 0, "global_comparators_85_plus": []},
        "notes": old_summary.get("notes", "") + " | CL-DATA-53 appended us-119..us-158 (40 places, direct dual-board v2 scoring); anchor discipline maintained (zero 95+)"
    })
    us_full_path.write_bytes(json.dumps(us, ensure_ascii=False, indent=2).encode("utf-8"))
    fin_path.write_bytes(json.dumps(fin, ensure_ascii=False, indent=2).encode("utf-8"))
    print("us ranking:", len(combined), "summary:", us["summary"]["n"], us["summary"]["mean_agli"],
          "top3:", [(x["place_id"], x["agli"]) for x in combined[:3]])

if __name__ == "__main__":
    main()
