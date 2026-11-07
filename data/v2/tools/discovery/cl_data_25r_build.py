#!/usr/bin/env python3
"""CL-DATA-25R: admit 渭水之丘 (tw-098, v2 3.8 >= 3.8 line) into legacy+V2+runtime."""
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(r'D:/tmp/cl-data-25r')
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    'cl25', str(ROOT / 'data/v2/tools/discovery/cl_data_25_build.py'))
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)

def dump(v): return json.dumps(v, ensure_ascii=False, indent=2) + '\n'
def load(p): return json.loads((ROOT / p).read_bytes().decode('utf-8'))
def write(p, text): (ROOT / p).write_bytes(text.encode('utf-8'))

P = {
    "place_id": "tw-098", "region": "tw", "slug": "weishui-hill",
    "shortlist_id": "tw-weishui-hill", "score": 3.8,
    "names": {"zh-TW": "渭水之丘／櫻花陵園", "en": "Weishui Hill, Jiaoxi",
              "ja": "渭水の丘", "local": "渭水之丘"},
    "lat": 24.823055, "lon": 121.7025, "elev_m": 800,
    "coord_conf": "medium_high",
    "coord_source": "zh.wikipedia 櫻花陵園 (24°49′23″N 121°42′9″E = 24.8231,121.7025；渭水之丘在園區最高丘地) — CL-DATA-23 dossier approx 24.636,121.64 與實際位置偏差大，依 web 證據修正；海拔約750–800 m（zh.wikipedia：海拔約750至800公尺，取 dossier 800）",
    "coord_sources": ["https://zh.wikipedia.org/wiki/%E6%AB%BB%E8%8A%B1%E9%99%B5%E5%9C%92",
                      "https://www.ta-mag.net/ta/News.php?id=1408",
                      "https://travel.ettoday.net/article/880376.htm"],
    "admin": "宜蘭縣", "category": "本島", "tags": ["mountain", "city"],
    "subjects": [
        {"suffix": "P01", "template": "cloud_sea", "seasonal": "lanyang_mist",
         "zh": "渭水之丘晨霧琉璃光", "en": "Weishui Hill morning mist glow",
         "ja": "渭水の丘の朝霧",
         "desc_zh": "懸空平台俯瞰蘭陽平原輻射霧／低雲覆平原的琉璃光（10–3月霧季晨前）；與 tw-031 抹茶山（3.28km，登山步道山景題材）題材錯位——本點為平原霧海俯視點。",
         "desc_en": "Overlook-plane radiation fog / low cloud over the Lanyang Plain at dawn (Oct-Mar mist season); subject-disjoint from tw-031 Matcha Mountain 3.28 km away (hiking-trail mountain scenery) - this place is a plain-fog-sea overlook.",
         "desc_ja": "蘭陽平原の放射霧・低雲を丘上から一望（10〜3月の霧季、夜明け前）。3.28km先の抹茶山（tw-031、登山道の山景）とは題材が別。"},
        {"suffix": "P02", "template": "city_night", "seasonal": None,
         "zh": "渭水之丘夜景", "en": "Weishui Hill night view", "ja": "渭水の丘の夜景",
         "desc_zh": "蘭陽平原夜間燈海全景（宜蘭/羅東市街光點）＋龜山島方向海平線；與既有 tw-029 鳶山等夜景題材地理錯位。",
         "desc_en": "Night-time sea of lights across the Lanyang Plain (Yilan/Luodong) with Guishan Island on the horizon; geographically disjoint from existing night-view places.",
         "desc_ja": "蘭陽平原の夜景（宜蘭・羅東の灯りの海）と亀山島の水平線。既存夜景地とは地理的に別。"},
    ],
}

cl.TYPICAL_WINDOWS["lanyang_mist"] = {"start": "10-01", "end": "03-31"}
cl.SEASON_NAMES["lanyang_mist"] = {
    "zh-TW": "蘭陽平原輻射霧季", "en": "Lanyang Plain radiation-fog season",
    "ja": "蘭陽平原の放射霧季"}
cl.SEASONAL_SOURCES["lanyang_mist"] = (
    "https://travel.yilan.gov.tw/zh-tw/attraction/381/",
    "Lanyang plain radiation fog / morning mist strongest Oct-Mar (same county portal source as cuifeng_mist)")

# ---- 1) V2 contracts
for subj in P["subjects"]:
    c = cl.build_contract(P, subj)
    text = cl.jdump(c).replace(
        "CL-DATA-25 admission web verification 2026-11-07",
        "CL-DATA-25R admission web verification 2026-11-07").replace(
        "CL-DATA-25 discovery admission (rubric >=3.8, owner ruling 2026-11-07)",
        "CL-DATA-25R admission (rubric v2 >=3.8, owner ruling 2026-11-07)")
    out = cl.DATA / f"{c['opportunity_id']}.json"
    cl.wbytes(out, text)
    print("contract written:", c["opportunity_id"])

# ---- 2) seasonal calendar
cal_path = ROOT / "data/v2/seasonal-calendar.json"
cal = json.loads(cal_path.read_bytes().decode("utf-8"))
have = {e["plant_id"] for e in cal["entries"]}
added = [e for e in cl.build_seasonal_entries([P]) if e["plant_id"] not in have]
cal["entries"].extend(added)
cl.wbytes(cal_path, cl.jdump(cal))
print("seasonal entries added:", [e["plant_id"] for e in added])

# ---- 3) regions.py
rp = ROOT / "regions.py"
text = rp.read_bytes().decode("utf-8").replace("\r\n", "\n")
n = P["names"]
if "渭水之丘" not in text:
    anchor_admin = '    "tw-095": ["南投縣"],\n'
    assert anchor_admin in text
    text = text.replace(anchor_admin, anchor_admin + '    "tw-098": ["宜蘭縣"],\n', 1)
    m = re.search(r'            \(25\.1664, 121\.5743, "擎天崗草原"[^\n]*\n', text)
    assert m, "tw tuple anchor missing (last tw tuple: 擎天崗)"
    tuple_line = (f'            ({P["lat"]}, {P["lon"]}, "{n["zh-TW"]}", "{n["en"]}", '
                  f'"{n["ja"]}", "{n["local"]}", "{P["category"]}", {json.dumps(P["tags"], ensure_ascii=False)}),\n')
    text = text[:m.end()] + tuple_line + text[m.end():]
    m = re.search(r'    "塔塔加夫妻樹／鹿林山觀景點": 2478,\n', text)
    assert m
    text = text[:m.end()] + f'    "{n["zh-TW"]}": {P["elev_m"]},\n' + text[m.end():]
    anchor = 'SPOT_OVERRIDES = {\n'
    ii = text.index(anchor) + len(anchor)
    q = n["local"]
    src = P["coord_source"].replace('"', "'")
    ins = (' "%s": {"lat": %s,\n           "lon": %s,\n           "map_query": %s,\n'
           '           "coordinate_source": %s,\n           "coordinate_confidence": "%s"},\n'
           % (n["zh-TW"], P["lat"], P["lon"], json.dumps(q, ensure_ascii=False),
              json.dumps("CL-DATA-25R admission web verification 2026-11-07: " + src, ensure_ascii=False),
              P["coord_conf"]))
    text = text[:ii] + ins + text[ii:]
assert "渭水之丘" in text
cl.wbytes(rp, text)
print("regions.py patched")

# ---- 4) runtime catalog
cat_path = ROOT / "runtime_catalog_v004_r4_2.json"
cat = json.loads(cat_path.read_bytes().decode("utf-8"))
max_var = 0
for s in cat["spots"]:
    for o in s["opportunities"]:
        for v in o.get("condition_variants", []):
            max_var = max(max_var, int(str(v["variant_id"]).split("-")[1]))
spot, _ = cl.build_legacy_spot(P, max_var + 1)
if "tw-098" in {s["spot_id"] for s in cat["spots"]}:
    cat["spots"] = [s for s in cat["spots"] if s["spot_id"] != "tw-098"]
cat["spots"].append(spot)
cat["counts"] = {
    "spots": len({s["spot_id"] for s in cat["spots"]}),
    "opportunities": sum(len(s["opportunities"]) for s in cat["spots"]),
    "condition_variants": sum(sum(len(o.get("condition_variants", [])) for o in s["opportunities"]) for s in cat["spots"]),
    "profile_viewpoint_relations": sum(sum(len(o.get("viewpoints", [])) for o in s["opportunities"]) for s in cat["spots"]),
}
cl.wbytes(cat_path, cl.jdump(cat))
print("runtime catalog counts:", cat["counts"])

# ---- 5) manifest: write totals AND tw region counts BEFORE importing opportunities
mf_path = ROOT / "runtime_catalog_manifest_r4_2.json"
mf = json.loads(mf_path.read_bytes().decode("utf-8"))
tw_spots = [s for s in cat["spots"] if s["spot_id"].startswith("tw-")]
tw_opps = [o for s in tw_spots for o in s["opportunities"]]
mf["regions"]["tw"]["numeric_id_end"] = 98
mf["regions"]["tw"]["counts"] = {
    "spots": len(tw_spots), "opportunities": len(tw_opps),
    "condition_variants": sum(len(o.get("condition_variants", [])) for o in tw_opps),
    "profile_viewpoint_relations": sum(len(o.get("viewpoints", [])) for o in tw_opps)}
mf["totals"] = dict(cat["counts"])
cl.wbytes(mf_path, cl.jdump(mf))
import opportunities as _O
pol = Counter()
for s in cat["spots"]:
    for o in s["opportunities"]:
        pol[_O.runtime_policy(o)] += 1
mf = json.loads(mf_path.read_bytes().decode("utf-8"))
mf["runtime_policy_counts"] = dict(pol)
cl.wbytes(mf_path, cl.jdump(mf))
print("manifest tw counts:", mf["regions"]["tw"]["counts"], mf["runtime_policy_counts"])

# ---- 6) runtime_dependencies profile gap (cloud_sea only; city_night has no component)
dep = ROOT / "runtime_dependencies.py"
rd = dep.read_bytes().decode("utf-8").replace("\r\n", "\n")
anchor = '    "spatial_weather_vertical_cloud": frozenset({\n'
assert anchor in rd
if "tw-098-P01" not in rd:
    i = rd.index(anchor) + len(anchor)
    rd = rd[:i] + '        "tw-098-P01",\n' + rd[i:]
cl.wbytes(dep, rd)
print("runtime_dependencies gap added")

# ---- 7) evidence audit: append place + evidence row
ev_path = ROOT / "data/v2/audits/cl-data-25_web_evidence.json"
ev = json.loads(ev_path.read_bytes().decode("utf-8"))
if not any(x["place_id"] == "tw-098" for x in ev["places"]):
    ev["places"].append({
        "place_id": "tw-098", "slug": P["slug"], "score": P["score"],
        "lat": P["lat"], "lon": P["lon"], "elev_m": P["elev_m"],
        "coord_confidence": P["coord_conf"], "coord_source": P["coord_source"],
        "sources": P["coord_sources"], "subjects": [s["zh"] for s in P["subjects"]],
        "ticket": "CL-DATA-25R"})
    ev["evidence"].append({
        "id": "e-d25-web-weishui-hill", "grade": "B",
        "kind": "official_or_wikipedia_text",
        "url": P["coord_sources"][0],
        "supports": P["coord_source"],
        "retrieved_at": "2026-11-07",
        "limitation": "Coordinate verified against zh.wikipedia (櫻花陵園 infobox 24°49′23″N 121°42′9″E, 園區最高丘地=渭水之丘); exact tripod position, viewing bearing and access not field-surveyed.",
        "ticket": "CL-DATA-25R"})
cl.wbytes(ev_path, cl.jdump(ev))
print("web evidence updated")

# ---- 8) 25R candidates record + dedupe addendum
cand = {
    "ticket": "CL-DATA-25R", "generated_at": "2026-11-07",
    "rule": "rubric v2 owner ruling 2026-11-07: weighted_total_v2 >= 3.8 admits directly; < 3.8 Excel side list only",
    "admitted": [{"place_id": "tw-098", "slug": P["slug"], "v2": 3.8, "v1": 4.0,
                  "note": "previously Excel-side at v1 for the 5km rule (vs tw-031 抹茶山 3.281 km); v2 ruling admits on score with subject differentiation documented in the dossier",
                  "dedupe": {"nearest": "tw-031 抹茶山", "km": 3.281,
                             "differentiation": "subject-disjoint: plain-fog overlook (cloud_sea) + plain night lights (city_night) vs hiking-trail mountain scenery (tw-031); different genre templates and viewing axis"}}],
    "excel_side": [
        {"id": "jp-north-monaiyama-unkai", "zh": "毛無山展望所（小樽雲海）", "v2": 3.55,
         "reason": "<3.8 v2 rubric — Excel-only per CL-DATA-25R owner ruling"},
        {"id": "jp-050", "zh": "安比高原雲海ゴンドラ", "v2": 3.30,
         "reason": "v1-built then rolled back (v2 <3.8) — Excel side list"},
        {"id": "tw-090", "zh": "加路蘭海岸遊憩區", "v2": 3.70,
         "reason": "v1-built then rolled back (v2 <3.8) — Excel side list"},
        {"id": "tw-092", "zh": "北關海潮公園", "v2": 3.60,
         "reason": "v1-built then rolled back (v2 <3.8) — Excel side list"},
        {"id": "tw-096", "zh": "半天寮好望角", "v2": 3.70,
         "reason": "v1-built then rolled back (v2 <3.8) — Excel side list"},
        {"id": "tw-097", "zh": "擎天崗草原", "v2": 3.20,
         "reason": "v1-built then rolled back (v2 <3.8) — Excel side list"},
        {"id": "tw-qingjing-farm", "zh": "清境農場霧上觀景帶", "v2": 3.45,
         "reason": "<3.8 v2 rubric — Excel-only"},
    ],
}
(ROOT / "data/v2/tools/discovery/cl_data_25r_candidates.json").write_bytes(dump(cand).encode("utf-8"))
print("25R candidates written")

# dedupe report: add candidate entry consistent with the check we ran earlier
rep = load("data/v2/audits/cl-data-25r_dedupe_report.json")
rep["tw_098_candidate"]["admitted"] = True
rep["tw_098_candidate"]["differentiation"] = cand["admitted"][0]["dedupe"]["differentiation"]
(ROOT / "data/v2/audits/cl-data-25r_dedupe_report.json").write_bytes(dump(rep).encode("utf-8"))

# ---- 9) dossier: record the corrected coordinate + 3.28km differentiation
dpath = ROOT / "data/v2/audits/discovery/tw-weishui-hill.md"
d = dpath.read_bytes().decode("utf-8")
d = d.replace("- 座標：24.636, 121.64（海拔 800 m）",
             "- 座標：24.823055, 121.7025（海拔 800 m；CL-DATA-25R 依 zh.wikipedia 櫻花陵園 infobox 24°49′23″N 121°42′9″E 修正——dossier 初版 24.636,121.64 與實際位置偏差大）")
d = d.replace("- 差異化（機械計算）：最近既有景點 松蘿湖，距離 12.4 km",
             "- 差異化（機械計算，CL-DATA-25R 修正座標後重跑）：最近既有景點 tw-031 抹茶山，距離 3.281 km（<5km）——**題材錯位**：本點為平原霧海俯視點（cloud_sea 琉璃光）＋平原夜間燈海（city_night），tw-031 為登山步道山景題材（sunrise/mountain），觀景軸線與契約題材不同，差異化成立；次近 tw-055 五峰旗瀑布 4.527 km（瀑布題材）")
dpath.write_bytes(d.encode("utf-8"))
print("dossier updated")
print("DONE: commit-ready build for tw-098")
