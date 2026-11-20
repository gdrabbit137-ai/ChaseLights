"""CL-DATA-81 — contract edits driver (three owner-ruled stages; jp-002-022 name translations moved OUT to a separate metadata ticket per owner ruling 2026-11-20).

1. Sea-view sunrise visibility gate (jp-008-P01 / tw-072-P01 / tw-075-P01):
   add REQUIRED visibility >= 15 km + REQUIRED aod_550nm <= 0.4, aligned with
   the Longpan/Suwa family (sea-fog / haze interception), trilingual rationale.
2. Star-contract moonlight dedup (34 contracts): remove the legacy REQUIRED
   moon_illumination_fraction <= 0.5 entry. Root cause: the night template's
   base-layer moon gate (M1) survived CL-DATA-75 Phase 0, which added the
   owner §1.2 track-2 gate (<= 0.25) without removing M1 — the migration/
   phase-0 double entry. The evaluator's M2/M3 alternation makes M1 fully
   dominated (moon-down passes outright; moon-up 0.25–0.5 fails track 2),
   so removal is semantics-preserving under the official evaluator and
   matches the owner-ruled any_of gate (moon below horizon OR (dim AND far)).
3. Weakness-list dispositions live in a separate stage (see audit report).
4. jp-002–jp-022 subject-name en/ja translations (20 records whose en/ja
   still carried the zh-TW string): web-verified landscape identities
   (Matsushima/Sōkanyama, Nakasenuma+Bandai, Yasumiya/Lake Towada,
   Hosooka/Kushiro, Sugatami/Asahidake, Bentenjima/Lake Hamana,
   Nishi-Hodaka ropeway stargazing, Yahiko/Echigo Plain).

Writes LF bytes (repo convention). Idempotent: re-running a stage that is
already applied is a no-op.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OPP = ROOT / "data/v2/opportunities"

VIS_AOD: dict[str, dict] = {
    "jp-008-P01": {
        "claim": "jp-008-P01-claim-01",
        "vis_rat": {
            "zh-TW": "面向海平線的松島灣朝日需要通透空氣：能見度 ≥15 km，海霧或霧霾吞掉灣內群島與金華山方向輪廓時直接否決（龍磐/諏訪湖同族標準值）。",
            "en": "A sunrise over Matsushima Bay needs transparent air: visibility >= 15 km; sea fog or haze that swallows the islands and the Kinkasan horizon vetoes the hour outright (Longpan/Suwa family standard).",
            "ja": "松島湾の朝日には透明な空気が要る：視程≥15 km。海霧やヘイズが湾内の島々と金華山方面の輪郭を飲み込む場合は否決（龍磐・諏訪湖と同族の標準値）。",
        },
        "aod_rat": {
            "zh-TW": "遠眺群島型地景需要高透明度：AOD ≤0.4，霧霾把松島群島糊化、只剩近島剪影時否決（遠景地景沿用已審門檻）。",
            "en": "A distant-archipelago vista needs high transparency: AOD <= 0.4; haze that blurs the Matsushima islands into near-shore silhouettes vetoes the hour (carried-over far-view threshold).",
            "ja": "島々の遠景には高い透明度が要る：AOD≤0.4。ヘイズで松島の島々がぼやけ、近景のシルエットしか見えない場合は否決（遠景地景の既審閾値を踏襲）。",
        },
    },
    "tw-072-P01": {
        "claim": "tw-072-P01-claim-01",
        "vis_rat": {
            "zh-TW": "面向海平線的南雅奇岩日出需要通透空氣：能見度 ≥15 km，海霧或霧霾吞掉海平線與基隆嶼輪廓時直接否決（龍磐/諏訪湖同族標準值）。",
            "en": "A sunrise facing the sea horizon at Nanya Rock needs transparent air: visibility >= 15 km; sea fog or haze that swallows the horizon and Keelung Islet vetoes the hour outright (Longpan/Suwa family standard).",
            "ja": "南雅奇岩の海平線を望む日の出には透明な空気が要る：視程≥15 km。海霧やヘイズが海平線と基隆嶼の輪郭を飲み込む場合は否決（龍磐・諏訪湖と同族の標準値）。",
        },
        "aod_rat": {
            "zh-TW": "奇岩地景層次需要高透明度：AOD ≤0.4，霧霾把風化紋理與遠處海岸線糊化時否決（遠景地景沿用已審門檻）。",
            "en": "The layered weathering textures need high transparency: AOD <= 0.4; haze that blurs the rock textures and the distant coastline vetoes the hour (carried-over far-view threshold).",
            "ja": "奇岩の風化模様の層次には高い透明度が要る：AOD≤0.4。ヘイズで岩のテクスチャと遠い海岸線がぼやける場合は否決（遠景地景の既審閾値を踏襲）。",
        },
    },
    "tw-075-P01": {
        "claim": "tw-075-P01-claim-01",
        "vis_rat": {
            "zh-TW": "海上日出與龜山島輪廓需要通透空氣：能見度 ≥15 km，海霧或霧霾吞掉海平線與龜山島剪影時直接否決（龍磐/諏訪湖同族標準值）。",
            "en": "A sunrise over the sea with Guishan Island in view needs transparent air: visibility >= 15 km; sea fog or haze that swallows the horizon and the island silhouette vetoes the hour outright (Longpan/Suwa family standard).",
            "ja": "海の日の出と亀山島の輪郭には透明な空気が要る：視程≥15 km。海霧やヘイズが海平線と亀山島のシルエットを飲み込む場合は否決（龍磐・諏訪湖と同族の標準値）。",
        },
        "aod_rat": {
            "zh-TW": "遠眺龜山島需要高透明度：AOD ≤0.4，霧霾把島影糊化成灰塊時否決（遠景地景沿用已審門檻）。",
            "en": "A distant view of Guishan Island needs high transparency: AOD <= 0.4; haze that blurs the island into a grey block vetoes the hour (carried-over far-view threshold).",
            "ja": "亀山島の遠望には高い透明度が要る：AOD≤0.4。ヘイズで島影が灰色の塊にぼやける場合は否決（遠景地景の既審閾値を踏襲）。",
        },
    },
}

NOTE_VIS = {
    "zh-TW": "2026-11-20 CL-DATA-81（owner 指示）：海景日出補能見度必須 ≥15 km＋AOD ≤0.4，與龍磐/諏訪湖同族對齊（海霧/霧霾攔截）。",
    "en": "2026-11-20 CL-DATA-81 (owner directive): sea-view sunrise gains REQUIRED visibility >= 15 km + AOD <= 0.4, aligned with the Longpan/Suwa family (sea-fog/haze interception).",
    "ja": "2026-11-20 CL-DATA-81（オーナー指示）：海景日の出に視程≥15 km＋AOD≤0.4の必須条件を追加。龍磐・諏訪湖と同族で整合（海霧・ヘイズ遮断）。",
}



def load(oid: str) -> dict:
    return json.loads((OPP / f"{oid}.json").read_text(encoding="utf-8"))


def save(d: dict) -> None:
    (OPP / f"{d['opportunity_id']}.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def next_cond_index(conds: list[dict], oid: str) -> int:
    prefix = f"C-{oid}-"
    nums = [int(c["id"].removeprefix(prefix)) for c in conds]
    return max(nums) + 1


def add_visibility_aod(d: dict) -> list[str]:
    spec = VIS_AOD[d["opportunity_id"]]
    cc = d["condition_contract"]
    conds = cc["conditions"]
    metrics = [c["metric"] for c in conds]
    changed = []
    if "visibility" not in metrics:
        idx = next_cond_index(conds, d["opportunity_id"])
        conds.append({
            "id": f"C-{d['opportunity_id']}-{idx:02d}",
            "role": "REQUIRED",
            "domain": "WEATHER",
            "evaluation_mode": "GUIDANCE",
            "capability": "CONDITIONS",
            "metric": "visibility",
            "operator": "gte",
            "threshold": 15,
            "unit": "km",
            "unknown_policy": "propagate_unknown",
            "claim_refs": [spec["claim"]],
            "model_binding": "dataset:gfs_0p25|field:visibility_km|role:MID",
            "validation_status": "provisional",
            "condition_tier": "MAIN",
            "threshold_source": "formula_derived",
            "calibration_status": "provisional",
            "rationale_i18n": spec["vis_rat"],
            "notes_i18n": NOTE_VIS,
        })
        cc.setdefault("conditions_v2", {}).setdefault("required", []).append(
            {"id": f"C-{d['opportunity_id']}-{idx:02d}", "metric": "visibility",
             "op": "gte", "value": 15})
        changed.append("visibility_gte_15")
    if "aod_550nm" not in metrics:
        idx = next_cond_index(conds, d["opportunity_id"])
        conds.append({
            "id": f"C-{d['opportunity_id']}-{idx:02d}",
            "role": "REQUIRED",
            "domain": "WEATHER",
            "evaluation_mode": "GUIDANCE",
            "capability": "CONDITIONS",
            "metric": "aod_550nm",
            "operator": "lte",
            "threshold": 0.4,
            "unit": None,
            "unknown_policy": "propagate_unknown",
            "claim_refs": [spec["claim"]],
            "model_binding": "dataset:cams_global|field:aerosol_optical_depth_550nm|role:AEROSOL",
            "validation_status": "provisional",
            "condition_tier": "MAIN",
            "threshold_source": "formula_derived",
            "calibration_status": "provisional",
            "rationale_i18n": spec["aod_rat"],
            "notes_i18n": NOTE_VIS,
        })
        cc.setdefault("conditions_v2", {}).setdefault("required", []).append(
            {"id": f"C-{d['opportunity_id']}-{idx:02d}", "metric": "aod_550nm",
             "op": "lte", "value": 0.4})
        changed.append("aod_lte_04")
    return changed


def dedup_moon(d: dict) -> list[str]:
    cc = d["condition_contract"]
    conds = cc["conditions"]
    dupes = [c for c in conds
             if c["metric"] == "moon_illumination_fraction"
             and c.get("role") == "REQUIRED" and c.get("threshold") == 0.5]
    if not dupes:
        return []
    ids = {c["id"] for c in dupes}
    cc["conditions"] = [c for c in conds if c["id"] not in ids]
    v2 = cc.get("conditions_v2") or {}
    for group in ("required", "quality"):
        if group in v2:
            v2[group] = [n for n in v2[group] if n.get("id") not in ids]
    return sorted(ids)


def main() -> int:
    stats = {"vis_aod": {}, "moon_dedup": {}, }
    # stage 1 + note
    for oid in VIS_AOD:
        d = load(oid)
        changed = add_visibility_aod(d)
        if changed:
            save(d)
        stats["vis_aod"][oid] = changed
    # stage 2 + note (all non-blue-tears contracts with the double entry)
    for path in sorted(OPP.glob("*.json")):
        d = json.loads(path.read_text(encoding="utf-8"))
        if d.get("lifecycle_status") == "retired":
            continue
        cc = d.get("condition_contract") or {}
        m1 = [c for c in cc.get("conditions", [])
              if c["metric"] == "moon_illumination_fraction"
              and c.get("role") == "REQUIRED" and c.get("threshold") == 0.5]
        track2 = [c for c in cc.get("conditions", [])
                  if c["metric"] == "moon_illumination_fraction"
                  and c.get("role") == "REQUIRED" and c.get("threshold") == 0.25]
        # only contracts that carry BOTH the legacy gate and the owner track-2
        if not (m1 and track2):
            continue
        ids = dedup_moon(d)
        if ids:
            d["revision"] = int(d.get("revision") or 1) + 1
            save(d)
            stats["moon_dedup"][d["opportunity_id"]] = ids
    print(json.dumps(stats, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
