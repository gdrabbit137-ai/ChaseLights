#!/usr/bin/env python3
"""CL-DATA-31 — scenic v3 supplementary scoring for discovery candidates.

Candidate pool (CL-DATA-25R/26: jp-north + tw shortlists) members that were NOT
yet admitted into the catalog have no scenic-v3 composite. This tool runs the
same CL-DATA-30 pipeline (photo fetch -> community signals -> finalize with
vision layer) for those candidate ids and writes:

  data/v2/audits/discovery/scenic-v3-candidates-progress.json  (fetch + community)
  data/v2/audits/discovery/scenic-v3-candidates.json           (final composites)

Vision layer: montages (scratch/d31_montages, same layout as scenic_v3_montage)
are scored into <scratch>/d31_vision/<batch>.json as
  place_id -> {label: {valid: bool, subs: [4 ints 1-10] or null, note, reason}}

Stages: python scenic_v3_candidates.py --stage fetch|community|finalize
"""
from __future__ import annotations
import json, os, statistics, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "data/v2/tools"))

OUT = REPO / "data/v2/audits/discovery/scenic-v3-candidates-progress.json"
RESULT = REPO / "data/v2/audits/discovery/scenic-v3-candidates.json"
SCRATCH = Path(os.environ.get(
    "CL31_SCRATCH",
    "C:/Users/Dick_/AppData/Local/hermes/profiles/chaselights_manager/cache/scratch"))

# Candidates absent from the catalog -> absent from scenic-v3-full.json.
# (id, name_zh, name_en, name_ja, cert_tier, cert_evidence)
CANDIDATES = [
    ("jp-north-biei-blue-pond", "青い池（美瑛・白金）", "Blue Pond Biei",
     "青い池（美瑛・白金）", 3,
     "多方攝影/觀光攻略共識景點（媒體報導與清單文），無官方景觀分類"),
    ("jp-north-monaiyama-unkai", "毛無山展望所（小樽雲海）", "Monaiyama Unkai Otaru",
     "毛無山展望所（小樽）", 2,
     "地方展望所，無官方景觀認證、攻略清單頻率不足"),
    ("jp-north-appi-unkai", "安比高原雲海ゴンドラ", "APPI Kogen Unkai Gondola",
     "安比高原 雲海ゴンドラ", 2,
     "度假村商業設施，無官方景觀認證"),
    ("tw-qingjing-farm", "清境農場霧上觀景帶", "Qingjing Farm Nantou",
     "清境農場", 3,
     "民宿帶觀景媒體與攝影部落格多方共識，無官方景觀分類"),
    ("tw-qingtiangang", "擎天崗草原", "Qingtiangang Grassland Taipei",
     "擎天崗草原", 2,
     "國家公園內遊憩區但無景觀級認證、攻略清單頻率不足"),
]


def load_pool_carried():
    """Pool members already in the catalog: carry their scenic-v3-full composites."""
    v3 = json.loads((REPO / "data/v2/audits/discovery/scenic-v3-full.json")
                    .read_text(encoding="utf-8"))
    by_name = {p["name_zh"]: p for p in v3["places"]}
    out = {}
    for f in ("jp-north-shortlist", "tw-shortlist"):
        d = json.loads((REPO / f"data/v2/audits/discovery/{f}.json")
                       .read_text(encoding="utf-8"))
        for c in d["candidates"]:
            z = c["name_i18n"]["zh-TW"]
            if z in by_name:
                p = by_name[z]
                out[c["id"]] = {
                    "name_zh": z, "source": "catalog(scenic-v3-full)",
                    "catalog_place_id": p["place_id"],
                    "composite_v3": p["composite_v3"],
                    "visual_0_5": p["visual_0_5"], "cert_tier": p["cert_tier"],
                    "community_adj": p["community_adj"],
                    "cert_evidence": p["cert_evidence"]}
    return out


def stage_fetch():
    import scenic_v3_fetch as F
    prog = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {
        "schema": "scenic-v3-candidates/1", "ticket": "CL-DATA-31",
        "stage_photos": {}, "stage_community": {}}
    for pid, zh, en, ja, tier, ev in CANDIDATES:
        if pid in prog["stage_photos"]:
            continue
        cands = []
        for q in (zh, en, ja):
            if not q:
                continue
            cands += F.commons_search(q, 8)
            time.sleep(1.0)
        for lang, q in (("zh", zh), ("en", en), ("ja", ja)):
            if not q:
                continue
            cands += F.wiki_images(lang, q, 10)
            time.sleep(1.0)
        cands = F.dedupe_filter(cands)
        good = [c for c in cands if not c.get("filtered_out")]
        if len(good) < 6 and en:
            cands += F.openverse(en)
            time.sleep(0.5)
            cands = F.dedupe_filter(cands)
            good = [c for c in cands if not c.get("filtered_out")]
        files, srcs = [], set()
        by_src = {}
        for c in good:
            by_src.setdefault(c["source"], []).append(c)
        order = list(by_src)
        while len(files) < 6 and any(by_src[s] for s in order):
            for s in order:
                if by_src[s] and len(files) < 6:
                    files.append(by_src[s].pop(0))
                    srcs.add(s)
        prog["stage_photos"][pid] = {
            "name": zh, "photos": files,
            "dropped_titles": [c.get("title") for c in cands if c.get("filtered_out")],
            "sources_tried": sorted(srcs), "cert_tier": tier, "cert_evidence": ev}
        prog["updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        tmp = OUT.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(prog, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(OUT)
        print(pid, len(files), sorted(srcs), flush=True)


def stage_community():
    import scenic_v3_community as C
    C.OUT = OUT
    C.main()


def community_adj(photos, comm):
    """Same owner-corrected rule as scenic_v3_finalize.community_adj."""
    any_badge, any_highpv, has = False, False, False
    inv_complete, payload_missing, all_lowpv = True, False, True
    for p in photos:
        if not p.get("_valid"):
            continue
        c = comm.get(p["key"])
        if not c:
            inv_complete = False
            continue
        has = True
        if "badges" not in c:
            inv_complete = False
        elif c["badges"]:
            any_badge = True
        pv = c.get("pv12mo")
        if pv is None:
            payload_missing = True
        else:
            if pv >= 5000:
                any_highpv = True
            if pv >= 50:
                all_lowpv = False
    if not has:
        return 0, "無社群信號資料"
    if any_badge:
        return 0.5, "Commons 社群標章（代表性篩選通過照片）"
    if any_highpv:
        return 0.25, "檔案頁12個月瀏覽≥5000"
    if inv_complete and not payload_missing and all_lowpv:
        return -0.25, "完整標章盤點無標章且12個月瀏覽均<50"
    return 0, "無標章、瀏覽量普通或資料不完整（不負向校正）"


def stage_finalize():
    prog = json.loads(OUT.read_text(encoding="utf-8"))
    vision = {}
    vdir = SCRATCH / "d31_vision"
    if vdir.is_dir():
        for f in sorted(vdir.glob("*.json")):
            vision.update(json.loads(f.read_text(encoding="utf-8")))
    results = []
    for pid, zh, en, ja, tier, ev in CANDIDATES:
        photos = (prog["stage_photos"].get(pid) or {}).get("photos") or []
        vis_scores = vision.get(pid) or {}
        pl = []
        for i, ph in enumerate(photos):
            lab = chr(65 + i)
            key = ph.get("title") or ph.get("url") or ""
            v = vis_scores.get(lab) or {}
            subs = v.get("subs")
            pl.append({**ph, "key": key, "label": lab,
                       "_valid": bool(v.get("valid")) and bool(subs),
                       "_subs": subs if v.get("valid") else None,
                       "_note": v.get("note", ""), "_reason": v.get("reason", "")})
        for x in pl:
            x["_photo_mean"] = round(sum(x["_subs"]) / 4, 2) \
                if x["_subs"] and x["_valid"] else None
        means = [x["_photo_mean"] for x in pl if x["_valid"] and x["_subs"]]
        if len(means) >= 2:
            visual10 = statistics.median(means)
        elif len(means) == 1:
            visual10 = means[0]
        else:
            visual10 = None
        visual = round(visual10 / 2, 2) if visual10 is not None else None
        cadj, cev = community_adj(pl, prog.get("stage_community", {}))
        if visual is None:
            comp = cert_adj = None
            why = "unknown：無有效代表照片（不虛構分數）"
        else:
            cert_adj = max(-1, min(1, tier - visual))
            comp = round(max(0, min(5, visual + cert_adj + cadj)), 2)
            why = f"視覺{visual}＋認證校正{round(cert_adj, 2)}＋社群{cadj}"
        results.append({
            "id": pid, "name_zh": zh, "photos": pl,
            "n_photos_fetched": len(photos),
            "n_valid": sum(1 for x in pl if x["_valid"]),
            "sources": (prog["stage_photos"].get(pid) or {}).get("sources_tried"),
            "visual_0_5": visual, "cert_tier": tier, "cert_evidence": ev,
            "community_adj": cadj, "community_evidence": cev,
            "composite_v3": comp, "composite_formula": why,
            "source": "candidate-supplementary",
        })
    RESULT.write_text(json.dumps({
        "schema": "scenic-v3-candidates/1", "ticket": "CL-DATA-31",
        "method": {"visual": "多源照片→代表性篩選→四子項1–10（n≥2取中位數、n=1取均值）÷2",
                   "cert": "認證階梯±1（5=UNESCO/國際、4=國家級官方、3=多攻略共識、2=一般）",
                   "community": "Commons 標章/瀏覽量 ±0.5（視覺為主）",
                   "composite": "visual_0_5 + clamp(tier−visual,−1,+1) + community ±0.5，clip 0–5"},
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "carried_from_catalog": load_pool_carried(),
        "candidates": results,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("finalized:", [(r["id"], r["composite_v3"]) for r in results])


if __name__ == "__main__":
    stage = sys.argv[sys.argv.index("--stage") + 1] if "--stage" in sys.argv else "fetch"
    {"fetch": stage_fetch, "community": stage_community,
     "finalize": stage_finalize}[stage]()
