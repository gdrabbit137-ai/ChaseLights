#!/usr/bin/env python3
"""CL-DATA-71 one-shot: append cloud_base_height conditions to audited contracts.

Run from the worktree root. Idempotent (skips contracts that already carry a
cloud_base_height condition). Serialization is per-file round-trip preserving
(indent, newline, trailing-newline) so diffs stay minimal.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OPP = ROOT / "data/v2/opportunities"

# oid -> (mode, threshold, elev_m, elev_source)
#   mode "band"    = catalog-recorded band (evidence_review)
#   mode "derived" = DEM-200 fallback (computed); elev_m used for the notes
PLAN = {
    "tw-128-P01": ("band", [50, 120], 157.0,
                   "camera_context web-verified altitude_m 157 m"),
    "tw-145-P01": ("derived", None, 305.0,
                   "catalog DEM (V1 spot catalog api_elevation) 305 m"),
    "tw-148-P01": ("derived", None, 401.0,
                   "catalog DEM (V1 spot catalog api_elevation) 401 m"),
    "tw-163-P01": ("derived", None, 418.0,
                   "catalog DEM (V1 spot catalog api_elevation) 418 m"),
    "tw-179-P01": ("derived", None, 253.0,
                   "catalog DEM (V1 spot catalog api_elevation) 253 m"),
    "tw-035-P06": ("derived", None, 944.0,
                   "catalog DEM (V1 spot catalog api_elevation) 944 m"),
    "tw-043-P02": ("derived", None, 3560.0,
                   "catalog DEM (V1 spot catalog api_elevation) 3560 m"),
    "tw-047-P01": ("derived", None, 3092.0,
                   "catalog DEM (V1 spot catalog api_elevation) 3092 m"),
    "tw-047-P02": ("derived", None, 3092.0,
                   "catalog DEM (V1 spot catalog api_elevation) 3092 m"),
    "tw-049-P03": ("derived", None, 3325.0,
                   "catalog DEM (V1 spot catalog api_elevation) 3325 m"),
    "jp-037-P02": ("derived", None, 1088.0,
                   "camera_context web-verified altitude_m 1088 m"),
    "us-087-P01": ("derived", None, 1590.0,
                   "catalog DEM (V1 spot catalog api_elevation) 1590 m"),
    "us-113-P01": ("derived", None, 3055.0,
                   "camera_context web-verified altitude_m 3055 m"),
}


def build_condition(oid, mode, threshold, elev, elev_source, claim_refs):
    if mode == "band":
        lo, hi = threshold
        operator, thr, source = "between", [lo, hi], "evidence_review"
        win = f"{lo}–{hi} m"
        rationale = {
            "zh-TW": (f"琉璃光高度窗（CL-DATA-71）：雲底（既有 LCL 代理）須落在本點帶 "
                      f"{win}——雲層懸在觀點（{elev:g} m）下方、市街燈海上方，燈光經薄雲散射成琉璃光；"
                      f"雲底高於帶外（晴天無雲或雲層高掛）時夜燈銳利、無散射層，本題材不成立。"),
            "en": (f"Glow (liuli) cloud-base window (CL-DATA-71): the cloud base "
                   f"(existing LCL proxy) must fall in this place's recorded band "
                   f"{win} - the deck hangs below the viewpoint ({elev:g} m) and above the "
                   f"town lights, scattering them into the glow; a base outside the band "
                   f"(clear sky or deck hanging high) gives crisp unlit-scatter lights and "
                   f"the subject does not hold."),
            "ja": (f"琉璃光の雲底窓（CL-DATA-71）：雲底（既存LCL代理）は本地点の帯 "
                   f"{win} に収まること。雲が視点（{elev:g} m）の下・街灯の上に掛かり、"
                   f"光が薄雲で散って琉璃光になる。帯外（快晴や雲が高い）では街灯が鋭く、散乱層がなく題材は成立しない。"),
        }
        notes = {
            "zh-TW": (f"CL-DATA-71：帶值照 catalog 記載（data/v2/audits/subject-lists/"
                      f"liuli-cloudheights.json，owner-gemini-liuliglow-30 清單）；"
                      f"觀點海拔＝{elev_source}。評估值＝ASL 雲底高度（格點海拔＋LCL）："
                      f"lcl_height_m_agl 為觀點格點 2m 溫度/露點推算、相對「格點地面」的高度，"
                      f"評估前一律換算為海拔高度（metres ASL），不以 AGL 直接比較門檻。"),
            "en": (f"CL-DATA-71: band values as recorded in the catalog "
                   f"(data/v2/audits/subject-lists/liuli-cloudheights.json, "
                   f"owner-gemini-liuliglow-30 list); viewpoint elevation = {elev_source}. "
                   f"Observed value = the ASL cloud base (grid elevation + LCL): "
                   f"lcl_height_m_agl is the 2 m temperature/dew-point parcel estimate at the "
                   f"viewpoint grid, expressed in metres above the grid GROUND, and is converted "
                   f"to metres ASL (above mean sea level) before it meets any threshold."),
            "ja": (f"CL-DATA-71：帯値はカタログ記載どおり（data/v2/audits/subject-lists/"
                   f"liuli-cloudheights.json、owner-gemini-liuliglow-30 リスト）；"
                   f"視点高度＝{elev_source}。評価値＝ASL の雲底高度（グリッド標高＋LCL）："
                   f"lcl_height_m_agl は視点グリッドの地上2m気温/露点から推算した「グリッド地面」"
                   f"からの高さで、評価前に海抜高度（metres ASL）へ換算する。"),
        }
    else:
        thr = round(elev - 200.0)
        operator, source = "lt", "computed"
        rationale = {
            "zh-TW": (f"雲海/雲瀑/夜光高度窗（CL-DATA-71）：雲底（既有 LCL 代理）須低於視線餘量"
                      f"（觀點海拔 {elev:g} m − 200 m = {thr} m，雲海族 DEM−200 慣例）；"
                      f"晴天無雲時雲底抬升遠超閾值，展望/夜光主體雖銳利但無下方雲層，本題材不成立。"),
            "en": (f"Cloud-sea/cascade/night-glow base window (CL-DATA-71): the cloud base "
                   f"(existing LCL proxy) must sit below the sight-line margin "
                   f"(viewpoint {elev:g} m - 200 m = {thr} m, the CL-DATA-12 cloud-sea-family "
                   f"DEM-200 convention); on clear nights the base rises far above the "
                   f"threshold - no deck below, the subject does not hold."),
            "ja": (f"雲海/雲瀑/夜光の雲底窓（CL-DATA-71）：雲底（既存LCL代理）は視線マージンより低いこと"
                   f"（視点 {elev:g} m − 200 m = {thr} m、雲海族 DEM−200 慣例）；"
                   f"快晴時は雲底が閾値を大きく超え、下方に雲がなく題材は成立しない。"),
        }
        notes = {
            "zh-TW": (f"CL-DATA-71：本點 catalog 無雲底帶記載，閾值以派生規則求得："
                      f"觀點海拔（{elev_source}）− 200 m = {thr} m。"
                      f"評估值＝ASL 雲底高度（格點海拔＋LCL）：lcl_height_m_agl 為觀點格點 "
                      f"2m 溫度/露點推算、相對「格點地面」的高度，評估前一律換算為海拔高度"
                      f"（metres ASL），不以 AGL 直接比較門檻；觀點海拔缺落時誠實 "
                      f"propagate_unknown。"),
            "en": (f"CL-DATA-71: no cloud-base band is recorded for this place in the "
                   f"catalog, so the threshold follows the derivation rule: viewpoint "
                   f"elevation ({elev_source}) - 200 m = {thr} m. Observed value = the "
                   f"ASL cloud base (grid elevation + LCL): lcl_height_m_agl is the 2 m "
                   f"temperature/dew-point parcel estimate at the viewpoint grid, expressed "
                   f"in metres above the grid GROUND, and is converted to metres ASL (above "
                   f"mean sea level) before it meets any threshold; a missing viewpoint "
                   f"elevation propagates UNKNOWN honestly."),
            "ja": (f"CL-DATA-71：本地点はカタログに雲底帯の記載がないため、閾値は派生規則による："
                   f"視点高度（{elev_source}）− 200 m = {thr} m。評価値＝ASL の雲底高度"
                   f"（グリッド標高＋LCL）：lcl_height_m_agl は視点グリッドの地上2m気温/露点から"
                   f"推算した「グリッド地面」からの高さで、評価前に海抜高度（metres ASL）へ"
                   f"換算する。視点高度が欠落する場合は誠実に unknown 伝播。"),
        }
    return {
        "id": f"C-{oid}-CB1",
        "role": "REQUIRED",
        "domain": "WEATHER",
        "evaluation_mode": "GUIDANCE",
        "capability": "CONDITIONS",
        "metric": "cloud_base_height",
        "operator": operator,
        "threshold": thr,
        "unit": "m",
        "unknown_policy": "propagate_unknown",
        "claim_refs": claim_refs,
        "model_binding": "dataset:open_meteo|field:lcl_height_m_agl|viewpoint_relative",
        "validation_status": "provisional",
        "condition_tier": "MAIN",
        "threshold_source": source,
        "calibration_status": "provisional",
        "rationale_i18n": rationale,
        "notes_i18n": notes,
    }


def serialize(d, indent, nl, trail):
    return json.dumps(d, indent=indent, ensure_ascii=False).replace("\n", nl) + trail


def detect(raw: str):
    nl = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(nl)
    second = lines[1] if len(lines) > 1 else ""
    indent = len(second) - len(second.lstrip(" "))
    trail = ""
    body = raw
    while body.endswith(nl):
        trail += nl
        body = body[:-len(nl)]
    return indent, nl, trail


def main():
    changed = []
    refreshed = []
    for oid, (mode, threshold, elev, elev_source) in PLAN.items():
        path = OPP / f"{oid}.json"
        raw = path.read_bytes().decode("utf-8")
        d = json.loads(raw)
        cc = d["condition_contract"]
        conds = cc["conditions"]
        indent, nl, trail = detect(raw)
        # sanity: round-trip must reproduce the file before we touch it
        assert serialize(d, indent, nl, trail) == raw, f"round-trip mismatch {oid}"
        claim_refs = next(iter(
            [c["claim_refs"] for c in conds if c.get("claim_refs")]), [])
        existing = next((c for c in conds
                         if c.get("metric") == "cloud_base_height"), None)
        if existing is not None:
            # Refresh path (CL-PHYS-02): the note text is the shipped contract
            # wording. Re-running after a wording change must propagate it into
            # the contracts instead of silently skipping them.
            fresh = build_condition(oid, mode, threshold, elev, elev_source,
                                    claim_refs)
            if existing.get("notes_i18n") == fresh["notes_i18n"]:
                print(f"skip {oid} (notes already current)")
                continue
            existing["notes_i18n"] = fresh["notes_i18n"]
            d["revision"] = int(d["revision"]) + 1
            path.write_text(serialize(d, indent, nl, trail), encoding="utf-8",
                            newline="")
            refreshed.append(oid)
            print(f"refreshed {oid}: notes -> ASL datum, revision={d['revision']}")
            continue
        conds.append(build_condition(oid, mode, threshold, elev, elev_source,
                                     claim_refs))
        d["revision"] = int(d["revision"]) + 1
        path.write_text(serialize(d, indent, nl, trail), encoding="utf-8",
                        newline="")
        changed.append(oid)
        print(f"patched {oid}: mode={mode} threshold={conds[-1]['threshold']} "
              f"elev={elev:g} revision={d['revision']}")
    print("total patched:", len(changed), "refreshed:", len(refreshed))


if __name__ == "__main__":
    main()
