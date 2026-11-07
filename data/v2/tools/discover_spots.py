#!/usr/bin/env python3
"""CL-DATA-23 — candidate spot discovery & evaluation pipeline (machine-runnable).

Reads a per-region candidate JSON (data/v2/tools/discovery/<region>_candidates.json),
computes the mechanical rubric dimension (differentiation: >5 km from every existing
catalog spot, via regions.py), validates the manual rubric dimensions, and writes:

  - data/v2/audits/discovery/<region>-shortlist.json   machine-readable shortlist
      (schema "cl-data-23-discovery-1", same convention as jp-north)
  - data/v2/audits/discovery/<region>-<slug>.md        per-candidate dossier
  - data/v2/audits/discovery/<region>-shortlist.md     human-readable Top-N summary

This tool NEVER modifies the catalog: shortlist membership is a PM/owner product
decision. It only produces dossiers + a ranked shortlist.

Rubric v2 (CL-DATA-26 owner ruling 2026-11-07; 1–5, weights sum 100:
subject 25 / weather-light 20 / verifiability 20 / differentiation 15 /
scenic_beauty 20):
  a) subject_strength          — iconic subject present (manual, audited)
  b) weather_light_dependency  — how decisive our weather/light model is
                                 (cloud sea / glow / milky way / seasonal → high;
                                  indoor or weather-free → low) (manual)
  c) verifiability             — coordinates/elevation verifiable from web
                                 evidence (manual)
  d) differentiation           — MECHANICAL: culled if within 5 km of any existing
                                 catalog spot with tag overlap; otherwise scored by
                                 nearest-distance band
  e) scenic_beauty             — MECHANICAL from dossier evidence, three 0/1
                                 signals (base 2, +1 each, +1 top-tier bonus):
                                   s1 photo-community prominence (攝影社群/攝影
                                      平台專題收錄)
                                   s2 official classification (官方 A 級・全国観光
                                      資源評価特A級・世界遺産・日本三大〜・八景/
                                      百選類)
                                   s3 guide-list frequency (≥2 獨立攻略清單文
                                      收錄)
                                 top-tier bonus (+1, cap 5): 世界遺産 / 特A級 /
                                 三大之首 / 観光資源台帳 A級・日本一級超級位階
  safe_access REMOVED from scoring (CL-DATA-26): its seasonal-window/closure
  information is still REQUIRED in dossiers and contracts (seasonal_window,
  access_note, safety_note) — it just no longer influences admission scoring.

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

# rubric v2 key in candidates JSON -> shortlist key (weight); weights sum to 100
RUBRIC_MAP = {
    "subject_strength":     ("subject_strength", 25),
    "weather_dependency":   ("weather_light_dependency", 20),
    "data_availability":    ("verifiability", 20),
    "differentiation":      ("differentiation", 15),
    "scenic_beauty":        ("scenic_beauty", 20),
}
MANUAL_KEYS = [k for k in RUBRIC_MAP if k != "differentiation"]

# v1 rubric (CL-DATA-23) kept ONLY for score comparison — safe_access no longer
# scores; its seasonal-window/closure info stays in dossier/contract fields.
V1_RUBRIC_MAP = {
    "subject_strength":     ("subject_strength", 25),
    "weather_dependency":   ("weather_light_dependency", 20),
    "data_availability":    ("verifiability", 20),
    "differentiation":      ("differentiation", 15),
    "accessibility_safety": ("safe_access", 20),
}


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def load_existing_spots(region="tw"):
    """Existing catalog spots (regions.py) for dedup."""
    import regions
    spots = regions.get_spots(region)
    return [(s["name_i18n"]["zh-TW"], s["lat"], s["lon"], s["tags"]) for s in spots]


def check_differentiation(cand, existing, radius_km=DEDUP_RADIUS_KM):
    """Mechanical rubric item (d). Returns (score, geo, culled, reasons)."""
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
        return (1, geo, True, reasons)
    if nearest_km is None:
        return (3, geo, False, reasons)
    if nearest_km > 15:
        score = 5
    elif nearest_km > 8:
        score = 4
    else:
        score = 3
    return (score, geo, False, reasons)


def evaluate(cand, existing):
    missing = [k for k in MANUAL_KEYS if k not in cand.get("scores", {})]
    if missing:
        raise SystemExit(f"{cand['slug']}: missing manual rubric scores {missing}")
    diff_score, geo, culled, cull_reasons = check_differentiation(cand, existing)
    rubric = {RUBRIC_MAP[k][0]: int(cand["scores"][k]) for k in MANUAL_KEYS}
    rubric["differentiation"] = diff_score
    total_w = sum(w for _, w in RUBRIC_MAP.values())
    weighted = round(sum(rubric[key] * w for key, w in RUBRIC_MAP.values())
                     / total_w, 2)
    # v1 comparison score (CL-DATA-23 rubric incl. safe_access) when the old
    # score key is still carried — informational only, never gates admission.
    weighted_v1 = None
    if "accessibility_safety" in cand.get("scores", {}):
        v1rubric = {V1_RUBRIC_MAP[k][0]: int(cand["scores"][k])
                    for k in V1_RUBRIC_MAP if k != "differentiation"}
        v1rubric["differentiation"] = diff_score
        weighted_v1 = round(
            sum(v1rubric[key] * w for key, w in V1_RUBRIC_MAP.values()) / 100, 2)
    return {
        "id": f"{cand.get('region', 'tw')}-{cand['slug']}",
        "name_i18n": {"zh-TW": cand["name_zh"], "en": cand["name_en"],
                      "ja": cand["name_ja"]},
        "prefecture": cand.get("pref", cand["name_en"]),
        "subjects": list(cand["tags"]),
        "rubric": rubric,
        "weighted_total": weighted,
        "weighted_total_v1": weighted_v1,
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
    lines = [
        f"# 候選景點 dossier：{cand['name_zh']}（{cand['name_en']}）",
        "",
        f"- region: {cand.get('region', 'tw')} | slug: `{ev['id']}`",
        f"- 座標：{cand['lat']}, {cand['lon']}（海拔 {cand['elev_m']} m）",
        f"- 擬設 subjects：{', '.join(cand['tags'])}",
        f"- 差異化（機械計算）：最近既有景點 {ev['_geo']['nearest']}，距離 {ev['_geo']['km']} km",
        f"- **rubric 加權總分：{ev['weighted_total']} / 5**",
        "",
        "## Rubric 評分（v2，1–5，權重 25/20/20/15/20＝100）",
        "",
        "| 項目 | 分數 |",
        "|---|---|",
    ]
    for key, _ in RUBRIC_MAP.values():
        lines.append(f"| {key} | {ev['rubric'][key]} |")
    if ev.get("weighted_total_v1") is not None:
        lines += ["", f"> v1（CL-DATA-23 含 safe_access）加權總分對照：{ev['weighted_total_v1']} / 5",
                  "> v2 移除 safe_access 評分（其季節窗/封閉期資訊仍保留於本 dossier 與契約）。"]
    lines += ["", "## Web 證據", ""]
    for ref in cand["source_refs"]:
        lines.append(f"- [{ref['url']}]({ref['url']}) — {ref['note']}")
    if cand.get("scenic_beauty_evidence"):
        lines += ["", "## scenic_beauty 證據（v2 機械化分級依據）", "",
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
    lines.append("> 本 dossier 僅為候選建議；清單成員是 owner 產品決策。座標標註「近似」者入選前須 Maps 定位驗證。")
    return "\n".join(lines)


def render_shortlist_md(region, ranked, kept, culled, top_n):
    lines = [
        f"# {region.upper()} 候選景點短名單（CL-DATA-23 首輪）",
        "",
        f"候選 {len(ranked)} 個｜進短名單 {len(kept)}｜差異化剔除 {len(culled)}｜Top N = {top_n}",
        "",
        "| 排名 | 景點 | 加權總分 | 擬設題材 | 最近既有景點 (km) |",
        "|---|---|---|---|---|",
    ]
    for i, ev in enumerate(kept[:top_n], 1):
        lines.append(f"| {i} | {ev['name_i18n']['zh-TW']} | {ev['weighted_total']} | "
                     f"{', '.join(ev['subjects'])} | "
                     f"{ev['_geo']['nearest']} ({ev['_geo']['km']}) |")
    if culled:
        lines += ["", "## 已剔除", ""]
        for ev in culled:
            lines.append(f"- {ev['name_i18n']['zh-TW']} — {'; '.join(ev['_cull_reasons'])}")
    lines += ["",
              "> 僅供 PM 短名單決策；本管線不直接加入任何景點。"
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
    outdir = REPO_ROOT / args.outdir
    outdir.mkdir(parents=True, exist_ok=True)

    evals = [evaluate(c, existing) for c in data["candidates"]]
    for ev in evals:
        (outdir / f"{ev['id']}.md").write_text(render_dossier(ev), encoding="utf-8")

    kept = sorted([e for e in evals if not e["_culled"]],
                  key=lambda e: -e["weighted_total"])
    culled = [e for e in evals if e["_culled"]]

    shortlist = {
        "schema_version": "cl-data-23-discovery-1",
        "ticket": "CL-DATA-23 + CL-DATA-26 (rubric v2)",
        "region": args.region,
        "region_scope": "台灣本島＋離島",
        "generated_at": date.today().isoformat(),
        "generated_by": "chaselights_rd (AI discovery round, owner arbiter on catalog membership)",
        "rubric": {
            "dimensions": [
                {"key": "subject_strength", "weight": 25,
                 "description": "題材本身的攝影知名度與畫面張力（全國級=5，地方級=3）"},
                {"key": "weather_light_dependency", "weight": 20,
                 "description": "成片品質對特定天氣/光影條件的依賴程度（幾乎全天可拍=1，雲海/銀河/季節=5）"},
                {"key": "verifiability", "weight": 20,
                 "description": "官方/權威來源對座標、季節窗、交通與閉鎖資訊的可查證程度"},
                {"key": "differentiation", "weight": 15,
                 "description": "與既有 catalog 地理 5km＋題材重複之差異化（機械計算）"},
                {"key": "scenic_beauty", "weight": 20,
                 "description": "景觀美譽（CL-DATA-26 v2 機械化）：攝影社群熱度 s1、官方分類（A級/世界遺產/三大類/八景百選）s2、攻略清單文出現頻率（≥2獨立清單）s3 — 各 0/1，分數 = 2 + s1+s2+s3，世界遺產/特A級/三大之首/台帳A級加 +1（上限5），dossier 證據為準"},
            ],
            "scoring_removed": [
                {"key": "safe_access",
                 "reason": "CL-DATA-26 owner ruling 2026-11-07: 移除 safe_access（20 分權重改給 scenic_beauty）；其季節窗/封閉期資訊仍必須留在 dossier 與契約（seasonal_window/access_note/safety_note），只是不再影響評分"},
            ],
        },
        "candidates": [
            {k: v for k, v in e.items() if not k.startswith("_")} for e in kept
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
                      "kept": len(kept), "culled": len(culled),
                      "top5": [f"{e['name_i18n']['zh-TW']} {e['weighted_total']}" for e in kept[:5]]},
                     ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
