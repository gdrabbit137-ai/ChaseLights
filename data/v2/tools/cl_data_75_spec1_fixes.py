#!/usr/bin/env python3
"""CL-DATA-75 Phase 0 — owner spec §1 four logic fixes across canonical contracts.

Owner spec: data/v2/audits/spec-quality-engine.md (supplied 2026-11-20, §1):
  1. mountain_view (mountain_vista): cloud_cover_mid [30,60] REQUIRED -> QUALITY/BONUS;
     add REQUIRED visibility >= 15 km + cloud_cover_low <= 30 %.
     jp-015-P02 re-genre -> golden_hour (golden_hour_window REQUIRED).
  2. night_sky (astrophotography): moon gate any_of per owner spec — anchor
     moon_altitude < 0 (M2, already the alternation anchor) OR (illumination <= 0.25
     AND separation >= 45): separation 40 -> 45; the milky-layer illuminance_proxy
     gate becomes moon_illumination_fraction <= 0.25 (moon-down override + alternation
     machinery realise the any_of in the current schema). galactic_core hard gate
     -> QUALITY/BONUS.
  3. golden_hour: golden_hour_window REQUIRED (all 6); add cloud_cover_low <= 40.
     snow_ice: add snow-cover gate (snow_depth>0 OR snowfall>0 via the CL-DATA-74
     derived snow_cover_state; raw snow_depth_cm lands in Phase 1) + rain exclusion
     (precipitation < 0.2) + wind <= 7 m/s (was 15).
  4. jp-010-P01: add cloud_cover_low <= 30 + visibility >= 15 + flower-season windows
     (seasonal-calendar.json entries, web-verified 2026-11-20).
     jp-010-P02: remove REQUIRED seasonal_state (year-round subject).

Idempotent: already-conformed files are left byte-identical.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "data/v2/opportunities"

SPEC_NOTE = {
    "zh-TW": "2026-11-20 CL-DATA-75（owner《攝影題材規則重構與 QUALITY 計分引擎規格書》§1）",
    "en": "2026-11-20 CL-DATA-75 (owner spec \u201cPhotography-genre rule refactor & QUALITY scoring engine\u201d \u00a71)",
    "ja": "2026-11-20 CL-DATA-75（オーナー仕様書「撮影題材ルール再構築とQUALITY計分エンジン」§1）",
}


def notes(zh, en, ja):
    return {
        "zh-TW": SPEC_NOTE["zh-TW"] + "：" + zh,
        "en": SPEC_NOTE["en"] + ": " + en,
        "ja": SPEC_NOTE["ja"] + "：" + ja,
    }


def cond(cid, metric, operator, threshold, unit, binding, claim_refs, rationale, note, *,
         role="REQUIRED", domain="WEATHER", tier="MAIN", threshold_source="formula_derived"):
    return {
        "id": cid,
        "role": role,
        "domain": domain,
        "evaluation_mode": "GUIDANCE",
        "capability": "CONDITIONS",
        "metric": metric,
        "operator": operator,
        "threshold": threshold,
        "unit": unit,
        "unknown_policy": "propagate_unknown",
        "claim_refs": list(claim_refs),
        "model_binding": binding,
        "validation_status": "provisional",
        "condition_tier": tier,
        "threshold_source": threshold_source,
        "calibration_status": "provisional",
        "rationale_i18n": rationale,
        "notes_i18n": note,
    }


def next_id(oid, conditions):
    nums = []
    prefix = f"C-{oid}-"
    for c in conditions:
        suffix = c["id"][len(prefix):] if c["id"].startswith(prefix) else ""
        if suffix.isdigit():
            nums.append(int(suffix))
    return f"C-{oid}-{(max(nums) if nums else 0) + 1:02d}"


def first_claim_refs(conditions):
    for c in conditions:
        if c.get("claim_refs"):
            return c["claim_refs"]
    raise AssertionError("contract without any claim_refs")


def dump(doc: dict, path: Path):
    text = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    path.write_bytes(text.encode("utf-8"))


# ---------------------------------------------------------------------------
LOW_CLOUD_30 = {
    "zh-TW": "低雲罩頂就沒有山景：低雲 ≤30%（僅高層薄雲或晴空時山體清晰可辨）；中雲層次感改列加分項，不再否決晴空。",
    "en": "A low deck over the mountains kills the vista: low cloud <= 30% (the ridgelines stay legible under a clear or only high-thin sky); mid-cloud layering is a bonus, never a veto.",
    "ja": "低層雲が山頂を覆えば眺望は成立しない：下層雲≤30%（晴または上層の薄雲のみならず稜線が明瞭）。中層雲の重なりは加点項とし、晴空を否決しない。",
}
VIS_15 = {
    "zh-TW": "山景的價值在看得遠：能見度 ≥15 km，霧霾把遠山吃掉時直接否決（owner 規格 §1.1 標準值）。",
    "en": "The value of a mountain vista is distance: visibility >= 15 km; haze that swallows the far ridges vetoes the hour outright (owner-spec section 1.1 standard value).",
    "ja": "山景の価値は遠くまで見えること：視程≥15 km。ヘイズが遠山を飲み込む場合は否決（オーナー仕様書 §1.1 の標準値）。",
}
LOW_CLOUD_40_GH = {
    "zh-TW": "金色時刻要讓低角度光斜灑進畫面：低雲 ≤40%；厚低雲把斜光整層擋掉就不成立。",
    "en": "Golden hour needs the low-angle light to rake across the scene: low cloud <= 40%; a thick low deck blocks the rake and the hour fails.",
    "ja": "ゴールデンアワーは低角度の光が斜めに差し込むことを要する：下層雲≤40%。厚い下層雲は光を遮り不成立。",
}
SNOW_PRECIP = {
    "zh-TW": "排除降雨：降水 ≥0.2 mm/h 時濕雪與器材風險，否決（owner 規格 §1.3）。",
    "en": "Rain excluded: at precipitation >= 0.2 mm/h wet snow and gear risk veto the hour (owner spec section 1.3).",
    "ja": "降雨の除外：降水≥0.2 mm/hでは濡れ雪と機材リスクにより否決（オーナー仕様書 §1.3）。",
}
SNOW_COVER = {
    "zh-TW": "有雪才成立：雪深 >0 或降雪 >0（以 CL-DATA-74 派生三態 snowing/snow_covered/none 實作 OR 語義；原始 snow_depth_cm 數值門檻待 Phase 1 ETL 標準化）。",
    "en": "Snow must be present: snow depth > 0 OR snowfall > 0 (implemented via the CL-DATA-74 derived state snowing/snow_covered/none, which collapses the OR; the raw snow_depth_cm gate lands with the Phase 1 ETL standardisation).",
    "ja": "雪があることが前提：雪深>0 または降雪>0（CL-DATA-74 の派生状態 snowing/snow_covered/none でORを実装。素の snow_depth_cm 閾値は Phase 1 の ETL 標準化で導入）。",
}
WIND_7 = {
    "zh-TW": "冰雪環境收緊風速：≤7 m/s（原 15 m/s 過寬——大風吹雪既毀雪面也站不穩腳架，owner 規格 §1.3）。",
    "en": "Tighten wind for snow & ice: <= 7 m/s (the old 15 m/s was far too loose - blowing snow destroys the surface and no tripod stands in it; owner spec section 1.3).",
    "ja": "雪氷環境では風速を引き締める：≤7 m/s（従来の15 m/sは緩すぎ——吹雪は雪面を荒らし脚も立たない。オーナー仕様書 §1.3）。",
}


def fix_mountain_view(doc, oid):
    changed = []
    cc = doc["condition_contract"]
    claims = first_claim_refs(cc["conditions"])
    has_low = any(c["metric"] == "cloud_cover_low" for c in cc["conditions"])
    has_vis = any(c["metric"] == "visibility" for c in cc["conditions"])
    for c in cc["conditions"]:
        if c["metric"] == "cloud_cover_mid" and c["role"] == "REQUIRED" \
                and c.get("operator") == "between" and c.get("threshold") == [30, 60]:
            c["role"] = "QUALITY"
            c["condition_tier"] = "BONUS"
            c["rationale_i18n"] = {
                "zh-TW": "中雲 30–60% 帶來層次感，但只是加分——晴空萬里同樣是絕佳山景（owner 規格 §1.1：移除必須，避免晴空被誤殺）。",
                "en": "Mid-cloud 30-60% adds layering, but as a bonus only - a cloudless clear sky is equally a superb mountain vista (owner spec section 1.1: the gate is removed so clear skies are no longer killed).",
                "ja": "中層雲30〜60%は画面に重なりを与えるが加点にとどめる——雲一つない晴空も優れた山景（オーナー仕様書 §1.1：必須を撤去し晴空の誤殺を防ぐ）。",
            }
            c["notes_i18n"] = notes(
                "cloud_cover_mid [30,60] 必須 → 加分項（BONUS）。",
                "cloud_cover_mid [30,60] demoted from REQUIRED gate to QUALITY/BONUS.",
                "cloud_cover_mid [30,60] を必須から加点（BONUS）へ降格。")
            changed.append("cloud_mid_demoted")
    if not has_low:
        cc["conditions"].append(cond(
            next_id(oid, cc["conditions"]), "cloud_cover_low", "lte", 30, "%",
            "dataset:gfs_0p25|field:cloud_cover_low_percent|role:MID", claims,
            LOW_CLOUD_30, notes("新增必須：低雲 ≤30%。",
                                "Added REQUIRED: low cloud <= 30%.",
                                "必須条件を追加：下層雲≤30%。")))
        changed.append("cloud_low_added")
    if not has_vis:
        cc["conditions"].append(cond(
            next_id(oid, cc["conditions"]), "visibility", "gte", 15, "km",
            "dataset:gfs_0p25|field:visibility_km|role:MID", claims,
            VIS_15, notes("新增必須：能見度 ≥15 km。",
                          "Added REQUIRED: visibility >= 15 km.",
                          "必須条件を追加：視程≥15 km。")))
        changed.append("visibility_added")
    return changed


def fix_night_sky(doc, oid):
    changed = []
    cc = doc["condition_contract"]
    for c in cc["conditions"]:
        if c["metric"] == "galactic_core_altitude" and c["role"] == "REQUIRED":
            c["role"] = "QUALITY"
            c["condition_tier"] = "BONUS"
            c["rationale_i18n"] = {
                "zh-TW": "銀河核心仰角僅作加分項（owner 規格 §1.2）：冬季核心低於地平線不封殺星空；核心高懸的夏夜畫面更佳，作為品質層訊號。",
                "en": "Galactic-core altitude is a bonus signal only (owner spec section 1.2): in winter the core sits below the horizon and must never veto the starry sky; a high summer core simply makes the frame better.",
                "ja": "銀河中心の高度は加点信号に過ぎない（オーナー仕様書 §1.2）：冬は中心が地平線下でも星空を否決しない。夏の高仰角は画面をより良くするだけ。",
            }
            c["notes_i18n"] = notes(
                "galactic_core ≥20 硬門檻移除，改 BONUS 加分項。",
                "galactic-core >= 20 hard gate removed, demoted to QUALITY/BONUS.",
                "galactic_core ≥20 の必須門檻を撤去し、加点（BONUS）へ。")
            changed.append("galactic_demoted")
        if c["metric"] == "moon_target_separation_deg" and c.get("threshold") == 40:
            c["threshold"] = 45
            c["rationale_i18n"] = {
                "zh-TW": "月亮離銀河核心 ≥45°（owner 規格 §1.2）：細月升起但夠遠時銀河帶仍可拍；僅在月亮升起時啟用（月光 any_of 第二軌——月下 OR（細月 ∧ 夠遠））。",
                "en": "Moon at least 45 deg from the galactic core (owner spec section 1.2): with a thin moon up but far from the core the galactic band stays shootable; active only while the moon is up (track 2 of the moonlight any_of: moon down OR (crescent AND far)).",
                "ja": "月が銀河中心から≥45度（オーナー仕様書 §1.2）：細い月でも遠ければ銀河帯は撮れる。月が昇っている間のみ有効（月光any_of第2軌道——月が沈む OR（細月∧遠い））。",
            }
            c["notes_i18n"] = notes(
                "分離門檻 40°→45°（any_of 第二軌成員）。",
                "separation threshold 40 deg -> 45 deg (track-2 member of the any_of).",
                "分離閾値40°→45°（any_of第2軌道の構成要素）。")
            changed.append("separation_45")
        if c["metric"] == "moon_illuminance_proxy" and c.get("operator") == "lte":
            c["metric"] = "moon_illumination_fraction"
            c["threshold"] = 0.25
            c["unit"] = None
            c["rationale_i18n"] = {
                "zh-TW": "月光 any_of 第二軌（owner 規格 §1.2）：月亮升起時須為細月（月照 ≤25%）且離銀河核心 ≥45°；月亮在地平線下（仰角 <0）時由 M2 錨點成立、本軌不適用。取代原先的照度代理閘（實作細節見 evaluate_batch M2/M3 交替邏輯）。",
                "en": "Track 2 of the moonlight any_of (owner spec section 1.2): while the moon is up it must be a crescent (illumination <= 0.25) AND at least 45 deg from the galactic core; with the moon below the horizon the M2 anchor satisfies the set and this track does not apply. Replaces the old illuminance-proxy gate (see the M2/M3 alternation in evaluate_batch).",
                "ja": "月光any_ofの第2軌道（オーナー仕様書 §1.2）：月が昇っている間は細い月（月照≤0.25）かつ銀河中心から≥45度を要する。月が地平線下ならM2アンカーが成立し本軌道は適用されない。旧の照度プロキシゲートを置き換え（evaluate_batch の M2/M3 交替ロジック参照）。",
            }
            c["notes_i18n"] = notes(
                "月光雙軌：月照閘 ≤0.25 取代照度代理（月下時本條件自動成立——評估器對月下月亮的月照一律放行）。",
                "moon dual-track: illumination gate <= 0.25 replaces the illuminance proxy (a moon below the horizon auto-passes this condition by the evaluator's moon-down override).",
                "月光二段構え：月照ゲート≤0.25が照度プロキシを置換（月が地平線下なら評価器の月下オーバーライドで自動成立）。")
            changed.append("illum_025")
    return changed


def fix_golden_hour(doc, oid):
    changed = []
    cc = doc["condition_contract"]
    claims = first_claim_refs(cc["conditions"])
    for c in cc["conditions"]:
        if c["metric"] == "golden_hour_window" and c["role"] == "QUALITY":
            c["role"] = "REQUIRED"
            c["condition_tier"] = "MAIN"
            c["rationale_i18n"] = {
                "zh-TW": "金色時刻窗為必要（owner 規格 §1.3）：低角度金光定義本題材，正午不再觸發；晨昏雙向皆可（phase 不限）。",
                "en": "The golden-hour window is REQUIRED (owner spec section 1.3): low-angle golden light defines the subject, noon no longer qualifies; both morning and evening rakes qualify (no phase constraint).",
                "ja": "ゴールデンアターの窓は必須（オーナー仕様書 §1.3）：低角度の金色光が本題材を定義し、正午は成立しない。朝夕いずれも可（phase 制約なし）。",
            }
            c["notes_i18n"] = notes(
                "golden_hour_window 設必須（原為加分項導致正午誤觸發）。",
                "golden_hour_window set REQUIRED (was QUALITY, letting noon hours qualify).",
                "golden_hour_window を必須に（旧QUALITYでは正午が誤成立）。")
            changed.append("gh_window_required")
    if not any(c["metric"] == "cloud_cover_low" for c in cc["conditions"]):
        cc["conditions"].append(cond(
            next_id(oid, cc["conditions"]), "cloud_cover_low", "lte", 40, "%",
            "dataset:gfs_0p25|field:cloud_cover_low_percent|role:MID", claims,
            LOW_CLOUD_40_GH, notes("新增必須：低雲 ≤40%。",
                                   "Added REQUIRED: low cloud <= 40%.",
                                   "必須条件を追加：下層雲≤40%。")))
        changed.append("cloud_low_added")
    return changed


def fix_snow_ice(doc, oid):
    changed = []
    cc = doc["condition_contract"]
    claims = first_claim_refs(cc["conditions"])
    for c in cc["conditions"]:
        if c["metric"] == "wind_speed_10m" and c.get("threshold") in (15.0, 15):
            c["operator"] = "lte"
            c["threshold"] = 7.0
            c["rationale_i18n"] = WIND_7
            c["notes_i18n"] = notes("風速上限 15→7 m/s。",
                                    "wind ceiling 15 -> 7 m/s.",
                                    "風速上限15→7 m/s。")
            changed.append("wind_7")
    if not any(c["metric"] == "precipitation" for c in cc["conditions"]):
        cc["conditions"].append(cond(
            next_id(oid, cc["conditions"]), "precipitation", "lt", 0.2, "mm/h",
            "dataset:gfs_0p25|field:precipitation_rate_mm_h|role:MID", claims,
            SNOW_PRECIP, notes("新增必須：排除降雨（<0.2 mm/h）。",
                               "Added REQUIRED: rain excluded (< 0.2 mm/h).",
                               "必須条件を追加：降雨の除外（<0.2 mm/h）。")))
        changed.append("precip_added")
    if not any(c["metric"] == "snow_cover_state" for c in cc["conditions"]):
        cc["conditions"].append(cond(
            next_id(oid, cc["conditions"]), "snow_cover_state", "none", None, None,
            None, claims, SNOW_COVER,
            notes("新增必須：有雪（雪深>0 或降雪>0 的派生狀態）。",
                  "Added REQUIRED: snow present (derived state of depth>0 OR falling snow).",
                  "必須条件を追加：雪の存在（雪深>0または降雪>0の派生状態）。"),
            threshold_source="computed"))
        changed.append("snow_gate_added")
    return changed


def fix_jp010_P01(doc):
    changed = []
    cc = doc["condition_contract"]
    claims = first_claim_refs(cc["conditions"])
    if not any(c["metric"] == "cloud_cover_low" for c in cc["conditions"]):
        cc["conditions"].append(cond(
            next_id(doc["opportunity_id"], cc["conditions"]), "cloud_cover_low", "lte", 30, "%",
            "dataset:gfs_0p25|field:cloud_cover_low_percent|role:MID", claims,
            LOW_CLOUD_30, notes("新增必須：低雲 ≤30%（跨湖望富士需要乾淨的低層天空）。",
                                "Added REQUIRED: low cloud <= 30% (viewing Fuji across the lake needs a clean low sky).",
                                "必須条件を追加：下層雲≤30%（湖越しの富士には澄んだ低空が必要）。")))
        changed.append("cloud_low_added")
    if not any(c["metric"] == "visibility" for c in cc["conditions"]):
        cc["conditions"].append(cond(
            next_id(doc["opportunity_id"], cc["conditions"]), "visibility", "gte", 15, "km",
            "dataset:gfs_0p25|field:visibility_km|role:MID", claims,
            VIS_15, notes("新增必須：能見度 ≥15 km（富士山可見的前提）。",
                          "Added REQUIRED: visibility >= 15 km (the precondition for seeing Fuji at all).",
                          "必須条件を追加：視程≥15 km（富士の可視の前提）。")))
        changed.append("visibility_added")
    return changed


def fix_jp010_P02(doc):
    cc = doc["condition_contract"]
    before = len(cc["conditions"])
    cc["conditions"] = [c for c in cc["conditions"]
                        if c["metric"] != "seasonal_state"]
    if len(cc["conditions"]) == before:
        return []
    for c in cc["conditions"]:
        if c["metric"] == "light_window":
            base = c.get("notes_i18n") or {}
            c["notes_i18n"] = {k: ((base.get(k) or "").rstrip() +
                                   ("\n" if base.get(k) else "") + v)
                               for k, v in notes(
                "移除季節窗必須（全年可拍——逆さ富士的成立條件是湖面平靜與富士可見，不是花季；owner 規格 §1.4：避免對照空值季節窗）。",
                "seasonal window gate removed (year-round subject: the reverse-Fuji lives on calm water and a visible Fuji, not a bloom season; owner spec section 1.4 - avoids referencing an empty seasonal field).",
                "季節窓の必須を撤去（通年撮影可——逆さ富士は湖面の静けさと富士の可視で成立し、花の季節ではない。オーナー仕様書 §1.4：空の季節欄参照を回避）。").items()}
            break
    return ["seasonal_removed"]


def fix_jp015_P02(doc):
    changed = []
    cc = doc["condition_contract"]
    claims = first_claim_refs(cc["conditions"])
    cc["genre_template"] = "golden_hour"
    cc["template_version"] = "golden_hour-v0.1"
    for c in cc["conditions"]:
        if c["metric"] == "cloud_cover_mid" and c["role"] == "REQUIRED":
            c["role"] = "QUALITY"
            c["condition_tier"] = "BONUS"
            c["rationale_i18n"] = {
                "zh-TW": "中雲 30–60% 給廣場全景明暗節奏，但只是加分——晴空同樣成立（owner 規格 §1.1 同源修正）。",
                "en": "Mid-cloud 30-60% gives the plaza panorama its light rhythm, as a bonus only - a clear sky also qualifies (same-source fix as owner spec section 1.1).",
                "ja": "中層雲30〜60%は広場の全景に明暗のリズムを与えるが加点にとどめる——晴空でも成立（オーナー仕様書 §1.1 同源の修正）。",
            }
            c["notes_i18n"] = notes(
                "cloud_cover_mid 必須 → 加分項。",
                "cloud_cover_mid demoted from gate to bonus.",
                "cloud_cover_mid を必須から加点へ。")
            changed.append("cloud_mid_demoted")
        if c["metric"] == "sunrise_time_window":
            # owner spec: re-genre to golden_hour -> the window becomes the
            # REQUIRED golden-hour window (both dawn and dusk rakes qualify)
            c["metric"] = "golden_hour_window"
            c["role"] = "REQUIRED"
            c["operator"] = "none"
            c["condition_tier"] = "MAIN"
            c["threshold_source"] = "computed"
            c["rationale_i18n"] = {
                "zh-TW": "金色時刻窗為必要（owner 規格 §1：皇居廣場全景改歸 golden_hour 題材）：低角度金光定義本題材，正午不再觸發；晨昏雙向皆可。",
                "en": "The golden-hour window is REQUIRED (owner spec section 1: the Kokyo Gaien plaza panorama re-genred to golden_hour): low-angle golden light defines the subject, noon no longer qualifies; morning and evening both qualify.",
                "ja": "ゴールデンアワーの窓は必須（オーナー仕様書 §1：皇居前広場の全景は golden_hour 題材へ再分類）：低角度の金色光が本題材を定義し、正午は不成立。朝夕どちらも可。",
            }
            c["notes_i18n"] = notes(
                "題材改歸 golden_hour：晨昏窗升為必要（原 sunrise 加分項）。",
                "re-genred to golden_hour: the golden-hour window is now REQUIRED (was a sunrise bonus).",
                "golden_hour 題材へ再分類：朝夕の窓を必須に（旧は日の出の加点項）。")
            changed.append("genred_golden_hour")
    if not any(c["metric"] == "cloud_cover_low" for c in cc["conditions"]):
        cc["conditions"].append(cond(
            next_id(doc["opportunity_id"], cc["conditions"]), "cloud_cover_low", "lte", 40, "%",
            "dataset:gfs_0p25|field:cloud_cover_low_percent|role:MID", claims,
            LOW_CLOUD_40_GH, notes("新增必須：低雲 ≤40%（golden_hour 題材 §1.3 家族標準）。",
                                   "Added REQUIRED: low cloud <= 40% (golden_hour family standard, spec section 1.3).",
                                   "必須条件を追加：下層雲≤40%（golden_hour題材 §1.3 の標準）。")))
        changed.append("cloud_low_added")
    return changed


def main():
    summary = {}
    for path in sorted(CANON.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        oid = doc["opportunity_id"]
        gt = (doc.get("condition_contract") or {}).get("genre_template")
        changed = []
        if gt == "mountain_view" and oid != "jp-015-P02":
            changed = fix_mountain_view(doc, oid)
        elif gt == "night_sky":
            changed = fix_night_sky(doc, oid)
        elif gt == "golden_hour":
            changed = fix_golden_hour(doc, oid)
        elif gt == "snow_ice":
            changed = fix_snow_ice(doc, oid)
        elif oid == "jp-010-P01":
            changed = fix_jp010_P01(doc)
        elif oid == "jp-010-P02":
            changed = fix_jp010_P02(doc)
        elif oid == "jp-015-P02":
            changed = fix_jp015_P02(doc)
        if changed:
            doc["revision"] = int(doc.get("revision") or 1) + 1
            dump(doc, path)
            summary[oid] = changed
    print(json.dumps({"changed_files": len(summary), "detail": summary},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
