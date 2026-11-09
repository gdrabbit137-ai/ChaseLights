#!/usr/bin/env python3
"""CL-DATA-50: AGLI dual-board (v2) derivation for all 261 places.
Reads the three landed single-board AGLI full files (8-dim merged scores),
derives AGLI-L / AGLI-P per the owner's 2026-11-09 three rulings, computes the
two independent metrics (subject diversity / shot certainty) mechanically from
the opportunity contracts, and emits agli-final.json + comparison artifacts.

Rulings implemented:
  R1  光影可拍性 (light-window shootability) is OUT of scoring.
  R2  題材多樣性 & 出片確定性 are recorded independently, NOT in any total.
  R3  AGLI-P = 成品高度 60% + 畫面美感 40%; AGLI-L = 壯麗/獨特/美感/豐富/季節.
"""
import json, glob, os, sys

ROOT = os.path.abspath(__file__).split(os.sep+"data"+os.sep)[0]
AG = os.path.join(ROOT, "data/v2/audits/agli")
OPP = os.path.join(ROOT, "data/v2/opportunities")

# --- weights -------------------------------------------------------------
W_L = dict(grandeur=0.28, uniqueness=0.28, visual=0.22, richness=0.12, season=0.10)
W_P_HEIGHT = dict(grandeur=0.45, uniqueness=0.35, richness=0.20)  # terrain/subject ceiling
AGLI_P = dict(height=0.60, aesthetics=0.40)

def composite(d, w):
    return round(sum(d[k] * v for k, v in w.items()), 1)

# --- load single-board records ------------------------------------------
records, region = [], []
for f, region_name in [("agli-tw-full.json", "tw"), ("agli-jp-full.json", "jp"), ("agli-us-full.json", "us/ak/hi")]:
    d = json.load(open(os.path.join(AG, f), encoding="utf-8"))
    for r in d["records"]:
        m = r.get("merged") or r.get("pass_A")  # us file carries flat A too
        if "merged" not in r and "pass_B" in r:
            m = {k: round((r["pass_A"][k] + r["pass_B"][k]) / 2) for k in r["pass_A"]}
        records.append({
            "place_id": r["place_id"], "name_zh": r["name_zh"], "l1": r.get("l1", ""),
            "l1_name": r.get("l1_name", ""), "region": region_name,
            "dims": m, "pass_A": r.get("pass_A"), "pass_B": r.get("pass_B"),
            "old_agli": r.get("agli"), "confidence": r.get("confidence", "unknown"),
            "n_evidence": len(r.get("photo_evidence") or []),
            "evidence_note": r.get("evidence_note"),
            "reasons": r.get("reasons", {}),
            "global_comparator": r.get("global_comparator"),
        })

# --- opportunity mechanical stats ---------------------------------------
def opp_stats():
    per = {}
    for f in glob.glob(os.path.join(OPP, "*.json")):
        try:
            c = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        pid = c.get("place_id")
        cc = c.get("condition_contract", {})
        conds = cc.get("conditions", [])
        req = [x for x in conds if x.get("role") == "REQUIRED"]
        req_num_weather = [x for x in req if x.get("domain") == "WEATHER" and x.get("threshold") is not None]
        timing = [x for x in req if any(t in str(x.get("metric")) for t in
                  ("sunset_window", "sunrise_time_window", "golden_hour", "blue_hour", "city_night_window",
                   "astronomical_darkness", "light_window", "galactic"))]
        season = [x for x in req if x.get("domain") == "SEASON_TIME"]
        state = [x for x in req if x.get("domain") in ("HYDROLOGY", "SUBJECT_STATE")]
        s = per.setdefault(pid, dict(n_opp=0, genres=set()))
        s["n_opp"] += 1
        g = cc.get("genre_template")
        if g:
            s["genres"].add(g)
        s.setdefault("pen", 0)
        s["pen"] += 7 * max(0, len(req_num_weather) - 1) + 8 * len(timing) + 12 * len(season) + 10 * len(state)
    return per

stats = opp_stats()

def diversity(s):
    if not s or s["n_opp"] == 0:
        return None
    return min(95, 30 + 15 * (s["n_opp"] - 1) + 10 * (len(s["genres"]) - 1))

def certainty(s):
    if not s or s["n_opp"] == 0:
        return None
    return round(min(90, max(10, 85 - s["pen"])), 0)

# --- derive boards -------------------------------------------------------
out, recheck = [], []
for r in records:
    d = r["dims"]
    L = composite(d, W_L)
    height = composite(d, W_P_HEIGHT)
    P = round(AGLI_P["height"] * height + AGLI_P["aesthetics"] * d["visual"], 1)
    s = stats.get(r["place_id"])
    div, cer = diversity(s), certainty(s)
    # anomaly rule: two-pass (A/B) composite divergence > 15 on either board
    flags = []
    if r["pass_A"] and r["pass_B"]:
        pa = composite(r["pass_A"], W_L); pb = composite(r["pass_B"], W_L)
        if abs(pa - pb) > 15:
            flags.append(f"AGLI-L A/B 差 {abs(pa-pb):.0f}")
        ha = composite(r["pass_A"], W_P_HEIGHT); hb = composite(r["pass_B"], W_P_HEIGHT)
        vA, vB = r["pass_A"]["visual"], r["pass_B"]["visual"]
        pA = AGLI_P["height"] * ha + AGLI_P["aesthetics"] * vA
        pB = AGLI_P["height"] * hb + AGLI_P["aesthetics"] * vB
        if abs(pA - pB) > 15:
            flags.append(f"AGLI-P A/B 差 {abs(pA-pB):.0f}")
    if flags:
        recheck.append({"place_id": r["place_id"], "name_zh": r["name_zh"], "flags": flags})
    basis = ("成品高度=0.45G+0.35U+0.20R（地形/主體上限，光影可拍性已移出）；"
             "畫面美感=visual 合併分；光窗價值移入獨立出片確定性")
    out.append({
        "place_id": r["place_id"], "name_zh": r["name_zh"], "region": r["region"], "l1": r["l1"],
        "l1_name": r["l1_name"],
        "agli_l": L, "agli_p": P,
        "components": {"L_weights": W_L, "p_height": height, "p_aesthetics": d["visual"],
                       "height_formula": "0.45*grandeur+0.35*uniqueness+0.20*richness"},
        "diversity": div, "certainty": cer,
        "certainty_inputs": ({"n_opp": s["n_opp"], "genres": sorted(s["genres"]), "penalty": s["pen"]} if s else None),
        "confidence": r["confidence"], "old_agli_v1": r["old_agli"],
        "recheck_flag": bool(flags), "recheck_flags": flags,
        "derivation_basis": basis,
        "provenance": {
            "source_files": ["agli-tw-full.json" if r["region"] == "tw" else
                             ("agli-jp-full.json" if r["region"] == "jp" else "agli-us-full.json")],
            "method": "CL-DATA-50 v2 mechanical remap of 8-dim merged scores + contract-condition mechanical metrics",
            "tickets": ["CL-DATA-44", "CL-DATA-48", "CL-DATA-49", "CL-DATA-50"],
        },
    })

_dist = {}
out.sort(key=lambda x: -x["agli_l"])
for i, o in enumerate(out, 1):
    o["rank_l"] = i
out_p = sorted(out, key=lambda x: -x["agli_p"])
by_p = {o["place_id"]: i + 1 for i, o in enumerate(out_p)}
for o in out:
    o["rank_p"] = by_p[o["place_id"]]

summary = {
    "n": len(out),
    "mean_l": round(sum(o["agli_l"] for o in out) / len(out), 1),
    "mean_p": round(sum(o["agli_p"] for o in out) / len(out), 1),
    "recheck_flagged": len(recheck),
    "diversity": {"n": sum(1 for o in out if o["diversity"] is not None),
                  "mean": round(sum(o["diversity"] for o in out if o["diversity"] is not None) /
                                max(1, sum(1 for o in out if o["diversity"] is not None)), 1),
                  "dist": {}},
    "certainty": {"mean": round(sum(o["certainty"] for o in out if o["certainty"] is not None) /
                                max(1, sum(1 for o in out if o["certainty"] is not None)), 1)},
    "top5_l": [{"place_id": o["place_id"], "name_zh": o["name_zh"], "agli_l": o["agli_l"]} for o in out[:5]],
    "top5_p": [{"place_id": o["place_id"], "name_zh": o["name_zh"], "agli_p": o["agli_p"]} for o in out_p[:5]],
}
for o in out:
    if o["diversity"] is not None:
        b = int(o["diversity"] // 10) * 10
        _dist[b] = _dist.get(b, 0) + 1
summary["diversity"]["dist"] = {str(k): v for k, v in sorted(_dist.items())}

final = {
    "schema": "agli-final/v2",
    "ticket": "CL-DATA-50",
    "generated": "2026-11-09",
    "method_doc": "data/v2/audits/agli/agli-method.md (v2)",
    "rulings": ["光影可拍性移出評分", "題材多樣性/出片確定性獨立記錄不計分", "AGLI-P=成品高度60+畫面美感40"],
    "summary": summary,
    "recheck_list": recheck,
    "places": out,
}
json.dump(final, open(os.path.join(AG, "agli-final.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(json.dumps(summary, ensure_ascii=False, indent=1)[:2500])
print("flagged:", recheck[:10])
