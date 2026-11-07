#!/usr/bin/env python3
"""CL-DATA-30: finalize scenic-v3 full-catalog composite scores.

Inputs:
  progress.json stage_photos + stage_community
  scratch/d30_vision/*.json  (visual layer: per-montage sub-scores + INVALID marks)
  scratch/cl27_results.json  (pilot visual layer, carried over verbatim)
  data/v2/tools/scenic_v3_cert_ladder.json
Composite (CL-DATA-27/29 method):
  visual_0_5 = median of per-photo means when n>=2 valid photos, else mean (n==1), else None
  cert_adj   = clamp(tier - visual_0_5, -1, +1)      (±1, vision-primary)
  community  = +0.5 any Commons badge (Featured/Quality/Valued/POTD) on a valid photo;
               else +0.25 if a valid photo has >=5000 views/90d;
               else -0.25 if no badge AND all valid-photo pageviews < 50; else 0   (±0.5)
  composite  = clip(visual_0_5 + cert_adj + community, 0, 5), round 2dp
  visual None -> composite unknown (honest blank)
"""
from __future__ import annotations
import json, statistics, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PROG = REPO / "data/v2/audits/discovery/scenic-v3-full-progress.json"
SCRATCH = Path("C:/Users/Dick_/AppData/Local/hermes/profiles/chaselights_manager/cache/scratch")
CERT = json.loads((REPO / "data/v2/tools/scenic_v3_cert_ladder.json").read_text(encoding="utf-8"))["tiers"]
PILOT = json.loads((SCRATCH / "cl27_results.json").read_text(encoding="utf-8"))
SCORING = json.loads((REPO / "data/v2/audits/discovery/catalog-scoring.json").read_text(encoding="utf-8"))

def clip(x, lo, hi):
    return max(lo, min(hi, x))

def community_adj(photos, comm):
    """Owner correction (CL-DATA-29 validation): badges only on representative-passing
    photos; negative correction ONLY when the place has a COMPLETE badge inventory
    (every valid photo formally checked against Quality/Featured/Popular/PotD cats)
    AND every pageview payload present; magnitude ±0.25."""
    any_badge, any_highpv, has = False, False, False
    inv_complete, payload_missing, all_lowpv = True, False, True
    for p in photos:
        if not p.get("_valid"):
            continue
        c = comm.get(p["key"])
        if not c:
            inv_complete = False  # valid photo not inventoried -> no negative branch
            continue
        has = True
        if "badges" not in c:
            inv_complete = False
        elif c["badges"]:
            any_badge = True
        pv = c.get("pv12mo")
        if pv is None:
            payload_missing = True  # unknown, never counted as 0
        else:
            if pv >= 5000:
                any_highpv = True
            if pv >= 50:
                all_lowpv = False
    if not has:
        return 0, "無社群信號資料"
    if any_badge:
        return 0.5, "Commons 社群標章（Featured/Quality/Valued/Popular/PotD，代表性篩選通過照片）"
    if any_highpv:
        return 0.25, "檔案頁12個月瀏覽≥5000"
    if inv_complete and not payload_missing and all_lowpv:
        return -0.25, "完整標章盤點無標章且12個月瀏覽均<50（社群關注低）"
    return 0, "無標章、瀏覽量普通或資料不完整（不負向校正）"

def main():
    prog = json.loads(PROG.read_text(encoding="utf-8"))
    photos_stage = prog["stage_photos"]
    comm = prog.get("stage_community", {})
    # vision layer from montage batches
    vision = {}
    for f in sorted((SCRATCH / "d30_vision").glob("*.json")):
        vision.update(json.loads(f.read_text(encoding="utf-8")))
    mapping = json.loads((SCRATCH / "d30_montages" / "mapping.json").read_text(encoding="utf-8"))
    pilot_by_id = {p["place_id"]: p for p in PILOT}

    results = []
    for pid, entry in photos_stage.items():
        photos = entry.get("photos") or []
        # attach valid + subs
        if pid in pilot_by_id:
            p = pilot_by_id[pid]
            pl = []
            for ph in p["photos"]:
                lab = ph.get("label")
                key = ph.get("title") or ph.get("url")
                pl.append({**ph, "key": key, "label": lab,
                           "_valid": ph.get("valid", True),
                           "_subs": ph.get("sub_scores"), "_note": ""})
            visual10 = p.get("visual_median10")
        else:
            pl = []
            vis_scores = (vision.get(pid) or {})
            for i, ph in enumerate(photos):
                lab = chr(65 + i)
                v = vis_scores.get(lab, {})
                key = ph.get("title") or ph.get("url") or ""
                pl.append({**ph, "key": key, "label": lab,
                           "_valid": v.get("valid", False),
                           "_subs": v.get("subs"), "_note": v.get("note", ""),
                           "_reason": v.get("reason", "")})
            means = [sum(x["_subs"]) / 4 for x in pl if x["_valid"] and x["_subs"]]
            if len(means) >= 2:
                visual10 = statistics.median(means)
            elif len(means) == 1:
                visual10 = means[0]
            else:
                visual10 = None
            for x in pl:
                x["_photo_mean"] = round(sum(x["_subs"]) / 4, 2) if x["_subs"] and x["_valid"] else None
        n_valid = sum(1 for x in pl if x["_valid"])
        visual_0_5 = round(visual10 / 2, 2) if visual10 is not None else None
        tier, cert_ev = CERT.get(pid, [None, "查無證據（unknown）"])
        cadj, cev = community_adj(pl, comm)
        if visual_0_5 is None:
            comp = None
            why = "unknown：無有效代表照片" + ("" if tier is None else "（有認證但無視覺信號，不虛構分數）")
            cert_adj = 0.0
        else:
            cert_adj = clip(tier - visual_0_5, -1, 1)
            comp = round(clip(visual_0_5 + cert_adj + cadj, 0, 5), 2)
            why = f"視覺{visual_0_5}＋認證校正{round(cert_adj,2)}＋社群{cadj}"
        results.append({
            "place_id": pid, "name_zh": entry.get("name"),
            "photos": pl, "n_photos_fetched": len(photos), "n_valid": n_valid,
            "sources": entry.get("sources_tried"),
            "visual_0_5": visual_0_5,
            "cert_tier": tier, "cert_evidence": cert_ev,
            "community_adj": cadj, "community_evidence": cev,
            "composite_v3": comp, "composite_formula": why,
            "v2_weighted_total": next((r.get("weighted_total") for r in SCORING["ranking"] if r["place_id"] == pid), None),
        })

    done = [r for r in results if r["composite_v3"] is not None]
    unknown = [r for r in results if r["composite_v3"] is None]
    scores = sorted(r["composite_v3"] for r in done)
    import statistics as st
    summary = {
        "n_total": len(results), "n_scored": len(done), "n_unknown": len(unknown),
        "mean": round(st.mean(scores), 2) if scores else None,
        "median": round(st.median(scores), 2) if scores else None,
        "top10": sorted(done, key=lambda r: -r["composite_v3"])[:10],
        "bottom10": sorted(done, key=lambda r: r["composite_v3"])[:10],
    }
    out = {"schema": "scenic-v3-full/1", "ticket": "CL-DATA-30",
           "method": {"visual": "多源照片（Commons search/langlinks/Openverse）→代表性篩選→四子項1–10（n≥2取中位數、n=1取均值）÷2",
                      "cert": "認證階梯±1（5=UNESCO/國際、4=國家級官方、3=多攻略共識、2=一般）",
                      "community": "Commons 標章/瀏覽量 ±0.5（視覺為主）",
                      "composite": "visual_0_5 + clamp(tier−visual,−1,+1) + community ±0.5，clip 0–5"},
           "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "summary": summary, "places": results}
    (REPO / "data/v2/audits/discovery/scenic-v3-full.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("top10", "bottom10")}, ensure_ascii=False))
    print("TOP10:", [(r["place_id"], r["name_zh"], r["composite_v3"]) for r in summary["top10"]])
    print("BOTTOM10:", [(r["place_id"], r["name_zh"], r["composite_v3"]) for r in summary["bottom10"]])
    print("UNKNOWN:", [r["place_id"] for r in unknown])
    write_md(out, summary, results, unknown)

def write_md(out, summary, results, unknown):
    L = ["# CL-DATA-30 景色優美評分 v3 全庫報告（218 景點）", "",
         "Owner 裁決「直接跑全庫」。方法沿用 CL-DATA-27/28/29：",
         "- 多源抓照（Wikimedia Commons 搜尋＋Wikipedia 語言連結＋Openverse，每點目標 3–6 張）",
         "- 代表性篩選（標題黑名單前置＋視覺複核 INVALID 標註，n≥2 取中位數、n=1 取均值）",
         "- 視覺評分四子項 1–10：地貌獨特性／構圖層次／光影天氣戲劇性／色彩，÷2 換算 0–5",
         "- 社群信號（修正版）：標章僅採計通過代表性篩選照片（+0.5）；檔案頁 12 個月瀏覽 ≥5000（+0.25）；負向 −0.25 僅在逐景點完成完整標章盤點（Quality/Featured/Popular/PotD 類別正式交集）且瀏覽 payload 完整時才可扣；缺 payload 一律 unknown 不計 0",
         "- 認證階梯 ±1（5=UNESCO/國際、4=國家級官方、3=多攻略共識、2=一般）",
         "- 合成分 = 視覺0–5 ＋ clamp(認證−視覺, ±1) ＋ 社群，clip 0–5；無有效照片 → 誠實 unknown",
         "",
         f"統計：{summary['n_scored']}/{summary['n_total']} 已評分，均分 {summary['mean']}，中位數 {summary['median']}，unknown {summary['n_unknown']}。", "",
         "## Top 10", "", "| 名次 | id | 景點 | v3 | v2 | 視覺 | 認證 | 社群 |", "|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(summary["top10"], 1):
        L.append(f"| {i} | {r['place_id']} | {r['name_zh']} | **{r['composite_v3']}** | {r['v2_weighted_total'] or '—'} | {r['visual_0_5']} | {r['cert_tier']} | {'+' if r['community_adj']>0 else ''}{r['community_adj']} |")
    L += ["", "## Bottom 10", "", "| 名次 | id | 景點 | v3 | v2 | 視覺 | 認證 | 社群 |", "|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(summary["bottom10"], 1):
        L.append(f"| {i} | {r['place_id']} | {r['name_zh']} | **{r['composite_v3']}** | {r['v2_weighted_total'] or '—'} | {r['visual_0_5']} | {r['cert_tier']} | {'+' if r['community_adj']>0 else ''}{r['community_adj']} |")
    if unknown:
        L += ["", f"## Unknown（{len(unknown)} 點，誠實標註）", "", "| id | 景點 | 抓到照片 | 有效照片 | 認證 |", "|---|---|---|---|---|"]
        for r in unknown:
            L.append(f"| {r['place_id']} | {r['name_zh']} | {r['n_photos_fetched']} | {r['n_valid']} | {r['cert_tier'] or 'unknown'} |")
    L += ["", "## 逐景點明細", ""]
    for r in results:
        L.append(f"### {r['place_id']} {r['name_zh']} — v3 **{r['composite_v3'] if r['composite_v3'] is not None else 'unknown'}**（v2: {r['v2_weighted_total'] or 'new'}，視覺 {r['visual_0_5']}，認證 {r['cert_tier']}，社群 {r['community_adj']:+}）")
        L.append(f"- 認證依據：{r['cert_evidence']}")
        L.append(f"- 合成：{r['composite_formula']}；社群：{r['community_evidence']}")
        L.append(f"- 照片來源：{', '.join(r['sources'] or [])}；抓到 {r['n_photos_fetched']} 張，有效 {r['n_valid']} 張")
        for i, ph in enumerate(r["photos"]):
            lab = chr(65 + i)
            if ph.get("_valid"):
                L.append(f"- {lab}：子項 {ph.get('_subs')} 均分 {ph.get('_photo_mean')} — {ph.get('title')}（{ph.get('source')}）{('〈' + ph['_note'] + '〉') if ph.get('_note') else ''}")
            else:
                reason = ph.get("_reason") or "非風景代表照"
                L.append(f"- {lab}：INVALID（{reason}）— {ph.get('title')}")
        L.append("")
    (REPO / "data/v2/audits/discovery/scenic-v3-full.md").write_text("\n".join(L), encoding="utf-8")
    print("md written", len(L), "lines")

if __name__ == "__main__":
    main()
