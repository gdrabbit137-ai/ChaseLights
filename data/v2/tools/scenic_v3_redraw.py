#!/usr/bin/env python3
"""CL-DATA-31 — rubric v3 redraw + catalog health report.

Rubric v3 (owner ruling): admission is judged on a SINGLE dimension — 景色優美
程度 (scenic beauty), 0–5, from the scenic-v3 composite (visual-primary +
cert-ladder correction ±1 + community ±0.5). The old five-dimension weighted
rubric (v2) is retired for admission decisions.

Line redraw: CL-DATA-25R/26 candidate pool (jp-north + tw shortlists) scored
with scenic v3; admission line = composite_v3 >= 3.8.

Inputs:
  data/v2/audits/discovery/scenic-v3-full.json        (catalog 218)
  data/v2/audits/discovery/scenic-v3-candidates.json  (candidates, CL-DATA-31)
  data/v2/audits/discovery/jp-north-shortlist.json    (old pool lists)
  data/v2/audits/discovery/tw-shortlist.json

Outputs:
  data/v2/audits/discovery/cl-data-31-rubric-v3-redraw.json
  data/v2/audits/discovery/cl-data-31-rubric-v3-redraw.md

This tool NEVER adds/removes catalog spots: lists are handed to PM -> owner.
"""
from __future__ import annotations
import json, statistics, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
D = REPO / "data/v2/audits/discovery"
LINE = 3.8


def load(fn):
    return json.loads((D / fn).read_text(encoding="utf-8"))


def main():
    v3full = load("scenic-v3-full.json")
    cand = load("scenic-v3-candidates.json")
    jp = load("jp-north-shortlist.json")
    tw = load("tw-shortlist.json")

    # ---- candidate pool v3 scores ----
    supp = {c["id"]: c for c in cand["candidates"]}
    carried = cand["carried_from_catalog"]
    pool = []
    for c in jp["candidates"] + tw["candidates"]:
        cid = c["id"]
        if cid in carried:
            pool.append({"id": cid, "name_zh": carried[cid]["name_zh"],
                         "catalog_place_id": carried[cid]["catalog_place_id"],
                         "v3": carried[cid]["composite_v3"],
                         "v2_old": c.get("weighted_total"),
                         "source": "catalog(scenic-v3-full)"})
        elif cid in supp:
            s = supp[cid]
            pool.append({"id": cid, "name_zh": s["name_zh"],
                         "catalog_place_id": None, "v3": s["composite_v3"],
                         "v2_old": c.get("weighted_total"),
                         "source": "candidate-supplementary",
                         "visual_0_5": s["visual_0_5"],
                         "cert_tier": s["cert_tier"],
                         "n_valid": s["n_valid"]})
        else:
            pool.append({"id": cid, "name_zh": c["name_i18n"]["zh-TW"],
                         "catalog_place_id": None, "v3": None,
                         "v2_old": c.get("weighted_total"),
                         "source": "unscored"})
    for p in pool:
        p["admits_v3"] = p["v3"] is not None and p["v3"] >= LINE
        p["was_admitted_v2"] = p["v2_old"] is not None and p["v2_old"] >= LINE

    admitted = sorted([p for p in pool if p["admits_v3"]], key=lambda x: -x["v3"])
    dropped = [p for p in pool if p["was_admitted_v2"] and not p["admits_v3"]]
    below_never = [p for p in pool if not p["was_admitted_v2"] and not p["admits_v3"]]
    borderline = [p for p in pool if p["v3"] is not None and LINE - 0.25 <= p["v3"] < LINE]

    # ---- catalog health (218 places by scenic v3) ----
    places = v3full["places"]
    scored = [p["composite_v3"] for p in places if p["composite_v3"] is not None]
    unknown = [p for p in places if p["composite_v3"] is None]
    health = {
        "n_total": len(places), "n_scored": len(scored), "n_unknown": len(unknown),
        "mean": round(statistics.mean(scored), 2), "median": round(statistics.median(scored), 2),
        "buckets": {
            "5.0": sum(1 for s in scored if s == 5),
            "4.5-4.99": sum(1 for s in scored if 4.5 <= s < 5),
            "4.0-4.49": sum(1 for s in scored if 4.0 <= s < 4.5),
            "3.8-3.99": sum(1 for s in scored if LINE <= s < 4.0),
            "3.0-3.79": sum(1 for s in scored if 3.0 <= s < LINE),
            "2.0-2.99": sum(1 for s in scored if 2.0 <= s < 3.0),
            "<2.0": sum(1 for s in scored if s < 2.0),
        },
        "low_list_lt3.8": sorted(
            [{"place_id": p["place_id"], "name_zh": p["name_zh"],
              "v3": p["composite_v3"], "visual": p["visual_0_5"],
              "cert_tier": p["cert_tier"]}
             for p in places if p["composite_v3"] is not None and p["composite_v3"] < LINE],
            key=lambda x: x["v3"]),
        "unknown_list": [p["place_id"] for p in unknown],
    }

    out = {
        "schema": "cl-data-31-redraw/1", "ticket": "CL-DATA-31",
        "rubric": "v3 single-dimension 景色優美 (scenic-v3 composite), v2 five-dimension retired",
        "line": LINE,
        "pool": pool,
        "new_admitted": admitted,
        "dropped": dropped,
        "below_line_never_admitted": below_never,
        "borderline": borderline,
        "catalog_health": health,
    }
    (D / "cl-data-31-rubric-v3-redraw.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # ---- markdown ----
    L = ["# CL-DATA-31 — rubric v3 納入線重劃與 218 景點健康度", "",
         f"> 評分制：景色優美單維度（scenic v3 合成分，0–5，視覺主＋認證階梯±1＋社群±0.5）；"
         f"納入線 composite_v3 ≥ {LINE}。舊五維 rubric（v2）退役。本報告僅產出清單，"
         "不直接增刪景點（決策：PM → owner）。", ""]
    L += [f"## 新納入清單（≥{LINE}，{len(admitted)}）", "",
          "| 候選 | v3 分 | 對應 catalog | 舊 v2 分 |", "|---|---|---|---|"]
    for p in admitted:
        L.append(f"| {p['id']} {p['name_zh']} | {p['v3']} | "
                 f"{p['catalog_place_id'] or '（未入 catalog）'} | {p['v2_old']} |")
    L += ["", f"## 掉線清線清單（舊 v2 ≥3.8、v3 <{LINE}，{len(dropped)}）", "",
          "| 候選 | v3 分 | 對應 catalog | 舊 v2 分 |", "|---|---|---|---|"]
    for p in dropped:
        L.append(f"| {p['id']} {p['name_zh']} | {p['v3']} | "
                 f"{p['catalog_place_id'] or '（未入 catalog）'} | {p['v2_old']} |")
    if borderline:
        L += ["", "## 近線（3.55–3.79，owner 可斟酌）", ""]
        for p in borderline:
            L.append(f"- {p['id']} {p['name_zh']} — v3 {p['v3']}")
    L += ["", "## 本就在線下（舊 v2 <3.8 且 v3 <3.8）", ""]
    for p in below_never:
        L.append(f"- {p['id']} {p['name_zh']} — v3 {p['v3']} / 舊 v2 {p['v2_old']}")
    h = health
    L += ["", "## 既有 218 景點健康度（scenic v3）", "",
          f"- 已評 {h['n_scored']}／218（unknown {h['n_unknown']}：{', '.join(h['unknown_list'])}）",
          f"- 均分 {h['mean']}／中位數 {h['median']}", "",
          "| 分數帶 | 數量 |", "|---|---|"]
    for k, v in h["buckets"].items():
        L.append(f"| {k} | {v} |")
    low = h["low_list_lt3.8"]
    L += ["", f"### 低分清單（v3 < {LINE}，共 {len(low)}，供 owner 裁處置）", "",
          "| place_id | 景點 | v3 | 視覺 | 認證 |", "|---|---|---|---|---|"]
    for p in low:
        L.append(f"| {p['place_id']} | {p['name_zh']} | {p['v3']} | {p['visual']} | {p['cert_tier']} |")
    L += ["", "> 源資料：scenic-v3-full.json（CL-DATA-30）＋ scenic-v3-candidates.json（本票補評 5 候選）。"
          "本工具唯讀 catalog。"]
    (D / "cl-data-31-rubric-v3-redraw.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(json.dumps({"admitted": len(admitted), "dropped": len(dropped),
                      "health": {k: h[k] for k in ("n_scored", "n_unknown", "mean", "median")}},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
