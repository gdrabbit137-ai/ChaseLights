#!/usr/bin/env python3
"""CL-DATA-64 stage 2: curation names/classifications for the 13 new places
+ AGLI v2 dual-board direct scoring (appends to regional full boards and
agli-final.json, recomputes regional rankings with anchor discipline)."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    'cl64a', str(ROOT / 'data/v2/tools/discovery/cl_data_64_build.py'))
m64 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m64)
TICKET = "CL-DATA-64"
VER = m64.VER_DATE
PLACES = m64.PLACES
wb = m64.wb
def wcur(p, obj):
    (ROOT / p).write_bytes((json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
jdump = json.dumps

L1 = {"tw-121": "F3", "tw-122": "F3", "tw-123": "F3", "tw-124": "F3",
      "us-159": "U1", "us-160": "U1",
      "jp-092": "JP9", "jp-093": "JP9", "jp-094": "JP4", "jp-095": "JP4",
      "us-161": "U8", "us-162": "U8", "us-163": "U8"}
REGION = {p["place_id"]: p["region"] for p in PLACES}

# place_id: (G, U, V, R, S, custom_uniqueness_or_dict, confidence, diversity, certainty, note)
S = {
"tw-121": (45, 75, 78, 55, 55, "CNN 世界15大自然奇景題材，馬祖代表性沙灘追淚點", "medium", 35, 18, "seasonal window -12; noctiluca density unverifiable -8"),
"tw-122": (50, 82, 80, 50, 50, "坑道內靜水搖櫓近距離追淚的官方夜間遊程，全台唯一", "medium", 40, 18, "seasonal window -12; reservation access -4; noctiluca density unverifiable -8"),
"tw-123": (42, 68, 70, 45, 55, "東莒白沙灘追淚點，無光害海岸", "medium", 30, 22, "seasonal window -12; noctiluca density unverifiable -8"),
"tw-124": (42, 66, 66, 45, 55, "礁岩海岸浪打螢光，與沙灘/坑道型態不同", "medium", 30, 22, "seasonal window -12; noctiluca density unverifiable -8"),
"us-159": (68, 80, 82, 55, 75, "全球最著名準時間歇泉，噴發可預期", "high", 45, 35, None),
"us-160": (50, 72, 75, 45, 75, None, "medium", 35, 35, None),
"jp-092": (52, 70, 75, 50, 75, None, "medium", 35, 35, None),
"jp-093": (45, 68, 70, 45, 75, None, "medium", 30, 35, None),
"jp-094": (48, 75, 72, 55, 78, "日本湧出量第一的溫泉象徵，國家特別名勝", "medium", 40, 35, None),
"jp-095": (45, 78, 70, 50, 45, "世界唯一雪猴泡湯景觀", "medium", 40, 18, "snow season dependency -12; wild-animal presence uncertain -8"),
"us-161": (75, 85, 85, 55, 60, "全球最活躍火山之一的熔岩湖紅光，噴發期噴泉柱高達數百呎", "high", 50, 22, "volcanic_activity gating -10; eruption episodic pause -6"),
"us-162": (42, 62, 62, 45, 85, None, "medium", 30, 35, None),
"us-163": (58, 70, 70, 50, 85, None, "medium", 35, 35, None),
}

LW = {"grandeur": 0.28, "uniqueness": 0.28, "visual": 0.22, "richness": 0.12, "season": 0.10}
L1_NAMES = {
    "F3": "馬祖列島", "U1": "Southwest Canyon Mesa Region", "U8": "Hawaiian Islands Region",
    "JP4": "中部・北陸東海（信越・北陸・東海丘陵）", "JP9": "九州（阿蘇・霧島・櫻島火火山帶＋北九州都市帶）",
}


def dims(g, u, v, r, s):
    return {"grandeur": g, "uniqueness": u, "visual": v, "richness": r, "season": s}


def main():
    # ---------- curation ----------
    cur_path = ROOT / "data/v2/indexes/research/curation.json"
    cur = json.loads(cur_path.read_bytes().decode("utf-8"))
    topic_for = {"blue_tears": "topic:coastal-landscape",
                 "mountain_view": "topic:mountain-landscape", "overlook": "topic:mountain-landscape",
                 "sunrise": "topic:sunrise", "sunset": "topic:sunset", "reflection": "topic:reflection"}
    added_names = added_cls = 0
    for p in PLACES:
        pid = p["place_id"]
        if pid not in cur["names"]:
            src = {"tw": "tw_weather.json", "jp": "jp_weather.json", "us": "us_weather.json"}[p["region"]]
            cur["names"][pid] = {
                lang: {"direct_source": True, "source_path": src,
                       "spot_id": pid, "pointer": f"/name_i18n/{lang}"}
                for lang in ("zh-TW", "en", "ja")}
            added_names += 1
        for subj in p["subjects"]:
            oid = f"{pid}-{subj['suffix']}"
            if oid in cur["classifications"]:
                continue
            legacy_theme = m64.cl.LEGACY_MAP[subj["template"]][0]
            cur["classifications"][oid] = {
                "topic_ids": ([topic_for[subj["template"]]] if subj["template"] in topic_for else []),
                "canonical_pointers": ["/targets/0/name_i18n", "/description_i18n"],
                "evidence_claim_id": f"{oid}-claim-01",
                "evidence_refs": [f"e-d64-web-{p['slug']}"],
                "classification_basis": f"legacy_theme={legacy_theme} ({TICKET} admission)"}
            added_cls += 1
    wcur("data/v2/indexes/research/curation.json", cur)
    print("curation names +%d, classifications +%d (totals %d/%d)" % (
        added_names, added_cls, len(cur["names"]), len(cur["classifications"])))

    # ---------- AGLI ----------
    full_files = {"tw": "agli-tw-full.json", "jp": "agli-jp-full.json", "us": "agli-us-full.json"}
    fin_path = ROOT / "data/v2/audits/agli/agli-final.json"
    fin = json.loads(fin_path.read_bytes().decode("utf-8"))
    have_f = {x["place_id"] for x in fin["places"]}
    fulls = {r: json.loads((ROOT / "data/v2/audits/agli" / f).read_bytes().decode("utf-8"))
             for r, f in full_files.items()}
    n_added = 0
    for p in PLACES:
        pid = p["place_id"]
        g, u, v, r, s_, custom, conf, div, cert, note = S[pid]
        L = round(LW["grandeur"]*g + LW["uniqueness"]*u + LW["visual"]*v + LW["richness"]*r + LW["season"]*s_, 1)
        p_h = round(0.45*g + 0.35*u + 0.20*r, 1)
        P = round(0.6*p_h + 0.4*v, 1)
        reg = p["region"]
        fu = fulls[reg]
        have_r = {x["place_id"] for x in fu["records"]}
        reasons = {
            "grandeur": "landscape scale is not top-tier but clean",
            "uniqueness": custom or ("unique subject, few substitutes" if u >= 75 else "similar subjects exist"),
            "visual": "photogenic luminous/banded subject" if v >= 75 else "photogenic but noisy",
            "richness": "can be paired with multiple subjects" if r >= 55 else "subjects are relatively focused",
            "season": "seasons are relatively free" if s_ >= 68 else "strong seasonal sense",
        }
        if pid not in have_r:
            fu["records"].append({
                "place_id": pid, "name_zh": p["names"]["zh-TW"], "l1": None,
                "pass_A": None, "pass_B": None,
                "merged": dict(dims(g, u, v, r, s_), photo=v, experience=None, cultural=None),
                "confidence": conf, "gli_version": "64-direct-v2", "source": f"cl-data-64-direct",
                "evidence_note": (f"{TICKET} construction direct eval: v2 L/P are in agli-final.json; this record's "
                                  "merged field is the v1-style 8-dim breakdown (experience/humanity are low-confidence "
                                  "estimates and are not scored in v2); access/reservation/eruption-closure limitations "
                                  "are recorded in access notes but are NOT SCORED per the ticket ruling"),
                "reasons": reasons, "agli": L})
            n_added += 1
        if pid not in have_f:
            fin["places"].append({
                "place_id": pid, "name_zh": p["names"]["zh-TW"], "region": reg, "l1": L1[pid],
                "agli_l": L, "agli_p": P,
                "components": {"L_weights": dict(LW), "p_height": p_h, "p_aesthetics": v,
                               "height_formula": "0.45*grandeur+0.35*uniqueness+0.20*richness"},
                "diversity": div, "certainty": cert,
                "certainty_inputs": {"n_opp": 1, "penalty_basis": "agli-method.md v2 §3 mechanical",
                                     "note": note or "no mechanical penalty"},
                "confidence": conf, "old_agli_v1": None, "recheck_flag": False, "recheck_flags": [],
                "derivation_basis": (f"成品高度=0.45G+0.35U+0.20R（光窗移出）；畫面美感=visual；{TICKET} 建置直評（證據於 "
                                     f"cl-data-64_web_evidence.json）；預約/欄架/噴發管制等 access 限制記錄於 access notes，NOT SCORED（ticket ruling）"),
                "provenance": {"source_files": [full_files[reg], "data/v2/audits/cl-data-64_web_evidence.json"],
                               "method": f"{TICKET} v2 direct dual-board scoring ({VER})"},
            })
    # recompute each region's ranking
    RAW_INDENT = {}
    for reg, fname in full_files.items():
        raw = (ROOT / "data/v2/audits/agli" / fname).read_bytes().decode("utf-8")
        RAW_INDENT[reg] = 2 if raw.startswith('{\n  "') else 1
    def dump2(obj, reg):
        return json.dumps(obj, ensure_ascii=False, indent=RAW_INDENT[reg]) + "\n"
    for reg, fu in fulls.items():
        new_ids = [p["place_id"] for p in PLACES if p["region"] == reg]
        fplace = {x["place_id"]: x for x in fin["places"]}
        if fu["ranking"] and isinstance(fu["ranking"][0], str):
            # jp-full keeps a string place-id ranking sorted by agli desc - append new ids
            appended = sorted(new_ids, key=lambda pid: -fplace[pid]["agli_l"])
            fu["ranking"] = fu["ranking"] + appended
            import statistics
            Ls = [fplace[x]["agli_l"] for x in fu["ranking"]]
            old = fu.get("summary", {})
            fu["summary"].update({
                "n": len(fu["ranking"]),
                "mean_agli": round(statistics.mean(Ls), 2),
                "median_agli": round(statistics.median(Ls), 1),
                "n_90_plus": sum(1 for x in Ls if x >= 90),
                "notes": (old.get("notes", "") or "") + f" | {TICKET} appended {','.join(new_ids)} ({len(new_ids)} places, direct dual-board v2 scoring); anchor discipline maintained (zero 95+)",
            })
            (ROOT / "data/v2/audits/agli" / full_files[reg]).write_bytes(
                dump2(fu, reg).encode("utf-8"))
            print(f"{reg} ranking (string-list):", len(fu["ranking"]), "mean", fu["summary"]["mean_agli"])
            continue
        l1_group = {}
        for x in fu["ranking"]:
            if not isinstance(x, dict) or "place_id" not in x:
                continue
            l1_group.setdefault(x["l1"], []).append((x["agli"], x["place_id"]))
        have_rank = {x["place_id"] for x in fu["ranking"] if isinstance(x, dict)}
        combined = [x for x in fu["ranking"] if isinstance(x, dict)]
        for pid in new_ids:
            if pid in have_rank:
                continue
            rec = next(x for x in fu["records"] if x["place_id"] == pid)
            l1 = L1[pid]
            combined.append({"rank": 0, "place_id": pid, "name_zh": fplace[pid]["name_zh"], "l1": l1,
                             "l1_rank": 0, "agli": fplace[pid]["agli_l"], "confidence": fplace[pid]["confidence"],
                             "source": "cl-data-64-direct"})
            l1_group.setdefault(l1, []).append((fplace[pid]["agli_l"], pid))
        combined.sort(key=lambda x: -x["agli"])
        for i, x in enumerate(combined):
            x["rank"] = i + 1
            grp = sorted(l1_group[x["l1"]], key=lambda t: -t[0])
            x["l1_rank"] = [p for _, p in grp].index(x["place_id"]) + 1
        fu["ranking"] = combined
        names = {r2["place_id"]: r2["name_zh"] for r2 in combined}
        if isinstance(fu.get("l1_region_rankings"), dict):
            # tw-full keeps a dict l1 -> [ {rank, place_id, agli} ] - update affected groups only
            l1rr = fu["l1_region_rankings"]
            for k in {L1[pid] for pid in new_ids}:
                grp = sorted(l1_group.get(k, []), key=lambda t: -t[0])
                l1rr[k] = [{"rank": i + 1, "place_id": pid, "agli": a}
                           for i, (a, pid) in enumerate(grp)]
        else:
            l1rr = []
            for k in sorted(l1_group):
                grp = sorted(l1_group[k], key=lambda t: -t[0])
                top = grp[0]
                l1rr.append({"l1": k, "name": L1_NAMES.get(k, k), "top": f"{top[1]}:{names[top[1]]}",
                             "top_agli": top[0], "n": len(grp)})
            fu["l1_region_rankings"] = l1rr
        import statistics
        Ls = [x["agli"] for x in combined]
        old = fu.get("summary", {})
        fu["summary"].update({
            "n": len(combined),
            "mean_agli": round(statistics.mean(Ls), 2),
            "median_agli": round(statistics.median(Ls), 1),
            "n_90_plus": sum(1 for x in Ls if x >= 90),
            "notes": (old.get("notes", "") or "") + f" | {TICKET} appended {','.join(new_ids)} ({len(new_ids)} places, direct dual-board v2 scoring); anchor discipline maintained (zero 95+)",
        })
        (ROOT / "data/v2/audits/agli" / full_files[reg]).write_bytes(
            dump2(fu, reg).encode("utf-8"))
        print(f"{reg} ranking:", len(combined), "mean", fu["summary"]["mean_agli"])
    fin["summary"] = fin.get("summary", {})
    fin["generated"] = VER
    fin_path.write_bytes(dump2(fin, "us").encode("utf-8"))
    print("AGLI records added:", n_added, "final places:", len(fin["places"]))


if __name__ == "__main__":
    main()
