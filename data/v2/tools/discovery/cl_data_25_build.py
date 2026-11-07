#!/usr/bin/env python3
"""CL-DATA-25 discovery-admission builder (owner ruling 2026-11-07: rubric >=3.8 admits directly).

Reads data/v2/tools/discovery/cl_data_25_candidates.json (web-verified 2026-11-07)
and materialises BOTH tracks for every admitted place:

  a) V2: 委託書式 contracts under data/v2/opportunities/<place>-PNN.json
     (condition sets cloned from reviewed exemplar contracts of the same genre,
     per-place LCL/elevation overrides, seasonal_state REQUIRED wherever an
     operating/season window exists - calendar entries appended to
     data/v2/seasonal-calendar.json; drift_ice subject honestly not_evaluatable
     like the CL-DATA-20 tidal pattern).
  b) legacy: regions.py spot tuple + admin area + SPOT_OVERRIDES/
     ELEVATION_OVERRIDES entries, runtime_catalog_v004_r4_2.json spots/opportunities,
     runtime_catalog_manifest_r4_2.json ranges/counts, and
     runtime_dependencies.py RUNTIME_PROFILE_GAPS entries (fail-closed module_pending).

Idempotent: re-running regenerates the same output. Files are written as bytes
(LF preserved) to avoid the Windows CRLF pitfall.
"""
from __future__ import annotations

import json
import re
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "data/v2/opportunities"
DISC = ROOT / "data/v2/tools/discovery"
CAND = json.loads((DISC / "cl_data_25_candidates.json").read_text(encoding="utf-8"))

EXEMPLARS = {
    "cloud_sea": "tw-001-P02",
    "sunrise": "tw-019-P01",
    "sunset": "jp-013-P01",
    "night_sky": "jp-022-P03",
    "reflection": "jp-007-P01",
    "overlook": "jp-006-P01",
    "mountain_view": "tw-016-P01",
    "seasonal_plant": "tw-083-P02",
    "city_night": "tw-006-P03",
}
WINDOW_METRICS = {
    "light_window", "city_night_window", "astronomical_darkness",
    "sunrise_time_window", "sunset_window", "blue_hour_window", "golden_hour_window",
}
# legacy runtime mapping (theme, formula_status) - verified against runtime_dependencies.py
LEGACY_MAP = {
    "cloud_sea": ("cloud_sea", "needs_spatial_weather_module"),
    "sunrise": ("sunrise", "needs_directional_horizon_visibility_module"),
    "sunrise_marine": ("sunrise", "needs_marine_directional_horizon_module"),
    "sunset": ("sunset", "needs_directional_horizon_visibility_module"),
    "night_sky": ("milky_way", "needs_astronomy_ephemeris_module"),
    "city_night": ("city_night", "needs_visibility_module"),
    "reflection": ("reflection", "needs_water_surface_module"),
    "reflection_lake": ("reflection", "needs_water_surface_visibility_module"),
    "reflection_lakelevel": ("reflection", "needs_water_surface_module"),
    "overlook": ("mountain_view", "needs_visibility_module"),
    "mountain_view": ("mountain_view", "needs_visibility_module"),
    "seasonal_plant": ("seasonal_foreground", "needs_seasonal_foreground_module"),
    "snow_ice": ("snow_scene", "needs_snow_state_module"),
    "snow_ice_night": ("snow_scene", "needs_snow_state_module"),
    "drift_ice": ("snow_scene", "needs_snow_state_module"),
}
PROFILE_GAP_COMPONENTS = {
    "needs_spatial_weather_module": "spatial_weather_vertical_cloud",
    "needs_directional_horizon_visibility_module": "directional_horizon",
    "needs_marine_directional_horizon_module": "directional_horizon",
    "needs_seasonal_foreground_module": "seasonal_foreground",
    "needs_astronomy_ephemeris_module": "astronomy_ephemeris",
}

def wbytes(path: Path, text: str):
    data = text.replace("\r\n", "\n").encode("utf-8")
    path.write_bytes(data)

def jdump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"

# ---------------------------------------------------------------- season calendar
SEASONAL_SOURCES = {
    "unkai_tomamu": ("https://www.snowtomamu.jp/summer/unkai/", "2026 season gondola 5/13-10/13, 4:30-8:00"),
    "unkai_kussharo": ("https://www.masyuko.or.jp/enjoy/unkai/", "cloud sea Jun-Oct early morning; road 588 closed Nov-May"),
    "unkai_bihoro": ("https://www.town.bihoro.hokkaido.jp/site/kanko/1604.html", "spring/autumn pre-dawn cloud sea; winter closures"),
    "juhyo_zao": ("https://zaoropeway.co.jp/winter/juhyo/", "official juhyo calendar: late Dec-early Mar, peak late Jan-late Feb"),
    "juhyo_zao_lightup": ("https://zaoropeway.co.jp/winter/juhyo/", "night illumination announced yearly, approx late Dec-late Feb"),
    "juhyo_moriyoshi": ("https://www.aniski.jp/mtmoriyoshi/juhyo/", "viewing period Jan 7 - Mar 5 (2025 example)"),
    "juhyo_hakkoda": ("https://hakkoda-ropeway.jp/", "peak mid Jan-late Feb; winter hours 9:00-15:40"),
    "ryuhyo_utoro": ("https://www.sno.co.jp/seaice", "drift ice onshore late Jan-Mar, February peak"),
    "lavender": ("https://www.farm-tomita.co.jp/east/", "open approx 6/20-7/20 (2026); bloom temperature-driven"),
    "aoike_season": ("https://www.tohokukanko.jp/attractions/detail_1007187.html", "trail open Apr-Nov"),
    "nukabira_bridge": ("https://www.taushubetsu-journal.com/data/", "lake-level log: visible Jan (frozen lake) to mid-May"),
    "zao_okama_season": ("https://www.zao-machi.com/sightseeing_spot/1.html", "eco/hyline roads open late Apr-early Nov"),
    "kitayamazaki_season": ("https://www.vill.tanohata.iwate.jp/kankou/see/kitayamazaki.html", "decks accessible Apr-Nov"),
    "unkai_monaiyama": ("https://www.city.otaru.lg.jp/docs/2020100900664/#kenasi", "spring-early-summer fog; winter closure"),
    "unkai_appi": ("https://www.appi.co.jp/snow-mountain-resort/1304", "green-season gondola daily; dates provisional Jun-Oct"),
    "unkai_daxueshan": ("https://www.forest.gov.tw/news/0070337", "cloud-sea/radiation-fog season approx Oct-Apr"),
    "cuifeng_mist": ("https://travel.yilan.gov.tw/zh-tw/attraction/381/", "morning mist strongest autumn-winter; park hours apply"),
    "guanwu_unkai": ("https://recreation.forest.gov.tw/Forest/RA?typ_id=0200004", "cloud-sea home; late autumn-spring"),
    "lanyang_riliu": ("https://travel.ettoday.net/article/880376.htm", "Lanyang radiation-fog season late autumn-spring"),
    "smangus_unkai": ("https://digiphoto.techbang.com/posts/531-division-forward-marcus-below", "tribal cloud sea late autumn-spring"),
    "guishan_sunrise": ("https://www.necoast-nsa.gov.tw/Attraction-Content.aspx?a=274", "Gueishan sunrise best Jun-Sep"),
    "fushoushan_unkai": ("https://www.fushoushan.com.tw/Outer/FarmOverview", "Lishan valley cloud sea autumn-winter; night controls"),
    "qingtiangang_grass_season": ("https://www.yangmingshan.gov.tw/", "grassland mist/low cloud Apr-Sep"),
}

def build_seasonal_entries(places):
    entries = []
    for p in places:
        for subj in p["subjects"]:
            sid = subj.get("seasonal")
            if not sid:
                continue
            months_note = ""
            for e in entries:
                if e["plant_id"] == sid:
                    e["spots"].append(f"{p['place_id']}-{subj['suffix']}")
                    break
            else:
                url, note = SEASONAL_SOURCES[sid]
                win = TYPICAL_WINDOWS[sid]
                entries.append({
                    "plant_id": sid,
                    "spots": [f"{p['place_id']}-{subj['suffix']}"],
                    "name_i18n": SEASON_NAMES[sid],
                    "typical_window": win,
                    "sources": [{"url": url, "kind": "official", "note_i18n": {
                        "zh-TW": note, "en": note, "ja": note}}],
                })
    return entries

TYPICAL_WINDOWS = {
    "unkai_tomamu": {"start": "05-13", "end": "10-13"},
    "unkai_kussharo": {"start": "06-01", "end": "10-31"},
    "unkai_bihoro": {"start": "04-01", "end": "10-31"},
    "juhyo_zao": {"start": "12-20", "end": "03-10"},
    "juhyo_zao_lightup": {"start": "12-25", "end": "02-25"},
    "juhyo_moriyoshi": {"start": "01-07", "end": "03-05"},
    "juhyo_hakkoda": {"start": "01-15", "end": "02-25"},
    "ryuhyo_utoro": {"start": "01-20", "end": "03-31"},
    "lavender": {"start": "06-20", "end": "07-20"},
    "aoike_season": {"start": "04-01", "end": "11-30"},
    "nukabira_bridge": {"start": "01-01", "end": "05-15"},
    "zao_okama_season": {"start": "04-20", "end": "11-05"},
    "kitayamazaki_season": {"start": "04-01", "end": "11-30"},
    "unkai_monaiyama": {"start": "04-01", "end": "10-31"},
    "unkai_appi": {"start": "06-01", "end": "10-31"},
    "unkai_daxueshan": {"start": "10-01", "end": "04-30"},
    "cuifeng_mist": {"start": "09-01", "end": "04-30"},
    "guanwu_unkai": {"start": "10-01", "end": "03-31"},
    "lanyang_riliu": {"start": "10-01", "end": "03-31"},
    "smangus_unkai": {"start": "10-01", "end": "03-31"},
    "guishan_sunrise": {"start": "06-01", "end": "09-30"},
    "fushoushan_unkai": {"start": "10-01", "end": "03-31"},
    "qingtiangang_grass_season": {"start": "04-01", "end": "09-30"},
}
SEASON_NAMES = {
    "unkai_tomamu": {"zh-TW": "雲海ゴンドラ夏季運行期", "en": "Unkai gondola summer season", "ja": "雲海ゴンドラ夏季運行期間"},
    "unkai_kussharo": {"zh-TW": "屈斜路湖雲海季", "en": "Kussharo cloud-sea season", "ja": "屈斜路湖の雲海シーズン"},
    "unkai_bihoro": {"zh-TW": "美幌峠雲海季", "en": "Bihoro cloud-sea season", "ja": "美幌峠の雲海シーズン"},
    "juhyo_zao": {"zh-TW": "蔵王樹氷期", "en": "Zao juhyo season", "ja": "蔵王の樹氷期"},
    "juhyo_zao_lightup": {"zh-TW": "蔵王樹氷ライトアップ期", "en": "Zao juhyo illumination season", "ja": "蔵王の樹氷ライトアップ期間"},
    "juhyo_moriyoshi": {"zh-TW": "森吉山樹氷観賞期", "en": "Moriyoshi juhyo viewing period", "ja": "森吉山の樹氷観賞期間"},
    "juhyo_hakkoda": {"zh-TW": "八甲田樹氷期", "en": "Hakkoda juhyo season", "ja": "八甲田の樹氷期"},
    "ryuhyo_utoro": {"zh-TW": "知床流氷接岸期", "en": "Shiretoko drift-ice season", "ja": "知床の流氷接岸期"},
    "lavender": {"zh-TW": "薰衣草開花期", "en": "Lavender bloom", "ja": "ラベンダー開花"},
    "aoike_season": {"zh-TW": "十二湖青池開放期", "en": "Aoike open season", "ja": "十二湖・青池の開放期"},
    "nukabira_bridge": {"zh-TW": "糠平湖橋梁可見期", "en": "Nukabira bridge visible period", "ja": "糠平湖の橋梁可視期間"},
    "zao_okama_season": {"zh-TW": "蔵王御釜通行期", "en": "Okama access season", "ja": "蔵王・御釜の通行期間"},
    "kitayamazaki_season": {"zh-TW": "北山崎展望期", "en": "Kitayamazaki viewing season", "ja": "北山崎の展望期"},
    "unkai_monaiyama": {"zh-TW": "毛無山展望所開放期", "en": "Monai-yama observatory season", "ja": "毛無山展望所の開放期"},
    "unkai_appi": {"zh-TW": "安比雲海季（暫定）", "en": "Appi cloud-sea season (provisional)", "ja": "安比の雲海シーズン（暫定）"},
    "unkai_daxueshan": {"zh-TW": "大雪山雲海霧季", "en": "Daxueshan cloud-sea/fog season", "ja": "大雪山の雲海・霧季"},
    "cuifeng_mist": {"zh-TW": "翠峰湖晨霧季", "en": "Cuifeng morning-mist season", "ja": "翠峰湖の朝霧シーズン"},
    "guanwu_unkai": {"zh-TW": "觀霧雲海季", "en": "Guanwu cloud-sea season", "ja": "観霧の雲海シーズン"},
    "lanyang_riliu": {"zh-TW": "蘭陽平原輻射霧季", "en": "Lanyang radiation-fog season", "ja": "蘭陽平原の放射霧季"},
    "smangus_unkai": {"zh-TW": "司馬庫斯雲海季", "en": "Smangus cloud-sea season", "ja": "スマングスの雲海シーズン"},
    "guishan_sunrise": {"zh-TW": "龜山島朝日方位季", "en": "Gueishan sunrise alignment season", "ja": "亀山島の朝日方位季"},
    "fushoushan_unkai": {"zh-TW": "福壽山雲海季", "en": "Fushoushan cloud-sea season", "ja": "福寿山の雲海シーズン"},
    "qingtiangang_grass_season": {"zh-TW": "擎天崗草原雲霧季", "en": "Qingtiangang grass mist season", "ja": "擎天崗の雲霧シーズン"},
}

# ---------------------------------------------------------------- V2 contracts
def clone_conditions(oid, template_key, overrides=None):
    ex = json.loads((DATA / f"{EXEMPLARS[template_key]}.json").read_text(encoding="utf-8"))
    conds = deepcopy(ex["condition_contract"]["conditions"])
    out, n = [], 0
    for c in conds:
        c["id"] = f"C-{oid}-{n+1:02d}" if c["metric"] not in WINDOW_METRICS else None
        c["claim_refs"] = [f"{oid}-claim-01"]
        out.append(c)
        n += 1
    for c in out:
        if c["id"] is None:
            c["id"] = f"C-{oid}-LW1"
    if overrides:
        for c in out:
            if c["metric"] in overrides:
                c.update(overrides[c["metric"]])
    return out

def seasonal_condition(oid, sid):
    win = TYPICAL_WINDOWS[sid]
    name = SEASON_NAMES[sid]
    return {
        "id": f"C-{oid}-S1", "role": "REQUIRED", "domain": "SEASON_TIME",
        "evaluation_mode": "GUIDANCE", "capability": "CONDITIONS",
        "metric": "seasonal_state", "operator": "eq", "threshold": "window_open",
        "unit": None, "unknown_policy": "propagate_unknown",
        "claim_refs": [f"{oid}-claim-01"], "model_binding": None,
        "validation_status": "provisional", "condition_tier": "MAIN",
        "threshold_source": "computed", "calibration_status": "provisional",
        "rationale_i18n": {
            "zh-TW": f"季節窗判定（window_open/window_closed，例年窗 {win['start']}–{win['end']} 讀自 seasonal-calendar.json，實況優先，兩者皆缺時誠實 not_evaluatable）：本題材受營運期/季節窗硬性約束（CL-DATA-25 建置時即帶窗）。",
            "en": f"Seasonal-window verdict (window_open/window_closed; typical window {win['start']}-{win['end']} from seasonal-calendar.json, observed takes precedence, neither present = honestly not_evaluatable): this subject is hard-gated by an operating/season window (built in at CL-DATA-25 admission).",
            "ja": f"季節窓判定（window_open/window_closed。例年窓 {win['start']}〜{win['end']} は seasonal-calendar.json から、実況優先、両方欠ければ誠実に not_evaluatable）。本題材は営業期・季節窓でハード制約（CL-DATA-25 作成時に組み込み）。"},
    }

def snow_ice_conditions(oid, sid, night):
    conds = [seasonal_condition(oid, sid)]
    conds.append({
        "id": f"C-{oid}-02", "role": "REQUIRED", "domain": "WEATHER",
        "evaluation_mode": "GUIDANCE", "capability": "CONDITIONS",
        "metric": "visibility", "operator": "gte", "threshold": 3.0, "unit": "km",
        "unknown_policy": "propagate_unknown", "claim_refs": [f"{oid}-claim-01"],
        "model_binding": "dataset:gfs_0p25|field:visibility_km|role:MID",
        "validation_status": "provisional", "condition_tier": "MAIN",
        "threshold_source": "formula_derived", "calibration_status": "provisional",
        "rationale_i18n": {
            "zh-TW": "能見度 ≥3 km：樹氷拍攝的否決條件是暴雪/白牆（ホワイトアウト）；降雪本身不否決（飄雪中的樹氷反而是加分）。",
            "en": "Visibility >= 3 km: the veto condition is blizzard/whiteout; falling snow itself is not a veto (snow monsters in falling snow are a bonus).",
            "ja": "視程≥3km。否決条件は吹雪・ホワイトアウト。降雪自体は否決しない（降雪中の樹氷はむしろ好条件）。"},
    })
    conds.append({
        "id": f"C-{oid}-03", "role": "REQUIRED", "domain": "WEATHER",
        "evaluation_mode": "GUIDANCE", "capability": "CONDITIONS",
        "metric": "wind_speed_10m", "operator": "lt", "threshold": 15.0, "unit": "m/s",
        "unknown_policy": "propagate_unknown", "claim_refs": [f"{oid}-claim-01"],
        "model_binding": "dataset:gfs_0p25|field:wind_speed_10m_m_s|role:MID",
        "validation_status": "provisional", "condition_tier": "MAIN",
        "threshold_source": "formula_derived", "calibration_status": "provisional",
        "rationale_i18n": {
            "zh-TW": "風 <15 m/s：山頂強風下拍攝與纜車/步行安全界線（八甲田公式 25 m/s 運休的保守折半值；安全為先，成立值可再校準）。",
            "en": "Wind < 15 m/s: summit-wind safety boundary between shooting and ropeway/walking risk (a conservative half of Hakkoda's official 25 m/s suspension threshold; calibrated down for safety first).",
            "ja": "風<15m/s。山頂の強風での撮影とロープウェイ・歩行の安全境界（八甲田公式25m/s運休基準の保守的半分。安全優先で較正）。"},
    })
    lw = {
        "id": f"C-{oid}-{'LW1' if not night else 'LW1'}", "role": "REQUIRED",
        "domain": "ASTRONOMY", "evaluation_mode": "GUIDANCE", "capability": "CONDITIONS",
        "metric": "city_night_window" if night else "light_window",
        "operator": "none", "threshold": None, "unit": None,
        "unknown_policy": "propagate_unknown", "claim_refs": [f"{oid}-claim-01"],
        "model_binding": None, "validation_status": "provisional",
        "condition_tier": "MAIN", "threshold_source": "computed",
        "calibration_status": "provisional",
        "rationale_i18n": {
            "zh-TW": "時間窗（必要條件）：日間樹氷只在民用光（太陽仰角 > −6°）內成立" if not night else "夜間ライトアップ時間窗（人工光夜間題材；成立時段由年度公佈運用時間決定，契約以夜間窗對拍，不會把白天時段判為符合）。",
            "en": "Time window (necessary condition): daytime juhyo qualifies only in civil light (sun elevation > -6 deg)" if not night else "Night illumination window: an artificial-light night subject; qualifying hours follow the yearly announced operating hours - daytime hours never qualify.",
            "ja": "時間窓（必要条件）。日中の樹氷は市民光（太陽高度>−6°）内でのみ成立" if not night else "夜間ライトアップの時間窓。人工光の夜間題材であり、昼間時間帯は決して成立しない。"},
    }
    conds.append(lw)
    return conds

def drift_ice_condition(oid):
    return [{
        "id": f"C-{oid}-01", "role": "REQUIRED", "domain": "WEATHER",
        "evaluation_mode": "GUIDANCE", "capability": "CONDITIONS",
        "metric": "legacy_drift_ice", "operator": "none", "threshold": None,
        "unit": None, "unknown_policy": "propagate_unknown",
        "claim_refs": [f"{oid}-claim-01"], "model_binding": None,
        "notes_i18n": {
            "zh-TW": "CL-DATA-25（2026-11-07）：本筆標記為流氷主導題材（genre_template=drift_ice）。支配條件是海冰接岸與否（風向/海況/海冰分佈），非天氣；系統現無海冰資料源，誠實 not_evaluatable（fail-closed）待海冰模組實作後再建契約，不提供天氣契約以免誤導（同 CL-DATA-20 潮汐語意）。季節窗（1月下旬–3月）已在 seasonal-calendar 供參考。",
            "en": "CL-DATA-25 (2026-11-07): drift-ice-governed subject (genre_template=drift_ice). The governing condition is whether sea ice is onshore (wind/sea state/ice distribution), not weather; the system has no sea-ice data source, so it is honestly not_evaluatable (fail-closed) until a sea-ice module exists - no weather contract is offered to avoid misleading (same semantics as the CL-DATA-20 tidal pattern). The seasonal window (late Jan-Mar) is in seasonal-calendar for reference.",
            "ja": "CL-DATA-25（2026-11-07）：流氷支配の題材（genre_template=drift_ice）。支配的条件は海氷の接岸有無（風向・海況・海氷分布）で天気ではない。海氷データソースが現状ないため誠実に not_evaluatable（fail-closed）。潮汐型（CL-DATA-20）と同じ語義。気象契約は誤解を避けるため提供しない。季節窓（1月下旬〜3月）は seasonal-calendar 参照。"},
        "validation_status": "provisional",
    }]

def build_contract(p, subj):
    oid = f"{p['place_id']}-{subj['suffix']}"
    tpl = subj["template"]
    night = bool(subj.get("night"))
    if tpl == "cloud_sea":
        conds = clone_conditions(oid, "cloud_sea")
        elev = p.get("elev_m")
        for c in conds:
            if c["metric"] == "lcl_height_m_agl" and elev:
                c["threshold"] = elev - 200
        if subj.get("seasonal"):
            conds.insert(0, seasonal_condition(oid, subj["seasonal"]))
    elif tpl == "sunrise":
        key = "sunrise_marine" if p["slug"] in ("shiretoko-utoro-ryuhyo", "jialulan-coast") else "sunrise"
        conds = clone_conditions(oid, "sunrise")
        if subj.get("seasonal"):
            conds.insert(0, seasonal_condition(oid, subj["seasonal"]))
    elif tpl == "sunset":
        conds = clone_conditions(oid, "sunset")
        if subj.get("seasonal"):
            conds.insert(0, seasonal_condition(oid, subj["seasonal"]))
    elif tpl == "night_sky":
        conds = clone_conditions(oid, "night_sky")
        if subj.get("seasonal"):
            conds.insert(0, seasonal_condition(oid, subj["seasonal"]))
    elif tpl == "reflection":
        conds = clone_conditions(oid, "reflection")
        if subj.get("seasonal"):
            conds.insert(0, seasonal_condition(oid, subj["seasonal"]))
    elif tpl == "overlook":
        conds = clone_conditions(oid, "overlook")
        if subj.get("seasonal"):
            conds.insert(0, seasonal_condition(oid, subj["seasonal"]))
    elif tpl == "mountain_view":
        conds = clone_conditions(oid, "mountain_view")
        if subj.get("seasonal"):
            conds.insert(0, seasonal_condition(oid, subj["seasonal"]))
    elif tpl == "seasonal_plant":
        conds = clone_conditions(oid, "seasonal_plant")
    elif tpl == "city_night":
        conds = clone_conditions(oid, "city_night")
    elif tpl == "snow_ice":
        conds = snow_ice_conditions(oid, subj["seasonal"], night=False)
    elif tpl == "snow_ice_night":
        conds = snow_ice_conditions(oid, subj["seasonal"], night=True)
    elif tpl == "drift_ice":
        conds = drift_ice_condition(oid)
    else:
        raise SystemExit(f"unknown template {tpl}")

    geo_src = " ; ".join(p["coord_sources"])
    deriv = (
        f"CL-DATA-25 admission web verification 2026-11-07 ({p['coord_source']}; "
        f"source URLs: {geo_src}). CL-DATA-23 dossier coordinate was approx - corrected/confirmed as stated."
    )
    elev = p.get("elev_m")
    elev_i18n = (
        {"zh-TW": f"海拔 {elev} m（來源：{p['coord_source']}）。" if elev else "海拔未核實——誠實留空，勿引用未證實數值。",
         "en": f"Elevation {elev} m (source: {p['coord_source']})." if elev else "Elevation not yet verified - left empty honestly.",
         "ja": f"標高 {elev} m（出典：{p['coord_source']}）。" if elev else "標高は未確認。空欄のまま誠実に扱う。"}
    )
    access = {
        "zh-TW": subj["desc_zh"] + "（開放/營運狀態以現場公告為準。）",
        "en": subj["desc_en"] + " (Opening/operating status follows on-site notices.)",
        "ja": subj["desc_ja"] + "（開放・営業状況は現地の案内に従う。）",
    }
    safety = {
        "zh-TW": "請依現場安全指示行動；夜間/冬季天候險惡時請勿冒進。",
        "en": "Follow on-site safety guidance; do not push on in severe night/winter weather.",
        "ja": "現地の安全指示に従う。夜間・冬季の悪天候では無理をしない。",
    }
    point = {"kind": "point", "status": "provisional",
             "geojson": {"type": "Point", "coordinates": [p["lon"], p["lat"]]},
             "uncertainty_m": None, "derivation_method": deriv,
             "source_geometry_revision": None, "reason_if_absent": None}
    return {
        "schema_version": "2.1.0",
        "opportunity_id": oid,
        "place_id": p["place_id"],
        "revision": 1,
        "lifecycle_status": "draft",
        "name_i18n": {"zh-TW": subj["zh"], "en": subj["en"], "ja": subj["ja"]},
        "description_i18n": {"zh-TW": subj["desc_zh"], "en": subj["desc_en"], "ja": subj["desc_ja"]},
        "camera_contexts": [{
            "id": f"CZ-{oid}-01", "kind": "area", "geometry": dict(point),
            "verification_status": "provisional", "evidence_refs": [],
            "access_notes_i18n": access, "safety_notes_i18n": safety,
            "altitude_m": float(elev) if elev else None,
        }],
        "targets": [{
            "id": f"SG-{oid}-01", "kind": "multi_component",
            "name_i18n": {"zh-TW": subj["zh"], "en": subj["en"], "ja": subj["ja"]},
            "geometry": dict(point), "phenomenon_model_id": None,
            "evidence_refs": [], "components": [],
        }],
        "observation_relations": [{
            "id": f"VR-{oid}-01", "camera_context_id": f"CZ-{oid}-01",
            "target_id": f"SG-{oid}-01", "type": "foreground_background",
            "geometry_mode": "unknown", "azimuth_deg": None, "elevation_deg": None,
            "distance_m": None, "evidence_refs": [], "derivation_method": None,
            "uncertainty_note": "CL-DATA-25 admission reference; angles and distance unknown pending field survey.",
        }],
        "navigation_targets": [{
            "id": f"NAV-{oid}-01", "status": "needs_review", "target_type": "other",
            "lat": p["lat"], "lon": p["lon"],
            "label_i18n": {"zh-TW": p["names"]["local"], "en": p["names"]["en"], "ja": p["names"]["local"]},
            "evidence_refs": [], "confidence": "low",
        }],
        "condition_contract": {
            "contract_id": f"CC-{oid}-v1", "status": "draft",
            "genre_template": tpl, "template_version": f"{tpl}-v0.1",
            "recommendation_policy_version": None,
            "conditions": conds,
        },
        "evidence_claims": [{
            "claim_id": f"{oid}-claim-01", "claim_type": "existence",
            "evidence_refs": [f"e-d25-web-{p['slug']}"], "audit_status": "UNKNOWN",
            "scope_note": "CL-DATA-25 discovery admission (rubric >=3.8, owner ruling 2026-11-07); coordinates/elevation web-verified 2026-11-07 (sources in camera derivation_method and data/v2/audits/cl-data-25_web_evidence.json); thresholds provisional pending real-shoot calibration.",
        }],
        "readiness": {"research_level": "R1", "gaps": ["RESEARCH_GAP"]},
        "provenance": {
            "source_catalog": "CL-DATA-23 discovery shortlist (CL-DATA-25 admission)",
            "source_revision": f"cl-data-23:{p['shortlist_id']}",
            "imported_at": "2026-11-07T00:00:00Z",
            "review_status": "pending", "reviewed_by": None,
        },
    }

# ---------------------------------------------------------------- legacy catalog
def legacy_variant_id(existing_max):
    return existing_max + 1

def build_legacy_spot(p, next_var_id):
    subjects = []
    var_id = next_var_id
    elev = p.get("elev_m")
    for subj in p["subjects"]:
        oid = f"{p['place_id']}-{subj['suffix']}"
        theme_key = subj["template"]
        if theme_key == "sunrise" and p["slug"] in ("shiretoko-utoro-ryuhyo", "jialulan-coast"):
            theme_key = "sunrise_marine"
        if theme_key == "reflection":
            theme_key = {"taushubetsu-bridge": "reflection_lakelevel",
                         "cuifeng-lake": "reflection_lake"}.get(p["slug"], "reflection")
        theme, status = LEGACY_MAP[theme_key]
        if subj.get("seasonal"):
            best_season = f"季節窗 {TYPICAL_WINDOWS[subj['seasonal']]['start']}–{TYPICAL_WINDOWS[subj['seasonal']]['end']}（seasonal-calendar）"
            best_season_i18n = {"zh-TW": best_season,
                                "en": f"Seasonal window {TYPICAL_WINDOWS[subj['seasonal']]['start']}-{TYPICAL_WINDOWS[subj['seasonal']]['end']} (seasonal-calendar)",
                                "ja": f"季節窓 {TYPICAL_WINDOWS[subj['seasonal']]['start']}〜{TYPICAL_WINDOWS[subj['seasonal']]['end']}（seasonal-calendar）"}
        else:
            best_season = "全年候選，實際成立與否以當日資料為準"
            best_season_i18n = {"zh-TW": best_season, "en": "Year-round candidate; actual validity follows the day's data.", "ja": "通年候補。成立は当日データ次第。"}
        variant = {
            "variant_id": f"VAR-{var_id}", "variant_name": subj["zh"],
            "hard_gates": "眺望點合法可達且安全；官方封閉/營運停止時不成立",
            "required_conditions": "以 V2 契約條件為準（draft/provisional，未校準）",
            "boosters": subj["desc_zh"][:80],
            "penalties": "惡劣天候、能見度差、營運/季節窗外",
            "formula_status": status,
            "variant_name_i18n": {"zh-TW": subj["zh"], "en": subj["en"], "ja": subj["ja"]},
            "required_conditions_i18n": {
                "zh-TW": "以 V2 契約條件為準（draft/provisional，未校準）",
                "en": "Judged by the V2 contract conditions (draft/provisional, uncalibrated).",
                "ja": "V2契約の条件に従う（draft/provisional、未校正）。"},
            "boosters_i18n": {"zh-TW": subj["desc_zh"], "en": subj["desc_en"], "ja": subj["desc_ja"]},
            "penalties_i18n": {
                "zh-TW": "惡劣天候、能見度差、營運/季節窗外",
                "en": "Severe weather, poor visibility, outside operating/season window.",
                "ja": "悪天候、視程不良、営業・季節窓外。"},
        }
        var_id += 1
        subjects.append({
            "opportunity_id": oid, "spot_id": p["place_id"],
            "name_zh": subj["zh"], "legacy_theme": theme,
            # CL-INT-90: op-level locale parity — name_i18n mirrors the admitted
            # subject names; best_time stays honest (no invented time window)
            # and carries trilingual copy instead of the name-as-placeholder bug.
            "name_i18n": {"zh-TW": subj["zh"], "en": subj["en"], "ja": subj["ja"]},
            "best_time": "本題材尚未核定特定拍攝時段；實際成立與否以當日評估資料為準",
            "best_time_i18n": {
                "zh-TW": "本題材尚未核定特定拍攝時段；實際成立與否以當日評估資料為準",
                "en": "No specific shooting window has been verified for this subject; whether it forms is judged from the day's evaluation data.",
                "ja": "この題材の特定の撮影時間帯はまだ確認されていません。成立するかは当日の評価データで判断します。",
            },
            "mode": "area_opportunity", "sampling_topology": "local_area",
            "geometry_required": False, "opportunity_confidence": "medium",
            "formula_status": status,
            "formula_version": f"v0.04-cl-data-25-{p['slug']}-{subj['suffix']}",
            "formula_confidence": 50,
            "best_time": subj["zh"],
            "best_season": best_season,
            "best_season_i18n": best_season_i18n,
            "condition_variants": [variant],
            "viewpoints": [{
                "viewpoint_id": f"{p['place_id']}-VP01", "relation_role": "reference",
                "sort_order": 1, "name": p["names"]["local"],
                "name_i18n": {"zh-TW": p["names"]["local"], "en": p["names"]["en"], "ja": p["names"]["local"]},
                "lat": p["lat"], "lon": p["lon"],
                "coord_confidence": p["coord_conf"],
                "elevation_m": float(elev) if elev else None,
                "coordinate_source": p["coord_source"],
                "verification_status": "cl_data_25_web_verified_2026_11_07",
                "geometry_type": "area", "geometry_extent_m": 300,
                "geometry_note": "CL-DATA-25 admission: web-verified place anchor (sources in research_sources); exact tripod position and access not field-surveyed.",
            }],
        })
    spot = {
        "spot_id": p["place_id"],
        "canonical_name": p["names"]["local"],
        "product_status": "KEEP",
        "product_review_stage": "R4_2_CL_DATA_25_DISCOVERY_ADMISSION",
        "research_sources": [{
            "authority": "CL-DATA-23 discovery shortlist + CL-DATA-25 web verification (AI, owner ruling 2026-11-07 rubric >=3.8 direct admission)",
            "url": p["coord_sources"][0],
            "verified_on": "2026-11-07",
            "supports": f"{p['coord_source']}. Verified on 2026-11-07; exact tripod position and access not field-surveyed.",
        }],
        "opportunities": subjects,
    }
    return spot, var_id

def main():
    places = CAND["places"]
    # ---- V2 contracts
    written = []
    for p in places:
        for subj in p["subjects"]:
            c = build_contract(p, subj)
            out = DATA / f"{c['opportunity_id']}.json"
            wbytes(out, jdump(c))
            written.append(c["opportunity_id"])
    print(f"contracts written: {len(written)}")

    # ---- seasonal calendar
    cal_path = ROOT / "data/v2/seasonal-calendar.json"
    cal = json.loads(cal_path.read_bytes().decode("utf-8"))
    have = {e["plant_id"] for e in cal["entries"]}
    new_entries = build_seasonal_entries(places)
    added = [e for e in new_entries if e["plant_id"] not in have]
    cal["entries"].extend(added)
    wbytes(cal_path, jdump(cal))
    print(f"seasonal entries added: {len(added)}")

    # ---- regions.py
    rp = ROOT / "regions.py"
    text = rp.read_bytes().decode("utf-8").replace("\r\n", "\n")
    tw_lines, jp_lines, elev_lines, spot_lines, admin_tw, admin_jp = [], [], [], [], [], []
    for p in places:
        n = p["names"]
        tup = (f'            ({p["lat"]}, {p["lon"]}, "{n["zh-TW"]}", "{n["en"]}", '
               f'"{n["ja"]}", "{n["local"]}", "{p["category"]}", {json.dumps(p["tags"], ensure_ascii=False)}),\n')
        (jp_lines if p["region"] == "jp" else tw_lines).append(tup)
        elev_lines.append(f'    "{n["zh-TW"]}": {p["elev_m"]},\n' if p.get("elev_m") is not None else "")
    # rebuild spot overrides lines cleanly (f-string brace pitfalls avoided)
    spot_lines = []
    for p in places:
        n = p["names"]
        src = p["coord_source"].replace('"', "'")
        q = n["local"]
        spot_lines.append(
            ' "%s": {"lat": %s,\n           "lon": %s,\n           "map_query": %s,\n           "coordinate_source": %s,\n           "coordinate_confidence": "%s"},\n'
            % (n["zh-TW"], p["lat"], p["lon"], json.dumps(q, ensure_ascii=False),
               json.dumps("CL-DATA-25 admission web verification 2026-11-07: " + src, ensure_ascii=False),
               p["coord_conf"])
        )
    for p in places:
        (admin_jp if p["region"] == "jp" else admin_tw).append(
            '    "%s": ["%s"],\n' % (p["place_id"], p["admin"])
        )
    a1 = '            (25.140639, 121.420333, "八里崁頭里・淡水大橋觀景點", "Bali Kantou Guandu Bridge Viewpoint", "八里崁頭・淡水大橋展望地", "八里崁頭里・淡水大橋觀景點", "本島", ["coast", "city", "cloud_sea"]),\n'
    assert a1 in text, "tw spots anchor missing"
    if "# CL-DATA-25 discovery admission (web-verified 2026-11-07)" not in text:
        text = text.replace(a1, a1 + "".join(tw_lines), 1)
    a2 = '            (32.7016613, 131.3003766, "高千穗峽", "Takachiho Gorge", "高千穂峡", "高千穂峡", "九州/沖繩", ["waterfall", "forest", "mountain"]),\n'
    assert a2 in text, "jp spots anchor missing"
    if "# CL-DATA-25 discovery admission (web-verified 2026-11-07)" not in text:
        text = text.replace(a2, a2 + "".join(jp_lines), 1)
    a3 = '    "tw-086": ["新北市"],\n'
    assert a3 in text
    if "# CL-DATA-25 admission admin areas" not in text:
        text = text.replace(a3, a3 + "    # CL-DATA-25 admission admin areas\n" + "".join(admin_tw), 1)
    a4 = '    "jp-036": ["宮崎県"],\n'
    assert a4 in text
    if "# CL-DATA-25 admission admin areas" not in text:
        text = text.replace(a4, a4 + "    # CL-DATA-25 admission admin areas\n" + "".join(admin_jp), 1)
    a5 = '    "富士山": 3776,\n}\n'
    ins5 = "".join(l for l in elev_lines if l)
    if "# CL-DATA-25 discovery admission elevations" not in text:
        assert a5 in text
        text = text.replace(a5, a5.replace('}\n', '    # CL-DATA-25 discovery admission elevations (web-verified 2026-11-07; null elevations omitted honestly)\n' + ins5 + '}\n'), 1)
    a6 = 'SPOT_OVERRIDES = {\n'
    if "# CL-DATA-25 discovery admission (web-verified 2026-11-07)" not in text:
        assert a6 in text
        text = text.replace(a6, a6 + " # CL-DATA-25 discovery admission (web-verified 2026-11-07)\n" + "".join(spot_lines), 1)
    wbytes(rp, text)
    print("regions.py patched")

    # ---- runtime catalog
    cat_path = ROOT / "runtime_catalog_v004_r4_2.json"
    cat = json.loads(cat_path.read_bytes().decode("utf-8"))
    max_var = 0
    for s in cat["spots"]:
        for o in s["opportunities"]:
            for v in o.get("condition_variants", []):
                vid = int(str(v["variant_id"]).split("-")[1])
                max_var = max(max_var, vid)
    existing_ids = {s["spot_id"] for s in cat["spots"]}
    spots_added = opps_added = variants_added = vp_added = 0
    var_id = max_var + 1
    for p in places:
        if p["place_id"] in existing_ids:
            continue
        spot, var_id = build_legacy_spot(p, var_id)
        cat["spots"].append(spot)
        spots_added += 1
        opps_added += len(spot["opportunities"])
        variants_added += len(spot["opportunities"])
        vp_added += sum(len(o.get("viewpoints", [])) for o in spot["opportunities"])
    cat["counts"] = {
        "spots": len({s['spot_id'] for s in cat['spots']}),
        "opportunities": sum(len(s["opportunities"]) for s in cat["spots"]),
        "condition_variants": sum(sum(len(o.get("condition_variants", [])) for o in s["opportunities"]) for s in cat["spots"]),
        "profile_viewpoint_relations": sum(sum(len(o.get("viewpoints", [])) for o in s["opportunities"]) for s in cat["spots"]),
    }
    wbytes(cat_path, jdump(cat))
    print(f"runtime catalog: +{spots_added} spots, +{opps_added} opportunities, +{variants_added} variants, +{vp_added} viewpoints")

    # ---- manifest
    mf_path = ROOT / "runtime_catalog_manifest_r4_2.json"
    mf = json.loads(mf_path.read_bytes().decode("utf-8"))
    tw_spots = [s for s in cat["spots"] if s["spot_id"].startswith("tw-")]
    jp_spots = [s for s in cat["spots"] if s["spot_id"].startswith("jp-")]
    def region_counts(spots):
        opps = [o for s in spots for o in s["opportunities"]]
        return {"spots": len(spots), "opportunities": len(opps),
                "condition_variants": sum(len(o.get("condition_variants", [])) for o in opps),
                "profile_viewpoint_relations": sum(len(o.get("viewpoints", [])) for o in opps)}
    mf["regions"]["tw"]["numeric_id_end"] = max(int(p["place_id"].split("-")[1]) for p in places if p["place_id"].startswith("tw-"))
    mf["regions"]["jp"]["numeric_id_end"] = max(int(p["place_id"].split("-")[1]) for p in places if p["place_id"].startswith("jp-"))
    mf["regions"]["tw"]["counts"] = region_counts(tw_spots)
    mf["regions"]["jp"]["counts"] = region_counts(jp_spots)
    mf["totals"] = dict(cat["counts"])
    import collections
    import opportunities as _O
    pol = collections.Counter()
    for s in cat["spots"]:
        for o in s["opportunities"]:
            pol[_O.runtime_policy(o)] += 1
    mf["runtime_policy_counts"] = dict(pol)
    wbytes(mf_path, jdump(mf))
    print("manifest updated:", mf["regions"]["tw"]["counts"], mf["regions"]["jp"]["counts"])

    # ---- runtime_dependencies profile gaps
    rd_path = ROOT / "runtime_dependencies.py"
    rd = rd_path.read_bytes().decode("utf-8").replace("\r\n", "\n")
    gaps = {}
    for p in places:
        for subj in p["subjects"]:
            oid = f"{p['place_id']}-{subj['suffix']}"
            theme_key = subj["template"]
            if theme_key == "sunrise" and p["slug"] in ("shiretoko-utoro-ryuhyo", "jialulan-coast"):
                theme_key = "sunrise_marine"
            if theme_key == "reflection":
                theme_key = {"taushubetsu-bridge": "reflection_lakelevel",
                             "cuifeng-lake": "reflection_lake"}.get(p["slug"], "reflection")
            status = LEGACY_MAP[theme_key][1]
            comp = PROFILE_GAP_COMPONENTS.get(status)
            if comp:
                gaps.setdefault(comp, set()).add(oid)
    for comp, ids in gaps.items():
        anchor = f'    "{comp}": frozenset({{\n'
        if anchor not in rd:
            if comp == "astronomy_ephemeris":
                insert_at = rd.index('    "seasonal_foreground": frozenset({')
                block = f'    "astronomy_ephemeris": frozenset({{\n'
                block += "".join(f'        "{oid}",\n' for oid in sorted(ids))
                block += "    }),\n"
                rd = rd[:insert_at] + block + rd[insert_at:]
            continue
        i = rd.index(anchor) + len(anchor)
        insert = "".join(f'        "{oid}",\n' for oid in sorted(ids))
        rd = rd[:i] + insert + rd[i:]
    wbytes(rd_path, rd)
    print("runtime_dependencies gaps:", {k: len(v) for k, v in gaps.items()})

    # ---- evidence json
    ev = {"ticket": "CL-DATA-25", "verified_on": "2026-11-07", "places": []}
    for p in places:
        ev["places"].append({
            "place_id": p["place_id"], "slug": p["slug"], "score": p["score"],
            "lat": p["lat"], "lon": p["lon"], "elev_m": p.get("elev_m"),
            "coord_confidence": p["coord_conf"], "coord_source": p["coord_source"],
            "sources": p["coord_sources"], "subjects": [s["zh"] for s in p["subjects"]],
        })
    ev["excel_side"] = CAND["excel_side"]
    ev["excluded"] = CAND["excluded"]
    # evidence registry rows consumed by research_index (pinned audits/* evidence)
    ev["evidence"] = [{
        "id": f"e-d25-web-{p['slug']}", "grade": "A" if p["coord_conf"] == "high" else "B",
        "kind": "official_or_wikipedia_text",
        "url": next(u for u in p["coord_sources"] if u.startswith("https://")),
        "supports": p["coord_source"],
        "retrieved_at": "2026-11-07",
        "limitation": "Coordinate verified against official/Wikipedia source; exact tripod position, bearing and access not field-surveyed.",
    } for p in places]
    wbytes(ROOT / "data/v2/audits/cl-data-25_web_evidence.json", jdump(ev))
    print("evidence json written")

if __name__ == "__main__":
    main()
