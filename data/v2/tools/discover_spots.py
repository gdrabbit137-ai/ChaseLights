#!/usr/bin/env python3
"""CL-DATA-31 — candidate spot discovery & evaluation pipeline (rubric v3).

Reads a per-region candidate JSON (data/v2/tools/discovery/<region>_candidates.json),
computes the mechanical differentiation cull (>5 km + tag overlap from every
existing catalog spot, via regions.py), and scores admission with RUBRIC V3
(owner ruling, CL-DATA-31):

  評分＝景色優美程度（單一維度 0–5），來源＝scenic v3 合成分
    composite_v3 = visual_0_5（多源照片視覺主，1–10 四子項中位數÷2）
                 + clamp(cert_tier − visual, −1, +1)   （認證階梯校正）
                 + community ±0.5                        （Commons 標章/瀏覽量）
  三重信號：視覺主＋認證（官方層級）＋社群校正。

  - 既有 catalog 景點之分數取自 data/v2/audits/discovery/scenic-v3-full.json
  - 新候選走同一管線：data/v2/tools/scenic_v3_candidates.py 產出
    data/v2/audits/discovery/scenic-v3-candidates.json；分數缺漏者標
    「unscored（須補評）」，永不虛構分數。
  - 納入線：composite_v3 >= 3.8（與 CL-DATA-25R/26 同線）。
  - v2 五維加權 rubric（subject/weather/verifiability/differentiation/scenic
    三信號機械化版）RETIRED：不再影響納入；dossier 仍保留其歷史證據文字。
  - 照片 provenance：v3 評分所用的每張代表照片（label/url/source/子分）原樣
    進入 shortlist 與 dossier，可回溯視覺評分依據。

differentiation 仍是 MECHANICAL cull（5 km＋tag 重疊剔除），但不計入分數；
safe_access / subject 等 v2 維度不再計分，其季節窗/可達性資訊仍必須留在
dossier 與契約欄位。

This tool NEVER modifies the catalog: shortlist membership is a PM/owner
product decision. It only produces dossiers + a ranked shortlist.

Usage:
  python discover_spots.py --region tw [--top 10] [--outdir data/v2/audits/discovery]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEDUP_RADIUS_KM = 5.0
DIFFERENTIATION_TAG_OVERLAP_LIMIT = 1  # overlapping spot tags allowed before cull

LINE = 3.8  # 納入線（CL-DATA-25R/26 同線；rubric v3）

V3_FULL = REPO_ROOT / "data/v2/audits/discovery/scenic-v3-full.json"
V3_CAND = REPO_ROOT / "data/v2/audits/discovery/scenic-v3-candidates.json"

# retired v2 dimensions — kept only as evidence fields in dossiers
V2_RETIRED_KEYS = ["subject_strength", "weather_dependency", "data_availability",
                   "scenic_beauty"]


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def load_existing_spots(region="tw"):
    """Existing catalog spots (regions.py) for the differentiation cull."""
    import regions
    spots = regions.get_spots(region)
    return [(s["name_i18n"]["zh-TW"], s["lat"], s["lon"], s["tags"]) for s in spots]


def check_differentiation(cand, existing, radius_km=DEDUP_RADIUS_KM):
    """Mechanical cull (not a scored dimension under v3).
    Returns (culled, geo, reasons)."""
    reasons = []
    nearest_name, nearest_km = None, None
    worst_overlap = None
    for name, lat, lon, tags in existing:
        d = haversine_km(cand["lat"], cand["lon"], lat, lon)
        if nearest_km is None or d < nearest_km:
            nearest_name, nearest_km = name, d
        if d <= radius_km:
            overlap = sorted(set(cand["tags"]) & set(tags))
            reasons.append(
                f"geographic conflict: {name} at {d:.1f} km (<= {radius_km} km), "
                f"tag overlap {overlap}")
            if worst_overlap is None or len(overlap) > len(worst_overlap[1]):
                worst_overlap = (name, overlap)
    geo = {"nearest": nearest_name,
           "km": round((nearest_km if nearest_km is not None else 0.0), 1)}
    if worst_overlap is not None:
        return True, geo, reasons
    return False, geo, reasons


def load_v3_scores():
    """scenic-v3 composite by 景點中文名 — catalog + candidate supplements."""
    scores = {}
    if V3_FULL.exists():
        d = json.loads(V3_FULL.read_text(encoding="utf-8"))
        for p in d["places"]:
            scores.setdefault(p["name_zh"], {
                "composite_v3": p["composite_v3"], "visual_0_5": p["visual_0_5"],
                "cert_tier": p["cert_tier"], "cert_evidence": p["cert_evidence"],
                "community_adj": p["community_adj"],
                "community_evidence": p["community_evidence"],
                "composite_formula": p["composite_formula"],
                "photos": p["photos"], "place_id": p["place_id"],
                "source": "catalog(scenic-v3-full)"})
    if V3_CAND.exists():
        d = json.loads(V3_CAND.read_text(encoding="utf-8"))
        for c in d["candidates"]:
            if c.get("composite_v3") is None:
                continue
            scores.setdefault(c["name_zh"], {
                "composite_v3": c["composite_v3"], "visual_0_5": c["visual_0_5"],
                "cert_tier": c["cert_tier"], "cert_evidence": c["cert_evidence"],
                "community_adj": c["community_adj"],
                "community_evidence": c["community_evidence"],
                "composite_formula": c["composite_formula"],
                "photos": c["photos"], "place_id": None,
                "source": "candidate-supplementary"})
    return scores


def evaluate(cand, existing, v3):
    culled, geo, cull_reasons = check_differentiation(cand, existing)
    s = v3.get(cand["name_zh"])
    if s is None:
        scenic = {"composite_v3": None, "status": "unscored（須補評：走 "
                                                     "scenic_v3_candidates.py 同管線）"}
        admits = False
    else:
        scenic = dict(s)
        scenic["status"] = "scored"
        admits = scenic["composite_v3"] is not None and scenic["composite_v3"] >= LINE
    return {
        "id": f"{cand.get('region', 'tw')}-{cand['slug']}",
        "name_i18n": {"zh-TW": cand["name_zh"], "en": cand["name_en"],
                      "ja": cand["name_ja"]},
        "prefecture": cand.get("pref", cand["name_en"]),
        "subjects": list(cand["tags"]),
        "rubric_v3": scenic,
        "admits": admits and not culled,
        # informational only — v2 five-dimension weighted total is retired
        "weighted_total_v2_retired": cand.get("scores", {}).get("scenic_beauty"),
        "scenic_beauty_evidence": cand.get("scenic_beauty_evidence", ""),
        "sources": [r["url"] for r in cand["source_refs"]],
        "coords_approx": {"lat": cand["lat"], "lon": cand["lon"]},
        "elev_m": cand["elev_m"],
        "seasonal_window": cand.get("seasonal_window"),
        "access_note": cand["access_note"],
        "safety_note": cand["safety_note"],
        "differentiation_note": cand["differentiation_note"],
        "_cand": cand, "_geo": geo, "_culled": culled, "_cull_reasons": cull_reasons,
    }


def render_dossier(ev):
    cand = ev["_cand"]
    s = ev["rubric_v3"]
    comp = s.get("composite_v3")
    lines = [
        f"# 候選景點 dossier：{cand['name_zh']}（{cand['name_en']}）",
        "",
        f"- region: {cand.get('region', 'tw')} | slug: `{ev['id']}`",
        f"- 座標：{cand['lat']}, {cand['lon']}（海拔 {cand['elev_m']} m）",
        f"- 擬設 subjects：{', '.join(cand['tags'])}",
        f"- 差異化剔除檢查（機械）：最近既有景點 {ev['_geo']['nearest']}，距離 {ev['_geo']['km']} km",
        f"- **rubric v3 景色優美單維度：{comp if comp is not None else 'unscored（須補評）'} / 5"
        f"（納入線 ≥ {LINE}）**",
    ]
    if comp is not None:
        lines.append(f"- 合成式：{s.get('composite_formula')}｜認證：tier "
                     f"{s.get('cert_tier')}（{s.get('cert_evidence')}）｜"
                     f"社群：{s.get('community_adj')}（{s.get('community_evidence')}）")
        photos = s.get("photos") or []
        if photos:
            lines += ["", "## 照片 provenance（v3 視覺評分依據）", "",
                      "| 標籤 | 代表照片 | 來源 | 子分(色彩/構圖/光影/獨特性) | 有效 |",
                      "|---|---|---|---|---|"]
            for ph in photos:
                subs = ph.get("_subs") or ph.get("sub_scores")
                valid = ph.get("_valid", ph.get("valid", False))
                lines.append(
                    f"| {ph.get('label', '')} | {ph.get('title') or ph.get('url', '')} "
                    f"| {ph.get('source', '')} | {subs if subs else '—'} "
                    f"| {'✓' if valid else '✗'} |")
    lines += ["", "## Web 證據", ""]
    for ref in cand["source_refs"]:
        lines.append(f"- [{ref['url']}]({ref['url']}) — {ref['note']}")
    if cand.get("scenic_beauty_evidence"):
        lines += ["", "## v2 機械化證據（已退役，僅歷史參考）", "",
                  f"- {cand['scenic_beauty_evidence']}"]
    lines += ["", "## 擬設題材與條件草案", "",
              f"- 題材：{cand['subject_draft']}",
              f"- 條件草案：{cand['condition_draft']}"]
    if cand.get("seasonal_window"):
        sw = cand["seasonal_window"]
        lines.append(f"- 季節窗：月份 {sw['months']} — {sw['note']}")
    lines += [f"- 可達性：{cand['access_note']}",
              f"- 安全：{cand['safety_note']}",
              f"- 差異化說明：{cand['differentiation_note']}",
              ""]
    if ev["_culled"]:
        lines.append("## ⛔ 差異化剔除（不進短名單）")
        lines.append("")
        for r in ev["_cull_reasons"]:
            lines.append(f"- {r}")
        lines.append("")
    if comp is not None and comp < LINE and not ev["_culled"]:
        lines.append(f"> v3 分數低於納入線 {LINE}：列 Excel 側／掉線清單，交 PM → owner。")
    lines.append("> 本 dossier 僅為候選建議；清單成員是 owner 產品決策。座標標註「近似」者入選前須 Maps 定位驗證。")
    return "\n".join(lines)


def render_shortlist_md(region, ranked, kept, culled, top_n):
    lines = [
        f"# {region.upper()} 候選景點短名單（rubric v3：景色優美單維度）",
        "",
        f"候選 {len(ranked)} 個｜達納入線（v3 ≥ {LINE}）且未剔除 {len(kept)}｜"
        f"差異化剔除 {len(culled)}｜Top N = {top_n}",
        "",
        "| 排名 | 景點 | v3 景色優美 | 視覺 | 認證 | 擬設題材 | 最近既有景點 (km) |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, ev in enumerate(kept[:top_n], 1):
        s = ev["rubric_v3"]
        comp = s.get("composite_v3")
        lines.append(
            f"| {i} | {ev['name_i18n']['zh-TW']} | "
            f"{comp if comp is not None else 'unscored'} | "
            f"{s.get('visual_0_5', '—')} | {s.get('cert_tier', '—')} | "
            f"{', '.join(ev['subjects'])} | "
            f"{ev['_geo']['nearest']} ({ev['_geo']['km']}) |")
    if culled:
        lines += ["", "## 已剔除（差異化）", ""]
        for ev in culled:
            lines.append(f"- {ev['name_i18n']['zh-TW']} — {'; '.join(ev['_cull_reasons'])}")
    lines += ["",
              f"> 納入線 v3 ≥ {LINE}（景色優美單維度；v2 五維 rubric 已退役）。"
              "僅供 PM 短名單決策；本管線不直接加入任何景點。"
              "源頭掃描原始紀錄：_source_sweep_raw.json（web 搜尋快取）。"]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default="tw")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--outdir", default="data/v2/audits/discovery")
    args = ap.parse_args(argv)

    cand_path = REPO_ROOT / f"data/v2/tools/discovery/{args.region}_candidates.json"
    with open(cand_path, encoding="utf-8") as f:
        data = json.load(f)

    existing = load_existing_spots(args.region)
    v3 = load_v3_scores()
    outdir = REPO_ROOT / args.outdir
    outdir.mkdir(parents=True, exist_ok=True)

    evals = [evaluate(c, existing, v3) for c in data["candidates"]]
    for ev in evals:
        (outdir / f"{ev['id']}.md").write_text(render_dossier(ev), encoding="utf-8")

    kept = sorted([e for e in evals if not e["_culled"] and e["admits"]],
                  key=lambda e: -(e["rubric_v3"]["composite_v3"] or 0))
    unscored = [e for e in evals if not e["_culled"] and not e["admits"]
                and e["rubric_v3"]["composite_v3"] is None]
    below_line = [e for e in evals if not e["_culled"] and not e["admits"]
                  and e["rubric_v3"]["composite_v3"] is not None]
    culled = [e for e in evals if e["_culled"]]

    shortlist = {
        "schema_version": "cl-data-31-rubric-v3-1",
        "ticket": "CL-DATA-31 (rubric v3 景色優美單維度)",
        "region": args.region,
        "region_scope": "台灣本島＋離島",
        "generated_at": date.today().isoformat(),
        "generated_by": "chaselights_rd (AI discovery round, owner arbiter on catalog membership)",
        "rubric": {
            "version": "v3",
            "admission_line": LINE,
            "dimension": [{
                "key": "scenic_beauty_v3",
                "scale": "0–5",
                "description": "景色優美程度（單一維度）：scenic v3 合成分 = "
                               "視覺主（多源照片四子項中位數÷2）+ 認證階梯校正 ±1 "
                               "+ 社群校正 ±0.5；缺分者標 unscored（須補評），永不虛構",
            }],
            "retired": [
                {"version": "v2 (CL-DATA-26)", "keys": V2_RETIRED_KEYS,
                 "note": "五維加權 rubric 退役，不再影響納入；dossier 保留證據文字。"
                         "differentiation 改為純機械剔除（不計分）。"},
                {"version": "v1/v2 safe_access",
                 "note": "季節窗/封閉期資訊仍必須留在 dossier 與契約，只是從不計分。"},
            ],
        },
        "candidates": [
            {k: v for k, v in e.items() if not k.startswith("_")}
            for e in kept + unscored + below_line
        ],
        "below_line_candidates": [
            {"id": e["id"], "zh": e["name_i18n"]["zh-TW"],
             "v3": e["rubric_v3"]["composite_v3"]}
            for e in below_line
        ],
        "unscored_candidates": [
            {"id": e["id"], "zh": e["name_i18n"]["zh-TW"]} for e in unscored
        ],
        "culled_candidates": [
            {"id": e["id"], "zh": e["name_i18n"]["zh-TW"],
             "reason": "; ".join(e["_cull_reasons"])} for e in culled
        ],
        "source_sweep": "data/v2/audits/discovery/_source_sweep_raw.json",
    }
    (outdir / f"{args.region}-shortlist.json").write_text(
        json.dumps(shortlist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (outdir / f"{args.region}-shortlist.md").write_text(
        render_shortlist_md(args.region, evals, kept, culled, args.top),
        encoding="utf-8")

    print(json.dumps({"region": args.region, "candidates": len(evals),
                      "kept": len(kept), "unscored": len(unscored),
                      "below_line": len(below_line), "culled": len(culled),
                      "top5": [f"{e['name_i18n']['zh-TW']} "
                               f"{e['rubric_v3']['composite_v3']}" for e in kept[:5]]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
