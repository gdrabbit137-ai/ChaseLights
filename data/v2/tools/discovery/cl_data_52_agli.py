#!/usr/bin/env python3
"""CL-DATA-52 stage 6: AGLI v2 dual-board (L/P) direct scoring for jp-065..jp-091.

Method: data/v2/audits/agli/agli-method.md v2 — AGLI-L (0.28G+0.28U+0.22V+0.12R+0.10S),
AGLI-P (0.60*成品高度 + 0.40*畫面美感, 成品高度=0.45G+0.35U+0.20R), independent
diversity/certainty mechanical columns, anchor discipline (L>75 must name a global
same-type comparandum; 90+ never given outside legendary-tier; zero 90+ inflation).
Records appended to agli-final.json (dual-board source of truth) with global rank
recomputation, and v2 records appended to agli-jp-full.json (per-place dims +
reasons; gli field carries AGLI-L with a pointer note to the dual-board file).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TICKET = "CL-DATA-52"

# v1-style dims G/U/V/R/P/S/E/C per place (0-100 anchor scores, PM judgment on
# dossier + web evidence; E/C low-confidence estimates excluded from v2 totals)
DIMS = {
    "jp-065": (92, 95, 80, 40, 78, 55, 60, 30, "comparandum: Matterhorn/Kilimanjaro summit class (legendary-tier allowed below 85 global line)"),
    "jp-066": (45, 70, 78, 55, 72, 70, 78, 40, None),
    "jp-067": (65, 60, 76, 60, 70, 65, 65, 40, None),
    "jp-068": (70, 72, 72, 55, 74, 75, 55, 45, None),
    "jp-069": (45, 55, 75, 55, 62, 70, 70, 35, None),
    "jp-070": (40, 55, 72, 65, 62, 72, 72, 45, None),
    "jp-071": (30, 75, 80, 40, 70, 85, 60, 30, None),
    "jp-072": (45, 80, 76, 55, 70, 75, 65, 85, "UNESCO World Heritage"),
    "jp-073": (60, 68, 72, 45, 68, 75, 62, 30, None),
    "jp-074": (35, 85, 75, 45, 72, 70, 60, 80, "日本百名城"),
    "jp-075": (40, 50, 65, 45, 60, 65, 55, 30, None),
    "jp-076": (68, 62, 74, 55, 70, 60, 68, 35, None),
    "jp-077": (25, 78, 76, 40, 70, 70, 65, 60, None),
    "jp-078": (30, 72, 78, 40, 68, 80, 60, 35, None),
    "jp-079": (35, 68, 80, 55, 68, 70, 70, 40, None),
    "jp-080": (48, 60, 78, 45, 72, 72, 70, 35, None),
    "jp-081": (25, 80, 70, 40, 66, 70, 62, 35, None),
    "jp-082": (25, 70, 74, 40, 64, 60, 60, 35, None),
    "jp-083": (45, 72, 70, 40, 66, 65, 68, 35, None),
    "jp-084": (35, 82, 74, 35, 68, 68, 55, 45, None),
    "jp-085": (25, 70, 66, 35, 62, 65, 72, 55, None),
    "jp-086": (58, 65, 74, 60, 68, 65, 62, 35, None),
    "jp-087": (25, 72, 82, 55, 70, 88, 72, 30, None),
    "jp-088": (40, 65, 76, 45, 68, 65, 75, 35, None),
    "jp-089": (30, 55, 68, 40, 62, 60, 65, 30, None),
    "jp-090": (35, 85, 74, 45, 70, 75, 50, 30, None),
    "jp-091": (45, 75, 74, 55, 66, 65, 60, 60, "UNESCO World Natural Heritage (Yakushima)"),
}
L1 = {"jp-065": "JP3", "jp-066": "JP3", "jp-080": "JP3", "jp-088": "JP3",
      "jp-069": "JP1", "jp-070": "JP2", "jp-071": "JP2", "jp-079": "JP2",
      "jp-075": "JP3", "jp-083": "JP3", "jp-087": "JP3",
      "jp-073": "JP4", "jp-089": "JP4", "jp-067": "JP5", "jp-068": "JP5", "jp-072": "JP5",
      "jp-077": "JP6", "jp-074": "JP7", "jp-084": "JP7", "jp-078": "JP8", "jp-082": "JP8",
      "jp-076": "JP9", "jp-081": "JP9", "jp-085": "JP9", "jp-086": "JP9", "jp-090": "JP9", "jp-091": "JP9"}

REASONS = {
 "jp-065": {"grandeur": "日本最高峰山體對比落差3,700m級，火山圓錐體態全球罕見", "uniqueness": "世界唯一以單一山體為國家認同的活火山聖峰，形態記憶點無可替代", "visual": "雪面山體簡潔對稱，光面變化（影富士/鑽石富士）在巔值成立", "richness": "題材集中於山體本身，季節與光線變化多但皆同主體", "photo": "登頂級機位相對受限（御來光與影富士短窗），但成品高度極高"},
 "jp-066": {"grandeur": "山腹展望，山體非本點自身，尺度靠富士借景", "uniqueness": "五重塔+富士同框為全球級代表構圖，型態記憶點極強", "visual": "塔·山·花三層構圖乾淨，四季皆有色彩", "richness": "春櫻/秋楓/冬雪多面但構圖同型", "photo": "定番成熟機位，正面單一構圖，機位成熟度滿分型"},
 "jp-067": {"grandeur": "燒岳與穗高連峰環景，谷地尺度中上", "uniqueness": "噴火形成枯立木+倒影為日本少見型態", "visual": "晨霧+枯木剪影+山岳倒影乾淨耐看", "richness": "河童橋/梓川/岳澤多點同谷可延伸", "photo": "步道機位完善，晨霧窗穩定"},
 "jp-068": {"grandeur": "2,400m級山域高地與立山連峰，雪山巨壁", "uniqueness": "高地池塘倒影+雪之大谷雪壁為日本唯一型態", "visual": "連峰倒影乾淨，雪壁藍白硬朗", "richness": "倒影/雪壁/殘雪火山地形多題材", "photo": "室堂設施完善，雪壁期構圖線形強"},
 "jp-069": {"grandeur": "丘陵尺度小，靠樹與田拼布取勝", "uniqueness": "拼布農地+孤樹群日本獨有", "visual": "幾何田塊與孤樹線形乾淨", "richness": "四季田色多變（麥浪/雪景）", "photo": "定番機位多，構圖彈性大"},
 "jp-070": {"grandeur": "溪谷尺度中上，瀑布群連續展開", "uniqueness": "十四公里步道急流型態少見", "visual": "苔溪+急流+光影乾淨", "richness": "瀑/溪/林多層次", "photo": "步道機位完善但視角受限步道"},
 "jp-071": {"grandeur": "沼澤尺度小", "uniqueness": "朝燒三條件成立的短窗倒影為東北代表性記憶點", "visual": "紅葉+朝燒+鏡面巔值極高，但成立窗口極短", "richness": "主體單一", "photo": "時刻/風況依賴極重，機位單一"},
 "jp-072": {"grandeur": "溪谷村落尺度中", "uniqueness": "合掌造聚落全球獨有（UNESCO）", "visual": "雪景+點燈暖色對比經典", "richness": "四季+夜間題材多", "photo": "荻町城展望定番機位成熟"},
 "jp-073": {"grandeur": "山頂俯瞰盆地尺度中上", "uniqueness": "纜車直達雲海層的營運點型態少見", "visual": "雲海金色面乾淨", "richness": "主題集中雲海", "photo": "機位完善、纜車依賴"},
 "jp-074": {"grandeur": "山城規模小，靠浮城氣氛", "uniqueness": "浮空山城記憶點極強（雲海+石垣）", "visual": "藍調石垣+雲海乾淨", "richness": "四季城景+雲海窗", "photo": "展望機位單一但成熟"},
 "jp-075": {"grandeur": "盆地霧海尺度中", "uniqueness": "關東近郊大規模霧海窗口少見", "visual": "群山霧海乾淨", "richness": "主題集中", "photo": "公園展望機位受限較多"},
 "jp-076": {"grandeur": "外輪山俯瞰巨大破火山口，尺度大", "uniqueness": "五岳環景為世界少見破火山口型態", "visual": "草原+山稜線乾淨", "richness": "火山/草原/雲海題材多", "photo": "展望臺機位完善"},
 "jp-077": {"grandeur": "湖面鳥居尺度小", "uniqueness": "湖中鳥居+對面夕日複合少見", "visual": "剪影+湖面暖色乾淨", "richness": "主題集中", "photo": "岸邊機位單一但成熟"},
 "jp-078": {"grandeur": "海灘尺度小", "uniqueness": "日本版天空之鏡記憶點強但型態依賴潮汐", "visual": "鏡面+夕陽巔值高", "richness": "主體單一", "photo": "潮汐/風況依賴重，機位寬闊"},
 "jp-079": {"grandeur": "沼群尺度小", "uniqueness": "鈷藍–翡翠變色湖水全球少見", "visual": "水色乾淨耐看", "richness": "湖沼線多點可延伸", "photo": "步道機位完善，主體單一但色彩變化多"},
 "jp-080": {"grandeur": "借景富士尺度大", "uniqueness": "湖面鑽石富士為複合事件型記憶點", "visual": "山+鏡面+光柱巔值高", "richness": "四季湖景+事件窗口", "photo": "岸邊機位單一，光窗依賴重"},
 "jp-081": {"grandeur": "瀑布落差12m小", "uniqueness": "裏見水簾洞型態日本代表", "visual": "水簾+逆光+苔綠乾淨", "richness": "主題集中", "photo": "瀑後機位獨特但空間窄"},
 "jp-082": {"grandeur": "溪流尺度中", "uniqueness": "仁淀藍水色為日本第一水質專屬記憶點", "visual": "藍水乾淨", "richness": "淵/灘多樣但分散", "photo": "機位分散、點位待精確化"},
 "jp-083": {"grandeur": "30m落差斷面尺度中上", "uniqueness": "『如海割裂』分流瀑型態罕見", "visual": "岩石斷面+白瀑對比乾淨", "richness": "主題集中", "photo": "觀瀑臺機位成熟"},
 "jp-084": {"grandeur": "離岸岩礁尺度小", "uniqueness": "夕陽『點燈蠟燭』複合事件型態全球少見", "visual": "剪影+夕照巔值高", "richness": "主題集中", "photo": "船班依賴重，岸上替代機位遠"},
 "jp-085": {"grandeur": "灘面尺度小", "uniqueness": "隆起波狀岩帶型態少見", "visual": "幾何波紋線形乾淨", "richness": "神社+島景延伸有限", "photo": "岸線機位寬闊，逆光條件依賴"},
 "jp-086": {"grandeur": "208島入海尺度大", "uniqueness": "rias海岸群島拓撲日本代表性", "visual": "島群線形乾淨", "richness": "多展望臺+遊船多題材", "photo": "展望機位成熟，構圖彈性大"},
 "jp-087": {"grandeur": "丘陵尺度小", "uniqueness": "藍色花海+海平線複合型態少見", "visual": "藍色+海天乾淨巔值高", "richness": "花種輪替全年多題材", "photo": "丘上機位成熟"},
 "jp-088": {"grandeur": "茶田尺度中，借景富士", "uniqueness": "無電線茶園越し富士稀有", "visual": "畝線導引+雪冠對比乾淨", "richness": "四季茶田+富士多面", "photo": "定番成熟機位"},
 "jp-089": {"grandeur": "村域尺度小", "uniqueness": "日本第一星空認定記憶點強", "visual": "銀河+山脊剪影乾淨", "richness": "主題集中", "photo": "人工平台機位，光害控制佳"},
 "jp-090": {"grandeur": "礁岸尺度小", "uniqueness": "日本唯一南十字星全貌視點", "visual": "星軌+夜海剪影乾淨", "richness": "主題集中", "photo": "岸邊開闊，星空窗依賴"},
 "jp-091": {"grandeur": "溪谷尺度中", "uniqueness": "苔蘚巨岩溪谷（もののけの森）全球少見", "visual": "苔綠+溪流霧氣乾淨", "richness": "溪/林/巨岩多層次", "photo": "步道機位多但光線幽暗"},
}

cert_recs = {}
for i in range(65, 92):
    pid = f"jp-{i:03d}"
    p = ROOT / "data/v2/opportunities" / f"{pid}-P01.json"
    certs = []
    for suffix in ("-P01", "-P02"):
        f = ROOT / "data/v2/opportunities" / f"{pid}{suffix}.json"
        if not f.exists():
            continue
        c = json.loads(f.read_text(encoding="utf-8"))
        n_weather = 0
        pen = 0
        for cond in c["condition_contract"]["conditions"]:
            if cond.get("role") != "REQUIRED":
                continue
            dom = cond.get("domain")
            if dom == "SEASON_TIME":
                pen += 12
            elif dom == "ASTRONOMY":
                pen += 8
            elif dom == "OCEAN_STATE":
                pen += 10
            elif dom == "WEATHER":
                n_weather += 1
                if n_weather > 1:
                    pen += 7
        certs.append(max(10, min(90, 85 - pen)))
    cert_recs[pid] = min(certs)

final_path = ROOT / "data/v2/audits/agli/agli-final.json"
final = json.loads(final_path.read_text(encoding="utf-8"))
have = {p["place_id"] for p in final["places"]}
new_recs = []
for pid, dims in DIMS.items():
    G, U, V, R, P, S, E, C, compar = dims
    if pid in have:
        continue
    agg_l = round(0.28 * G + 0.28 * U + 0.22 * V + 0.12 * R + 0.10 * S, 1)
    p_height = 0.45 * G + 0.35 * U + 0.20 * R
    agg_p = round(0.60 * p_height + 0.40 * V, 1)
    # diversity mechanical: n_opp / genres from the build data
    n_opp = 2 if pid in ("jp-068", "jp-087") else 1
    n_genre = n_opp
    diversity = min(95, 30 + 15 * (n_opp - 1) + 10 * (n_genre - 1))
    cert = cert_recs[pid]
    base = {
        "place_id": pid, "name_zh": None, "region": "jp", "l1": L1[pid],
        "agli_l": agg_l, "agli_p": agg_p,
        "components": {
            "L_weights": {"grandeur": 0.28, "uniqueness": 0.28, "visual": 0.22,
                          "richness": 0.12, "season": 0.10},
            "p_height": round(p_height, 1), "p_aesthetics": V,
            "height_formula": "0.45*grandeur+0.35*uniqueness+0.20*richness"},
        "diversity": diversity,
        "certainty": cert, "certainty_inputs": {
            "n_opp": n_opp, "penalty_basis": "agli-method.md v2 §3 mechanical",
            "note": "seasonal windows -12, extra numeric weather -7, light windows -8, subject/ocean-state -10"},
        "confidence": "medium",
        "old_agli_v1": None,
        "recheck_flag": False, "recheck_flags": [],
        "derivation_basis": "成品高度=0.45G+0.35U+0.20R（光窗移出）；畫面美感=visual；CL-DATA-52 建置直評（證據於 cl-data-52_web_evidence.json）",
        "provenance": {"source_files": ["agli-jp-full.json", "data/v2/audits/cl-data-52_web_evidence.json"],
                       "method": "CL-DATA-52 v2 direct dual-board scoring per agli-method.md v2",
                       "tickets": [TICKET]},
    }
    if compar:
        base["anchor_comparandum"] = compar
    new_recs.append(base)

import sys
sys.path.insert(0, str(ROOT))
import regions
names = {}
for s in regions.get_spots("jp"):
    names[s["spot_id"]] = s["name_i18n"]["zh-TW"]
for r in new_recs:
    r["name_zh"] = names[r["place_id"]]

final["places"].extend(new_recs)
final["places"].sort(key=lambda p: p["place_id"])
by_l = sorted(final["places"], key=lambda p: -p["agli_l"])
by_p = sorted(final["places"], key=lambda p: -p["agli_p"])
for i, r in enumerate(by_l):
    r["rank_l"] = i + 1
for i, r in enumerate(by_p):
    r["rank_p"] = i + 1
final["summary"]["n"] = len(final["places"])
final["summary"]["tickets"] = sorted(set(final["summary"].get("tickets", []) + [TICKET])) if isinstance(final["summary"].get("tickets"), list) else final["summary"].get("tickets")
zero90 = sum(1 for p in final["places"] if p["agli_l"] >= 90 or p["agli_p"] >= 90)
final["summary"][f"cl_data_52_additions"] = {
    "n": len(new_recs),
    "top_l": sorted(new_recs, key=lambda r: -r["agli_l"])[:3],
    "zero_90_plus": zero90 == 0,
}
final_path.write_text(json.dumps(final, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
top = sorted(new_recs, key=lambda r: -r["agli_l"])[:5]
print(json.dumps({"new": len(new_recs), "total": len(final["places"]),
                  "top3_l": [(r['place_id'], r['name_zh'], r['agli_l']) for r in top[:3]],
                  "top3_p": [(r['place_id'], r['name_zh'], r['agli_p']) for r in sorted(new_recs, key=lambda r: -r['agli_p'])[:3]],
                  "global_top_l": by_l[0]['place_id']}, ensure_ascii=False))

# agli-jp-full.json v2-direct records (same convention as d51 '51-direct')
jp_path = ROOT / "data/v2/audits/agli/agli-jp-full.json"
jp = json.loads(jp_path.read_text(encoding="utf-8"))
have_jp = {r["place_id"] for r in jp["records"]}
added = 0
for r in new_recs:
    pid = r["place_id"]
    if pid in have_jp:
        continue
    G, U, V, R2, P2, S, E, C, _c = DIMS[pid]
    jp["records"].append({
        "place_id": pid, "name_zh": r["name_zh"], "l1": L1[pid],
        "pass_A": None, "pass_B": None,
        "merged": {"grandeur": G, "uniqueness": U, "visual": V, "richness": R2,
                   "photo": P2, "season": S, "experience": E, "cultural": C},
        "confidence": "medium",
        "gli_version": "52-direct-v2",
        "source": "cl-data-52-direct",
        "evidence_note": "CL-DATA-52 建置直評：v2 雙榜 L/P 分見 agli-final.json；本檔 merged 為 v1 型 8 維拆解（體驗/人文為低信心估計，不入 v2 總分）",
        "reasons": REASONS[pid],
        "agli": r["agli_l"],
    })
    added += 1
jp["summary"]["n"] = len(jp["records"])
# l1_region_rankings recompute for JP1..JP9
l1r = {}
for rec in jp["records"]:
    key = rec["l1"]
    cur = l1r.setdefault(key, {"n": 0, "top": rec["place_id"], "top_name": rec["name_zh"], "top_agli": rec["agli"]})
    cur["n"] += 1
    if rec["agli"] > cur["top_agli"]:
        cur.update({"top": rec["place_id"], "top_name": rec["name_zh"], "top_agli": rec["agli"]})
jp["l1_region_rankings"] = l1r
jp_path.write_text(json.dumps(jp, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print("jp-full records:", len(jp["records"]), "added", added)
