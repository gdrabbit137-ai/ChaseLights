#!/usr/bin/env python3
"""CL-DATA-24 — full-catalog mechanical scoring of every existing place/opportunity.

Reverse sweep of the CL-DATA-23 discovery rubric over the EXISTING catalog:
All catalog places x opportunity contracts, five rubric v2 dimensions
(weights: subject 25 / weather_light 20 / verifiability 20 / differentiation 15 /
scenic_beauty 20 — rubric v2 per CL-DATA-26 owner ruling 2026-11-07 which removed
safe_access), scored MECHANICALLY from in-repo data only (contracts,
place-index, source-lock, seasonal-calendar, evidence registry/audits).
READ-ONLY: this tool never modifies any catalog/contract data; it only writes the
audit report pair. scenic_beauty is judged from in-catalog classification/scoring
evidence (CL-DATA-26 s1/s2/s3 classes); places without evidence are honestly
marked "unknown" (never fabricated).

Dimension definitions (deterministic, no manual input):
  subject_strength          — condition richness of the contract: distinct metrics,
                              QUALITY/BONUS/MODIFIER layer, astro/subject-state family.
  weather_light_dependency  — decisive weather/light model dependency judged from the
                              contract's conditions: light/time windows, astro darkness,
                              seasonal windows, cloud-sea (LCL) family => high; only
                              static scene conditions (precip/AOD/visibility/wind) => low.
  verifiability             — provenance completeness: geometry verification status,
                              evidence_refs, claim_refs/threshold_source, non-placeholder
                              access/safety notes, navigation confidence.
  differentiation           — MECHANICAL 5 km nearest-neighbour between places
                              (haversine over canonical coordinates), CL-DATA-23 bands.
  scenic_beauty             — rubric v2 (CL-DATA-26): base 2 + s1 photo-community
                              (+1) + s2 official A-class/UNESCO/Three-X classification
                              (+1, +1 top-tier bonus) + s3 guide-list frequency >=2
                              independent sources (+1), cap 5; no evidence -> "unknown"

Usage:
  python data/v2/tools/catalog_scoring.py \
      [--outdir data/v2/audits/discovery]
Writes catalog-scoring.json (machine) + catalog-scoring.md (human).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scenic_beauty_v2 import score_scenic_beauty, _load_audit_rows

REPO_ROOT = Path(__file__).resolve().parents[3]
OPP_DIR = REPO_ROOT / "data/v2/opportunities"
PLACE_INDEX = REPO_ROOT / "data/v2/indexes/research/place-index.json"
SOURCE_LOCK = REPO_ROOT / "data/v2/indexes/research/source-lock.json"

WEIGHTS = {
    "subject_strength": 25,
    "weather_light_dependency": 20,
    "verifiability": 20,
    "differentiation": 15,
    "scenic_beauty": 20,  # rubric v2 (CL-DATA-26, owner ruling 2026-11-07): safe_access removed
}

LIGHT_WINDOW_METRICS = {
    "light_window", "sunset_window", "sunrise_time_window",
    "golden_hour_window", "blue_hour_window", "city_night_window",
}
DEEP_NIGHT_METRICS = {
    "astronomical_darkness", "galactic_core_altitude", "moon_altitude",
    "moon_target_separation_deg", "moon_illuminance_proxy",
    "moon_illumination_fraction",
}
SEASON_METRICS = {"seasonal_state"}
CLOUD_SEA_METRICS = {"lcl_height_m_agl", "relative_humidity_925hpa",
                     "relative_humidity_850hpa", "relative_humidity_700hpa",
                     "relative_humidity_600hpa"}
CLOUD_METRICS = {"cloud_cover_mid", "cloud_cover_low", "cloud_cover_total",
                 "cloud_cover_mid_and_high"}
STATIC_METRICS = {"precipitation", "aod_550nm", "visibility", "wind_speed_10m",
                  "wind_speed_850hpa", "wind_speed_600hpa",
                  "temperature_delta_850_925_c", "temperature_delta_700_600_c",
                  "water_surface_state", "landform_present",
                  "legacy_long_exposure", "legacy_reflection",
                  "legacy_mountain_view", "light_direction"}

PLACEHOLDER_MARKS = ("尚未核實", "not yet verified", "未確認", "現場安全指示", "on-site safety guidance", "現場の告知")


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def load_opportunities():
    opps = []
    for f in sorted(OPP_DIR.glob("*.json")):
        opps.append(json.loads(f.read_text(encoding="utf-8")))
    return opps


def region_of(place_id):
    return place_id.split("-", 1)[0]


def score_subject(opp):
    conds = (opp.get("condition_contract") or {}).get("conditions") or []
    metrics = {c.get("metric") for c in conds}
    score = 1
    if len(metrics) >= 2:
        score += 1
    if len(metrics) >= 4:
        score += 1
    if any(c.get("role") in ("QUALITY",) or c.get("condition_tier") in ("BONUS", "MODIFIER")
           for c in conds):
        score += 1
    domains = {c.get("domain") for c in conds}
    if domains & {"ASTRONOMY", "SUBJECT_STATE"}:
        score += 1
    return min(5, score)


def score_weather_light(opp):
    conds = (opp.get("condition_contract") or {}).get("conditions") or []
    decisive = set()
    bonus_window = False
    for c in conds:
        m = c.get("metric")
        if m is None:
            continue
        is_window = (m in LIGHT_WINDOW_METRICS or m in DEEP_NIGHT_METRICS
                     or m in SEASON_METRICS)
        if not is_window:
            continue
        if c.get("role") == "REQUIRED":
            decisive.add(m)
        else:
            bonus_window = True
    if decisive:
        return 5
    req_metrics = {c.get("metric") for c in conds if c.get("role") == "REQUIRED"}
    if req_metrics & CLOUD_SEA_METRICS:
        return 4
    if req_metrics & CLOUD_METRICS:
        return 3
    if bonus_window and (req_metrics & CLOUD_METRICS or req_metrics & CLOUD_SEA_METRICS):
        return 3
    if bonus_window:
        return 2
    # only static scene conditions -> the weather model adds little
    return 2 if len(req_metrics) >= 3 else 1


def _note_is_placeholder(text):
    if not text:
        return True
    return any(mark in text for mark in PLACEHOLDER_MARKS)


def score_verifiability(opp):
    pts = 0.0
    ctxs = opp.get("camera_contexts") or []
    statuses = [c.get("geometry", {}).get("status") for c in ctxs]
    geo_pts = {"verified": 2.0, "derived": 1.5, "provisional": 0.5}.get(
        statuses[0] if statuses else None, 0.0)
    pts += geo_pts
    if any((t.get("evidence_refs") or []) for t in opp.get("targets") or []):
        pts += 1.0
    conds = (opp.get("condition_contract") or {}).get("conditions") or []
    if conds and all((c.get("claim_refs") or []) and c.get("threshold_source")
                     for c in conds):
        pts += 1.0
    if any(c.get("threshold_source") == "evidence_review" for c in conds):
        pts += 0.5
    notes = [c.get("access_notes_i18n", {}).get("zh-TW", "") for c in ctxs]
    if notes and not any(_note_is_placeholder(n) for n in notes):
        pts += 1.0
    navs = opp.get("navigation_targets") or []
    conf = {"high": 0.5, "medium": 0.25}.get(
        (navs[0].get("confidence") if navs else None), 0.0)
    pts += conf
    return round(min(5.0, max(1.0, pts)), 2)


def score_safe_access(opp):
    pts = 0
    ctxs = opp.get("camera_contexts") or []
    access = [c.get("access_notes_i18n", {}).get("zh-TW", "") for c in ctxs]
    safety = [c.get("safety_notes_i18n", {}).get("zh-TW", "") for c in ctxs]
    if access and not any(_note_is_placeholder(n) for n in access):
        pts += 1
    if safety and not any(_note_is_placeholder(n) for n in safety):
        pts += 1
    conds = (opp.get("condition_contract") or {}).get("conditions") or []
    if any(c.get("domain") == "SEASON_TIME" for c in conds):
        pts += 2
    if ctxs and ctxs[0].get("geometry", {}).get("status") == "verified":
        pts += 1
    if any(c.get("altitude_m") is not None for c in ctxs):
        pts += 0.5
    navs = opp.get("navigation_targets") or []
    if navs and navs[0].get("confidence") == "high":
        pts += 0.5
    return round(min(5.0, 1.0 + pts), 2)


def place_coords(opp):
    for cz in opp.get("camera_contexts") or []:
        g = (cz.get("geometry") or {}).get("geojson") or {}
        coords = g.get("coordinates")
        if isinstance(coords, list) and len(coords) == 2:
            return coords[1], coords[0]
    for nav in opp.get("navigation_targets") or []:
        if nav.get("lat") is not None and nav.get("lon") is not None:
            return nav["lat"], nav["lon"]
    return None


def score_differentiation(km):
    if km is None:
        return 3
    if km > 15:
        return 5
    if km > 8:
        return 4
    if km > 5:
        return 3
    return 1


def verify_canonical(source_lock):
    locked = {r["opportunity_id"] for r in source_lock.get("canonical_records", [])}
    return locked


def build_report():
    opps = load_opportunities()
    place_index = json.loads(PLACE_INDEX.read_text(encoding="utf-8"))
    source_lock = json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))
    locked = verify_canonical(source_lock)
    names = {p["place_id"]: p["name_i18n"]["zh-TW"] for p in place_index["places"]}
    names_i18n = {p["place_id"]: p["name_i18n"] for p in place_index["places"]}
    evidence_rows = _load_audit_rows()

    per_opp = {}
    coords = {}
    for opp in opps:
        oid = opp["opportunity_id"]
        pid = opp["place_id"]
        s = {
            "subject_strength": score_subject(opp),
            "weather_light_dependency": score_weather_light(opp),
            "verifiability": score_verifiability(opp),
        }
        if pid not in coords:
            c = place_coords(opp)
            if c:
                coords[pid] = c
        verif_gaps = []
        ctxs = opp.get("camera_contexts") or []
        conds = (opp.get("condition_contract") or {}).get("conditions") or []
        if not ctxs or ctxs[0].get("geometry", {}).get("status") not in ("verified", "derived"):
            verif_gaps.append("geometry_not_verified")
        if not any((t.get("evidence_refs") or []) for t in opp.get("targets") or []):
            verif_gaps.append("targets_missing_evidence_refs")
        if conds and not all((c.get("claim_refs") or []) and c.get("threshold_source")
                             for c in conds):
            verif_gaps.append("conditions_missing_claim_or_threshold_source")
        if ctxs and any(_note_is_placeholder(c.get("access_notes_i18n", {}).get("zh-TW", ""))
                        for c in ctxs):
            verif_gaps.append("access_note_placeholder")
        per_opp[oid] = {
            "place_id": pid, "scores": s, "verif_gaps": verif_gaps,
            "canonical_locked": oid in locked,
            "lifecycle_status": opp.get("lifecycle_status"),
        }

    place_ids = sorted({o["place_id"] for o in opps})
    # place-level differentiation: nearest other place
    nearest = {}
    for a in place_ids:
        if a not in coords:
            nearest[a] = None
            continue
        best = None
        for b in place_ids:
            if b == a or b not in coords:
                continue
            d = haversine_km(coords[a][0], coords[a][1], coords[b][0], coords[b][1])
            if best is None or d < best[1]:
                best = (b, d)
        nearest[a] = best

    places = []
    for pid in place_ids:
        oids = sorted(o for o, v in per_opp.items() if v["place_id"] == pid)
        dims = {k: round(statistics.mean(per_opp[o]["scores"][k] for o in oids), 2)
                for k in WEIGHTS if k != "differentiation" and k != "scenic_beauty"}
        km = nearest[pid][1] if nearest[pid] else None
        dims["differentiation"] = score_differentiation(km)
        sb, sb_detail = score_scenic_beauty(pid, names_i18n.get(pid, {}), opps, evidence_rows)
        if sb is None:
            dims["scenic_beauty"] = "unknown"
        else:
            dims["scenic_beauty"] = sb
        if sb is None:
            weighted = None  # honest: no scenic_beauty evidence -> no fabricated total
        else:
            weighted = round(sum((dims[k] if isinstance(dims[k], (int, float)) else 0)
                                 * w for k, w in WEIGHTS.items())
                             / sum(WEIGHTS.values()), 2)
        places.append({
            "place_id": pid,
            "name_zh": names.get(pid, pid),
            "region": region_of(pid),
            "n_opportunities": len(oids),
            "opportunity_ids": oids,
            "rubric": dims,
            "scenic_beauty_evidence": sb_detail,
            "weighted_total": weighted,
            "nearest_place": nearest[pid][0] if nearest[pid] else None,
            "nearest_km": round(km, 2) if km is not None else None,
            "coords": coords.get(pid),
        })

    ranked = sorted(places, key=lambda p: (-(p["weighted_total"] if p["weighted_total"] is not None else -1),
                                           p["place_id"]))
    totals = [p["weighted_total"] for p in ranked if p["weighted_total"] is not None]
    by_region = {}
    for p in ranked:
        by_region.setdefault(p["region"], []).append(p)

    # 5 km clusters (connected components over pairs <= 5 km)
    parent = {p: p for p in place_ids}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, a in enumerate(place_ids):
        for b in place_ids[i + 1:]:
            if a in coords and b in coords:
                if haversine_km(*coords[a], *coords[b]) <= 5.0:
                    ra, rb = find(a), find(b)
                    if ra != rb:
                        parent[rb] = ra
    groups = {}
    for p in place_ids:
        groups.setdefault(find(p), []).append(p)
    clusters = []
    place_by_id = {p["place_id"]: p for p in places}
    for members in groups.values():
        if len(members) >= 2:
            clusters.append({
                "members": [{"place_id": m, "name_zh": place_by_id[m]["name_zh"],
                             "nearest_km": place_by_id[m]["nearest_km"]}
                            for m in sorted(members)],
            })

    opps_out = []
    for oid in sorted(per_opp):
        v = per_opp[oid]
        opps_out.append({"opportunity_id": oid, **v})

    low_wl = sorted(
        (o for o in opps_out if o["scores"]["weather_light_dependency"] <= 2),
        key=lambda o: o["opportunity_id"])
    low_verif = sorted(
        (o for o in opps_out if o["scores"]["verifiability"] <= 2.0),
        key=lambda o: o["opportunity_id"])

    # determinism fingerprint over inputs (not wall-clock)
    h = hashlib.sha256()
    for f in sorted(OPP_DIR.glob("*.json")):
        h.update(f.name.encode())
        h.update(f.read_bytes())
    h.update(PLACE_INDEX.read_bytes())
    h.update(SOURCE_LOCK.read_bytes())

    return {
        "schema_version": "cl-data-24-catalog-scoring-2",
        "ticket": "CL-DATA-24 (re-run CL-DATA-25R, rubric v2)",
        "rubric_version": "v2 (CL-DATA-26 owner ruling 2026-11-07: safe_access removed, scenic_beauty 20; honest unknown when no evidence)",
        "rubric_weights": WEIGHTS,
        "inputs_fingerprint_sha256": h.hexdigest(),
        "summary": {
            "places": len(places),
            "opportunities": len(opps_out),
            "canonical_locked_opportunities": sum(1 for o in opps_out if o["canonical_locked"]),
            "places_with_unknown_scenic_beauty": sum(1 for p in places if p["rubric"]["scenic_beauty"] == "unknown"),
            "mean_weighted_total": round(statistics.mean(totals), 2) if totals else None,
            "median_weighted_total": round(statistics.median(totals), 2) if totals else None,
            "mean_basis": "places with evidenced scenic_beauty only (rubric v2 honest-unknown rule)",
            "region_counts": {r: len(v) for r, v in sorted(by_region.items())},
            "weakness_counts": {
                "low_weather_light_opportunities": len(low_wl),
                "low_verifiability_opportunities": len(low_verif),
                "clusters_within_5km": len(clusters),
            },
        },
        "ranking": ranked,
        "opportunity_scores": opps_out,
        "weakness_lists": {
            "low_weather_light": [
                {"opportunity_id": o["opportunity_id"], "place_id": o["place_id"],
                 "score": o["scores"]["weather_light_dependency"],
                 "recommendation": "改題材"}
                for o in low_wl],
            "low_verifiability": [
                {"opportunity_id": o["opportunity_id"], "place_id": o["place_id"],
                 "score": o["scores"]["verifiability"],
                 "gaps": o["verif_gaps"], "recommendation": "補資料"}
                for o in low_verif],
            "clusters_within_5km": [
                {**c,
                 "recommendation": "高重叠區：檢討題材差異化或候選裁撤（評估合併/裁撤，僅建議）"}
                for c in clusters],
        },
    }


def render_md(rep):
    s = rep["summary"]
    lines = [
        "# CL-DATA-24 全庫景點機械評分（catalog scoring）",
        "",
        f"評分範圍：{s['places']} places × {s['opportunities']} opportunities（全數來自庫內契約；唯讀分析）。",
        f"Rubric 權重（v2）：subject 25 / weather_light 20 / verifiability 20 / differentiation 15 / scenic_beauty 20（CL-DATA-26 owner ruling 2026-11-07：safe_access 移除、scenic_beauty 20）。",
        f"輸入指紋：`{rep['inputs_fingerprint_sha256'][:16]}…`（重跑可驗證確定性）。",
        "",
        f"- 全庫加權均分：**{s['mean_weighted_total']} / 5**；中位數：**{s['median_weighted_total']} / 5**（僅計 scenic_beauty 有庫內證據的景點；"
        f"scenic_beauty 無證據者誠實標 unknown＝**{s['places_with_unknown_scenic_beauty']}** 個，不虛構分數）。",
        f"- 區域分布：{', '.join(f'{r}={n}' for r, n in s['region_counts'].items())}",
        f"- 弱點清單筆數：低 weather_light **{s['weakness_counts']['low_weather_light_opportunities']}**、"
        f"低 verifiability **{s['weakness_counts']['low_verifiability_opportunities']}**、"
        f"5km 群聚 **{s['weakness_counts']['clusters_within_5km']}**。",
        "",
        "## 五維判定規則（機械、可重跑）",
        "",
        "| 維度 | 判定 |",
        "|---|---|",
        "| subject_strength | 契約條件豐富度：≥2 指標 +1、≥4 +1、有 QUALITY/BONUS/MODIFIER +1、天文/題材狀態 family +1 |",
        "| weather_light | 光線/時間窗（light/sunset/sunrise/golden/blue/夜間窗）＝5；深夜天文組＝5；季節窗＝5；雲海 LCL 組 REQUIRED＝4；雲量主導＝3；僅靜態地景條件＝1–2 |",
        "| verifiability | provenance 完整度：geometry verified/derived、targets evidence_refs、claim_refs+threshold_source、access/safety 非佔位、navigation confidence |",
        "| differentiation | 機械 5km 最近鄰（>15→5、>8→4、>5→3、≤5→1） |",
        "| scenic_beauty (v2) | 庫內分類/評分證據機械判定：base 2 + s1 攝影社群(+1) + s2 官方A級/UNESCO/三大類分類(+1，頂級＋1) + s3 攻略清單頻率≥2獨立來源(+1)，上限 5；無證據＝unknown（不虛構） |",
        "",
        "## 排名（前 20 / 後 20）",
        "",
        "### Top 20",
        "",
        "| 排名 | place | 名稱 | 區域 | 題材數 | 加權總分 | 五維 |",
        "|---|---|---|---|---|---|---|",
    ]
    for i, p in enumerate(rep["ranking"][:20], 1):
        r = p["rubric"]
        lines.append(
            f"| {i} | `{p['place_id']}` | {p['name_zh']} | {p['region']} | "
            f"{p['n_opportunities']} | **{p['weighted_total']}** | "
            f"{r['subject_strength']}/{r['weather_light_dependency']}/"
            f"{r['verifiability']}/{r['differentiation']}/{r['scenic_beauty']} |")
    lines += ["", "### Bottom 20", "",
              "| 排名 | place | 名稱 | 區域 | 題材數 | 加權總分 | 五維 | 最近景點 (km) |",
              "|---|---|---|---|---|---|---|---|"]
    for i, p in enumerate(rep["ranking"][-20:], len(rep["ranking"]) - 19):
        r = p["rubric"]
        lines.append(
            f"| {i} | `{p['place_id']}` | {p['name_zh']} | {p['region']} | "
            f"{p['n_opportunities']} | **{p['weighted_total']}** | "
            f"{r['subject_strength']}/{r['weather_light_dependency']}/"
            f"{r['verifiability']}/{r['differentiation']}/{r['scenic_beauty']} | "
            f"{p['nearest_place']} ({p['nearest_km']}) |")

    wl = rep["weakness_lists"]
    lines += ["", "## 弱點清單 A：低 weather_light（模型幫不上忙的景點 → 建議改題材）", "",
              "| opportunity | place | 分數 |", "|---|---|---|"]
    for o in wl["low_weather_light"]:
        lines.append(f"| `{o['opportunity_id']}` | {o['place_id']} | {o['score']} |")
    lines += ["", "## 弱點清單 B：低 verifiability（資料缺口 → 建議補資料）", "",
              "| opportunity | place | 分數 | 缺口 |", "|---|---|---|---|"]
    for o in wl["low_verifiability"]:
        lines.append(f"| `{o['opportunity_id']}` | {o['place_id']} | {o['score']} | "
                     f"{', '.join(o['gaps']) or '—'} |")
    lines += ["", "## 弱點清單 C：高重叠區（5km 群聚 → 檢討差異化/候選裁撤，僅建議）", ""]
    for c in wl["clusters_within_5km"]:
        ms = "、".join(f"{m['name_zh']}（{m['place_id']}，最近 {m['nearest_km']} km）"
                       for m in c["members"])
        lines.append(f"- {ms}")
    lines += ["",
              "> Rubric v2（CL-DATA-25R 重跑）：safe_access 權重移除、scenic_beauty 權重 20，由庫內證據機械判定；"
              "scenic_beauty 無證據的景點誠實標 unknown，其加權總分留空（不虛構）。季節窗/封閉期資訊仍保留於 dossier 與契約。\n"
              "> 本報告為唯讀分析：不改任何 catalog/契約資料；弱點處置（改題材/補資料/裁撤）"
              "為建議，決策權在 PM/owner。機器可讀版本：catalog-scoring.json。"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="data/v2/audits/discovery")
    args = ap.parse_args(argv)
    rep = build_report()
    outdir = REPO_ROOT / args.outdir
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "catalog-scoring.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=1, sort_keys=False) + "\n",
        encoding="utf-8")
    (outdir / "catalog-scoring.md").write_text(render_md(rep), encoding="utf-8")
    s = rep["summary"]
    print(json.dumps({"places": s["places"], "opportunities": s["opportunities"],
                      "mean": s["mean_weighted_total"], "median": s["median_weighted_total"],
                      "low_wl": s["weakness_counts"]["low_weather_light_opportunities"],
                      "low_verif": s["weakness_counts"]["low_verifiability_opportunities"],
                      "clusters": s["weakness_counts"]["clusters_within_5km"],
                      "top3": [f"{p['place_id']} {p['name_zh']} {p['weighted_total']}"
                               for p in rep["ranking"][:3]],
                      "bottom3": [f"{p['place_id']} {p['name_zh']} {p['weighted_total']}"
                                  for p in rep["ranking"][-3:]]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
